# Protocolli di comunicazione nel fotovoltaico — percorso di studio

Un corso pratico, dal cavo RS-485 fino al controllore centrale d'impianto, con un laboratorio
Python **senza dipendenze esterne** in cui vedi ogni byte che viaggia sulla rete.

## Percorso consigliato

| # | Lezione | Cosa impari |
|---|---|---|
| 1 | [Fondamenti](01-fondamenti.md) | architettura di un impianto, livelli, RS-485, paradigmi (polling, eventi, pub/sub), trappole sui dati |
| 2 | [Modbus RTU e TCP](02-modbus.md) | frame byte per byte, function code, eccezioni, CRC, gateway, buone pratiche |
| 3 | [SunSpec](03-sunspec.md) | mappe standard degli inverter, discovery, scale factor, modelli 1/103/123 |
| 4 | [Portali di monitoraggio](04-monitoraggio.md) | datalogger, HTTPS/MQTT/SFTP, API REST, KPI, qualità del dato |
| 5 | [Controllore d'impianto e rete](05-controllo-impianto.md) | PPC/CCI, IEC 60870-5-104, IEC 61850, CEI 0-16 Allegati O e T |
| 6 | [Esercizi](06-esercizi.md) | 8 esercizi guidati sul laboratorio |
| 7 | [Glossario e risorse](07-glossario-e-risorse.md) | termini, standard, strumenti |

**Versione web per tablet e telefono**: [`web/corso.html`](web/corso.html) contiene il corso e un laboratorio interattivo in JavaScript, senza bisogno di Python (vedi [`web/README.md`](web/README.md)).

Suggerimento: dopo ogni lezione fai gli esercizi corrispondenti — i protocolli si capiscono
davvero solo guardando i frame.

## Il laboratorio (`lab/`)

Serve solo Python 3.8+.

| File | Ruolo nell'impianto | Protocollo |
|---|---|---|
| `sim_inverter.py` | **inverter** trifase simulato (giornata solare compressa, limitazione, watchdog) | server Modbus TCP + SunSpec |
| `client_sunspec.py` | strumento del **tecnico**: discovery e lettura, comandi di limitazione | client Modbus TCP + SunSpec |
| `datalogger.py` | **datalogger**: polling, CSV locale, payload JSON per il cloud (MQTT) | Modbus TCP → JSON |
| `ppc.py` | **controllore d'impianto**: regolazione ad anello chiuso della potenza al POI | Modbus TCP + SunSpec 123 |
| `modbus_rtu.py` | anatomia del frame **seriale**, CRC, tempi del bus RS-485, gateway TCP→RTU | Modbus RTU |
| `iec104.py` | sessione di **telecontrollo** impianto ↔ centro di controllo, decodificatore | IEC 60870-5-104 |
| `mbtcp.py`, `sunspec.py` | librerie didattiche (leggile: sono commentate) | |
| `test_lab.py` | test automatici | |

Avvio rapido:

```bash
cd lab
python3 sim_inverter.py --trace            # terminale 1: l'inverter
python3 client_sunspec.py --trace          # terminale 2: leggi tutto, byte per byte
python3 client_sunspec.py --limit 40 --revert 20 --watch 2   # limita al 40% per 20 s
python3 modbus_rtu.py                      # il mondo seriale
python3 iec104.py                          # il mondo del telecontrollo
python3 -m unittest -v test_lab.py         # verifica che tutto funzioni
```

> Il codice è volutamente minimale e didattico. Non usarlo per comandare impianti reali:
> in produzione si usano librerie mature, testate e configurate secondo i requisiti del gestore.
