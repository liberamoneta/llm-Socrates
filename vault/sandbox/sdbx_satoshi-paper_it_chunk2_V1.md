---
stato: BOZZA
lingua: italiano
fonte: satoshi-paper_it_chunk2.md
data_ingest: 2026-06-13
---

# 📌 SINTESI ESAUSTIVA

Una volta che l’ultima transazione che spende un output è sepolta sotto un numero sufficiente di blocchi, le transazioni precedenti possono essere scartate per risparmiare spazio su disco. Per facilitare questa operazione senza rompere l’hash del blocco, le transazioni vengono inserite in un Merkle tree e solo la radice dell’albero viene inclusa nell’intestazione del blocco. I blocchi vecchi possono quindi essere compressi eliminando i rami interni dell’albero, conservando solo le intestazioni di blocco e la radice di Merkle. Un’intestazione senza transazioni occupa circa 80 byte; con un blocco ogni 10 minuti, la crescita annua è di circa 4,2 MB (80 byte × 6 × 24 × 365). Con i sistemi del 2008 dotati tipicamente di 2 GB di RAM e la legge di Moore che prevedeva una crescita di circa 1,2 GB/anno, la conservazione delle intestazioni in memoria non rappresentava un problema.

È possibile verificare i pagamenti senza gestire un nodo completo: un utente deve soltanto possedere una copia delle intestazioni dei blocchi della catena con la proof-of-work più lunga (ottenuta interrogando i nodi della rete) e il ramo di Merkle che collega la transazione al blocco in cui è stata timestampata. L’utente non può verificare la transazione in autonomia, ma può constatare che un nodo della rete l’ha accettata e che i blocchi successivi ne confermano l’accettazione. Questa verifica semplificata è affidabile finché la maggioranza della potenza di calcolo è onesta, ma diventa vulnerabile se la rete è sopraffatta da un attaccante. Per mitigare il rischio, i nodi possono inviare avvisi quando rilevano un blocco non valido, spingendo il software a scaricare l’intero blocco per verificare l’inconsistenza. Le aziende che ricevono pagamenti frequenti probabilmente gestiranno comunque un proprio nodo per sicurezza e verifica più rapida.

Per evitare la scomodità di gestire singole unità di moneta, le transazioni ammettono più input e output. Tipicamente si ha un singolo input derivante da una transazione precedente più grande, oppure più input che aggregano importi minori; al massimo due output: uno per il pagamento e uno per restituire il resto al mittente. Il fan‑out, cioè una transazione che dipende da molte transazioni precedenti e queste da altre ancora, non è un problema perché non occorre mai estrarre una copia completa della storia di una transazione.

Nel sistema bancario tradizionale la privacy è garantita limitando l’accesso alle informazioni alle parti coinvolte e a un terzo di fiducia. L’obbligo di annunciare pubblicamente tutte le transazioni impedisce questo approccio, ma la privacy può essere preservata interrompendo il flusso informativo in un altro punto: mantenendo anonime le chiavi pubbliche. Il pubblico vede che qualcuno invia un importo a qualcun altro, ma non ha informazioni che colleghino la transazione a una persona fisica. Questo è simile al nastro delle borse valori, dove ora e dimensione delle operazioni sono pubbliche ma le controparti restano ignote. Come ulteriore protezione, per ogni transazione occorrerebbe usare una nuova coppia di chiavi, evitando che transazioni diverse vengano ricondotte a uno stesso proprietario. Tuttavia, le transazioni con più input rivelano necessariamente che gli input appartenevano allo stesso proprietario; se l’identità di una chiave venisse svelata, si potrebbero collegare altre transazioni della stessa persona.

La sezione dei calcoli modella la competizione tra la catena onesta e una catena alternativa costruita da un attaccante come un Random Walk Binomiale. Sia p la probabilità che il prossimo blocco venga trovato da un nodo onesto, e q quella dell’attaccante. La probabilità che l’attaccante riesca a raggiungere la catena onesta partendo da uno svantaggio di z blocchi è data da:

\[
q_z = \begin{cases} 
\left(\dfrac{q}{p}\right)^z & \text{se } p > q \\
1 & \text{se } q > p 
\end{cases}
\]

Con l’ipotesi p > q, la probabilità di recupero cala esponenzialmente all’aumentare del distacco. Le tabelle riportate nel paper mostrano, ad esempio, che con q=0.10 (attacker 10% della potenza) dopo 5 blocchi la probabilità di raggiungere la catena onesta è circa 0.0000012; per q=0.20 occorrono 11 blocchi per scendere sotto lo 0.1%, mentre con q=0.45 servono 340 blocchi.

Il destinatario di una nuova transazione può quindi valutare dopo quanti blocchi sia ragionevole considerare la transazione irreversibile. Per impedire al mittente di preparare in anticipo una catena parallela prima di effettuare il pagamento, il destinatario genera una nuova coppia di chiavi e fornisce la chiave pubblica al mittente subito prima della firma. Dopo l’invio della transazione, il mittente disonesto lavora in segreto su una catena parallela contenente una versione alternativa della propria transazione. Le probabilità calcolate mostrano che, con p > q, il vantaggio della catena onesta cresce nel tempo.

La conclusione ribadisce che il sistema proposto consente transazioni elettroniche senza fiducia in un terzo. Partendo dallo schema delle monete basate su firme digitali, che fornisce un forte controllo della proprietà ma non impedisce il double-spending, si è introdotta una rete peer-to-peer che usa la proof-of-work per registrare una storia pubblica delle transazioni. Modificare tale storia diventa computazionalmente impraticabile se i nodi onesti controllano la maggioranza della potenza di calcolo. La rete è robusta nella sua semplicità non strutturata: i nodi lavorano con poca coordinazione, non devono essere identificati (i messaggi non sono instradati a destinatari specifici e vengono consegnati con il miglior sforzo), possono entrare e uscire a piacimento accettando la catena di proof-of-work come prova di ciò che è accaduto in loro assenza. I nodi votano con la loro potenza di calcolo, estendendo i blocchi validi e rifiutando quelli non validi, facendo rispettare tutte le regole e gli incentivi necessari.

---

## 🗨️ DISCUSSIONE SOCRATICA

---

## ✅ IL MIO SAPERE
