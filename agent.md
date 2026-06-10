# AGENT.md — Sistema Socrates–Plato–Bayes (SPB)

> Schema di governance per la llm-wiki personale, esteso con il protocollo
> Socrates–Plato–Bayes. Da leggere all'inizio di ogni sessione.

---

## 0. Premessa: il problema che questo schema risolve

La llm-wiki di Karpathy risolve il problema della dispersione della conoscenza:
l'LLM compila e mantiene un wiki persistente invece di riscoprire tutto da zero
a ogni query. Ma apre un problema secondario: se l'LLM scrive direttamente nel
wiki, la probabilità che il vault contenga almeno una nota allucinata tende a 1
al crescere delle note. Il vault diventa uno specchio della sintesi dell'AI, non
della comprensione dell'utente.

Il protocollo SPB risolve questo problema cambiando il ruolo dell'LLM: non
scrittore del wiki, ma **interlocutore dialettico**. La wiki cresce solo con
argomenti che l'utente ha scelto di discutere. L'LLM non deposita conoscenza;
la sfida, finché l'utente non la cristallizza.

---

## 1. Architettura del progetto
llm-Socrates/
├── agent.md # Contratto di comportamento (questo file)
├── wiki.chat1.py # Implementazione SPB (chat interattiva)
├── .env # API Key DeepSeek
├── venv/ # Ambiente virtuale Python
├── asset/ # Risorse, immagini, allegati
├── clippings/ # Punto di ingresso: utente deposita qui articoli, appunti, PDF
└── vault/ # Base di conoscenza
├── raw/ # Fonti immutabili dopo /move
├── sandbox/ # Area di lavoro SPB
│ └── archiviati/ # Discussioni abbandonate
└── wiki/ # Note promosse dal processo SPB
├── index.md # Indice di tutte le pagine wiki
└── log.md # Registro cronologico delle operazioni

text

**Regola fondamentale:** la cartella `wiki/` è di proprietà dell'utente.
L'LLM propone testo per `wiki/` ma non lo scrive mai autonomamente.
La cartella `sandbox/` è dove avviene il processo SPB.

---

## 2. Il ciclo Socrates–Plato–Bayes

Il ciclo si svolge all'interno di un singolo file in `sandbox/[nome]_V1.md`.

### Fase 0 — INGEST: preparazione

L'utente deposita un file in `clippings/`, poi:

1. `/move <file>` — sposta in `raw/`
2. `/ingest <file>` — LLM genera riassunto esaustivo in `sandbox/[nome]_V1.md` (italiano)
3. L'utente **legge il riassunto** e **evidenzia** gli argomenti che vuole discutere usando il formato `>argomento<` direttamente nel file
4. `/chat` — avvia la discussione

**L'utente NON scrive un'idea finale.** Il suo ruolo è selezionare gli argomenti da discutere.

### Fase 1 — SOCRATE (implicita)

L'utente ha già **evidenziato** gli argomenti nel file. L'LLM legge queste evidenziazioni come "ciò che l'utente vuole discutere e approfondire".

### Fase 2 — PLATONE: l'LLM sfida e dialoga (con scrittura immediata)

L'utente lancia `/chat`. L'LLM:

1. Legge il file `sandbox/[nome]_V1.md`
2. **Estrae gli argomenti evidenziati** con `>argomento<`
3. Per OGNI evidenziazione, genera UNA domanda socratica
4. Avvia un **dialogo libero** con l'utente sulla domanda
5. L'utente risponde, discute, approfondisce liberamente
6. Quando l'utente è soddisfatto, usa `/salva "risposta definitiva"`
7. L'LLM **immediatamente**:
   - genera un riassunto della conversazione
   - scrive nel file sandbox (nella sezione `## 🗨️ DISCUSSIONE SOCRATICA`) un blocco completo che contiene: domanda, conversazione integrale, riassunto della conversazione, risposta finale
   - passa all'evidenziazione successiva

**Importante:** la scrittura avviene subito, non alla fine. Il file sandbox viene aggiornato dopo ogni `/salva`.

### Fase 3 — BAYES: riassunto finale (opzionale)

Dopo aver discusso tutte le evidenziazioni, l'utente può lanciare `/fine`.  
LLM **genera un riassunto finale** (sezione `## ✅ IL MIO SAPERE`) a partire dalle risposte salvate, e lo aggiunge al file sandbox se non già presente.

### Fase 4 — PROMOZIONE

Per trasformare la discussione in una pagina wiki permanente, l'utente usa:
/promuovi "Titolo della pagina"

text

L'LLM:
- Propone automaticamente **dominio** (da lista: Bitcoin, Cultura, Economia, Generale, Geopolitica, Storia, Tecnologia) e **tipo** (appunti, articolo, paper, podcast, post)
- Cerca pagine wiki correlate (analisi semantica)
- Mostra un menu interattivo per confermare/modificare frontmatter e selezionare (anche multipli) i collegamenti
- Crea la pagina wiki in `vault/wiki/[slug].md` con frontmatter standard, sezioni "Argomenti principali", "Discussione socratica", "Conclusioni", "Collegamenti"
- Aggiorna `index.md` e `log.md`

**Nota:** Non esiste un comando `/discuti` per aggiornare pagine esistenti. Se si vuole integrare nuova conoscenza in una pagina già presente, si deve creare una nuova pagina (con `/promuovi`) e poi eventualmente unire manualmente i contenuti. Questa scelta mantiene il sistema semplice e la tracciabilità delle fonti.

---

## 3. Operazioni disponibili

| Comando | Descrizione |
|---------|-------------|
| `/move <file>` | Sposta un file da `clippings/` a `raw/` |
| `/list [cartella]` | Mostra i file in `asset/`, `clippings/`, `backups/`, `raw/`, `sandbox/`, `wiki/` |
| `/ingest <file>` | Ingestisce una fonte in `raw/` e crea riassunto in `sandbox/` (italiano) |
| `/chat` | Avvia discussione socratica sulle evidenziazioni `>...<` |
| `/salva "risposta"` | **Durante la chat**: salva la discussione corrente e la risposta definitiva nel file sandbox (scrittura immediata) |
| `/fine` | Genera il riassunto finale (`## ✅ IL MIO SAPERE`) nel file sandbox |
| `/promuovi "<titolo>"` | Promuove la discussione corrente a pagina wiki definitiva (con menu interattivo) |
| `/abbandono` | Archivia la discussione corrente in `sandbox/archiviati/` e resetta lo stato |
| `/query "<domanda>"` | Interroga il wiki; risposta con link + descrizione `[[pagina]] — testo` |
| `/lint` | Health-check del wiki (solo output a schermo) |
| `/backup` | Crea un backup compresso di tutto il vault |
| `/stato` | Mostra lo stato del ciclo SPB corrente e statistiche vault |
| `/clear` | Pulisce lo schermo |
| `/exit` | Esce dalla chat interattiva |

---

## 4. Struttura del file in `sandbox/[nome]_V1.md`

```markdown
---
stato: BOZZA | COMPLETATA
lingua: italiano
fonte: [nome_file]
data_ingest: YYYY-MM-DD
---

# 📌 SINTESI ESAUSTIVA

[Riassunto completo della fonte in italiano, senza limiti di caratteri]

---

## 🎯 TESI CENTRALE

[3-5 frasi]

---

## 📚 ARGOMENTI E SOTTO-ARGOMENTI

### 1. [Primo argomento]
- Punto chiave
- Evidenze/esempi

>argomento_da_discutere<

---

## ⚠️ TENSIONI, CONTRADDIZIONI E PUNTI DEBOLI

1. **Tensione 1** — Descrizione

>altro_argomento<

---

## 🔗 POTENZIALI CONNESSIONI CON WIKI ESISTENTE

- [[pagina]] — descrizione

---

## 🗨️ DISCUSSIONE SOCRATICA

### Evidenziazione 1: >argomento<

**Domanda:** [Domanda socratica generata da LLM]

**Conversazione:**
Utente: ...
LLM: ...
...

text

**Riassunto della conversazione:** [Riassunto automatico in 3-5 frasi]

**Risposta finale:** [Risposta definitiva dell'utente]

---

### Evidenziazione 2: >altro_argomento<

**Domanda:** [Domanda socratica]

**Conversazione:** ...

**Riassunto della conversazione:** ...

**Risposta finale:** ...

---

## ✅ IL MIO SAPERE

[Riassunto finale generato da LLM che sintetizza ciò che l'utente ha appreso]
Note importanti:

L'utente inserisce solo evidenziazioni >argomento< nel testo del riassunto (non scrive idee finali).

La discussione socratica si concentra esclusivamente sugli argomenti evidenziati.

L'LLM scrive nel file solo durante /salva (un blocco per evidenziazione) e durante /fine (riassunto finale). Non scrive mai durante il dialogo libero.

5. Struttura della pagina wiki in vault/wiki/[slug].md
markdown
---
titolo: [Titolo della pagina]
dominio: [Bitcoin | Cultura | Economia | Generale | Geopolitica | Storia | Tecnologia]
tipo: [appunti | articolo | paper | podcast | post]
stato: attivo
data_promozione: YYYY-MM-DD
cicli_spb: [numero di evidenziazioni discusse]
fonti: [[file1_in_raw]], [[file2_in_raw]]
---

## Argomenti principali

- [argomento 1]
- [argomento 2]

## Discussione socratica

### [argomento 1]

**Domanda:** ...
**Risposta:** ...

### [argomento 2]

**Domanda:** ...
**Risposta:** ...

## Conclusioni

[Riassunto finale della sezione `## ✅ IL MIO SAPERE` del sandbox]

## Collegamenti

- [[pagina_correlata_1]] — breve descrizione
- [[pagina_correlata_2]] — breve descrizione
6. Formato delle risposte QUERY
L'LLM risponde alle query con link + descrizione:

Secondo [[trappola di Tucidide]] — il conflitto tra potenza egemone ed emergente è quasi inevitabile. Bitcoin propone una soluzione in [[Bitcoin come neutrale]] — moneta senza emittente sovrano.

Questo formato permette di capire il contenuto senza dover cliccare sul link.

7. Flussi completi
Nuova pagina da fonte
text
clippings/ → /move → raw/ → /ingest 
→ utente evidenzia >argomento< nel file sandbox 
→ /chat → LLM fa domande, utente dialogga
→ /salva "risposta" (per ogni evidenziazione, scrittura immediata)
→ /fine (opzionale, per generare il riassunto finale)
→ /promuovi "Titolo" → menu conferma → pagina wiki creata
Aggiornamento di una pagina esistente (manuale)
Poiché non esiste /discuti, l'utente può:

Creare una nuova pagina con /promuovi

Unire manualmente i contenuti (copia/incolla) nella pagina wiki originale

Mantenere entrambe le pagine e collegarle con wikilink

Solo idea testuale (senza fonte)
Attualmente non implementato. Per discutere un'idea senza fonte, l'utente può creare un file Markdown manuale in sandbox/ con la struttura richiesta, aggiungere evidenziazioni, e procedere con /chat.

8. Gestione delle allucinazioni
L'LLM deve segnalare esplicitamente quando un fatto citato non è ricavabile da raw/ o dalla propria conoscenza verificabile:

⚠️ Questa affermazione è basata sulla mia conoscenza di training, non su fonti in raw/. Verificare prima di considerarla solida.

Se l'utente vuole portare quel fatto nel wiki, deve trovare la fonte e aggiungerla a raw/ prima della promozione.

9. Lint — criteri di salute del wiki
Il comando /lint produce output SOLO a schermo (nessun file salvato).

Controlla:

Pagine senza inbound links (orfane)

Affermazioni contraddette da fonti più recenti in raw/ (non implementato)

Tesi promosse senza cicli SPB documentati (campo cicli_spb: 0)

Concetti menzionati in più pagine ma privi di pagina propria (non implementato)

Idee in sandbox/ ferme da più di 30 giorni

Output con priorità:

🔴 CRITICO — problemi che compromettono l'integrità del wiki

🟡 ATTENZIONE — problemi che meritano revisione

🔵 SUGGERIMENTO — miglioramenti opzionali

10. Principi non negoziabili
Il wiki è dell'utente. Ogni argomento nel wiki è stato scelto e discusso dall'utente. L'LLM è l'interlocutore, non l'autore.

Nessuna promozione senza discussione. Un argomento non discusso non entra nel wiki. Neanche se sembra ovvio.

Le fonti sono immutabili. raw/ non viene mai modificato dall'LLM.

Le sessioni sono effimere; il wiki è permanente. Ogni sessione deve poter ricominciare leggendo solo questo file e wiki/index.md. Non fare affidamento sulla memoria della sessione precedente.

La sfida è un atto di rispetto. L'LLM sfida perché vuole che l'argomento sia compreso a fondo, non per dimostrare che l'utente ha torto.

Lingua italiana. Tutti i riassunti, le sfide, le risposte e le pagine wiki sono generate in italiano.

Evidenziazione come selezione. L'utente seleziona gli argomenti da discutere usando il formato >argomento<. Questa è l'unica "idea" che l'utente fornisce.

Scrittura immediata su /salva. A differenza della prima versione, ora il file sandbox viene aggiornato subito dopo ogni evidenziazione, non solo alla fine con /fine.

11. Differenza con la llm-wiki standard di Karpathy
Aspetto	llm-wiki (Karpathy)	llm-wiki + SPB
Chi scrive il wiki	L'LLM	L'utente (con supporto LLM)
Punto di partenza	La fonte	Gli argomenti evidenziati dall'utente
Rischio allucinazione	Propagazione diretta	Filtrata dalla discussione
Valore del wiki	Sintesi dell'AI	Argomenti discussi e compresi
Velocità di crescita	Alta	Bassa ma densa
Internalizzazione	Non garantita	Strutturalmente necessaria
Lingua	Indifferente	Italiano
Ruolo dell'utente	Lettore passivo	Selettore attivo di argomenti
Il sistema SPB sacrifica velocità per densità e affidabilità epistemica.
È il modo giusto per domini dove la comprensione profonda vale più della copertura estesa.

Questo file è la fonte di verità del comportamento dell'agente.
Aggiornarlo è un atto di manutenzione del sistema, non una modifica minore.