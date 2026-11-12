# Lezione 2 — Modbus RTU e Modbus TCP, byte per byte

Modbus (1979) è il protocollo più diffuso nel fotovoltaico perché è semplice, aperto e
supportato da ogni dispositivo. Lo trovi tra datalogger e inverter, tra PPC e inverter,
verso contatori, analizzatori di rete, stazioni meteo, string box.

## 2.1 Il modello dati di Modbus: quattro tabelle

| Tabella | Dimensione | Accesso | Function code tipici | Uso nel FV |
|---|---|---|---|---|
| Coils | 1 bit | lettura/scrittura | 01, 05, 15 | comandi on/off (raro) |
| Discrete inputs | 1 bit | sola lettura | 02 | stati digitali |
| **Input registers** | 16 bit | sola lettura | **04** | misure (alcuni produttori) |
| **Holding registers** | 16 bit | lettura/scrittura | **03, 06, 16** | misure e comandi (SunSpec usa solo questi) |

Nella documentazione trovi spesso la notazione "Modicon":
`0xxxx` coils, `1xxxx` discrete inputs, `3xxxx` input registers, `4xxxx` holding registers.
Quindi "registro 40001" significa: *holding register numero 1* → **indirizzo 0 nel frame**.
SunSpec invece indica direttamente l'indirizzo di protocollo **40000** (cioè "registro 40001").

> Se leggi valori "sfasati di uno" (es. trovi lo scale factor dove ti aspetti la potenza),
> quasi sempre è un problema di indirizzamento base 0 / base 1.

## 2.2 La PDU: uguale in RTU e TCP

La *Protocol Data Unit* è la parte comune: `function code (1 byte) + dati`.

**Richiesta FC03** – leggi 50 holding register a partire da 40072 (= 0x9C88):

```
03 9C 88 00 32
│  └─┬─┘ └─┬─┘
│    │     └── quantità: 0x0032 = 50 registri
│    └──────── indirizzo iniziale: 0x9C88 = 40072
└───────────── function code 03 = Read Holding Registers
```

**Risposta**: `03 64 <100 byte di dati>` → FC, byte count (0x64 = 100), poi i registri in big-endian.

**Risposta di eccezione**: `83 02` → FC con il bit alto a 1 (0x03 | 0x80) e codice di errore:

| Codice | Nome | Causa tipica |
|---|---|---|
| 01 | Illegal function | il dispositivo non supporta quella funzione (es. FC04 invece di FC03) |
| 02 | Illegal data address | indirizzo inesistente, o lettura che "sconfina" in una zona vuota |
| 03 | Illegal data value | valore fuori range, quantità > 125 |
| 04 | Server device failure | errore interno |
| 06 | Server busy | riprova più tardi |
| 0B | Gateway target failed to respond | il gateway TCP→RTU non ha avuto risposta dallo slave seriale |

Limiti: max **125 registri** per lettura, **123** per scrittura multipla.

## 2.3 Modbus RTU (seriale, RS-485)

```
[indirizzo slave 1 byte][PDU][CRC-16 2 byte, byte basso per primo]
 01                     03 9C 88 00 32   6A 65
```

- Indirizzi slave 1–247 (0 = broadcast, solo scritture, nessuna risposta).
- Fine frame riconosciuta da **3,5 caratteri di silenzio** (≈ 4 ms a 9600 baud).
- Parametri da far combaciare: baud (9600 / 19200 / 38400…), bit di dati (8), parità (E/N/O),
  bit di stop. Lo standard vuole 11 bit per carattere (8E1 o 8N2), ma tanti dispositivi usano 8N1.
- Il **CRC** protegge dagli errori di linea: un frame corrotto viene scartato *in silenzio*
  → il master vede un **timeout**, non un errore.

Prova: `python3 lab/modbus_rtu.py` (calcola CRC, tempi di bus, conversione TCP→RTU).

## 2.4 Modbus TCP (Ethernet)

```
[Transaction ID 2][Protocol ID 2 = 0][Length 2][Unit ID 1][PDU]
 00 07             00 00              00 06     01         03 9C 88 00 32
```

- Porta TCP **502**. Niente CRC (ci pensa TCP).
- **Transaction ID**: il client lo incrementa, il server lo ricopia → abbina risposte e richieste.
- **Unit ID**: per un dispositivo collegato direttamente spesso è ignorato (o deve valere 1 / 255);
  per un **gateway** TCP↔RTU indica l'indirizzo dello slave sul bus seriale dietro di lui.

Prova: avvia `python3 lab/sim_inverter.py --trace` e in un altro terminale
`python3 lab/client_sunspec.py --trace`: vedrai ogni byte in entrambe le direzioni.

## 2.5 Valori a 32 bit, float e stringhe

Un registro = 16 bit. Per valori più grandi servono più registri:

- `uint32`/`acc32` (contatori di energia): 2 registri. Valore = `hi × 65536 + lo` (se word order big-endian).
- `float32` IEEE-754: 2 registri. Molti contatori espongono float; SunSpec preferisce interi + scale factor.
- Stringhe: 2 caratteri ASCII per registro.

Esempio: contatore = 1 234 567 Wh → 0x0012D687 → registri `[0x0012, 0xD687]` = `[18, 54919]`.
Se il dispositivo usa il word swap leggerai `[54919, 18]` → valore assurdo 3 599 171 602 Wh.

## 2.6 Buone pratiche di polling (esperienza di campo)

- **Leggi a blocchi**: una richiesta da 50 registri è molto meglio di 50 richieste da 1.
- Ma **non sconfinare** in zone non mappate: molti inverter rispondono con eccezione 02 all'intera richiesta.
- Imposta **timeout** e **retry** ragionevoli; distingui "timeout" (problema di linea/indirizzo) da "eccezione" (il dispositivo ha risposto, ma la richiesta è sbagliata).
- Su RS-485 considera il **tempo di ciclo**: (n° dispositivi × tempo per dispositivo). Vedi il calcolo in `modbus_rtu.py`.
- Su TCP molti dispositivi accettano **poche connessioni contemporanee** (a volte 1!). Se datalogger e PPC leggono lo stesso inverter, uno dei due può restare fuori.
- **Scritture**: evita di scrivere continuamente parametri salvati in memoria non volatile (EEPROM/flash) — si usurano. I comandi "dinamici" (limitazione di potenza) vanno sui registri pensati per quello (es. SunSpec 123/704).

## 2.7 Sicurezza

Modbus **non ha autenticazione né cifratura**: chiunque raggiunga la porta 502 può leggere e
*comandare* l'inverter. Regole minime: mai esporre la 502 su Internet, segmentare la rete di
impianto, accesso remoto solo via VPN, firewall che permetta il 502 solo dal datalogger/PPC.
Esiste *Modbus/TCP Security* (TLS, porta 802), ancora poco diffuso nei dispositivi FV.
