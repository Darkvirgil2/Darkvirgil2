# Capitolo 8 — Regolazione e controllore d'impianto

**Cosa imparerai:** perché la rete elettrica ha bisogno di regolare gli impianti; cosa
significa regolare la potenza attiva e la reattiva; la differenza tra comando "ad anello
aperto" e "ad anello chiuso"; com'è fatto e come lavora un controllore d'impianto; cosa
deve succedere quando la comunicazione si interrompe.

## 8.1 Perché la rete chiede di regolare gli impianti

La rete elettrica deve rispettare in ogni istante due condizioni.

**1. Produzione e consumo devono essere in equilibrio.** L'elettricità non si accumula nei cavi:
quello che si produce deve essere consumato nello stesso istante. Se si produce troppo la
**frequenza** sale sopra i 50 Hz, se si produce troppo poco scende. Terna mantiene
l'equilibrio chiedendo alle centrali di aumentare o ridurre la produzione.

**2. La tensione deve restare nei limiti.** In ogni punto della rete la tensione deve stare vicino
al valore nominale, entro qualche punto percentuale. Un impianto che immette molta energia in
una linea lunga e poco carica fa **alzare la tensione** in quel tratto, a volte oltre i limiti.

Quando c'erano solo grandi centrali, il problema riguardava poche decine di impianti. Oggi i
generatori fotovoltaici ed eolici sono centinaia di migliaia: per mantenere la rete stabile il
gestore deve poterli **osservare** e, quando serve, **regolare**.

Le richieste più comuni sono:

- **limitare la potenza attiva** (P), per esempio perché una linea è congestionata o c'è troppa
  produzione rispetto ai consumi;
- **regolare la potenza reattiva** (Q), per aiutare a tenere la tensione nei limiti;
- **seguire delle rampe**: aumentare o diminuire la potenza gradualmente, senza salti bruschi;
- in alcuni casi, **immissione zero o limitata**: l'impianto può alimentare i consumi interni ma
  non deve immettere in rete oltre una certa soglia.

### Come la potenza reattiva aiuta la tensione

In prima approssimazione la potenza attiva influenza soprattutto i flussi di energia e, a livello
di sistema, la frequenza; la reattiva influenza soprattutto la **tensione**. Un impianto che
**assorbe** potenza reattiva tende ad **abbassare** la tensione nel suo punto di connessione;
uno che la **eroga** tende ad alzarla. Nelle reti di distribuzione anche la potenza attiva ha un
effetto non trascurabile sulla tensione, ma la reattiva è la leva che si può usare senza
rinunciare a produrre energia.

## 8.2 Funzioni locali e funzioni centralizzate

Alcune regolazioni le fa **ogni inverter da solo**, guardando le grandezze ai propri morsetti,
senza bisogno di comunicare:

- se la frequenza sale troppo, l'inverter riduce automaticamente la potenza (funzione P(f));
- può regolare la reattiva in funzione della tensione che misura (funzione Q(V));
- se tensione o frequenza escono dai limiti di sicurezza, l'SPI stacca l'impianto.

Queste funzioni sono rapide e non dipendono dalla comunicazione. Hanno però un limite: ogni
inverter vede solo sé stesso, mentre il gestore di rete è interessato a cosa succede al
**punto di connessione** dell'intero impianto. Qui entra in gioco il controllore d'impianto.

## 8.3 Anello aperto e anello chiuso

Prima di vedere il controllore, serve un concetto fondamentale della regolazione.

**Anello aperto.** Dai un comando e "ti fidi" che produca l'effetto voluto, senza verificarlo.

> **Esempio**
> Il gestore chiede che l'impianto immetta al massimo 600 kW. L'impianto ha 1000 kW di inverter.
> Il controllore invia a tutti gli inverter "limitatevi al 60%" e non fa altro.
> Risultato: al punto di connessione arrivano forse 570 kW, perché cavi, trasformatore e servizi
> ausiliari consumano una parte dell'energia. Oppure un inverter è guasto e il totale è più
> basso. L'obiettivo non è rispettato con precisione.

**Anello chiuso.** Dai un comando, **misuri** il risultato, confronti il risultato con l'obiettivo e
**correggi** il comando. E ricominci, continuamente.

È quello che fai sotto la doccia: apri l'acqua calda, senti la temperatura, la trovi fredda, giri
ancora un po' la manopola, la risenti… finché la temperatura è giusta. Oppure il regolatore di
velocità dell'automobile, che aumenta o riduce l'acceleratore guardando continuamente il
tachimetro.

```
           obiettivo                        comando
 Gestore ──(600 kW)──► [ confronto ] ──errore──► [ calcolo ] ──────► Inverter
                            ▲                                          │
                            │            misura al POI                 │
                            └────────── Analizzatore ◄─────── energia ─┘
```

Il controllore misura la potenza al punto di connessione, calcola l'**errore** (obiettivo −
misura) e corregge il comando agli inverter in proporzione all'errore. Se mancano 30 kW alza un
po' il limite, se ce ne sono 20 in più lo abbassa.

### Quanto correggere ogni volta?

Se a ogni ciclo si corregge **poco**, l'impianto arriva all'obiettivo lentamente ma con
dolcezza. Se si corregge **molto**, ci arriva velocemente ma rischia di superarlo, tornare
indietro, superarlo di nuovo: **oscilla**. La "forza" della correzione si chiama **guadagno**, e
sceglierla bene, cioè **tarare** il regolatore, è una parte importante della messa in servizio.
La difficoltà cresce se gli inverter impiegano qualche secondo a eseguire i comandi, perché il
controllore vede gli effetti in ritardo.

I regolatori industriali più comuni si chiamano **PI** (proporzionale-integrale): la parte
proporzionale reagisce all'errore attuale, quella integrale accumula gli errori passati per
eliminare anche le piccole differenze che rimarrebbero.

## 8.4 Il controllore d'impianto

Il **controllore d'impianto**, in inglese **PPC** (*Power Plant Controller*), è il dispositivo che
realizza l'anello chiuso. Negli impianti italiani in media tensione la norma CEI 0-16 lo chiama
**CCI**, Controllore Centrale di Impianto (capitolo 11). È di solito un PLC o un computer
industriale installato in cabina.

```
             Gestore di rete                SCADA / manutenzione
                   ▲  IEC 61850, IEC 104          ▲  IEC 104, OPC UA, Modbus TCP
                   │                              │
            ┌──────┴──────────────────────────────┴──────┐
            │        Controllore d'impianto (PPC / CCI)   │
            └──┬──────────────────┬───────────────────┬───┘
     Modbus TCP│                  │ Modbus TCP        │ ingressi e uscite
               ▼                  ▼ (SunSpec o mappe  ▼ cablati
        Analizzatore al POI    Inverter 1 … N  del    Interruttori,
        (P, Q, V, f, cos φ)    produttore)            protezioni
```

Il controllore comunica in tre direzioni:

1. **verso l'alto**, con il gestore di rete o lo SCADA: riceve obiettivi e comandi, invia misure e
   stati. Si usano protocolli robusti come IEC 61850 e IEC 60870-5-104 (capitoli 9 e 10);
2. **verso le misure**: legge l'analizzatore di rete al punto di connessione, di solito via Modbus TCP;
3. **verso il basso**: comanda gli inverter, di solito via Modbus TCP con i modelli SunSpec
   (capitolo 6) o con le mappe proprietarie. Alcuni produttori offrono comandi *broadcast* per
   raggiungere tutti gli inverter con un solo messaggio.

### Il ciclo di lavoro

Il controllore ripete continuamente lo stesso ciclo, in genere da qualche volta al secondo a una
volta al secondo:

1. **legge** l'obiettivo attuale (dal gestore di rete o da un valore impostato);
2. **misura** la potenza al punto di connessione;
3. **calcola** l'errore e il nuovo comando;
4. **distribuisce** il comando tra gli inverter, tenendo conto di quelli guasti o spenti;
5. **invia** i comandi, con un tempo di ritorno (capitolo 6);
6. **riporta** al gestore le misure e lo stato.

> **Esempio**
> Obiettivo: 25 kW al punto di connessione. Due inverter da 20 kW, che con il sole attuale
> producono insieme 35 kW. Il controllore parte dal 100%:
>
> | Ciclo | Misura | Errore | Nuovo limite |
> |---|---|---|---|
> | 1 | 35,1 kW | −10,1 kW | 87% |
> | 2 | 34,2 kW | −9,2 kW | 76% |
> | 3 | 30,3 kW | −5,3 kW | 69% |
> | … | … | … | … |
> | 10 | 25,0 kW | −0,04 kW | 62,5% |
>
> Il limite si assesta intorno al 62,5% (il 62,5% di 40 kW fa 25 kW). Se arriva una nuvola e
> gli inverter non hanno più potenza sufficiente, il controllore alza il limite fino al 100%
> e l'impianto produce quel che può.

## 8.5 Quando la comunicazione si interrompe

Un sistema di controllo serio deve sapere **cosa fare quando non sente più nessuno**. È la
domanda più importante del progetto, e va posta a ogni livello.

**Il controllore smette di comunicare con gli inverter.** Grazie al **tempo di ritorno** impostato
nei comandi, dopo un tempo prestabilito gli inverter tornano a un comportamento definito invece
di restare bloccati sull'ultimo comando. Questo comportamento può essere "produci liberamente"
o "vai a un valore di sicurezza", secondo le regole concordate.

**Il gestore di rete smette di comunicare con il controllore.** Il controllore deve sapere se
mantenere l'ultimo obiettivo ricevuto, tornare a un valore predefinito o applicare un valore di
sicurezza. Anche questo è stabilito dalle regole tecniche e dagli accordi con il gestore.

**L'analizzatore al punto di connessione non risponde.** Senza misura l'anello chiuso non può
funzionare. Il controllore deve accorgersene, segnalarlo e passare a una strategia di riserva,
per esempio un comando ad anello aperto prudente.

> **Ricorda**
> In ogni sistema di controllo chiediti: **chi si accorge** che la comunicazione si è interrotta,
> **in quanto tempo**, e **in quale stato** va il sistema. Se non sai rispondere a queste tre
> domande, il progetto non è finito.

## 8.6 Le altre domande di progetto

**Tempi.** Il gestore di rete stabilisce entro quanto tempo l'impianto deve rispondere a un nuovo
obiettivo. Nel ciclo rientrano il tempo di lettura delle misure, quello di calcolo, quello per
inviare i comandi a tutti gli inverter (capitolo 5: su RS-485 può essere lungo) e il tempo di
risposta degli inverter stessi, con le loro rampe.

**Sincronizzazione degli orologi.** Misure ed eventi devono avere un orario preciso e coerente tra
campo, controllore e gestore. Si usano protocolli come **NTP** o, dove serve una precisione molto
alta, **PTP**.

**Qualità del dato.** Una misura non valida va dichiarata tale, non sostituita con zero o con
l'ultimo valore senza dirlo. I protocolli dei capitoli 9 e 10 hanno campi appositi per la qualità.

**Sicurezza informatica.** Il controllore può spegnere un impianto: è un obiettivo appetibile per un
attacco. Servono rete separata, collegamento protetto con il gestore, accessi controllati, gestione
di password e certificati.

**Documentazione e collaudo.** L'elenco dei segnali scambiati con il gestore, le mappe dei registri,
i file di configurazione e i verbali delle prove fatte insieme al gestore sono parte del sistema
quanto i dispositivi.

## Riepilogo

- La rete deve mantenere **equilibrio** (frequenza) e **tensione**: per questo osserva e regola gli impianti.
- Richieste tipiche: limitare **P**, regolare **Q**, seguire **rampe**, immissione **zero o limitata**.
- Gli inverter hanno funzioni **locali** veloci; il **controllore d'impianto** regola ciò che conta al **punto di connessione**.
- **Anello chiuso**: misura, confronta, correggi, ripeti. Il **guadagno** decide velocità e rischio di oscillazione.
- Il controllore parla verso l'alto (IEC 61850, IEC 104), verso le misure e verso gli inverter (Modbus, SunSpec).
- Progetta sempre il comportamento in caso di **perdita di comunicazione** (tempo di ritorno, valori di sicurezza).

> **Prova**
> Nel [laboratorio Controllore d'impianto](#lab-ppc) avvia il controllore con 25 kW, cambia il
> guadagno e osserva il grafico. Poi premi «Simula guasto del PPC» e guarda cosa succede dopo
> due secondi.

## Domande di verifica

**1.** Perché un comando "limitatevi al 60%" inviato a tutti gli inverter non garantisce 600 kW al punto di connessione di un impianto da 1000 kW?

<details markdown="1">
<summary>Risposta</summary>

Perché tra inverter e punto di connessione ci sono perdite e consumi ausiliari, alcuni inverter
possono essere guasti o non avere abbastanza sole, e la potenza nominale non coincide sempre con
quella effettiva. Solo misurando al punto di connessione e correggendo (anello chiuso) si
rispetta l'obiettivo.

</details>

**2.** Cosa osservi se il guadagno del regolatore è troppo alto?

<details markdown="1">
<summary>Risposta</summary>

La potenza supera l'obiettivo, poi scende sotto, poi lo risupera: **oscilla** intorno al valore
voluto invece di assestarsi. Il fenomeno peggiora se gli inverter rispondono in ritardo.

</details>

**3.** Un impianto riceve dal gestore una limitazione a 3 MW. Il controllore si blocca. Cosa succede agli inverter se il tempo di ritorno è 0, cioè disattivato? E se è 60 s?

<details markdown="1">
<summary>Risposta</summary>

Con tempo di ritorno 0 gli inverter mantengono l'ultimo comando ricevuto **all'infinito**: se il
controllore si è bloccato mentre la limitazione era attiva, l'impianto resta limitato finché
qualcuno non interviene. Con 60 s, dopo un minuto senza rinnovi gli inverter tornano al
comportamento predefinito. Quale comportamento sia corretto, cioè tornare liberi o andare a un
valore di sicurezza, dipende dalle regole del gestore.

</details>

**4.** Per alzare la tensione nel punto di connessione, l'impianto deve erogare o assorbire potenza reattiva?

<details markdown="1">
<summary>Risposta</summary>

**Erogare** potenza reattiva tende ad alzare la tensione; assorbirla tende ad abbassarla.

</details>
