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

```
llm-Socrates/
├── agent.md                  # Contratto di comportamento (questo file)
├── analisi_wiki.py           # Implementazione SPB (chat interattiva)
├── pdf_to_md.py              # Converte PDF in Markdown
├── traduci.py                # Traduce file Markdown in italiano
├── .env                      # API Key DeepSeek / SiliconFlow
├── venv/                     # Ambiente virtuale Python
├── asset/                    # Risorse, immagini, allegati
├── clippings/                # Punto di ingresso: utente deposita qui articoli, appunti, PDF
└── vault/                    # Base di conoscenza
    ├── raw/                  # Fonti immutabili (Markdown pronti per ingest)
    ├── sandbox/              # Area di lavoro SPB
    │   ├── .stato_spb.json   # Stato della sessione corrente
    │   ├── .checkpoint.json  # Checkpoint per /pausa e ripresa
    │   └── archiviati/       # Discussioni completate o abbandonate
    └── wiki/                 # Note promosse dal processo SPB
        ├── index.md          # Indice tabellare di tutte le pagine wiki
        ├── log.md            # Registro cronologico delle operazioni
        └── .indice_wiki.json # Indice JSON leggero per /query
```

**Regola fondamentale:** la cartella `wiki/` è di proprietà dell'utente.
L'LLM propone testo per `wiki/` ma non lo scrive mai autonomamente.
La cartella `sandbox/` è dove avviene il processo SPB.

**Nota:** I file sandbox hanno prefisso `sdbx_` (es. `sdbx_articolo_V1.md`).

---

## 2. Flusso completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FLUSSO COMPLETO SPB                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📄 PDF / articolo                                                          │
│       ↓                                                                     │
│  python pdf_to_md.py        → clippings/documento.md + asset/immagini       │
│       ↓                                                                     │
│  python traduci.py (opz.)   → raw/documento_it.md                           │
│       ↓                                                                     │
│  [MANUALE] Aggiungi marcatori >>...<< e ??...?? nel file raw/               │
│       ↓                                                                     │
│  📥 /analizza documento.md  → sandbox/sdbx_documento_V1.md                  │
│       ↓                                                                     │
│  💬 /chat                   → discussione socratica ibrida                  │
│       ↓                                                                     │
│  💾 /salva "risposta"       → salva discussione + riassunto nel sandbox     │
│       ↓                                                                     │
│  🏁 /fine                   → genera "IL MIO SAPERE" (riassunto unificato)  │
│       ↓                                                                     │
│  📚 /promuovi "Titolo"      → wiki/Titolo.md + sandbox archiviato           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Marcatori nei file raw/

Prima di lanciare `/analizza`, l'utente **manualmente** inserisce due tipi
di marcatori nel file Markdown dentro `raw/`:

| Marcatore | Effetto |
|-----------|---------|
| `>>testo<<` | **COPIA** il testo nella sezione `## 📌 EVIDENZE DA DISCUTERE` del sandbox. Il testo marcato viene **rimosso dalla sintesi** (non la influenza). Serve a dare contesto alla chat. |
| `??testo??` | **GENERA** una domanda socratica nella sezione `## ❓ DOMANDE DA DISCUTERE`. Anche questo testo è **escluso dalla sintesi**. |

Esempio di file raw con marcatori:

```markdown
L'economia circolare è un modello di produzione e consumo che implica
condivisione, prestito, riutilizzo, riparazione e riciclo dei materiali
e prodotti esistenti il più a lungo possibile.

>>L'UE genera 2.2 miliardi di tonnellate di rifiuti ogni anno.<<

Questo modello sfida il tradizionale paradigma lineare "prendi-produci-getta".

??Quali settori industriali sono più resistenti alla transizione circolare??
```

---

## 4. Il ciclo Socrates–Plato–Bayes

### Fase 1 — INGEST: `/analizza <file>`

**Input:** un file Markdown in `raw/` (da `pdf_to_md.py`, `traduci.py` o creato manualmente).

**Processo:**
1. Estrae i marcatori `>>...<<` (blocchi evidenza) e `??...??` (domande socratiche)
2. Rimuove tutti i marcatori dal testo originale
3. Invia il testo pulito all'LLM per generare una **sintesi esaustiva** in paragrafi continui
4. Crea il file sandbox con tre sezioni: SINTESI, EVIDENZE, DOMANDE

**Nota:** il file viene elaborato **intero**, senza suddivisione in chunk
(il valore `CHUNK_SIZE = 1500` è definito ma attualmente inutilizzato).

**File creato:** `sandbox/sdbx_[nome]_V1.md`

**Struttura del sandbox dopo `/analizza`:**

```markdown
---
stato: BOZZA
lingua: italiano
fonte: documento.md
data_ingest: YYYY-MM-DD
---

# 📌 SINTESI ESAUSTIVA

[Riassunto in paragrafi continui, termini tecnici originali,
seguendo l'ordine del documento. Niente elenchi puntati.]

---

## 📌 EVIDENZE DA DISCUTERE

### Evidenza 1

>>L'UE genera 2.2 miliardi di tonnellate di rifiuti ogni anno.<<

### Evidenza 2

>>...<<

---

## ❓ DOMANDE DA DISCUTERE

### Domanda 1

??Quali settori industriali sono più resistenti alla transizione circolare??

### Domanda 2

??...??
```

### Fase 2 — SOCRATE: `/chat [file]`

**Processo:**
1. Legge il file sandbox
2. Estrae tutte le domande `??...??` dalla sezione `## ❓ DOMANDE DA DISCUTERE`
3. Estrae tutte le evidenze `>>...<<` dalla sezione `## 📌 EVIDENZE DA DISCUTERE`
4. Per **ogni domanda** (in sequenza), avvia un dialogo con **approccio ibrido**

**Approccio ibrido:**
- **Domande fattuali** ("quando?", "quanti?", "come funziona?", "cos'è?") → LLM risponde **direttamente** con dati e precisione
- **Domande concettuali** ("perché?", "ha senso?", "è giusto?") → LLM usa **approccio socratico** (domande guidate, mai la risposta diretta)
- L'LLM può mescolare: rispondere ai fatti e poi fare una domanda socratica di approfondimento
- L'LLM può cercare online (Brave API o DuckDuckGo) se utile

**Comandi disponibili durante `/chat`:**

| Comando | Effetto |
|---------|---------|
| `/salva "risposta"` | Salva la discussione corrente (conversazione + riassunto + risposta finale) e passa alla prossima domanda |
| `/salta` | Salta la domanda corrente senza salvarla; passa alla successiva |
| `/pausa` | Salva un checkpoint e torna al prompt principale (riprendibile con `/chat`) |
| `/archivia` | Archivia l'intera discussione in `archiviati/` ed esce dalla chat |
| `/list` | Mostra i file delle cartelle |
| `/stato` | Mostra lo stato corrente |
| `/lint` | Health-check del wiki |
| `/backup` | Backup del vault |

**Su `/salva`, il sistema scrive immediatamente nel sandbox:**

```markdown
## 🗨️ DISCUSSIONE SOCRATICA

### Discussione 1: ??Quali settori sono più resistenti???

**Conversazione:**
Utente: Secondo me il settore automotive...
LLM: Interessante. Ma consideriamo che...
...

**Riassunto della conversazione:**
[Riassunto narrativo tecnico generato dall'LLM, testo fluido senza elenchi]

**Risposta finale:** Il settore energetico fossile è il più resistente
perché l'infrastruttura estrattiva non è riconvertibile.

---

### Discussione 2: ??...??
...
```

**Struttura del sandbox dopo `/chat` e `/salva` (tutte le domande):**

```markdown
---
stato: BOZZA
...

# 📌 SINTESI ESAUSTIVA
...

## 📌 EVIDENZE DA DISCUTERE
...

## ❓ DOMANDE DA DISCUTERE
...

## 🗨️ DISCUSSIONE SOCRATICA

### Discussione 1: ...
### Discussione 2: ...
```

### Fase 3 — BAYES: `/fine`

Genera il **riassunto narrativo unificato** di tutte le discussioni salvate.

**Processo:**
1. Estrae ogni blocco `### Discussione N:` dal sandbox
2. Per ciascuno recupera: domanda, riassunto della conversazione, risposta finale
3. Invia tutto all'LLM per generare un riassunto in prima persona
4. Scrive il risultato nella sezione `## ✅ IL MIO SAPERE` del sandbox

**Se la sezione `IL MIO SAPERE` esiste già** (non vuota): non viene rigenerata.

### Fase 4 — PROMOZIONE: `/promuovi "Titolo"`

Promuove il sandbox a pagina wiki permanente.

**Processo interattivo:**
1. Chiede **dominio** (Bitcoin, Cultura, Economia, Generale, Geopolitica, Storia, Tecnologia, o inserimento manuale)
2. Chiede **tipo** (appunti, articolo, paper, podcast, post, o inserimento manuale)
3. Pulisce il contenuto sandbox:
   - Rimuove il vecchio frontmatter YAML
   - Rimuove `## 📌 EVIDENZE DA DISCUTERE`
   - Rimuove `## ❓ DOMANDE DA DISCUTERE`
   - Rimuove `## 🗨️ DISCUSSIONE SOCRATICA` (il wiki conserva il risultato, non il percorso)
   - Rimuove i riassunti delle conversazioni e i placeholder
   - Conserva: `# 📌 SINTESI ESAUSTIVA` + `## ✅ IL MIO SAPERE`
4. Crea un nuovo frontmatter YAML con titolo, dominio, tipo, data, cicli_spb, fonti
5. Scrive la pagina wiki
6. Sposta il sandbox in `sandbox/archiviati/`
7. Aggiorna `wiki/index.md` e `wiki/log.md`

**Versionamento:** se una pagina con lo stesso slug esiste già:
- Se esistono versioni `_v2`, `_v3`... → crea `_v{N+1}`
- Altrimenti → crea `_YYYYMMDD` con data

**Struttura della pagina wiki risultante:**

```markdown
---
titolo: Titolo della pagina
dominio: Tecnologia
tipo: articolo
stato: attivo
data_promozione: YYYY-MM-DD
cicli_spb: 3
fonti: [[documento.md]]
---

# 📌 SINTESI ESAUSTIVA

[Contenuto copiato dal sandbox]

## ✅ IL MIO SAPERE

[Contenuto copiato dal sandbox]
```

---

## 5. Riepilogo comandi

| Comando | Dove | Descrizione |
|---------|------|-------------|
| `/analizza <file>` | Prompt principale | Analizza file in `raw/`, estrae marcatori, genera sintesi nel sandbox |
| `/chat [file]` | Prompt principale | Avvia/riprende discussione socratica ibrida sulle domande `??...??` |
| `/salva "risposta"` | Durante `/chat` | Salva discussione, riassunto e risposta; passa alla prossima domanda |
| `/salta` | Durante `/chat` | Salta la domanda corrente e passa alla successiva |
| `/pausa` | Durante `/chat` | Salva checkpoint e torna al prompt principale |
| `/fine` | Prompt principale | Genera riassunto unificato in `## ✅ IL MIO SAPERE` |
| `/promuovi "Titolo"` | Prompt principale | Promuove sandbox a pagina wiki e archivia il sandbox |
| `/riprendi <file>` | Prompt principale | Ripristina un sandbox da `archiviati/` per continuare |
| `/archivia` | Entrambi | Archivia il sandbox corrente in `archiviati/` |
| `/query "domanda"` | Prompt principale | Interroga wiki locale + fallback ricerca web |
| `/list [cartella]` | Entrambi | Mostra file in asset, clippings, backups, raw, sandbox, wiki |
| `/lint` | Entrambi | Health-check: pagine orfane, sandbox attivi da >30gg |
| `/backup` | Entrambi | Crea backup zip di vault, clippings, asset, agent.md, analisi.py, .env |
| `/stato` | Entrambi | Mostra provider, modello, fase corrente, statistiche vault |
| `/clear` | Prompt principale | Pulisce lo schermo |
| `/exit` | Prompt principale | Esce dal programma |

---

## 6. Comandi di dettaglio

### `/query "domanda"`

1. **Primo passo:** cerca nel wiki locale usando `.indice_wiki.json`
   - Matching per: dominio nel testo della domanda, tag, titolo
   - Restituisce fino a 3 pagine più rilevanti
2. **Se trova pagine:** estrae da ciascuna le sezioni `## Sviluppo analitico`,
   `## ✅ Il mio sapere`, `## Le mie evidenze` e chiede all'LLM di rispondere
   basandosi su quei contenuti
3. **Se la risposta wiki è sufficiente** (>150 caratteri): mostra risultato marcato `[WIKI]`
4. **Altrimenti:** fallback a ricerca web (Brave API → DuckDuckGo)
   - I risultati web vengono mostrati direttamente

### `/stato`

Mostra:
- Provider e modello in uso
- Fase corrente (es. `INGEST_COMPLETATO`, `IN_DISCUSSIONE`)
- File attivo
- Numero di evidenze/domande trovate e indice corrente
- Statistiche: conteggio file in `raw/`, `wiki/`, `sandbox/`

### `/lint`

Controlla (solo output a schermo, nessun file modificato):
- **Pagine orfane:** pagine wiki senza wikilink entranti da altre pagine
- **Sandbox vecchi:** file `sdbx_*.md` non archiviati da più di 30 giorni

### `/backup`

Crea uno zip in `backups/vault_backup_YYYYMMDD_HHMMSS.zip` contenente:
- Cartelle: `clippings/`, `vault/`, `asset/`
- File: `agent.md`, `analisi_wiki.py`, `.env`

### `/list [cartella]`

Se viene specificata una cartella (`raw`, `sandbox`, `wiki`, `clippings`, `asset`, `backups`):
mostra fino a 20 file contenuti.

Se nessuna cartella o `all`: mostra tutte le cartelle con fino a 10 file ciascuna.

### `/riprendi <file>`

1. Cerca il file in `sandbox/archiviati/`
2. Accetta nomi con o senza prefisso `sdbx_` e con o senza `.md`
3. **Copia** (non sposta) il file in `sandbox/`
4. Imposta lo stato come `INGEST_COMPLETATO`

---

## 7. Autocompletamento (Tab)

Se `readline` è disponibile, il sistema offre completamento tramite Tab:

| Contesto | Completamento |
|----------|--------------|
| Inizio riga | Tutti i comandi (`/analizza`, `/chat`, `/list`, ...) |
| `/list ` | Cartelle (`asset`, `clippings`, `backups`, `raw`, `sandbox`, `wiki`, `all`) |
| `/analizza ` | File `.md` in `raw/` |
| `/chat ` | File `sdbx_*.md` in `sandbox/` |

---

## 8. Provider e modelli

Selezionabili all'avvio tramite menu interattivo.

### DeepSeek Ufficiale
Base URL: `https://api.deepseek.com`

| Modello | Descrizione |
|---------|-------------|
| `deepseek-chat` | Standard |
| `deepseek-reasoner` | Ragionamento |
| `deepseek-v4-pro` | Modello di punta |

### SiliconFlow
Base URL: `https://api.siliconflow.com/v1`

| Modello | Descrizione |
|---------|-------------|
| `deepseek-ai/DeepSeek-V3` | Chat generale, ragionamento, codice |
| `deepseek-ai/DeepSeek-R1` | Ragionamento avanzato, matematica, logica |
| `deepseek-ai/DeepSeek-V2` | Bilanciato, veloce, economico |
| `Qwen/Qwen2.5-72B-Instruct` | Traduzioni, scrittura, analisi testi |
| `Qwen/Qwen2.5-32B-Instruct` | Traduzioni, scrittura (più economico) |
| `zai-org/GLM-5.2` | Coding |

### Configurazione `.env`

```env
DEEPSEEK_API_KEY=sk-...
SILICONFLOW_API_KEY=sk-...
BRAVE_API_KEY=...              # opzionale, per ricerca web
```

Il sistema cerca `.env` in: `./.env`, `./llm-Socrates/.env`, `../.env`.

---

## 9. Stato e persistenza

### File di stato
- `.stato_spb.json` — fase, file corrente, domande, storico chat
- `.checkpoint.json` — creato da `/pausa`; scade dopo 24 ore
- `.indice_wiki.json` — indice leggero per `/query`; rigenerabile con `costruisci_indice()`

### Fasi possibili nello stato
```
NESSUNO  →  INGEST_COMPLETATO  →  IN_DISCUSSIONE  →  COMPLETATA
```

---

## 10. Gestione delle allucinazioni

L'LLM deve segnalare esplicitamente quando un fatto citato non è ricavabile
da `raw/` o dalla propria conoscenza verificabile:

> ⚠️ Questa affermazione è basata sulla mia conoscenza di training, non su
> fonti in raw/. Verificare prima di considerarla solida.

Se l'utente vuole portare quel fatto nel wiki, deve trovare la fonte e
aggiungerla a `raw/` prima della promozione.

---

## 11. Principi non negoziabili

| Principio | Descrizione |
|-----------|-------------|
| **Il wiki è dell'utente** | Ogni argomento nel wiki è stato scelto e discusso dall'utente. L'LLM è l'interlocutore, non l'autore. |
| **Nessuna promozione senza discussione** | Un argomento non discusso non entra nel wiki. Neanche se sembra ovvio. |
| **Le fonti sono immutabili** | `raw/` non viene mai modificato dall'LLM. |
| **Sessioni effimere, wiki permanente** | Ogni sessione deve poter ricominciare leggendo solo questo file e `wiki/index.md`. |
| **La sfida è un atto di rispetto** | L'LLM sfida perché vuole che l'argomento sia compreso a fondo, non per dimostrare che l'utente ha torto. |
| **Lingua italiana** | Tutti i riassunti, le sfide, le risposte e le pagine wiki sono generate in italiano. |
| **Marcatori nel raw** | L'utente prepara il file con `>>...<<` (evidenze) e `??...??` (domande) prima dell'ingest. |
| **Chat ibrida** | L'LLM risponde direttamente a domande fattuali e usa approccio socratico per domande concettuali. |
| **Scrittura immediata su `/salva`** | Il sandbox viene aggiornato subito dopo ogni discussione, non alla fine. |
| **Riassunto narrativo tecnico** | I riassunti sono testi fluidi, senza punti elenco, con linguaggio preciso. |
| **Archiviazione dopo promozione** | I sandbox promossi vengono spostati in `sandbox/archiviati/`. |
| **Versionamento pagine wiki** | Se una pagina esiste già, `/promuovi` crea una nuova versione con wikilink all'originale. |

---

## 12. Differenza con la llm-wiki standard di Karpathy

| Aspetto | llm-wiki (Karpathy) | llm-wiki + SPB |
|---------|---------------------|----------------|
| Chi scrive il wiki | L'LLM | L'utente (con supporto LLM) |
| Punto di partenza | La fonte | Marcatori `>>...<<` e `??...??` nel raw |
| Rischio allucinazione | Propagazione diretta | Filtrata dalla discussione socratica |
| Valore del wiki | Sintesi dell'AI | Argomenti discussi e compresi |
| Velocità di crescita | Alta | Bassa ma densa |
| Internalizzazione | Non garantita | Strutturalmente necessaria |
| Lingua | Indifferente | Italiano |
| Ruolo dell'utente | Lettore passivo | Preparatore di marcatori + interlocutore |

Il sistema SPB sacrifica velocità per densità e affidabilità epistemica.
È il modo giusto per domini dove la comprensione profonda vale più della
copertura estesa.

---

Questo file è la fonte di verità del comportamento dell'agente.
Aggiornarlo è un atto di manutenzione del sistema, non una modifica minore.
