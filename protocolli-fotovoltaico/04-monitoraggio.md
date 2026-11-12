# Lezione 4 — Protocolli dei portali di monitoraggio

## 4.1 La catena del dato

```
Dispositivo  ──(1) campo──►  Datalogger  ──(2) WAN──►  Cloud/portale  ──(3) API──►  Altri software
inverter,     Modbus RTU/TCP,  buffer locale,   HTTPS, MQTT,    database a serie   REST/JSON,
contatori,    SunSpec,         normalizzazione  SFTP/FTP (CSV), temporali, KPI,     webhook,
meteo         proprietari                       VPN             allarmi            export CSV
```

Ogni anello introduce latenza, possibili perdite e trasformazioni del dato: quando un numero sul
portale "non torna", si risale la catena anello per anello.

## 4.2 (1) Il lato campo

- **Inverter**: Modbus RTU su RS-485 (impianti più vecchi e residenziali), Modbus TCP (impianti
  recenti), SunSpec o mappe proprietarie. Alcuni produttori usano protocolli proprietari sul bus
  (il datalogger del produttore li "parla" nativamente, quelli di terze parti no).
- **Contatori / analizzatori di rete**: quasi sempre Modbus. I **contatori fiscali** di produzione
  e scambio usano invece protocolli metrologici (IEC 62056 / DLMS-COSEM, porta ottica) e sono letti
  dal distributore; il monitoraggio di solito legge un *analizzatore* parallelo o le uscite impulsi.
- **Sensori meteo**: piranometri e celle di riferimento (irraggiamento), sonde di temperatura
  modulo e ambiente, anemometri — Modbus RTU o uscite analogiche (4–20 mA, 0–10 V) acquisite da
  un modulo I/O.
- **String box / string monitoring**: correnti di stringa, utili per trovare stringhe guaste.

## 4.3 (2) Dal datalogger al cloud

| Metodo | Come funziona | Pro | Contro |
|---|---|---|---|
| **HTTPS push (POST JSON)** | il logger invia ogni N minuti un pacchetto di dati | semplice, attraversa i firewall | overhead per messaggio |
| **MQTT** (spesso su TLS, porta 8883) | il logger pubblica su un *topic* presso un *broker* | leggero, connessione persistente, QoS, ideale per dati frequenti | serve un broker, schema del payload da definire |
| **FTP/SFTP con file CSV** | il logger carica un file ogni 5–15 min | universale, facile importare da logger di marche diverse | latenza, gestione file duplicati/parziali; FTP in chiaro è da evitare |
| **Pull via VPN** | il portale interroga direttamente il logger o i dispositivi | accesso completo in tempo reale | infrastruttura VPN, porte, sicurezza |

Principi di un buon datalogger (li trovi in `lab/datalogger.py`):

- **Store & forward**: memorizza in locale e reinvia quando la connessione torna → nessun buco nei dati.
- **Timestamp alla sorgente in UTC**, non all'arrivo sul server. Attenzione all'ora legale!
- **Distinguere "0" da "dato mancante"**: inverter spento di notte ≠ inverter che non comunica.
- **Aggregazione**: medie/min/max su 1, 5 o 15 minuti; per l'energia meglio inviare il **valore del contatore** (cumulativo) e calcolare le differenze lato server, così una perdita di dati non altera il totale.

### MQTT in 5 righe

- **Broker**: il server centrale. **Client**: chi pubblica e chi si iscrive.
- **Topic** gerarchici: `pv/<impianto>/<dispositivo>/telemetry`; wildcard `+` e `#` per iscriversi.
- **QoS** 0 (al più una volta), 1 (almeno una volta), 2 (esattamente una volta).
- **Retained message**: l'ultimo valore resta disponibile per chi si iscrive dopo.
- **Last Will**: messaggio pubblicato dal broker se il client si disconnette male → stato "offline".
  Il formato del payload (JSON, Sparkplug B, ecc.) non è definito da MQTT: lo decidi tu.

## 4.4 (3) Le API dei portali (northbound)

I portali dei produttori (e quelli indipendenti) espongono API, quasi sempre **REST su HTTPS
con JSON**, per integrare i dati in altri software (SCADA di flotta, gestionali, fatturazione).
Elementi ricorrenti:

- **Autenticazione**: API key, token OAuth2, login con sessione/cookie.
- **Rate limit**: numero massimo di chiamate al giorno/minuto → occorre pianificare le letture,
  usare endpoint "bulk" e salvare in locale.
- **Granularità**: dati a 5/15 minuti, giornalieri, mensili; i dati "in tempo reale" spesso sono limitati.
- **Fusi orari**: verificare sempre se i timestamp sono locali o UTC.

Alcuni inverter offrono anche un'**API HTTP locale** (JSON sulla rete dell'impianto): comoda per
integrazioni domotiche senza passare dal cloud.

> Le API cambiano nel tempo: fai sempre riferimento alla documentazione ufficiale e corrente
> del produttore (di solito richiede registrazione).

## 4.5 Cosa calcola un portale con questi dati

- **Energia** prodotta (dai contatori cumulativi), **potenza** istantanea.
- **Performance Ratio (PR)** = energia reale / energia teorica attesa con l'irraggiamento misurato
  → serve un sensore di irraggiamento affidabile e sincronizzato con i dati elettrici.
- **Disponibilità** tecnica (tempo in cui l'impianto poteva produrre ed era funzionante).
- **Allarmi**: da bit di evento (es. SunSpec `Evt1`), da stati (`St = 7 Fault`), da confronti
  (un inverter produce il 20% in meno dei vicini), da **assenza di comunicazione**.

## 4.6 Sicurezza

- Datalogger che si connette **in uscita** verso il cloud (TLS) > porte aperte in ingresso.
- Credenziali di default cambiate, firmware aggiornati, VPN per l'accesso remoto.
- Rete di impianto separata (VLAN/firewall) dalla rete ospiti / uffici / videosorveglianza.
