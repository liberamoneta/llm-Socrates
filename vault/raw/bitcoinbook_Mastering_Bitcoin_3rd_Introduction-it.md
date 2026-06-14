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

Bitcoin è un insieme di concetti e tecnologie che costituiscono la base di un ecosistema di moneta digitale. Unità di valuta chiamate bitcoin vengono utilizzate per conservare e trasmettere valore tra i partecipanti alla rete Bitcoin. Gli utenti Bitcoin comunicano tra loro utilizzando il protocollo Bitcoin principalmente tramite internet, sebbene possano essere utilizzate anche altre reti di trasporto. Lo stack del protocollo Bitcoin, disponibile come software open source, può essere eseguito su un'ampia gamma di dispositivi informatici, inclusi laptop e smartphone, rendendo la tecnologia facilmente accessibile.

| Suggerimento | In questo libro, l'unità di valuta è chiamata "bitcoin" con la *b* minuscola, e il sistema è chiamato "Bitcoin" con la *B* maiuscola. |
| --- | --- |

Gli utenti possono trasferire bitcoin sulla rete per fare praticamente qualsiasi cosa si possa fare con le valute convenzionali, inclusi acquistare e vendere beni, inviare denaro a persone o organizzazioni, o concedere credito. Il bitcoin può essere acquistato, venduto e scambiato con altre valute presso appositi exchange di valuta. Bitcoin è probabilmente la forma di denaro perfetta per internet perché è veloce, sicura e senza confini.

A differenza delle valute tradizionali, la valuta bitcoin è completamente virtuale. Non esistono monete fisiche o nemmeno singole monete digitali. Le monete sono implicite nelle transazioni che trasferiscono valore dal pagatore al ricevente. Gli utenti di Bitcoin controllano chiavi che permettono loro di dimostrare la proprietà di bitcoin nella rete Bitcoin. Con queste chiavi, possono firmare transazioni per sbloccare il valore e spenderlo trasferendolo a un nuovo proprietario. Le chiavi sono spesso conservate in un portafoglio digitale sul computer o smartphone di ogni utente. Il possesso della chiave che può firmare una transazione è l'unico prerequisito per spendere bitcoin, mettendo il controllo interamente nelle mani di ogni utente.

Bitcoin è un sistema distribuito, peer-to-peer. Di conseguenza, non esiste un server centrale o un punto di controllo. Le unità di bitcoin vengono create attraverso un processo chiamato "mining", che implica l'esecuzione ripetuta di un compito computazionale che fa riferimento a un elenco di transazioni Bitcoin recenti. Qualsiasi partecipante alla rete Bitcoin può operare come miner, utilizzando i propri dispositivi informatici per aiutare a proteggere le transazioni. Ogni 10 minuti, in media, un miner Bitcoin può aggiungere sicurezza alle transazioni passate e viene ricompensato sia con nuovi bitcoin sia con le commissioni pagate dalle transazioni recenti. Essenzialmente, il mining di Bitcoin decentralizza le funzioni di emissione della valuta e di compensazione di una banca centrale e sostituisce la necessità di qualsiasi banca centrale.

Il protocollo Bitcoin include algoritmi integrati che regolano la funzione di mining attraverso la rete. La difficoltà del compito computazionale che i miner devono eseguire viene regolata dinamicamente in modo che, in media, qualcuno abbia successo ogni 10 minuti indipendentemente da quanti miner (e quanta potenza di elaborazione) stiano competendo in un dato momento. Il protocollo diminuisce anche periodicamente il numero di nuovi bitcoin creati, limitando il numero totale di bitcoin che verranno mai creati a un totale fisso di poco inferiore a 21 milioni di monete. Il risultato è che il numero di bitcoin in circolazione segue da vicino una curva facilmente prevedibile in cui metà delle monete rimanenti vengono aggiunte alla circolazione ogni quattro anni. Approssimativamente al blocco 1.411.200, che si prevede venga prodotto intorno all'anno 2035, sarà stato emesso il 99% di tutti i bitcoin che esisteranno mai. A causa del tasso di emissione decrescente di Bitcoin, nel lungo termine, la valuta Bitcoin è deflazionistica. Inoltre, nessuno può costringerti ad accettare bitcoin creati oltre il tasso di emissione previsto.

Dietro le quinte, Bitcoin è anche il nome del protocollo, una rete peer-to-peer e un'innovazione informatica distribuita. Bitcoin si basa su decenni di ricerca in crittografia e sistemi distribuiti e include almeno quattro innovazioni chiave riunite in una combinazione unica e potente. Bitcoin consiste in:

- Una rete peer-to-peer decentralizzata (il protocollo Bitcoin)
- Un registro pubblico delle transazioni (la blockchain)
- Un insieme di regole per la validazione indipendente delle transazioni e l'emissione di valuta (regole di consenso)
- Un meccanismo per raggiungere un consenso globale decentralizzato sulla blockchain valida (algoritmo di proof-of-work)

Come sviluppatore, vedo Bitcoin come analogo a internet del denaro, una rete per propagare valore e proteggere la proprietà di asset digitali tramite calcolo distribuito. C'è molto di più in Bitcoin di quanto sembri a prima vista.

In questo capitolo inizieremo spiegando alcuni dei concetti e termini principali, ottenendo il software necessario e utilizzando Bitcoin per semplici transazioni. Nei capitoli seguenti, inizieremo a svelare gli strati di tecnologia che rendono possibile Bitcoin ed esamineremo il funzionamento interno della rete e del protocollo Bitcoin.

Valute Digitali Prima di Bitcoin

L'emergere di moneta digitale praticabile è strettamente legato agli sviluppi della crittografia. Ciò non sorprende se si considerano le sfide fondamentali coinvolte nell'uso di bit per rappresentare valore che può essere scambiato con beni e servizi. Tre domande fondamentali per chiunque accetti denaro digitale sono:

- Posso fidarmi che il denaro sia autentico e non contraffatto?
- Posso fidarmi che il denaro digitale possa essere speso una sola volta (noto come problema della "doppia spesa")?
- Posso essere sicuro che nessun altro possa affermare che questo denaro appartiene a loro e non a me?

Gli emittenti di cartamoneta combattono costantemente il problema della contraffazione utilizzando carte e tecnologie di stampa sempre più sofisticate. Il denaro fisico risolve facilmente il problema della doppia spesa perché la stessa banconota non può trovarsi in due posti contemporaneamente. Naturalmente, anche il denaro convenzionale viene spesso conservato e trasmesso digitalmente. In questi casi, i problemi di contraffazione e doppia spesa vengono gestiti compensando tutte le transazioni elettroniche attraverso autorità centrali che hanno una visione globale della valuta in circolazione. Per il denaro digitale, che non può sfruttare inchiostri esoterici o strisce olografiche, la crittografia fornisce la base per fidarsi della legittimità della rivendicazione di valore da parte di un utente. Nello specifico, le firme digitali crittografiche consentono a un utente di firmare un asset digitale o una transazione dimostrando la proprietà di quell'asset. Con l'architettura appropriata, le firme digitali possono anche essere utilizzate per affrontare il problema della doppia spesa.

Quando la crittografia iniziò a diventare più ampiamente disponibile e compresa alla fine degli anni '80, molti ricercatori iniziarono a cercare di utilizzare la crittografia per costruire valute digitali. Questi primi progetti di valuta digitale emettevano denaro digitale, solitamente garantito da una valuta nazionale o da un metallo prezioso come l'oro.

Sebbene queste precedenti valute digitali funzionassero, erano centralizzate e, di conseguenza, facili da attaccare da parte di governi e hacker. Le prime valute digitali utilizzavano una camera di compensazione centrale per saldare tutte le transazioni a intervalli regolari, proprio come un sistema bancario tradizionale. Sfortunatamente, nella maggior parte dei casi, queste nascenti valute digitali furono prese di mira da governi preoccupati e alla fine estinte per via legale. Alcune fallirono in spettacolari crolli quando la società madre liquidò bruscamente. Per essere robusti contro l'intervento di antagonisti, siano essi governi legittimi o elementi criminali, era necessaria una valuta digitale *decentralizzata* per evitare un singolo punto di attacco. Bitcoin è un tale sistema, decentralizzato per progettazione e libero da qualsiasi autorità centrale o punto di controllo che possa essere attaccato o corrotto.

### Storia di Bitcoin

Bitcoin fu descritto per la prima volta nel 2008 con la pubblicazione di un documento intitolato "Bitcoin: A Peer-to-Peer Electronic Cash System", <sup>[<a href="#_footnotedef_1" title="Vedi nota.">1</a>]</sup> scritto sotto lo pseudonimo di Satoshi Nakamoto (vedi [\[satoshi\_whitepaper\]](#satoshi_whitepaper)). Nakamoto combinò diverse invenzioni precedenti come le firme digitali e Hashcash per creare un sistema di contante elettronico completamente decentralizzato che non si basa su un'autorità centrale per l'emissione di valuta o la compensazione e validazione delle transazioni. Un'innovazione chiave fu l'uso di un sistema di calcolo distribuito (chiamato algoritmo "proof-of-work") per condurre una lotteria globale ogni 10 minuti in media, permettendo alla rete decentralizzata di raggiungere un *consenso* sullo stato delle transazioni. Ciò risolve elegantemente il problema della doppia spesa in cui una singola unità di valuta può essere spesa due volte. In precedenza, il problema della doppia spesa era un punto debole della valuta digitale e veniva affrontato compensando tutte le transazioni attraverso una camera di compensazione centrale.

La rete Bitcoin iniziò nel 2009, basata su un'implementazione di riferimento pubblicata da Nakamoto e successivamente rivista da molti altri programmatori. Il numero e la potenza delle macchine che eseguono l'algoritmo proof-of-work (mining) che fornisce sicurezza e resilienza a Bitcoin sono aumentati esponenzialmente, e la loro potenza di calcolo combinata ora supera il numero combinato di operazioni di calcolo dei supercomputer più potenti del mondo.

Satoshi Nakamoto si ritirò dalla scena pubblica nell'aprile 2011, lasciando la responsabilità dello sviluppo del codice e della rete a un fiorente gruppo di volontari. L'identità della persona o delle persone dietro Bitcoin è ancora sconosciuta. Tuttavia, né Satoshi Nakamoto né nessun altro esercita un controllo individuale sul sistema Bitcoin, che opera basandosi su principi matematici completamente trasparenti, codice open source e consenso tra i partecipanti. L'invenzione stessa è rivoluzionaria e ha già generato nuova scienza nei campi del calcolo distribuito, dell'economia e dell'econometria.

Una Soluzione a un Problema di Calcolo Distribuito

L'invenzione di Satoshi Nakamoto è anche una soluzione pratica e innovativa a un problema nel calcolo distribuito, noto come "Problema dei Generali Bizantini". In breve, il problema consiste nel cercare di far sì che più partecipanti senza un leader concordino su una linea d'azione scambiandosi informazioni su una rete inaffidabile e potenzialmente compromessa. La soluzione di Satoshi Nakamoto, che utilizza il concetto di proof of work per raggiungere il consenso *senza un'autorità centrale fidata*, rappresenta una svolta nel calcolo distribuito.

### Per Iniziare

Bitcoin è un protocollo a cui si può accedere utilizzando un'applicazione che parla il protocollo. Un "portafoglio Bitcoin" è l'interfaccia utente più comune per il sistema Bitcoin, proprio come un browser web è l'interfaccia utente più comune per il protocollo HTTP. Esistono molte implementazioni e marche di portafogli Bitcoin, proprio come esistono molte marche di browser web (ad es. Chrome, Safari e Firefox). E proprio come tutti abbiamo i nostri browser preferiti, i portafogli Bitcoin variano in qualità, prestazioni, sicurezza, privacy e affidabilità. Esiste anche un'implementazione di riferimento del protocollo Bitcoin che include un portafoglio, nota come "Bitcoin Core", che deriva dall'implementazione originale scritta da Satoshi Nakamoto.

#### Scegliere un Portafoglio Bitcoin

I portafogli Bitcoin sono una delle applicazioni più attivamente sviluppate nell'ecosistema Bitcoin. C'è una concorrenza intensa, e mentre un nuovo portafoglio viene probabilmente sviluppato in questo momento, diversi portafogli dell'anno scorso non sono più mantenuti attivamente. Molti portafogli si concentrano su piattaforme specifiche o usi specifici e alcuni sono più adatti ai principianti mentre altri sono pieni di funzionalità per utenti avanzati. Scegliere un portafoglio è altamente soggettivo e dipende dall'uso e dall'esperienza dell'utente. Pertanto, sarebbe inutile raccomandare una marca o un portafoglio specifico. Tuttavia, possiamo categorizzare i portafogli Bitcoin in base alla loro piattaforma e funzione e fornire un po' di chiarezza su tutti i diversi tipi di portafogli che esistono. Vale la pena provare diversi portafogli finché non ne trovi uno che soddisfi le tue esigenze.

##### Tipi di portafogli Bitcoin

I portafogli Bitcoin possono essere categorizzati come segue, in base alla piattaforma:

Portafoglio desktop

Un portafoglio desktop è stato il primo tipo di portafoglio Bitcoin creato come implementazione di riferimento. Molti utenti utilizzano portafogli desktop per le funzionalità, l'autonomia e il controllo che offrono. L'esecuzione su sistemi operativi per uso generale come Windows e macOS presenta tuttavia alcuni svantaggi di sicurezza, poiché queste piattaforme sono spesso insicure e mal configurate.

Portafoglio mobile

Un portafoglio mobile è il tipo più comune di portafoglio Bitcoin. Eseguendo su sistemi operativi per smartphone come Apple iOS e Android, questi portafogli sono spesso un'ottima scelta per i nuovi utenti. Molti sono progettati per semplicità e facilità d'uso, ma esistono anche portafogli mobili completi per utenti esperti. Per evitare di scaricare e archiviare grandi quantità di dati, la maggior parte dei portafogli mobili recupera informazioni da server remoti, riducendo la tua privacy rivelando a terze parti informazioni sui tuoi indirizzi e saldi Bitcoin.

Portafoglio web

I portafogli web sono accessibili tramite un browser web e archiviano il portafoglio dell'utente su un server di proprietà di terze parti. Questo è simile alla webmail in quanto si basa interamente su un server di terze parti. Alcuni di questi servizi operano utilizzando codice lato client eseguito nel browser dell'utente, che mantiene il controllo delle chiavi Bitcoin nelle mani dell'utente, sebbene la dipendenza dell'utente dal server comprometta comunque la loro privacy. La maggior parte, tuttavia, prende il controllo delle chiavi Bitcoin dagli utenti in cambio della facilità d'uso. Non è consigliabile conservare grandi quantità di bitcoin su sistemi di terze parti.

Dispositivi di firma hardware

I dispositivi di firma hardware sono dispositivi che possono archiviare chiavi e firmare transazioni utilizzando hardware e firmware specializzati. Di solito si collegano a un portafoglio desktop, mobile o web tramite cavo USB, comunicazione in prossimità (NFC) o una fotocamera con codici QR. Gestendo tutte le operazioni relative a Bitcoin sull'hardware specializzato, questi portafogli sono meno vulnerabili a molti tipi di attacchi. I dispositivi di firma hardware sono talvolta chiamati "portafogli hardware", ma devono essere abbinati a un portafoglio completo per inviare e ricevere transazioni, e la sicurezza e la privacy offerte da quel portafoglio abbinato giocano un ruolo critico nel determinare quanta sicurezza e privacy ottiene l'utente quando utilizza il dispositivo di firma hardware.

##### Nodo completo vs Leggero

Un altro modo per categorizzare i portafogli Bitcoin è in base al loro grado di autonomia e a come interagiscono con la rete Bitcoin:

Nodo completo

Un nodo completo è un programma che convalida l'intera storia delle transazioni Bitcoin (ogni transazione di ogni utente, mai). Opzionalmente, i nodi completi possono anche archiviare transazioni precedentemente convalidate e servire dati ad altri programmi Bitcoin, sia sullo stesso computer che su internet. Un nodo completo utilizza risorse informatiche sostanziali—più o meno come guardare un video in streaming di un'ora per ogni giorno di transazioni Bitcoin—ma il nodo completo offre completa autonomia ai suoi utenti.

Client leggero

Un client leggero, noto anche come client di verifica del pagamento semplificata (SPV), si connette a un nodo completo o altro server remoto per ricevere e inviare informazioni sulle transazioni Bitcoin, ma archivia il portafoglio dell'utente localmente, convalida parzialmente le transazioni che riceve e crea indipendentemente transazioni in uscita.

Client API di terze parti

Un client API di terze parti è quello che interagisce con Bitcoin attraverso un sistema di API di terze parti piuttosto che connettendosi direttamente alla rete Bitcoin. Il portafoglio può essere archiviato dall'utente o da server di terze parti, ma il client si fida del server remoto per fornirgli informazioni accurate e proteggere la sua privacy.

| Suggerimento | Bitcoin è una rete peer-to-peer (P2P). I nodi completi sono i *peer*: ogni peer convalida individualmente ogni transazione confermata e può fornire dati al suo utente con piena autorità. I portafogli leggeri e altri software sono *client*: ogni client dipende da uno o più peer per fornirgli dati validi. I client Bitcoin possono eseguire una validazione secondaria su alcuni dei dati che ricevono e stabilire connessioni a più peer per ridurre la loro dipendenza dall'integrità di un singolo peer, ma la sicurezza di un client dipende in ultima analisi dall'integrità dei suoi peer. |
| --- | --- |

##### Chi controlla le chiavi

Una considerazione aggiuntiva molto importante è *chi controlla le chiavi*. Come vedremo nei capitoli successivi, l'accesso ai bitcoin è controllato da "chiavi private", che sono come PIN molto lunghi. Se sei l'unico ad avere il controllo su queste chiavi private, hai il controllo dei tuoi bitcoin. Al contrario, se non hai il controllo, allora i tuoi bitcoin sono gestiti da una terza parte che controlla in ultima analisi i tuoi fondi per tuo conto. Il software di gestione delle chiavi rientra in due importanti categorie basate sul controllo: *portafogli*, dove controlli le chiavi, e i fondi e i conti con custodi dove una terza parte controlla le chiavi. Per sottolineare questo punto, io (Andreas) ho coniato la frase: *Le tue chiavi, le tue monete. Non le tue chiavi, non le tue monete*.

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

#### Indirizzi Bitcoin

Alice è ora pronta per iniziare a usare il suo nuovo portafoglio Bitcoin. La sua applicazione portafoglio ha generato casualmente una chiave privata (descritta più in dettaglio in [\[private\_keys\]](#private_keys)) che verrà utilizzata per derivare indirizzi Bitcoin che indirizzano al suo portafoglio. A questo punto, i suoi indirizzi Bitcoin non sono noti alla rete Bitcoin né "registrati" con alcuna parte del sistema Bitcoin. I suoi indirizzi Bitcoin sono semplicemente numeri che corrispondono alla sua chiave privata che può utilizzare per controllare l'accesso ai fondi. Gli indirizzi vengono generati indipendentemente dal suo portafoglio senza riferimento o registrazione con alcun servizio.

| Suggerimento | Esistono una varietà di formati di indirizzi Bitcoin e fatture. Indirizzi e fatture possono essere condivisi con altri utenti Bitcoin che possono usarli per inviare bitcoin direttamente al tuo portafoglio. Puoi condividere un indirizzo o una fattura con altre persone senza preoccuparti della sicurezza dei tuoi bitcoin. A differenza di un numero di conto bancario, nessuno che venga a conoscenza di uno dei tuoi indirizzi Bitcoin può prelevare denaro dal tuo portafoglio—devi avviare tu tutte le spese. Tuttavia, se dai a due persone lo stesso indirizzo, saranno in grado di vedere quanti bitcoin l'altra persona ti ha inviato. Se pubblichi il tuo indirizzo pubblicamente, tutti potranno vedere quanto bitcoin altre persone hanno inviato a quell'indirizzo. Per proteggere la tua privacy, dovresti generare una nuova fattura con un nuovo indirizzo ogni volta che richiedi un pagamento. |
| --- | --- |

#### Ricevere Bitcoin

Alice usa il pulsante *Ricevi*, che visualizza un codice QR, mostrato in [Alice usa la schermata Ricevi sul suo portafoglio Bitcoin mobile e mostra il suo indirizzo in formato codice QR.](#wallet_receive).

[![[mbc3_0101.png|Schermata di ricezione del portafoglio con codice QR visualizzato. Immagine derivata da Bitcoin Design Guide CC-BY]]](https://github.com/bitcoinbook/bitcoinbook/blob/develop/images/mbc3_0101.png)

Figura 1. Alice usa la schermata Ricevi sul suo portafoglio Bitcoin mobile e mostra il suo indirizzo in formato codice QR.

Il codice QR è il quadrato con un motivo di punti bianchi e neri, che funge da forma di codice a barre che contiene le stesse informazioni in un formato che può essere scansionato dalla fotocamera dello smartphone di Joe.

| Avvertenza | Qualsiasi fondo inviato agli indirizzi in questo libro andrà perso. Se vuoi testare l'invio di bitcoin, considera di donarlo a un ente di beneficenza che accetta bitcoin. |
| --- | --- |

#### Ottenere il Tuo Primo Bitcoin

Il primo compito per i nuovi utenti è acquisire un po' di bitcoin.

Le transazioni Bitcoin sono irreversibili. La maggior parte delle reti di pagamento elettronico come carte di credito, carte di debito, PayPal e bonifici bancari sono reversibili. Per qualcuno che vende bitcoin, questa differenza introduce un rischio molto alto che l'acquirente inverta il pagamento elettronico dopo aver ricevuto bitcoin, di fatto frodando il venditore. Per mitigare questo rischio, le aziende che accettano pagamenti elettronici tradizionali in cambio di bitcoin di solito richiedono agli acquirenti di sottoporsi a verifica dell'identità e controlli di affidabilità creditizia, che possono richiedere diversi giorni o settimane. Come nuovo utente, ciò significa che non puoi acquistare bitcoin istantaneamente con una carta di credito. Con un po' di pazienza e pensiero creativo, tuttavia, non ne avrai bisogno.

Ecco alcuni metodi per acquisire bitcoin come nuovo utente:

- Trova un amico che ha bitcoin e comprane un po' direttamente da lui/lei. Molti utenti Bitcoin iniziano in questo modo. Questo metodo è il meno complicato. Un modo per incontrare persone con bitcoin è partecipare a un meetup Bitcoin locale elencato su [Meetup.com](https://meetup.com/).
- Guadagna bitcoin vendendo un prodotto o servizio per bitcoin. Se sei un programmatore, vendi le tue capacità di programmazione. Se sei un parrucchiere, taglia i capelli per bitcoin.
- Usa un Bitcoin ATM nella tua città. Un Bitcoin ATM è una macchina che accetta contanti e invia bitcoin al tuo portafoglio Bitcoin sullo smartphone.
- Usa un exchange di valuta Bitcoin collegato al tuo conto bancario. Molti paesi ora hanno exchange di valuta che offrono un mercato per acquirenti e venditori per scambiare bitcoin con valuta locale. I servizi di quotazione dei tassi di cambio, come [BitcoinAverage](https://bitcoinaverage.com/), spesso mostrano un elenco di exchange Bitcoin per ogni valuta.

| Suggerimento | Uno dei vantaggi di Bitcoin rispetto ad altri sistemi di pagamento è che, se usato correttamente, offre agli utenti molta più privacy. Acquisire, detenere e spendere bitcoin non richiede di divulgare informazioni sensibili e personalmente identificabili a terze parti. Tuttavia, dove Bitcoin tocca sistemi tradizionali, come gli exchange di valuta, spesso si applicano normative nazionali e internazionali. Per scambiare bitcoin con la tua valuta nazionale, ti verrà spesso richiesto di fornire prova di identità e informazioni bancarie. Gli utenti dovrebbero essere consapevoli che una volta che un indirizzo Bitcoin è collegato a un'identità, altre transazioni Bitcoin associate potrebbero anche diventare facili da identificare e tracciare—incluse transazioni effettuate in precedenza. Questo è uno dei motivi per cui molti utenti scelgono di mantenere conti di exchange dedicati indipendenti dai loro portafogli. |
| --- | --- |

Alice è stata introdotta a Bitcoin da un amico, quindi ha un modo semplice per acquisire i suoi primi bitcoin. Successivamente, vedremo come acquista bitcoin dal suo amico Joe e come Joe invia i bitcoin al suo portafoglio.

#### Trovare il Prezzo Corrente di Bitcoin

Prima che Alice possa acquistare bitcoin da Joe, devono concordare il *tasso di cambio* tra bitcoin e dollari USA. Ciò solleva una domanda comune per i nuovi arrivati a Bitcoin: "Chi fissa il prezzo dei bitcoin?" La risposta breve è che il prezzo è fissato dai mercati.

Bitcoin, come la maggior parte delle altre valute, ha un *tasso di cambio fluttuante*. Ciò significa che il valore del bitcoin fluttua in base alla domanda e all'offerta nei vari mercati in cui viene scambiato. Ad esempio, il "prezzo" del bitcoin in dollari USA viene calcolato in ogni mercato in base alla transazione più recente di bitcoin e dollari USA. Di conseguenza, il prezzo tende a fluttuare minuziosamente più volte al secondo. Un servizio di determinazione dei prezzi aggregherà i prezzi di diversi mercati e calcolerà una media ponderata per volume che rappresenta il tasso di cambio di mercato ampio di una coppia di valute (ad es. BTC/USD).

Esistono centinaia di applicazioni e siti web che possono fornire il tasso di mercato corrente. Ecco alcuni dei più popolari:

[Bitcoin Average](https://bitcoinaverage.com/)

Un sito che fornisce una semplice visualizzazione della media ponderata per volume per ogni valuta.

[CoinCap](https://coincap.io/)

Un servizio che elenca la capitalizzazione di mercato e i tassi di cambio di centinaia di criptovalute, inclusi i bitcoin.

[Chicago Mercantile Exchange Bitcoin Reference Rate](https://oreil.ly/ACieC)

Un tasso di riferimento che può essere utilizzato per riferimento istituzionale e contrattuale, fornito come parte dei feed di dati di investimento dal CME.

Oltre a questi vari siti e applicazioni, alcuni portafogli Bitcoin convertiranno automaticamente gli importi tra bitcoin e altre valute.

#### Inviare e Ricevere Bitcoin

Alice ha deciso di acquistare 0,001 bitcoin. Dopo che lei e Joe hanno controllato il tasso di cambio, lei dà a Joe una quantità adeguata di contanti, apre la sua applicazione portafoglio mobile e seleziona Ricevi. Questo visualizza un codice QR con il primo indirizzo Bitcoin di Alice.

Joe quindi seleziona Invia sul suo portafoglio smartphone e apre lo scanner del codice QR. Ciò permette a Joe di scansionare il codice a barre con la fotocamera del suo smartphone in modo da non dover digitare l'indirizzo Bitcoin di Alice, che è piuttosto lungo.

Joe ora ha l'indirizzo Bitcoin di Alice impostato come destinatario. Joe inserisce l'importo come 0,001 bitcoin (BTC); vedi [Schermata di invio del portafoglio Bitcoin.](#wallet-send). Alcuni portafogli potrebbero mostrare l'importo in una denominazione diversa: 0,001 BTC è 1 millibitcoin (mBTC) o 100.000 satoshi (sats).

Alcuni portafogli potrebbero anche suggerire a Joe di inserire un'etichetta per questa transazione; in tal caso, Joe inserisce "Alice". Settimane o mesi dopo, questo aiuterà Joe a ricordare perché ha inviato questi 0,001 bitcoin. Alcuni portafogli potrebbero anche chiedere a Joe informazioni sulle commissioni. A seconda del portafoglio e di come viene inviata la transazione, il portafoglio potrebbe chiedere a Joe di inserire un tasso di commissione di transazione o suggerirgli una commissione (o tasso di commissione). Più alta è la commissione di transazione, più velocemente la transazione verrà confermata (vedi [Conferme](#confirmations)).

[![[mbc3_0102.png|Schermata di invio del portafoglio. Immagine derivata da Bitcoin Design Guide CC-BY]]](https://github.com/bitcoinbook/bitcoinbook/blob/develop/images/mbc3_0102.png)

Figura 2. Schermata di invio del portafoglio Bitcoin.

Joe quindi controlla attentamente per assicurarsi di aver inserito l'importo corretto, perché sta per trasmettere denaro e gli errori diventeranno presto irreversibili. Dopo aver ricontrollato l'indirizzo e l'importo, preme Invia per trasmettere la transazione. Il portafoglio Bitcoin mobile di Joe costruisce una transazione che assegna 0,001 BTC all'indirizzo fornito da Alice, prelevando i fondi dal portafoglio di Joe e firmando la transazione con le chiavi private di Joe. Questo dice alla rete Bitcoin che Joe ha autorizzato un trasferimento di valore al nuovo indirizzo di Alice. Mentre la transazione viene trasmessa tramite il protocollo peer-to-peer, si propaga rapidamente attraverso la rete Bitcoin. Dopo pochi secondi, la maggior parte dei nodi ben connessi nella rete riceve la transazione e vede l'indirizzo di Alice per la prima volta.

Nel frattempo, il portafoglio di Alice è costantemente "in ascolto" per nuove transazioni sulla rete Bitcoin, cercando quelle che corrispondono agli indirizzi che contiene. Pochi secondi dopo che il portafoglio di Joe ha trasmesso la transazione, il portafoglio di Alice indicherà che sta ricevendo 0,001 BTC.

Conferme

All'inizio, l'indirizzo di Alice mostrerà la transazione da Joe come "Non confermata". Ciò significa che la transazione è stata propagata alla rete ma non è ancora stata registrata nel registro delle transazioni Bitcoin, noto come blockchain. Per essere confermata, una transazione deve essere inclusa in un blocco e aggiunta alla blockchain, cosa che avviene ogni 10 minuti, in media. In termini finanziari tradizionali questo è noto come *compensazione*. Per maggiori dettagli sulla propagazione, validazione e compensazione (conferma) delle transazioni bitcoin, vedi [\[mining\]](#mining).

Alice è ora la fiera proprietaria di 0,001 BTC che può spendere. Nei giorni successivi, Alice acquista più bitcoin usando un ATM e un exchange. Nel prossimo capitolo esamineremo il suo primo acquisto con Bitcoin e analizzeremo più in dettaglio la transazione sottostante e le tecnologie di propagazione.

---

[1](#_footnoteref_1). ["Bitcoin: A Peer-to-Peer Electronic Cash System"](https://oreil.ly/KUaBM), Satoshi Nakamoto.