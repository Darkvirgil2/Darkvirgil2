#!/usr/bin/env python3
"""
datalogger.py - Il "ponte" tra il campo e il portale di monitoraggio.

Un datalogger reale (es. quelli che trovi nei quadri di campo) fa esattamente questo:
  1. interroga periodicamente i dispositivi in campo (inverter, contatori, sensori) via Modbus;
  2. normalizza i dati (scale factor, unita', stati);
  3. li salva in locale (buffer: se Internet cade, i dati non si perdono);
  4. li invia al cloud: qui mostriamo il messaggio JSON che verrebbe pubblicato via MQTT
     (o inviato con una POST HTTPS) - l'invio vero e' lasciato come esercizio.

    python3 datalogger.py --devices 127.0.0.1:5020 127.0.0.1:5021 --period 5
"""

import argparse
import csv
import datetime as dt
import json
import os
import time

import mbtcp
import sunspec

FIELDS = ["W", "WH", "PhVphA", "Hz", "DCV", "DCW", "TmpCab", "St"]


def poll(host, port, unit):
    with mbtcp.ModbusTcpClient(host, port, unit, timeout=2) as client:
        _base, models = sunspec.discover(client)
        common = sunspec.read_model(client, models, 1)
        inv = sunspec.read_model(client, models, 103)
    return common["SN"][0], {k: inv[k][0] for k in FIELDS}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--devices", nargs="+", default=["127.0.0.1:5020"], help="host:porta[:unit]")
    p.add_argument("--period", type=float, default=5, help="Periodo di campionamento (s)")
    p.add_argument("--csv", default="misure.csv")
    p.add_argument("--plant-id", default="impianto-demo")
    p.add_argument("--cycles", type=int, default=0, help="Numero di cicli (0 = infinito)")
    args = p.parse_args()

    new_file = not os.path.exists(args.csv)
    with open(args.csv, "a", newline="") as fh:
        writer = csv.writer(fh)
        if new_file:
            writer.writerow(["timestamp_utc", "device", "serial"] + FIELDS + ["comm_ok"])
        cycle = 0
        while True:
            ts = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
            payload = {"plant": args.plant_id, "ts": ts, "devices": []}
            for dev in args.devices:
                host, port, *unit = dev.split(":")
                unit = int(unit[0]) if unit else 1
                try:
                    serial, data = poll(host, int(port), unit)
                    writer.writerow([ts, dev, serial] + [data[k] for k in FIELDS] + [1])
                    payload["devices"].append({"sn": serial, **data})
                except (OSError, ConnectionError, RuntimeError, mbtcp.ModbusException) as exc:
                    # Un buon datalogger registra ANCHE l'assenza di comunicazione:
                    # sul portale e' diverso "0 W" da "dato mancante".
                    writer.writerow([ts, dev, ""] + [""] * len(FIELDS) + [0])
                    payload["devices"].append({"device": dev, "error": str(exc)})
            fh.flush()
            topic = f"pv/{args.plant_id}/telemetry"
            print(f"MQTT publish  topic={topic}\n  {json.dumps(payload)}")
            cycle += 1
            if args.cycles and cycle >= args.cycles:
                break
            time.sleep(args.period)


if __name__ == "__main__":
    main()
