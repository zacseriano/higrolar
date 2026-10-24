# -*- coding: utf-8 -*-
"""Gera o conjunto limpo da campanha Higrolar AP2 a partir do CSV bruto.

Regras, na ordem:
  1. so entram mensagens do topico .../telemetria;
  2. a chave logica (id, boot_id, seq) define a leitura; repeticoes do QoS 1
     sao descartadas, ficando a primeira chegada;
  3. nenhuma linha e interpolada nem preenchida; ts nulo (antes do NTP)
     continua nulo e ts_origem diz qual hora usar.

O bruto (mensagens.csv) nao e alterado.

Uso:
    py limpar.py
    py limpar.py mensagens.csv --saida telemetria_limpa.csv
"""

import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FUSO = timezone(timedelta(hours=-3))
COLUNAS = ["id", "boot_id", "seq", "ts", "ts_local", "ts_origem", "t_chegada",
           "sensor_ok", "temp_c", "umid_pct"]


def argumentos():
    p = argparse.ArgumentParser(description="Deduplica a telemetria do CSV bruto")
    p.add_argument("csv", nargs="?", type=Path, default=AQUI / "mensagens.csv")
    p.add_argument("--saida", type=Path, default=AQUI / "telemetria_limpa.csv")
    return p.parse_args()


def main():
    a = argumentos()
    vistas = set()
    linhas = []
    repetidas = 0
    with a.csv.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if not r["topico"].endswith("/telemetria"):
                continue
            p = json.loads(r["payload"])
            chave = (p["id"], p["boot_id"], p["seq"])
            if chave in vistas:
                repetidas += 1
                continue
            vistas.add(chave)
            # Antes do NTP o no publica ts nulo; a hora de chegada e a melhor
            # aproximacao disponivel e fica marcada como tal.
            ts = p["ts"]
            origem = "no" if ts is not None else "chegada"
            instante = ts if ts is not None else float(r["t_chegada"])
            linhas.append({
                "id": p["id"], "boot_id": p["boot_id"], "seq": p["seq"],
                "ts": "" if ts is None else ts,
                "ts_local": datetime.fromtimestamp(instante, FUSO).isoformat(timespec="seconds"),
                "ts_origem": origem,
                "t_chegada": r["t_chegada"],
                "sensor_ok": str(p["sensor_ok"]).lower(),
                "temp_c": "" if p["temp_c"] is None else p["temp_c"],
                "umid_pct": "" if p["umid_pct"] is None else p["umid_pct"],
            })

    linhas.sort(key=lambda l: (l["id"], l["boot_id"], l["seq"]))
    with a.saida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(linhas)
    print(f"[limpar] {len(linhas)} leituras unicas, {repetidas} repetidas descartadas")
    print(f"[limpar] saida: {a.saida}")


if __name__ == "__main__":
    main()
