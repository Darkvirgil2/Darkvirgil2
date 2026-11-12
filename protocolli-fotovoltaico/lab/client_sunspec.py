#!/usr/bin/env python3
"""
client_sunspec.py - Client Modbus TCP che "scopre" un dispositivo SunSpec e ne legge i dati.

Esempi:
    python3 client_sunspec.py                         # legge 127.0.0.1:5020
    python3 client_sunspec.py --trace                 # mostra ogni byte scambiato
    python3 client_sunspec.py --watch 2               # rilegge ogni 2 secondi
    python3 client_sunspec.py --limit 40              # limita la potenza al 40%
    python3 client_sunspec.py --limit 40 --revert 30  # ...con ritorno automatico dopo 30 s
    python3 client_sunspec.py --release               # rimuove il limite
"""

import argparse
import time

import mbtcp
import sunspec


def fmt(value, unit):
    if value is None:
        return "n/d (non implementato)"
    return f"{value} {unit}".strip()


def print_model(title, data, only=None):
    print(f"\n== {title} ==")
    for name, (value, unit, desc, raw) in data.items():
        if only and name not in only:
            continue
        extra = ""
        if name == "St" and value is not None:
            extra = f"  -> {sunspec.INVERTER_STATES.get(value, '?')}"
        raw_txt = "" if isinstance(raw, str) or raw is None else f"  [grezzo={raw}]"
        print(f"  {name:<19} {fmt(value, unit):<26}{raw_txt}{extra}   {desc}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5020)
    p.add_argument("--unit", type=int, default=1)
    p.add_argument("--trace", action="store_true", help="Stampa i frame Modbus in esadecimale")
    p.add_argument("--watch", type=float, metavar="SEC", help="Ripeti la lettura ogni SEC secondi")
    p.add_argument("--limit", type=float, metavar="PCT", help="Imposta il limite di potenza in %%")
    p.add_argument("--revert", type=int, default=0, metavar="SEC",
                   help="Timeout di ritorno del limite (0 = permanente)")
    p.add_argument("--release", action="store_true", help="Disabilita il limite di potenza")
    args = p.parse_args()

    with mbtcp.ModbusTcpClient(args.host, args.port, args.unit, trace=args.trace) as client:
        base, models = sunspec.discover(client)
        print(f"Marker SunS trovato all'indirizzo {base}. Modelli presenti:")
        for mid, start, length in models:
            title = sunspec.MODELS.get(mid, ("sconosciuto",))[0]
            print(f"  - modello {mid:<4} ({title}) dati da {start} a {start + length - 1} (L={length})")

        print_model("Modello 1 - Common", sunspec.read_model(client, models, 1))

        if args.limit is not None:
            sunspec.set_power_limit(client, models, args.limit, args.revert)
            print(f"\n>>> Limite impostato al {args.limit}% (revert={args.revert}s)")
        if args.release:
            sunspec.set_power_limit(client, models, None)
            print("\n>>> Limite rimosso")

        while True:
            print_model("Modello 103 - Inverter trifase", sunspec.read_model(client, models, 103))
            print_model("Modello 123 - Comandi", sunspec.read_model(client, models, 123),
                        only={"Conn", "WMaxLimPct", "WMaxLimPct_RvrtTms", "WMaxLim_Ena"})
            if not args.watch:
                break
            time.sleep(args.watch)


if __name__ == "__main__":
    main()
