#!/usr/bin/env python3
"""
analisi_ingest.py — Sistema Socrates–Plato–Bayes (SPB) - Versione Definitiva
Flusso: /estrai (>>---<<) → /analizza (unificato) → /chat → /salva → /fine → /promuovi
"""

import os
import sys
import json
import shutil
import zipfile
import re
import textwrap
from datetime import date, datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Tentativo di importare readline per autocompletamento (opzionale)
try:
    import readline
except ImportError:
    readline = None

load_dotenv()

class Colors:
    GREEN = '\033[92m'; YELLOW = '\033[93m'; BLUE = '\033[94m'
    RED = '\033[91m'; CYAN = '\033[96m'; MAGENTA = '\033[95m'
    END = '\033[0m'; BOLD = '\033[1m'; DIM = '\033[2m'

def print_wrapped(text, color=Colors.CYAN, prefix="🤖 "):
    try:
        width = shutil.get_terminal_size().columns - len(prefix) - 2
        if width < 40:
            width = 80
    except:
        width = 80
    wrapped = textwrap.fill(text, width=width)
    print(f"\n{color}{prefix}{wrapped}{Colors.END}")

# ============================================================
# COSTANTI
# ============================================================

ASSET = Path("asset")
CLIPPINGS = Path("clippings")
BACKUPS = Path("backups")
VAULT = Path("vault")
RAW = VAULT / "raw"
WIKI = VAULT / "wiki"
SANDBOX = VAULT / "sandbox"
ARCHIVIATI = SANDBOX / "archiviati"
INDEX = WIKI / "index.md"
LOG = WIKI / "log.md"
AGENT_MD = Path("agent.md")
STATE_FILE = SANDBOX / ".stato_spb.json"
CHECKPOINT_PATH = SANDBOX / ".checkpoint.json"
INDICE_PATH = WIKI / ".indice_wiki.json"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print(f"{Colors.RED}❌ ERRORE: DEEPSEEK_API_KEY non trovata{Colors.END}")
    sys.exit(1)

CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Modello DeepSeek
DEEPSEEK_PRO = "deepseek-v4-pro"
CURRENT_MODEL = DEEPSEEK_PRO

# Dimensione chunk per ingest
CHUNK_SIZE = 1500

# Brave Search API
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

# ============================================================
# FUNZIONI DI UTILITÀ
# ============================================================

def init_vault():
    for d in [ASSET, CLIPPINGS, BACKUPS, RAW, WIKI, SANDBOX, ARCHIVIATI]:
        d.mkdir(parents=True, exist_ok=True)
    if not INDEX.exists():
        INDEX.write_text("# Indice del Wiki\n\n| Pagina | Dominio | Tipo | Data |\n|--------|---------|------|------|\n\n", encoding='utf-8')
    if not LOG.exists():
        LOG.write_text("# Log delle Operazioni\n\n", encoding='utf-8')

def read_file_safe(filepath: Path) -> str:
    with open(filepath, 'rb') as f:
        raw = f.read()
    for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'cp850']:
        try:
            return raw.decode(enc)
        except:
            continue
    return raw.decode('utf-8', errors='replace')

def write_file_safe(filepath: Path, content: str):
    filepath.write_text(content, encoding='utf-8', errors='replace')

def load_stato() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(read_file_safe(STATE_FILE))
        except:
            return {"fase": None, "file_corrente": None, "evidenziazioni": [], "conversazioni": [], "indice": 0,
                    "domanda_corrente": None, "evidenziazione_corrente": None, "storico_chat": []}
    return {"fase": None, "file_corrente": None, "evidenziazioni": [], "conversazioni": [], "indice": 0,
            "domanda_corrente": None, "evidenziazione_corrente": None, "storico_chat": []}

def save_stato(stato: dict):
    write_file_safe(STATE_FILE, json.dumps(stato, ensure_ascii=False, indent=2))

def reset_stato():
    save_stato({"fase": None, "file_corrente": None, "evidenziazioni": [], "conversazioni": [], "indice": 0,
                "domanda_corrente": None, "evidenziazione_corrente": None, "storico_chat": []})

def read_agent_md() -> str:
    return read_file_safe(AGENT_MD) if AGENT_MD.exists() else "(agent.md non trovato)"

def update_log(operation, details):
    """Aggiorna log.md"""
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_entry = f"## [{today}] {operation}\n{details}\n\n"
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def call_llm(system: str, messages: list, allow_search: bool = False, model: str = None) -> str:
    """Chiamata LLM con supporto opzionale per ricerca esterna"""
    try:
        if allow_search:
            print(f"{Colors.DIM}🔍 Ricerca esterna abilitata...{Colors.END}", flush=True)
        
        model_to_use = model if model else CURRENT_MODEL
        print(f"{Colors.DIM}🤖 Chiamata DeepSeek ({model_to_use})...{Colors.END}", flush=True)
        response = CLIENT.chat.completions.create(
            model=model_to_use,
            messages=[{"role": "system", "content": system}, *messages],
            max_tokens=8000, temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"{Colors.RED}Errore API: {e}{Colors.END}"

def build_system(enable_search: bool = False) -> str:
    base = f"""Sei l'agente del sistema Socrates–Plato–Bayes (SPB) in lingua italiana.
Regole: Fase INGEST: riassunto ESAUSTIVO. Fase CHAT: conversazione socratica.
Mantieni un tono colloquiale ma rigoroso.
{read_agent_md()}"""
    
    if enable_search:
        base += """
        
        RICERCA ESTERNA ABILITATA: Se ritieni utile approfondire un tema con dati, esempi o controesempi tratti dal web, puoi farlo. 
        Scrivi "🔍 RICERCA: [query]" e io simulerò una ricerca. Usa questo solo quando arricchisce la discussione in modo critico e costruttivo.
        Le fonti devono essere citate in modo verosimile.
        """
    return base

def estrai_evidenziazioni(contenuto: str) -> list:
    """Estrae evidenziazioni >...< per la chat"""
    return re.findall(r'>([^<]+)<', contenuto)

def estrai_sezione(contenuto: str, pattern: str) -> str:
    """Estrae una sezione dal markdown usando un pattern regex"""
    match = re.search(pattern + r'\n\n(.*?)(?=\n##|\n---|\Z)', contenuto, re.DOTALL)
    return match.group(1).strip() if match else ""

def estrai_evidenze_marcate(contenuto: str) -> list:
    """Estrae i blocchi marcati con >>---<< per /estrai"""
    pattern_multiriga = r'>>---<<\s*\n(.*?)\n\s*>>---<<'
    matches = re.findall(pattern_multiriga, contenuto, re.DOTALL)
    pattern_singola = r'>>---<<(.*?)>>---<<'
    matches_singola = re.findall(pattern_singola, contenuto, re.DOTALL)
    tutte = [m.strip() for m in matches] + [m.strip() for m in matches_singola]
    return tutte

# ============================================================
# CHECKPOINT E ROLLBACK
# ============================================================

def salva_checkpoint(operazione: str, file_corrente: str, stato: dict):
    """Salva checkpoint dell'operazione in corso"""
    checkpoint = {
        "operazione": operazione,
        "file_corrente": file_corrente,
        "stato": stato,
        "timestamp": datetime.now().isoformat()
    }
    write_file_safe(CHECKPOINT_PATH, json.dumps(checkpoint, ensure_ascii=False, indent=2))

def carica_checkpoint() -> dict:
    """Carica l'ultimo checkpoint"""
    if CHECKPOINT_PATH.exists():
        try:
            return json.loads(read_file_safe(CHECKPOINT_PATH))
        except:
            return {}
    return {}

def ripulisci_file_orfani():
    """Pulisce file temporanei orfani all'avvio"""
    for chunk_file in RAW.glob("*_chunk*.md"):
        sb_name = chunk_file.name.replace(".md", "_V1.md")
        sb_name = f"sdbx_{sb_name}"
        if not (SANDBOX / sb_name).exists():
            print(f"{Colors.DIM}🧹 Rimozione file orfano: {chunk_file.name}{Colors.END}")
            chunk_file.unlink()
    
    if CHECKPOINT_PATH.exists():
        try:
            checkpoint = json.loads(read_file_safe(CHECKPOINT_PATH))
            timestamp = datetime.fromisoformat(checkpoint.get("timestamp", ""))
            if (datetime.now() - timestamp).days > 0:
                CHECKPOINT_PATH.unlink()
        except:
            pass

# ============================================================
# INDICE LEGGERO PER /query
# ============================================================

def costruisci_indice():
    """Costruisce un indice leggero del wiki (titolo→dominio→tags)"""
    indice = {}
    for f in WIKI.glob("*.md"):
        if f.name in ["index.md", "log.md", ".indice_wiki.json"]:
            continue
        contenuto = read_file_safe(f)
        
        frontmatter = {}
        fm_match = re.search(r'^---\n(.*?)\n---', contenuto, re.DOTALL)
        if fm_match:
            for line in fm_match.group(1).split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    frontmatter[key.strip()] = val.strip()
        
        indice[f.stem] = {
            "percorso": str(f),
            "dominio": frontmatter.get("dominio", "Generale"),
            "tipo": frontmatter.get("tipo", "analisi"),
            "data": frontmatter.get("data_promozione", ""),
            "tags": frontmatter.get("tags", "").split(',')
        }
    
    write_file_safe(INDICE_PATH, json.dumps(indice, ensure_ascii=False, indent=2))
    return indice

def cerca_nel_wiki(domanda: str) -> list:
    """Cerca nel wiki usando l'indice leggero"""
    if not INDICE_PATH.exists():
        costruisci_indice()
    
    try:
        indice = json.loads(read_file_safe(INDICE_PATH))
    except:
        return []
    
    parole_domanda = set(domanda.lower().split())
    punteggi = []
    
    for titolo, info in indice.items():
        score = 0
        if info["dominio"].lower() in domanda.lower():
            score += 3
        for tag in info.get("tags", []):
            if tag.strip().lower() in parole_domanda:
                score += 2
        if titolo.lower() in domanda.lower():
            score += 1
        if score > 0:
            punteggi.append((score, titolo, info["percorso"]))
    
    punteggi.sort(reverse=True)
    return punteggi[:3]

# ============================================================
# RICERCA WEB (Brave Search API + DuckDuckGo fallback)
# ============================================================

def web_search_brave(query: str, num_results: int = 5) -> list:
    """Cerca online usando Brave Search API"""
    if not BRAVE_API_KEY:
        return web_search_duckduckgo(query, num_results)
    
    try:
        import requests
        
        url = "https://api.search.brave.com/res/v1/web/search"
        params = {"q": query, "count": num_results, "text_decorations": False}
        headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
        
        print(f"{Colors.DIM}🌐 Ricerca Brave: {query}{Colors.END}", flush=True)
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", "")
            })
        return results
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️ Errore Brave API: {e}. Fallback a DuckDuckGo.{Colors.END}")
        return web_search_duckduckgo(query, num_results)

def web_search_duckduckgo(query: str, num_results: int = 5) -> list:
    """Fallback: cerca online usando DuckDuckGo HTML"""
    import urllib.parse
    import urllib.request
    from html.parser import HTMLParser
    
    class DDGParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.results = []
            self.current = {}
            self.in_link = False
            self.in_title = False
            self.in_snippet = False
            self.link_url = ""
        
        def handle_starttag(self, tag, attrs):
            if tag == 'a' and not self.in_link:
                for attr, value in attrs:
                    if attr == 'href' and value.startswith('/url?q='):
                        self.in_link = True
                        url_match = re.search(r'/url\?q=([^&]+)', value)
                        if url_match:
                            self.link_url = urllib.parse.unquote(url_match.group(1))
                        break
            elif tag == 'h3' and self.in_link:
                self.in_title = True
            elif tag == 'div' and self.in_link:
                for attr, value in attrs:
                    if attr == 'class' and 's' in value:
                        self.in_snippet = True
                        break
        
        def handle_endtag(self, tag):
            if tag == 'a' and self.in_link:
                self.in_link = False
                if self.link_url and self.current.get('title'):
                    self.results.append({
                        'title': self.current.get('title', ''),
                        'url': self.link_url,
                        'snippet': self.current.get('snippet', '')
                    })
                    self.current = {}
                self.link_url = ""
            elif tag == 'h3':
                self.in_title = False
            elif tag == 'div':
                self.in_snippet = False
        
        def handle_data(self, data):
            if self.in_title:
                self.current['title'] = data.strip()
            elif self.in_snippet:
                if 'snippet' not in self.current:
                    self.current['snippet'] = data.strip()
                else:
                    self.current['snippet'] += ' ' + data.strip()
    
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print(f"{Colors.DIM}🌐 Ricerca DuckDuckGo (fallback): {query}{Colors.END}", flush=True)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            parser = DDGParser()
            parser.feed(html)
            return parser.results[:num_results]
            
    except Exception as e:
        print(f"{Colors.DIM}⚠️ Errore DuckDuckGo: {e}{Colors.END}", flush=True)
        return []

# ============================================================
# COMANDO /estrai
# ============================================================

def cmd_estrai():
    """Estrae evidenze marcate con >>---<< da un file in raw/"""
    
    md_files = [f for f in RAW.glob("*.md") if not f.name.startswith("estratto_")]
    
    if not md_files:
        print(f"{Colors.RED}❌ Nessun file .md trovato in raw/{Colors.END}")
        return
    
    print(f"\n{Colors.CYAN}📁 File disponibili per estrazione:{Colors.END}")
    for i, f in enumerate(md_files, 1):
        size = f.stat().st_size / 1024
        print(f"   {i}. {f.name} ({size:.1f} KB)")
    
    try:
        scelta = input(f"\n👉 Scegli il numero del file (0 per uscire): ").strip()
        if scelta == "0":
            return
        idx = int(scelta) - 1
        if idx < 0 or idx >= len(md_files):
            print(f"{Colors.RED}❌ Scelta non valida{Colors.END}")
            return
        src_file = md_files[idx]
    except ValueError:
        print(f"{Colors.RED}❌ Scelta non valida{Colors.END}")
        return
    
    contenuto = read_file_safe(src_file)
    evidenze = estrai_evidenze_marcate(contenuto)
    
    if not evidenze:
        print(f"{Colors.YELLOW}⚠️ Nessuna evidenza >>---<< trovata in {src_file.name}{Colors.END}")
        return
    
    print(f"{Colors.GREEN}✅ Trovate {len(evidenze)} evidenze{Colors.END}")
    
    output_name = f"estratto_{src_file.stem}.md"
    output_path = RAW / output_name
    
    md_content = f"""---
titolo: {src_file.stem} - Estratti
fonte: {src_file.name}
data_estrazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tipo: estratti
numero_estratti: {len(evidenze)}
---

# 📌 ESTRATTI SELEZIONATI

Fonte originale: `{src_file.name}`

"""
    for i, ev in enumerate(evidenze, 1):
        md_content += f"\n## Estratto {i}\n\n{ev}\n\n---\n"
    
    write_file_safe(output_path, md_content)
    print(f"{Colors.GREEN}✅ File estratto creato: {output_name}{Colors.END}")
    print(f"{Colors.CYAN}💡 Ora usa /analizza {output_name}{Colors.END}")

# ============================================================
# COMANDO /analizza (UNIFICATO)
# ============================================================

def cmd_ingest_diretto(src: Path, contenuto: str):
    """Ingest diretto per file piccoli (≤ CHUNK_SIZE)"""
    print(f"\n{Colors.GREEN}📥 Ingest diretto: {src.name}{Colors.END}")
    
    out_name = f"sdbx_{src.stem}_V1.md"
    out_file = SANDBOX / out_name
    
    msg = [{"role": "user", "content": f"""Analizza questa fonte e scrivi un riassunto ESAUSTIVO in italiano che segua fedelmente la struttura e il filo logico del documento originale.

Fonte: {src.name}
Contenuto: {contenuto[:15000]}

REGOLE FONDAMENTALI:

1. **Mantieni i termini tecnici originali** - Usa ESATTAMENTE le stesse parole dell'autore per concetti chiave.
2. **Segui la struttura originale** - Rispetta l'ordine dei paragrafi e delle sezioni.
3. **Flusso narrativo continuo** - Scrivi in paragrafi collegati.
4. **Preserva i dati quantitativi** - Tutti i numeri, percentuali, formule.
5. **Taglia il superfluo** - Elimina esempi ripetuti, mai definizioni essenziali.

STRUTTURA RICHIESTA NEL FILE:

# 📌 SINTESI ESAUSTIVA

(riassunto in paragrafi continui, seguendo l'ordine originale del documento)

---

## 🗨️ DISCUSSIONE SOCRATICA

(Lascia vuoto)

---

## ✅ IL MIO SAPERE

(Lascia vuoto)

IMPORTANTE: NON inserire evidenziazioni >...< nel testo. L'utente le aggiungerà manualmente dopo.
"""}]
    
    risposta = call_llm(build_system(), msg)
    full = f"""---
stato: BOZZA
lingua: italiano
fonte: {src.name}
data_ingest: {date.today()}
---

{risposta}
"""
    write_file_safe(out_file, full)
    print(f"{Colors.GREEN}✅ Sandbox creato: {out_name}{Colors.END}")
    print(f"{Colors.YELLOW}✏️ Ora aggiungi >argomento< nel file e usa /chat{Colors.END}")
    
    stato = load_stato()
    stato["fase"] = "INGEST_COMPLETATO"
    stato["file_corrente"] = out_name
    save_stato(stato)

def ingest_chunk(src: Path, contenuto: str, parole_totali: int):
    """Suddivide in chunk, ingerisce ogni chunk, crea sandbox"""
    print(f"\n{Colors.CYAN}📥 Ingest a chunk: {src.name}{Colors.END}")
    
    num_chunk = (parole_totali // CHUNK_SIZE) + (1 if parole_totali % CHUNK_SIZE > 0 else 0)
    print(f"   {num_chunk} chunk da ingerire\n")
    
    if src.parent != RAW:
        dest = RAW / src.name
        shutil.move(str(src), str(dest))
        print(f"{Colors.GREEN}✅ Spostato in raw/{src.name}{Colors.END}")
        src = dest
    
    parole_lista = contenuto.split()
    sandbox_creati = []
    
    for i in range(num_chunk):
        start = i * CHUNK_SIZE
        end = min((i + 1) * CHUNK_SIZE, parole_totali)
        chunk_testo = " ".join(parole_lista[start:end])
        
        chunk_filename = f"{src.stem}_chunk{i+1}.md"
        chunk_path = RAW / chunk_filename
        write_file_safe(chunk_path, chunk_testo)
        print(f"{Colors.DIM}📄 Chunk {i+1}/{num_chunk} salvato: {chunk_filename}{Colors.END}")
        
        print(f"{Colors.DIM}🤖 Ingest chunk {i+1}/{num_chunk}...{Colors.END}")
        
        out_name = f"sdbx_{src.stem}_chunk{i+1}_V1.md"
        out_file = SANDBOX / out_name
        
        msg = [{"role": "user", "content": f"""Analizza questa fonte e scrivi un riassunto ESAUSTIVO in italiano che segua fedelmente la struttura e il filo logico del documento originale.

Fonte: {chunk_filename}
Contenuto: {chunk_testo[:15000]}

REGOLE:
1. Mantieni i termini tecnici originali
2. Segui la struttura originale
3. Flusso narrativo continuo
4. Preserva i dati quantitativi

STRUTTURA:
# 📌 SINTESI ESAUSTIVA
(riassunto)

## 🗨️ DISCUSSIONE SOCRATICA
(Lascia vuoto)

## ✅ IL MIO SAPERE
(Lascia vuoto)
"""}]
        
        risposta = call_llm(build_system(), msg)
        full = f"""---
stato: BOZZA
lingua: italiano
fonte: {chunk_filename}
data_ingest: {date.today()}
---

{risposta}
"""
        write_file_safe(out_file, full)
        print(f"{Colors.GREEN}   ✅ Sandbox creato: {out_name}{Colors.END}")
        sandbox_creati.append(out_name)
        print()
        
        chunk_path.unlink()
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✅ INGEST COMPLETATO!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"   File originale: {src.name}")
    print(f"   Sandbox creati: {len(sandbox_creati)}")
    for sb in sandbox_creati:
        print(f"     - {sb}")
    print(f"\n{Colors.YELLOW}✏️ Ora aggiungi >argomento< nel file e usa /chat{Colors.END}")
    
    stato = load_stato()
    stato["fase"] = "INGEST_COMPLETATO"
    stato["file_corrente"] = sandbox_creati[0] if sandbox_creati else None
    save_stato(stato)

def cmd_analizza(filepath: str):
    """Analizza un file, mostra chunk, chiede conferma ed esegue ingest"""
    src = RAW / filepath
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in raw/: {filepath}{Colors.END}")
        return
    
    contenuto = read_file_safe(src)
    parole = len(contenuto.split())
    num_chunk = (parole // CHUNK_SIZE) + (1 if parole % CHUNK_SIZE > 0 else 0)
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📊 ANALISI FILE: {src.name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.CYAN}📏 Dimensioni:{Colors.END}")
    print(f"   - Parole: {parole}")
    print(f"   - Chunk necessari: {num_chunk}\n")
    
    if parole <= CHUNK_SIZE:
        print(f"{Colors.GREEN}✅ File ottimale ({parole} parole ≤ {CHUNK_SIZE}). Non è necessario suddividere in chunk.{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️ File lungo ({parole} parole > {CHUNK_SIZE}). Sarà suddiviso in {num_chunk} chunk da {CHUNK_SIZE} parole ciascuno.{Colors.END}")
    
    print(f"\n{Colors.YELLOW}📌 Procedere con l'ingest?{Colors.END}")
    scelta = input(f"{Colors.CYAN}👉 (s/n): {Colors.END}").lower()
    
    if scelta != 's':
        print(f"{Colors.RED}❌ Operazione annullata.{Colors.END}")
        return
    
    if parole <= CHUNK_SIZE:
        cmd_ingest_diretto(src, contenuto)
    else:
        ingest_chunk(src, contenuto, parole)

# ============================================================
# COMANDI ESISTENTI
# ============================================================

def cmd_list(cartella: str = None):
    cartelle = {"asset":ASSET,"clippings":CLIPPINGS,"backups":BACKUPS,"raw":RAW,"sandbox":SANDBOX,"wiki":WIKI}
    if cartella and cartella in cartelle:
        path = cartelle[cartella]
        files = list(path.glob("*"))
        print(f"\n{Colors.CYAN}📁 {cartella}/ ({len(files)} elementi){Colors.END}")
        for f in files[:20]:
            print(f"  - {f.name}")
    elif not cartella or cartella=="all":
        for name,path in cartelle.items():
            files = list(path.glob("*"))
            print(f"\n{Colors.CYAN}📁 {name}/ ({len(files)} elementi){Colors.END}")
            for f in files[:10]:
                print(f"  - {f.name}")
            if len(files)>10:
                print(f"  ... e altri {len(files)-10}")
    else:
        print(f"{Colors.RED}❌ Cartella sconosciuta{Colors.END}")
    print()

def cmd_chat(filearg: str = None):
    """Avvia chat su un file sandbox. Se filearg è specificato, lo imposta come corrente."""
    stato = load_stato()
    
    if filearg and filearg.strip():
        target_file = filearg.strip()
        if not target_file.endswith(".md"):
            target_file = target_file + ".md"
        if not target_file.startswith("sdbx_"):
            target_file = f"sdbx_{target_file}"
        sandbox_path = SANDBOX / target_file
        if not sandbox_path.exists():
            print(f"{Colors.RED}❌ File non trovato in sandbox/: {target_file}{Colors.END}")
            print(f"   File disponibili in sandbox/:")
            for f in SANDBOX.glob("sdbx_*_V1.md"):
                print(f"     - {f.name}")
            return
        
        checkpoint = carica_checkpoint()
        if checkpoint and checkpoint.get("file_corrente") == target_file:
            print(f"{Colors.YELLOW}⚠️ Trovato checkpoint per questo file. Riprendere?{Colors.END}")
            riprendi = input(f"{Colors.CYAN}👉 Riprendere? (s/n): {Colors.END}").lower()
            if riprendi == 's':
                stato.update(checkpoint.get("stato", {}))
                stato["file_corrente"] = target_file
                save_stato(stato)
                CHECKPOINT_PATH.unlink()
                print(f"{Colors.GREEN}✅ Stato ripristinato. Riprendo la discussione.{Colors.END}")
                idx = stato.get("indice", 0)
                evidenze = stato.get("evidenziazioni", [])
                if idx < len(evidenze):
                    print(f"\n{Colors.YELLOW}📌 Riprendo dall'evidenziazione {idx+1}/{len(evidenze)}:{Colors.END}")
                    print(f"   {Colors.CYAN}{evidenze[idx]}{Colors.END}")
                chat_libera()
                return
        
        if stato.get("file_corrente") == target_file and stato.get("fase") == "IN_DISCUSSIONE":
            print(f"{Colors.GREEN}✅ Ripresa discussione su: {target_file}{Colors.END}")
            idx = stato.get("indice", 0)
            evidenze = stato.get("evidenziazioni", [])
            totale = len(evidenze)
            
            if idx < totale:
                print(f"\n{Colors.YELLOW}📌 Riprendo dall'evidenziazione {idx+1}/{totale}:{Colors.END}")
                print(f"   {Colors.CYAN}{evidenze[idx]}{Colors.END}")
                
                if stato.get("domanda_corrente"):
                    print(f"\n{Colors.DIM}📝 Domanda in corso:{Colors.END}")
                    print_wrapped(stato["domanda_corrente"], color=Colors.CYAN, prefix="")
                
                storico_len = len(stato.get("storico_chat", []))
                if storico_len > 0:
                    print(f"\n{Colors.DIM}💬 Storico conversazione: {storico_len} messaggi{Colors.END}")
                print()
                chat_libera()
                return
            else:
                print(f"{Colors.YELLOW}⚠️ Tutte le {totale} evidenziazioni sono già state completate.{Colors.END}")
                print(f"   Usa /fine per generare il riassunto finale.{Colors.END}")
                print()
                return
        
        stato["file_corrente"] = target_file
        stato["fase"] = "INGEST_COMPLETATO"
        stato["evidenziazioni"] = []
        stato["conversazioni"] = []
        stato["indice"] = 0
        stato["domanda_corrente"] = None
        stato["evidenziazione_corrente"] = None
        stato["storico_chat"] = []
        save_stato(stato)
        print(f"{Colors.GREEN}✅ File attivo cambiato in: {target_file}{Colors.END}")
        print()
    
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file attivo. Usa /analizza prima o /chat sdbx_nome_V1.md{Colors.END}")
        return
    file_path = SANDBOX / stato["file_corrente"]
    if not file_path.exists():
        print(f"{Colors.RED}❌ File non trovato: {file_path}{Colors.END}")
        return
    
    contenuto = read_file_safe(file_path)
    evidenze = estrai_evidenziazioni(contenuto)
    if not evidenze:
        print(f"{Colors.YELLOW}⚠️ Nessuna evidenziazione >...< trovata in {stato['file_corrente']}{Colors.END}")
        print(f"   Aggiungi >argomento< nel file e riprova.")
        return
    print(f"{Colors.GREEN}🔍 Trovate {len(evidenze)} evidenziazioni in {stato['file_corrente']}:{Colors.END}")
    for e in evidenze:
        print(f"   • {e}")
    print()
    stato["fase"] = "IN_DISCUSSIONE"
    stato["evidenziazioni"] = evidenze
    stato["conversazioni"] = []
    stato["indice"] = 0
    save_stato(stato)
    avvia_evidenziazione()

def avvia_evidenziazione():
    stato = load_stato()
    idx = stato["indice"]
    if idx >= len(stato["evidenziazioni"]):
        print(f"\n{Colors.GREEN}✅ Tutte le evidenziazioni discusse!{Colors.END}")
        print(f"   Usa /fine per generare il riassunto finale (opzionale).")
        print()
        return
    ev = stato["evidenziazioni"][idx]
    print(f"\n{Colors.MAGENTA}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}💬 Evidenziazione {idx+1}/{len(stato['evidenziazioni'])}: {ev}{Colors.END}")
    print(f"{Colors.MAGENTA}{'='*60}{Colors.END}")
    print(f"{Colors.DIM}🤖 LLM genera domanda socratica...{Colors.END}")
    msg = [{"role":"user","content":f"Genera una domanda socratica su: {ev}\nSolo la domanda, senza preamboli."}]
    domanda = call_llm(build_system(), msg)
    print(f"\n{Colors.GREEN}📝 DOMANDA:{Colors.END}")
    print_wrapped(domanda, color=Colors.CYAN, prefix="")
    print(f"\n{Colors.DIM}Dialogo libero. Quando hai la risposta definitiva, usa:{Colors.END}")
    print(f"   {Colors.GREEN}/salva \"la tua risposta\"{Colors.END}")
    print(f"   {Colors.YELLOW}/salta{Colors.END} per saltare questa evidenziazione")
    print(f"   {Colors.YELLOW}/pausa{Colors.END} per salvare e uscire")
    stato["domanda_corrente"] = domanda
    stato["evidenziazione_corrente"] = ev
    stato["storico_chat"] = []
    save_stato(stato)
    chat_libera()

def chat_libera():
    stato = load_stato()
    ev = stato["evidenziazione_corrente"]
    domanda = stato["domanda_corrente"]
    while True:
        user_input = input(f"{Colors.GREEN}tu> {Colors.END}").strip()
        if not user_input:
            continue
        
        if user_input.lower() == "/salta":
            print(f"{Colors.YELLOW}⏭️ Evidenziazione saltata: {ev}{Colors.END}")
            stato["indice"] += 1
            stato["domanda_corrente"] = None
            stato["evidenziazione_corrente"] = None
            stato["storico_chat"] = []
            save_stato(stato)
            if stato["indice"] < len(stato["evidenziazioni"]):
                avvia_evidenziazione()
            else:
                print(f"\n{Colors.GREEN}🎉 Tutte le evidenziazioni discusse/saltate!{Colors.END}")
            return
        
        if user_input.lower() == "/pausa":
            salva_checkpoint("chat", stato.get("file_corrente"), {
                "indice": stato.get("indice", 0),
                "evidenziazioni": stato.get("evidenziazioni", []),
                "storico_chat": stato.get("storico_chat", []),
                "domanda_corrente": domanda,
                "evidenziazione_corrente": ev
            })
            print(f"{Colors.CYAN}⏸️ Sessione salvata. Usa /chat per riprendere.{Colors.END}")
            reset_stato()
            return
        
        if user_input.startswith("/salva"):
            match = re.search(r'/salva\s+"([^"]+)"', user_input)
            if not match:
                print(f"{Colors.RED}❌ Formato: /salva \"risposta\"{Colors.END}")
                continue
            risposta_finale = match.group(1)
            
            storico = stato.get("storico_chat", [])
            testo_conv = "\n".join(storico)
            
            if testo_conv.strip():
                prompt_riassunto = f"""Genera un riassunto NARRATIVO e TECNICO della seguente conversazione socratica.

EVIDENZIAZIONE: {ev}
DOMANDA INIZIALE: {domanda}

CONVERSAZIONE:
{testo_conv}

REGOLE:
1. Scrivi in forma narrativa (nessun punto elenco, nessuna lista)
2. Usa linguaggio tecnico preciso ma non divulgativo
3. Racconta: la posizione iniziale dell'utente, le obiezioni dell'LLM, l'evoluzione del dialogo, gli accordi/disaccordi, le domande aperte
4. Mantieni le sfumature e le tensioni emerse
5. Lunghezza proporzionale alla complessità della discussione

Rispondi SOLO con il riassunto, in italiano."""
                riassunto_conv = call_llm(build_system(), [{"role":"user","content":prompt_riassunto}])
            else:
                riassunto_conv = "Nessuna conversazione registrata."
            
            file_path = SANDBOX / stato["file_corrente"]
            contenuto_attuale = read_file_safe(file_path)
            nuovo_blocco = f"\n\n### Evidenziazione {stato['indice']+1}: {ev}\n"
            nuovo_blocco += f"**Domanda:** {domanda}\n\n"
            nuovo_blocco += f"**Conversazione:**\n```\n{testo_conv}\n```\n\n"
            nuovo_blocco += f"**Riassunto della conversazione:**\n\n{riassunto_conv}\n\n"
            nuovo_blocco += f"**Risposta finale:** {risposta_finale}\n\n---\n"
            
            if "## 🗨️ DISCUSSIONE SOCRATICA" in contenuto_attuale:
                if "## ✅ IL MIO SAPERE" in contenuto_attuale:
                    contenuto_attuale = contenuto_attuale.replace("## ✅ IL MIO SAPERE", nuovo_blocco + "\n## ✅ IL MIO SAPERE")
                else:
                    contenuto_attuale += nuovo_blocco
            else:
                contenuto_attuale += "\n## 🗨️ DISCUSSIONE SOCRATICA\n" + nuovo_blocco
            write_file_safe(file_path, contenuto_attuale)
            print(f"{Colors.GREEN}✅ Salvato nel file: domanda, conversazione, riassunto narrativo, risposta.{Colors.END}")
            print()
            stato["indice"] += 1
            stato["conversazioni"].append({})
            stato["domanda_corrente"] = None
            stato["evidenziazione_corrente"] = None
            stato["storico_chat"] = []
            save_stato(stato)
            if stato["indice"] < len(stato["evidenziazioni"]):
                avvia_evidenziazione()
            else:
                print(f"\n{Colors.GREEN}🎉 Tutte le evidenziazioni discusse e salvate!{Colors.END}")
                print(f"   Usa /fine per il riassunto finale unificato (opzionale).")
                print()
            return
        
        if user_input.lower() == "/archivia":
            cmd_archivia()
            return
        
        else:
            storico = stato.get("storico_chat", [])
            storico.append(f"Utente: {user_input}")
            
            msg_chat = [{"role":"user","content":f"""Evidenziazione: {ev}
Domanda iniziale: {domanda}
Storico:
{chr(10).join(storico[-15:])}
Ora l'utente dice: "{user_input}"

Rispondi in modo socratico, colloquiale ma rigoroso.
Se utile per la discussione, puoi cercare informazioni esterne (dati, esempi, controesempi) usando "🔍 RICERCA: [query]".
Mantieni un tono costruttivo e critico."""}]
            
            risp_llm = call_llm(build_system(enable_search=True), msg_chat)
            
            if "🔍 RICERCA:" in risp_llm:
                search_match = re.search(r'🔍 RICERCA:\s*([^\n]+)', risp_llm)
                if search_match:
                    query = search_match.group(1)
                    search_result = web_search_brave(query)
                    risp_llm = risp_llm.replace(f"🔍 RICERCA: {query}", f"[Ricerca: {query}]\n{search_result}")
            
            storico.append(f"LLM: {risp_llm}")
            stato["storico_chat"] = storico
            save_stato(stato)
            print_wrapped(risp_llm)
            print()

def cmd_fine():
    """Genera riassunto narrativo unificato di tutte le evidenziazioni"""
    stato = load_stato()
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file attivo{Colors.END}")
        return
    file_path = SANDBOX / stato["file_corrente"]
    if not file_path.exists():
        print(f"{Colors.RED}❌ File non trovato{Colors.END}")
        return
    contenuto = read_file_safe(file_path)
    if "## ✅ IL MIO SAPERE" in contenuto and "NON ANCORA GENERATO" not in contenuto:
        print(f"{Colors.YELLOW}⚠️ Il riassunto finale esiste già. Non lo rigenero.{Colors.END}")
        return
    
    riassunti_evidenze = []
    blocchi = re.findall(r'### Evidenziazione \d+: (.+?)\n\*\*Domanda:\*\* (.+?)\n\*\*Riassunto della conversazione:\*\*\n\n(.*?)\n\n\*\*Risposta finale:\*\* (.+?)(?:\n---|$)', contenuto, re.DOTALL)
    for ev, dom, riass, risp in blocchi:
        riassunti_evidenze.append(f"**{ev}**\nDomanda: {dom}\nDiscussione: {riass}\nRisposta: {risp}")
    
    if not riassunti_evidenze:
        print(f"{Colors.YELLOW}⚠️ Non trovate evidenziazioni salvate. Esegui prima /chat e /salva.{Colors.END}")
        return
    
    testo_riassunti = "\n\n---\n\n".join(riassunti_evidenze)
    
    prompt_unificato = f"""Genera un RIASSUNTO NARRATIVO UNIFICATO di TUTTE le seguenti evidenziazioni discusse.

EVIDENZIAZIONI:
{testo_riassunti}

REGOLE:
1. Scrivi in prima persona ("Ho compreso che...", "È emerso che...")
2. Forma narrativa fluida (nessun punto elenco, nessuna lista)
3. Usa linguaggio tecnico preciso ma non divulgativo
4. Trova un FILO LOGICO che collega le diverse evidenziazioni tra loro
5. Metti in luce le tensioni ricorrenti, le scoperte concettuali, i punti ancora aperti
6. Lunghezza proporzionale alla complessità (minimo 1000 caratteri)

Rispondi SOLO con il riassunto, in italiano."""
    
    riassunto_unificato = call_llm(build_system(), [{"role":"user","content":prompt_unificato}])
    
    if "## ✅ IL MIO SAPERE" in contenuto:
        contenuto = re.sub(r'## ✅ IL MIO SAPERE\n.*?(?=\n##|$)', f"## ✅ IL MIO SAPERE\n\n{riassunto_unificato}\n", contenuto, flags=re.DOTALL)
    else:
        contenuto += f"\n## ✅ IL MIO SAPERE\n\n{riassunto_unificato}\n"
    write_file_safe(file_path, contenuto)
    print(f"{Colors.GREEN}✅ Riassunto unificato aggiunto al file (IL MIO SAPERE).{Colors.END}")
    print()
    stato["fase"] = "COMPLETATA"
    save_stato(stato)

# ============================================================
# COMANDO /promuovi (NUOVA STRUTTURA WIKI)
# ============================================================

def cmd_promuovi(titolo: str):
    """Promuove il sandbox a pagina wiki con nuova struttura"""
    stato = load_stato()
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file sandbox attivo. Esegui /analizza prima.{Colors.END}")
        return
    sandbox_path = SANDBOX / stato["file_corrente"]
    if not sandbox_path.exists():
        print(f"{Colors.RED}❌ File sandbox non trovato: {sandbox_path}{Colors.END}")
        return

    contenuto_sandbox = read_file_safe(sandbox_path)

    sintesi_esaustiva = estrai_sezione(contenuto_sandbox, r'# 📌 SINTESI ESAUSTIVA')
    il_mio_sapere = estrai_sezione(contenuto_sandbox, r'## ✅ IL MIO SAPERE')

    if not il_mio_sapere:
        print(f"{Colors.YELLOW}⚠️ Sezione 'IL MIO SAPERE' non trovata. Esegui /fine prima di promuovere.{Colors.END}")
        print(f"   Generazione automatica in corso...")
        cmd_fine()
        contenuto_sandbox = read_file_safe(sandbox_path)
        il_mio_sapere = estrai_sezione(contenuto_sandbox, r'## ✅ IL MIO SAPERE')

    # Verifica se la pagina esiste già
    slug_base = titolo.lower().replace(" ", "_").replace("-", "_")
    wiki_path_base = WIKI / f"{slug_base}.md"
    
    titolo_finale = titolo
    wikilink_originale = None
    
    if wiki_path_base.exists():
        data_str = datetime.now().strftime("%Y-%m-%d")
        versioni_esistenti = list(WIKI.glob(f"{slug_base}_v*.md")) + list(WIKI.glob(f"{slug_base}_*.md"))
        if versioni_esistenti:
            numeri = []
            for v in versioni_esistenti:
                match = re.search(r'_v(\d+)', v.name)
                if match:
                    numeri.append(int(match.group(1)))
            prossimo_numero = max(numeri) + 1 if numeri else 2
            titolo_finale = f"{titolo} v{prossimo_numero}"
            slug_finale = f"{slug_base}_v{prossimo_numero}"
        else:
            titolo_finale = f"{titolo} ({data_str})"
            slug_finale = f"{slug_base}_{data_str.replace('-', '')}"
        
        wiki_path = WIKI / f"{slug_finale}.md"
        wikilink_originale = titolo
        
        print(f"{Colors.YELLOW}⚠️ Pagina '{titolo}' già esistente.{Colors.END}")
        print(f"   Creerò una nuova versione: '{titolo_finale}'")
        print(f"   Con wikilink alla versione originale: [[{titolo}]]")
        print()
    else:
        wiki_path = wiki_path_base
        titolo_finale = titolo

    # Proposta dominio/tipo
    print(f"{Colors.CYAN}🤖 Analizzo il contenuto per proporre dominio e tipo...{Colors.END}")
    domini_validi = ["Bitcoin", "Cultura", "Economia", "Generale", "Geopolitica", "Storia", "Tecnologia"]
    tipi_validi = ["appunti", "articolo", "paper", "podcast", "post"]
    
    prompt_frontmatter = f"""Leggi il seguente riassunto finale, poi proponi un dominio e un tipo per una pagina wiki.

DOMINI DISPONIBILI: {', '.join(domini_validi)}
TIPI DISPONIBILI: {', '.join(tipi_validi)}

RIASSUNTO FINALE:
{il_mio_sapere[:1500]}

Rispondi SOLO in formato JSON:
{{"dominio": "uno dei domini", "tipo": "uno dei tipi"}}
"""
    msg = [{"role": "user", "content": prompt_frontmatter}]
    proposta_json = call_llm(build_system(), msg)
    try:
        proposta = json.loads(proposta_json)
        dominio_proposto = proposta.get("dominio", "Generale")
        tipo_proposto = proposta.get("tipo", "articolo")
        if dominio_proposto not in domini_validi:
            dominio_proposto = "Generale"
        if tipo_proposto not in tipi_validi:
            tipo_proposto = "articolo"
    except:
        dominio_proposto = "Generale"
        tipo_proposto = "articolo"

    # Genera la struttura wiki dalla SINTESI ESAUSTIVA
    print(f"{Colors.CYAN}🤖 Generazione struttura wiki dalla SINTESI ESAUSTIVA...{Colors.END}")
    
    prompt_wiki = f"""Analizza la seguente SINTESI ESAUSTIVA e genera una struttura wiki.

SINTESI ESAUSTIVA:
{sintesi_esaustiva[:8000]}

Genera i seguenti elementi:

1. **TL;DR** - Una frase che riassume la tesi centrale

2. **Mappa concettuale** - In formato:
   - **Problema:** ...
   - **Argomento:** ...
   - **Conclusione:** ...
   - **Implicazione per te:** ...

3. **Punti chiave** - Massimo 7, ciascuno una frase, in formato numerato

4. **Citazioni rilevanti** - Se presenti nel testo, usa > "..."
   Se non ci sono citazioni esplicite, lascia vuoto

5. **Entità collegate** - Wiki-link [[...]] a concetti correlati esistenti (formato: [[X]], [[Y]])

6. **Concetti generati** - Wiki-link [[...]] a nuovi concetti emersi (formato: [[A]], [[B]])

Rispondi SOLO con i contenuti, senza commenti aggiuntivi, usando ESATTAMENTE i titoli delle sezioni come nell'esempio.
"""
    
    wiki_content_raw = call_llm(build_system(), [{"role": "user", "content": prompt_wiki}])
    
    # Estrai i componenti dalla risposta
    tl_dr = re.search(r'## TL;DR\n(.*?)(?=\n##|$)', wiki_content_raw, re.DOTALL)
    tl_dr = tl_dr.group(1).strip() if tl_dr else ""

    mappa = re.search(r'## Mappa concettuale\n(.*?)(?=\n##|$)', wiki_content_raw, re.DOTALL)
    mappa = mappa.group(1).strip() if mappa else ""

    punti_chiave = re.search(r'## Punti chiave\n(.*?)(?=\n##|$)', wiki_content_raw, re.DOTALL)
    punti_chiave = punti_chiave.group(1).strip() if punti_chiave else ""

    citazioni = re.search(r'## Citazioni rilevanti\n(.*?)(?=\n##|$)', wiki_content_raw, re.DOTALL)
    citazioni = citazioni.group(1).strip() if citazioni else ""

    entita_collegate = re.search(r'## Entità collegate\n(.*?)(?=\n##|$)', wiki_content_raw, re.DOTALL)
    entita_collegate = entita_collegate.group(1).strip() if entita_collegate else ""

    concetti_generati = re.search(r'## Concetti generati\n(.*?)(?=\n##|$)', wiki_content_raw, re.DOTALL)
    concetti_generati = concetti_generati.group(1).strip() if concetti_generati else ""

    # Menu interattivo per dominio e tipo
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📝 CREAZIONE NUOVA PAGINA WIKI{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    print(f"{Colors.GREEN}Titolo:{Colors.END} {titolo_finale}")
    if wikilink_originale:
        print(f"{Colors.CYAN}🔗 Link alla versione originale: [[{wikilink_originale}]]{Colors.END}")

    print(f"\n{Colors.YELLOW}📌 Scegli il DOMINIO:{Colors.END}")
    for i, d in enumerate(domini_validi, 1):
        default = " (proposto)" if d == dominio_proposto else ""
        print(f"  {i}. {d}{default}")
    print(f"  {len(domini_validi)+1}. Inserisci manualmente")
    scelta_dom = input(f"{Colors.CYAN}👉 Numero (invio per {dominio_proposto}): {Colors.END}").strip()
    if scelta_dom == "":
        dominio_finale = dominio_proposto
    elif scelta_dom.isdigit() and 1 <= int(scelta_dom) <= len(domini_validi):
        dominio_finale = domini_validi[int(scelta_dom)-1]
    elif scelta_dom == str(len(domini_validi)+1):
        dominio_finale = input(f"{Colors.CYAN}Dominio: {Colors.END}").strip() or dominio_proposto
    else:
        dominio_finale = dominio_proposto

    print(f"\n{Colors.YELLOW}📌 Scegli il TIPO:{Colors.END}")
    for i, t in enumerate(tipi_validi, 1):
        default = " (proposto)" if t == tipo_proposto else ""
        print(f"  {i}. {t}{default}")
    print(f"  {len(tipi_validi)+1}. Inserisci manualmente")
    scelta_tipo = input(f"{Colors.CYAN}👉 Numero (invio per {tipo_proposto}): {Colors.END}").strip()
    if scelta_tipo == "":
        tipo_finale = tipo_proposto
    elif scelta_tipo.isdigit() and 1 <= int(scelta_tipo) <= len(tipi_validi):
        tipo_finale = tipi_validi[int(scelta_tipo)-1]
    elif scelta_tipo == str(len(tipi_validi)+1):
        tipo_finale = input(f"{Colors.CYAN}Tipo: {Colors.END}").strip() or tipo_proposto
    else:
        tipo_finale = tipo_proposto

    # Fonti
    fonti_match = re.search(r'fonte: (.*?)(?:\n|$)', contenuto_sandbox)
    fonti = [f.strip() for f in fonti_match.group(1).split(',')] if fonti_match else []
    fonti_str = ", ".join([f"[[{f}]]" for f in fonti])
    
    # Numero di cicli SPB
    evidenze_risposte = re.findall(r'### Evidenziazione \d+:', contenuto_sandbox)
    cicli_spb = len(evidenze_risposte)

    # Costruisci il contenuto del wiki
    wiki_content = f"""---
titolo: {titolo_finale}
dominio: {dominio_finale}
tipo: {tipo_finale}
stato: attivo
data_promozione: {date.today()}
cicli_spb: {cicli_spb}
fonti: {fonti_str}
---

## TL;DR

{tl_dr}

## Mappa concettuale

{mappa}

## Punti chiave

{punti_chiave}

## Sviluppo analitico

{sintesi_esaustiva}

## Citazioni rilevanti

{citazioni}

## Entità collegate

{entita_collegate}

## Concetti generati

{concetti_generati}

---

## ✅ IL MIO SAPERE

{il_mio_sapere}
"""

    # Salva wiki
    slug_finale = titolo_finale.lower().replace(" ", "_").replace("-", "_")
    wiki_path = WIKI / f"{slug_finale}.md"
    write_file_safe(wiki_path, wiki_content)

    with INDEX.open("a", encoding='utf-8') as f:
        f.write(f"| [[{titolo_finale}]] | {dominio_finale} | {tipo_finale} | {date.today()} |\n")
    with LOG.open("a", encoding='utf-8') as f:
        f.write(f"\n## [{date.today()}] promuovi | {titolo_finale}\n")
        f.write(f"- File sandbox: {stato['file_corrente']}\n")
        f.write(f"- Cicli SPB: {cicli_spb}\n")
        f.write(f"- Pagina wiki: {wiki_path.name}\n")
        if wikilink_originale:
            f.write(f"- Wikilink a versione originale: [[{wikilink_originale}]]\n")

    print(f"\n{Colors.GREEN}✅ Pagina wiki creata: {wiki_path}{Colors.END}")
    print(f"{Colors.GREEN}✅ Indice e log aggiornati.{Colors.END}")
    
    # Archivia il sandbox
    if sandbox_path.exists():
        arch_path = ARCHIVIATI / sandbox_path.name
        shutil.move(str(sandbox_path), str(arch_path))
        print(f"{Colors.YELLOW}🗂️ Sandbox archiviato in: {arch_path}{Colors.END}")
    
    print()
    reset_stato()
    costruisci_indice()

# ============================================================
# ALTRI COMANDI
# ============================================================

def cmd_riprendi(filename: str):
    """Ripristina un file sandbox archiviato per riprenderne la discussione"""
    if not filename.endswith(".md"):
        filename = filename + ".md"
    if not filename.startswith("sdbx_"):
        filename = f"sdbx_{filename}"
    
    src = ARCHIVIATI / filename
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in archiviati/: {filename}{Colors.END}")
        print(f"   File disponibili:")
        for f in ARCHIVIATI.glob("sdbx_*_V1.md"):
            print(f"     - {f.name}")
        return
    
    dest = SANDBOX / src.name
    shutil.copy2(str(src), str(dest))
    print(f"{Colors.GREEN}✅ File ripristinato: {dest}{Colors.END}")
    
    stato = load_stato()
    stato["file_corrente"] = src.name
    stato["fase"] = "INGEST_COMPLETATO"
    stato["evidenziazioni"] = []
    stato["conversazioni"] = []
    stato["indice"] = 0
    stato["domanda_corrente"] = None
    stato["evidenziazione_corrente"] = None
    stato["storico_chat"] = []
    save_stato(stato)
    
    print(f"{Colors.CYAN}💡 Ora usa /chat per continuare la discussione.{Colors.END}")
    print()

def cmd_archivia():
    """Archivia la discussione corrente"""
    stato = load_stato()
    if stato.get("file_corrente"):
        src = SANDBOX / stato["file_corrente"]
        if src.exists():
            arch = ARCHIVIATI / f"archiviato_{src.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            shutil.move(str(src), str(arch))
            print(f"{Colors.YELLOW}🗂️ Archiviato: {arch}{Colors.END}")
    reset_stato()
    print(f"{Colors.GREEN}✅ Discussione archiviata{Colors.END}")
    print()

def cmd_query(domanda: str):
    """Interroga il wiki usando indice leggero + ricerca web con marcatura fonti"""
    
    pagine_rilevanti = cerca_nel_wiki(domanda)
    
    risposta_wiki = None
    fonti_wiki = []
    
    if pagine_rilevanti:
        ctx = ""
        for score, titolo, percorso in pagine_rilevanti:
            contenuto = read_file_safe(Path(percorso))
            sintesi = estrai_sezione(contenuto, r'## Sviluppo analitico')
            mio_sapere = estrai_sezione(contenuto, r'## ✅ IL MIO SAPERE')
            ctx += f"### [[{titolo}]]\n"
            if sintesi:
                ctx += f"SINTESI: {sintesi[:500]}\n"
            if mio_sapere:
                ctx += f"CONCLUSIONI: {mio_sapere[:300]}\n"
            ctx += "\n"
            fonti_wiki.append(titolo)
        
        msg = [{"role":"user","content":f"Domanda: {domanda}\n\nPagine wiki rilevanti:\n{ctx}\nRispondi in italiano. Se le info sono insufficienti, scrivi 'INFO_INSUFFICIENTI'."}]
        risposta_wiki = call_llm(build_system(), msg)
    
    if risposta_wiki and "INFO_INSUFFICIENTI" not in risposta_wiki and len(risposta_wiki) > 150:
        for fonte in fonti_wiki:
            risposta_wiki = risposta_wiki.replace(f"[[{fonte}]]", f"[WIKI] [[{fonte}]]")
        print(f"\n{Colors.CYAN}[WIKI] {Colors.END}")
        print_wrapped(risposta_wiki)
        print()
        return
    
    print(f"\n{Colors.DIM}⚠️ Informazioni insufficienti nel wiki. Ricerca online in corso...{Colors.END}\n")
    
    risultati_web = web_search_brave(domanda, num_results=5)
    
    if not risultati_web:
        if risposta_wiki:
            print_wrapped(f"[WIKI] {risposta_wiki}")
        else:
            print(f"{Colors.YELLOW}⚠️ Nessun risultato trovato.{Colors.END}")
        print()
        return
    
    web_ctx = ""
    for i, r in enumerate(risultati_web, 1):
        web_ctx += f"### Risultato {i}: {r['title']}\n"
        web_ctx += f"**Fonte:** {r['url']}\n"
        web_ctx += f"**Contenuto:** {r['snippet']}\n\n"
    
    msg_web = [{"role":"user","content":f"""Domanda: {domanda}

FONTI WIKI (validate SPB):
{chr(10).join([f"- [[{f}]]" for f in fonti_wiki]) if fonti_wiki else '(nessuna)'}

RISULTATI RICERCA WEB (non validate):
{web_ctx}

Sintetizza una risposta. Marca ESPLICITAMENTE ogni affermazione con:
- [WIKI] se proviene dalle fonti wiki validate
- [WEB] se proviene dalla ricerca online (e cita la fonte)

Rispondi in italiano."""}]
    
    risposta_completa = call_llm(build_system(), msg_web)
    
    print(f"\n{Colors.CYAN}🌐 RISPOSTA (WIKI + WEB):{Colors.END}")
    print_wrapped(risposta_completa)
    print()
    
    update_log(f"query | {domanda[:50]}...", f"- Wiki: {len(fonti_wiki)} fonti\n- Web: {len(risultati_web)} risultati")

def cmd_lint():
    print(f"\n{Colors.CYAN}🔬 LINT DEL WIKI{Colors.END}")
    wiki_pages = [f.stem for f in WIKI.glob("*.md") if f.name not in ["index.md","log.md", ".indice_wiki.json"]]
    backlinks = {}
    for f in WIKI.glob("*.md"):
        if f.name in ["index.md", "log.md", ".indice_wiki.json"]:
            continue
        cont = read_file_safe(f)
        for p in wiki_pages:
            if f"[[{p}]]" in cont:
                backlinks[p] = backlinks.get(p,0)+1
    orphans = [p for p in wiki_pages if backlinks.get(p,0)==0]
    if orphans:
        print(f"{Colors.RED}🔴 Pagine orfane: {len(orphans)}{Colors.END}")
    else:
        print(f"{Colors.GREEN}✅ Nessuna orfana{Colors.END}")
    old = []
    for f in SANDBOX.glob("sdbx_*.md"):
        age = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        if age>30:
            old.append((f.name,age))
    if old:
        print(f"{Colors.YELLOW}🟡 Sandbox attivi da >30gg: {len(old)}{Colors.END}")
    else:
        print(f"{Colors.GREEN}✅ Nessun sandbox vecchio{Colors.END}")
    print()

def cmd_backup():
    print(f"{Colors.CYAN}💾 Backup...{Colors.END}")
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bkp = BACKUPS / f"vault_backup_{ts}.zip"
    with zipfile.ZipFile(bkp, 'w', zipfile.ZIP_DEFLATED) as z:
        for d in [CLIPPINGS, VAULT, ASSET]:
            if d.exists():
                for f in d.rglob("*"):
                    if f.is_file():
                        z.write(f, f.relative_to(Path.cwd()))
        for f in [AGENT_MD, Path("analisi_ingest.py"), Path(".env")]:
            if f.exists():
                z.write(f)
    print(f"{Colors.GREEN}✅ Backup: {bkp}{Colors.END}")
    print()

def cmd_stato():
    stato = load_stato()
    print(f"\n{Colors.BLUE}📊 STATO{Colors.END}")
    print(f"  Modello attivo: {Colors.CYAN}{CURRENT_MODEL}{Colors.END}")
    print(f"  Fase: {stato.get('fase','nessuna')}")
    print(f"  File: {stato.get('file_corrente','nessuno')}")
    print(f"  Evidenziazioni: {len(stato.get('evidenziazioni',[]))} trovate, indice {stato.get('indice',0)}")
    print(f"  raw/: {len(list(RAW.glob('*')))} | wiki/: {len(list(WIKI.glob('*.md')))}")
    print(f"  sandbox/ (attivi): {len(list(SANDBOX.glob('sdbx_*.md')))}")
    print(f"  sandbox/archiviati/: {len(list(ARCHIVIATI.glob('*')))}")
    print()

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def print_banner():
    modello_nome = "V4 Pro"
    print(f"""
{Colors.BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║     SISTEMA SOCRATES-PLATO-BAYES - Versione Definitiva       ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}Modello attivo:{Colors.END} {Colors.CYAN}{modello_nome} ({CURRENT_MODEL}){Colors.END}
{Colors.YELLOW}Soglia chunk:{Colors.END} {Colors.CYAN}{CHUNK_SIZE} parole{Colors.END}
""")

    # File in raw/
    raw_files = list(RAW.glob("*.md"))
    print(f"{Colors.CYAN}📁 File disponibili in raw/ (pronti per estrazione/ingest):{Colors.END}")
    if raw_files:
        for i, f in enumerate(raw_files, 1):
            size = f.stat().st_size / 1024
            
            if f.name.startswith("estratto_"):
                icon = "📥"
            else:
                contenuto = read_file_safe(f)
                if '>>---<<' in contenuto:
                    icon = "✂️"
                else:
                    icon = "📄"
            
            print(f"   {i:2}. {icon} {f.name:<50} ({size:.1f} KB)")
        
        if len(raw_files) > 10:
            print(f"   ... e altri {len(raw_files)-10} file")
    else:
        print(f"   {Colors.DIM}(vuoto - aggiungi file markdown){Colors.END}")
    
    # Sandbox attivi
    sandbox_files = list(SANDBOX.glob("sdbx_*_V1.md"))
    print(f"\n{Colors.YELLOW}💬 Sandbox attivi in sandbox/ (pronti per /chat):{Colors.END}")
    if sandbox_files:
        for i, f in enumerate(sandbox_files[:10], 1):
            size = f.stat().st_size / 1024
            display_name = f.name.replace("sdbx_", "").replace("_V1.md", "")
            print(f"   {i}. {display_name:<50} ({size:.1f} KB)")
        if len(sandbox_files) > 10:
            print(f"   ... e altri {len(sandbox_files)-10} sandbox")
    else:
        print(f"   {Colors.DIM}(vuoto - usa /analizza per creare sandbox){Colors.END}")

    # Menu comandi
    print(f"""
{Colors.BLUE}{'='*60}{Colors.END}
{Colors.BOLD}📋 COMANDI DISPONIBILI:{Colors.END}
{Colors.BLUE}{'='*60}{Colors.END}

{Colors.MAGENTA}✂️  ESTRAZIONE{Colors.END}
  /estrai                         Estrae evidenze >>---<< e crea estratto_nome.md

{Colors.GREEN}📥 ANALISI E INGEST{Colors.END}
  /analizza <file>                Analizza dimensioni, mostra chunk necessari,
                                  chiede conferma ed esegue ingest

{Colors.YELLOW}💬 DISCUSSIONE SOCRATICA{Colors.END}
  /chat [file]                    Avvia/riprendi discussione
  /salva "risposta"               Salva evidenziazione (riassunto narrativo)
  /fine                           Genera riassunto unificato (IL MIO SAPERE)

{Colors.CYAN}📚 PROMOZIONE E CONSULTAZIONE{Colors.END}
  /promuovi "Titolo"              Crea pagina wiki
  /query "domanda"                Interroga wiki + ricerca web

{Colors.BLUE}🔧 UTILITY{Colors.END}
  /list [cartella]                Mostra file (raw, sandbox, wiki, clippings)
  /riprendi <file>                Ripristina sandbox archiviato
  /archivia                       Archivia discussione corrente
  /lint                           Health-check
  /backup                         Backup completo
  /stato                          Mostra stato
  /clear                          Pulisce schermo
  /exit                           Esci

{Colors.BLUE}💡 Suggerimenti:{Colors.END}
  • usa >>---<< per estrarre argomenti
  • usa >...< per evidenziare argomenti
  • usa TAB per autocompletare nomi file
  • In /chat: usa /salta (salta evidenziazione), /pausa (salva sessione)
""")

# ============================================================
# AUTOCOMPLETAMENTO
# ============================================================

class SpbCompleter:
    def __init__(self):
        self.commands = ["/estrai", "/list", "/analizza", "/chat", "/salva", "/fine", "/promuovi", "/riprendi", "/archivia", "/query", "/lint", "/backup", "/stato", "/clear", "/exit"]
        self.list_targets = ["asset", "clippings", "backups", "raw", "sandbox", "wiki", "all"]

    def get_matches(self, text, state):
        if readline is None:
            return None
        try:
            line = readline.get_line_buffer().strip()
        except Exception:
            return None
        parts = line.split()
        if not parts:
            return None
        cmd = parts[0].lower()
        
        if len(parts) == 1 and not line.endswith(' '):
            matches = [c for c in self.commands if c.startswith(text)]
            return matches[state] if state < len(matches) else None
        
        if cmd == "/list" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            matches = [t for t in self.list_targets if t.startswith(prefix)]
            return matches[state] if state < len(matches) else None
        
        if cmd == "/analizza" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in RAW.glob("*.md") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        
        if cmd == "/chat" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in SANDBOX.glob("sdbx_*_V1.md") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        
        if cmd == "/riprendi" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in ARCHIVIATI.glob("sdbx_*_V1.md") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        
        return None

# ============================================================
# MAIN
# ============================================================

def main():
    init_vault()
    ripulisci_file_orfani()
    clear_screen()
    print_banner()

    costruisci_indice()

    if readline is not None:
        completer = SpbCompleter()
        readline.set_completer(completer.get_matches)
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims(' \t\n;')
    else:
        print(f"{Colors.YELLOW}⚠️ readline non disponibile, autocompletamento disabilitato{Colors.END}")

    checkpoint = carica_checkpoint()
    if checkpoint:
        print(f"{Colors.YELLOW}⚠️ È presente una sessione interrotta: {checkpoint.get('operazione')}{Colors.END}")
        riprendi = input(f"{Colors.CYAN}👉 Riprendere? (s/n): {Colors.END}").lower()
        if riprendi == 's':
            stato = load_stato()
            stato.update(checkpoint.get("stato", {}))
            save_stato(stato)
            print(f"{Colors.GREEN}✅ Stato ripristinato. Usa /chat per continuare.{Colors.END}")
        CHECKPOINT_PATH.unlink()

    while True:
        try:
            inp = input(f"{Colors.GREEN}spb>{Colors.END} ").strip()
            if not inp:
                continue
            if inp.lower() in ["/exit","exit","/quit"]:
                break
            if inp == "/clear":
                clear_screen()
                print_banner()
                continue
            parts = inp.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts)>1 else ""

            if cmd == "/estrai":
                cmd_estrai()
            elif cmd == "/list":
                cmd_list(arg if arg else None)
            elif cmd == "/analizza":
                if arg:
                    cmd_analizza(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file: /analizza documento.md{Colors.END}")
            elif cmd == "/chat":
                cmd_chat(arg if arg else None)
            elif cmd == "/salva":
                print(f"{Colors.YELLOW}⚠️ Usa /salva durante la chat (dopo /chat){Colors.END}")
            elif cmd == "/fine":
                cmd_fine()
            elif cmd == "/promuovi":
                if arg:
                    cmd_promuovi(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il titolo: /promuovi \"Titolo della pagina\"{Colors.END}")
            elif cmd == "/riprendi":
                if arg:
                    cmd_riprendi(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file da riprendere (TAB per autocompletare){Colors.END}")
            elif cmd == "/archivia":
                cmd_archivia()
            elif cmd == "/query":
                if arg:
                    cmd_query(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica la domanda: /query \"testo\"{Colors.END}")
            elif cmd == "/lint":
                cmd_lint()
            elif cmd == "/backup":
                cmd_backup()
            elif cmd == "/stato":
                cmd_stato()
            elif cmd in ["/help","/?"]:
                print_banner()
            else:
                print(f"{Colors.RED}❌ Comando sconosciuto. Usa TAB per autocompletare.{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.BLUE}👋 Bye{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ {e}{Colors.END}")

if __name__ == "__main__":
    main()