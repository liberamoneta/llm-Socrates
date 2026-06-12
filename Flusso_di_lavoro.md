┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASE 1: INGEST                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /move file.md                                                               │
│       │                                                                      │
│       ▼                                                                      │
│  clippings/file.md ──────────────────────────────────────────► raw/file.md  │
│                                                                              │
│  /ingest file.md                                                             │
│       │                                                                      │
│       ▼                                                                      │
│  raw/file.md ──────────────────────────────────────────► sandbox/sdbx_file_V1.md
│                                                                    │         │
│                                                    (riassunto + sezioni vuote)
│                                                                    │         │
│                                              (utente aggiunge >argomento< manuale)
│                                                                    │         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASE 2: CHAT                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /chat [sdbx_file_V1.md]                                                     │
│       │                                                                      │
│       ▼                                                                      │
│  LLM genera domanda socratica per ogni >argomento<                           │
│       │                                                                      │
│       ▼                                                                      │
│  Dialogo libero (LLM può cercare online)                                     │
│       │                                                                      │
│       ▼                                                                      │
│  /salva "risposta finale"                                                    │
│       │                                                                      │
│       ▼                                                                      │
│  Aggiunge al sandbox:                                                         │
│    • Domanda                                                                  │
│    • Conversazione completa                                                   │
│    • Riassunto narrativo tecnico (senza punti elenco)                         │
│    • Risposta finale                                                          │
│       │                                                                      │
│       ▼                                                                      │
│  (ripeti per ogni evidenziazione)                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASE 3: SINTESI                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /fine                                                                       │
│       │                                                                      │
│       ▼                                                                      │
│  LLM legge tutti i riassunti delle evidenziazioni                            │
│       │                                                                      │
│       ▼                                                                      │
│  Genera riassunto UNIFICATO (IL MIO SAPERE):                                  │
│    • Prima persona ("Ho compreso che...")                                     │
│    • Narrativo, tecnico, senza punti elenco                                   │
│    • Trova filo logico tra le evidenziazioni                                  │
│       │                                                                      │
│       ▼                                                                      │
│  Aggiunge al sandbox la sezione ## ✅ IL MIO SAPERE                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASE 4: PROMOZIONE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /promuovi "Titolo della pagina"                                              │
│       │                                                                      │
│       ▼                                                                      │
│  LLM propone:                                                                 │
│    • Dominio (Bitcoin, Cultura, Economia, Generale, Geopolitica, Storia, Tecnologia)
│    • Tipo (appunti, articolo, paper, podcast, post)                          │
│    • Wikilink (cerca pagine wiki correlate)                                  │
│       │                                                                      │
│       ▼                                                                      │
│  Menu interattivo:                                                            │
│    • Confermi frontmatter? (s/n/modifica)                                    │
│    • Selezioni wikilink (numeri separati da virgole)                         │
│       │                                                                      │
│       ▼                                                                      │
│  Crea wiki/titolo.md con:                                                     │
│    • Frontmatter (confermato)                                                │
│    • COPIA ESATTA del sandbox                                                │
│    • Sezione Collegamenti (wikilink scelti)                                  │
│       │                                                                      │
│       ▼                                                                      │
│  Sposta sandbox in sandbox/archiviati/                                        │
│       │                                                                      │
│       ▼                                                                      │
│  Aggiorna wiki/index.md e wiki/log.md                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASE 5: RIPRISTINO (opzionale)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /riprendi sdbx_nome_V1.md                                                   │
│       │                                                                      │
│       ▼                                                                      │
│  Cerca in sandbox/archiviati/                                                │
│       │                                                                      │
│       ▼                                                                      │
│  COPIA (non sposta) il file in sandbox/                                      │
│       │                                                                      │
│       ▼                                                                      │
│  Resetta stato                                                               │
│       │                                                                      │
│       ▼                                                                      │
│  Messaggio: "✅ Discussione ripristinata. Usa /chat per continuare"          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘