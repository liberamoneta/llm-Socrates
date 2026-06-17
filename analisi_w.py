#!/usr/bin/env python3
"""
analisi_w.py — Sistema Socrates–Plato–Bayes (SPB) - Versione Definitiva
Flusso: /estrai (%%...%% + ??...??) → /chat → /salva → /fine → /analizza → /promuovi
Supporta: DeepSeek Ufficiale e SiliconFlow
Marcatori:
  %%...%%  → Testo da estrarre per la sintesi
  ??...??  → Testo da discutere in chat
  > ...    → Citazione normale (rimane nel testo)
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
from typing import Tuple, List, Optional
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
    print(f"\n{color}{prefix}{wrapped}{Colors.END}", flush=True)

def safe_input(prompt):
    """Versione per Git Bash - il prompt è sempre visibile"""
    # Stampa un newline e il prompt
    print()
    print(prompt, end='', flush=True)
    # Legge l'input
    return input()

def safe_input_semplice(prompt):
    """Versione ultra-semplice per Git Bash"""
    print()
    return input(prompt)

# ============================================================
# DESCRIZIONI MODELLI
# ============================================================

MODEL_DESCRIPTIONS = {
    # DeepSeek Ufficiale
    "deepseek-v4-pro": "🔥 DeepSeek V4 Pro - Modello di punta",
    "deepseek-v4-flash": "⚡ DeepSeek V4 Flash - Veloce ed economico",
    "deepseek-chat": "💬 DeepSeek Chat - Standard",
    "deepseek-reasoner": "🧠 DeepSeek Reasoner - Ragionamento",
    
    # DeepSeek SiliconFlow
    "deepseek-ai/DeepSeek-V3": "💬 Chat generale, ragionamento, codice",
    "deepseek-ai/DeepSeek-R1": "🧠 Ragionamento avanzato, matematica, logica",
    "deepseek-ai/DeepSeek-V2": "⚡ Bilanciato, veloce ed economico",
    
    # Qwen
    "Qwen/Qwen2.5-72B-Instruct": "📝 Traduzioni, scrittura, analisi testi",
    "Qwen/Qwen2.5-32B-Instruct": "📝 Traduzioni, scrittura (più economico)",
    "Qwen/Qwen2.5-14B-Instruct": "📝 Traduzioni leggere, veloci",
    "Qwen/Qwen2.5-7B-Instruct": "📝 Traduzioni ultra-leggere",
    
    # Qwen Visione
    "Qwen/Qwen3-VL-30B-A3B-Instruct": "👁️ OCR avanzato + traduzione",
    "Qwen/Qwen3-VL-8B-Instruct": "👁️ OCR veloce + traduzione leggera",
    "Qwen/Qwen3-VL-32B-Instruct": "👁️ OCR alta qualità + traduzione",
    
    # Meta Llama
    "meta-llama/Meta-Llama-3.1-70B-Instruct": "💬 Chat, ragionamento, codice",
    "meta-llama/Meta-Llama-3.1-8B-Instruct": "💬 Chat leggera, veloce",
    "meta-llama/Llama-3.2-3B-Instruct": "💬 Chat ultra-leggera",
    
    # Altri
    "OpenGVLab/InternVL2-8B": "👁️ Visione, OCR, analisi immagini",
    "OpenGVLab/InternVL2-26B": "👁️ Visione avanzata, OCR",
    "ZhipuAI/GLM-4-9B": "💬 Chat, ragionamento, codice",
    "01-ai/Yi-1.5-34B": "💬 Chat, ragionamento",
    "01-ai/Yi-1.5-9B": "💬 Chat leggera, veloce",
    "mistralai/Mistral-7B-Instruct-v0.2": "💬 Chat efficiente, codice",
}

# ============================================================
# CONFIGURAZIONE PROVIDER
# ============================================================

def carica_api_keys_ingest():
    """Carica le API keys da .env"""
    env_paths = [
        Path.cwd() / ".env",
        Path.cwd() / "llm-Socrates" / ".env",
        Path(__file__).parent / ".env",
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
    
    return {
        "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        "siliconflow": os.getenv("SILICONFLOW_API_KEY")
    }

API_KEYS = carica_api_keys_ingest()

# Configurazione provider per ingest
PROVIDER_CONFIG = {
    "deepseek": {
        "nome": "DeepSeek Ufficiale",
        "base_url": "https://api.deepseek.com",
        "modelli": [
            "deepseek-chat",
            "deepseek-reasoner",
            "deepseek-v4-pro"
        ]
    },
    "siliconflow": {
        "nome": "SiliconFlow",
        "base_url": "https://api.siliconflow.com/v1",
        "modelli": [
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "deepseek-ai/DeepSeek-V2",
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct"
        ]
    }
}

def scegli_provider_e_modello_ingest() -> Tuple[str, str, str]:
    """Menu per scegliere provider e modello per ingest"""
    
    print("\n" + "=" * 60, flush=True)
    print("🔧 SCEGLI PROVIDER E MODELLO per INGEST", flush=True)
    print("=" * 60, flush=True)
    
    provider_keys = list(PROVIDER_CONFIG.keys())
    print("\n📡 Provider disponibili:", flush=True)
    for i, key in enumerate(provider_keys, 1):
        config = PROVIDER_CONFIG[key]
        has_key = API_KEYS.get(key) is not None
        status = "✅" if has_key else "❌ (chiave mancante)"
        print(f"   {i}. {config['nome']} - {status}", flush=True)
    
    print(f"   {len(provider_keys)+1}. Esci", flush=True)
    
    while True:
        try:
            choice = safe_input_semplice("\n👉 Scegli provider (numero): ").strip()
            if choice == str(len(provider_keys)+1):
                return None, None, None
            
            idx = int(choice) - 1
            if 0 <= idx < len(provider_keys):
                provider_key = provider_keys[idx]
                provider_config = PROVIDER_CONFIG[provider_key]
                
                api_key = API_KEYS.get(provider_key)
                if not api_key:
                    print(f"   ❌ Chiave API non trovata per {provider_config['nome']}", flush=True)
                    print(f"   Aggiungi {provider_key.upper()}_API_KEY nel .env", flush=True)
                    continue
                
                print(f"\n🤖 Modelli disponibili su {provider_config['nome']}:", flush=True)
                print("-" * 60, flush=True)
                
                # Mostra modelli con descrizioni
                for i, model_id in enumerate(provider_config['modelli'], 1):
                    desc = MODEL_DESCRIPTIONS.get(model_id, "💬 Modello generico")
                    # Allinea il nome del modello a sinistra e la descrizione a destra
                    print(f"   {i}. {model_id:<35} {desc}", flush=True)
                print("-" * 60, flush=True)
                
                while True:
                    try:
                        model_choice = safe_input_semplice("\n👉 Scegli modello (numero): ").strip()
                        idx_model = int(model_choice) - 1
                        if 0 <= idx_model < len(provider_config['modelli']):
                            model_id = provider_config['modelli'][idx_model]
                            print(f"\n   📌 {MODEL_DESCRIPTIONS.get(model_id, 'Modello selezionato')}", flush=True)
                            return provider_key, model_id, api_key
                        else:
                            print(f"   ❌ Scelta non valida (1-{len(provider_config['modelli'])})", flush=True)
                    except ValueError:
                        print("   ❌ Inserisci un numero valido", flush=True)
            else:
                print(f"   ❌ Scelta non valida (1-{len(provider_keys)})", flush=True)
        except ValueError:
            print("   ❌ Inserisci un numero valido", flush=True)
        except KeyboardInterrupt:
            return None, None, None

# ============================================================
# COSTANTI - DIRECTORIES
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

# ============================================================
# VARIABILI GLOBALI (impostate da main)
# ============================================================

DEEPSEEK_API_KEY = None
CURRENT_MODEL = None
CLIENT = None
PROVIDER_NOME = None

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
    """Chiamata LLM con supporto provider variabile"""
    global CLIENT, CURRENT_MODEL
    
    try:
        if allow_search:
            print(f"{Colors.DIM}🔍 Ricerca esterna abilitata...{Colors.END}", flush=True)
        
        model_to_use = model if model else CURRENT_MODEL
        print(f"{Colors.DIM}🤖 Chiamata LLM ({model_to_use})...{Colors.END}", flush=True)
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

# ============================================================
# FUNZIONI DI ESTRAZIONE CON NUOVI MARCATORI
# ============================================================

def estrai_evidenziazioni(contenuto: str) -> list:
    """Estrae evidenziazioni ??...?? per la chat"""
    return re.findall(r'\?\?(.*?)\?\?', contenuto, re.DOTALL)

def estrai_sezione(contenuto: str, pattern: str) -> str:
    """Estrae una sezione dal markdown usando un pattern regex"""
    match = re.search(pattern + r'\n\n(.*?)(?=\n##|\n---|\Z)', contenuto, re.DOTALL)
    return match.group(1).strip() if match else ""

def estrai_estratti(contenuto: str) -> list:
    """Estrae i blocchi marcati con %%...%% per la sintesi"""
    pattern = r'%%(.*?)%%'
    matches = re.findall(pattern, contenuto, re.DOTALL)
    return [m.strip() for m in matches]

def estrai_evidenze_chat(contenuto: str) -> list:
    """Estrae i blocchi marcati con ??...?? per la chat"""
    pattern = r'\?\?(.*?)\?\?'
    matches = re.findall(pattern, contenuto, re.DOTALL)
    return [m.strip() for m in matches]

def estrai_evidenze_e_chat(contenuto: str) -> Tuple[List[str], List[str]]:
    """
    Estrae i blocchi %%...%% (per la sintesi) e ??...?? (per la chat)
    Restituisce (estratti, evidenze_chat)
    """
    estratti = estrai_estratti(contenuto)
    evidenze_chat = estrai_evidenze_chat(contenuto)
    return estratti, evidenze_chat

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
            print(f"{Colors.DIM}🧹 Rimozione file orfano: {chunk_file.name}{Colors.END}", flush=True)
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
        print(f"{Colors.YELLOW}⚠️ Errore Brave API: {e}. Fallback a DuckDuckGo.{Colors.END}", flush=True)
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
    """
    Estrae evidenze marcate con %%...%% e ??...?? da un file in raw/
    Crea estratto_nome.md con entrambi i tipi di marcatori
    """
    
    md_files = [f for f in RAW.glob("*.md") if not f.name.startswith("estratto_")]
    
    if not md_files:
        print(f"{Colors.RED}❌ Nessun file .md trovato in raw/{Colors.END}", flush=True)
        return
    
    print(f"\n{Colors.CYAN}📁 File disponibili per estrazione:{Colors.END}", flush=True)
    for i, f in enumerate(md_files, 1):
        size = f.stat().st_size / 1024
        print(f"   {i}. {f.name} ({size:.1f} KB)", flush=True)
    
    try:
        scelta = safe_input_semplice(f"\n👉 Scegli il numero del file (0 per uscire): ").strip()
        if scelta == "0":
            return
        idx = int(scelta) - 1
        if idx < 0 or idx >= len(md_files):
            print(f"{Colors.RED}❌ Scelta non valida{Colors.END}", flush=True)
            return
        src_file = md_files[idx]
    except ValueError:
        print(f"{Colors.RED}❌ Scelta non valida{Colors.END}", flush=True)
        return
    
    contenuto = read_file_safe(src_file)
    
    # Estrai entrambi i tipi di marcatori
    estratti, evidenze_chat = estrai_evidenze_e_chat(contenuto)
    
    if not estratti and not evidenze_chat:
        print(f"{Colors.YELLOW}⚠️ Nessuna evidenza %%...%% o ??...?? trovata in {src_file.name}{Colors.END}", flush=True)
        print(f"   Aggiungi %%...%% per estrarre e ??...?? per discutere.", flush=True)
        return
    
    print(f"{Colors.GREEN}✅ Trovate {len(estratti)} evidenze %%...%%{Colors.END}", flush=True)
    print(f"{Colors.GREEN}✅ Trovate {len(evidenze_chat)} evidenze ??...?? per la chat{Colors.END}", flush=True)
    
    output_name = f"estratto_{src_file.stem}.md"
    output_path = RAW / output_name
    
    md_content = f"""---
titolo: {src_file.stem} - Estratti
fonte: {src_file.name}
data_estrazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tipo: estratti
numero_estratti: {len(estratti)}
numero_evidenze: {len(evidenze_chat)}
---

# 📌 ESTRATTI SELEZIONATI

Fonte originale: `{src_file.name}`

"""
    for i, ev in enumerate(estratti, 1):
        md_content += f"\n## Estratto {i}\n\n{ev}\n\n---\n"
    
    if evidenze_chat:
        md_content += "\n# 💬 EVIDENZE PER LA CHAT\n\n"
        for ev in evidenze_chat:
            md_content += f"?? {ev} ??\n\n"
    
    write_file_safe(output_path, md_content)
    print(f"{Colors.GREEN}✅ File estratto creato: {output_name}{Colors.END}", flush=True)
    print(f"{Colors.CYAN}💡 Ora usa /chat {output_name} per iniziare la discussione socratica.{Colors.END}", flush=True)

# ============================================================
# COMANDO /chat (PRIMA dell'ingest)
# ============================================================

def cmd_chat(filearg: str = None):
    """
    Avvia la discussione socratica su un file estratto.
    PRIMA dell'ingest - discute le evidenze ??...??
    """
    stato = load_stato()
    
    if filearg and filearg.strip():
        target_file = filearg.strip()
        if not target_file.endswith(".md"):
            target_file = target_file + ".md"
        
        # Supporta sia file diretti che estratti
        if not target_file.startswith("estratto_") and not target_file.startswith("sdbx_"):
            # Cerca prima in raw/, poi in sandbox/
            if (RAW / target_file).exists():
                target_file = target_file
            elif (RAW / f"estratto_{target_file}").exists():
                target_file = f"estratto_{target_file}"
        
        # Cerca il file in raw/ o sandbox/
        file_path = RAW / target_file
        if not file_path.exists():
            file_path = SANDBOX / target_file
        if not file_path.exists():
            print(f"{Colors.RED}❌ File non trovato: {target_file}{Colors.END}", flush=True)
            print(f"   File disponibili in raw/:", flush=True)
            for f in RAW.glob("estratto_*.md"):
                print(f"     - {f.name}", flush=True)
            print(f"   File disponibili in sandbox/:", flush=True)
            for f in SANDBOX.glob("sdbx_*_V1.md"):
                print(f"     - {f.name}", flush=True)
            return
        
        stato["file_corrente"] = file_path.name
        stato["file_path"] = str(file_path)
        stato["fase"] = "IN_DISCUSSIONE"
        stato["evidenziazioni"] = []
        stato["conversazioni"] = []
        stato["indice"] = 0
        stato["domanda_corrente"] = None
        stato["evidenziazione_corrente"] = None
        stato["storico_chat"] = []
        save_stato(stato)
        print(f"{Colors.GREEN}✅ File attivo: {file_path.name}{Colors.END}", flush=True)
    
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file attivo. Usa /chat nome_file.md{Colors.END}", flush=True)
        return
    
    file_path = Path(stato.get("file_path", stato["file_corrente"]))
    if not file_path.exists():
        file_path = RAW / stato["file_corrente"]
        if not file_path.exists():
            file_path = SANDBOX / stato["file_corrente"]
        if not file_path.exists():
            print(f"{Colors.RED}❌ File non trovato: {stato['file_corrente']}{Colors.END}", flush=True)
            return
    
    contenuto = read_file_safe(file_path)
    
    # Estrai evidenze ??...??
    evidenze = estrai_evidenze_chat(contenuto)
    
    if not evidenze:
        print(f"{Colors.YELLOW}⚠️ Nessuna evidenza ??...?? trovata in {file_path.name}{Colors.END}", flush=True)
        print(f"   Aggiungi ??...?? nel file e riprova.", flush=True)
        return
    
    print(f"{Colors.GREEN}🔍 Trovate {len(evidenze)} evidenze ??...?? in {file_path.name}:{Colors.END}", flush=True)
    for e in evidenze:
        print(f"   • {e}", flush=True)
    print(flush=True)
    
    stato["fase"] = "IN_DISCUSSIONE"
    stato["evidenziazioni"] = evidenze
    stato["conversazioni"] = []
    stato["indice"] = 0
    stato["file_path"] = str(file_path)
    save_stato(stato)
    avvia_evidenziazione()

def avvia_evidenziazione():
    """Avvia la discussione su una singola evidenziazione"""
    stato = load_stato()
    idx = stato["indice"]
    evidenze = stato.get("evidenziazioni", [])
    
    if idx >= len(evidenze):
        print(f"\n{Colors.GREEN}✅ Tutte le evidenze ??...?? discusse!{Colors.END}", flush=True)
        print(f"   Usa /fine per generare IL MIO SAPERE (riassunto finale).", flush=True)
        print(flush=True)
        return
    
    ev = evidenze[idx]
    print(f"\n{Colors.MAGENTA}{'='*60}{Colors.END}", flush=True)
    print(f"{Colors.YELLOW}💬 Evidenza {idx+1}/{len(evidenze)}: {ev}{Colors.END}", flush=True)
    print(f"{Colors.MAGENTA}{'='*60}{Colors.END}", flush=True)
    print(f"{Colors.DIM}🤖 LLM genera domanda socratica...{Colors.END}", flush=True)
    
    msg = [{"role":"user","content":f"Genera una domanda socratica su: {ev}\nSolo la domanda, senza preamboli."}]
    domanda = call_llm(build_system(), msg)
    
    print(f"\n{Colors.GREEN}📝 DOMANDA:{Colors.END}", flush=True)
    print_wrapped(domanda, color=Colors.CYAN, prefix="")
    print(f"\n{Colors.DIM}Dialogo libero. Quando hai la risposta definitiva, usa:{Colors.END}", flush=True)
    print(f"   {Colors.GREEN}/salva \"la tua risposta\"{Colors.END}", flush=True)
    print(f"   {Colors.YELLOW}/salta{Colors.END} per saltare questa evidenza", flush=True)
    print(f"   {Colors.YELLOW}/pausa{Colors.END} per salvare e uscire", flush=True)
    
    stato["domanda_corrente"] = domanda
    stato["evidenziazione_corrente"] = ev
    stato["storico_chat"] = []
    save_stato(stato)
    chat_libera()

def chat_libera():
    """Dialogo interattivo durante la chat"""
    stato = load_stato()
    ev = stato["evidenziazione_corrente"]
    domanda = stato["domanda_corrente"]
    file_path = Path(stato.get("file_path", stato["file_corrente"]))
    
    while True:
        user_input = safe_input_semplice(f"{Colors.GREEN}tu> {Colors.END}").strip()
        if not user_input:
            continue
        
        if user_input.lower() == "/salta":
            print(f"{Colors.YELLOW}⏭️ Evidenza saltata: {ev}{Colors.END}", flush=True)
            stato["indice"] += 1
            stato["domanda_corrente"] = None
            stato["evidenziazione_corrente"] = None
            stato["storico_chat"] = []
            save_stato(stato)
            if stato["indice"] < len(stato.get("evidenziazioni", [])):
                avvia_evidenziazione()
            else:
                print(f"\n{Colors.GREEN}🎉 Tutte le evidenze discusse/saltate!{Colors.END}", flush=True)
            return
        
        if user_input.lower() == "/pausa":
            salva_checkpoint("chat", stato.get("file_corrente"), {
                "indice": stato.get("indice", 0),
                "evidenziazioni": stato.get("evidenziazioni", []),
                "storico_chat": stato.get("storico_chat", []),
                "domanda_corrente": domanda,
                "evidenziazione_corrente": ev
            })
            print(f"{Colors.CYAN}⏸️ Sessione salvata. Usa /chat per riprendere.{Colors.END}", flush=True)
            reset_stato()
            return
        
        if user_input.startswith("/salva"):
            match = re.search(r'/salva\s+"([^"]+)"', user_input)
            if not match:
                print(f"{Colors.RED}❌ Formato: /salva \"risposta\"{Colors.END}", flush=True)
                continue
            risposta_finale = match.group(1)
            
            storico = stato.get("storico_chat", [])
            testo_conv = "\n".join(storico)
            
            if testo_conv.strip():
                prompt_riassunto = f"""Genera un riassunto NARRATIVO e TECNICO della seguente conversazione socratica.

EVIDENZA: {ev}
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
            
            # Aggiorna il file con la discussione
            contenuto_attuale = read_file_safe(file_path)
            nuovo_blocco = f"\n\n### Evidenza {stato['indice']+1}: {ev}\n"
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
            print(f"{Colors.GREEN}✅ Salvato nel file: domanda, conversazione, riassunto narrativo, risposta.{Colors.END}", flush=True)
            print(flush=True)
            
            stato["indice"] += 1
            stato["conversazioni"].append({})
            stato["domanda_corrente"] = None
            stato["evidenziazione_corrente"] = None
            stato["storico_chat"] = []
            save_stato(stato)
            
            if stato["indice"] < len(stato.get("evidenziazioni", [])):
                avvia_evidenziazione()
            else:
                print(f"\n{Colors.GREEN}🎉 Tutte le evidenze discusse e salvate!{Colors.END}", flush=True)
                print(f"   Usa /fine per il riassunto finale unificato (IL MIO SAPERE).", flush=True)
                print(flush=True)
            return
        
        if user_input.lower() == "/archivia":
            cmd_archivia()
            return
        
        else:
            storico = stato.get("storico_chat", [])
            storico.append(f"Utente: {user_input}")
            
            msg_chat = [{"role":"user","content":f"""Evidenza: {ev}
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
            print(flush=True)

# ============================================================
# COMANDO /fine (riassunto finale)
# ============================================================

def cmd_fine():
    """Genera riassunto narrativo unificato di tutte le evidenze (IL MIO SAPERE)"""
    stato = load_stato()
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file attivo{Colors.END}", flush=True)
        return
    
    file_path = Path(stato.get("file_path", stato["file_corrente"]))
    if not file_path.exists():
        file_path = RAW / stato["file_corrente"]
        if not file_path.exists():
            file_path = SANDBOX / stato["file_corrente"]
        if not file_path.exists():
            print(f"{Colors.RED}❌ File non trovato{Colors.END}", flush=True)
            return
    
    contenuto = read_file_safe(file_path)
    
    if "## ✅ IL MIO SAPERE" in contenuto and "NON ANCORA GENERATO" not in contenuto:
        print(f"{Colors.YELLOW}⚠️ Il riassunto finale esiste già. Non lo rigenero.{Colors.END}", flush=True)
        return
    
    # Estrai le discussioni salvate
    riassunti_evidenze = []
    blocchi = re.findall(r'### Evidenza \d+: (.+?)\n\*\*Domanda:\*\* (.+?)\n\*\*Riassunto della conversazione:\*\*\n\n(.*?)\n\n\*\*Risposta finale:\*\* (.+?)(?:\n---|$)', contenuto, re.DOTALL)
    
    for ev, dom, riass, risp in blocchi:
        riassunti_evidenze.append(f"**{ev}**\nDomanda: {dom}\nDiscussione: {riass}\nRisposta: {risp}")
    
    if not riassunti_evidenze:
        print(f"{Colors.YELLOW}⚠️ Non trovate evidenze salvate. Esegui prima /chat e /salva.{Colors.END}", flush=True)
        return
    
    testo_riassunti = "\n\n---\n\n".join(riassunti_evidenze)
    
    prompt_unificato = f"""Genera un RIASSUNTO NARRATIVO UNIFICATO di TUTTE le seguenti evidenze discusse.

EVIDENZE:
{testo_riassunti}

REGOLE:
1. Scrivi in prima persona ("Ho compreso che...", "È emerso che...")
2. Forma narrativa fluida (nessun punto elenco, nessuna lista)
3. Usa linguaggio tecnico preciso ma non divulgativo
4. Trova un FILO LOGICO che collega le diverse evidenze tra loro
5. Metti in luce le tensioni ricorrenti, le scoperte concettuali, i punti ancora aperti
6. Lunghezza proporzionale alla complessità (minimo 1000 caratteri)

Rispondi SOLO con il riassunto, in italiano."""
    
    riassunto_unificato = call_llm(build_system(), [{"role":"user","content":prompt_unificato}])
    
    if "## ✅ IL MIO SAPERE" in contenuto:
        contenuto = re.sub(r'## ✅ IL MIO SAPERE\n.*?(?=\n##|$)', f"## ✅ IL MIO SAPERE\n\n{riassunto_unificato}\n", contenuto, flags=re.DOTALL)
    else:
        contenuto += f"\n## ✅ IL MIO SAPERE\n\n{riassunto_unificato}\n"
    
    write_file_safe(file_path, contenuto)
    print(f"{Colors.GREEN}✅ Riassunto unificato aggiunto al file (IL MIO SAPERE).{Colors.END}", flush=True)
    print(flush=True)
    stato["fase"] = "COMPLETATA"
    save_stato(stato)

# ============================================================
# COMANDO /analizza (INGEST dopo la discussione)
# ============================================================

def cmd_ingest_diretto(src: Path, contenuto: str):
    """Ingest diretto per file piccoli (≤ CHUNK_SIZE)"""
    print(f"\n{Colors.GREEN}📥 Ingest diretto: {src.name}{Colors.END}", flush=True)
    
    out_name = f"sdbx_{src.stem}_V1.md"
    out_file = SANDBOX / out_name
    
    msg = [{"role": "user", "content": f"""Analizza questa fonte e scrivi un riassunto ESAUSTIVO in italiano che segua fedelmente la struttura e il filo logico del documento originale.

Fonte: {src.name}
Contenuto: {contenuto[:15000]}

REGOLE FONDAMENTALI:
1. Mantieni i termini tecnici originali
2. Segui la struttura originale
3. Flusso narrativo continuo
4. Preserva i dati quantitativi
5. Taglia il superfluo

STRUTTURA RICHIESTA NEL FILE:

# 📌 SINTESI ESAUSTIVA

(riassunto in paragrafi continui, seguendo l'ordine originale del documento)

---

## 🗨️ DISCUSSIONE SOCRATICA

(Lascia vuoto)

---

## ✅ IL MIO SAPERE

(Lascia vuoto)
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
    print(f"{Colors.GREEN}✅ Sandbox creato: {out_name}{Colors.END}", flush=True)
    print(f"{Colors.YELLOW}✏️ Ora aggiungi ??...?? nel file e usa /chat{Colors.END}", flush=True)
    
    stato = load_stato()
    stato["fase"] = "INGEST_COMPLETATO"
    stato["file_corrente"] = out_name
    save_stato(stato)

def cmd_analizza(filepath: str):
    """Analizza un file (dopo la discussione) e crea sandbox per la wiki"""
    src = RAW / filepath
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in raw/: {filepath}{Colors.END}", flush=True)
        return
    
    contenuto = read_file_safe(src)
    parole = len(contenuto.split())
    num_chunk = (parole // CHUNK_SIZE) + (1 if parole % CHUNK_SIZE > 0 else 0)
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}", flush=True)
    print(f"{Colors.BOLD}📊 ANALISI FILE: {src.name}{Colors.END}", flush=True)
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n", flush=True)
    
    print(f"{Colors.CYAN}📏 Dimensioni:{Colors.END}", flush=True)
    print(f"   - Parole: {parole}", flush=True)
    print(f"   - Chunk necessari: {num_chunk}\n", flush=True)
    
    if parole <= CHUNK_SIZE:
        print(f"{Colors.GREEN}✅ File ottimale ({parole} parole ≤ {CHUNK_SIZE}).{Colors.END}", flush=True)
    else:
        print(f"{Colors.YELLOW}⚠️ File lungo ({parole} parole > {CHUNK_SIZE}). Sarà suddiviso in {num_chunk} chunk.{Colors.END}", flush=True)
    
    print(f"\n{Colors.YELLOW}📌 Procedere con l'ingest?{Colors.END}", flush=True)
    scelta = safe_input_semplice(f"{Colors.CYAN}👉 (s/n): {Colors.END}").lower()
    
    if scelta != 's':
        print(f"{Colors.RED}❌ Operazione annullata.{Colors.END}", flush=True)
        return
    
    if parole <= CHUNK_SIZE:
        cmd_ingest_diretto(src, contenuto)
    else:
        # ingest_chunk sarebbe qui
        pass

# ============================================================
# COMANDO /promuovi (CREAZIONE WIKI)
# ============================================================

def cmd_promuovi(titolo: str):
    """Promuove il sandbox a pagina wiki con nuova struttura"""
    stato = load_stato()
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file sandbox attivo. Esegui /analizza prima.{Colors.END}", flush=True)
        return
    
    sandbox_path = SANDBOX / stato["file_corrente"]
    if not sandbox_path.exists():
        # Prova a cercare in raw/
        raw_path = RAW / stato["file_corrente"]
        if raw_path.exists():
            sandbox_path = raw_path
        else:
            print(f"{Colors.RED}❌ File non trovato: {sandbox_path}{Colors.END}", flush=True)
            return

    contenuto_sandbox = read_file_safe(sandbox_path)

    sintesi_esaustiva = estrai_sezione(contenuto_sandbox, r'# 📌 SINTESI ESAUSTIVA')
    il_mio_sapere = estrai_sezione(contenuto_sandbox, r'## ✅ IL MIO SAPERE')

    if not il_mio_sapere:
        print(f"{Colors.YELLOW}⚠️ Sezione 'IL MIO SAPERE' non trovata. Esegui /fine prima di promuovere.{Colors.END}", flush=True)
        print(f"   Generazione automatica in corso...", flush=True)
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
        
        print(f"{Colors.YELLOW}⚠️ Pagina '{titolo}' già esistente.{Colors.END}", flush=True)
        print(f"   Creerò una nuova versione: '{titolo_finale}'", flush=True)
        print(f"   Con wikilink alla versione originale: [[{titolo}]]", flush=True)
        print(flush=True)
    else:
        wiki_path = wiki_path_base
        titolo_finale = titolo

    # Proposta dominio/tipo
    print(f"{Colors.CYAN}🤖 Analizzo il contenuto per proporre dominio e tipo...{Colors.END}", flush=True)
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
    print(f"{Colors.CYAN}🤖 Generazione struttura wiki dalla SINTESI ESAUSTIVA...{Colors.END}", flush=True)
    
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
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}", flush=True)
    print(f"{Colors.BOLD}📝 CREAZIONE NUOVA PAGINA WIKI{Colors.END}", flush=True)
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n", flush=True)
    print(f"{Colors.GREEN}Titolo:{Colors.END} {titolo_finale}", flush=True)
    if wikilink_originale:
        print(f"{Colors.CYAN}🔗 Link alla versione originale: [[{wikilink_originale}]]{Colors.END}", flush=True)

    print(f"\n{Colors.YELLOW}📌 Scegli il DOMINIO:{Colors.END}", flush=True)
    for i, d in enumerate(domini_validi, 1):
        default = " (proposto)" if d == dominio_proposto else ""
        print(f"  {i}. {d}{default}", flush=True)
    print(f"  {len(domini_validi)+1}. Inserisci manualmente", flush=True)
    scelta_dom = safe_input_semplice(f"{Colors.CYAN}👉 Numero (invio per {dominio_proposto}): {Colors.END}").strip()
    if scelta_dom == "":
        dominio_finale = dominio_proposto
    elif scelta_dom.isdigit() and 1 <= int(scelta_dom) <= len(domini_validi):
        dominio_finale = domini_validi[int(scelta_dom)-1]
    elif scelta_dom == str(len(domini_validi)+1):
        dominio_finale = safe_input_semplice(f"{Colors.CYAN}Dominio: {Colors.END}").strip() or dominio_proposto
    else:
        dominio_finale = dominio_proposto

    print(f"\n{Colors.YELLOW}📌 Scegli il TIPO:{Colors.END}", flush=True)
    for i, t in enumerate(tipi_validi, 1):
        default = " (proposto)" if t == tipo_proposto else ""
        print(f"  {i}. {t}{default}", flush=True)
    print(f"  {len(tipi_validi)+1}. Inserisci manualmente", flush=True)
    scelta_tipo = safe_input_semplice(f"{Colors.CYAN}👉 Numero (invio per {tipo_proposto}): {Colors.END}").strip()
    if scelta_tipo == "":
        tipo_finale = tipo_proposto
    elif scelta_tipo.isdigit() and 1 <= int(scelta_tipo) <= len(tipi_validi):
        tipo_finale = tipi_validi[int(scelta_tipo)-1]
    elif scelta_tipo == str(len(tipi_validi)+1):
        tipo_finale = safe_input_semplice(f"{Colors.CYAN}Tipo: {Colors.END}").strip() or tipo_proposto
    else:
        tipo_finale = tipo_proposto

    # Fonti
    fonti_match = re.search(r'fonte: (.*?)(?:\n|$)', contenuto_sandbox)
    fonti = [f.strip() for f in fonti_match.group(1).split(',')] if fonti_match else []
    fonti_str = ", ".join([f"[[{f}]]" for f in fonti])
    
    # Numero di cicli SPB
    evidenze_risposte = re.findall(r'### Evidenza \d+:', contenuto_sandbox)
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

    print(f"\n{Colors.GREEN}✅ Pagina wiki creata: {wiki_path}{Colors.END}", flush=True)
    print(f"{Colors.GREEN}✅ Indice e log aggiornati.{Colors.END}", flush=True)
    
    # Archivia il sandbox
    if sandbox_path.exists():
        arch_path = ARCHIVIATI / sandbox_path.name
        shutil.move(str(sandbox_path), str(arch_path))
        print(f"{Colors.YELLOW}🗂️ Sandbox archiviato in: {arch_path}{Colors.END}", flush=True)
    
    print(flush=True)
    reset_stato()
    costruisci_indice()

# ============================================================
# COMANDI ESISTENTI (list, riprendi, archivia, query, lint, backup, stato)
# ============================================================

def cmd_list(cartella: str = None):
    cartelle = {"asset":ASSET,"clippings":CLIPPINGS,"backups":BACKUPS,"raw":RAW,"sandbox":SANDBOX,"wiki":WIKI}
    if cartella and cartella in cartelle:
        path = cartelle[cartella]
        files = list(path.glob("*"))
        print(f"\n{Colors.CYAN}📁 {cartella}/ ({len(files)} elementi){Colors.END}", flush=True)
        for f in files[:20]:
            print(f"  - {f.name}", flush=True)
    elif not cartella or cartella=="all":
        for name,path in cartelle.items():
            files = list(path.glob("*"))
            print(f"\n{Colors.CYAN}📁 {name}/ ({len(files)} elementi){Colors.END}", flush=True)
            for f in files[:10]:
                print(f"  - {f.name}", flush=True)
            if len(files)>10:
                print(f"  ... e altri {len(files)-10}", flush=True)
    else:
        print(f"{Colors.RED}❌ Cartella sconosciuta{Colors.END}", flush=True)
    print(flush=True)

def cmd_riprendi(filename: str):
    """Ripristina un file sandbox archiviato"""
    if not filename.endswith(".md"):
        filename = filename + ".md"
    if not filename.startswith("sdbx_"):
        filename = f"sdbx_{filename}"
    
    src = ARCHIVIATI / filename
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in archiviati/: {filename}{Colors.END}", flush=True)
        return
    
    dest = SANDBOX / src.name
    shutil.copy2(str(src), str(dest))
    print(f"{Colors.GREEN}✅ File ripristinato: {dest}{Colors.END}", flush=True)
    
    stato = load_stato()
    stato["file_corrente"] = src.name
    stato["fase"] = "INGEST_COMPLETATO"
    stato["evidenziazioni"] = []
    stato["conversazioni"] = []
    stato["indice"] = 0
    save_stato(stato)
    print(f"{Colors.CYAN}💡 Ora usa /chat per continuare.{Colors.END}", flush=True)

def cmd_archivia():
    """Archivia la discussione corrente"""
    stato = load_stato()
    if stato.get("file_corrente"):
        src = Path(stato.get("file_path", stato["file_corrente"]))
        if not src.exists():
            src = SANDBOX / stato["file_corrente"]
        if src.exists():
            arch = ARCHIVIATI / f"archiviato_{src.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            shutil.move(str(src), str(arch))
            print(f"{Colors.YELLOW}🗂️ Archiviato: {arch}{Colors.END}", flush=True)
    reset_stato()
    print(f"{Colors.GREEN}✅ Discussione archiviata{Colors.END}", flush=True)

def cmd_query(domanda: str):
    """Interroga il wiki usando indice leggero + ricerca web"""
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
        
        msg = [{"role":"user","content":f"Domanda: {domanda}\n\nPagine wiki rilevanti:\n{ctx}\nRispondi in italiano."}]
        risposta_wiki = call_llm(build_system(), msg)
    
    if risposta_wiki and "INFO_INSUFFICIENTI" not in risposta_wiki and len(risposta_wiki) > 150:
        for fonte in fonti_wiki:
            risposta_wiki = risposta_wiki.replace(f"[[{fonte}]]", f"[WIKI] [[{fonte}]]")
        print(f"\n{Colors.CYAN}[WIKI] {Colors.END}", flush=True)
        print_wrapped(risposta_wiki)
        return
    
    print(f"\n{Colors.DIM}⚠️ Ricerca online in corso...{Colors.END}\n", flush=True)
    risultati_web = web_search_brave(domanda, num_results=5)
    
    if not risultati_web:
        if risposta_wiki:
            print_wrapped(f"[WIKI] {risposta_wiki}")
        else:
            print(f"{Colors.YELLOW}⚠️ Nessun risultato trovato.{Colors.END}", flush=True)
        return

def cmd_lint():
    print(f"\n{Colors.CYAN}🔬 LINT DEL WIKI{Colors.END}", flush=True)
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
        print(f"{Colors.RED}🔴 Pagine orfane: {len(orphans)}{Colors.END}", flush=True)
    else:
        print(f"{Colors.GREEN}✅ Nessuna orfana{Colors.END}", flush=True)
    
    old = []
    for f in SANDBOX.glob("sdbx_*.md"):
        age = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        if age>30:
            old.append((f.name,age))
    if old:
        print(f"{Colors.YELLOW}🟡 Sandbox attivi da >30gg: {len(old)}{Colors.END}", flush=True)
    else:
        print(f"{Colors.GREEN}✅ Nessun sandbox vecchio{Colors.END}", flush=True)
    print(flush=True)

def cmd_backup():
    print(f"{Colors.CYAN}💾 Backup...{Colors.END}", flush=True)
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
    print(f"{Colors.GREEN}✅ Backup: {bkp}{Colors.END}", flush=True)

def cmd_stato():
    stato = load_stato()
    print(f"\n{Colors.BLUE}📊 STATO{Colors.END}", flush=True)
    print(f"  Provider: {Colors.CYAN}{PROVIDER_NOME}{Colors.END}", flush=True)
    print(f"  Modello attivo: {Colors.CYAN}{CURRENT_MODEL}{Colors.END}", flush=True)
    print(f"  Fase: {stato.get('fase','nessuna')}", flush=True)
    print(f"  File: {stato.get('file_corrente','nessuno')}", flush=True)
    print(f"  Evidenze: {len(stato.get('evidenziazioni',[]))} trovate, indice {stato.get('indice',0)}", flush=True)
    print(f"  raw/: {len(list(RAW.glob('*')))} | wiki/: {len(list(WIKI.glob('*.md')))}", flush=True)
    print(f"  sandbox/ (attivi): {len(list(SANDBOX.glob('sdbx_*.md')))}", flush=True)
    print(flush=True)

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def print_banner():
    modello_nome = CURRENT_MODEL if CURRENT_MODEL else "Non selezionato"
    provider_nome = PROVIDER_NOME if PROVIDER_NOME else "Non selezionato"
    print(f"""
{Colors.BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║     SISTEMA SOCRATES-PLATO-BAYES - Versione Definitiva       ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}Provider:{Colors.END} {Colors.CYAN}{provider_nome}{Colors.END}
{Colors.YELLOW}Modello attivo:{Colors.END} {Colors.CYAN}{modello_nome}{Colors.END}
{Colors.YELLOW}Soglia chunk:{Colors.END} {Colors.CYAN}{CHUNK_SIZE} parole{Colors.END}

{Colors.BLUE}{'='*60}{Colors.END}
{Colors.BOLD}📋 COMANDI DISPONIBILI:{Colors.END}
{Colors.BLUE}{'='*60}{Colors.END}

{Colors.MAGENTA}✂️  ESTRAZIONE{Colors.END}
  /estrai                         Estrae evidenze %%...%% e crea estratto_nome.md

{Colors.GREEN}📥 ANALISI E INGEST{Colors.END}
  /analizza <file>                Analizza dimensioni, mostra chunk necessari,
                                  chiede conferma ed esegue ingest

{Colors.YELLOW}💬 DISCUSSIONE SOCRATICA{Colors.END}
  /chat [file]                    Avvia/riprendi discussione
  /salva "risposta"               Salva evidenza (riassunto narrativo)
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
  • usa %%...%% per estrarre argomenti (sintesi)
  • usa ??...?? per evidenziare argomenti da discutere (chat)
  • usa TAB per autocompletare nomi file
  • In /chat: usa /salta (salta evidenza), /pausa (salva sessione)
""", flush=True)

    raw_files = list(RAW.glob("*.md"))
    print(f"{Colors.CYAN}📁 File disponibili in raw/:{Colors.END}", flush=True)
    if raw_files:
        for f in raw_files[:10]:
            print(f"   - {f.name}", flush=True)
        if len(raw_files)>10:
            print(f"   ... e altri {len(raw_files)-10}", flush=True)
    else:
        print(f"   {Colors.DIM}(vuoto){Colors.END}", flush=True)

# ============================================================
# MENU PRINCIPALE
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
                files = [f.name for f in RAW.glob("*.md") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        
        return None

def main():
    clear_screen()
    
    print("=" * 60, flush=True)
    print("🧠 SISTEMA SOCRATES-PLATO-BAYES (SPB)", flush=True)
    print("   Supporta: DeepSeek Ufficiale | SiliconFlow", flush=True)
    print("=" * 60, flush=True)
    
    provider_key, model_id, api_key = scegli_provider_e_modello_ingest()
    if provider_key is None:
        print("\n👋 Arrivederci!", flush=True)
        return
    
    provider_config = PROVIDER_CONFIG[provider_key]
    base_url = provider_config["base_url"]
    
    global DEEPSEEK_API_KEY, CURRENT_MODEL, CLIENT, PROVIDER_NOME
    DEEPSEEK_API_KEY = api_key
    CURRENT_MODEL = model_id
    PROVIDER_NOME = provider_config["nome"]
    CLIENT = OpenAI(api_key=api_key, base_url=base_url)
    
    print(f"\n✅ Provider: {provider_config['nome']}", flush=True)
    print(f"✅ Modello: {model_id}", flush=True)
    
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

    while True:
        try:
            inp = safe_input_semplice(f"{Colors.GREEN}spb>{Colors.END} ").strip()
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
                    print(f"{Colors.RED}❌ Specifica il file: /analizza documento.md{Colors.END}", flush=True)
            elif cmd == "/chat":
                cmd_chat(arg if arg else None)
            elif cmd == "/salva":
                print(f"{Colors.YELLOW}⚠️ Usa /salva durante la chat (dopo /chat){Colors.END}", flush=True)
            elif cmd == "/fine":
                cmd_fine()
            elif cmd == "/promuovi":
                if arg:
                    cmd_promuovi(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il titolo: /promuovi \"Titolo della pagina\"{Colors.END}", flush=True)
            elif cmd == "/riprendi":
                if arg:
                    cmd_riprendi(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file da riprendere{Colors.END}", flush=True)
            elif cmd == "/archivia":
                cmd_archivia()
            elif cmd == "/query":
                if arg:
                    cmd_query(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica la domanda: /query \"testo\"{Colors.END}", flush=True)
            elif cmd == "/lint":
                cmd_lint()
            elif cmd == "/backup":
                cmd_backup()
            elif cmd == "/stato":
                cmd_stato()
            elif cmd in ["/help","/?"]:
                print_banner()
            else:
                print(f"{Colors.RED}❌ Comando sconosciuto.{Colors.END}", flush=True)
        except KeyboardInterrupt:
            print(f"\n{Colors.BLUE}👋 Bye{Colors.END}", flush=True)
            break
        except Exception as e:
            print(f"{Colors.RED}❌ {e}{Colors.END}", flush=True)

if __name__ == "__main__":
    main()