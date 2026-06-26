---
title: "bitcoinbook_Mastering_Bitcoin_3rd_Introduction "
source: "https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch01_intro.adoc"
author:
  - "Antonopolus"
published:
created: 2026-06-14
description: "Mastering Bitcoin 3rd Edition - Programming the Open Blockchain - bitcoinbook/bitcoinbook"
tags:
  - "clippings"
---
## Introduzione

Bitcoin è un insieme di concetti e tecnologie che costituiscono la base di un ecosistema di moneta digitale. Le unità di valuta chiamate bitcoin vengono utilizzate per conservare e trasferire valore tra i partecipanti della rete Bitcoin. Gli utenti di Bitcoin comunicano tra loro utilizzando il protocollo Bitcoin principalmente tramite internet, sebbene possano essere impiegate anche altre reti di trasporto. Lo stack del protocollo Bitcoin, disponibile come software open source, può essere eseguito su un'ampia gamma di dispositivi informatici, inclusi laptop e smartphone, rendendo la tecnologia facilmente accessibile.

| Suggerimento | In questo libro, l'unità di valuta è chiamata "bitcoin" con la *b* minuscola, mentre il sistema è chiamato "Bitcoin", con la *B* maiuscola. |
| --- | --- |

Gli utenti possono trasferire bitcoin sulla rete per fare praticamente tutto ciò che si può fare con le valute convenzionali, compresi acquistare e vendere beni, inviare denaro a persone o organizzazioni, o concedere credito. I bitcoin possono essere acquistati, venduti e scambiati con altre valute presso borse di cambio specializzate. Bitcoin è probabilmente la forma di moneta perfetta per internet perché è veloce, sicuro e senza confini.

A differenza delle valute tradizionali, la valuta bitcoin è interamente virtuale. Non esistono monete fisiche e nemmeno singole monete digitali. Le monete sono implicite nelle transazioni che trasferiscono valore dal mittente al destinatario. Gli utenti di Bitcoin controllano delle chiavi che consentono loro di dimostrare la proprietà dei bitcoin sulla rete Bitcoin. Con queste chiavi, possono firmare le transazioni per sbloccare il valore e spenderlo trasferendolo a un nuovo proprietario. Le chiavi sono spesso conservate in un portafoglio digitale sul computer o sullo smartphone di ciascun utente. Il possesso della chiave in grado di firmare una transazione è l'unico prerequisito per spendere bitcoin, ponendo il controllo interamente nelle mani di ogni utente.

Bitcoin è un sistema distribuito e peer-to-peer. In quanto tale, non esiste un server centrale né un punto di controllo. Le unità di bitcoin vengono create attraverso un processo chiamato "mining" (estrazione), che consiste nell'eseguire ripetutamente un compito computazionale che fa riferimento a un elenco di transazioni Bitcoin recenti. Qualsiasi partecipante alla rete Bitcoin può operare come miner, utilizzando i propri dispositivi di calcolo per contribuire a proteggere le transazioni. Ogni 10 minuti, in media, un miner Bitcoin può aggiungere sicurezza alle transazioni passate e viene ricompensato con bitcoin nuovi di zecca e con le commissioni pagate dalle transazioni recenti. In sostanza, il mining di Bitcoin decentralizza le funzioni di emissione e compensazione della valuta proprie di una banca centrale e sostituisce la necessità di una banca centrale.

Il protocollo Bitcoin include algoritmi integrati che regolano la funzione di mining sull'intera rete. La difficoltà del compito computazionale che i miner devono svolgere viene regolata dinamicamente in modo che, in media, qualcuno riesca ogni 10 minuti, indipendentemente da quanti miner (e quanta potenza di elaborazione) siano in competizione in un dato momento. Il protocollo inoltre riduce periodicamente il numero di nuovi bitcoin creati, limitando il numero totale di bitcoin che saranno mai creati a un totale fisso di poco inferiore a 21 milioni di monete. Ne consegue che il numero di bitcoin in circolazione segue fedelmente una curva facilmente prevedibile, in cui la metà delle monete rimanenti viene aggiunta alla circolazione ogni quattro anni. Approssimativamente al blocco 1.411.200, che si prevede sarà prodotto intorno all'anno 2035, sarà stato emesso il 99% di tutti i bitcoin che mai esisteranno. A causa del tasso di emissione decrescente di Bitcoin, nel lungo termine la valuta Bitcoin è deflazionistica. Inoltre, nessuno può costringerti ad accettare bitcoin creati oltre il tasso di emissione previsto.

Dietro le quinte, Bitcoin è anche il nome del protocollo, di una rete peer-to-peer e di un'innovazione di calcolo distribuito. Bitcoin si basa su decenni di ricerca in crittografia e sistemi distribuiti e comprende almeno quattro innovazioni chiave riunite in una combinazione unica e potente. Bitcoin è costituito da:

- Una rete peer-to-peer decentralizzata (il protocollo Bitcoin)
- Un registro pubblico delle transazioni (la blockchain)
- Un insieme di regole per la convalida indipendente delle transazioni e l'emissione della valuta (regole di consenso)
- Un meccanismo per raggiungere un consenso decentralizzato globale sulla blockchain valida (algoritmo proof-of-work)

Come sviluppatore, vedo Bitcoin come una sorta di internet del denaro, una rete per propagare valore e garantire la proprietà di asset digitali tramite il calcolo distribuito. C'è molto di più in Bitcoin di quanto non appaia a prima vista.

In questo capitolo inizieremo spiegando alcuni dei concetti e dei termini principali, procurandoci il software necessario e usando Bitcoin per semplici transazioni. Nei capitoli successivi, inizieremo a svelare gli strati tecnologici che rendono possibile Bitcoin ed esamineremo il funzionamento interno della rete e del protocollo Bitcoin.

Valute digitali prima di Bitcoin

L'emergere di una moneta digitale praticabile è strettamente legato agli sviluppi della crittografia. Ciò non sorprende se si considerano le sfide fondamentali legate all'uso di bit per rappresentare un valore che può essere scambiato con beni e servizi. Tre domande fondamentali per chiunque accetti moneta digitale sono:

- Posso fidarmi che il denaro sia autentico e non contraffatto?
- Posso fidarmi che la moneta digitale possa essere spesa una sola volta (noto come problema del "double-spend")?
- Posso essere sicuro che nessun altro possa rivendicare la proprietà di questo denaro al posto mio?

Gli emittenti di moneta cartacea combattono costantemente il problema della contraffazione utilizzando carte e tecnologie di stampa sempre più sofisticate. La moneta fisica affronta facilmente il problema della doppia spesa perché la stessa banconota non può trovarsi in due posti contemporaneamente. Naturalmente, anche la moneta convenzionale viene spesso conservata e trasmessa digitalmente. In questi casi, i problemi di contraffazione e doppia spesa sono gestiti compensando tutte le transazioni elettroniche attraverso autorità centrali che hanno una visione globale della valuta in circolazione. Per la moneta digitale, che non può sfruttare inchiostri speciali o strisce olografiche, la crittografia fornisce la base per fidarsi della legittimità della rivendicazione di valore da parte di un utente. In particolare, le firme digitali crittografiche consentono a un utente di firmare un asset digitale o una transazione dimostrando la proprietà di tale asset. Con un'architettura adeguata, le firme digitali possono essere utilizzate anche per affrontare il problema della doppia spesa.

Quando la crittografia iniziò a diventare più ampiamente disponibile e compresa alla fine degli anni '80, molti ricercatori iniziarono a cercare di utilizzare la crittografia per costruire valute digitali. I primi progetti di valuta digitale emettevano moneta digitale, solitamente garantita da una valuta nazionale o da un metallo prezioso come l'oro.

Sebbene queste prime valute digitali funzionassero, erano centralizzate e, di conseguenza, facili da attaccare da parte di governi e hacker. Le prime valute digitali utilizzavano una stanza di compensazione centrale per regolare tutte le transazioni a intervalli regolari, proprio come un sistema bancario tradizionale. Sfortunatamente, nella maggior parte dei casi queste nascenti valute digitali furono prese di mira da governi preoccupati e alla fine eliminate per vie legali. Alcune fallirono in spettacolari crolli quando la società madre liquidò improvvisamente. Per resistere agli interventi di antagonisti, siano essi governi legittimi o elementi criminali, era necessaria una valuta digitale *decentralizzata* per evitare un unico punto di attacco. Bitcoin è un sistema del genere, decentralizzato per progettazione e privo di qualsiasi autorità centrale o punto di controllo che possa essere attaccato o corrotto.

### Storia di Bitcoin

Bitcoin fu descritto per la prima volta nel 2008 con la pubblicazione di un articolo intitolato "Bitcoin: A Peer-to-Peer Electronic Cash System" (Bitcoin: un sistema di moneta elettronica peer-to-peer), <sup>[<a href="#_footnotedef_1" title="Vedi nota a piè di pagina.">1</a>]</sup> scritto sotto lo pseudonimo di Satoshi Nakamoto (vedi [\[satoshi\_whitepaper\]](#satoshi_whitepaper)). Nakamoto combinò diverse invenzioni precedenti, come le firme digitali e Hashcash, per creare un sistema di moneta elettronica completamente decentralizzato che non si basa su un'autorità centrale per l'emissione, la compensazione e la convalida delle transazioni. Un'innovazione chiave fu l'uso di un sistema di calcolo distribuito (chiamato algoritmo "proof-of-work") per condurre una lotteria globale ogni 10 minuti in media, consentendo alla rete decentralizzata di raggiungere il *consenso* sullo stato delle transazioni. Ciò risolve elegantemente il problema della doppia spesa, in cui una singola unità di valuta può essere spesa due volte. In precedenza, il problema della doppia spesa era un punto debole della valuta digitale e veniva affrontato compensando tutte le transazioni tramite una stanza di compensazione centrale.

La rete Bitcoin è stata avviata nel 2009, basandosi su un'implementazione di riferimento pubblicata da Nakamoto e da allora modificata da molti altri programmatori. Il numero e la potenza delle macchine che eseguono l'algoritmo proof-of-work (mining), che fornisce sicurezza e resilienza a Bitcoin, sono aumentati esponenzialmente, e la loro potenza computazionale combinata supera ora il numero complessivo di operazioni di calcolo dei più potenti supercomputer mondiali.

Satoshi Nakamoto si ritirò dalla scena pubblica nell'aprile 2011, lasciando la responsabilità dello sviluppo del codice e della rete a un fiorente gruppo di volontari. L'identità della persona o delle persone dietro Bitcoin è ancora sconosciuta. Tuttavia, né Satoshi Nakamoto né chiunque altro esercita un controllo individuale sul sistema Bitcoin, che opera sulla base di principi matematici completamente trasparenti, codice open source e consenso tra i partecipanti. L'invenzione stessa è rivoluzionaria e ha già generato nuova scienza nei campi del calcolo distribuito, dell'economia e dell'econometria.

Una soluzione a un problema di calcolo distribuito

L'invenzione di Satoshi Nakamoto è anche una soluzione pratica e innovativa a un problema di calcolo distribuito noto come "problema dei generali bizantini". In breve, il problema consiste nel tentativo di far sì che più partecipanti senza un leader concordino una linea d'azione scambiandosi informazioni su una rete inaffidabile e potenzialmente compromessa. La soluzione di Satoshi Nakamoto, che utilizza il concetto di proof-of-work per raggiungere il consenso *senza un'autorità centrale fidata*, rappresenta una svolta nel calcolo distribuito.

### Per iniziare

Bitcoin è un protocollo a cui si può accedere utilizzando un'applicazione che parla tale protocollo. Un "portafoglio Bitcoin" è l'interfaccia utente più comune per il sistema Bitcoin, proprio come un browser web è l'interfaccia utente più comune per il protocollo HTTP. Esistono molte implementazioni e marche di portafogli Bitcoin, così come esistono molte marche di browser web (ad esempio Chrome, Safari e Firefox). E proprio come tutti noi abbiamo i nostri browser preferiti, i portafogli Bitcoin variano in termini di qualità, prestazioni, sicurezza, privacy e affidabilità. Esiste anche un'implementazione di riferimento del protocollo Bitcoin che include un portafoglio, nota come "Bitcoin Core", derivata dall'implementazione originale scritta da Satoshi Nakamoto.

#### Scegliere un portafoglio Bitcoin

I portafogli Bitcoin sono una delle applicazioni più attivamente sviluppate nell'ecosistema Bitcoin. C'è un'intensa competizione, e mentre probabilmente in questo momento un nuovo portafoglio è in fase di sviluppo, diversi portafogli dell'anno scorso non sono più attivamente mantenuti. Molti portafogli si concentrano su piattaforme specifiche o usi particolari e alcuni sono più adatti ai principianti, mentre altri sono ricchi di funzionalità per utenti avanzati. La scelta del portafoglio è altamente soggettiva e dipende dall'uso e dall'esperienza dell'utente. Pertanto, sarebbe inutile raccomandare una marca o un portafoglio specifico. Tuttavia, possiamo categorizzare i portafogli Bitcoin in base alla loro piattaforma e funzione e fornire un po' di chiarezza su tutti i diversi tipi di portafogli esistenti. Vale la pena provare diversi portafogli fino a trovarne uno che soddisfi le proprie esigenze.

##### Tipi di portafogli Bitcoin

I portafogli Bitcoin possono essere classificati come segue, in base alla piattaforma:

Portafoglio desktop

Un portafoglio desktop è stato il primo tipo di portafoglio Bitcoin creato come implementazione di riferimento. Molti utenti utilizzano portafogli desktop per le funzionalità, l'autonomia e il controllo che offrono. L'esecuzione su sistemi operativi di uso generale come Windows e macOS presenta tuttavia alcuni svantaggi in termini di sicurezza, poiché queste piattaforme sono spesso insicure e mal configurate.

Portafoglio mobile

Un portafoglio mobile è il tipo più comune di portafoglio Bitcoin. Funzionando su sistemi operativi per smartphone come Apple iOS e Android, questi portafogli sono spesso un'ottima scelta per i nuovi utenti. Molti sono progettati per la semplicità e la facilità d'uso, ma esistono anche portafogli mobili completi per utenti esperti. Per evitare di scaricare e archiviare grandi quantità di dati, la maggior parte dei portafogli mobili recupera le informazioni da server remoti, riducendo la tua privacy poiché rivela a terze parti informazioni sui tuoi indirizzi e saldi Bitcoin.

Portafoglio web

I portafogli web sono accessibili tramite un browser web e conservano il portafoglio dell'utente su un server di proprietà di terzi. È simile alla webmail in quanto si basa interamente su un server di terze parti. Alcuni di questi servizi operano utilizzando codice lato client in esecuzione nel browser dell'utente, che mantiene il controllo delle chiavi Bitcoin nelle mani dell'utente, sebbene la dipendenza dell'utente dal server comprometta comunque la sua privacy. La maggior parte, tuttavia, prende il controllo delle chiavi Bitcoin dagli utenti in cambio della facilità d'uso. È sconsigliabile conservare grandi quantità di bitcoin su sistemi di terze parti.

Dispositivi di firma hardware

I dispositivi di firma hardware sono dispositivi in grado di memorizzare le chiavi e firmare le transazioni utilizzando hardware e firmware specializzati. Di solito si collegano a un portafoglio desktop, mobile o web tramite cavo USB, comunicazione in prossimità (NFC) o una fotocamera con codici QR. Gestendo tutte le operazioni relative a Bitcoin sull'hardware specializzato, questi portafogli sono meno vulnerabili a molti tipi di attacchi. I dispositivi di firma hardware sono talvolta chiamati "portafogli hardware", ma devono essere abbinati a un portafoglio completo per inviare e ricevere transazioni, e la sicurezza e la privacy offerte da tale portafoglio abbinato giocano un ruolo fondamentale nel determinare quanta sicurezza e privacy ottiene l'utente quando utilizza il dispositivo di firma hardware.

##### Nodo completo vs Leggero

Un altro modo per categorizzare i portafogli Bitcoin è in base al loro grado di autonomia e al modo in cui interagiscono con la rete Bitcoin:

Nodo completo

Un nodo completo è un programma che convalida l'intera cronologia delle transazioni Bitcoin (ogni transazione di ogni utente, di sempre). Opzionalmente, i nodi completi possono anche archiviare le transazioni precedentemente convalidate e fornire dati ad altri programmi Bitcoin, sia sullo stesso computer che su internet. Un nodo completo utilizza risorse computazionali sostanziali—all'incirca equivalenti a guardare un video in streaming di un'ora per ogni giorno di transazioni Bitcoin—ma il nodo completo offre completa autonomia ai suoi utenti.

Client leggero

Un client leggero, noto anche come client a verifica di pagamento semplificata (SPV), si connette a un nodo completo o ad un altro server remoto per ricevere e inviare informazioni sulle transazioni Bitcoin, ma memorizza il portafoglio dell'utente localmente, convalida parzialmente le transazioni che riceve e crea autonomamente transazioni in uscita.

Client API di terze parti

Un client API di terze parti interagisce con Bitcoin attraverso un sistema di API di terze parti anziché connettersi direttamente alla rete Bitcoin. Il portafoglio può essere conservato dall'utente o dai server di terze parti, ma il client si fida del server remoto per fornire informazioni accurate e proteggere la sua privacy.

| Suggerimento | Bitcoin è una rete peer-to-peer (P2P). I nodi completi sono i *peer:* ogni peer convalida individualmente ogni transazione confermata e può fornire dati al proprio utente con piena autorevolezza. I portafogli leggeri e altri software sono *client:* ogni client dipende da uno o più peer per ottenere dati validi. I client Bitcoin possono eseguire una convalida secondaria su alcuni dei dati che ricevono e stabilire connessioni a più peer per ridurre la loro dipendenza dall'integrità di un singolo peer, ma la sicurezza di un client si basa in ultima analisi sull'integrità dei suoi peer. |
| --- | --- |

##### Chi controlla le chiavi

Una considerazione aggiuntiva molto importante è *chi controlla le chiavi*. Come vedremo nei capitoli successivi, l'accesso ai bitcoin è controllato da "chiavi private", che sono come PIN molto lunghi. Se sei l'unico ad avere il controllo su queste chiavi private, hai il controllo dei tuoi bitcoin. Al contrario, se non ne hai il controllo, i tuoi bitcoin sono gestiti da una terza parte che alla fine controlla i tuoi fondi per tuo conto. Il software di gestione delle chiavi rientra in due importanti categorie basate sul controllo: *portafogli*, in cui tu controlli le chiavi e i fondi, e conti presso depositari in cui una terza parte controlla le chiavi. Per enfatizzare questo punto, io (Andreas) ho coniato la frase: *Le tue chiavi, i tuoi bitcoin. Non le tue chiavi, non i tuoi bitcoin*.

Combinando queste categorizzazioni, molti portafogli Bitcoin ricadono in alcuni gruppi, i tre più comuni sono: nodo completo desktop (controlli le chiavi), portafoglio mobile leggero (controlli le chiavi) e conti online con terze parti (non controlli le chiavi). I confini tra le diverse categorie sono talvolta sfumati, poiché il software funziona su più piattaforme e può interagire con la rete in modi diversi.

#### Avvio rapido

Alice non è un'utente tecnica e ha solo recentemente sentito parlare di Bitcoin dalla sua amica Joe. Durante una festa, Joe sta spiegando con entusiasmo Bitcoin a tutti i presenti e offre una dimostrazione. Incuriosita, Alice chiede come può iniziare con Bitcoin. Joe dice che un portafoglio mobile è la scelta migliore per i nuovi utenti e le consiglia alcuni dei suoi portafogli preferiti. Alice ne scarica uno raccomandato da Joe e lo installa sul suo telefono.

Quando Alice esegue l'applicazione del portafoglio per la prima volta, sceglie l'opzione per creare un nuovo portafoglio Bitcoin. Poiché il portafoglio che ha scelto è non-custodiale, Alice (e solo Alice) avrà il controllo delle sue chiavi. Pertanto, è sua responsabilità farne il backup, poiché perdere le chiavi significa perdere l'accesso ai suoi bitcoin. Per facilitare questo, il suo portafoglio produce un *codice di recupero* che può essere utilizzato per ripristinare il suo portafoglio.

#### Codici di recupero

La maggior parte dei moderni portafogli Bitcoin non-custodiali fornirà un codice di recupero per il backup da parte dell'utente. Il codice di recupero di solito è composto da numeri, lettere o parole selezionati casualmente dal software, ed è utilizzato come base per le chiavi generate dal portafoglio. Vedi [\[recovery\_code\_sample\]](#recovery_code_sample) per alcuni esempi.

Esempi di codici di recupero

| Portafoglio | Codice di recupero |
| --- | --- |
| BlueWallet | (1) media (2) suspect (3) effort (4) dish (5) album (6) shaft (7) price (8) junk (9) pizza (10) situate (11) oyster (12) rib |
| Electrum | nephew dog crane clever quantum crazy purse traffic repeat fruit old clutch |
| Muun | LAFV TZUN V27E NU4D WPF4 BRJ4 ELLP BNFL |

| Suggerimento | Un codice di recupero è talvolta chiamato "mnemonico" o "frase mnemonica", il che implica che dovresti memorizzare la frase, ma scrivere la frase su carta richiede meno sforzo e tende ad essere più affidabile della memoria della maggior parte delle persone. Un altro nome alternativo è "frase seme" perché fornisce l'input ("seme") alla funzione che genera tutte le chiavi di un portafoglio. |
| --- | --- |

Se succede qualcosa al portafoglio di Alice, può scaricare una nuova copia del suo software del portafoglio e inserire questo codice di recupero per ricostruire il database del portafoglio di tutte le transazioni onchain che ha mai inviato o ricevuto. Tuttavia, il recupero dal codice di recupero non ripristinerà da solo eventuali dati aggiuntivi che Alice ha inserito nel suo portafoglio, come le etichette associate a particolari indirizzi o transazioni. Anche se perdere l'accesso a quei metadati non è importante quanto perdere l'accesso al denaro, può comunque essere importante a modo suo. Immagina di dover rivedere un vecchio estratto conto bancario o della carta di credito e il nome di ogni entità a cui hai pagato (o che ti ha pagato) è stato cancellato. Per evitare di perdere i metadati, molti portafogli forniscono una funzionalità di backup aggiuntiva oltre ai codici di recupero.

Per alcuni portafogli, quella funzionalità di backup aggiuntiva è oggi ancora più importante di un tempo. Molti pagamenti Bitcoin vengono ora effettuati utilizzando la tecnologia *offchain*, in cui non tutti i pagamenti sono memorizzati nella blockchain pubblica. Ciò riduce i costi per gli utenti e migliora la privacy, tra gli altri vantaggi, ma significa che un meccanismo come i codici di recupero che dipende dai dati onchain non può garantire il recupero di tutti i bitcoin di un utente. Per le applicazioni con supporto offchain, è importante effettuare frequenti backup del database del portafoglio.

È interessante notare che, quando si ricevono fondi su un nuovo portafoglio mobile per la prima volta, molti portafogli spesso riverificheranno che tu abbia eseguito correttamente il backup del tuo codice di recupero. Questo può variare da un semplice messaggio alla richiesta all'utente di reinserire manualmente il codice.

| Avvertenza | Sebbene molti portafogli legittimi ti chiederanno di reinserire il tuo codice di recupero, ci sono anche molte applicazioni malware che imitano il design di un portafoglio, insistono affinché tu inserisca il codice di recupero e poi inoltrano qualsiasi codice inserito allo sviluppatore del malware in modo che possano rubare i tuoi fondi. Questo è l'equivalente dei siti web di phishing che cercano di indurti con l'inganno a fornire la tua passphrase bancaria. Per la maggior parte delle applicazioni di portafoglio, le uniche volte in cui ti chiederanno il codice di recupero sono durante la configurazione iniziale (prima che tu abbia ricevuto bitcoin) e durante il recupero (dopo aver perso l'accesso al portafoglio originale). Se l'applicazione richiede il tuo codice di recupero in qualsiasi altro momento, consulta un esperto per assicurarti di non essere vittima di phishing. |
| --- | --- |

#### Indirizzi Bitcoin

Alice è ora pronta per iniziare a usare il suo nuovo portafoglio Bitcoin. La sua applicazione del portafoglio ha generato casualmente una chiave privata (descritta più dettagliatamente in [\[private\_keys\]](#private_keys)) che verrà utilizzata per derivare indirizzi Bitcoin che conducono al suo portafoglio. A questo punto, i suoi indirizzi Bitcoin non sono noti alla rete Bitcoin né "registrati" presso alcuna parte del sistema Bitcoin. I suoi indirizzi Bitcoin sono semplicemente numeri che corrispondono alla sua chiave privata che può utilizzare per controllare l'accesso ai fondi. Gli indirizzi sono generati autonomamente dal suo portafoglio senza riferimento o registrazione presso alcun servizio.

| Suggerimento | Esistono vari formati di indirizzi e fatture Bitcoin. Gli indirizzi e le fatture possono essere condivisi con altri utenti Bitcoin che possono usarli per inviare bitcoin direttamente al tuo portafoglio. Puoi condividere un indirizzo o una fattura con altre persone senza preoccuparti della sicurezza dei tuoi bitcoin. A differenza di un numero di conto bancario, chiunque apprenda uno dei tuoi indirizzi Bitcoin non può prelevare denaro dal tuo portafoglio: tutte le spese devono essere avviate da te. Tuttavia, se dai a due persone lo stesso indirizzo, potranno vedere quanti bitcoin l'altra persona ti ha inviato. Se pubblichi il tuo indirizzo pubblicamente, tutti potranno vedere quanto bitcoin altre persone hanno inviato a quell'indirizzo. Per proteggere la tua privacy, dovresti generare una nuova fattura con un nuovo indirizzo ogni volta che richiedi un pagamento. |
| --- | --- |

#### Ricevere Bitcoin

Alice utilizza il pulsante *Ricevi*, che mostra un codice QR, come illustrato in [Alice usa la schermata Ricevi sul suo portafoglio mobile Bitcoin e mostra il suo indirizzo in formato codice QR.](#wallet_receive).

[![[mbc3_0101.png|Schermata Ricevi del portafoglio con codice QR visualizzato. Immagine derivata dalla Bitcoin Design Guide CC-BY]]](https://github.com/bitcoinbook/bitcoinbook/blob/develop/images/mbc3_0101.png)

Figura 1. Alice usa la schermata Ricevi sul suo portafoglio mobile Bitcoin e mostra il suo indirizzo in formato codice QR.

Il codice QR è il quadrato con uno schema di punti bianchi e neri, che funge da forma di codice a barre contenente le stesse informazioni in un formato che può essere scansionato dalla fotocamera dello smartphone di Joe.

| Avvertenza | Qualsiasi fondo inviato agli indirizzi presenti in questo libro andrà perso. Se vuoi testare l'invio di bitcoin, ti invitiamo a donarli a un'organizzazione benefica che accetta bitcoin. |
| --- | --- |

#### Ottenere i tuoi primi bitcoin

Il primo compito per i nuovi utenti è acquisire un po' di bitcoin.

Le transazioni Bitcoin sono irreversibili. La maggior parte delle reti di pagamento elettronico come carte di credito, carte di debito, PayPal e bonifici bancari sono reversibili. Per chi vende bitcoin, questa differenza introduce un rischio molto elevato che l'acquirente annulli il pagamento elettronico dopo aver ricevuto i bitcoin, frodando di fatto il venditore. Per mitigare questo rischio, le aziende che accettano pagamenti elettronici tradizionali in cambio di bitcoin di solito richiedono agli acquirenti di sottoporsi a verifica dell'identità e controlli di solvibilità, che possono richiedere diversi giorni o settimane. Come nuovo utente, ciò significa che non puoi acquistare bitcoin all'istante con una carta di credito. Tuttavia, con un po' di pazienza e pensiero creativo, non sarà necessario.

Ecco alcuni metodi per acquisire bitcoin come nuovo utente:

- Trova un amico che abbia bitcoin e comprane un po' direttamente da lui o da lei. Molti utenti Bitcoin iniziano in questo modo. Questo metodo è il meno complicato. Un modo per incontrare persone con bitcoin è partecipare a un incontro Bitcoin locale elencato su [Meetup.com](https://meetup.com/).
- Guadagna bitcoin vendendo un prodotto o un servizio in cambio di bitcoin. Se sei un programmatore, vendi le tue competenze di programmazione. Se sei un parrucchiere, taglia i capelli per bitcoin.
- Usa un bancomat Bitcoin nella tua città. Un bancomat Bitcoin è una macchina che accetta contanti e invia bitcoin al tuo portafoglio Bitcoin sullo smartphone.
- Usa un exchange di valuta Bitcoin collegato al tuo conto bancario. Molti paesi hanno ora exchange di valuta che offrono un mercato per acquirenti e venditori per scambiare bitcoin con valuta locale. I servizi di quotazione dei tassi di cambio, come [BitcoinAverage](https://bitcoinaverage.com/), spesso mostrano un elenco di exchange Bitcoin per ogni valuta.

| Suggerimento | Uno dei vantaggi di Bitcoin rispetto ad altri sistemi di pagamento è che, se utilizzato correttamente, offre agli utenti molta più privacy. Acquisire, detenere e spendere bitcoin non richiede di divulgare informazioni sensibili e personalmente identificabili a terze parti. Tuttavia, quando bitcoin incontra i sistemi tradizionali, come gli exchange di valuta, spesso si applicano regolamentazioni nazionali e internazionali. Per cambiare bitcoin nella tua valuta nazionale, ti verrà spesso richiesto di fornire una prova di identità e informazioni bancarie. Gli utenti dovrebbero essere consapevoli che una volta che un indirizzo Bitcoin è collegato a un'identità, anche altre transazioni Bitcoin associate potrebbero diventare facili da identificare e tracciare, comprese le transazioni effettuate in precedenza. Questo è uno dei motivi per cui molti utenti scelgono di mantenere conti exchange dedicati indipendenti dai loro portafogli. |
| --- | --- |

Alice è stata introdotta a Bitcoin da un'amica, quindi ha un modo semplice per acquisire i suoi primi bitcoin. Successivamente, vedremo come acquista bitcoin dal suo amico Joe e come Joe invia i bitcoin al suo portafoglio.

#### Trovare il prezzo attuale di Bitcoin

Prima che Alice possa acquistare bitcoin da Joe, devono concordare il *tasso di cambio* tra bitcoin e dollari statunitensi. Questo solleva una domanda comune per chi è nuovo a Bitcoin: "Chi stabilisce il prezzo dei bitcoin?" La risposta breve è che il prezzo è determinato dai mercati.

Bitcoin, come la maggior parte delle altre valute, ha un *tasso di cambio fluttuante*. Ciò significa che il valore del bitcoin fluttua in base alla domanda e all'offerta nei vari mercati in cui viene scambiato. Ad esempio, il "prezzo" del bitcoin in dollari statunitensi viene calcolato in ciascun mercato sulla base dell'ultimo scambio di bitcoin e dollari statunitensi. Pertanto, il prezzo tende a fluttuare minuziosamente diverse volte al secondo. Un servizio di quotazione aggrega i prezzi di diversi mercati e calcola una media ponderata per volume che rappresenta l'ampio tasso di cambio di mercato di una coppia di valute (ad esempio BTC/USD).

Ci sono centinaia di applicazioni e siti web che possono fornire il tasso di mercato corrente. Ecco alcuni dei più popolari:

[Bitcoin Average](https://bitcoinaverage.com/)

Un sito che fornisce una semplice visualizzazione della media ponderata per volume per ogni valuta.

[CoinCap](https://coincap.io/)

Un servizio che elenca la capitalizzazione di mercato e i tassi di cambio di centinaia di criptovalute, inclusi i bitcoin.

[Chicago Mercantile Exchange Bitcoin Reference Rate](https://oreil.ly/ACieC)

Un tasso di riferimento che può essere utilizzato per riferimenti istituzionali e contrattuali, fornito come parte dei feed di dati sugli investimenti dal CME.

Oltre a questi vari siti e applicazioni, alcuni portafogli Bitcoin convertiranno automaticamente gli importi tra bitcoin e altre valute.

#### Inviare e ricevere Bitcoin

Alice ha deciso di acquistare 0,001 bitcoin. Dopo che lei e Joe hanno controllato il tasso di cambio, lei dà a Joe una quantità adeguata di contanti, apre la sua applicazione del portafoglio mobile e seleziona Ricevi. Questo mostra un codice QR con il primo indirizzo Bitcoin di Alice.

Joe seleziona quindi Invia sul suo portafoglio per smartphone e apre lo scanner di codici QR. Ciò consente a Joe di scansionare il codice a barre con la fotocamera del suo smartphone in modo da non dover digitare l'indirizzo Bitcoin di Alice, che è piuttosto lungo.

Joe ha ora impostato l'indirizzo Bitcoin di Alice come destinatario. Joe inserisce l'importo come 0,001 bitcoin (BTC); vedi [Schermata di invio del portafoglio Bitcoin.](#wallet-send). Alcuni portafogli potrebbero mostrare l'importo in un diverso taglio: 0,001 BTC equivale a 1 millibitcoin (mBTC) o 100.000 satoshi (sats).

Alcuni portafogli potrebbero anche suggerire a Joe di inserire un'etichetta per questa transazione; in tal caso, Joe inserisce "Alice". Tra settimane o mesi, questo aiuterà Joe a ricordare perché ha inviato questi 0,001 bitcoin. Alcuni portafogli potrebbero anche chiedere a Joe informazioni sulle commissioni. A seconda del portafoglio e di come viene inviata la transazione, il portafoglio potrebbe chiedere a Joe di inserire un tasso di commissione di transazione o suggerirgliene uno (o un tasso di commissione). Maggiore è la commissione di transazione, più velocemente la transazione verrà confermata (vedi [Conferme](#confirmations)).

[![[mbc3_0102.png|Schermata di invio del portafoglio. Immagine derivata dalla Bitcoin Design Guide CC-BY]]](https://github.com/bitcoinbook/bitcoinbook/blob/develop/images/mbc3_0102.png)

Figura 2. Schermata di invio del portafoglio Bitcoin.

Joe quindi controlla attentamente di aver inserito l'importo corretto, perché sta per trasmettere denaro e gli errori diventeranno presto irreversibili. Dopo aver ricontrollato l'indirizzo e l'importo, preme Invia per trasmettere la transazione. Il portafoglio mobile Bitcoin di Joe costruisce una transazione che assegna 0,001 BTC all'indirizzo fornito da Alice, prelevando i fondi dal portafoglio di Joe e firmando la transazione con le chiavi private di Joe. Questo comunica alla rete Bitcoin che Joe ha autorizzato un trasferimento di valore al nuovo indirizzo di Alice. Mentre la transazione viene trasmessa tramite il protocollo peer-to-peer, si propaga rapidamente attraverso la rete Bitcoin. Dopo pochi secondi, la maggior parte dei nodi ben collegati nella rete riceve la transazione e vede l'indirizzo di Alice per la prima volta.

Nel frattempo, il portafoglio di Alice è costantemente "in ascolto" di nuove transazioni sulla rete Bitcoin, cercando quelle che corrispondono agli indirizzi che contiene. Pochi secondi dopo che il portafoglio di Joe trasmette la transazione, il portafoglio di Alice indicherà che sta ricevendo 0,001 BTC.

Conferme

Inizialmente, l'indirizzo di Alice mostrerà la transazione da Joe come "Non confermata". Ciò significa che la transazione è stata propagata alla rete ma non è ancora stata registrata nel registro delle transazioni Bitcoin, noto come blockchain. Per essere confermata, una transazione deve essere inclusa in un blocco e aggiunta alla blockchain, il che avviene in media ogni 10 minuti. In termini finanziari tradizionali questo è noto come *compensazione*. Per maggiori dettagli sulla propagazione, convalida e compensazione (conferma) delle transazioni bitcoin, vedi [\[mining\]](#mining).

Alice è ora la fiera proprietaria di 0,001 BTC che può spendere. Nei giorni successivi, Alice acquista altri bitcoin utilizzando un bancomat e un exchange. Nel prossimo capitolo esamineremo il suo primo acquisto con Bitcoin e analizzeremo più in dettaglio le tecnologie sottostanti di transazione e propagazione.

---

[1](#_footnoteref_1). ["Bitcoin: A Peer-to-Peer Electronic Cash System"](https://oreil.ly/KUaBM), Satoshi Nakamoto.