# Esercizi con il laboratorio Python

Apri tre terminali nella cartella `lab/`.

### Esercizio 1 — Leggere i byte
1. Terminale A: `python3 sim_inverter.py --trace`
2. Terminale B: `python3 client_sunspec.py --trace`
3. Trova nel trace la richiesta che legge il modello 103. Verifica a mano che l'indirizzo in
   esadecimale (`9C 88`) corrisponda a 40072 e la quantità (`00 32`) a 50.
4. Nella risposta, individua i due byte della potenza attiva `W` (offset 12 → byte 24–25 dei dati)
   e convertili in decimale.

### Esercizio 2 — Scale factor e "non implementato"
1. Avvia il simulatore con `--wmax 60000`. Cosa cambia in `W_SF`? Perché? (vedi `choose_sf`)
2. Perché `TmpSnk` appare come "n/d"? Che valore grezzo c'è nel registro?

### Esercizio 3 — Errori Modbus
Usando `mbtcp.ModbusTcpClient` in una shell Python:
```python
import mbtcp
c = mbtcp.ModbusTcpClient("127.0.0.1", 5020, trace=True).connect()
c.read_holding_registers(30000, 2)      # che eccezione ricevi?
c.write_single_register(40084, 0)       # e qui?
c.unit_id = 5; c.read_holding_registers(40000, 2)  # e qui? che ruolo ha l'Unit ID?
```

### Esercizio 4 — Limitazione di potenza e watchdog
1. `python3 client_sunspec.py --limit 30 --revert 15 --watch 3`
2. Osserva `St` passare a THROTTLED e la potenza scendere. Dopo 15 s cosa succede? Perché è una
   sicurezza importante?

### Esercizio 5 — Il controllore d'impianto
1. Avvia due simulatori: porte 5020 e 5021 (`--serial LAB0000002` per il secondo).
2. `python3 ppc.py --devices 127.0.0.1:5020 127.0.0.1:5021 --setpoint 25000`
3. Prova `--ki 0.1` e `--ki 1.5`: cosa succede alla convergenza? Cosa succederebbe con inverter reali
   che hanno una rampa di qualche secondo? (suggerimento: aggiungi un ritardo/rampa nel simulatore)
4. Interrompi il PPC con `kill -9` (non Ctrl+C): cosa fanno gli inverter dopo qualche secondo?

### Esercizio 6 — Datalogger
1. `python3 datalogger.py --devices 127.0.0.1:5020 127.0.0.1:5021 127.0.0.1:5099 --period 5`
2. Il terzo dispositivo non esiste: come viene registrato nel CSV? Perché è meglio che scrivere 0?
3. Sfida: installa un broker MQTT (es. Mosquitto) e la libreria `paho-mqtt`, e fai pubblicare davvero il payload.

### Esercizio 7 — Modbus RTU
1. `python3 modbus_rtu.py`, poi calcola il CRC di `01 06 9C BC 00 00` (scrittura singola).
2. Quanto tempo serve per leggere 20 inverter a 19200 baud con una sola richiesta da 50 registri ciascuno?

### Esercizio 8 — IEC 60870-5-104
1. `python3 iec104.py` e segui la sessione.
2. Decodifica: `python3 iec104.py 68 12 0A 00 06 00 0D 01 03 00 01 00 EA 03 00 00 00 48 42 00`
   — quale grandezza, con che indirizzo e che valore? Perché è "spontanea"?
3. Cosa cambia se il byte di qualità finale vale `80`?

### Per andare oltre
- Usa **pymodbus** (`pip install pymodbus`) per riscrivere il client con una libreria reale.
- Usa **pySunSpec2** per leggere il simulatore tramite le definizioni ufficiali dei modelli.
- Apri un trace con **Wireshark** (filtri `mbtcp`, `iec60870_104`, `mms`, `goose`): ha i
  dissector per tutti i protocolli di questo corso.
- Con un convertitore USB–RS-485 e un contatore Modbus economico puoi fare le stesse prove su un bus vero.
