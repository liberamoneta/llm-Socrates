esc---
title: "La blockchain più antica del mondo si nasconde in un giornale dal 1995"
source: "https://www.vice.com/it/article/blockchain-surety-new-york-times-1995-haber-stornetta/"
author:
  - "[[Daniel Oberhaus]]"
published: 2018-08-28
created: 2026-06-09
description: "È sempre stata lì sotto gli occhi di tutti nelle copie del New York Times dal 1995."
tags:
  - "clippings"
---
La prima volta che ho sentito nominare la blockchain è stato durante una festa: un mio amico ha passato tutta la serata a parlarmi di questa cosa chiamata Bitcoin spiegandomi tutti i buoni motivi per cui avrei dovuto acquistarne un po’. Credo che per molti il primo approccio con la blockchain sia stato simile a questo. Tuttavia, anche se possiamo attribuire a Bitcoin il merito di aver portato la blockchain — un registro digitale distribuito — all’attenzione del grande pubblico, non è il primo esempio di sistema che sfrutta le caratteristiche alla base di questa tecnologia così complessa.

In realtà, la blockchain più antica del mondo ha anticipato Bitcoin di 13 anni ed è sempre rimasta nascosta agli occhi dei più, stampata ogni settimana all’interno di uno dei giornali più diffusi al mondo: Il *New York Times*.

## La prima blockchain del mondo

Di base, una blockchain è solo un database mantenuto da una rete di utenti che viene protetto attraverso la crittografia. Quando vengono aggiunte nuove informazioni al database, queste vengono suddivise in ”blocchi” che contengono questi dati. Ogni tanto, viene creato un nuovo blocco connesso a una ”catena” di blocchi creati in precedenza. Ogni blocco possiede un ID univoco chiamato hash che viene creato sottoponendo a un algoritmo crittografico l’ID del blocco che lo ha preceduto e i dati memorizzati nel blocco corrente. Questo garantisce l’integrità di tutti i dati memorizzati sulla blockchain. Se i dati di un blocco venissero alterati, infatti, l’algoritmo di hash restituirebbe risultati differenti.

<iframe src="https://motherboard.vice.com/it/embed/article/xw7emq/fermiamo-la-blockchain-prima-che-privatizzi-le-nostre-gif?utm_source=stylizedembed_motherboard.vice.com&amp;utm_campaign=j5nzx4&amp;site=motherboard" frameborder="0" allowfullscreen=""></iframe>
Oggi, la parola ”blockchain” indica per estensione la tecnologia che si trova alla base della maggior parte delle cripto-valute e sistemi di valuta digitale, come [Bitcoin](https://motherboard.vice.com/en_us/topic/bitcoin) o [Ethereum](https://motherboard.vice.com/en_us/topic/ethereum). Anche se le blockchain vengono sfruttate come registro sicuro in cui memorizzare i dati delle transazioni finanziarie, possono essere utilizzate in molti altri modi. Infatti, qualsiasi tipo di informazione può essere memorizzata in una blockchain, dalla [mappatura del genoma delle varie qualità di marijuana](https://motherboard.vice.com/it/article/qk3qk3/mappatura-genoma-delle-varieta-di-marijuana-con-blockchain-di-bitcoin), ai [crypto-gattini](https://motherboard.vice.com/it/article/bj78jv/ho-allevato-dei-crypto-gattini-sulla-blockchain-di-ethereum), dal [sushi alle opere d’arte](https://motherboard.vice.com/it/article/3k4qkj/foto-surreali-di-unassurda-conferenza-per-ricchi-sulle-criptovalute), gli esempi di cosa è stato memorizzato su un registro distribuito sono moltissimi.

Le blockchain, in quanto semplice registro di dati crittografati aggiunti in ordine cronologico, sono state inventate per la prima volta dai crittografi Stuart Haber e Scott Stronetta nel 1991 per utilizzi molto meno ambiziosi. I due hanno infatti concepito la tecnologia come un modo per ottenere il timestamp (ovvero, la marcatura temporale, cioè l’associazione di data e ora certe e legalmente valide) di documenti digitali e verificarne l’autenticità. Come spiegato in un [articolo pubblicato su The Journal of Cryptology](https://www.anf.es/pdf/Haber_Stornetta.pdf), la capacità di certificare quando un documento è stato creato o modificato l’ultima volta è fondamentale per risolvere questioni come i diritti di proprietà intellettuale.

Nel mondo IRL, esistono diversi metodi per ottenere il timestamp di un documento, ad esempio, spedendolo attraverso una busta sigillata oppure prendendo nota della data della sua creazione in registri appositi. In questi casi, qualsiasi prova di manomissione — come l’apertura della busta o il tentativo di inserire una pagina nei registri ufficiali — risulta evidente. Ma quando si tratta di verificare l’autenticità di un documento digitale, è molto più difficile determinare se il documento è stato alterato.

Come hanno capito Haber e Stornetta, il timestamp di un documento digitale richiederebbe la soluzione di due problemi. In primo luogo, i dati stessi dovrebbero essere contrassegnati con l’ora ”in modo che sia impossibile modificare anche un solo bit del documento senza che la modifica sia evidente.” In secondo luogo, bisogna rendere impossibile la modifica del calendario stesso.

**Leggi Anche:** [Per favore, ridateci la blockchain di una volta](https://motherboard.vice.com/it/article/gywjmj/per-favore-ridateci-la-blockchain-di-una-volta)

La soluzione più semplice a questo problema consiste nell’inviare il documento digitale a un servizio di timestamping che lo conservi in una ”digital safety deposit box” che soddisfi entrambi i requisiti indicati sopra. L’aspetto negativo di questo approccio è che compromette la privacy della persona che invia il documento e non elimina la possibilità che il documento venga danneggiato quando viene inviato al servizio o memorizzato dallo stesso.

La soluzione a cui sono giunti Haber e Stornetta è stata invece quella di sottoporre il documento a un algoritmo di hashing crittografico, che produce un ID univoco per il documento. Se viene modificato anche un singolo bit del documento e questo viene sottoposto nuovamente all’algoritmo di hashing, l’ID che ne risulterà sarà completamente diverso. Questo concetto è stato abbinato all’idea connessa di firma digitale, che può essere utilizzata per identificare in modo univoco il firmatario. In questo modo, invece di inviare l’intero documento a un servizio di timestamping, gli utenti possono semplicemente inviare il valore di hash crittografico, che poteva essere a sua volta firmato dal servizio per assicurarsi che fosse stato ricevuto in un determinato momento e non fosse stato corrotto — praticamente la stessa funzione che svolgono i notai per i documenti IRL.

Ma dove entra in gioco il *New York Times*? Nelle criptovalute, gli hash sono inseriti in un registro pubblico noto come blockchain, in cui chiunque può constatare di persona che l’integrità dei dati è intatta. Haber e Stornetta avevano capito che i quotidiani più importanti della nazione potevano rivelarsi utili a questo scopo.

## Ispirare Satoshi

Nel loro paper del 1991, Haber e Stornetta hanno descritto un prototipo delle blockchain su cui fanno affidamento la maggior parte delle criptovalute attuali. A conferma di questo fatto, nel white paper del 2008 di Satoshi Nakamoto che descrive per la prima volta Bitcoin, tre degli otto articoli citati portano la firma di Haber e Stornetta. Alla domanda su come si sentiva ad avere ispirato Bitcoin, Stornetta ha dichiarato al *[Wall Street Journal](https://www.wsj.com/articles/the-eureka-moment-that-made-bitcoin-possible-1527268025)* che si sentiva ”piuttosto fico.”

Ma 14 anni prima dell’invenzione di Bitcoin, Haber e Stornetta hanno creato il loro servizio di timestamping [Surety](http://surety.com/) per tradurre in pratica la loro idea.

![Hashwerte von Surety, die in der New York Times abgedruckt wurden.](https://www.vice.com/wp-content/uploads/sites/2/2018/08/1535400878477-lost_and_found.jpeg)

Un esempio degli hash di Surety pubblicati sul New York Times nel 2009. Immagine: Surety

Il prodotto principale di Surety si chiama ”Absolute Proof,” e funziona come sigillo crittografico sicuro per i documenti digitali. Il suo meccanismo di base è lo stesso descritto nel documento originale di Haber e Stornetta. I clienti utilizzano AbsoluteProof per creare l’hash di un documento digitale, che viene poi inviato ai server di Surety dove viene eseguito il processo di timestamp. Questo sigillo è un identificativo univoco sicuro dal punto di vista crittografico che viene poi restituito al programma software per essere memorizzato per conto del cliente.

Allo stesso tempo, una copia di quel sigillo e di ogni altro sigillo creato dai clienti di Surety viene inviata al ”database duniversale” di AbsoluteProof — una ”hash-chain” composta interamente dai sigilli dei clienti Surety. Questo crea un record immutabile di tutti i sigilli Surety mai prodotti, in modo che sia impossibile per l’azienda o qualsiasi malintenzionato modificare un sigillo. Tuttavia, questo esclude una parte importante dell’equazione della blockchain: l’affidabilità. Come ci si può fidare della legittimità dei registri interni di Surety?

Invece di pubblicare gli hash dei clienti in un registro digitale pubblico, ogni settimana, Surety crea un valore hash unico di tutti i nuovi sigilli aggiunti al database e pubblica questo valore hash sul *New York Times*. L’hash è inserito in un piccolo annuncio nella sezione “Notices & Lost and Found” una volta alla settimana dal 1995.

Secondo l’azienda, ”questo rende impossibile per chiunque — Surety compresa — retrodatare i timestamp o convalidare record elettronici che non sono copie esatte dell’originale.” O nel peggiore dei casi, quasi impossibile.

[Come ha spiegato scherzando su Twitter](https://twitter.com/VitalikButerin/status/1034014732984967175) il cofondatore di Ethereum Vitalik Buterin, se qualcuno volesse compromettere la blockchain di Surety potrebbe ”creare dei quotidiani falsi con una diversa catena di hash e diffonderli più ampiamente” rispetto a quelli autentici. Dato che il *New York Times* ha una tiratura media giornaliera di circa [570.000 copie](https://d18rn0p25nwr6d.cloudfront.net/CIK-0000071691/37d516f5-b9da-4ca8-a50f-d70630760094.pdf), si tratterebbe probabilmente della truffa del secolo.

Sia Haber che Stornetta [hanno lasciato Surety più di dieci anni fa per tornare a occuparsi di ricerc](https://www.wsj.com/articles/the-eureka-moment-that-made-bitcoin-possible-1527268025) e oggi lavorano come crittografi su altri progetti basati sulla blockchain. In ogni caso, anche se non hanno mai fatto il botto nel nuovo selvaggio mondo delle criptovalute che hanno contribuito a creare, Haber e Stornetta possono vantarsi a pieno titolo nell’ambiente di aver pensato a un nuovo utilizzo dei quotidiani nazionali.

*Questo articolo è comparso originariamente su Motherboard US.*