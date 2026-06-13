#!/usr/bin/env python3
"""
wiki.py — Sistema Socrates–Plato–Bayes (SPB) - Versione Definitiva
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
GLOSSARIO_PATH = RAW / "glossario.json"
CHECKPOINT_PATH = SANDBOX / ".checkpoint.json"
INDICE_PATH = WIKI / ".indice_wiki.json"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print(f"{Colors.RED}❌ ERRORE: DEEPSEEK_API_KEY non trovata{Colors.END}")
    sys.exit(1)

CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Modelli DeepSeek V4
DEEPSEEK_FLASH = "deepseek-v4-flash"
DEEPSEEK_PRO = "deepseek-v4-pro"

# Modello predefinito (cambia qui tra FLASH e PRO)
CURRENT_MODEL = DEEPSEEK_PRO

# Dimensione chunk per traduzione e ingest
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
    """Chiamata LLM con supporto opzionale per ricerca esterna e selezione modello"""
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
    return re.findall(r'>([^<]+)<', contenuto)

def estrai_sezione(contenuto: str, pattern: str) -> str:
    """Estrae una sezione dal markdown usando un pattern regex"""
    match = re.search(pattern + r'\n\n(.*?)(?=\n##|\n---|\Z)', contenuto, re.DOTALL)
    return match.group(1).strip() if match else ""

# ============================================================
# GLOSSARIO TERMINOLOGICO
# ============================================================

def carica_glossario() -> dict:
    """Carica il glossario terminologico"""
    if GLOSSARIO_PATH.exists():
        try:
            return json.loads(read_file_safe(GLOSSARIO_PATH))
        except:
            return {}
    return {}

def salva_glossario(glossario: dict):
    """Salva il glossario terminologico"""
    write_file_safe(GLOSSARIO_PATH, json.dumps(glossario, ensure_ascii=False, indent=2))

def aggiorna_glossario_da_chunk(chunk_testo: str, traduzione: str):
    """Aggiorna il glossario con termini rilevanti dal chunk tradotto"""
    glossario = carica_glossario()
    # Estrai termini in maiuscolo o tra asterischi come possibili termini tecnici
    termini_originali = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b|`([^`]+)`|\*([^*]+)\*', chunk_testo)
    for t in termini_originali:
        termine = t[0] or t[1] or t[2]
        if termine and len(termine) > 3 and termine.lower() not in glossario:
            glossario[termine.lower()] = {
                "originale": termine,
                "traduzione": "",
                "ultimo_aggiornamento": datetime.now().isoformat()
            }
    salva_glossario(glossario)

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
    # Cerca chunk temporanei in raw/ senza sandbox corrispondente
    for chunk_file in RAW.glob("*_chunk*.md"):
        sb_name = chunk_file.name.replace(".md", "_V1.md")
        sb_name = f"sdbx_{sb_name}"
        if not (SANDBOX / sb_name).exists():
            print(f"{Colors.DIM}🧹 Rimozione file orfano: {chunk_file.name}{Colors.END}")
            chunk_file.unlink()
    
    # Pulisci checkpoint vecchi (>24 ore)
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
        
        # Estrai frontmatter
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
        # Match con dominio
        if info["dominio"].lower() in domanda.lower():
            score += 3
        # Match con tags
        for tag in info.get("tags", []):
            if tag.strip().lower() in parole_domanda:
                score += 2
        # Match con titolo
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
# COMANDI: ANALIZZA
# ============================================================

def cmd_analizza(filepath: str):
    """Analizza un file e propone opzioni: 1. Ingest, 2. Traduci, 3. Annulla"""
    src = CLIPPINGS / filepath
    if not src.exists():
        src = RAW / filepath
        if not src.exists():
            print(f"{Colors.RED}❌ File non trovato in clippings/ o raw/: {filepath}{Colors.END}")
            sys.stdout.flush()
            return
    
    contenuto = read_file_safe(src)
    caratteri = len(contenuto)
    parole = len(contenuto.split())
    righe = len(contenuto.splitlines())
    pagine = round(parole / 300, 1)
    num_chunk = (parole // CHUNK_SIZE) + (1 if parole % CHUNK_SIZE > 0 else 0)
    
    if parole <= CHUNK_SIZE:
        strategia = "OTTIMALE"
        colore = Colors.GREEN
        suggerimento = f"Il file è ottimale (≤{CHUNK_SIZE} parole)."
    elif parole <= 5000:
        strategia = "LIMITE"
        colore = Colors.YELLOW
        suggerimento = f"Il file è lungo ({parole} parole). Consiglio di suddividerlo in chunk da {CHUNK_SIZE} parole."
    else:
        strategia = "TROPPO LUNGO"
        colore = Colors.RED
        suggerimento = f"Il file è troppo lungo ({parole} parole). Deve essere suddiviso in {num_chunk} chunk da {CHUNK_SIZE} parole."
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📊 ANALISI FILE: {src.name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.CYAN}📏 Dimensioni:{Colors.END}")
    print(f"   - Parole: {parole}")
    print(f"   - Caratteri: {caratteri}")
    print(f"   - Righe: {righe}")
    print(f"   - Pagine stimate: {pagine}\n")
    
    print(f"{Colors.CYAN}📋 Valutazione:{Colors.END}")
    print(f"   - Soglia SPB: {CHUNK_SIZE} parole")
    print(f"   - Chunk necessari: {num_chunk}")
    print(f"   - Stato: {colore}{strategia}{Colors.END}")
    print(f"   - {suggerimento}\n")
    
    print(f"{Colors.YELLOW}📌 Opzioni disponibili:{Colors.END}")
    print(f"   1. Ingest (suddivide in chunk, ingerisce ogni chunk, crea sandbox)")
    print(f"   2. Traduci (traduce in italiano, raggruppa in raw/nome_it.md, poi ingest a chunk)")
    print(f"   3. Annulla")
    
    scelta = input(f"\n{Colors.CYAN}👉 Scegli opzione (1-3): {Colors.END}").strip()
    
    if scelta == "1":
        ingest_chunk(src, contenuto, parole)
    elif scelta == "2":
        traduci_ingest_chunk(src, contenuto, parole)
    else:
        print(f"{Colors.RED}❌ Operazione annullata.{Colors.END}")
    
    sys.stdout.flush()

def ingest_chunk(src: Path, contenuto: str, parole_totali: int):
    """Opzione 1: Suddivide in chunk, ingerisce ogni chunk, crea sandbox"""
    print(f"\n{Colors.CYAN}📥 Ingest a chunk di {src.name}{Colors.END}")
    
    num_chunk = (parole_totali // CHUNK_SIZE) + (1 if parole_totali % CHUNK_SIZE > 0 else 0)
    print(f"   {num_chunk} chunk da ingerire separatamente\n")
    
    # Assicura che il file sia in raw/
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
        cmd_ingest(chunk_filename)
        sandbox_creati.append(f"sdbx_{src.stem}_chunk{i+1}_V1.md")
        print()
    
    # Pulisci i file chunk temporanei
    for i in range(num_chunk):
        chunk_file = RAW / f"{src.stem}_chunk{i+1}.md"
        if chunk_file.exists():
            chunk_file.unlink()
    
    print(f"\n{Colors.GREEN}✅ Ingest completato. {num_chunk} sandbox creati:{Colors.END}")
    for sb in sandbox_creati:
        print(f"   - {sb}")
    print(f"\n{Colors.CYAN}💡 Ora puoi usare /chat su ogni file sandbox.{Colors.END}")
    update_log("ingest_chunk", f"File: {src.name}\nChunk: {num_chunk}\nSandbox: {', '.join(sandbox_creati)}")

def traduci_ingest_chunk(src: Path, contenuto: str, parole_totali: int):
    """Opzione 2: Traduce, raggruppa in raw/nome_it.md, poi ingest a chunk"""
    print(f"\n{Colors.CYAN}📖 Traduzione di {src.name}{Colors.END}")
    
    # Carica glossario per coerenza terminologica
    glossario = carica_glossario()
    glossario_prompt = ""
    if glossario:
        glossario_prompt = "\n\nGLOSSARIO TERMINI TECNICI (da mantenere coerenti):\n"
        for termine, info in glossario.items():
            if info.get("traduzione"):
                glossario_prompt += f"- {info.get('originale', termine)} → {info['traduzione']}\n"
            else:
                glossario_prompt += f"- {termine} → (da tradurre coerentemente)\n"
    
    num_chunk = (parole_totali // CHUNK_SIZE) + (1 if parole_totali % CHUNK_SIZE > 0 else 0)
    print(f"   Parole totali: {parole_totali}")
    print(f"   Chunk da tradurre: {num_chunk}\n")
    
    conferma = input(f"{Colors.YELLOW}✅ Procedere con la traduzione? (s/n): {Colors.END}").lower()
    if conferma != 's':
        print(f"{Colors.RED}❌ Operazione annullata.{Colors.END}")
        return
    
    parole_lista = contenuto.split()
    chunk_traduzioni = []
    
    for i in range(num_chunk):
        start = i * CHUNK_SIZE
        end = min((i + 1) * CHUNK_SIZE, parole_totali)
        chunk_testo = " ".join(parole_lista[start:end])
        
        print(f"{Colors.DIM}🤖 Traduzione chunk {i+1}/{num_chunk}...{Colors.END}")
        
        prompt = f"""Traduci il seguente testo dall'inglese all'italiano.
{glossario_prompt}

REGOLE:
1. Mantieni la struttura markdown
2. Preserva i wikilink [[...]] e i link esterni
3. Traduci in modo naturale
4. Mantieni i termini tecnici in inglese se consolidati
5. Usa il glossario fornito per mantenere coerenza terminologica

TESTO:
{chunk_testo[:8000]}

Rispondi SOLO con il testo tradotto."""
        
        msg = [{"role": "user", "content": prompt}]
        tradotto = call_llm(build_system(), msg, model=DEEPSEEK_FLASH)
        chunk_traduzioni.append(tradotto)
        
        # Aggiorna glossario
        aggiorna_glossario_da_chunk(chunk_testo, tradotto)
        print(f"{Colors.GREEN}   ✅ Chunk {i+1}/{num_chunk} tradotto{Colors.END}")
    
    # Raggruppa i chunk tradotti in un unico file
    testo_tradotto = "\n\n---\n\n".join(chunk_traduzioni)
    out_name = f"{src.stem}_it.md"
    out_file = RAW / out_name
    write_file_safe(out_file, testo_tradotto)
    
    print(f"\n{Colors.GREEN}✅ Traduzione completata. File raggruppato: {out_file}{Colors.END}")
    
    # Ora fai ingest del file tradotto
    print(f"\n{Colors.CYAN}📥 Ingest del file tradotto a chunk...{Colors.END}")
    
    contenuto_tradotto = read_file_safe(out_file)
    parole_tradotte = len(contenuto_tradotto.split())
    
    num_chunk_tradotto = (parole_tradotte // CHUNK_SIZE) + (1 if parole_tradotte % CHUNK_SIZE > 0 else 0)
    print(f"   {num_chunk_tradotto} chunk da ingerire\n")
    
    parole_lista_tradotto = contenuto_tradotto.split()
    sandbox_creati = []
    
    for i in range(num_chunk_tradotto):
        start = i * CHUNK_SIZE
        end = min((i + 1) * CHUNK_SIZE, parole_tradotte)
        chunk_testo = " ".join(parole_lista_tradotto[start:end])
        
        chunk_filename = f"{src.stem}_chunk{i+1}_it.md"
        chunk_path = RAW / chunk_filename
        write_file_safe(chunk_path, chunk_testo)
        print(f"{Colors.DIM}📄 Chunk {i+1}/{num_chunk_tradotto} salvato: {chunk_filename}{Colors.END}")
        
        print(f"{Colors.DIM}🤖 Ingest chunk {i+1}/{num_chunk_tradotto}...{Colors.END}")
        cmd_ingest(chunk_filename)
        sandbox_creati.append(f"sdbx_{src.stem}_chunk{i+1}_it_V1.md")
        print()
    
    # Pulisci i file chunk temporanei
    for i in range(num_chunk_tradotto):
        chunk_file = RAW / f"{src.stem}_chunk{i+1}_it.md"
        if chunk_file.exists():
            chunk_file.unlink()
    
    print(f"\n{Colors.GREEN}✅ Ingest completato. {num_chunk_tradotto} sandbox creati:{Colors.END}")
    for sb in sandbox_creati:
        print(f"   - {sb}")
    print(f"\n{Colors.CYAN}💡 Il file tradotto completo è disponibile in: {out_file}{Colors.END}")
    print(f"{Colors.CYAN}💡 Ora puoi usare /chat su ogni file sandbox.{Colors.END}")
    update_log("traduci_ingest_chunk", f"File originale: {src.name}\nFile tradotto: {out_name}\nSandbox: {', '.join(sandbox_creati)}")

# ============================================================
# COMANDI ESISTENTI
# ============================================================

def cmd_move(filepath: str):
    src = CLIPPINGS / filepath
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in clippings/{Colors.END}")
        sys.stdout.flush()
        return
    dest = RAW / src.name
    shutil.move(str(src), str(dest))
    print(f"{Colors.GREEN}✅ Spostato: clippings/{filepath} → raw/{src.name}{Colors.END}")
    print()
    sys.stdout.flush()

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
    sys.stdout.flush()

def cmd_ingest(filepath: str):
    src = RAW / filepath
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in raw/{Colors.END}")
        sys.stdout.flush()
        return
    print(f"{Colors.GREEN}📥 Ingest: {src.name}{Colors.END}")
    testo = read_file_safe(src)
    out_name = f"sdbx_{src.stem}_V1.md"
    out_file = SANDBOX / out_name
    msg = [{"role":"user","content":f"""Analizza e scrivi riassunto ESAUSTIVO in italiano.

Fonte: {src.name}
Contenuto: {testo[:10000]}

USA ESATTAMENTE QUESTA STRUTTURA:

# 📌 SINTESI ESAUSTIVA
...

## 🎯 TESI CENTRALE
...

## 📚 ARGOMENTI E SOTTO-ARGOMENTI
...

## ⚠️ TENSIONI, CONTRADDIZIONI E PUNTI DEBOLI
...

## 🔗 POTENZIALI CONNESSIONI CON WIKI ESISTENTE
...

## 🗨️ DISCUSSIONE SOCRATICA
(Lascia vuoto)

## ✅ IL MIO SAPERE
(Lascia vuoto)

NON inserire evidenziazioni.
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
    print(f"{Colors.GREEN}✅ Riassunto generato in {out_file}{Colors.END}")
    print(f"{Colors.YELLOW}✏️ Ora aggiungi >argomento< nel file e usa /chat{Colors.END}")
    print()
    sys.stdout.flush()
    stato = load_stato()
    stato["fase"] = "INGEST_COMPLETATO"
    stato["file_corrente"] = out_name
    save_stato(stato)

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
            sys.stdout.flush()
            return
        
        # Ripresa da checkpoint se esiste
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
                # Mostra lo stato corrente
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
                sys.stdout.flush()
                chat_libera()
                return
            else:
                print(f"{Colors.YELLOW}⚠️ Tutte le {totale} evidenziazioni sono già state completate.{Colors.END}")
                print(f"   Usa /fine per generare il riassunto finale.{Colors.END}")
                print()
                sys.stdout.flush()
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
        sys.stdout.flush()
    
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file attivo. Usa /ingest prima o /chat sdbx_nome_V1.md{Colors.END}")
        sys.stdout.flush()
        return
    file_path = SANDBOX / stato["file_corrente"]
    if not file_path.exists():
        print(f"{Colors.RED}❌ File non trovato: {file_path}{Colors.END}")
        sys.stdout.flush()
        return
    
    contenuto = read_file_safe(file_path)
    evidenze = estrai_evidenziazioni(contenuto)
    if not evidenze:
        print(f"{Colors.YELLOW}⚠️ Nessuna evidenziazione >...< trovata in {stato['file_corrente']}{Colors.END}")
        print(f"   Aggiungi >argomento< nel file e riprova.")
        sys.stdout.flush()
        return
    print(f"{Colors.GREEN}🔍 Trovate {len(evidenze)} evidenziazioni in {stato['file_corrente']}:{Colors.END}")
    for e in evidenze:
        print(f"   • {e}")
    print()
    sys.stdout.flush()
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
        sys.stdout.flush()
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
    sys.stdout.flush()
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
        
        # Comando /salta
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
        
        # Comando /pausa
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
        
        # Comando /salva
        if user_input.startswith("/salva"):
            match = re.search(r'/salva\s+"([^"]+)"', user_input)
            if not match:
                print(f"{Colors.RED}❌ Formato: /salva \"risposta\"{Colors.END}")
                sys.stdout.flush()
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
2. Usa linguaggio tecnico preciso ma non divulgativo (chi legge è esperto)
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
            sys.stdout.flush()
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
                sys.stdout.flush()
            return
        
        # Comando /archivia
        if user_input.lower() == "/archivia":
            cmd_archivia()
            return
        
        # Dialogo normale
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
            sys.stdout.flush()

def cmd_fine():
    """Genera riassunto narrativo unificato di tutte le evidenziazioni"""
    stato = load_stato()
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file attivo{Colors.END}")
        sys.stdout.flush()
        return
    file_path = SANDBOX / stato["file_corrente"]
    if not file_path.exists():
        print(f"{Colors.RED}❌ File non trovato{Colors.END}")
        sys.stdout.flush()
        return
    contenuto = read_file_safe(file_path)
    if "## ✅ IL MIO SAPERE" in contenuto and "NON ANCORA GENERATO" not in contenuto:
        print(f"{Colors.YELLOW}⚠️ Il riassunto finale esiste già. Non lo rigenero.{Colors.END}")
        sys.stdout.flush()
        return
    
    riassunti_evidenze = []
    blocchi = re.findall(r'### Evidenziazione \d+: (.+?)\n\*\*Domanda:\*\* (.+?)\n\*\*Riassunto della conversazione:\*\*\n\n(.*?)\n\n\*\*Risposta finale:\*\* (.+?)(?:\n---|$)', contenuto, re.DOTALL)
    for ev, dom, riass, risp in blocchi:
        riassunti_evidenze.append(f"**{ev}**\nDomanda: {dom}\nDiscussione: {riass}\nRisposta: {risp}")
    
    if not riassunti_evidenze:
        print(f"{Colors.YELLOW}⚠️ Non trovate evidenziazioni salvate. Esegui prima /chat e /salva.{Colors.END}")
        sys.stdout.flush()
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
    sys.stdout.flush()
    stato["fase"] = "COMPLETATA"
    save_stato(stato)

def cmd_promuovi(titolo: str):
    """Promuove il sandbox a pagina wiki (esclude DISCUSSIONE SOCRATICA)"""
    stato = load_stato()
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file sandbox attivo. Esegui /ingest prima.{Colors.END}")
        sys.stdout.flush()
        return
    sandbox_path = SANDBOX / stato["file_corrente"]
    if not sandbox_path.exists():
        print(f"{Colors.RED}❌ File sandbox non trovato: {sandbox_path}{Colors.END}")
        sys.stdout.flush()
        return

    contenuto_sandbox = read_file_safe(sandbox_path)

    # Estrai solo le sezioni desiderate (escludendo DISCUSSIONE SOCRATICA)
    sintesi_esaustiva = estrai_sezione(contenuto_sandbox, r'# 📌 SINTESI ESAUSTIVA')
    tesi_centrale = estrai_sezione(contenuto_sandbox, r'## 🎯 TESI CENTRALE')
    argomenti = estrai_sezione(contenuto_sandbox, r'## 📚 ARGOMENTI E SOTTO-ARGOMENTI')
    tensioni = estrai_sezione(contenuto_sandbox, r'## ⚠️ TENSIONI, CONTRADDIZIONI E PUNTI DEBOLI')
    il_mio_sapere = estrai_sezione(contenuto_sandbox, r'## ✅ IL MIO SAPERE')

    if not il_mio_sapere:
        print(f"{Colors.YELLOW}⚠️ Sezione 'IL MIO SAPERE' non trovata. Esegui /fine prima di promuovere.{Colors.END}")
        print(f"   Generazione automatica in corso...")
        cmd_fine()
        contenuto_sandbox = read_file_safe(sandbox_path)
        il_mio_sapere = estrai_sezione(contenuto_sandbox, r'## ✅ IL MIO SAPERE')

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

    # Ricerca wikilink
    print(f"{Colors.CYAN}🔍 Cerco pagine wiki correlate...{Colors.END}")
    wiki_pages = {}
    for f in WIKI.glob("*.md"):
        if f.name not in ["index.md", "log.md"]:
            wiki_pages[f.stem] = read_file_safe(f)[:1000]
    collegamenti_trovati = []
    if wiki_pages:
        prompt_link = f"""Elenco pagine wiki esistenti (nome e inizio contenuto):
{chr(10).join([f"- [[{nome}]]: {testo[:200]}" for nome, testo in wiki_pages.items()])}

Nuova pagina in creazione: "{titolo}"
Riassunto finale: {il_mio_sapere[:1000]}

Quali di queste pagine sono semanticamente correlate? Per ognuna, spiega brevemente perché.
Restituisci JSON: [{{"pagina": "nome", "ragione": "spiegazione breve"}}, ...]
Massimo 5.
"""
        msg_link = [{"role": "user", "content": prompt_link}]
        link_response = call_llm(build_system(), msg_link)
        try:
            collegamenti_trovati = json.loads(link_response)
            if not isinstance(collegamenti_trovati, list):
                collegamenti_trovati = []
        except:
            collegamenti_trovati = []

    # Menu interattivo
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📝 CREAZIONE NUOVA PAGINA WIKI{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    print(f"{Colors.GREEN}Titolo:{Colors.END} {titolo}")

    # Scelta dominio
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

    # Scelta tipo
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
    
    # Numero di cicli SPB = numero evidenziazioni
    evidenze_risposte = re.findall(r'### Evidenziazione \d+:', contenuto_sandbox)
    cicli_spb = len(evidenze_risposte)

    # Mostra frontmatter
    print(f"\n{Colors.BLUE}{'─'*40}{Colors.END}")
    print(f"{Colors.BOLD}📄 Frontmatter:{Colors.END}")
    print(f"  titolo: {titolo}")
    print(f"  dominio: {dominio_finale}")
    print(f"  tipo: {tipo_finale}")
    print(f"  stato: attivo")
    print(f"  data_promozione: {date.today()}")
    print(f"  cicli_spb: {cicli_spb}")
    print(f"  fonti: {fonti_str}")
    print(f"{Colors.BLUE}{'─'*40}{Colors.END}")

    conferma = input(f"{Colors.YELLOW}✅ Confermi? (s/n/modifica): {Colors.END}").lower()
    if conferma == 'n':
        print(f"{Colors.RED}❌ Promozione annullata.{Colors.END}")
        sys.stdout.flush()
        return
    elif conferma == 'modifica':
        nuovo_titolo = input(f"Titolo ({titolo}): ").strip()
        if nuovo_titolo: titolo = nuovo_titolo
        nuovo_dominio = input(f"Dominio ({dominio_finale}): ").strip()
        if nuovo_dominio: dominio_finale = nuovo_dominio
        nuovo_tipo = input(f"Tipo ({tipo_finale}): ").strip()
        if nuovo_tipo: tipo_finale = nuovo_tipo

    # Scelta wikilink
    collegamenti_scelti = []
    if collegamenti_trovati:
        print(f"\n{Colors.CYAN}🔗 Pagine wiki correlate trovate:{Colors.END}")
        for i, link in enumerate(collegamenti_trovati, 1):
            print(f"  {i}. [[{link['pagina']}]] — {link.get('ragione', 'correlata')}")
        print(f"  {len(collegamenti_trovati)+1}. Nessuno")
        scelta_link = input(f"{Colors.YELLOW}👉 Numeri da mantenere (es. 1,3,5) o invio: {Colors.END}").strip()
        if scelta_link:
            indici = re.findall(r'\d+', scelta_link)
            for idx in indici:
                num = int(idx)
                if 1 <= num <= len(collegamenti_trovati):
                    collegamenti_scelti.append(collegamenti_trovati[num-1]['pagina'])
    else:
        aggiungi_manuale = input(f"{Colors.CYAN}Vuoi aggiungere collegamenti manualmente? (s/n): {Colors.END}").lower()
        if aggiungi_manuale == 's':
            while True:
                manuale = input(f"Nome pagina wiki (vuoto per finire): ").strip()
                if not manuale:
                    break
                collegamenti_scelti.append(manuale)

    wikilink_list = "\n".join([f"- [[{link}]]" for link in collegamenti_scelti])
    
    # Costruisci il contenuto del wiki (SENZA DISCUSSIONE SOCRATICA)
    wiki_content = f"""---
titolo: {titolo}
dominio: {dominio_finale}
tipo: {tipo_finale}
stato: attivo
data_promozione: {date.today()}
cicli_spb: {cicli_spb}
fonti: {fonti_str}
---

# 📌 SINTESI ESAUSTIVA

{sintesi_esaustiva}

## 🎯 TESI CENTRALE

{tesi_centrale}

## 📚 ARGOMENTI E SOTTO-ARGOMENTI

{argomenti}

## ⚠️ TENSIONI, CONTRADDIZIONI E PUNTI DEBOLI

{tensioni}

## ✅ IL MIO SAPERE

{il_mio_sapere}

## Collegamenti

{wikilink_list}
"""
    slug = titolo.lower().replace(" ", "_").replace("-", "_")
    wiki_path = WIKI / f"{slug}.md"
    write_file_safe(wiki_path, wiki_content)

    with INDEX.open("a", encoding='utf-8') as f:
        f.write(f"| [[{titolo}]] | {dominio_finale} | {tipo_finale} | {date.today()} |\n")
    with LOG.open("a", encoding='utf-8') as f:
        f.write(f"\n## [{date.today()}] promuovi | {titolo}\n- File sandbox: {stato['file_corrente']}\n- Cicli SPB: {cicli_spb}\n- Pagina wiki: {wiki_path.name}\n")

    print(f"\n{Colors.GREEN}✅ Pagina wiki creata: {wiki_path}{Colors.END}")
    print(f"{Colors.GREEN}✅ Indice e log aggiornati.{Colors.END}")
    
    # Archivia il sandbox
    if sandbox_path.exists():
        arch_path = ARCHIVIATI / sandbox_path.name
        shutil.move(str(sandbox_path), str(arch_path))
        print(f"{Colors.YELLOW}🗂️ Sandbox archiviato in: {arch_path}{Colors.END}")
    
    print()
    sys.stdout.flush()
    reset_stato()
    
    # Aggiorna indice wiki
    costruisci_indice()

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
        sys.stdout.flush()
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
    sys.stdout.flush()

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
    sys.stdout.flush()

def cmd_query(domanda: str):
    """Interroga il wiki usando indice leggero + ricerca web con marcatura fonti"""
    
    # FASE 1: Cerca nel wiki con indice leggero
    pagine_rilevanti = cerca_nel_wiki(domanda)
    
    risposta_wiki = None
    fonti_wiki = []
    
    if pagine_rilevanti:
        ctx = ""
        for score, titolo, percorso in pagine_rilevanti:
            contenuto = read_file_safe(Path(percorso))
            # Estrai solo IL MIO SAPERE e SINTESI
            sintesi = estrai_sezione(contenuto, r'# 📌 SINTESI ESAUSTIVA')
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
    
    # Verifica se la risposta del wiki è sufficiente
    if risposta_wiki and "INFO_INSUFFICIENTI" not in risposta_wiki and len(risposta_wiki) > 150:
        # Marca le fonti wiki
        for fonte in fonti_wiki:
            risposta_wiki = risposta_wiki.replace(f"[[{fonte}]]", f"[WIKI] [[{fonte}]]")
        print(f"\n{Colors.CYAN}[WIKI] {Colors.END}")
        print_wrapped(risposta_wiki)
        print()
        sys.stdout.flush()
        return
    
    # FASE 2: Cerca online
    print(f"\n{Colors.DIM}⚠️ Informazioni insufficienti nel wiki. Ricerca online in corso...{Colors.END}\n")
    
    risultati_web = web_search_brave(domanda, num_results=5)
    
    if not risultati_web:
        if risposta_wiki:
            print_wrapped(f"[WIKI] {risposta_wiki}")
        else:
            print(f"{Colors.YELLOW}⚠️ Nessun risultato trovato.{Colors.END}")
        print()
        sys.stdout.flush()
        return
    
    # Costruisci contesto dai risultati web
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

Esempio:
[WIKI] Secondo [[Bitcoin]] la blockchain è immutabile.
[WEB] Secondo una ricerca online (Fonte: esempio.com), ci sono 10 milioni di wallet attivi.

Rispondi in italiano."""}]
    
    risposta_completa = call_llm(build_system(), msg_web)
    
    print(f"\n{Colors.CYAN}🌐 RISPOSTA (WIKI + WEB):{Colors.END}")
    print_wrapped(risposta_completa)
    print()
    sys.stdout.flush()
    
    # Log della ricerca
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
    sys.stdout.flush()

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
        for f in [AGENT_MD, Path("wiki.py"), Path(".env")]:
            if f.exists():
                z.write(f)
    print(f"{Colors.GREEN}✅ Backup: {bkp}{Colors.END}")
    print()
    sys.stdout.flush()

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
    sys.stdout.flush()

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def print_banner():
    modello_nome = "V4 Pro" if CURRENT_MODEL == DEEPSEEK_PRO else "V4 Flash"
    print(f"""
{Colors.BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║     SISTEMA SOCRATES-PLATO-BAYES - Versione Definitiva       ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}Modello attivo:{Colors.END} {Colors.CYAN}{modello_nome} ({CURRENT_MODEL}){Colors.END}
{Colors.YELLOW}Soglia chunk:{Colors.END} {Colors.CYAN}{CHUNK_SIZE} parole{Colors.END}

{Colors.YELLOW}Comandi:{Colors.END}

  {Colors.GREEN}/move{Colors.END}      <file>               Sposta da clippings/ a raw/
  {Colors.GREEN}/list{Colors.END}     [cartella]           Mostra file
  {Colors.GREEN}/ingest{Colors.END}   <file>               Crea sandbox (prefisso sdbx_)
  {Colors.GREEN}/analizza{Colors.END} <file>               Analizza file (Ingest/Traduci/Annulla)
  {Colors.GREEN}/chat{Colors.END}     [file]               Avvia/riprendi discussione
  {Colors.GREEN}/salva{Colors.END}    "risposta"           Salva evidenziazione (riassunto narrativo)
  {Colors.GREEN}/fine{Colors.END}                         Genera riassunto unificato (IL MIO SAPERE)
  {Colors.GREEN}/promuovi{Colors.END} "Titolo"             Crea wiki (esclude DISCUSSIONE SOCRATICA)
  {Colors.GREEN}/riprendi{Colors.END} <file>               Ripristina sandbox archiviato
  {Colors.GREEN}/archivia{Colors.END}                     Archivia discussione corrente
  {Colors.GREEN}/query{Colors.END}    "domanda"            Interroga wiki (con indice + ricerca web)
  {Colors.GREEN}/lint{Colors.END}                         Health-check
  {Colors.GREEN}/backup{Colors.END}                       Backup completo
  {Colors.GREEN}/stato{Colors.END}                        Mostra stato
  {Colors.GREEN}/clear{Colors.END}                        Pulisce schermo
  {Colors.GREEN}/exit{Colors.END}                         Esci

{Colors.BLUE}💡 >argomento< nel file, poi /chat. /salva genera riassunto narrativo tecnico.{Colors.END}
{Colors.BLUE}💡 /analizza offre: 1. Ingest (chunk → sandbox), 2. Traduci (traduci → raggruppa → ingest chunk){Colors.END}
{Colors.BLUE}💡 /promuovi crea pagina wiki con SINTESI, TESI, ARGOMENTI, TENSIONI, IL MIO SAPERE (esclude DISCUSSIONE SOCRATICA){Colors.END}
{Colors.BLUE}💡 /query cerca prima nel wiki (con indice), poi online con Brave API. Marca [WIKI] e [WEB].{Colors.END}
{Colors.BLUE}💡 In /chat: /salta (salta evidenziazione), /pausa (salva sessione){Colors.END}
""")
    sys.stdout.flush()

# --------------------------------------------------------------
# AUTOCOMPLETAMENTO AVANZATO
# --------------------------------------------------------------

class SpbCompleter:
    def __init__(self):
        self.commands = ["/move", "/list", "/ingest", "/analizza", "/chat", "/salva", "/fine", "/promuovi", "/riprendi", "/archivia", "/query", "/lint", "/backup", "/stato", "/clear", "/exit"]
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
        
        if cmd == "/move" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in CLIPPINGS.glob("*") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        
        if cmd == "/ingest" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in RAW.glob("*") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        
        if cmd == "/analizza" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in CLIPPINGS.glob("*") if f.is_file()] + [f.name for f in RAW.glob("*") if f.is_file()]
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
        
        if cmd == "/query" and len(parts) <= 2:
            return None
        
        return None

# --------------------------------------------------------------
# MAIN
# --------------------------------------------------------------

def main():
    init_vault()
    ripulisci_file_orfani()
    clear_screen()
    print_banner()

    # Costruisci indice wiki all'avvio
    costruisci_indice()

    if readline is not None:
        completer = SpbCompleter()
        readline.set_completer(completer.get_matches)
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims(' \t\n;')
    else:
        print(f"{Colors.YELLOW}⚠️ readline non disponibile, autocompletamento disabilitato{Colors.END}")

    # Controlla checkpoint attivo
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

            if cmd == "/move":
                if arg:
                    cmd_move(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file (TAB per autocompletare){Colors.END}")
                    sys.stdout.flush()
            elif cmd == "/list":
                cmd_list(arg if arg else None)
            elif cmd == "/ingest":
                if arg:
                    cmd_ingest(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file (TAB per autocompletare){Colors.END}")
                    sys.stdout.flush()
            elif cmd == "/analizza":
                if arg:
                    cmd_analizza(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file: /analizza documento.md{Colors.END}")
                    sys.stdout.flush()
            elif cmd == "/chat":
                cmd_chat(arg if arg else None)
            elif cmd == "/salva":
                print(f"{Colors.YELLOW}⚠️ Usa /salva durante la chat (dopo /chat){Colors.END}")
                sys.stdout.flush()
            elif cmd == "/fine":
                cmd_fine()
            elif cmd == "/promuovi":
                if arg:
                    cmd_promuovi(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il titolo: /promuovi \"Titolo della pagina\"{Colors.END}")
                    sys.stdout.flush()
            elif cmd == "/riprendi":
                if arg:
                    cmd_riprendi(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file da riprendere (TAB per autocompletare){Colors.END}")
                    sys.stdout.flush()
            elif cmd == "/archivia":
                cmd_archivia()
            elif cmd == "/query":
                if arg:
                    cmd_query(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica la domanda: /query \"testo\"{Colors.END}")
                    sys.stdout.flush()
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
                sys.stdout.flush()
        except KeyboardInterrupt:
            print(f"\n{Colors.BLUE}👋 Bye{Colors.END}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ {e}{Colors.END}")
            sys.stdout.flush()

if __name__ == "__main__":
    main()