# Capitolo 5 — Modbus sul campo: RTU, TCP, gateway e diagnosi

**Cosa imparerai:** come la stessa PDU viene "imbustata" in Modbus RTU e in Modbus TCP; a
cosa serve il CRC; quanto tempo richiede leggere un impianto; cosa fa un gateway; una
procedura per trovare i guasti di comunicazione.

## 5.1 La busta e la lettera

Nel capitolo 4 abbiamo visto la **PDU**, il "contenuto" di un messaggio Modbus: codice
funzione e dati. Per spedirla serve una "busta" con l'indirizzo del destinatario e, a
seconda del mezzo, altre informazioni di servizio. Busta e lettera insieme si chiamano **ADU**
(*Application Data Unit*).

La lettera, cioè la PDU, è **identica** in RTU e in TCP. Cambia solo la busta:

```
Modbus RTU:   [ indirizzo slave ] [ PDU ] [ CRC ]
Modbus TCP:   [ intestazione MBAP (7 byte, contiene l'Unit ID) ] [ PDU ]
```

## 5.2 Modbus RTU

### Com'è fatto il messaggio

Riprendiamo la lettura di 50 registri da 40072 per lo slave numero 1:

```
01  03 9C 88 00 32  6A 65
│   └──── PDU ────┘  └─┬─┘
│                     CRC
indirizzo dello slave
```

- **`01`**: indirizzo dello slave a cui è destinato il messaggio;
- **`03 9C 88 00 32`**: la PDU che conosci già;
- **`6A 65`**: il **CRC**, un controllo d'errore.

### Il CRC: un "codice di controllo"

Su un cavo lungo, vicino a inverter e motori, un disturbo può cambiare un bit durante la
trasmissione. Il **CRC** (*Cyclic Redundancy Check*) serve ad accorgersene.

Funziona così: chi trasmette fa un calcolo matematico su tutti i byte del messaggio e ottiene
un numero da 16 bit, che aggiunge in fondo. Chi riceve rifà lo stesso calcolo sui byte
ricevuti: se il risultato coincide con il CRC ricevuto il messaggio è integro; se è diverso,
qualcosa si è rovinato per strada.

È come la cifra di controllo del codice fiscale o dell'IBAN: un errore di battitura viene
scoperto quasi sempre. Non serve saper fare il calcolo a mano. Ricorda però due cose:

- in Modbus RTU il CRC si trasmette con il **byte basso per primo** (little-endian), al
  contrario di tutto il resto del messaggio;
- se il CRC è sbagliato lo slave **scarta il messaggio in silenzio**, senza rispondere. Il
  master vede un **timeout**, non un'eccezione.

> **Esempio**
> Il messaggio classico degli esempi Modbus `01 03 00 00 00 0A` ha CRC 0xCDC5, trasmesso
> come `C5 CD`. Il messaggio completo è `01 03 00 00 00 0A C5 CD`. Se un disturbo trasforma
> il quarto byte da `00` a `01`, il CRC ricalcolato non coincide più e lo slave ignora il
> messaggio.

### Dove finisce un messaggio?

Sul bus non c'è un carattere speciale di "fine messaggio". La regola è temporale: un messaggio
finisce quando la linea resta in silenzio per almeno **3,5 caratteri**. A 9600 baud un
carattere (11 bit) dura circa 1,15 ms, quindi il silenzio è di circa 4 ms; sopra i 19 200 baud
la norma lo fissa a 1,75 ms. Per questo le pause tra un messaggio e l'altro non sono un
dettaglio: un convertitore o un software che "spezza" un messaggio con una pausa troppo lunga
lo rende illeggibile.

### Il messaggio "a tutti"

L'indirizzo **0** è riservato al **broadcast**: il messaggio è per tutti gli slave e nessuno
risponde. Si usa solo per le scritture, per esempio per dare lo stesso comando a tutti gli
inverter contemporaneamente. Il master però non riceve conferme.

## 5.3 Modbus TCP

### L'intestazione MBAP

In Modbus TCP la busta è un'intestazione di 7 byte chiamata **MBAP**. La stessa richiesta
diventa:

```
00 07  00 00  00 06  01  03 9C 88 00 32
└─┬─┘  └─┬─┘  └─┬─┘  │   └──── PDU ────┘
  │      │      │    Unit ID
  │      │      Length: quanti byte seguono (Unit ID + PDU = 1 + 5 = 6)
  │      Protocol ID: sempre 0 per Modbus
  Transaction ID: numero progressivo della richiesta
```

- **Transaction ID**: il client numera ogni richiesta e il server ricopia lo stesso numero
  nella risposta. Così, se più richieste sono in viaggio, il client sa abbinare le risposte.
- **Protocol ID**: vale sempre 0.
- **Length**: il numero di byte che seguono questo campo.
- **Unit ID**: equivalente dell'indirizzo dello slave. Vedremo tra poco quando conta.

Non c'è CRC: dell'integrità dei dati si occupa già TCP (capitolo 3). La porta standard è la **502**.

### L'Unit ID

Se il client parla direttamente con un inverter collegato in rete, l'inverter spesso ignora
l'Unit ID o si aspetta un valore fisso, di solito 1 oppure 255: lo dice il manuale. L'Unit ID
diventa fondamentale con i **gateway**.

## 5.4 Il gateway: un traduttore tra TCP e RTU

Spesso il datalogger o il controllore d'impianto è in rete Ethernet, mentre gli inverter sono
su un bus RS-485. In mezzo si mette un **gateway Modbus TCP/RTU**, un piccolo dispositivo che
traduce:

```
 Datalogger ──Ethernet── Gateway ──RS-485── Inverter 1, 2, 3 …
           Modbus TCP              Modbus RTU
```

Il gateway riceve la richiesta TCP, toglie l'intestazione MBAP, usa l'**Unit ID** come
indirizzo dello slave sul bus, aggiunge il CRC e trasmette. Quando arriva la risposta fa il
percorso inverso.

> **Esempio**
> Richiesta TCP `00 07 00 00 00 06 03 03 9C 88 00 32` con Unit ID 3.
> Il gateway trasmette sul bus `03 03 9C 88 00 32 + CRC`: è per l'inverter con indirizzo 3.

Se lo slave non risponde, il gateway restituisce al client l'eccezione **0B** (*gateway
target failed to respond*). Ricevere 0B significa quindi: la rete fino al gateway funziona,
il problema è sul bus seriale o nello slave.

## 5.5 Quanto tempo ci vuole a leggere un impianto?

Su RS-485 i messaggi viaggiano uno alla volta. Facciamo il conto per una lettura di 50 registri:

- la richiesta RTU è di 8 byte; la risposta è 1 (indirizzo) + 1 (codice) + 1 (numero di byte)
  + 100 (dati) + 2 (CRC) = 105 byte; in totale 113 byte;
- a 9600 baud, con 11 bit per carattere, un byte richiede circa 1,15 ms: 113 byte ≈ 130 ms;
- a questo si aggiungono le pause e il tempo che lo slave impiega a rispondere, spesso tra 20 e 100 ms.

Diciamo **circa 200 ms per inverter**. Con 30 inverter sullo stesso bus un giro completo
richiede **circa 6 secondi**. Per un portale che salva dati ogni 5 minuti va benissimo; per un
controllore d'impianto che deve reagire in un secondo no.

> **Ricorda**
> Il tempo di un giro di letture cresce con il numero di dispositivi e di registri e cala
> con la velocità del bus. Per gli impianti grandi si usano più bus in parallelo, Modbus TCP
> o protocolli più veloci per il controllo.

Su Modbus TCP i tempi sono molto più bassi, ma attenzione a un altro limite: molti dispositivi
accettano **poche connessioni contemporanee**, a volte una sola. Se datalogger e controllore
d'impianto vogliono leggere lo stesso inverter, uno dei due può restare escluso.

## 5.6 Buone pratiche di lettura

- **Leggere a blocchi.** Una richiesta da 50 registri è molto più efficiente di 50 richieste da 1.
- **Non sconfinare.** Se il blocco richiesto comprende registri inesistenti, molti dispositivi
  rifiutano l'intera richiesta con l'eccezione 02.
- **Timeout e tentativi ragionevoli.** Un timeout troppo corto genera falsi errori, uno troppo
  lungo rallenta tutto il giro.
- **Leggere insieme ciò che va insieme.** Un valore e il suo fattore di scala (capitolo 6), o le
  due parole di un numero a 32 bit, vanno letti nella stessa richiesta, altrimenti si rischia
  di combinare dati di istanti diversi.
- **Non scrivere in continuazione le impostazioni.** Alcuni registri sono salvati in una memoria
  che si consuma con le scritture. I comandi frequenti, come la limitazione di potenza, vanno
  inviati sui registri previsti apposta.

## 5.7 Diagnosi: una procedura passo per passo

Quando un dispositivo "non comunica", segui i livelli del capitolo 3:

1. **Alimentazione e cavo**: il dispositivo è acceso? Il cavo è collegato e integro? In Ethernet, i LED della porta sono accesi?
2. **RS-485**: A e B sono corretti (prova a invertirli)? Le terminazioni sono solo agli estremi?
3. **Parametri**: indirizzo dello slave, velocità, parità e bit di stop (RTU); indirizzo IP, maschera e porta (TCP).
4. **Una lettura semplice**: leggi pochi registri noti con un software di prova. Ottieni dati, un'eccezione o un timeout?
5. **Eccezione**: correggi la richiesta (codice funzione, indirizzo, quantità) consultando la mappa.
6. **Dati strani**: controlla numerazione da 0 o da 1, ordine di byte e parole, segno, fattore di scala.

## 5.8 Sicurezza

Modbus **non ha password né cifratura**: chiunque raggiunga la porta 502 di un inverter può
leggerlo e, se l'inverter lo permette, comandarlo, per esempio spegnendolo. Valgono le regole
del capitolo 3: mai la porta 502 su Internet, rete d'impianto separata, firewall che accetti
connessioni solo da datalogger e controllore, VPN per l'accesso remoto. Esiste una variante
sicura, *Modbus/TCP Security* (porta 802, con cifratura TLS), ma è ancora poco diffusa nei
dispositivi fotovoltaici.

## Riepilogo

- ADU = busta + PDU. La PDU è uguale in RTU e TCP.
- **RTU**: indirizzo + PDU + **CRC** (byte basso per primo); un CRC errato produce un timeout, non un'eccezione; i messaggi sono separati dal silenzio.
- **TCP**: intestazione **MBAP** di 7 byte (Transaction ID, Protocol ID, Length, Unit ID) + PDU; porta 502; niente CRC.
- Il **gateway** traduce TCP in RTU usando l'Unit ID come indirizzo; l'eccezione 0B indica problemi dietro il gateway.
- Il tempo di lettura su RS-485 cresce con dispositivi e registri: va calcolato.
- Diagnosi dal basso: cavo, parametri, lettura semplice, poi significato dei dati.

> **Prova**
> Nel [laboratorio Modbus RTU](#lab-rtu) calcola il CRC di un messaggio, guarda come il
> gateway trasforma un messaggio TCP in RTU e prova il calcolatore dei tempi del bus con
> 30 dispositivi a 9600 baud.

## Domande di verifica

**1.** Nel messaggio TCP `00 2A 00 00 00 06 01 03 00 64 00 0A`, quanto valgono Transaction ID, Unit ID, indirizzo e quantità?

<details markdown="1">
<summary>Risposta</summary>

Transaction ID 0x002A = 42; Unit ID 1; codice 03; indirizzo 0x0064 = 100; quantità 0x000A = 10.

</details>

**2.** Un datalogger collegato a un gateway riceve sempre l'eccezione 0B dall'inverter 4, mentre gli altri rispondono. Dove cerchi il guasto?

<details markdown="1">
<summary>Risposta</summary>

Sul bus RS-485 e sull'inverter 4: indirizzo impostato sull'inverter, parametri seriali, cablaggio
del suo tratto. La rete Ethernet fino al gateway funziona, altrimenti non arriverebbe nemmeno
l'eccezione.

</details>

**3.** Perché in Modbus TCP non serve il CRC?

<details markdown="1">
<summary>Risposta</summary>

Perché TCP garantisce già che i dati arrivino integri e nell'ordine giusto, con i suoi
controlli d'errore e le ritrasmissioni automatiche.

</details>

**4.** Un impianto ha 40 inverter su un unico bus a 9600 baud, letti ciascuno in circa 200 ms. Il controllore d'impianto deve aggiornare i comandi ogni secondo. Funziona?

<details markdown="1">
<summary>Risposta</summary>

No: un giro di sole letture richiede circa 40 × 0,2 = 8 secondi. Bisogna dividere gli
inverter su più bus, aumentare la velocità, ridurre i registri letti, usare comandi broadcast
o passare a Modbus TCP.

</details>
