# Capitolo 7 — Il monitoraggio: dal datalogger al portale

**Cosa imparerai:** cosa fa un datalogger; come i dati arrivano al cloud (HTTPS, MQTT, file);
cos'è il formato JSON; come funzionano le API dei portali; come si calcolano gli indicatori di
prestazione; quali errori rovinano la qualità dei dati.

## 7.1 La catena del dato

Il dato che vedi sul portale percorre una catena con tre anelli:

```
 Dispositivi ──(1)──► Datalogger ──(2)──► Cloud / portale ──(3)──► Altri software
 inverter,     Modbus   raccoglie,  Internet  archivia,       API    gestionali,
 contatori,    SunSpec  normalizza,           calcola,               SCADA di flotta,
 meteo                  conserva            mostra, allerta          fatturazione
```

1. **Campo**: il datalogger interroga i dispositivi, di solito via Modbus (capitoli 4–6).
2. **Trasferimento**: il datalogger invia i dati al cloud via Internet.
3. **Integrazione**: il portale mette i dati a disposizione di altri programmi tramite **API**.

Ogni anello può ritardare, perdere o trasformare il dato. Quando un numero sul portale "non
torna", si risale la catena anello per anello, esattamente come si risalgono i livelli del
capitolo 3.

## 7.2 Il datalogger

Il **datalogger** è un piccolo computer installato nell'impianto, spesso su barra DIN nel quadro.
Il suo lavoro si riassume in quattro verbi.

**Raccogliere.** Interroga periodicamente tutti i dispositivi: inverter, contatori, sensori
meteo, quadri di campo. Può usare Modbus, SunSpec o i protocolli proprietari dei produttori.
I datalogger venduti dai produttori di inverter parlano nativamente con i "loro" inverter;
quelli indipendenti supportano molte marche, con driver diversi.

**Normalizzare.** Converte i valori grezzi in grandezze con unità di misura: applica i fattori
di scala, interpreta gli stati e gli allarmi, uniforma i nomi.

**Conservare.** Salva i dati in una memoria locale. Se la connessione Internet cade per ore,
nessun dato si perde: verrà inviato appena la connessione torna. Questo principio si chiama
*store and forward* (memorizza e inoltra).

**Inviare.** Trasmette i dati al cloud a intervalli regolari, per esempio ogni 5 o 15 minuti,
oppure in tempo quasi reale.

### Tre regole d'oro per un buon datalogger

> **Ricorda**
> 1. **L'ora del dato è quella della misura, in UTC.** Il timestamp va messo quando il dato
>    viene letto, non quando arriva al server, e va espresso in tempo universale (UTC) per
>    evitare i pasticci del cambio d'ora legale, quando un'ora "si ripete" o "sparisce".
> 2. **Zero non è "dato mancante".** Un inverter che di notte produce 0 W è normale; un
>    inverter che non risponde va registrato come *assenza di dato*. Se il datalogger scrive
>    0 quando la comunicazione fallisce, il portale non può più distinguere un guasto di
>    comunicazione da un inverter fermo.
> 3. **Per l'energia, invia il contatore.** Invece di inviare "energia prodotta negli ultimi 5
>    minuti", conviene inviare il valore del contatore totale e calcolare le differenze sul
>    server. Così, se un pacchetto si perde, il totale della giornata resta corretto.

## 7.3 Come i dati arrivano al cloud

Esistono quattro metodi principali. Prima però serve capire il formato con cui i dati
viaggiano più spesso.

### Il formato JSON

**JSON** è un modo standard di scrivere dati strutturati come testo, leggibile sia dalle
persone sia dai programmi. Usa coppie *nome: valore*, raggruppate tra parentesi graffe `{ }`,
ed elenchi tra parentesi quadre `[ ]`.

```json
{
  "impianto": "Campo Sud",
  "ora": "2026-06-21T10:15:00Z",
  "inverter": [
    { "seriale": "LAB0000001", "potenza_W": 18500, "energia_Wh": 1234567, "stato": "MPPT" },
    { "seriale": "LAB0000002", "errore": "nessuna risposta" }
  ]
}
```

La `Z` finale nell'ora indica UTC. Nota come il secondo inverter non ha valori inventati:
riporta un errore.

### Metodo 1: HTTPS

Il datalogger invia periodicamente un messaggio JSON al server del portale usando **HTTPS**, lo
stesso protocollo dei siti web, cifrato. Tecnicamente invia una richiesta di tipo **POST** a un
indirizzo come `https://portale.example/api/dati`. Il server risponde con un **codice di
stato**: 200 o 201 significa "ricevuto", 401 "non autorizzato", 500 "errore del server".

È semplice e attraversa senza problemi firewall e router, perché è traffico web in uscita.

### Metodo 2: MQTT

**MQTT** è un protocollo leggero progettato per i dispositivi che inviano dati di continuo.
Funziona secondo il modello *pubblica e iscriviti* (capitolo 3):

- al centro c'è un **broker**, un server che smista i messaggi;
- il datalogger **pubblica** i dati su un **argomento** (*topic*), un nome gerarchico come
  `fv/campo-sud/inverter1/misure`;
- il portale, e chiunque sia autorizzato, si **iscrive** agli argomenti che gli interessano e
  riceve i messaggi appena arrivano;
- con i caratteri jolly ci si iscrive a molti argomenti insieme: `fv/campo-sud/+/misure`
  riceve le misure di tutti gli inverter dell'impianto.

Alcune caratteristiche utili:

- **QoS** (qualità del servizio): 0 = "al massimo una volta" (può perdersi), 1 = "almeno una
  volta" (può arrivare doppio), 2 = "esattamente una volta";
- **messaggio conservato** (*retained*): il broker tiene l'ultimo valore e lo consegna subito a
  chi si iscrive dopo;
- **ultime volontà** (*last will*): un messaggio che il broker pubblica da solo se il datalogger
  si disconnette all'improvviso. È il modo standard per sapere che un impianto è "offline".

Porte tipiche: 1883 in chiaro, **8883** cifrata con TLS, da preferire sempre. MQTT trasporta i
messaggi ma non dice com'è fatto il loro contenuto: il formato, spesso JSON, lo decide chi
progetta il sistema.

### Metodo 3: file CSV via FTP o SFTP

Il datalogger scrive ogni 5–15 minuti un file **CSV**, una tabella di testo con valori separati
da virgole o punti e virgola, e lo carica su un server con **FTP** o, meglio, **SFTP** (la versione
cifrata). È il metodo più vecchio ma è universale: quasi tutti i datalogger lo supportano. Il
portale deve però gestire file duplicati, incompleti o in ritardo.

> **Attenzione**
> FTP trasmette password e dati **in chiaro**: chiunque intercetti il traffico li legge. Usa
> SFTP o FTPS.

### Metodo 4: accesso diretto via VPN

Il portale si collega all'impianto attraverso una VPN e interroga direttamente datalogger o
dispositivi. Dà accesso completo e in tempo reale, ma richiede un'infrastruttura VPN da gestire
e mantenere sicura.

| Metodo | Punti di forza | Punti deboli |
|---|---|---|
| HTTPS | semplice, sicuro, passa ovunque | un messaggio per invio, meno efficiente per dati frequenti |
| MQTT | leggero, in tempo reale, segnala lo stato offline | richiede un broker e un formato dei messaggi concordato |
| CSV via SFTP | universale, facile da integrare | ritardo, gestione dei file |
| VPN | accesso completo | complessità e sicurezza da curare |

## 7.4 Le API dei portali

Un'**API** (*Application Programming Interface*) è una "porta di servizio" che un programma
offre ad altri programmi. Le API dei portali fotovoltaici sono quasi sempre **REST**: si
interrogano via HTTPS con richieste di tipo **GET** a indirizzi che descrivono la risorsa
voluta, e rispondono in JSON.

> **Esempio**
> Una richiesta come
> `GET https://api.portale.example/impianti/123/energia?da=2026-06-01&a=2026-06-30&passo=giorno`
> potrebbe restituire l'energia giornaliera di giugno dell'impianto 123 come elenco JSON di
> date e valori. Gli indirizzi reali dipendono dal portale e sono descritti nella sua
> documentazione.

Elementi che ritrovi in quasi tutte le API:

- **Autenticazione**: una chiave segreta (*API key*) o un *token* da inviare con ogni richiesta.
  Va custodita come una password.
- **Limiti di utilizzo** (*rate limit*): un numero massimo di richieste al minuto o al giorno.
  Superato il limite, il server risponde con il codice 429. Bisogna quindi pianificare le
  letture e salvare i dati in locale invece di richiederli ogni volta.
- **Granularità**: dati ogni 5 o 15 minuti, giornalieri o mensili.
- **Fuso orario**: verifica sempre se le ore restituite sono UTC o locali.

Alcuni inverter hanno anche un'**API locale**: rispondono in JSON direttamente sulla rete
dell'impianto, senza passare dal cloud. È comoda per integrazioni domotiche.

## 7.5 Cosa calcola un portale

### Energia

Si ricava dalla differenza tra due letture del contatore: energia di oggi = contatore alle
24:00 − contatore alle 00:00.

### Rendimento specifico

L'energia prodotta divisa per la potenza installata (kWh/kWp). Permette di confrontare impianti
di taglia diversa: un impianto che fa 4,5 kWh/kWp in una giornata estiva al Sud sta lavorando bene.

### Performance Ratio (PR)

Il **PR** è l'indicatore più importante: confronta l'energia prodotta con quella che l'impianto
avrebbe dovuto produrre **con il sole effettivamente disponibile**. Elimina così l'effetto del
meteo: un giorno nuvoloso produce poco, ma il PR può essere ottimo.

> PR = energia prodotta ÷ (potenza installata × irraggiamento ÷ 1 kW/m²)

> **Esempio**
> Impianto da 1000 kWp. In un giorno il piranometro sul piano dei moduli misura un
> irraggiamento totale di 5,5 kWh/m². L'impianto "ideale" avrebbe prodotto
> 1000 kWp × 5,5 kWh/m² ÷ 1 kW/m² = 5500 kWh. L'impianto ha prodotto 4600 kWh.
> PR = 4600 ÷ 5500 = **83,6%**. Tipicamente un buon impianto sta tra l'80% e il 90%.

Il PR dipende interamente dal sensore di irraggiamento: un piranometro sporco o starato rende
il PR inaffidabile. Per questo i sensori meteo vanno puliti e calibrati.

### Disponibilità

La percentuale di tempo in cui l'impianto, con il sole presente, era in grado di produrre.
Le definizioni contrattuali variano: conta come indisponibile anche una limitazione chiesta
dal gestore di rete? Va concordato.

### Allarmi

Un portale genera allarmi da più fonti:

- **dai dispositivi**: bit di allarme come `Evt1` di SunSpec, oppure lo stato `St = 7 FAULT`;
- **da confronti**: un inverter che produce il 20% in meno di quelli vicini; una stringa con
  corrente più bassa delle altre;
- **dall'assenza di dati**: un impianto che non invia nulla da un'ora.

## 7.6 La qualità del dato

La maggior parte dei problemi di monitoraggio non è "il portale è lento", ma **dati sbagliati
che sembrano giusti**. Le cause più comuni, in ordine di frequenza:

1. **Orari sbagliati**: datalogger con orologio non sincronizzato, ora legale gestita male.
2. **Zeri al posto di dati mancanti**.
3. **Unità o fattori di scala sbagliati**: kW scambiati per W, fattore di scala ignorato.
4. **Contatori che si azzerano**: dopo la sostituzione di un inverter il contatore riparte da zero
   e la differenza diventa un'enorme energia negativa.
5. **Dispositivi scambiati**: l'inverter 3 configurato al posto del 4, così gli allarmi
   puntano all'apparecchio sbagliato.
6. **Sensori meteo sporchi o orientati male**.

## 7.7 Sicurezza

- Il datalogger deve connettersi **in uscita** verso il cloud con protocolli cifrati (HTTPS, MQTT
  su TLS, SFTP), senza porte aperte in ingresso.
- Cambiare le password predefinite, aggiornare il firmware.
- Tenere la rete dell'impianto separata da quella degli uffici e della videosorveglianza.

## Riepilogo

- Catena: **campo → datalogger → cloud → API**. I problemi si cercano anello per anello.
- Il datalogger raccoglie, normalizza, conserva (*store and forward*) e invia.
- Regole d'oro: **ora UTC alla sorgente**, **zero ≠ dato mancante**, **inviare i contatori**.
- Trasferimento: **HTTPS** (POST JSON), **MQTT** (broker, topic, QoS, last will), **CSV via SFTP**, **VPN**.
- **API REST**: richieste GET in HTTPS, risposte JSON, chiave segreta, limiti di utilizzo.
- **PR** = energia reale ÷ energia attesa con il sole misurato; dipende dal sensore di irraggiamento.

## Domande di verifica

**1.** La connessione Internet di un impianto è caduta dalle 10 alle 14. Alle 14 torna. Cosa si vede sul portale se il datalogger fa *store and forward*? E se non lo fa?

<details markdown="1">
<summary>Risposta</summary>

Con *store and forward* i dati delle 10–14, salvati in locale, vengono inviati appena la
connessione torna e lo storico è completo. Senza, sul portale resta un buco di quattro ore. Se
però il datalogger invia il contatore di energia, l'energia totale della giornata resta comunque
corretta.

</details>

**2.** Un impianto da 500 kWp ha prodotto 2000 kWh in un giorno con irraggiamento di 5 kWh/m². Calcola il PR. È un buon risultato?

<details markdown="1">
<summary>Risposta</summary>

Energia attesa = 500 × 5 = 2500 kWh. PR = 2000 ÷ 2500 = **80%**. È al limite inferiore di un
risultato buono: vale la pena controllare guasti, sporcizia dei moduli e sensore di irraggiamento.

</details>

**3.** Il topic MQTT è `fv/campo-sud/inv07/misure`. A cosa ti iscrivi per ricevere le misure di tutti gli inverter di tutti gli impianti?

<details markdown="1">
<summary>Risposta</summary>

`fv/+/+/misure`: il carattere `+` sostituisce un singolo livello del topic.

</details>

**4.** Perché un datalogger che scrive "0 W" quando un inverter non risponde rende impossibile calcolare correttamente la disponibilità?

<details markdown="1">
<summary>Risposta</summary>

Perché il portale non può distinguere "l'inverter era fermo" (indisponibile) da "l'inverter
produceva ma non comunicava" (disponibile, dato mancante). Entrambi appaiono come zero.

</details>
