# Capitolo 3 — Come viaggiano i dati: seriale e rete

**Cosa imparerai:** l'idea dei "livelli" di una comunicazione; come funziona un bus seriale
RS-485 e come si cabla correttamente; cosa sono Ethernet, indirizzo IP, porta e connessione
TCP; i tre modi di organizzare un dialogo (interrogazione, eventi, pubblicazione).

## 3.1 L'idea dei livelli

Riprendiamo la telefonata del capitolo 0. Se la comunicazione non funziona, il problema può
stare a livelli molto diversi: il telefono è scarico, la linea è disturbata, l'altra persona
parla un'altra lingua, oppure parla italiano ma intende "cabina" in un altro senso. Per
trovare il guasto conviene controllare i livelli uno alla volta, dal basso.

Con i dispositivi elettronici è lo stesso. Per i nostri scopi bastano quattro livelli:

| Livello | Domanda | Esempi |
|---|---|---|
| **1. Fisico** | Che cavo? Che segnali elettrici? | RS-485, Ethernet in rame, fibra ottica, rete cellulare 4G |
| **2. Trasporto** | Come arriva il messaggio integro al destinatario giusto? | indirizzo seriale e controllo d'errore; indirizzo IP e TCP |
| **3. Applicazione** | Che cosa chiedo, che cosa rispondo? | «Leggi 50 registri a partire da 40072» |
| **4. Significato** | Cosa vogliono dire i numeri ricevuti? | «Il registro 40084 è la potenza attiva in watt» |

> **Ricorda**
> Quando qualcosa non funziona, risali i livelli dal basso: prima il cavo e i LED di
> collegamento, poi gli indirizzi, poi le richieste, infine il significato dei dati. Molte
> ore perse sul campo nascono dal cercare un errore al livello 4 quando il problema è al
> livello 1, o viceversa.

Nell'informatica si usa un modello più dettagliato, il **modello OSI** a sette livelli. Se lo
incontri, sappi che i nostri quattro livelli ne sono una versione semplificata.

## 3.2 La comunicazione seriale e RS-485

### Cos'è "seriale"

Si dice **seriale** una comunicazione in cui i bit viaggiano uno dopo l'altro sullo stesso
filo, a una velocità stabilita. La velocità si misura in **baud**, che qui possiamo
considerare equivalente ai bit al secondo. Valori tipici: **9600**, **19 200**, 38 400, 115 200.

Ogni byte viaggia "incorniciato" da bit di servizio: un **bit di start** che dice "sta
arrivando un byte", gli 8 bit di dati, un eventuale **bit di parità** per un semplice
controllo d'errore e uno o due **bit di stop**. La combinazione si scrive in forma compatta:
**8N1** significa 8 bit di dati, nessuna parità (*None*), 1 bit di stop; **8E1** significa
parità pari (*Even*) e 1 bit di stop.

> **Attenzione**
> Velocità, bit di dati, parità e bit di stop devono essere **identici** su tutti i
> dispositivi dello stesso cavo. Un solo dispositivo a 9600 baud su un bus a 19 200 non
> risponde mai, e a volte disturba anche gli altri.

### RS-485

**RS-485** è lo standard elettrico seriale più usato negli impianti fotovoltaici. Le sue
caratteristiche spiegano perché:

- **Segnale differenziale.** Usa una coppia di fili intrecciati, chiamati **A** e **B** (o D+ e D−).
  L'informazione è nella *differenza* di tensione tra i due fili. Un disturbo
  elettromagnetico, frequente vicino agli inverter, colpisce entrambi i fili allo stesso
  modo e la differenza resta intatta. Per questo funziona bene in ambienti rumorosi.
- **Distanze lunghe.** Fino a circa 1200 metri a velocità basse.
- **Molti dispositivi sullo stesso cavo.** Fino a 32 "carichi" standard per tratto (di più con
  dispositivi moderni a basso carico): tutti gli inverter di un campo possono stare sulla
  stessa linea, chiamata **bus**.
- **Uno parla alla volta** (*half-duplex*). Gli stessi due fili servono per trasmettere e per
  ricevere, quindi serve un **dispositivo che decide i turni**. Nel capitolo 4 vedremo che in
  Modbus questo ruolo è del *master*.

### Come si cabla un bus RS-485

```
 Datalogger          Inverter 1         Inverter 2         Inverter 3
 [120 Ω]──A──────────────●──────────────────●──────────────────●──[120 Ω]
          B──────────────●──────────────────●──────────────────●
          GND────────────●──────────────────●──────────────────●
   ▲                                                              ▲
   inizio del bus: terminazione                  fine del bus: terminazione
```

- **A catena (*daisy chain*)**: il cavo entra in un dispositivo ed esce verso il successivo.
  Niente stelle e niente derivazioni lunghe: creano riflessioni del segnale, come un'eco.
- **Terminazione da 120 Ω** ai **due estremi** del bus, e solo lì. Molti dispositivi hanno un
  interruttore o un ponticello per inserirla.
- **Polarizzazione** (*bias*): resistenze che tengono la linea in uno stato definito quando
  nessuno trasmette. Di solito le fornisce il master.
- **Cavo schermato a coppie intrecciate**, con lo schermo collegato a terra **da un solo lato**.
- **Riferimento comune (GND)**, spesso trascurato ma importante su distanze lunghe.

> **Attenzione**
> I produttori non sono d'accordo su quale filo chiamare A e quale B. Se un dispositivo
> nuovo non risponde, una delle prime prove è **invertire A e B** su quel dispositivo.

## 3.3 Ethernet e le reti IP

Negli impianti recenti la comunicazione passa sempre più spesso su **Ethernet**: lo stesso
tipo di rete degli uffici, con cavi in rame fino a 100 m, fibra ottica per le distanze lunghe
e **switch** che collegano tra loro i dispositivi.

### Indirizzo IP

Ogni dispositivo in rete ha un **indirizzo IP**, che identifica "chi è" sulla rete, come un
numero civico. Si scrive come quattro numeri da 0 a 255 separati da punti, per esempio
**192.168.1.20**.

Insieme all'indirizzo si configura la **maschera di sottorete** (*subnet mask*, spesso
255.255.255.0, scritto anche "/24"). Indica quali dispositivi sono "nella stessa via" e si
possono raggiungere direttamente: con /24, tutti quelli che hanno uguali i primi tre numeri
(192.168.1.x). Per raggiungere indirizzi diversi serve un **gateway** (o *router*), un
dispositivo che fa da ponte verso altre reti, per esempio verso Internet.

> **Esempio**
> Datalogger 192.168.1.10/24, inverter 192.168.1.20/24: stessa rete, si parlano direttamente.
> Se l'inverter avesse 192.168.2.20, il datalogger non lo raggiungerebbe senza un router.
> È uno degli errori di configurazione più comuni.

### Porta

Un dispositivo può offrire più servizi contemporaneamente: una pagina web di configurazione,
il protocollo Modbus, un servizio di aggiornamento. Per distinguerli si usa la **porta**, un
numero da 0 a 65 535. Se l'indirizzo IP è il numero civico, la porta è l'interno
dell'appartamento. Alcune porte sono convenzionali:

| Porta | Servizio |
|---|---|
| 502 | Modbus TCP |
| 2404 | IEC 60870-5-104 |
| 102 | IEC 61850 (MMS) |
| 1883 / 8883 | MQTT (in chiaro / cifrato) |
| 80 / 443 | Web, HTTP / HTTPS |

### TCP: la connessione affidabile

Sopra IP lavora quasi sempre **TCP**, che crea una **connessione** tra due programmi e
garantisce che i dati arrivino tutti, integri e nell'ordine giusto: se un pezzo si perde,
TCP lo ritrasmette da solo. Il programma che apre la connessione si chiama **client**; quello
che attende connessioni su una porta si chiama **server**.

> **Esempio**
> Il datalogger (client) apre una connessione TCP verso 192.168.1.20 porta 502. L'inverter
> (server Modbus) accetta. Da quel momento il datalogger può inviare richieste e ricevere
> risposte sulla stessa connessione, finché uno dei due non la chiude.

Esiste anche **UDP**, più leggero e senza garanzie di consegna; nel nostro ambito è poco
usato, a parte casi particolari.

## 3.4 Tre modi di organizzare un dialogo

Indipendentemente dal cavo, i protocolli organizzano lo scambio di informazioni in tre modi.

**1. Interrogazione (*polling*).** Uno chiede, l'altro risponde. È come un insegnante che
interroga gli studenti uno per uno. Semplice e prevedibile, ma chi chiede deve ripetere le
domande in continuazione anche se nulla è cambiato, e un evento importante viene scoperto
solo alla domanda successiva. È il modello di **Modbus**.

**2. Segnalazione spontanea (a eventi).** Il dispositivo invia un'informazione quando cambia,
per esempio quando un interruttore si apre o una misura varia più di una soglia. È come
un collega che ti chiama quando c'è una novità. Meno traffico, reazione immediata, e
l'evento può portare con sé l'ora esatta in cui è avvenuto. È il modello di **IEC 104** e
**IEC 61850** (capitoli 9 e 10).

**3. Pubblicazione e iscrizione (*publish/subscribe*).** Chi produce dati li "pubblica" su un
argomento presso un intermediario; chi è interessato si "iscrive" a quell'argomento e li
riceve. È come una newsletter. Ottimo per mandare dati al cloud: è il modello di **MQTT**
(capitolo 7).

## 3.5 Un cenno alla sicurezza

Molti protocolli del campo sono nati quando gli impianti erano isolati e **non prevedono
password né cifratura**: chiunque raggiunga la porta di un inverter può leggerlo e, a volte,
comandarlo. Le regole di base sono:

- **non esporre mai** i dispositivi di campo direttamente su Internet;
- separare la rete dell'impianto da altre reti (uffici, telecamere, ospiti);
- per l'accesso da remoto usare una **VPN**, un "tunnel" cifrato che rende il collegamento
  esterno sicuro come se fossi in impianto;
- un **firewall** che lasci passare solo le comunicazioni necessarie.

## Riepilogo

- Quattro livelli: **fisico, trasporto, applicazione, significato**. I guasti si cercano dal basso.
- **RS-485**: due fili differenziali, a catena, terminazioni da 120 Ω agli estremi, uno parla alla volta, parametri seriali identici su tutti.
- **Ethernet/IP**: indirizzo IP (chi), porta (quale servizio), TCP (connessione affidabile tra client e server).
- Dialoghi: **interrogazione** (Modbus), **eventi** (IEC 104, IEC 61850), **pubblicazione** (MQTT).
- I protocolli di campo spesso non sono protetti: rete separata, VPN, firewall.

## Domande di verifica

**1.** Su un bus RS-485 con 10 inverter, l'ultimo inverter non risponde mai, gli altri sì. Cosa controlli?

<details markdown="1">
<summary>Risposta</summary>

Livello fisico: collegamento del cavo, A/B invertiti, terminazione presente all'estremità
(e solo lì). Poi i parametri seriali dell'inverter (velocità, parità) e il suo indirizzo, che
potrebbe essere diverso da quello atteso o duplicato.

</details>

**2.** Cosa succede se la terminazione da 120 Ω viene inserita su tutti e 10 gli inverter?

<details markdown="1">
<summary>Risposta</summary>

Dieci resistenze da 120 Ω in parallelo equivalgono a 12 Ω: il carico sulla linea diventa
eccessivo, il segnale si indebolisce e la comunicazione diventa instabile o impossibile.

</details>

**3.** Un datalogger con IP 10.0.0.5/24 deve leggere un inverter con IP 10.0.1.7/24. Si raggiungono direttamente?

<details markdown="1">
<summary>Risposta</summary>

No: con maschera /24 sono nella stessa rete solo gli indirizzi che iniziano con 10.0.0.
L'inverter è in 10.0.1.x. Bisogna cambiare uno dei due indirizzi o passare attraverso un router.

</details>

**4.** Perché per mandare dati al cloud si preferisce che sia il datalogger ad aprire la connessione, e non il cloud?

<details markdown="1">
<summary>Risposta</summary>

Perché così non serve aprire porte in ingresso nel firewall dell'impianto: la connessione
parte dall'interno verso l'esterno, come quando navighi in Internet. È molto più sicuro e
funziona anche dietro router e reti cellulari.

</details>
