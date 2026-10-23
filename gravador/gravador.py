# -*- coding: utf-8 -*-
"""Gravador MQTT do Higrolar AP2 — equipe eq04, broker EMQX Cloud.

Contrato de telemetria: id, boot_id, seq, ts, sensor_ok, temp_c, umid_pct.
Cada mensagem bruta é preservada; (id, boot_id, seq) é a chave lógica.
Nao elimina duplicatas: o qualidade.py as identifica e contabiliza.

Instalacao: py -m pip install "paho-mqtt>=2,<3"
Execucao: py gravador.py --host HOST_EMQX --usuario USUARIO_GRAVADOR
Senha: variavel de ambiente MQTT_SENHA ou prompt seguro.
"""

import argparse
import csv
import getpass
import json
import os
import ssl
import sys
import time
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent / "dados"
COLUNAS = [
    "t_chegada", "chegada", "topico", "retido", "payload", "qos", "dup",
    "id", "boot_id", "seq",
]


def argumentos():
    p = argparse.ArgumentParser(description="Grava mensagens MQTT do Higrolar com boot_id")
    p.add_argument("--host", required=True, help="Host EMQX sem https:// ou mqtts://")
    p.add_argument("--usuario", required=True, help="Usuario MQTT exclusivo do gravador")
    p.add_argument("--equipe", default="eq04", help="Equipe MQTT (padrao: eq04)")
    p.add_argument("--no", default="no02", help="No a acompanhar ou '+' para todos")
    p.add_argument("--porta", type=int, default=8883, help="Porta TLS (padrao: 8883)")
    p.add_argument("--client-id", default="ufpi-iot26-eq04-gravador",
                   help="Identificador de cliente MQTT, fixo e exclusivo")
    p.add_argument("--saida", type=Path, default=DADOS / "mensagens.csv",
                   help="CSV de destino")
    p.add_argument("--sessao-limpa", action="store_true",
                   help="Desativa sessao persistente (nao recomendado na campanha)")
    return p.parse_args()


def abrir_csv(caminho: Path):
    """Novo contrato: exige cabeçalho com id/boot_id/seq."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    existente = caminho.exists() and caminho.stat().st_size > 0
    if existente:
        with caminho.open("r", newline="", encoding="utf-8-sig") as entrada:
            cabecalho = next(csv.reader(entrada), [])
        if cabecalho != COLUNAS:
            raise ValueError(
                f"CSV existente usa outro formato: {cabecalho!r}. "
                "Antes da campanha, renomeie/remova seu CSV de testes "
                "ou use --saida com um novo nome."
            )

    arquivo = caminho.open("a", newline="", encoding="utf-8")
    escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
    if not existente:
        escritor.writeheader()
        arquivo.flush()
        os.fsync(arquivo.fileno())
    return arquivo, escritor


def ao_conectar(cliente, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f"[mqtt] conexao recusada: {reason_code}", flush=True)
        return
    print(f"[mqtt] conectado; sessao anterior: "
          f"{'existia' if flags.session_present else 'nao existia'}", flush=True)
    prefixo = f"ufpi-iot26/{userdata['equipe']}/{userdata['no']}"
    for tipo in ("telemetria", "status", "config"):
        topico = f"{prefixo}/{tipo}"
        rc, mid = cliente.subscribe(topico, qos=1)
        if rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[mqtt] SUBSCRIBE QoS 1: {topico} (mid={mid})", flush=True)
        else:
            print(f"[mqtt] falha ao assinar {topico}: {rc}", flush=True)


def ao_falhar_conexao(cliente, userdata):
    print("[mqtt] conexao TCP falhou; aguardando nova tentativa", flush=True)


def ao_desconectar(cliente, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f"[mqtt] desconectado inesperadamente: {reason_code}", flush=True)


def extrair_identificacao(topico, texto):
    """Extrai a chave lógica quando a mensagem é uma telemetria válida.

    Preserva mensagens fora do contrato; qualidade.py conta erros depois.
    """
    if not topico.endswith("/telemetria"):
        return "", "", ""
    try:
        doc = json.loads(texto)
    except (json.JSONDecodeError, UnicodeError):
        return "", "", ""
    if not isinstance(doc, dict):
        return "", "", ""
    identificador = doc.get("id")
    boot_id = doc.get("boot_id")
    seq = doc.get("seq")
    return (
        identificador if isinstance(identificador, str) else "",
        boot_id if type(boot_id) is int and boot_id > 0 else "",
        seq if type(seq) is int and seq > 0 else "",
    )


def ao_receber(cliente, userdata, msg):
    agora = time.time()
    horario = datetime.fromtimestamp(agora).astimezone().isoformat(timespec="seconds")
    texto = msg.payload.decode("utf-8", errors="replace")
    ident, boot_id, seq = extrair_identificacao(msg.topic, texto)
    linha = {
        "t_chegada": f"{agora:.3f}",
        "chegada": horario,
        "topico": msg.topic,
        "retido": int(bool(msg.retain)),
        "payload": texto,
        "qos": msg.qos,
        "dup": int(bool(msg.dup)),
        "id": ident,
        "boot_id": boot_id,
        "seq": seq,
    }

    try:
        userdata["escritor"].writerow(linha)
        userdata["arquivo"].flush()
        os.fsync(userdata["arquivo"].fileno())
    except (OSError, csv.Error) as exc:
        # Sem confirmação MQTT em caso de falha de escrita.
        print(f"[csv] ERRO ao persistir; sem ACK: {exc}", file=sys.stderr, flush=True)
        return

    if msg.qos > 0:
        resultado = cliente.ack(msg.mid, msg.qos)
        if resultado != mqtt.MQTT_ERR_SUCCESS:
            print(f"[mqtt] aviso: ACK mid={msg.mid} retornou {resultado}", flush=True)

    marca = []
    if msg.retain:
        marca.append("retida")
    if msg.dup:
        marca.append("DUP")
    extras = f" [{', '.join(marca)}]" if marca else ""
    chave = f" id={ident} boot_id={boot_id} seq={seq}" if ident and boot_id != "" else ""
    print(f"{horario} {msg.topic}{chave} {texto}{extras}", flush=True)


def main():
    a = argumentos()
    if not a.host or "://" in a.host or "/" in a.host:
        raise SystemExit("Use somente o hostname no --host, sem protocolo nem caminho.")
    if not (1 <= a.porta <= 65535):
        raise SystemExit("Porta TCP invalida.")
    if a.no != "+" and any(c in a.no for c in "+#"):
        raise SystemExit("Use um no sem curingas ou exatamente '+'.")
    if not a.equipe or any(c in a.equipe for c in "+#/" ):
        raise SystemExit("Nome de equipe MQTT invalido.")

    senha = os.environ.get("MQTT_SENHA") or getpass.getpass(f"Senha MQTT de {a.usuario}: ")
    if not senha:
        raise SystemExit("A senha MQTT nao pode estar vazia.")

    try:
        arquivo, escritor = abrir_csv(a.saida)
    except (OSError, ValueError, csv.Error) as exc:
        raise SystemExit(f"[csv] erro: {exc}") from exc

    with arquivo:
        userdata = {"arquivo": arquivo, "escritor": escritor,
                    "equipe": a.equipe, "no": a.no}
        cliente = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=a.client_id,
            clean_session=a.sessao_limpa,
            protocol=mqtt.MQTTv311,
            userdata=userdata,
            manual_ack=True,
        )
        cliente.username_pw_set(a.usuario, senha)
        # Certificados confiaveis do Windows/sistema; nao desativa verificacao TLS.
        contexto = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        cliente.tls_set_context(contexto)
        cliente.reconnect_delay_set(min_delay=2, max_delay=30)
        cliente.on_connect = ao_conectar
        cliente.on_connect_fail = ao_falhar_conexao
        cliente.on_disconnect = ao_desconectar
        cliente.on_message = ao_receber

        print(f"[gravador] broker {a.host}:{a.porta} (TLS com validacao)")
        print(f"[gravador] usuario={a.usuario}, client_id={a.client_id}")
        print(f"[gravador] arquivo={a.saida.resolve()}")
        print(f"[gravador] sessao persistente={not a.sessao_limpa}")
        print("[gravador] CSV inclui id, boot_id, seq; Ctrl+C para terminar")

        try:
            cliente.connect(a.host, a.porta, keepalive=30)
            cliente.loop_forever()
        except KeyboardInterrupt:
            print("\n[gravador] encerramento solicitado.")
        except ssl.SSLCertVerificationError as exc:
            print(f"[tls] erro de certificado: {exc}; confira hostname, data do PC e CA no Windows",
                  file=sys.stderr)
            raise SystemExit(2) from exc
        except (OSError, ssl.SSLError) as exc:
            print(f"[mqtt] falha de rede/TLS: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        finally:
            cliente.disconnect()
            arquivo.flush()
            os.fsync(arquivo.fileno())
            print("[gravador] CSV fechado.")


if __name__ == "__main__":
    main()
