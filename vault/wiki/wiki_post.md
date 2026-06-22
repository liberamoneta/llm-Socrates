---
titolo: wiki_post
dominio: Bitcoin
tipo: post
stato: attivo
data_promozione: 2026-06-22
cicli_spb: 2
fonti: [[Post_Telegram.md]]
---

# 📌 SINTESI ESAUSTIVA

Sembra un paradosso, ma è il punto che pochi capiscono: Bitcoin è nato per togliere il potere alle banche e ai governi di decidere per te, creando un sistema dove tu controlli i tuoi soldi. Tuttavia, la maggior parte delle persone non vuole questo controllo. Preferisce delegare la custodia a un exchange, che di fatto opera come una banca con un logo diverso, evitando di gestire le proprie chiavi e scegliendo la comodità al posto della sovranità. Bitcoin non giudica questa scelta.

La differenza sostanziale è che, prima di Bitcoin, la fiducia era obbligatoria. Per effettuare una transazione online non c’erano alternative: si doveva passare attraverso una banca o un intermediario come PayPal, con il potere totalmente concentrato e nessuna possibilità di sottrarsi. Con Bitcoin, la fiducia diventa opzionale. Si può scegliere di essere sovrani, gestendo le proprie chiavi, verificando le transazioni e diventando la propria banca, ma pagando un prezzo in termini di competenza, responsabilità e tempo. Oppure si può legittimamente decidere di delegare, affidando i bitcoin a terzi.

Il punto non è che tutti debbano essere sovrani. Il punto è che ora è possibile esserlo. In passato la porta della sovranità era chiusa a chiave; Bitcoin ha consegnato la chiave. Spetta a ciascuno decidere se usarla.

---

### Discussione 1: Come funziona Bip39

**Conversazione:**
```
Utente: La mnemonica viene usata come “password” di un algoritmo PBKDF2 insieme a una **passphrase** opzionale (spesso chiamata “25ª parola”) e al sale `"mnemonic" + passphrase`. L’algoritmo (HMAC-SHA512) itera 2048 volte e produce un seed di 512 bit come funziona
LLM: Partiamo dai dettagli: la frase mnemonica (le 12/18/24 parole) viene normalizzata secondo lo standard **NFKD** (Unicode) e poi trasformata in una sequenza di byte (UTF‑8). Quella sequenza diventa la **password** dell'algoritmo PBKDF2.

Il sale è costruito come la stringa fissa `"mnemonic"` seguita dalla **passphrase** opzionale (detta “25ª parola”). Anche la passphrase viene normalizzata NFKD; se l’utente non ne imposta una, il sale è semplicemente `"mnemonic"` (stringa ASCII). Quindi:

```
sale = "mnemonic" + passphrase_normalizzata
```

A questo punto il PBKDF2 (definito in RFC 2898) viene eseguito usando come funzione pseudo-casuale **HMAC‑SHA512**. Le iterazioni sono fissate a **2048**, e la lunghezza del seed richiesto è di **512 bit** (64 byte). In pratica:

1. Si calcola HMAC‑SHA512 con chiave = password (la mnemonica) e messaggio = sale + un contatore a 4 byte codificato in big‑endian.
2. Questo HMAC viene ripetuto 2048 volte, in ogni iterazione il valore precedente è il “messaggio” per l’HMAC successivo (con la stessa chiave).
3. Lo XOR dei 2048 risultati intermedi produce un blocco di 512 bit; se la lunghezza richiesta è maggiore, si incrementa il contatore e si ripete il processo, ma per 512 bit basta un singolo blocco perché l’output di HMAC‑SHA512 è di 512 bit, quindi dopo 2048 iterazioni si ottiene direttamente il seed finale.

Il seed a 512 bit è il **master seed** dell’HD wallet (BIP32): da qui vengono derivate, tramite le catene di derivazione, tutte le chiavi private, gli indirizzi, le chiavi estese. Nota tecnica: BIP39 non definisce una struttura per wallet, lascia libertà, ma lo standard successivo BIP32 si appoggia proprio su questo seed.

Perché 2048 iterazioni? È un compromesso: rallenta un attacco brute‑force (chi ruba la mnemonica e prova passphrase) di un fattore 2048, ma rimane ancora abbastanza veloce su hardware normale (anche su portafogli hardware o smartphone). Se si usasse un solo HMAC, provare 100 miliardi di passphrase sarebbe più rapido; con 2048 iterazioni il costo computazionale cresce proporzionalmente.

Un aspetto cruciale: **qualsiasi modifica alla passphrase produce un seed completamente diverso**, anche partendo dalla stessa mnemonica. Questo permette di creare più portafogli indipendenti dalla medesima lista di parole, oppure di aggiungere uno strato di protezione: se qualcuno trova la mnemonica ma non conosce la passphrase, non può accedere ai fondi (a meno che la passphrase non sia debole). Tuttavia, se dimentichi la passphrase, perdi l’accesso a quel portafoglio per sempre, anche se hai ancora la mnemonica.

Ora una domanda socratica: dopo aver chiarito il meccanismo, cosa pensi della scelta di fissare il sale `"mnemonic"` come stringa costante, invece di usare un sale più imprevedibile? A livello di sicurezza, aiuta o è solo uno standard di comodo? E la passphrase vuota è davvero una scelta sicura?
```

**Risposta finale:** Partiamo dai dettagli: la frase mnemonica (le 12/18/24 parole) viene normalizzata secondo lo standard**NFKD** (Unicode) e poi trasformata in una sequenza di byte (UTF‑8). Quella sequenza diventa la **password**dell'algoritmo PBKDF2.

---

### Discussione 2: è sicuro detenere le chiavi

**Conversazione:**
```
Utente: come detenere le chiavi in sicurezza esplora il web e trovami degli esempi
LLM: Certo, ti do una risposta diretta con esempi concreti dal web, poi aggiungo una domanda socratica per ragionarci sopra.

🔍 **RICERCA: metodi sicuri custodia chiavi private bitcoin esempi 2024 incidenti**

---

### Come detenere le chiavi in sicurezza: esempi e metodi

La domanda «è sicuro detenere le chiavi» ha una risposta articolata: sì, se si adottano protocolli precisi; no, se si sottovalutano i rischi. Ecco cosa ho trovato di rilevante.

**1. Metodi di custodia (dal più sicuro al più rischioso)**

- **Hardware wallet con seed phrase ben protetta** : dispositivi come Trezor, Ledger, Coldcard isolano le chiavi dal mondo online. Il punto debole è la gestione del backup (le 12/24 parole). Se scritte su carta in chiaro e conservate in casa, un furto o un incendio le compromettono. La buona pratica è usare una **passphrase aggiuntiva** (25ª parola) memorizzata mentalmente, e conservare le parole fisiche in un luogo separato e sicuro (es. cassetta di sicurezza, o incise su metallo).

- **Multisig collaborativo** : portafogli come Unchained Capital o Casa usano schemi 2-of-3 o 3-of-5, dove le chiavi sono distribuite tra l'utente, l'azienda e un terzo fidato (o un secondo dispositivo). Questo protegge dal singolo punto di fallimento. Esempio concreto: **Casa** offre un vault 3-of-5 con una chiave utente, una su hardware wallet, una su un nodo personale, una su un server Casa e una di backup. Per spendere servono almeno 3 firme, rendendo l'attacco a singola chiave inutile.

- **Backup su metallo e distribuzione geografica** : prodotti come Cryptosteel o Billfodl permettono di incidere le parole su acciaio resistente al fuoco e all'acqua. Alcuni utenti conservano copie in luoghi diversi (es. una in banca, una da un familiare, una nascosta in un'altra proprietà). Attenzione: dividere le parole in frammenti stile "Shamir Secret Sharing" (SLIP-39) è tecnicamente valido, ma se fatto male può introdurre nuovi rischi.

- **Air-gapped setup con vecchi smartphone** : meno comune ma efficace: usare un telefono mai connesso a internet dopo l'installazione di un wallet Bitcoin-only (es. Electrum su Android senza SIM né Wi-Fi) e firmare transazioni via QR code.

**2. Esempi di incidenti famosi (cattiva custodia)**

- **James Howells (2013)** : perse 8.000 BTC gettando erroneamente un hard disk contenente le chiavi. Oggi quell'hard disk giace in una discarica e lui combatte ancora per recuperarlo. Lezione: **backup multipli su supporti diversi**.
- **Stefan Thomas (2011)** : dimenticò la password di un IronKey USB con 7.002 BTC (oggi ~500 mln $). Dopo 10 tentativi falliti il dispositivo si autodistrugge. Lezione: **la password è parte della custodia**, serve un sistema mnemonico o un erede digitale.
- **Exchange hack (Mt.Gox 2014, Binance 2019, FTX 2022)** : non detengono veramente le chiavi di tutti gli utenti, e quando la piattaforma fallisce o viene attaccata, i fondi spariscono. Lezione: **not your keys, not your coins**.
- **Uso di wallet "brain wallet" deboli** : nel 2015 un ricercatore rubò fondi a decine di utenti che avevano usato frasi celebri o parole comuni come seed. Lezione: **mai generare le chiavi partendo da un essere umano non entropico**.

**3. Protocolli avanzati per grandi somme**

- **Self-custody istituzionale** : aziende come Swan Bitcoin offrono un vault multisig assistito, ma le chiavi restano in controllo dell'utente.
- **Timelock e ereditarietà** : alcuni wallet permettono di impostare una transazione "erede" che dopo un certo periodo di inattività invia i fondi a indirizzi di beneficiari, evitando la perdita per morte improvvisa. Esempio: Liana wallet by Wizardsardine.

---

Ora la parte socratica: hai notato che tutti gli incidenti citati hanno una radice comune? Non un bug tecnico, ma un **errore umano legato alla gestione delle informazioni**.

Qual è secondo te la differenza profonda tra «avere una chiave» e «essere in grado di ricostruirla quando serve»? E cosa succederebbe se il tuo io futuro dimenticasse la procedura che oggi stai progettando?
```

**Risposta finale:** *Air-gapped setup con vecchi smartphone**

---
