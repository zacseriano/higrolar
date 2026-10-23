# -*- coding: utf-8 -*-
"""Qualidade da campanha Higrolar AP2 — equipe eq04, contrato com boot_id.

Chave lógica de mensagem: (id, boot_id, seq).
Lacunas e duplicacoes sao analisadas separadamente para cada inicializacao.
Reinicios observados: quantidade de boot_id distintos menos um; nao equivale
necessariamente ao numero total de resets, pois nem todo boot publica.

Uso:
    py qualidade.py
    py qualidade.py --de 23:30 --ate 00:30
    py qualidade.py --de 2026-10-23T18:00 --ate 2026-10-24T06:00
    py qualidade.py --saida-json ../dados/relatorio_qualidade.json
"""

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PADRAO = AQUI.parent / "dados" / "mensagens.csv"


def argumentos():
    p = argparse.ArgumentParser(description="Analisa perdas e repeticoes por boot_id e seq")
    p.add_argument("csv", nargs="?", type=Path, default=PADRAO, help="CSV criado pelo gravador")
    p.add_argument("--de", help="Inicio HH:MM ou AAAA-MM-DDTHH:MM")
    p.add_argument("--ate", help="Fim HH:MM ou AAAA-MM-DDTHH:MM (minuto inclusivo)")
    p.add_argument("--saida-json", type=Path, help="Salva um resumo JSON")
    return p.parse_args()


def parse_filtro(texto):
    if not texto:
        return None
    if len(texto) == 5 and texto[2] == ":":
        dt = datetime.strptime(texto, "%H:%M")
        return ("hora", dt.hour * 60 + dt.minute)
    try:
        dt = datetime.fromisoformat(texto)
    except ValueError as exc:
        raise ValueError(f"Janela invalida: {texto!r}") from exc
    if len(texto) < 16:
        raise ValueError("Para filtro com data, use AAAA-MM-DDTHH:MM")
    return ("data", dt)


def dentro(t, inicio, fim):
    """Filtros por hora local; intervalo HH:MM pode cruzar a meia-noite."""
    if not inicio and not fim:
        return True
    tipo = (inicio or fim)[0]
    if tipo == "hora":
        dt = datetime.fromtimestamp(t)
        minuto = dt.hour * 60 + dt.minute
        a = inicio[1] if inicio else None
        b = fim[1] if fim else None
        if a is not None and b is not None:
            return a <= minuto <= b if a <= b else minuto >= a or minuto <= b
        return (a is None or minuto >= a) and (b is None or minuto <= b)

    # Datas sem fuso sao interpretadas no fuso horario local do computador.
    def epoch(valor):
        return valor.astimezone().timestamp()

    # Inclui o minuto inteiro especificado em --ate.
    limite_fim = epoch(fim[1].replace(second=0, microsecond=0)) + 60 if fim else None
    return (inicio is None or t >= epoch(inicio[1])) and (limite_fim is None or t < limite_fim)


def horario(t):
    return datetime.fromtimestamp(t).astimezone().isoformat(timespec="seconds")


def numero_ts(valor):
    if isinstance(valor, bool) or not isinstance(valor, (float, int)):
        return None
    if not math.isfinite(valor) or valor < 946684800:
        return None
    return float(valor)


def contrato_valido(d):
    """Campanha nova exige boot_id positivo e seq positivo em TODA telemetria."""
    if not isinstance(d, dict):
        return False
    if not isinstance(d.get("id"), str) or not d["id"]:
        return False
    if type(d.get("boot_id")) is not int or d["boot_id"] <= 0:
        return False
    if type(d.get("seq")) is not int or d["seq"] <= 0:
        return False
    if not isinstance(d.get("sensor_ok"), bool):
        return False
    if d.get("ts") is not None and numero_ts(d["ts"]) is None:
        return False
    if d["sensor_ok"]:
        for campo in ("temp_c", "umid_pct"):
            valor = d.get(campo)
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
                return False
    else:
        # Se falhou o sensor, as grandezas podem ser nulas.
        for campo in ("temp_c", "umid_pct"):
            valor = d.get(campo)
            if valor is not None and (
                    isinstance(valor, bool) or not isinstance(valor, (float, int)) or not math.isfinite(valor)):
                return False
    return True


def percentile_95(numeros):
    ordenados = sorted(numeros)
    return ordenados[max(0, math.ceil(0.95 * len(ordenados)) - 1)]


def avaliar_boot(boot_id, lista):
    """Avalia um boot em ordem de chegada; nao mistura sequencias de boots distintos."""
    lista = sorted(lista, key=lambda v: (v["chegada"], v["ordem"]))
    vistos = set()
    maior_observado = -1
    repetidas = 0
    fora_ordem = 0
    sem_hora = 0
    atrasos = []
    atrasos_negativos = 0
    umidade_fora = 0
    qos_dup = 0
    sensor_falhas = 0

    for l in lista:
        seq = l["seq"]
        if seq in vistos:
            repetidas += 1
        elif seq < maior_observado:
            fora_ordem += 1
        vistos.add(seq)
        maior_observado = max(maior_observado, seq)

        if l["ts"] is None:
            sem_hora += 1
        else:
            atraso = l["chegada"] - l["ts"]
            atrasos.append(atraso)
            if atraso < 0:
                atrasos_negativos += 1
        if l["umidade"] is not None and not (0 <= l["umidade"] <= 100):
            umidade_fora += 1
        if not l["sensor_ok"]:
            sensor_falhas += 1
        qos_dup += int(l["dup"])

    minimo, maximo = min(vistos), max(vistos)
    faltantes = maximo - minimo + 1 - len(vistos)
    return {
        "boot_id": boot_id,
        "recebidas": len(lista),
        "unicas": len(vistos),
        "seq_minimo": minimo,
        "seq_maximo": maximo,
        "faltantes_internas": faltantes,
        "duplicadas_por_chave": repetidas,
        "fora_de_ordem": fora_ordem,
        "completude_percentual": round(100 * len(vistos) / (len(vistos) + faltantes), 2),
        "sem_timestamp": sem_hora,
        "dup_flag_mqtt": qos_dup,
        "falhas_sensor": sensor_falhas,
        "umidades_fora_0_100": umidade_fora,
        "atrasos_negativos": atrasos_negativos,
        "atraso_mediana_s": round(statistics.median(atrasos), 3) if atrasos else None,
        "atraso_p95_s": round(percentile_95(atrasos), 3) if atrasos else None,
        "atraso_max_s": round(max(atrasos), 3) if atrasos else None,
        "primeira_chegada": horario(lista[0]["chegada"]),
        "ultima_chegada": horario(lista[-1]["chegada"]),
        "primeira_chegada_epoch": lista[0]["chegada"],
    }


def avaliar_no(lista):
    if not lista:
        return None
    boots = defaultdict(list)
    for l in lista:
        boots[l["boot_id"]].append(l)
    resultados = [avaliar_boot(b, mensagens) for b, mensagens in boots.items()]
    resultados.sort(key=lambda r: (r["primeira_chegada_epoch"], r["boot_id"]))

    recebidas = sum(r["recebidas"] for r in resultados)
    unicas = sum(r["unicas"] for r in resultados)
    faltantes = sum(r["faltantes_internas"] for r in resultados)
    atrasos = [l["chegada"] - l["ts"] for l in lista if l["ts"] is not None]
    inicio = min(l["chegada"] for l in lista)
    fim = max(l["chegada"] for l in lista)
    return {
        "recebidas": recebidas,
        "unicas": unicas,
        "faltantes_internas": faltantes,
        "duplicadas_por_chave": sum(r["duplicadas_por_chave"] for r in resultados),
        "fora_de_ordem": sum(r["fora_de_ordem"] for r in resultados),
        "boot_ids_observados": [r["boot_id"] for r in resultados],
        "inicializacoes_observadas": len(resultados),
        "reinicios_observados_entre_boots": max(0, len(resultados) - 1),
        "completude_percentual": round(100 * unicas / (unicas + faltantes), 2),
        "sem_timestamp": sum(r["sem_timestamp"] for r in resultados),
        "dup_flag_mqtt": sum(r["dup_flag_mqtt"] for r in resultados),
        "falhas_sensor": sum(r["falhas_sensor"] for r in resultados),
        "umidades_fora_0_100": sum(r["umidades_fora_0_100"] for r in resultados),
        "atrasos_negativos": sum(r["atrasos_negativos"] for r in resultados),
        "atraso_mediana_s": round(statistics.median(atrasos), 3) if atrasos else None,
        "atraso_p95_s": round(percentile_95(atrasos), 3) if atrasos else None,
        "atraso_max_s": round(max(atrasos), 3) if atrasos else None,
        "primeira_chegada": horario(inicio),
        "ultima_chegada": horario(fim),
        "por_boot": [
            {k: v for k, v in r.items() if k != "primeira_chegada_epoch"}
            for r in resultados
        ],
    }


def processar(arquivo, inicio, fim):
    leituras = defaultdict(list)
    estados = defaultdict(list)
    configs = defaultdict(list)
    contagens = defaultdict(int)

    with arquivo.open("r", newline="", encoding="utf-8-sig") as f:
        leitor = csv.DictReader(f)
        campos = set(leitor.fieldnames or [])
        necessarios = {"t_chegada", "chegada", "topico", "retido", "payload",
                       "qos", "dup", "id", "boot_id", "seq"}
        if campos != necessarios:
            raise ValueError("CSV fora do novo contrato com boot_id. "
                             "Inicie um CSV novo com o gravador atualizado.")

        for numero, linha in enumerate(leitor, start=2):
            try:
                t = float(linha["t_chegada"])
                topico = linha["topico"]
                partes = topico.split("/")
                if not math.isfinite(t) or len(partes) != 4 or partes[0] != "ufpi-iot26":
                    raise ValueError("timestamp ou topico invalido")
            except (ValueError, TypeError, AttributeError):
                contagens["linhas_invalidas"] += 1
                print(f"[aviso] linha {numero}: timestamp/topico invalido")
                continue

            if not dentro(t, inicio, fim):
                continue

            contagens["mensagens_na_janela"] += 1
            no = f"{partes[1]}-{partes[2]}"
            tipo = partes[3]
            payload = linha.get("payload") or ""
            if tipo == "status":
                estados[no].append((t, payload.strip(), linha.get("retido") == "1"))
            elif tipo == "config":
                configs[no].append((t, payload))
            elif tipo == "telemetria":
                try:
                    d = json.loads(payload)
                    if not contrato_valido(d):
                        raise ValueError("contrato invalido")
                    if d["id"] != no:
                        contagens["id_incompativel_topico"] += 1
                        raise ValueError("id incompatível com topico")
                    # Verificacao cruzada CSV x payload: codigo do gravador e contrato.
                    if (linha.get("id") != d["id"] or
                            str(linha.get("boot_id")) != str(d["boot_id"]) or
                            str(linha.get("seq")) != str(d["seq"])):
                        contagens["csv_payload_divergente"] += 1
                        raise ValueError("CSV e payload discordam")
                    leituras[no].append({
                        "boot_id": d["boot_id"], "seq": d["seq"],
                        "ts": numero_ts(d.get("ts")), "chegada": t,
                        "ordem": numero, "umidade": d.get("umid_pct"),
                        "sensor_ok": d["sensor_ok"],
                        "dup": linha.get("dup", "0") == "1",
                    })
                except (json.JSONDecodeError, ValueError, TypeError) as exc:
                    contagens["telemetrias_invalidas"] += 1
                    print(f"[aviso] linha {numero}: telemetria invalida ({exc})")
            else:
                contagens["outros_topicos"] += 1

    por_no = {}
    for no in sorted(set(leituras) | set(estados) | set(configs)):
        status_ordenados = sorted(estados.get(no, []))
        transicoes = []
        for t, estado, retido in status_ordenados:
            if not transicoes or transicoes[-1]["estado"] != estado:
                transicoes.append({"quando": horario(t), "estado": estado, "retido": retido})
        por_no[no] = {
            "telemetria": avaliar_no(leituras.get(no, [])),
            "status": transicoes,
            "mensagens_status": len(status_ordenados),
            "configuracoes": [{"quando": horario(t), "payload": p}
                             for t, p in sorted(configs.get(no, []))],
        }
    return dict(contagens), por_no


def main():
    a = argumentos()
    if not a.csv.is_file():
        raise SystemExit(f"Arquivo nao encontrado: {a.csv}\nExecute primeiro o gravador.py")
    try:
        inicio, fim = parse_filtro(a.de), parse_filtro(a.ate)
        if inicio and fim and inicio[0] != fim[0]:
            raise ValueError("Nao misture HH:MM e AAAA-MM-DDTHH:MM")
        contagens, por_no = processar(a.csv, inicio, fim)
    except (ValueError, OSError) as exc:
        raise SystemExit(f"[qualidade] erro: {exc}") from exc

    print(f"[qualidade] arquivo: {a.csv.resolve()}")
    print(f"[qualidade] mensagens na janela: {contagens.get('mensagens_na_janela', 0)}")
    for chave in ("linhas_invalidas", "telemetrias_invalidas",
                  "id_incompativel_topico", "csv_payload_divergente", "outros_topicos"):
        if contagens.get(chave):
            print(f"[qualidade] {chave}: {contagens[chave]}")

    if not por_no:
        print("[qualidade] nenhuma mensagem valida na janela")

    for no, dados in por_no.items():
        print(f"\n=== {no} ===")
        e = dados["telemetria"]
        if e:
            print(f"  leituras recebidas            {e['recebidas']}")
            print(f"  leituras unicas               {e['unicas']}")
            print(f"  boots observados              {e['inicializacoes_observadas']}: {e['boot_ids_observados']}")
            print(f"  reinicios observados          {e['reinicios_observados_entre_boots']}")
            print(f"  faltas internas               {e['faltantes_internas']}")
            print(f"  duplicatas (id,boot_id,seq)   {e['duplicadas_por_chave']}")
            print(f"  fora de ordem                 {e['fora_de_ordem']}")
            print(f"  completude estimada           {e['completude_percentual']}%")
            print(f"  timestamp ausente             {e['sem_timestamp']}")
            print(f"  flag DUP MQTT                 {e['dup_flag_mqtt']}")
            print(f"  falhas de sensor              {e['falhas_sensor']}")
            if e["atraso_mediana_s"] is not None:
                print(f"  chegada - ts                  mediana {e['atraso_mediana_s']}s; "
                      f"p95 {e['atraso_p95_s']}s; max {e['atraso_max_s']}s")
                if e["atrasos_negativos"]:
                    print(f"  atrasos negativos             {e['atrasos_negativos']}")
            print(f"  janela                        {e['primeira_chegada']} -> {e['ultima_chegada']}")
            print("  detalhamento por inicializacao:")
            for b in e["por_boot"]:
                print(f"    boot_id={b['boot_id']}: recebidas={b['recebidas']}, "
                      f"unicas={b['unicas']}, seq={b['seq_minimo']}..{b['seq_maximo']}, "
                      f"faltas={b['faltantes_internas']}, "
                      f"duplicadas={b['duplicadas_por_chave']}")
        else:
            print("  nenhuma telemetria valida")

        if dados["status"]:
            print("  transicoes de status:")
            for s in dados["status"]:
                print(f"    {s['quando']}  {s['estado'] or '(vazio)'}"
                      f"{' [retida]' if s['retido'] else ''}")
        if dados["configuracoes"]:
            print(f"  comandos config: {len(dados['configuracoes'])}")
            for c in dados["configuracoes"][-5:]:
                print(f"    {c['quando']}  {c['payload'][:100]}")

    print("\n[nota] Lacunas so sao inferidas entre o menor e maior seq de cada boot observado.")
    print("[nota] Boots sem telemetria nao podem ser contabilizados apenas pelo CSV.")
    print("[nota] Atraso chegada-ts depende de relogios sincronizados e backlog.")
    print("[nota] Flag DUP MQTT nao equivale necessariamente a duplicata logica.")

    if a.saida_json:
        a.saida_json.parent.mkdir(parents=True, exist_ok=True)
        resumo = {
            "gerado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
            "arquivo_csv": str(a.csv.resolve()),
            "janela": {"de": a.de, "ate": a.ate},
            "contagens": contagens,
            "nos": por_no,
        }
        with a.saida_json.open("w", encoding="utf-8") as saida:
            json.dump(resumo, saida, indent=2, ensure_ascii=False)
        print(f"[qualidade] resumo JSON salvo em {a.saida_json.resolve()}")


if __name__ == "__main__":
    main()
