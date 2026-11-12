#!/usr/bin/env python3
"""
ppc.py - Un controllore d'impianto (PPC / "power plant controller") giocattolo.

Obiettivo: mantenere la potenza immessa al punto di connessione (POI) sotto un limite,
per esempio perche' il gestore di rete lo ha richiesto (via IEC 61850 o IEC 60870-5-104)
o perche' l'impianto e' "a immissione zero / limitata".

Ciclo di controllo (ogni --period secondi):
  1. MISURA  : legge la potenza di ogni inverter (nella realta' si legge un MISURATORE al POI,
               perche' tra inverter e POI ci sono perdite, trasformatori, servizi ausiliari);
  2. CALCOLA : regolatore integrale -> nuova percentuale di limitazione;
  3. ATTUA   : scrive il limite (SunSpec modello 123) su tutti gli inverter, con un timeout
               di ritorno (watchdog): se il PPC si blocca, gli inverter non restano limitati
               all'infinito ne' continuano a seguire un comando vecchio.

    python3 ppc.py --devices 127.0.0.1:5020 127.0.0.1:5021 --setpoint 25000
"""

import argparse
import time

import mbtcp
import sunspec


class Inverter:
    def __init__(self, spec):
        host, port, *unit = spec.split(":")
        self.name = spec
        self.client = mbtcp.ModbusTcpClient(host, int(port), int(unit[0]) if unit else 1).connect()
        _base, self.models = sunspec.discover(self.client)

    def power(self):
        return sunspec.read_model(self.client, self.models, 103)["W"][0] or 0.0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--devices", nargs="+", default=["127.0.0.1:5020"])
    p.add_argument("--wmax", type=float, default=20000, help="Potenza nominale di OGNI inverter (W)")
    p.add_argument("--setpoint", type=float, required=True, help="Potenza massima al POI (W)")
    p.add_argument("--period", type=float, default=1.0)
    p.add_argument("--ki", type=float, default=0.5, help="Guadagno integrale")
    p.add_argument("--cycles", type=int, default=0)
    args = p.parse_args()

    inverters = [Inverter(d) for d in args.devices]
    capacity = args.wmax * len(inverters)
    pct = 100.0
    revert = max(1, int(3 * args.period))
    print(f"PPC: {len(inverters)} inverter, {capacity/1000:g} kW installati, "
          f"setpoint al POI {args.setpoint/1000:g} kW, watchdog {revert}s")

    cycle = 0
    try:
        while True:
            t_start = time.monotonic()
            total = sum(inv.power() for inv in inverters)
            error = args.setpoint - total
            # Regolatore integrale: corregge la % in proporzione all'errore.
            pct = min(100.0, max(0.0, pct + args.ki * error / capacity * 100))
            for inv in inverters:
                sunspec.set_power_limit(inv.client, inv.models, round(pct, 2), revert)
            latency = (time.monotonic() - t_start) * 1000
            print(f"POI={total/1000:7.2f} kW  errore={error/1000:+7.2f} kW  "
                  f"limite inviato={pct:6.2f}%  ciclo={latency:.0f} ms")
            cycle += 1
            if args.cycles and cycle >= args.cycles:
                break
            time.sleep(max(0, args.period - (time.monotonic() - t_start)))
    except KeyboardInterrupt:
        pass
    finally:
        # Uscita pulita: tolgo il limite. (Se il PPC "muore" male, interviene il watchdog.)
        for inv in inverters:
            try:
                sunspec.set_power_limit(inv.client, inv.models, None)
            finally:
                inv.client.close()
        print("Limiti rimossi, PPC fermato.")


if __name__ == "__main__":
    main()
