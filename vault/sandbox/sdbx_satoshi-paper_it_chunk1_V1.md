---
stato: BOZZA
lingua: italiano
fonte: satoshi-paper_it_chunk1.md
data_ingest: 2026-06-13
---

```markdown
---
stato: BOZZA
lingua: italiano
fonte: satoshi-paper_it_chunk1.md
data_ingest: 2025-03-30
---

# 📌 SINTESI ESAUSTIVA

Il paper propone un sistema di contante elettronico puramente peer‑to‑peer che consente pagamenti online diretti tra due parti senza l’intermediazione di un’istituzione finanziaria. Le firme digitali offrono una soluzione parziale, ma il vero beneficio si perde se serve ancora una terza parte fidata per prevenire la double‑spending. La soluzione presentata impiega una rete peer‑to‑peer che marca temporalmente le transazioni inserendone l’hash in una catena ininterrotta di proof‑of‑work basata su hash, formando una registrazione immodificabile senza rifare l’intero proof‑of‑work. La catena più lunga non solo dimostra la sequenza degli eventi osservati, ma prova anche di provenire dal più grande insieme di potenza di calcolo. Finché la maggioranza della potenza di CPU è controllata da nodi onesti che non cooperano per attaccare la rete, essi genereranno la catena più lunga e supereranno qualsiasi attaccante. La rete richiede una struttura minima: i messaggi sono propagati in “best effort” e i nodi possono andare e venire liberamente, accettando la catena di proof‑of‑work più lunga come prova di ciò che è accaduto in loro assenza.

L’introduzione osserva che il commercio su internet è quasi totalmente dipendente da istituzioni finanziarie che operano come terze parti fidate per elaborare i pagamenti. Sebbene il sistema funzioni per la maggior parte delle transazioni, soffre di debolezze intrinseche del modello basato sulla fiducia. Transazioni completamente irreversibili non sono davvero possibili perché le istituzioni non possono evitare di mediare le dispute. Il costo della mediazione alza i costi di transazione, limita la dimensione minima delle transazioni e impedisce le piccole transazioni occasionali; si perde inoltre la capacità di effettuare pagamenti non reversibili per servizi non reversibili. La reversibilità diffonde la necessità di fiducia: i commercianti devono diffidare dei clienti, chiedendo più informazioni del necessario, e una certa percentuale di frode è accettata come inevitabile. Il contante fisico evita questi costi e incertezze, ma non esiste un meccanismo per pagare attraverso un canale di comunicazione senza una parte fidata. Serve un sistema di pagamento elettronico fondato su prove crittografiche anziché sulla fiducia, che permetta a due parti disponibili di transare direttamente. Transazioni che siano computazionalmente impraticabili da invertire proteggerebbero i venditori, e semplici meccanismi di escrow ordinari potrebbero salvaguardare gli acquirenti. Il paper propone una soluzione al double‑spending usando un server di timestamp distribuito peer‑to‑peer per generare una prova computazionale dell’ordine cronologico delle transazioni. Il sistema è sicuro se i nodi onesti controllano collettivamente più potenza di CPU di qualunque gruppo cooperante di nodi attaccanti.

Nella sezione sulle transazioni, una moneta elettronica è definita come una chain of digital signatures. Il proprietario trasferisce la moneta al successivo firmando digitalmente un hash della transazione precedente e la chiave pubblica del nuovo proprietario, aggiungendo questi elementi in coda. Il beneficiario può verificare le firme per controllare la catena di proprietà. Il problema è che il beneficiario non può verificare che uno dei precedenti proprietari non abbia già speso due volte la stessa moneta. Una soluzione comune introduce un’autorità centrale fidata, o zecca, che controlla ogni transazione per il double‑spending: dopo ogni transazione la moneta deve tornare alla zecca per emetterne una nuova, e solo le monete emesse direttamente dalla zecca sono considerate non spese due volte. Il difetto è che l’intero sistema monetario dipende dall’ente che gestisce la zecca, esattamente come una banca. Bisogna quindi trovare un modo perché il beneficiario sappia che i precedenti proprietari non hanno firmato transazioni antecedenti. Ai fini del sistema, la transazione più antica è quella che conta, perciò non interessano i tentativi successivi di double‑spending. L’unico modo per confermare l’assenza di una transazione è essere a conoscenza di tutte le transazioni. Nel modello basato sulla zecca, la zecca conosceva tutte le transazioni e decideva quale fosse arrivata per prima. Per ottenere lo stesso risultato senza una parte fidata, le transazioni devono essere annunciate pubblicamente e serve un sistema affinché i partecipanti concordino su un’unica storia dell’ordine con cui sono state ricevute. Il beneficiario ha bisogno della prova che al momento di ciascuna transazione la maggioranza dei nodi ha concordato che fosse la prima ricevuta.

Il timestamp server rappresenta il punto di partenza della soluzione. Esso funziona prendendo un hash di un blocco di elementi da datare e pubblicando ampiamente tale hash. Ogni timestamp include il timestamp precedente nel proprio hash, formando una catena in cui ogni timestamp aggiuntivo rafforza quelli che lo precedono.

> Il timestamp prova che i dati devono essere esistiti al momento, ovviamente, per poter entrare nell’hash.

Per realizzare un server di timestamp distribuito su base peer‑to‑peer si ricorre a un sistema di proof‑of‑work simile a Hashcash di Adam Back, invece di usare giornali o post Usenet. Il proof‑of‑work consiste nello scandire un valore tale che, una volta passato da SHA‑256, l’hash cominci con un certo numero di bit a zero. Il lavoro medio richiesto è esponenziale nel numero di bit zero imposti e può essere verificato con un singolo hash.

> Per la nostra rete di timestamp, implementiamo il proof‑of‑work incrementando un nonce nel blocco fino a trovare un valore che dia all’hash del blocco i bit zero richiesti.

Una volta speso lo sforzo di CPU, il blocco non può più essere modificato senza rifare il lavoro. Con l’aggiunta di blocchi successivi, modificare un blocco passato richiederebbe rifare il proof‑of‑work di quel blocco e di tutti i successivi. Il proof‑of‑work risolve anche il problema della rappresentanza nelle decisioni a maggioranza. Se la maggioranza fosse basata su un voto per indirizzo IP, potrebbe essere sovvertita da chiunque possa allocare molti IP. Il proof‑of‑work è essenzialmente un voto per CPU: la decisione maggioritaria è rappresentata dalla catena più lunga, che ha il maggior sforzo di proof‑of‑work investito. Se la maggioranza della potenza di CPU è in mano a nodi onesti, la catena onesta crescerà più velocemente e supererà qualsiasi catena concorrente. Per modificare un blocco passato, un attaccante dovrebbe rifare il proof‑of‑work del blocco e di tutti i successivi, e poi raggiungere e superare il lavoro dei nodi onesti; la probabilità che un attaccante più lento recuperi diminuisce esponenzialmente all’aumentare dei blocchi aggiunti. Per compensare l’aumento della velocità hardware e l’interesse variabile nell’eseguire nodi nel tempo, la difficoltà del proof‑of‑work è determinata da una media mobile che mira a un numero medio di blocchi all’ora: se vengono generati troppo velocemente, la difficoltà sale.

La rete opera secondo un insieme di passi:

1. Le nuove transazioni vengono trasmesse a tutti i nodi.
2. Ogni nodo raccoglie le nuove transazioni in un blocco.
3. … (il testo si interrompe)

Proseguendo, il paper descrive l’incentivo. Le monete sono paragonate ai minatori d’oro che spendono risorse per aggiungere oro in circolazione; nel caso di Bitcoin, si impiegano tempo di CPU ed elettricità. L’incentivo può anche essere finanziato tramite commissioni di transazione: se il valore in uscita di una transazione è inferiore al valore in entrata, la differenza costituisce una commissione che si aggiunge all’incentivo del blocco contenente la transazione. Quando un numero predeterminato di monete sarà entrato in circolazione, l’incentivo potrà basarsi interamente sulle commissioni e il sistema potrà essere del tutto privo di inflazione. L’incentivo aiuta anche a incoraggiare i nodi a rimanere onesti: se un attaccante avido riuscisse a raccogliere più potenza di CPU di tutti i nodi onesti messi insieme, dovrebbe scegliere se usarla per frodare la gente invertendo i propri pagamenti o per generare nuove monete. Troverebbe più redditizio giocare secondo le regole, regole che lo favoriscono con più nuove monete di chiunque altro, piuttosto che minare il sistema e la validità della propria ricchezza.

Infine, per quanto riguarda il recupero dello spazio su disco, una volta che l’ultima transazione di una moneta è sepolta sotto un numero sufficiente di blocchi, le transazioni spese precedenti possono essere scartate per risparmiare spazio. Per fare ciò senza rompere l’hash del blocco, le transazioni sono hashatte in un Merkle Tree, e solo la radice viene inclusa nell’hash del blocco. I blocchi vecchi possono quindi essere compattati... (il testo si interrompe).

---

## 🗨️ DISCUSSIONE SOCRATICA

(Lascia vuoto)

---

## ✅ IL MIO SAPERE

(Lascia vuoto)
```
