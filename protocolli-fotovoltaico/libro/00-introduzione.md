# Capitolo 0 — Prima di cominciare

## Di cosa parla questo libro

Un impianto fotovoltaico non è fatto solo di pannelli e inverter. Accanto ai cavi che
trasportano l'energia corre un secondo sistema di cavi, e oggi anche di connessioni radio e
Internet, che trasporta **informazioni**. Grazie a queste informazioni:

- il proprietario vede sul telefono quanta energia ha prodotto oggi il suo impianto;
- il tecnico che fa manutenzione riceve un allarme quando un inverter si guasta;
- il gestore della rete elettrica sa quanta potenza l'impianto sta immettendo e, se serve,
  può chiedergli di ridurla;
- un piccolo computer installato nella cabina dell'impianto regola continuamente gli
  inverter perché l'impianto nel suo insieme rispetti le richieste del gestore di rete.

Perché tutti questi dispositivi possano capirsi devono seguire delle regole comuni. Queste
regole si chiamano **protocolli di comunicazione**. Questo libro ti accompagna dalla base,
cioè da cosa sono un bit e un byte, fino ai protocolli usati tra un impianto e il gestore
della rete elettrica.

## Che cos'è un protocollo, in parole semplici

Pensa a una telefonata di lavoro. Perché funzioni, le due persone devono essere d'accordo su
molte cose, quasi sempre senza pensarci:

1. **il mezzo**: usano entrambe un telefono collegato alla rete telefonica;
2. **come si inizia e come si finisce**: chi chiama dice «Pronto», chi risponde si presenta,
   alla fine ci si saluta;
3. **la lingua**: parlano entrambe italiano;
4. **il significato delle parole**: se uno dice «la cabina», entrambi devono intendere la
   stessa cabina.

Un protocollo di comunicazione tra dispositivi elettronici fissa esattamente le stesse cose,
ma con una precisione assoluta, perché le macchine non sanno interpretare né chiedere
chiarimenti. Stabilisce che tipo di cavo usare, come si riconosce l'inizio e la fine di un
messaggio, in che ordine stanno le informazioni dentro il messaggio e che cosa significa
ogni numero.

> **Ricorda**
> Un **protocollo** è un insieme di regole, scritte in un documento chiamato *specifica* o
> *norma*, che due dispositivi devono rispettare per scambiarsi informazioni. Se anche una
> sola regola non è rispettata, per esempio l'ordine di due byte, la comunicazione fallisce
> oppure, peggio, produce numeri sbagliati che sembrano giusti.

## Come è organizzato il libro

Il libro procede dal basso verso l'alto: ogni capitolo usa solo concetti già spiegati nei
capitoli precedenti.

| Capitolo | Argomento | A cosa ti serve |
|---|---|---|
| 1 | Bit, byte e numeri esadecimali | È la "lingua" in cui sono scritti tutti i messaggi. Senza questo capitolo il resto è incomprensibile |
| 2 | L'impianto fotovoltaico e i suoi attori | Capire chi parla con chi e quali grandezze si misurano |
| 3 | Come viaggiano i dati: seriale e rete | Cavi RS-485, Ethernet, indirizzi IP, porte, client e server |
| 4 | Modbus: i concetti | Il protocollo più diffuso tra i dispositivi di un impianto |
| 5 | Modbus sul campo | CRC, tempi, gateway, errori e come trovarli |
| 6 | SunSpec | Come si dà un significato standard ai dati degli inverter |
| 7 | Il monitoraggio | Datalogger, cloud, Internet, MQTT, API, indicatori di prestazione |
| 8 | Regolazione e controllore d'impianto | Perché la rete chiede di regolare gli impianti e come lo si fa |
| 9 | IEC 60870-5-104 | Il protocollo dei centri di telecontrollo |
| 10 | IEC 61850 | Il modello dati delle sottostazioni e del CCI |
| 11 | Le regole italiane: CEI 0-16 e CCI | Cosa è richiesto agli impianti in media tensione |
| A | Glossario | Tutti i termini in ordine alfabetico |

## Come studiare

- **Leggi in ordine**, almeno la prima volta. I capitoli 1 e 3 possono sembrare lontani dal
  fotovoltaico, ma sono quelli che rendono facili tutti gli altri.
- **Fai gli esempi con carta e penna.** Quando il testo converte un numero o scompone un
  messaggio, prova a rifarlo da solo prima di leggere la soluzione.
- **Usa il laboratorio.** Nella versione web del libro trovi un laboratorio che simula un
  inverter, un controllore d'impianto e i protocolli descritti. Nel testo i riquadri **Prova**
  ti dicono quando è il momento di usarlo.
- **Rispondi alle domande di verifica** a fine capitolo. Se non sai rispondere, rileggi la
  sezione indicata: è normale doverlo fare.

Nei capitoli troverai alcuni riquadri ricorrenti:

> **Esempio**
> Un caso concreto svolto passo per passo.

> **Attenzione**
> Un errore frequente, nella teoria o sul campo.

> **Ricorda**
> Il concetto da portare con te.

> **Prova**
> Un esercizio da fare nel laboratorio.

## Cosa serve sapere prima

Niente di particolare. È utile sapere cos'è un pannello fotovoltaico e avere una vaga idea di
cosa siano tensione, corrente e potenza, ma il capitolo 2 riprende anche queste nozioni. Non
serve saper programmare: il codice del laboratorio è un aiuto in più, non un requisito.
