# Protocolli di comunicazione nel fotovoltaico

Un libro di studio, scritto partendo da zero, su come comunicano inverter, contatori,
datalogger, portali di monitoraggio, controllori d'impianto e gestori di rete. Ogni capitolo
spiega i concetti prima di usarli e contiene esempi svolti, riquadri e domande di verifica
con risposta.

## Il libro (`libro/`)

| Cap. | Titolo | Argomenti |
|---|---|---|
| 0 | [Prima di cominciare](libro/00-introduzione.md) | cos'è un protocollo, come studiare |
| 1 | [Bit, byte e numeri esadecimali](libro/01-bit-byte-esadecimale.md) | binario, esadecimale, ordine dei byte, segno, float, ASCII |
| 2 | [L'impianto fotovoltaico e i suoi attori](libro/02-impianto-e-attori.md) | dispositivi, grandezze elettriche, distributore, Terna |
| 3 | [Come viaggiano i dati: seriale e rete](libro/03-seriale-e-rete.md) | RS-485, Ethernet, IP, porte, TCP, modelli di dialogo |
| 4 | [Modbus: i concetti](libro/04-modbus-concetti.md) | master e slave, registri, codici funzione, eccezioni |
| 5 | [Modbus sul campo](libro/05-modbus-sul-campo.md) | RTU e CRC, TCP e MBAP, gateway, tempi, diagnosi |
| 6 | [SunSpec](libro/06-sunspec.md) | modelli, discovery, fattori di scala, limitazione di potenza |
| 7 | [Il monitoraggio](libro/07-monitoraggio.md) | datalogger, JSON, HTTPS, MQTT, API, Performance Ratio |
| 8 | [Regolazione e controllore d'impianto](libro/08-regolazione-e-controllore.md) | perché si regola, anello chiuso, PPC, perdita di comunicazione |
| 9 | [IEC 60870-5-104](libro/09-iec-104.md) | telecontrollo, IOA, causa, qualità, sessione |
| 10 | [IEC 61850](libro/10-iec-61850.md) | modello dati, nodi logici, report, GOOSE, SCL |
| 11 | [Le regole italiane: CEI 0-16 e CCI](libro/11-normativa-italiana.md) | ARERA, CEI, Allegati O e T, obblighi |
| A | [Glossario](libro/12-glossario.md) | tutti i termini e le risorse per approfondire |

## Versione web per tablet e telefono (`web/`)

[`web/corso.html`](web/corso.html) contiene l'intero libro e un laboratorio interattivo che gira
nel browser: inverter SunSpec simulato con i byte visibili, controllore d'impianto, Modbus RTU e
IEC 104, più otto esercizi con soluzione. Vedi [`web/README.md`](web/README.md).

## Laboratorio Python (`lab/`)

Per chi usa un computer, la stessa simulazione in Python, senza dipendenze esterne:

| File | Ruolo | Protocollo |
|---|---|---|
| `sim_inverter.py` | inverter trifase simulato | server Modbus TCP + SunSpec |
| `client_sunspec.py` | discovery, lettura e comandi | client Modbus TCP + SunSpec |
| `datalogger.py` | polling, CSV, messaggio JSON per il cloud | Modbus TCP → JSON |
| `ppc.py` | controllore d'impianto ad anello chiuso | Modbus TCP + SunSpec 123 |
| `modbus_rtu.py` | frame seriale, CRC, tempi del bus, gateway | Modbus RTU |
| `iec104.py` | sessione di telecontrollo e decodificatore | IEC 60870-5-104 |
| `test_lab.py` | test automatici | |

```bash
cd lab
python3 sim_inverter.py --trace            # terminale 1: l'inverter
python3 client_sunspec.py --trace          # terminale 2: leggi tutto, byte per byte
python3 -m unittest -v test_lab.py         # verifica che tutto funzioni
```

Gli esercizi per la versione Python sono in [`esercizi-laboratorio-python.md`](esercizi-laboratorio-python.md).

> Il codice è didattico. Non usarlo per comandare impianti reali.
