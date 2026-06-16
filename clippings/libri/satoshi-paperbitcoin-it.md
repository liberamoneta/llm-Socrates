---
title: "satoshi-paper/bitcoin.md at master"
source: "https://github.com/karask/satoshi-paper/blob/master/bitcoin.md"
author:
published:
created: 2026-06-14
description: "Articolo originale di Satoshi in vari formati. Contribuisci allo sviluppo di karask/satoshi-paper creando un account su GitHub."
tags:
  - "clippings"
---
## Bitcoin: Un Sistema di Contante Elettronico Peer-to-Peer

: Satoshi Nakamoto

email

: [satoshin@gmx.com](mailto:satoshin@gmx.com)

sito

: [http://www.bitcoin.org/](http://www.bitcoin.org/)

**Abstract.** Una versione puramente peer-to-peer di contante elettronico consentirebbe di inviare pagamenti online direttamente da una parte all'altra senza passare attraverso un'istituzione finanziaria. Le firme digitali forniscono parte della soluzione, ma i principali vantaggi vengono persi se è ancora necessario un terzo fidato per prevenire la doppia spesa. Proponiamo una soluzione al problema della doppia spesa utilizzando una rete peer-to-peer. La rete timestampa le transazioni inserendole in hash in una catena continua di proof-of-work basato su hash, formando una registrazione che non può essere modificata senza rifare il proof-of-work. La catena più lunga non solo serve come prova della sequenza di eventi osservati, ma anche come prova che proviene dal pool più grande di potenza di calcolo. Finché la maggioranza della potenza di calcolo è controllata da nodi che non cooperano per attaccare la rete, essi genereranno la catena più lunga e supereranno gli aggressori. La rete stessa richiede una struttura minima. I messaggi vengono trasmessi al meglio, e i nodi possono lasciare e rientrare nella rete a piacimento, accettando la catena di proof-of-work più lunga come prova di ciò che è accaduto durante la loro assenza.

## Introduzione

Il commercio su Internet si è basato quasi esclusivamente su istituzioni finanziarie che fungono da terze parti fidate per elaborare i pagamenti elettronici. Sebbene il sistema funzioni abbastanza bene per la maggior parte delle transazioni, soffre ancora delle debolezze intrinseche del modello basato sulla fiducia. Le transazioni completamente irreversibili non sono realmente possibili, poiché le istituzioni finanziarie non possono evitare di mediare le controversie. Il costo della mediazione aumenta i costi di transazione, limitando la dimensione minima pratica della transazione e tagliando fuori la possibilità di piccole transazioni casuali, e c'è un costo più ampio nella perdita della capacità di effettuare pagamenti irreversibili per servizi non reversibili. Con la possibilità di inversione, la necessità di fiducia si diffonde. I commercianti devono diffidare dei loro clienti, chiedendo loro più informazioni di quanto altrimenti necessario. Una certa percentuale di frode è accettata come inevitabile. Questi costi e incertezze di pagamento possono essere evitati di persona utilizzando valuta fisica, ma non esiste alcun meccanismo per effettuare pagamenti attraverso un canale di comunicazione senza una parte fidata.

Ciò che serve è un sistema di pagamento elettronico basato su prove crittografiche invece che sulla fiducia, che permetta a due parti disposte di transare direttamente tra loro senza la necessità di una terza parte fidata. Le transazioni che sono computazionalmente impraticabili da invertire proteggerebbero i venditori dalle frodi, e meccanismi di deposito a garanzia di routine potrebbero essere facilmente implementati per proteggere gli acquirenti. In questo articolo, proponiamo una soluzione al problema della doppia spesa utilizzando un server di timestamp distribuito peer-to-peer per generare una prova computazionale dell'ordine cronologico delle transazioni. Il sistema è sicuro finché i nodi onesti controllano collettivamente più potenza di calcolo di qualsiasi gruppo cooperante di nodi aggressori.

## Transazioni

Definiamo una moneta elettronica come una catena di firme digitali. Ogni proprietario trasferisce la moneta al successivo firmando digitalmente un hash della transazione precedente e la chiave pubblica del prossimo proprietario, aggiungendoli alla fine della moneta. Un beneficiario può verificare le firme per verificare la catena di proprietà.

![transactions.png](asset/transactions.png)

Il problema, ovviamente, è che il beneficiario non può verificare che uno dei proprietari non abbia speso due volte la moneta. Una soluzione comune è introdurre un'autorità centrale fidata, o zecca, che controlli ogni transazione per la doppia spesa. Dopo ogni transazione, la moneta deve essere restituita alla zecca per emettere una nuova moneta, e solo le monete emesse direttamente dalla zecca sono considerate non spese due volte. Il problema di questa soluzione è che il destino dell'intero sistema monetario dipende dall'azienda che gestisce la zecca, con ogni transazione che deve passare attraverso di essa, proprio come una banca.

Abbiamo bisogno di un modo per il beneficiario di sapere che i precedenti proprietari non hanno firmato transazioni precedenti. Ai nostri fini, la transazione più antica è quella che conta, quindi non ci interessano i successivi tentativi di doppia spesa. L'unico modo per confermare l'assenza di una transazione è essere a conoscenza di tutte le transazioni. Nel modello basato sulla zecca, la zecca era a conoscenza di tutte le transazioni e decideva quale arrivava per prima. Per ottenere questo senza una parte fidata, le transazioni devono essere annunciate pubblicamente [^1], e abbiamo bisogno di un sistema in cui i partecipanti concordino su una singola storia dell'ordine in cui sono state ricevute. Il beneficiario ha bisogno della prova che, al momento di ogni transazione, la maggioranza dei nodi abbia concordato che fosse la prima ricevuta.

## Server di Timestamp

La soluzione che proponiamo inizia con un server di timestamp. Un server di timestamp funziona prendendo un hash di un blocco di elementi da timestampare e pubblicando ampiamente l'hash, ad esempio in un giornale o in un post Usenet [^2] [^3] [^4] [^5]. Il timestamp prova che i dati devono essere esistiti al momento, ovviamente, per poter entrare nell'hash. Ogni timestamp include il timestamp precedente nel suo hash, formando una catena, con ogni timestamp aggiuntivo che rafforza quelli precedenti.

![timestamp.png](asset/timestamp.png)

## Proof-of-Work

Per implementare un server di timestamp distribuito su base peer-to-peer, dovremo utilizzare un sistema di proof-of-work simile a Hashcash di Adam Back [^6], piuttosto che articoli di giornale o post Usenet. Il proof-of-work implica la scansione di un valore che, quando sottoposto a hash, ad esempio con SHA-256, l'hash inizi con un certo numero di bit zero. Il lavoro medio richiesto è esponenziale nel numero di bit zero richiesti e può essere verificato eseguendo un singolo hash.

Per la nostra rete di timestamp, implementiamo il proof-of-work incrementando un nonce nel blocco finché non viene trovato un valore che dia all'hash del blocco i bit zero richiesti. Una volta che lo sforzo della CPU è stato speso per soddisfare il proof-of-work, il blocco non può essere modificato senza rifare il lavoro. Poiché i blocchi successivi sono concatenati dopo di esso, il lavoro per modificare il blocco includerebbe il rifacimento di tutti i blocchi successivi.

![proof-of-work.png](asset/proof-of-work.png)

Il proof-of-work risolve anche il problema di determinare la rappresentanza nel processo decisionale a maggioranza. Se la maggioranza fosse basata su un voto per indirizzo IP, potrebbe essere sovvertita da chiunque sia in grado di allocare molti IP. Il proof-of-work è essenzialmente un voto per CPU. La decisione a maggioranza è rappresentata dalla catena più lunga, che ha il maggior sforzo di proof-of-work investito. Se una maggioranza della potenza di calcolo è controllata da nodi onesti, la catena onesta crescerà più velocemente e supererà qualsiasi catena concorrente. Per modificare un blocco passato, un aggressore dovrebbe rifare il proof-of-work del blocco e di tutti i blocchi successivi, e poi raggiungere e superare il lavoro dei nodi onesti. Mostreremo in seguito che la probabilità che un aggressore più lento recuperi il ritardo diminuisce esponenzialmente man mano che vengono aggiunti blocchi successivi.

Per compensare l'aumento della velocità hardware e il variare dell'interesse nell'esecuzione di nodi nel tempo, la difficoltà del proof-of-work è determinata da una media mobile che mira a un numero medio di blocchi all'ora. Se vengono generati troppo velocemente, la difficoltà aumenta.

## Rete

I passaggi per eseguire la rete sono i seguenti:

1. Le nuove transazioni vengono trasmesse a tutti i nodi.
2. Ogni nodo raccoglie le nuove transazioni in un blocco.
3. Ogni nodo lavora per trovare un proof-of-work difficile per il suo blocco.
4. Quando un nodo trova un proof-of-work, trasmette il blocco a tutti i nodi.
5. I nodi accettano il blocco solo se tutte le transazioni in esso contenute sono valide e non già spese.
6. I nodi esprimono la loro accettazione del blocco lavorando per creare il blocco successivo nella catena, utilizzando l'hash del blocco accettato come hash precedente.

I nodi considerano sempre la catena più lunga come quella corretta e continueranno a lavorare per estenderla. Se due nodi trasmettono versioni diverse del blocco successivo contemporaneamente, alcuni nodi potrebbero ricevere l'una o l'altra per prima. In tal caso, lavorano sulla prima che hanno ricevuto, ma salvano l'altro ramo nel caso diventi più lungo. L'impasse verrà risolta quando verrà trovato il prossimo proof-of-work e un ramo diventerà più lungo; i nodi che stavano lavorando sull'altro ramo passeranno quindi a quello più lungo.

Le trasmissioni di nuove transazioni non devono necessariamente raggiungere tutti i nodi. Finché raggiungono molti nodi, entreranno in un blocco prima o poi. Le trasmissioni di blocchi sono anche tolleranti ai messaggi persi. Se un nodo non riceve un blocco, lo richiederà quando riceve il blocco successivo e si accorge di averne perso uno.

## Incentivo

Per convenzione, la prima transazione in un blocco è una transazione speciale che crea una nuova moneta di proprietà del creatore del blocco. Questo aggiunge un incentivo per i nodi a supportare la rete e fornisce un modo per distribuire inizialmente le monete in circolazione, poiché non esiste un'autorità centrale per emetterle. L'aggiunta costante di una quantità costante di nuove monete è analoga ai minatori d'oro che spendono risorse per aggiungere oro alla circolazione. Nel nostro caso, sono il tempo della CPU e l'elettricità ad essere spesi.

L'incentivo può anche essere finanziato con le commissioni di transazione. Se il valore di output di una transazione è inferiore al suo valore di input, la differenza è una commissione di transazione che viene aggiunta al valore dell'incentivo del blocco contenente la transazione. Una volta che un numero predeterminato di monete è entrato in circolazione, l'incentivo può passare interamente alle commissioni di transazione ed essere completamente privo di inflazione.

L'incentivo può aiutare a incoraggiare i nodi a rimanere onesti. Se un aggressore avido è in grado di assemblare più potenza di calcolo di tutti i nodi onesti, dovrebbe scegliere tra usarla per frodare le persone rubando i propri pagamenti, o usarla per generare nuove monete. Dovrebbe trovare più redditizio giocare secondo le regole, regole che lo favoriscono con più nuove monete di tutti gli altri messi insieme, piuttosto che minare il sistema e la validità della propria ricchezza.

## Recupero dello Spazio su Disco

Una volta che l'ultima transazione in una moneta è sepolta sotto un numero sufficiente di blocchi, le transazioni spese precedenti possono essere scartate per risparmiare spazio su disco. Per facilitare questo senza rompere l'hash del blocco, le transazioni sono sottoposte a hash in un Albero di Merkle [^7] [^8] [^9], con solo la radice inclusa nell'hash del blocco. I vecchi blocchi possono quindi essere compattati tagliando i rami dell'albero. Gli hash interni non devono essere memorizzati.

![reclaiming-disk.png](asset/reclaiming-disk.png)

Un'intestazione di blocco senza transazioni sarebbe di circa 80 byte. Se supponiamo che i blocchi vengano generati ogni 10 minuti, 80 byte \* 6 \* 24 \* 365 = 4,2 MB all'anno. Con i sistemi informatici che tipicamente vendono con 2 GB di RAM a partire dal 2008, e la Legge di Moore che prevede una crescita attuale di 1,2 GB all'anno, l'archiviazione non dovrebbe essere un problema anche se le intestazioni dei blocchi devono essere mantenute in memoria.

## Verifica Semplificata dei Pagamenti

È possibile verificare i pagamenti senza eseguire un nodo di rete completo. Un utente deve solo conservare una copia delle intestazioni dei blocchi della catena di proof-of-work più lunga, che può ottenere interrogando i nodi della rete finché non è convinto di avere la catena più lunga, e ottenere il ramo Merkle che collega la transazione al blocco in cui è timestampata. Non può controllare la transazione da solo, ma collegandola a un punto della catena, può vedere che un nodo di rete l'ha accettata, e i blocchi aggiunti dopo confermano ulteriormente che la rete l'ha accettata.

![spv.png](asset/spv.png)

Pertanto, la verifica è affidabile finché i nodi onesti controllano la rete, ma è più vulnerabile se la rete è sopraffatta da un aggressore. Mentre i nodi di rete possono verificare le transazioni da soli, il metodo semplificato può essere ingannato dalle transazioni fabbricate da un aggressore finché l'aggressore può continuare a sopraffare la rete. Una strategia per proteggersi da questo sarebbe quella di accettare avvisi dai nodi di rete quando rilevano un blocco non valido, spingendo il software dell'utente a scaricare il blocco completo e le transazioni segnalate per confermare l'incoerenza. Le aziende che ricevono pagamenti frequenti probabilmente vorranno comunque eseguire i propri nodi per una sicurezza più indipendente e una verifica più rapida.

## Combinazione e Divisione del Valore

Sebbene sarebbe possibile gestire le monete individualmente, sarebbe scomodo fare una transazione separata per ogni centesimo in un trasferimento. Per consentire la divisione e la combinazione del valore, le transazioni contengono più input e output. Normalmente ci sarà un singolo input da una transazione precedente più grande o più input che combinano importi minori, e al massimo due output: uno per il pagamento e uno per restituire il resto, se presente, al mittente.

![combining-splitting.png](asset/combining-splitting.png)

Va notato che il fan-out, dove una transazione dipende da diverse transazioni, e quelle transazioni dipendono da molte altre, non è un problema qui. Non c'è mai la necessità di estrarre una copia completa e indipendente della storia di una transazione.

## Privacy

Il modello bancario tradizionale raggiunge un livello di privacy limitando l'accesso alle informazioni alle parti coinvolte e al terzo fidato. La necessità di annunciare tutte le transazioni pubblicamente preclude questo metodo, ma la privacy può ancora essere mantenuta interrompendo il flusso di informazioni in un altro punto: mantenendo anonime le chiavi pubbliche. Il pubblico può vedere che qualcuno sta inviando un importo a qualcun altro, ma senza informazioni che colleghino la transazione a nessuno. Questo è simile al livello di informazioni rilasciate dalle borse valori, dove l'ora e la dimensione delle singole operazioni, il "nastro", sono resi pubblici, ma senza dire chi fossero le parti.

![privacy.png](asset/privacy.png)

Come firewall aggiuntivo, dovrebbe essere utilizzata una nuova coppia di chiavi per ogni transazione per evitare che siano collegate a un proprietario comune. Alcuni collegamenti sono ancora inevitabili con transazioni multi-input, che rivelano necessariamente che i loro input erano di proprietà dello stesso proprietario. Il rischio è che se il proprietario di una chiave viene rivelato, il collegamento potrebbe rivelare altre transazioni appartenenti allo stesso proprietario.

## Calcoli

Consideriamo lo scenario di un aggressore che cerca di generare una catena alternativa più velocemente della catena onesta. Anche se questo viene realizzato, non apre il sistema a modifiche arbitrarie, come creare valore dal nulla o prendere denaro che non è mai appartenuto all'aggressore. I nodi non accetteranno una transazione non valida come pagamento, e i nodi onesti non accetteranno mai un blocco che le contiene. Un aggressore può solo cercare di modificare una delle proprie transazioni per riprendersi il denaro che ha recentemente speso.

La gara tra la catena onesta e una catena aggressore può essere caratterizzata come una Passeggiata Casuale Binomiale. L'evento di successo è la catena onesta che viene estesa di un blocco, aumentando il suo vantaggio di +1, e l'evento di fallimento è la catena dell'aggressore che viene estesa di un blocco, riducendo il divario di -1.

La probabilità che un aggressore recuperi da un dato deficit è analoga a un problema di Rovina del Giocatore. Supponiamo che un giocatore con credito illimitato inizi in deficit e giochi potenzialmente un numero infinito di prove per cercare di raggiungere il pareggio. Possiamo calcolare la probabilità che raggiunga mai il pareggio, o che un aggressore recuperi mai la catena onesta, come segue [^10]:

| p = probabilità che un nodo onesto trovi il prossimo blocco | q = probabilità che l'aggressore trovi il prossimo blocco | qz = probabilità che l'aggressore recuperi mai da z blocchi di ritardo

$$
q
          z
        
        =
        
          {
          
            
              
                1
              
              
                se 
                p
                ⩽
                q
              
            
            
              
                
                  
                    (
                    q
                    
                      /
                    
                    p
                    )
                  
                  z
                
              
              
                se 
                p
                >
                q
$$

Data la nostra ipotesi che p > q, la probabilità diminuisce esponenzialmente all'aumentare del numero di blocchi che l'aggressore deve recuperare. Con le probabilità contrarie, se non fa un fortunato balzo in avanti all'inizio, le sue possibilità diventano trascurabili man mano che resta indietro.

Consideriamo ora quanto tempo il destinatario di una nuova transazione deve attendere prima di essere sufficientemente certo che il mittente non possa modificare la transazione. Supponiamo che il mittente sia un aggressore che vuole far credere al destinatario di averlo pagato per un po', per poi cambiarlo e ripagarsi dopo che è passato del tempo. Il ricevente verrà avvisato quando ciò accade, ma il mittente spera che sia troppo tardi.

Il ricevente genera una nuova coppia di chiavi e fornisce la chiave pubblica al mittente poco prima della firma. Questo impedisce al mittente di preparare in anticipo una catena di blocchi lavorandoci continuamente finché non è abbastanza fortunato da andare abbastanza avanti, per poi eseguire la transazione in quel momento. Una volta inviata la transazione, il mittente disonesto inizia a lavorare in segreto su una catena parallela contenente una versione alternativa della sua transazione.

Il destinatario attende fino a quando la transazione non è stata aggiunta a un blocco e z blocchi sono stati collegati dopo di essa. Non conosce l'esatto progresso dell'aggressore, ma supponendo che i blocchi onesti abbiano impiegato il tempo medio previsto per blocco, il potenziale progresso dell'aggressore sarà una distribuzione di Poisson con valore atteso:

$$
λ
  =
  z
  
    q
    p
$$

Per ottenere la probabilità che l'aggressore possa ancora recuperare ora, moltiplichiamo la densità di Poisson per ogni quantità di progresso che potrebbe aver fatto per la probabilità che possa recuperare da quel punto:

$$
∑
          
            k
            =
            0
          
          ∞
        
        
          
            
              λ
              k
            
            
              e
              
                −
                λ
              
            
          
          
            k
            !
          
        
        ⋅
        
          {
          
            
              
                
                  
                    (
                    q
                    
                      /
                    
                    p
                    )
                  
                  
                    (
                    z
                    −
                    p
                    )
                  
                
              
              
                se 
                k
                ⩽
                z
              
            
            
              
                1
              
              
                se 
                k
                >
                z
$$

Riorganizzando per evitare di sommare la coda infinita della distribuzione...

$$
1
  −
  
    ∑
    
      k
      =
      0
    
    z
  
  
    
      
        λ
        k
      
      
        e
        
          −
          λ
        
      
    
    
      k
      !
    
  
  
    (
    1
    −
    
      
        (
        q
        
          /
        
        p
        )
      
      
        (
        z
        −
        k
        )
      
    
    )
$$

Convertendo in codice C...

```
#include <math.h>
double AttackerSuccessProbability(double q, int z)
{
    double p = 1.0 - q;
    double lambda = z * (q / p);
    double sum = 1.0;
    int i, k;
    for (k = 0; k <= z; k++)
    {
        double poisson = exp(-lambda);
        for (i = 1; i <= k; i++)
            poisson *= lambda / i;
        sum -= poisson * (1 - pow(q / p, z - k));
    }
    return sum;
}
```

Eseguendo alcuni risultati, possiamo vedere la probabilità diminuire esponenzialmente con z.

```
q=0.1
z=0 P=1.0000000
z=1 P=0.2045873
z=2 P=0.0509779
z=3 P=0.0131722
z=4 P=0.0034552
z=5 P=0.0009137
z=6 P=0.0002428
z=7 P=0.0000647
z=8 P=0.0000173
z=9 P=0.0000046
z=10 P=0.0000012

q=0.3
z=0 P=1.0000000
z=5 P=0.1773523
z=10 P=0.0416605
z=15 P=0.0101008
z=20 P=0.0024804
z=25 P=0.0006132
z=30 P=0.0001522
z=35 P=0.0000379
z=40 P=0.0000095
z=45 P=0.0000024
z=50 P=0.0000006
```

Risolvendo per P inferiore allo 0,1%...

```
P \< 0.001
q=0.10 z=5
q=0.15 z=8
q=0.20 z=11
q=0.25 z=15
q=0.30 z=24
q=0.35 z=41
q=0.40 z=89
q=0.45 z=340
```

## Conclusione

Abbiamo proposto un sistema per transazioni elettroniche senza fare affidamento sulla fiducia. Abbiamo iniziato con il consueto quadro di monete realizzate con firme digitali, che fornisce un forte controllo della proprietà, ma è incompleto senza un modo per prevenire la doppia spesa. Per risolvere questo, abbiamo proposto una rete peer-to-peer che utilizza il proof-of-work per registrare una storia pubblica delle transazioni che diventa rapidamente computazionalmente impraticabile da modificare per un aggressore se i nodi onesti controllano la maggioranza della potenza di calcolo. La rete è robusta nella sua semplicità non strutturata. I nodi lavorano tutti contemporaneamente con poca coordinazione. Non hanno bisogno di essere identificati, poiché i messaggi non vengono instradati verso un luogo particolare e devono solo essere consegnati al meglio. I nodi possono lasciare e rientrare nella rete a piacimento, accettando la catena di proof-of-work come prova di ciò che è accaduto durante la loro assenza. Votano con la loro potenza di calcolo, esprimendo la loro accettazione dei blocchi validi lavorando per estenderli e rifiutando i blocchi non validi rifiutandosi di lavorarci sopra. Qualsiasi regola e incentivo necessario può essere applicato con questo meccanismo di consenso.

[^1]: W. Dai, "b-money," [http://www.weidai.com/bmoney.txt](http://www.weidai.com/bmoney.txt), 1998.

[^2]: H. Massias, X.S. Avila, e J.-J. Quisquater, "Design of a secure timestamping service with minimal trust requirements," In 20th Symposium on Information Theory in the Benelux, Maggio 1999.

[^3]: S. Haber, W.S. Stornetta, "How to time-stamp a digital document," In Journal of Cryptology, vol 3, n. 2, pagine 99-111, 1991.

[^4]: D. Bayer, S. Haber, W.S. Stornetta, "Improving the efficiency and reliability of digital time-stamping," In Sequences II: Methods in Communication, Security and Computer Science, pagine 329-334, 1993.

[^5]: S. Haber, W.S. Stornetta, "Secure names for bit-strings," In Proceedings of the 4th ACM Conference on Computer and Communications Security, pagine 28-35, Aprile 1997.

[^6]: A. Back, "Hashcash - a denial of service counter-measure," [http://www.hashcash.org/papers/hashcash.pdf](http://www.hashcash.org/papers/hashcash.pdf), 2002.

[^7]: R.C. Merkle, "Protocols for public key cryptosystems," In Proc. 1980 Symposium on Security and Privacy, IEEE Computer Society, pagine 122-133, Aprile 1980.

[^8]: H. Massias, X.S. Avila, e J.-J. Quisquater, "Design of a secure timestamping service with minimal trust requirements," In 20th Symposium on Information Theory in the Benelux, Maggio 1999.

[^9]: S. Haber, W.S. Stornetta, "Secure names for bit-strings," In Proceedings of the 4th ACM Conference on Computer and Communications Security, pagine 28-35, Aprile 1997.

[^10]: W. Feller, "An introduction to probability theory and its applications," 1957.