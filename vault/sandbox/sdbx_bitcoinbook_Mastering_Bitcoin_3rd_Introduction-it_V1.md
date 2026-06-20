---
stato: BOZZA
lingua: italiano
fonte: bitcoinbook_Mastering_Bitcoin_3rd_Introduction-it.md
data_ingest: 2026-06-20
---

# 📌 SINTESI ESAUSTIVA

# 📌 SINTESI ESAUSTIVA

Bitcoin rappresenta un insieme integrato di concetti e tecnologie che fondano un ecosistema di moneta digitale, dove unità di valuta denominate bitcoin (con la “b” minuscola, per distinguerle dal sistema “Bitcoin” con la “B” maiuscola) sono utilizzate per conservare e trasferire valore tra i partecipanti alla rete. Gli utenti comunicano attraverso il protocollo Bitcoin principalmente via internet, ma sono possibili anche altre reti di trasporto. Lo stack del protocollo, rilasciato come software open source, può essere eseguito su un’ampia gamma di dispositivi, dai laptop agli smartphone, rendendo la tecnologia accessibile a chiunque. A differenza delle valute tradizionali, non esistono monete fisiche e nemmeno singole unità digitali: le monete sono implicite nelle transazioni che spostano valore dal pagatore al beneficiario. Gli utenti controllano chiavi crittografiche che consentono di provare la proprietà di bitcoin sulla rete e di firmare transazioni per sbloccare e spendere il valore, trasferendolo a un nuovo proprietario. Tali chiavi sono in genere custodite in un portafoglio digitale sul dispositivo dell’utente; il possesso della chiave capace di firmare è l’unico requisito per spendere bitcoin, ponendo il pieno controllo nelle mani di ciascun utente.

La creazione di nuove unità di bitcoin avviene tramite un processo chiamato mining, che comporta l’esecuzione ripetuta di un compito computazionale riferito a un insieme di transazioni recenti. Chiunque nella rete può operare come miner, usando i propri dispositivi per contribuire alla sicurezza delle transazioni. Mediamente ogni 10 minuti un miner può aggiungere sicurezza alle transazioni passate e viene ricompensato con nuovi bitcoin e con le commissioni pagate dalle transazioni più recenti. Il protocollo Bitcoin integra algoritmi che regolano automaticamente la difficoltà del compito computazionale, in modo che, indipendentemente dalla potenza di calcolo complessiva impiegata, qualcuno riesca a produrre un blocco valido circa ogni 10 minuti. Inoltre, il protocollo riduce periodicamente il numero di nuovi bitcoin emessi, dimezzando il tasso di emissione circa ogni quattro anni e ponendo un limite massimo di poco inferiore a 21 milioni di monete. La progressione è prevedibile: intorno al blocco 1.411.200, previsto per il 2035, sarà stato emesso il 99% di tutti i bitcoin destinati a esistere. A causa del tasso di emissione decrescente, nel lungo periodo Bitcoin assume un carattere deflazionistico e nessuno può obbligare ad accettare bitcoin creati oltre il tasso di emissione prestabilito.

Prima di Bitcoin, a partire dalla fine degli anni ’80, diversi ricercatori avevano tentato di costruire valute digitali basate sulla crittografia. Queste prime valute erano generalmente garantite da valute nazionali o metalli preziosi e si appoggiavano a una camera di compensazione centrale per regolare le transazioni. L’architettura centralizzata, tuttavia, le rendeva facili bersagli per governi e hacker; molte furono soppresse per via legale o fallirono in spettacolari dissesti quando la società madre venne liquidata. Bitcoin, pubblicato nel 2009 con un’implementazione di riferimento attribuita a Satoshi Nakamoto, è stato progettato per essere decentralizzato e privo di qualsiasi autorità centrale o punto di controllo attaccabile. Il numero e la potenza delle macchine che eseguono l’algoritmo proof-of-work (mining) sono cresciuti esponenzialmente, e la loro potenza combinata oggi supera quella dei più potenti supercomputer mondiali. Nakamoto si ritirò dalla scena pubblica nell’aprile 2011, lasciando lo sviluppo a una comunità di volontari. L’identità rimane sconosciuta, ma l’invenzione è di per sé rivoluzionaria e ha già generato nuova scienza nei campi del calcolo distribuito, dell’economia e dell’econometria. Dal punto di vista informatico, l’invenzione risolve in modo pratico il problema del consenso distribuito (il cosiddetto “problema dei generali bizantini”), usando la proof of work per raggiungere un accordo senza un’autorità centrale fidata — un risultato che costituisce una svolta nel calcolo distribuito.

I portafogli Bitcoin si classificano innanzitutto per piattaforma. I portafogli desktop, che rappresentano il primo tipo creato con l’implementazione di riferimento, offrono funzionalità, autonomia e controllo, ma soffrono delle vulnerabilità tipiche dei sistemi operativi general-purpose come Windows e macOS. I portafogli mobili, eseguiti su iOS e Android, sono oggi i più comuni e spesso privilegiati dai nuovi utenti per la semplicità; molti recuperano informazioni da server remoti per evitare di scaricare l’intera blockchain, sacrificando però la privacy perché rivelano a terze parti dettagli su indirizzi e saldi. I portafogli web sono accessibili via browser e memorizzano i dati su server di terze parti; alcuni eseguono codice lato client mantenendo il controllo delle chiavi in mano all’utente, ma la dipendenza dal server compromette comunque la privacy, mentre altri prendono il controllo completo delle chiavi in cambio di facilità d’uso, rendendo sconsigliabile conservarvi grandi quantità di bitcoin. I dispositivi di firma hardware costituiscono un’ulteriore categoria dedicata alla sicurezza.

Un’altra classificazione riguarda il grado di autonomia e il modo in cui il portafoglio interagisce con la rete Bitcoin. Il nodo completo è un programma che convalida l’intera storia delle transazioni e, opzionalmente, archivia e serve i dati, garantendo piena autonomia all’utente. Il client leggero, o client SPV (Simplified Payment Verification), si connette a nodi completi o server remoti per ricevere e inviare informazioni, conservando però il portafoglio in locale e validando parzialmente le transazioni in entrata, oltre a creare autonomamente quelle in uscita. Il client API di terze parti interagisce con Bitcoin attraverso un’interfaccia di programmazione di terze parti, fidandosi del server remoto per accuratezza e privacy; il portafoglio può risiedere presso l’utente o presso terze parti, ma la sicurezza dipende dalla fiducia nel servizio esterno. Bitcoin è una rete peer-to-peer: i nodi completi sono i peer, ciascuno dei quali convalida individualmente ogni transazione confermata, mentre i client leggeri e gli altri software sono client che dipendono da uno o più peer per ottenere dati validi; possono eseguire validazione secondaria e connettersi a più peer per ridurre la dipendenza, ma la loro sicurezza resta ancorata all’integrità dei peer.

Per acquisire bitcoin, un nuovo utente deve tenere conto del fatto che, sebbene le transazioni Bitcoin siano difficili da invertire, i metodi di pagamento elettronici tradizionali utilizzati per acquistare bitcoin (carte di credito, PayPal) possono essere stornati. Questo rischio spinge le aziende che accettano pagamenti tradizionali in cambio di bitcoin a richiedere verifica dell’identità e controlli di solvibilità che possono richiedere giorni o settimane, rendendo impossibile un acquisto immediato con carta di credito. Esistono comunque diverse alternative: acquistare bitcoin direttamente da un amico (molti utenti iniziano così, oppure partecipando a meetup Bitcoin locali elencati su Meetup.com); guadagnare bitcoin offrendo beni o servizi; usare un Bitcoin ATM che accetta contanti e invia bitcoin al portafoglio sullo smartphone; oppure servirsi di un exchange di valuta Bitcoin collegato al proprio conto bancario. I servizi di quotazione come BitcoinAverage mostrano un elenco di exchange per ciascuna valuta. È importante notare che, sebbene Bitcoin offra più privacy rispetto ad altri sistemi di pagamento se usato correttamente, quando si interagisce con sistemi finanziari tradizionali (come gli exchange) spesso si applicano normative che richiedono prova di identità e informazioni bancarie. Una volta che un indirizzo Bitcoin viene collegato a un’identità, altre transazioni associate possono diventare tracciabili, incluse quelle passate; per questo molti utenti mantengono conti exchange dedicati e separati dal proprio portafoglio personale.

Il prezzo dei bitcoin non è fissato da un’entità centrale, bensì dai mercati. Come la maggior parte delle valute, Bitcoin ha un tasso di cambio fluttuante: il prezzo in una data valuta (ad esempio, USD) è determinato in ciascun mercato dall’ultima transazione registrata e può variare più volte al secondo. I servizi di pricing aggregano i prezzi di diversi mercati e calcolano una media ponderata per volume che rappresenta il tasso di cambio complessivo della coppia valutaria (es. BTC/USD). Esistono numerosi siti e applicazioni per conoscere il tasso corrente, tra cui Bitcoin Average (media ponderata per volume), CoinCap (capitalizzazione di mercato e tassi di cambio per centinaia di criptovalute) e il Chicago Mercantile Exchange Bitcoin Reference Rate (un tasso di riferimento per uso istituzionale e contrattuale); molti portafogli offrono inoltre la conversione automatica tra bitcoin e valute locali.

Il processo di invio e ricezione di bitcoin viene illustrato con un esempio concreto: Alice decide di acquistare 0,001 BTC da Joe. Dopo aver concordato il tasso di cambio e versato il contante, Alice apre il proprio portafoglio mobile e seleziona “Ricevi”, ottenendo un indirizzo mostrato come codice QR. Joe seleziona “Invia” sul proprio portafoglio, scansiona il codice QR con la fotocamera dello smartphone e inserisce l’importo di 0,001 bitcoin (equivalente a 1 millibitcoin o 100.000 satoshi), eventualmente aggiungendo un’etichetta come “Alice” per tenere traccia della transazione. Il portafoglio può chiedere a Joe di indicare una commissione (o un tasso di commissione), poiché commissioni più elevate accelerano la conferma. Dopo aver controllato attentamente indirizzo e importo, Joe preme “Invia”. Il portafoglio di Joe costruisce una transazione che assegna 0,001 BTC all’indirizzo di Alice, prelevando i fondi dal suo portafoglio e firmandola con le proprie chiavi private. La transazione viene propagata rapidamente attraverso la rete peer-to-peer e, nel giro di pochi secondi, la maggior parte dei nodi ben connessi la riceve. Nel frattempo, il portafoglio di Alice, costantemente in ascolto, rileva la transazione in arrivo e mostra il ricevimento di 0,001 BTC.

Inizialmente la transazione appare come “Non confermata”, perché non è ancora stata inclusa in un blocco della blockchain, il registro pubblico delle transazioni Bitcoin. Per essere confermata, una transazione deve essere inserita in un blocco e aggiunta alla blockchain, evento che avviene mediamente ogni 10 minuti e che in finanza tradizionale equivale alla compensazione. Nei giorni successivi, Alice acquista ulteriori bitcoin tramite un ATM e un exchange, e il libro si propone di analizzare il suo primo acquisto reale con Bitcoin, esplorando in dettaglio la transazione sottostante e le tecnologie di propagazione.

---

## 📌 EVIDENZE DA DISCUTERE

### Evidenza 1

>>>Bitcoin è un sistema distribuito, peer-to-peer. Di conseguenza, non esiste un server centrale o un punto di controllo.<<<

### Evidenza 2

>>>il mining di Bitcoin decentralizza le funzioni di emissione della valuta e di compensazione di una banca centrale e sostituisce la necessità di qualsiasi banca centrale.<<<

### Evidenza 3

>>>Bitcoin con la B maiuscola è  il nome del protocollo, una rete peer-to-peer e un'innovazione informatica distribuita. Bitcoin si basa su decenni di ricerca in crittografia e sistemi distribuiti e include almeno quattro innovazioni chiave:

- Una rete peer-to-peer decentralizzata (il protocollo Bitcoin)
- Un registro pubblico delle transazioni (la blockchain)
- Un insieme di regole per la validazione indipendente delle transazioni e l'emissione di valuta (regole di consenso)
- Un meccanismo per raggiungere un consenso globale decentralizzato sulla blockchain valida (algoritmo di proof-of-work)<<<

### Evidenza 4

>>>L'emergere di moneta digitale praticabile è strettamente legato agli sviluppi della crittografia. Ciò non sorprende se si considerano le sfide fondamentali coinvolte nell'uso di bit per rappresentare valore che può essere scambiato con beni e servizi. Tre domande fondamentali per chiunque accetti denaro digitale sono:

- Posso fidarmi che il denaro sia autentico e non contraffatto?
- Posso fidarmi che il denaro digitale possa essere speso una sola volta (noto come problema della "doppia spesa")?
- Posso essere sicuro che nessun altro possa affermare che questo denaro appartiene a loro e non a me?

Gli emittenti di cartamoneta combattono costantemente il problema della contraffazione utilizzando carte e tecnologie di stampa sempre più sofisticate. Il denaro fisico risolve facilmente il problema della doppia spesa perché la stessa banconota non può trovarsi in due posti contemporaneamente. Naturalmente, anche il denaro convenzionale viene spesso conservato e trasmesso digitalmente. In questi casi, i problemi di contraffazione e doppia spesa vengono gestiti compensando tutte le transazioni elettroniche attraverso autorità centrali che hanno una visione globale della valuta in circolazione. Per bitcoin,che non può sfruttare inchiostri esoterici o strisce olografiche, >la crittografia fornisce la base per fidarsi della legittimità della rivendicazione di valore da parte di un utente.< Nello specifico, le firme digitali crittografiche consentono a un utente di firmare un asset digitale o una transazione dimostrando la proprietà di quell'asset.<<<

### Evidenza 5

>>>### Storia di Bitcoin

Bitcoin fu descritto per la prima volta nel 2008 con la pubblicazione di un documento intitolato "Bitcoin: A Peer-to-Peer Electronic Cash System",scritto sotto lo pseudonimo di Satoshi Nakamoto. Nakamoto combinò diverse invenzioni precedenti come le firme digitali e Hashcash per creare un sistema di contante elettronico completamente decentralizzato che non si basa su un'autorità centrale per l'emissione di valuta o la compensazione e validazione delle transazioni. L'innovazione chiave fu l'uso di un sistema di calcolo distribuito (chiamato algoritmo "proof-of-work") per condurre una lotteria globale ogni 10 minuti in media, permettendo alla rete decentralizzata di raggiungere un *consenso* sullo stato delle transazioni. Ciò risolve elegantemente il problema della doppia spesa in cui una singola unità di valuta può essere spesa due volte. In precedenza, il problema della doppia spesa era un punto debole della valuta digitale e veniva affrontato compensando tutte le transazioni attraverso una camera di compensazione centrale.<<<

### Evidenza 6

>>>né Satoshi Nakamoto né nessun altro esercita un controllo individuale sul sistema Bitcoin, che opera basandosi su principi matematici completamente trasparenti, codice open source e consenso tra i partecipanti.<<<

### Evidenza 7

>>>### Per Iniziare

Bitcoin è un protocollo a cui si può accedere utilizzando un'applicazione che parla con il protocollo, un "portafoglio Bitcoin", meglio conosciuto come wallet. Il wallet è l'interfaccia utente più comune per il sistema Bitcoin, proprio come un browser web è l'interfaccia utente più comune per il protocollo HTTP. Esistono molte implementazioni e marche di portafogli Bitcoin, proprio come esistono molte marche di browser web (ad es. Chrome, Safari e Firefox). E proprio come tutti abbiamo i nostri browser preferiti, i portafogli Bitcoin variano in qualità, prestazioni, sicurezza, privacy e affidabilità. Esiste anche un'implementazione di riferimento del protocollo Bitcoin che include un portafoglio, nota come "Bitcoin Core", che deriva dall'implementazione originale scritta da Satoshi Nakamoto.Vale la pena provare diversi portafogli finché non ne trovi uno che soddisfi le tue esigenze.<<<

### Evidenza 8

>>>##### Chi controlla le chiavi

Una considerazione aggiuntiva molto importante è *chi controlla le chiavi*. Come vedremo nei capitoli successivi, l'accesso ai bitcoin è controllato da "chiavi private", che sono come PIN molto lunghi. Se sei l'unico ad avere il controllo su queste chiavi private, hai il controllo dei tuoi bitcoin. Al contrario, se non hai il controllo, allora i tuoi bitcoin sono gestiti da una terza parte che controlla in ultima analisi i tuoi fondi per tuo conto. Il software di gestione delle chiavi rientra in due importanti categorie basate sul controllo: *portafogli*, dove controlli le chiavi, e i fondi e i conti con custodi dove una terza parte controlla le chiavi. Per sottolineare questo punto, Andreas Antonopolus ha coniato la frase: *Le tue chiavi, le tue monete. Non le tue chiavi, non le tue monete*.

Combinando queste categorizzazioni, molti portafogli Bitcoin rientrano in alcuni gruppi, con i tre più comuni che sono nodo completo desktop (controlli le chiavi), portafoglio leggero mobile (controlli le chiavi) e conti basati sul web con terze parti (non controlli le chiavi). I confini tra diverse categorie sono talvolta sfumati, poiché il software viene eseguito su più piattaforme e può interagire con la rete in modi diversi.

#### Avvio Rapido

Alice non è un'utente tecnica e ha sentito parlare di Bitcoin solo di recente dal suo amico Joe. Mentre sono a una festa, Joe spiega con entusiasmo Bitcoin a tutti i presenti e offre una dimostrazione. Incuriosita, Alice chiede come può iniziare con Bitcoin. Joe dice che un portafoglio mobile è il migliore per i nuovi utenti e le consiglia alcuni dei suoi portafogli preferiti. Alice scarica uno dei consigli di Joe e lo installa sul suo telefono.

Quando Alice esegue la sua applicazione portafoglio per la prima volta, sceglie l'opzione per creare un nuovo portafoglio Bitcoin. Poiché il portafoglio che ha scelto è un portafoglio non custodiale, Alice (e solo Alice) avrà il controllo delle sue chiavi. Pertanto, si assume la responsabilità di eseguirne il backup, poiché perdere le chiavi significa perdere l'accesso ai suoi bitcoin. Per facilitare ciò, il suo portafoglio produce un *codice di recupero* che può essere utilizzato per ripristinare il suo portafoglio.

#### Codici di Recupero

La maggior parte dei portafogli Bitcoin non custodiali moderni fornirà un codice di recupero per il backup da parte dell'utente. Il codice di recupero di solito consiste in numeri, lettere o parole selezionate casualmente dal software e viene utilizzato come base per le chiavi generate dal portafoglio. Vedi [\[recovery\_code\_sample\]](#recovery_code_sample) per esempi.

Codici di recupero di esempio

| Portafoglio | Codice di recupero |
| --- | --- |
| BlueWallet | (1) media (2) suspect (3) effort (4) dish (5) album (6) shaft (7) price (8) junk (9) pizza (10) situate (11) oyster (12) rib |
| Electrum | nephew dog crane clever quantum crazy purse traffic repeat fruit old clutch |
| Muun | LAFV TZUN V27E NU4D WPF4 BRJ4 ELLP BNFL |

| Suggerimento | Un codice di recupero è talvolta chiamato "mnemonico" o "frase mnemonica", il che implica che dovresti memorizzare la frase, ma scrivere la frase su carta richiede meno lavoro e tende ad essere più affidabile della memoria della maggior parte delle persone. Un altro nome alternativo è "frase seed" perché fornisce l'input ("seed") alla funzione che genera tutte le chiavi di un portafoglio. |
| --- | --- |

Se succede qualcosa al portafoglio di Alice, può scaricare una nuova copia del suo software portafoglio e inserire questo codice di recupero per ricostruire il database del portafoglio di tutte le transazioni onchain che ha mai inviato o ricevuto. Tuttavia, il recupero dal codice di recupero non ripristinerà da solo eventuali dati aggiuntivi inseriti da Alice nel suo portafoglio, come le etichette che ha associato a particolari indirizzi o transazioni. Sebbene perdere l'accesso a quei metadati non sia importante quanto perdere l'accesso al denaro, può comunque essere importante a modo suo. Immagina di dover rivedere un vecchio estratto conto bancario o di carta di credito e il nome di ogni entità a cui hai pagato (o che ti ha pagato) è stato oscurato. Per prevenire la perdita di metadati, molti portafogli forniscono una funzionalità di backup aggiuntiva oltre ai codici di recupero.

Per alcuni portafogli, quella funzionalità di backup aggiuntiva è ancora più importante oggi di quanto non lo fosse in passato. Molti pagamenti Bitcoin vengono ora effettuati utilizzando tecnologia *offchain*, dove non tutti i pagamenti sono archiviati nella blockchain pubblica. Ciò riduce i costi dell'utente e migliora la privacy, tra gli altri vantaggi, ma significa che un meccanismo come i codici di recupero che dipende dai dati onchain non può garantire il recupero di tutti i bitcoin di un utente. Per le applicazioni con supporto offchain, è importante eseguire backup frequenti del database del portafoglio.

Da notare, quando si ricevono fondi per la prima volta su un nuovo portafoglio mobile, molti portafogli spesso riverificano che tu abbia eseguito un backup sicuro del tuo codice di recupero. Ciò può variare da un semplice prompt alla richiesta all'utente di reinserire manualmente il codice.

| Avvertenza | Sebbene molti portafogli legittimi ti chiederanno di reinserire il tuo codice di recupero, esistono anche molte applicazioni malware che imitano il design di un portafoglio, insistono affinché tu inserisca il tuo codice di recupero, e poi inoltrano qualsiasi codice inserito allo sviluppatore del malware in modo che possa rubare i tuoi fondi. Questo è l'equivalente dei siti web di phishing che cercano di ingannarti per farti dare la tua frase di accesso bancaria. Per la maggior parte delle applicazioni portafoglio, le uniche volte in cui ti chiederanno il tuo codice di recupero sono durante la configurazione iniziale (prima di aver ricevuto bitcoin) e durante il recupero (dopo aver perso l'accesso al tuo portafoglio originale). Se l'applicazione ti chiede il tuo codice di recupero in qualsiasi altro momento, consulta un esperto per assicurarti di non essere vittima di phishing. |
| --- | --- |
>il codice di recupero è la seed phrase ?<

#### Indirizzi Bitcoin

Alice è ora pronta per iniziare a usare il suo nuovo portafoglio Bitcoin. La sua applicazione portafoglio ha generato casualmente una chiave privata (descritta più in dettaglio in [\[private\_keys\]](#private_keys)) che verrà utilizzata per derivare indirizzi Bitcoin che indirizzano al suo portafoglio. A questo punto, i suoi indirizzi Bitcoin non sono noti alla rete Bitcoin né "registrati" con alcuna parte del sistema Bitcoin. I suoi indirizzi Bitcoin sono semplicemente numeri che corrispondono alla sua chiave privata che può utilizzare per controllare l'accesso ai fondi. Gli indirizzi vengono generati indipendentemente dal suo portafoglio senza riferimento o registrazione con alcun servizio.

| Suggerimento | Esistono una varietà di formati di indirizzi Bitcoin e fatture. Indirizzi e fatture possono essere condivisi con altri utenti Bitcoin che possono usarli per inviare bitcoin direttamente al tuo portafoglio. Puoi condividere un indirizzo o una fattura con altre persone senza preoccuparti della sicurezza dei tuoi bitcoin. A differenza di un numero di conto bancario, nessuno che venga a conoscenza di uno dei tuoi indirizzi Bitcoin può prelevare denaro dal tuo portafoglio—devi avviare tu tutte le spese. Tuttavia, se dai a due persone lo stesso indirizzo, saranno in grado di vedere quanti bitcoin l'altra persona ti ha inviato. Se pubblichi il tuo indirizzo pubblicamente, tutti potranno vedere quanto bitcoin altre persone hanno inviato a quell'indirizzo. Per proteggere la tua privacy, dovresti generare una nuova fattura con un nuovo indirizzo ogni volta che richiedi un pagamento. |
| --- | --- |
>quindi l'indirizzo deriva dalla CHIAVE PRIVATA CHE DERIVA DAL CODICE DI RECUPERO. Condividerla non mette a rischio che qualcuno possa rubare i nostri fondi, mai usarla più volte perchà mettiamo a rischio la nostra privacy ?<
#### Ricevere Bitcoin

Alice usa il pulsante *Ricevi*, che visualizza un codice QR, mostrato in [Alice usa la schermata Ricevi sul suo portafoglio Bitcoin mobile e mostra il suo indirizzo in formato codice QR.](#wallet_receive).

[![[mbc3_0101.png|Schermata di ricezione del portafoglio con codice QR visualizzato. Immagine derivata da Bitcoin Design Guide CC-BY]]](https://github.com/bitcoinbook/bitcoinbook/blob/develop/images/mbc3_0101.png)

Figura 1. Alice usa la schermata Ricevi sul suo portafoglio Bitcoin mobile e mostra il suo indirizzo in formato codice QR.

Il codice QR è il quadrato con un motivo di punti bianchi e neri, che funge da forma di codice a barre che contiene le stesse informazioni in un formato che può essere scansionato dalla fotocamera dello smartphone di Joe.

| Avvertenza | Qualsiasi fondo inviato agli indirizzi in questo libro andrà perso. Se vuoi testare l'invio di bitcoin, considera di donarlo a un ente di beneficenza che accetta bitcoin. |
| --- | --- |

#### Ottenere il Tuo Primo Bitcoin

Il primo compito per i nuovi utenti è acquisire un po' di bitcoin.

>>>transazioni Bitcoin sono irreversibili. La maggior parte delle reti di pagamento elettronico come carte di credito, carte di debito, PayPal e bonifici bancari sono reversibili<<<



---

## ❓ DOMANDE DA DISCUTERE

### Domanda 1

>la valuta bitcoin è completamente virtuale.<

### Domanda 2

>>>Bitcoin è un sistema distribuito, peer-to-peer. Di conseguenza, non esiste un server centrale o un punto di controllo.<

### Domanda 3

>>>il mining di Bitcoin decentralizza le funzioni di emissione della valuta e di compensazione di una banca centrale e sostituisce la necessità di qualsiasi banca centrale.<

### Domanda 4

>>>Bitcoin con la B maiuscola è  il nome del protocollo, una rete peer-to-peer e un'innovazione informatica distribuita. Bitcoin si basa su decenni di ricerca in crittografia e sistemi distribuiti e include almeno quattro innovazioni chiave:

- Una rete peer-to-peer decentralizzata (il protocollo Bitcoin)
- Un registro pubblico delle transazioni (la blockchain)
- Un insieme di regole per la validazione indipendente delle transazioni e l'emissione di valuta (regole di consenso)
- Un meccanismo per raggiungere un consenso globale decentralizzato sulla blockchain valida (algoritmo di proof-of-work)<

### Domanda 5

>>>L'emergere di moneta digitale praticabile è strettamente legato agli sviluppi della crittografia. Ciò non sorprende se si considerano le sfide fondamentali coinvolte nell'uso di bit per rappresentare valore che può essere scambiato con beni e servizi. Tre domande fondamentali per chiunque accetti denaro digitale sono:

- Posso fidarmi che il denaro sia autentico e non contraffatto?
- Posso fidarmi che il denaro digitale possa essere speso una sola volta (noto come problema della "doppia spesa")?
- Posso essere sicuro che nessun altro possa affermare che questo denaro appartiene a loro e non a me?

Gli emittenti di cartamoneta combattono costantemente il problema della contraffazione utilizzando carte e tecnologie di stampa sempre più sofisticate. Il denaro fisico risolve facilmente il problema della doppia spesa perché la stessa banconota non può trovarsi in due posti contemporaneamente. Naturalmente, anche il denaro convenzionale viene spesso conservato e trasmesso digitalmente. In questi casi, i problemi di contraffazione e doppia spesa vengono gestiti compensando tutte le transazioni elettroniche attraverso autorità centrali che hanno una visione globale della valuta in circolazione. Per bitcoin,che non può sfruttare inchiostri esoterici o strisce olografiche, >la crittografia fornisce la base per fidarsi della legittimità della rivendicazione di valore da parte di un utente.<

### Domanda 6

>Per essere robusti contro l'intervento di antagonisti, siano essi governi legittimi o elementi criminali, era necessaria una valuta digitale *decentralizzata* per evitare un singolo punto di attacco.<

### Domanda 7

>>>### Storia di Bitcoin

Bitcoin fu descritto per la prima volta nel 2008 con la pubblicazione di un documento intitolato "Bitcoin: A Peer-to-Peer Electronic Cash System",scritto sotto lo pseudonimo di Satoshi Nakamoto. Nakamoto combinò diverse invenzioni precedenti come le firme digitali e Hashcash per creare un sistema di contante elettronico completamente decentralizzato che non si basa su un'autorità centrale per l'emissione di valuta o la compensazione e validazione delle transazioni. L'innovazione chiave fu l'uso di un sistema di calcolo distribuito (chiamato algoritmo "proof-of-work") per condurre una lotteria globale ogni 10 minuti in media, permettendo alla rete decentralizzata di raggiungere un *consenso* sullo stato delle transazioni. Ciò risolve elegantemente il problema della doppia spesa in cui una singola unità di valuta può essere spesa due volte. In precedenza, il problema della doppia spesa era un punto debole della valuta digitale e veniva affrontato compensando tutte le transazioni attraverso una camera di compensazione centrale.<

### Domanda 8

>>>né Satoshi Nakamoto né nessun altro esercita un controllo individuale sul sistema Bitcoin, che opera basandosi su principi matematici completamente trasparenti, codice open source e consenso tra i partecipanti.<

### Domanda 9

>"Problema dei Generali Bizantini".<

### Domanda 10

>>>### Per Iniziare

Bitcoin è un protocollo a cui si può accedere utilizzando un'applicazione che parla con il protocollo, un "portafoglio Bitcoin", meglio conosciuto come wallet. Il wallet è l'interfaccia utente più comune per il sistema Bitcoin, proprio come un browser web è l'interfaccia utente più comune per il protocollo HTTP. Esistono molte implementazioni e marche di portafogli Bitcoin, proprio come esistono molte marche di browser web (ad es. Chrome, Safari e Firefox). E proprio come tutti abbiamo i nostri browser preferiti, i portafogli Bitcoin variano in qualità, prestazioni, sicurezza, privacy e affidabilità. Esiste anche un'implementazione di riferimento del protocollo Bitcoin che include un portafoglio, nota come "Bitcoin Core", che deriva dall'implementazione originale scritta da Satoshi Nakamoto.Vale la pena provare diversi portafogli finché non ne trovi uno che soddisfi le tue esigenze.<

### Domanda 11

>I dispositivi di firma hardware sono dispositivi che possono archiviare chiavi e firmare transazioni utilizzando hardware e firmware specializzati. Di solito si collegano a un portafoglio desktop, mobile o web tramite cavo USB, comunicazione in prossimità (NFC) o una fotocamera con codici QR. Gestendo tutte le operazioni relative a Bitcoin sull'hardware specializzato, questi portafogli sono meno vulnerabili a molti tipi di attacchi. I dispositivi di firma hardware sono talvolta chiamati "portafogli hardware", ma devono essere abbinati a un portafoglio completo per inviare e ricevere transazioni, e la sicurezza e la privacy offerte da quel portafoglio abbinato giocano un ruolo critico nel determinare quanta sicurezza e privacy ottiene l'utente quando utilizza il dispositivo di firma hardware.<

### Domanda 12

>>>##### Chi controlla le chiavi

Una considerazione aggiuntiva molto importante è *chi controlla le chiavi*. Come vedremo nei capitoli successivi, l'accesso ai bitcoin è controllato da "chiavi private", che sono come PIN molto lunghi. Se sei l'unico ad avere il controllo su queste chiavi private, hai il controllo dei tuoi bitcoin. Al contrario, se non hai il controllo, allora i tuoi bitcoin sono gestiti da una terza parte che controlla in ultima analisi i tuoi fondi per tuo conto. Il software di gestione delle chiavi rientra in due importanti categorie basate sul controllo: *portafogli*, dove controlli le chiavi, e i fondi e i conti con custodi dove una terza parte controlla le chiavi. Per sottolineare questo punto, Andreas Antonopolus ha coniato la frase: *Le tue chiavi, le tue monete. Non le tue chiavi, non le tue monete*.

Combinando queste categorizzazioni, molti portafogli Bitcoin rientrano in alcuni gruppi, con i tre più comuni che sono nodo completo desktop (controlli le chiavi), portafoglio leggero mobile (controlli le chiavi) e conti basati sul web con terze parti (non controlli le chiavi). I confini tra diverse categorie sono talvolta sfumati, poiché il software viene eseguito su più piattaforme e può interagire con la rete in modi diversi.

#### Avvio Rapido

Alice non è un'utente tecnica e ha sentito parlare di Bitcoin solo di recente dal suo amico Joe. Mentre sono a una festa, Joe spiega con entusiasmo Bitcoin a tutti i presenti e offre una dimostrazione. Incuriosita, Alice chiede come può iniziare con Bitcoin. Joe dice che un portafoglio mobile è il migliore per i nuovi utenti e le consiglia alcuni dei suoi portafogli preferiti. Alice scarica uno dei consigli di Joe e lo installa sul suo telefono.

Quando Alice esegue la sua applicazione portafoglio per la prima volta, sceglie l'opzione per creare un nuovo portafoglio Bitcoin. Poiché il portafoglio che ha scelto è un portafoglio non custodiale, Alice (e solo Alice) avrà il controllo delle sue chiavi. Pertanto, si assume la responsabilità di eseguirne il backup, poiché perdere le chiavi significa perdere l'accesso ai suoi bitcoin. Per facilitare ciò, il suo portafoglio produce un *codice di recupero* che può essere utilizzato per ripristinare il suo portafoglio.

#### Codici di Recupero

La maggior parte dei portafogli Bitcoin non custodiali moderni fornirà un codice di recupero per il backup da parte dell'utente. Il codice di recupero di solito consiste in numeri, lettere o parole selezionate casualmente dal software e viene utilizzato come base per le chiavi generate dal portafoglio. Vedi [\[recovery\_code\_sample\]](#recovery_code_sample) per esempi.

Codici di recupero di esempio

| Portafoglio | Codice di recupero |
| --- | --- |
| BlueWallet | (1) media (2) suspect (3) effort (4) dish (5) album (6) shaft (7) price (8) junk (9) pizza (10) situate (11) oyster (12) rib |
| Electrum | nephew dog crane clever quantum crazy purse traffic repeat fruit old clutch |
| Muun | LAFV TZUN V27E NU4D WPF4 BRJ4 ELLP BNFL |

| Suggerimento | Un codice di recupero è talvolta chiamato "mnemonico" o "frase mnemonica", il che implica che dovresti memorizzare la frase, ma scrivere la frase su carta richiede meno lavoro e tende ad essere più affidabile della memoria della maggior parte delle persone. Un altro nome alternativo è "frase seed" perché fornisce l'input ("seed") alla funzione che genera tutte le chiavi di un portafoglio. |
| --- | --- |

Se succede qualcosa al portafoglio di Alice, può scaricare una nuova copia del suo software portafoglio e inserire questo codice di recupero per ricostruire il database del portafoglio di tutte le transazioni onchain che ha mai inviato o ricevuto. Tuttavia, il recupero dal codice di recupero non ripristinerà da solo eventuali dati aggiuntivi inseriti da Alice nel suo portafoglio, come le etichette che ha associato a particolari indirizzi o transazioni. Sebbene perdere l'accesso a quei metadati non sia importante quanto perdere l'accesso al denaro, può comunque essere importante a modo suo. Immagina di dover rivedere un vecchio estratto conto bancario o di carta di credito e il nome di ogni entità a cui hai pagato (o che ti ha pagato) è stato oscurato. Per prevenire la perdita di metadati, molti portafogli forniscono una funzionalità di backup aggiuntiva oltre ai codici di recupero.

Per alcuni portafogli, quella funzionalità di backup aggiuntiva è ancora più importante oggi di quanto non lo fosse in passato. Molti pagamenti Bitcoin vengono ora effettuati utilizzando tecnologia *offchain*, dove non tutti i pagamenti sono archiviati nella blockchain pubblica. Ciò riduce i costi dell'utente e migliora la privacy, tra gli altri vantaggi, ma significa che un meccanismo come i codici di recupero che dipende dai dati onchain non può garantire il recupero di tutti i bitcoin di un utente. Per le applicazioni con supporto offchain, è importante eseguire backup frequenti del database del portafoglio.

Da notare, quando si ricevono fondi per la prima volta su un nuovo portafoglio mobile, molti portafogli spesso riverificano che tu abbia eseguito un backup sicuro del tuo codice di recupero. Ciò può variare da un semplice prompt alla richiesta all'utente di reinserire manualmente il codice.

| Avvertenza | Sebbene molti portafogli legittimi ti chiederanno di reinserire il tuo codice di recupero, esistono anche molte applicazioni malware che imitano il design di un portafoglio, insistono affinché tu inserisca il tuo codice di recupero, e poi inoltrano qualsiasi codice inserito allo sviluppatore del malware in modo che possa rubare i tuoi fondi. Questo è l'equivalente dei siti web di phishing che cercano di ingannarti per farti dare la tua frase di accesso bancaria. Per la maggior parte delle applicazioni portafoglio, le uniche volte in cui ti chiederanno il tuo codice di recupero sono durante la configurazione iniziale (prima di aver ricevuto bitcoin) e durante il recupero (dopo aver perso l'accesso al tuo portafoglio originale). Se l'applicazione ti chiede il tuo codice di recupero in qualsiasi altro momento, consulta un esperto per assicurarti di non essere vittima di phishing. |
| --- | --- |
>il codice di recupero è la seed phrase ?<

### Domanda 13

>quindi l'indirizzo deriva dalla CHIAVE PRIVATA CHE DERIVA DAL CODICE DI RECUPERO. Condividerla non mette a rischio che qualcuno possa rubare i nostri fondi, mai usarla più volte perchà mettiamo a rischio la nostra privacy ?<

### Domanda 14

>>>transazioni Bitcoin sono irreversibili. La maggior parte delle reti di pagamento elettronico come carte di credito, carte di debito, PayPal e bonifici bancari sono reversibili<



---

## 🗨️ DISCUSSIONE SOCRATICA

(Lascia vuoto - verrà compilato durante /chat)

---

## ✅ IL MIO SAPERE

(Lascia vuoto - verrà compilato con /fine)
