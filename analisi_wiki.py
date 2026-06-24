#!/usr/bin/env python3
"""
analisi_w.py — Sistema Socrates–Plato–Bayes (SPB) - Versione Definitiva
Flusso: marcatori in raw/ → /analizza → sandbox → /chat → /salva → /promuovi

MARCATORI NEL FILE raw/:
  >>...<<  → COPIA il testo nella sezione EVIDENZE (non influenza la sintesi)
  ??...??  → GENERA una domanda socratica nella sezione DOMANDE

Supporta: DeepSeek Ufficiale e SiliconFlow
MODIFICA: chat ibrida - LLM può rispondere direttamente o usare approccio socratico
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
from typing import Optional
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
    print()
    print(prompt, end='', flush=True)
    return input()

def safe_input_semplice(prompt):
    print()
    return input(prompt)

# ============================================================
# DESCRIZIONI MODELLI
# ============================================================

MODEL_DESCRIPTIONS = {
    "deepseek-v4-pro": "🔥 DeepSeek V4 Pro - Modello di punta",
    "deepseek-v4-flash": "⚡ DeepSeek V4 Flash - Veloce ed economico",
    "deepseek-chat": "💬 DeepSeek Chat - Standard",
    "deepseek-reasoner": "🧠 DeepSeek Reasoner - Ragionamento",
    "deepseek-ai/DeepSeek-V3": "💬 Chat generale, ragionamento, codice",
    "deepseek-ai/DeepSeek-R1": "🧠 Ragionamento avanzato, matematica, logica",
    "deepseek-ai/DeepSeek-V2": "⚡ Bilanciato, veloce ed economico",
    "Qwen/Qwen2.5-72B-Instruct": "📝 Traduzioni, scrittura, analisi testi",
    "Qwen/Qwen2.5-32B-Instruct": "📝 Traduzioni, scrittura (più economico)",
    "Qwen/Qwen2.5-14B-Instruct": "📝 Traduzioni leggere, veloci",
    "Qwen/Qwen2.5-7B-Instruct": "📝 Traduzioni ultra-leggere",
    "Qwen/Qwen3-VL-30B-A3B-Instruct": "👁️ OCR avanzato + traduzione",
    "Qwen/Qwen3-VL-8B-Instruct": "👁️ OCR veloce + traduzione leggera",
    "Qwen/Qwen3-VL-32B-Instruct": "👁️ OCR alta qualità + traduzione",
    "meta-llama/Meta-Llama-3.1-70B-Instruct": "💬 Chat, ragionamento, codice",
    "meta-llama/Meta-Llama-3.1-8B-Instruct": "💬 Chat leggera, veloce",
    "meta-llama/Llama-3.2-3B-Instruct": "💬 Chat ultra-leggera",
    "OpenGVLab/InternVL2-8B": "👁️ Visione, OCR, analisi immagini",
    "OpenGVLab/InternVL2-26B": "👁️ Visione avanzata, OCR",
    "ZhipuAI/GLM-4-9B": "💬 Chat, ragionamento, codice",
    "01-ai/Yi-1.5-34B": "💬 Chat, ragionamento",
    "01-ai/Yi-1.5-9B": "💬 Chat leggera, veloce",
    "mistralai/Mistral-7B-Instruct-v0.2": "💬 Chat efficiente, codice",
    "zai-org/GLM-5.2": "coding",
}

# ============================================================
# CONFIGURAZIONE PROVIDER
# ============================================================

def carica_api_keys_ingest() -> dict[str, str | None]:
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

PROVIDER_CONFIG = {
    "deepseek": {
        "nome": "DeepSeek Ufficiale",
        "base_url": "https://api.deepseek.com",
        "modelli": ["deepseek-chat", "deepseek-reasoner", "deepseek-v4-pro"]
    },
    "siliconflow": {
        "nome": "SiliconFlow",
        "base_url": "https://api.siliconflow.com/v1",
        "modelli": [
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "deepseek-ai/DeepSeek-V2",
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "zai-org/GLM-5.2"
        ]
    }
}

def scegli_provider_e_modello_ingest() -> tuple[str | None, str | None, str | None]:
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
                    continue
                print(f"\n🤖 Modelli disponibili su {provider_config['nome']}:", flush=True)
                print("-" * 60, flush=True)
                for i, model_id in enumerate(provider_config['modelli'], 1):
                    desc = MODEL_DESCRIPTIONS.get(model_id, "💬 Modello generico")
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
# VARIABILI GLOBALI
# ============================================================

DEEPSEEK_API_KEY = None
CURRENT_MODEL = None
CLIENT = None
PROVIDER_NOME = None
CHUNK_SIZE = 1500
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
    # Pulisci spazi trailing e righe vuote eccessive prima di scrivere
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    cleaned = []
    empty_count = 0
    for line in lines:
        if line == '':
            empty_count += 1
            if empty_count <= 1:
                cleaned.append(line)
        else:
            empty_count = 0
            cleaned.append(line)
    content = '\n'.join(cleaned).strip() + '\n'
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
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_entry = f"## [{today}] {operation}\n{details}\n\n"
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def call_llm(system: str, messages: list, allow_search: bool = False, model: str = None) -> str:
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
Regole: Fase INGEST: sintesi ESAUSTIVA in paragrafi continui. Fase CHAT: conversazione socratica.
Mantieni un tono colloquiale ma rigoroso.
{read_agent_md()}"""
    base += """
REGOLA ASSOLUTA: Non puoi eseguire comandi di sistema, creare file, leggere directory o simulare operazioni sul filesystem. Se l'utente ti chiede di farlo, rispondi che non hai accesso diretto al filesystem e suggerisci il comando SPB corretto (es. /list, /stato). Non confermare mai la creazione o modifica di file che non hai effettivamente scritto tu.
"""
    if enable_search:
        base += """
RICERCA ESTERNA ABILITATA: Se ritieni utile approfondire un tema con dati, esempi o controesempi dal web, usa "🔍 RICERCA: [query]".
"""
    return base

# ============================================================
# FUNZIONI DI ESTRAZIONE MARCATORI
# ============================================================

def estrai_blocchi_copia(contenuto: str) -> list[str]:
    """Estrae i blocchi >>...<< (testo da copiare nelle evidenze)"""
    pattern = r'>>([\s\S]*?)<<'
    matches = re.findall(pattern, contenuto, re.DOTALL)
    return [m.strip() for m in matches]

def estrai_domande_socratiche(contenuto: str) -> list[str]:
    """Estrae le domande ??...?? (da trasformare in discussione socratica)"""
    pattern = r'\?\?([\s\S]*?)\?\?'
    matches = re.findall(pattern, contenuto, re.DOTALL)
    return [m.strip() for m in matches]

def rimuovi_marcatori(contenuto: str) -> str:
    """Rimuove tutti i marcatori >>...<< e ??...?? dal testo per la sintesi"""
    # Rimuovi >>...<<
    testo = re.sub(r'>>.*?<<', '', contenuto, flags=re.DOTALL)
    # Rimuovi ??...??
    testo = re.sub(r'\?\?.*?\?\?', '', testo, flags=re.DOTALL)
    # Pulisci spazi multipli
    testo = re.sub(r'\n\s*\n', '\n\n', testo)
    return testo.strip()

def estrai_evidenze_da_sezione(contenuto: str) -> str:
    """Estrae il contenuto della sezione EVIDENZE dal sandbox"""
    match = re.search(r'## 📌 EVIDENZE DA DISCUTERE\n+(.*?)(?=\n##|\n---|\Z)', contenuto, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

# ============================================================
# CHECKPOINT E ROLLBACK
# ============================================================

def salva_checkpoint(operazione: str, file_corrente: str, stato: dict):
    checkpoint = {
        "operazione": operazione,
        "file_corrente": file_corrente,
        "stato": stato,
        "timestamp": datetime.now().isoformat()
    }
    write_file_safe(CHECKPOINT_PATH, json.dumps(checkpoint, ensure_ascii=False, indent=2))

def carica_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        try:
            return json.loads(read_file_safe(CHECKPOINT_PATH))
        except:
            return {}
    return {}

def ripulisci_file_orfani():
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
# RICERCA WEB
# ============================================================

def web_search_brave(query: str, num_results: int = 5) -> list:
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
    import urllib.parse, urllib.request
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
# COMANDO /analizza (INGEST CON MARCATORI)
# ============================================================

def cmd_analizza(filepath: str):
    """
    Analizza il file in raw/ con marcatori:
    >>...<< → copia il testo nella sezione EVIDENZE
    ??...?? → genera domanda socratica nella sezione DOMANDE
    La sintesi ESAUSTIVA è indipendente dai marcatori
    """
    src = RAW / filepath
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in raw/: {filepath}{Colors.END}", flush=True)
        return
    
    print(f"\n{Colors.CYAN}📖 Analisi di: {src.name}{Colors.END}", flush=True)
    print(f"{Colors.DIM}   Identifico marcatori >>...<< e ??...??{Colors.END}", flush=True)
    
    contenuto_originale = read_file_safe(src)
    
    # Estrai blocchi e domande
    blocchi_copia = estrai_blocchi_copia(contenuto_originale)
    domande = estrai_domande_socratiche(contenuto_originale)
    
    # Rimuovi marcatori per la sintesi
    testo_pulito = rimuovi_marcatori(contenuto_originale)
    
    print(f"{Colors.GREEN}   Trovati {len(blocchi_copia)} blocchi da copiare (>>...<<){Colors.END}", flush=True)
    print(f"{Colors.GREEN}   Trovate {len(domande)} domande socratiche (??...??){Colors.END}", flush=True)
    
    # Genera sintesi esaustiva (indipendente dai marcatori)
    print(f"\n{Colors.DIM}🤖 Generazione sintesi esaustiva...{Colors.END}", flush=True)
    
    prompt_sintesi = f"""Genera una SINTESI ESAUSTIVA del seguente documento.

DOCUMENTO:
{testo_pulito}

REGOLE FONDAMENTALI:
1. Scrivi in paragrafi continui (NESSUN punto elenco, NESSUNA lista)
2. Segui l'ordine originale del documento
3. Mantieni i termini tecnici originali
4. Preserva tutti i dati quantitativi (numeri, date, percentuali)
5. La sintesi DEVE essere INDIPENDENTE dai marcatori:
   - >>...<< sono evidenze (da ignorare per la sintesi)
   - ??...?? sono domande socratiche (da ignorare per la sintesi)
6. Struttura: Introduzione → Sviluppo → Conclusioni

La sintesi deve essere completa e fluida."""
    
    msg = [{"role": "user", "content": prompt_sintesi}]
    sintesi = call_llm(build_system(), msg)
    
    # Prepara il contenuto del sandbox
    out_name = f"sdbx_{src.stem}_V1.md"
    out_file = SANDBOX / out_name
    
    # Costruisci sezione EVIDENZE
    evidenze_text = ""
    if blocchi_copia:
        for i, blocco in enumerate(blocchi_copia, 1):
            evidenze_text += f"### Evidenza {i}\n\n>>{blocco}<<\n\n"
    else:
        evidenze_text = "(nessuna evidenza marcata con >>...<<)\n"
    
    # Costruisci sezione DOMANDE
    domande_text = ""
    if domande:
        for i, domanda in enumerate(domande, 1):
            domande_text += f"### Domanda {i}\n\n??{domanda}??\n\n"
    else:
        domande_text = "(nessuna domanda marcata con ??...??)\n"
    
    # Rimuovi eventuale header duplicato che l'LLM include nella sintesi
    sintesi_pulita = re.sub(r'^#+ 📌 SINTESI ESAUSTIVA\s*\n', '', sintesi.strip(), flags=re.IGNORECASE)
    sintesi_pulita = re.sub(r'^# SINTESI ESAUSTIVA\s*\n', '', sintesi_pulita, flags=re.IGNORECASE)

    full_content = f"""---
stato: BOZZA
lingua: italiano
fonte: {src.name}
data_ingest: {date.today()}
---

# 📌 SINTESI ESAUSTIVA

{sintesi_pulita}

---

## 📌 EVIDENZE DA DISCUTERE

{evidenze_text}
---

## ❓ DOMANDE DA DISCUTERE

{domande_text}
"""
    
    write_file_safe(out_file, full_content)
    
    print(f"\n{Colors.GREEN}✅ Sandbox creato: {out_name}{Colors.END}", flush=True)
    print(f"{Colors.CYAN}📁 Posizione: {out_file}{Colors.END}", flush=True)
    print(f"\n{Colors.YELLOW}✏️  COSA FARE ORA:{Colors.END}", flush=True)
    print(f"   1. Apri il file in VS Code: {out_file}", flush=True)
    print(f"   2. Leggi la SINTESI ESAUSTIVA", flush=True)
    print(f"   3. Verifica le EVIDENZE copiate da >>...<<", flush=True)
    print(f"   4. Verifica le DOMANDE generate da ??...??", flush=True)
    print(f"   5. Se vuoi discutere, lancia /chat {out_name}", flush=True)
    print(flush=True)
    
    stato = load_stato()
    stato["fase"] = "INGEST_COMPLETATO"
    stato["file_corrente"] = out_name
    save_stato(stato)
    
    update_log("analizza", f"File: {src.name}\nEvidenze: {len(blocchi_copia)}\nDomande: {len(domande)}\nSandbox: {out_name}")

# ============================================================
# COMANDO /chat (DISCUSSIONE SOCRATICA - VERSIONE IBRIDA)
# ============================================================

def cmd_chat(filearg: str = None):
    """Avvia la discussione socratica su un file sandbox"""
    stato = load_stato()
    
    if filearg and filearg.strip():
        target_file = filearg.strip()
        if not target_file.endswith(".md"):
            target_file = target_file + ".md"
        
        # Cerca in sandbox/
        file_path = SANDBOX / target_file
        if not file_path.exists():
            # Cerca in raw/
            file_path = RAW / target_file
        if not file_path.exists():
            print(f"{Colors.RED}❌ File non trovato{Colors.END}", flush=True)
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
        file_path = SANDBOX / stato["file_corrente"]
        if not file_path.exists():
            file_path = RAW / stato["file_corrente"]
        if not file_path.exists():
            print(f"{Colors.RED}❌ File non trovato: {stato['file_corrente']}{Colors.END}", flush=True)
            return
    
    contenuto = read_file_safe(file_path)
    
    # Estrai domande ??...?? dalla sezione DOMANDE DA DISCUTERE
    domande = estrai_domande_socratiche(contenuto)
    
    if not domande:
        print(f"{Colors.YELLOW}⚠️ Nessuna domanda ??...?? trovata in {file_path.name}{Colors.END}", flush=True)
        print(f"   Aggiungi ??...?? nel file (sezione DOMANDE) e riprova.", flush=True)
        return
    
    print(f"{Colors.GREEN}🔍 Trovate {len(domande)} domande socratiche in {file_path.name}:{Colors.END}", flush=True)
    for d in domande:
        print(f"   • {d}", flush=True)
    print(flush=True)
    
    stato["fase"] = "IN_DISCUSSIONE"
    stato["evidenziazioni"] = domande
    stato["conversazioni"] = []
    stato["indice"] = 0
    stato["file_path"] = str(file_path)
    save_stato(stato)
    avvia_evidenziazione()

def avvia_evidenziazione():
    stato = load_stato()
    idx = stato["indice"]
    domande = stato.get("evidenziazioni", [])
    
    if idx >= len(domande):
        print(f"\n{Colors.GREEN}✅ Tutte le domande discusse!{Colors.END}", flush=True)
        print(f"   Usa /promuovi Titolo per creare la pagina wiki.", flush=True)
        print(flush=True)
        return
    
    domanda = domande[idx]
    
    # Leggi il file per estrarre le evidenze
    file_path = Path(stato.get("file_path", stato["file_corrente"]))
    evidenze = ""
    if file_path.exists():
        contenuto = read_file_safe(file_path)
        evidenze_raw = estrai_evidenze_da_sezione(contenuto)
        # Pulisci le evidenze per il prompt
        if evidenze_raw and "(nessuna" not in evidenze_raw:
            # Estrai solo il testo tra >>...<<
            blocchi = re.findall(r'>>([\s\S]*?)<<', evidenze_raw)
            if blocchi:
                evidenze = "\n".join([f"- {b.strip()}" for b in blocchi[:3]])  # Max 3 evidenze
            else:
                evidenze = evidenze_raw[:500]
        else:
            evidenze = "(nessuna evidenza marcata)"
    
    print(f"\n{Colors.MAGENTA}{'='*60}{Colors.END}", flush=True)
    print(f"{Colors.YELLOW}💬 Domanda {idx+1}/{len(domande)}: {domanda}{Colors.END}", flush=True)
    print(f"{Colors.MAGENTA}{'='*60}{Colors.END}", flush=True)
    
    # Avvia il dialogo socratico - VERSIONE IBRIDA MIGLIORATA
    msg = [{"role":"user","content":f"""Sei Socrate. L'utente ha posto questa domanda: "{domanda}"

EVIDENZE DAL TESTO (marcate dall'utente con >>...<<):
{evidenze}

IL TUO RUOLO - APPROCCIO IBRIDO:

**QUANDO RISPONDERE DIRETTAMENTE:**
- Domande fattuali ("quando è successo?", "quanti sono?", "chi ha detto?")
- Richieste di chiarimento tecnico ("come funziona?", "qual è la differenza tra X e Y?")
- Domande su definizioni ("cos'è esattamente...?")
- L'utente chiede esplicitamente una risposta

**QUANDO USARE APPROCCIO SOCRATICO:**
- Domande concettuali ("perché?", "ha senso?", "è giusto?")
- Domande aperte senza risposta univoca
- L'utente sta esplorando un tema nuovo
- Vuoi far emergere contraddizioni o tensioni

**REGOLA D'ORO:**
1. SE la domanda è fattuale → rispondi con chiarezza, precisione, dati
2. SE la domanda è concettuale → usa domande socratiche per guidare
3. PUOI mescolare: rispondere ai fatti E poi fare una domanda socratica

**STRUTTURA CONSIGLIATA PER RISPOSTE DIRETTE:**
1. Risposta chiara e diretta alla domanda
2. Eventuali dati/specifiche tecniche
3. Una domanda di approfondimento (se pertinente)

**STRUTTURA CONSIGLIATA PER APPROCCIO SOCRATICO:**
1. Apertura: analogia o esperimento mentale (NON una domanda, ma un'osservazione)
2. Riferimento a un'evidenza del testo: "Nel testo hai evidenziato che..."
3. Tensione: un paradosso o un controesempio che mette in crisi le risposte facili
4. Domanda finale: UNA domanda concreta, mirata, che invita l'utente a prendere posizione

NON correggere mai direttamente l'utente - anche quando rispondi, mantieni tono costruttivo.
NON rispondere alla domanda dell'utente se è concettuale - aiutalo a trovare la risposta da solo.
Se è fattuale, rispondi con precisione.

Rispondi in italiano, colloquiale ma rigoroso."""}]
    
    risposta_llm = call_llm(build_system(), msg)
    
    print(f"\n{Colors.CYAN}🤖 {risposta_llm}{Colors.END}", flush=True)
    print(flush=True)
    
    print(f"{Colors.DIM}📝 Comandi disponibili:{Colors.END}", flush=True)
    print(f"   {Colors.GREEN}/salva \"risposta\"{Colors.END} - salva la discussione", flush=True)
    print(f"   {Colors.YELLOW}/salta{Colors.END} - salta questa domanda", flush=True)
    print(f"   {Colors.YELLOW}/pausa{Colors.END} - salva e esci", flush=True)
    print(flush=True)
    
    stato["domanda_corrente"] = domanda
    stato["evidenziazione_corrente"] = domanda
    stato["storico_chat"] = []
    save_stato(stato)
    chat_libera()

def chat_libera():
    """Chat interattiva con approccio ibrido: risposte dirette o socratiche"""
    stato = load_stato()
    domanda = stato["domanda_corrente"]
    file_path = Path(stato.get("file_path", stato["file_corrente"]))
    evidenze = stato.get("evidenziazioni", [])
    idx = stato.get("indice", 0)
    
    while True:
        user_input = safe_input_semplice(f"{Colors.GREEN}tu> {Colors.END}").strip()
        if not user_input:
            continue
        
        if user_input.lower() == "/salta":
            print(f"{Colors.YELLOW}⏭️ Domanda saltata: {domanda}{Colors.END}", flush=True)
            stato["indice"] += 1
            stato["domanda_corrente"] = None
            stato["evidenziazione_corrente"] = None
            stato["storico_chat"] = []
            save_stato(stato)
            if stato["indice"] < len(evidenze):
                avvia_evidenziazione()
            else:
                print(f"\n{Colors.GREEN}🎉 Tutte le domande discusse/saltate!{Colors.END}", flush=True)
            return
        
        if user_input.lower() == "/pausa":
            salva_checkpoint("chat", stato.get("file_corrente"), {
                "indice": stato.get("indice", 0),
                "evidenziazioni": evidenze,
                "storico_chat": stato.get("storico_chat", []),
                "domanda_corrente": domanda,
                "evidenziazione_corrente": domanda
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
                prompt_riassunto = f"""Genera un riassunto NARRATIVO e TECNICO della seguente conversazione.

DOMANDA: {domanda}

CONVERSAZIONE:
{testo_conv}

REGOLE:
1. Scrivi in forma narrativa (nessun punto elenco, nessuna lista)
2. Usa linguaggio tecnico preciso ma non divulgativo
3. Racconta: la posizione iniziale dell'utente, le risposte/domande dell'LLM, l'evoluzione del dialogo, gli accordi/disaccordi, le domande aperte
4. Mantieni le sfumature e le tensioni emerse
5. Lunghezza proporzionale alla complessità della discussione

Rispondi SOLO con il riassunto, in italiano."""
                riassunto_conv = call_llm(build_system(), [{"role":"user","content":prompt_riassunto}])
            else:
                riassunto_conv = "Nessuna conversazione registrata."
            
            # Aggiorna il file
            contenuto_attuale = read_file_safe(file_path)
            # Preserva solo la prima occorrenza di "## ✅ IL MIO SAPERE" se esiste già
            nuovo_blocco = f"\n\n### Discussione {idx+1}: {domanda}\n\n"
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
            print(f"{Colors.GREEN}✅ Salvato nel file: conversazione, riassunto, risposta.{Colors.END}", flush=True)
            print(flush=True)
            
            stato["indice"] += 1
            stato["conversazioni"].append({})
            stato["domanda_corrente"] = None
            stato["evidenziazione_corrente"] = None
            stato["storico_chat"] = []
            save_stato(stato)
            
            if stato["indice"] < len(evidenze):
                avvia_evidenziazione()
            else:
                print(f"\n{Colors.GREEN}🎉 Tutte le domande discusse e salvate!{Colors.END}", flush=True)
                print(f"   Usa /promuovi Titolo per creare la pagina wiki.", flush=True)
                print(flush=True)
            return
        
        if user_input.lower() == "/archivia":
            cmd_archivia()
            return
        
        # Intercetta comandi slash inviati per errore durante la chat
        if user_input.startswith("/"):
            parts_cmd = user_input.split(maxsplit=1)
            cmd_inner = parts_cmd[0].lower()
            arg_inner = parts_cmd[1] if len(parts_cmd) > 1 else ""
            if cmd_inner == "/list":
                cmd_list(arg_inner if arg_inner else None)
            elif cmd_inner == "/stato":
                cmd_stato()
            elif cmd_inner == "/lint":
                cmd_lint()
            elif cmd_inner == "/backup":
                cmd_backup()
            else:
                print(f"{Colors.YELLOW}⚠️  Comando '{cmd_inner}' non disponibile durante /chat.{Colors.END}", flush=True)
                print(f"   Comandi validi in chat: /salva /salta /pausa /archivia /list /stato", flush=True)
            continue
        
        else:
            storico = stato.get("storico_chat", [])
            storico.append(f"Utente: {user_input}")
            
            # Leggi le evidenze per includerle nel contesto
            file_path = Path(stato.get("file_path", stato["file_corrente"]))
            evidenze_context = ""
            if file_path.exists():
                contenuto = read_file_safe(file_path)
                evidenze_raw = estrai_evidenze_da_sezione(contenuto)
                if evidenze_raw and "(nessuna" not in evidenze_raw:
                    blocchi = re.findall(r'>>([\s\S]*?)<<', evidenze_raw)
                    if blocchi:
                        evidenze_context = "\n".join([f"- {b.strip()}" for b in blocchi[:3]])
            
            # ============ VERSIONE IBRIDA - CHAT CON RISPOSTE DIRETTE ============
            storico_str = "\n".join(storico[-15:])
            msg_chat = [{
                "role": "user",
                "content": f"""Domanda originale: {domanda}

EVIDENZE DAL TESTO (marcate dall'utente):
{evidenze_context if evidenze_context else "(nessuna evidenza marcata)"}

STORICO CONVERSAZIONE:
{storico_str}

Ultimo messaggio dell'utente: "{user_input}"

=== ISTRUZIONI PER IL MODELLO ===

Tu sei un assistente ibrido che combina **approccio socratico** e **risposte dirette**.

**QUANDO RISPONDERE DIRETTAMENTE:**
- Domande fattuali ("quando e successo?", "quanti sono?", "chi ha detto?")
- Richieste di chiarimento tecnico ("come funziona?", "qual e la differenza tra X e Y?")
- Domande su definizioni ("cos'e esattamente...?")
- L'utente chiede esplicitamente una risposta

**QUANDO USARE APPROCCIO SOCRATICO:**
- Domande concettuali ("perche?", "ha senso?", "e giusto?")
- Domande aperte senza risposta univoca
- L'utente sta esplorando un tema nuovo
- Vuoi far emergere contraddizioni o tensioni

**REGOLA D'ORO:**
1. SE la domanda e fattuale risppondi con chiarezza, precisione, dati
2. SE la domanda e concettuale usa domande socratiche per guidare
3. PUOI mescolare: rispondere ai fatti E poi fare una domanda socratica

Rispondi in italiano, colloquiale ma rigoroso."""
            }]
            # ============ FINE MODIFICA ============
            
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
# COMANDO /fine (RIASSUNTO FINALE)
# ============================================================

def cmd_fine():
    stato = load_stato()
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file attivo{Colors.END}", flush=True)
        return
    
    file_path = Path(stato.get("file_path", stato["file_corrente"]))
    if not file_path.exists():
        file_path = SANDBOX / stato["file_corrente"]
        if not file_path.exists():
            file_path = RAW / stato["file_corrente"]
        if not file_path.exists():
            print(f"{Colors.RED}❌ File non trovato{Colors.END}", flush=True)
            return
    
    contenuto = read_file_safe(file_path)
    
    if "## ✅ IL MIO SAPERE" in contenuto and "NON ANCORA GENERATO" not in contenuto and "Lascia vuoto" not in contenuto.split("## ✅ IL MIO SAPERE")[-1][:50]:
        print(f"{Colors.YELLOW}⚠️ Il riassunto finale esiste già. Non lo rigenero.{Colors.END}", flush=True)
        return
    
    riassunti_discussioni = []
    # Estrai ogni blocco ### Discussione N: ... fino al prossimo o fine file
    sezioni = re.split(r'(?=### Discussione \d+:)', contenuto)
    for sezione in sezioni:
        if not sezione.strip().startswith('### Discussione'):
            continue
        # Domanda: prima riga dopo "### Discussione N: "
        dom_match = re.match(r'### Discussione \d+: (.+?)\n', sezione)
        if not dom_match:
            continue
        domanda_testo = dom_match.group(1).strip()
        # Riassunto: testo dopo "**Riassunto della conversazione:**" (tollerante a newline multipli)
        riass_match = re.search(r'\*\*Riassunto della conversazione:\*\*\s*\n+(.*?)(?=\n\*\*Risposta finale:|\n---)', sezione, re.DOTALL)
        riassunto_testo = riass_match.group(1).strip() if riass_match else ""
        # Risposta finale
        risp_match = re.search(r'\*\*Risposta finale:\*\*\s*(.+?)(?=\n---|$)', sezione, re.DOTALL)
        risposta_testo = risp_match.group(1).strip() if risp_match else ""
        if domanda_testo:
            riassunti_discussioni.append(f"**Domanda:** {domanda_testo}\n**Riassunto:** {riassunto_testo}\n**Risposta:** {risposta_testo}")

    if not riassunti_discussioni:
        print(f"{Colors.YELLOW}⚠️ Non trovate discussioni salvate. Esegui prima /chat e /salva.{Colors.END}", flush=True)
        return
    
    testo_riassunti = "\n\n---\n\n".join(riassunti_discussioni)
    
    prompt_unificato = f"""Genera un RIASSUNTO NARRATIVO UNIFICATO di TUTTE le seguenti discussioni.

DISCUSSIONI:
{testo_riassunti}

REGOLE:
1. Scrivi in prima persona ("Ho compreso che...", "È emerso che...")
2. Forma narrativa fluida (nessun punto elenco, nessuna lista)
3. Usa linguaggio tecnico preciso ma non divulgativo
4. Trova un FILO LOGICO che collega le diverse discussioni
5. Metti in luce le tensioni ricorrenti, le scoperte concettuali, i punti ancora aperti
6. Lunghezza proporzionale alla complessità (minimo 500 caratteri)

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
# COMANDO /promuovi (CREAZIONE WIKI)
# ============================================================

def cmd_promuovi(titolo: str):
    """Promuove il sandbox a wiki spostandolo direttamente nel wiki/."""
    titolo = titolo.strip().strip('"').strip("'")
    stato = load_stato()
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file sandbox attivo.{Colors.END}", flush=True)
        return

    sandbox_path = SANDBOX / stato["file_corrente"]
    if not sandbox_path.exists():
        print(f"{Colors.RED}❌ File sandbox non trovato: {sandbox_path}{Colors.END}", flush=True)
        return

    contenuto_sandbox = read_file_safe(sandbox_path)



    # Gestione versioni
    slug_base = titolo.lower().replace(" ", "_").replace("-", "_")
    wiki_path_base = WIKI / f"{slug_base}.md"

    if wiki_path_base.exists():
        versioni_esistenti = list(WIKI.glob(f"{slug_base}_v*.md"))
        if versioni_esistenti:
            numeri = [int(m.group(1)) for v in versioni_esistenti if (m := re.search(r'_v(\d+)', v.name))]
            prossimo = max(numeri) + 1 if numeri else 2
            titolo_finale = f"{titolo} v{prossimo}"
            wiki_path = WIKI / f"{slug_base}_v{prossimo}.md"
        else:
            data_str = datetime.now().strftime("%Y%m%d")
            titolo_finale = f"{titolo} ({date.today()})"
            wiki_path = WIKI / f"{slug_base}_{data_str}.md"
        print(f"{Colors.YELLOW}⚠️ Pagina già esistente. Creo versione: {titolo_finale}{Colors.END}", flush=True)
    else:
        wiki_path = wiki_path_base
        titolo_finale = titolo

    # Dati dal frontmatter del sandbox
    fonti_match = re.search(r'fonte: (.*?)(?:\n|$)', contenuto_sandbox)
    fonti_str = f"[[{fonti_match.group(1).strip()}]]" if fonti_match else ""
    discussioni = re.findall(r'### Discussione \d+:', contenuto_sandbox)
    cicli_spb = len(discussioni)

    # Chiedi dominio e tipo
    domini_validi = ["Bitcoin", "Cultura", "Economia", "Generale", "Geopolitica", "Storia", "Tecnologia"]
    tipi_validi = ["appunti", "articolo", "paper", "podcast", "post"]

    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}", flush=True)
    print(f"{Colors.BOLD}📝 PROMOZIONE A WIKI{Colors.END}", flush=True)
    print(f"{Colors.BLUE}{'='*60}{Colors.END}", flush=True)
    print(f"{Colors.GREEN}Titolo:{Colors.END} {titolo_finale}", flush=True)

    print(f"\n{Colors.YELLOW}📌 Scegli il DOMINIO:{Colors.END}", flush=True)
    for i, d in enumerate(domini_validi, 1):
        print(f"  {i}. {d}", flush=True)
    print(f"  {len(domini_validi)+1}. Inserisci manualmente", flush=True)
    scelta_dom = safe_input_semplice(f"{Colors.CYAN}👉 Numero (invio per Generale): {Colors.END}").strip()
    if scelta_dom == "":
        dominio_finale = "Generale"
    elif scelta_dom.isdigit() and 1 <= int(scelta_dom) <= len(domini_validi):
        dominio_finale = domini_validi[int(scelta_dom)-1]
    elif scelta_dom.isdigit() and int(scelta_dom) == len(domini_validi)+1:
        dominio_finale = safe_input_semplice(f"{Colors.CYAN}👉 Dominio: {Colors.END}").strip() or "Generale"
    else:
        dominio_finale = "Generale"

    print(f"\n{Colors.YELLOW}📌 Scegli il TIPO:{Colors.END}", flush=True)
    for i, t in enumerate(tipi_validi, 1):
        print(f"  {i}. {t}", flush=True)
    print(f"  {len(tipi_validi)+1}. Inserisci manualmente", flush=True)
    scelta_tipo = safe_input_semplice(f"{Colors.CYAN}👉 Numero (invio per articolo): {Colors.END}").strip()
    if scelta_tipo == "":
        tipo_finale = "articolo"
    elif scelta_tipo.isdigit() and 1 <= int(scelta_tipo) <= len(tipi_validi):
        tipo_finale = tipi_validi[int(scelta_tipo)-1]
    elif scelta_tipo.isdigit() and int(scelta_tipo) == len(tipi_validi)+1:
        tipo_finale = safe_input_semplice(f"{Colors.CYAN}👉 Tipo: {Colors.END}").strip() or "articolo"
    else:
        tipo_finale = "articolo"

    # --- Pulizia contenuto sandbox ---
    # Normalizza righe (rimuovi spazi trailing, collassa righe vuote multiple)
    def _clean(text):
        lines = [l.rstrip() for l in text.split('\n')]
        out, empty = [], 0
        for l in lines:
            if l == '':
                empty += 1
                if empty <= 1:
                    out.append(l)
            else:
                empty = 0
                out.append(l)
        return '\n'.join(out).strip()

    contenuto_sandbox = _clean(contenuto_sandbox)

    # Rimuovi il frontmatter YAML esistente (tollerante a spazi trailing su ---)
    contenuto_senza_fm = re.sub(r'^---\s*\n.*?\n---\s*\n', '', contenuto_sandbox, flags=re.DOTALL).lstrip('\n')

    # Rimuovi sezioni di lavoro sandbox che non appartengono al wiki
    sezioni_da_rimuovere = [
        r'## 📌 EVIDENZE DA DISCUTERE\n.*?(?=\n## |\Z)',
        r'## ❓ DOMANDE DA DISCUTERE\n.*?(?=\n## |\Z)',
        r'## 🗨️ DISCUSSIONE SOCRATICA\n.*?(?=\n### Discussione|\n## |\Z)',
        r'\(Lascia vuoto[^)]*\)',
        r'\*\*Riassunto della conversazione:\*\*\s*\n+.*?(?=\n\*\*Risposta finale:|\n---)',
        r'## ✅ IL MIO SAPERE\n.*?(?=\n##|\Z)',
        r'# SINTESI ESAUSTIVA\n',
    ]
    for pattern in sezioni_da_rimuovere:
        contenuto_senza_fm = re.sub(pattern, '', contenuto_senza_fm, flags=re.DOTALL)

    # Collassa nuovamente righe vuote dopo rimozioni
    contenuto_senza_fm = re.sub(r'\n{3,}', '\n\n', contenuto_senza_fm).strip()

    nuovo_frontmatter = f"""---
titolo: {titolo_finale}
dominio: {dominio_finale}
tipo: {tipo_finale}
stato: attivo
data_promozione: {date.today()}
cicli_spb: {cicli_spb}
fonti: {fonti_str}
---

"""
    wiki_content = nuovo_frontmatter + contenuto_senza_fm

    # Scrivi e sposta
    write_file_safe(wiki_path, wiki_content)
    arch_path = ARCHIVIATI / sandbox_path.name
    shutil.move(str(sandbox_path), str(arch_path))

    # Aggiorna indice e log
    with INDEX.open("a", encoding='utf-8') as f:
        f.write(f"| [[{titolo_finale}]] | {dominio_finale} | {tipo_finale} | {date.today()} |\n")
    with LOG.open("a", encoding='utf-8') as f:
        f.write(f"\n## [{date.today()}] promuovi | {titolo_finale}\n")
        f.write(f"- Cicli SPB: {cicli_spb}\n")
        f.write(f"- Pagina wiki: {wiki_path.name}\n")
        f.write(f"- Sandbox archiviato: {arch_path.name}\n")

    print(f"\n{Colors.GREEN}✅ Wiki creato: {wiki_path}{Colors.END}", flush=True)
    print(f"{Colors.GREEN}✅ Sandbox archiviato: {arch_path.name}{Colors.END}", flush=True)
    print(f"{Colors.GREEN}✅ Indice e log aggiornati.{Colors.END}", flush=True)
    print(flush=True)
    reset_stato()
    costruisci_indice()

# ============================================================
# ALTRI COMANDI
# ============================================================

def estrai_sezione(contenuto: str, pattern: str) -> str:
    match = re.search(pattern + r'\n+(.*?)(?=\n##|\n---|\Z)', contenuto, re.DOTALL)
    return match.group(1).strip() if match else ""

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
    if not filename.endswith(".md"):
        filename = filename + ".md"
    if not filename.startswith("sdbx_"):
        filename = f"sdbx_{filename}"
    src = ARCHIVIATI / filename
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in archiviati/{Colors.END}", flush=True)
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
    pagine_rilevanti = cerca_nel_wiki(domanda)
    risposta_wiki = None
    fonti_wiki = []
    
    if pagine_rilevanti:
        ctx = ""
        for score, titolo, percorso in pagine_rilevanti:
            contenuto = read_file_safe(Path(percorso))
            sintesi = estrai_sezione(contenuto, r'# 📌 SINTESI ESAUSTIVA')
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
    
    if risposta_wiki and len(risposta_wiki) > 150:
        for fonte in fonti_wiki:
            risposta_wiki = risposta_wiki.replace(f"[[{fonte}]]", f"[WIKI] [[{fonte}]]")
        print(f"\n{Colors.CYAN}[WIKI] {Colors.END}", flush=True)
        print_wrapped(risposta_wiki)
        return
    
    print(f"\n{Colors.DIM}⚠️ Ricerca online in corso...{Colors.END}\n", flush=True)
    risultati_web = web_search_brave(domanda, num_results=5)
    if risultati_web:
        print(f"{Colors.CYAN}[WEB] {Colors.END}", flush=True)
        for r in risultati_web[:5]:
            print(f"  🔗 {r['title']}", flush=True)
            print(f"     {r['snippet'][:200]}", flush=True)
            print(f"     {Colors.DIM}{r['url']}{Colors.END}", flush=True)
            print(flush=True)
    elif risposta_wiki:
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
        for f in [AGENT_MD, Path("analisi_wiki.py"), Path(".env")]:
            if f.exists():
                z.write(f)
    print(f"{Colors.GREEN}✅ Backup: {bkp}{Colors.END}", flush=True)

def cmd_stato():
    stato = load_stato()
    print(f"\n{Colors.BLUE}📊 STATO{Colors.END}", flush=True)
    print(f"  Provider: {Colors.CYAN}{PROVIDER_NOME}{Colors.END}", flush=True)
    print(f"  Modello: {Colors.CYAN}{CURRENT_MODEL}{Colors.END}", flush=True)
    print(f"  Fase: {stato.get('fase','nessuna')}", flush=True)
    print(f"  File: {stato.get('file_corrente','nessuno')}", flush=True)
    print(f"  Evidenze: {len(stato.get('evidenziazioni',[]))} trovate, indice {stato.get('indice',0)}", flush=True)
    print(f"  raw/: {len(list(RAW.glob('*')))} | wiki/: {len(list(WIKI.glob('*.md')))}", flush=True)
    print(f"  sandbox/: {len(list(SANDBOX.glob('sdbx_*.md')))}", flush=True)
    print(flush=True)

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def print_banner():
    modello_nome = CURRENT_MODEL if CURRENT_MODEL else "Non selezionato"
    provider_nome = PROVIDER_NOME if PROVIDER_NOME else "Non selezionato"
    print(f"""
{Colors.BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║     SISTEMA SOCRATES-PLATO-BAYES - Versione Ibrida          ║
║         (Risposte Dirette + Approccio Socratico)            ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}Provider:{Colors.END} {Colors.CYAN}{provider_nome}{Colors.END}
{Colors.YELLOW}Modello:{Colors.END} {Colors.CYAN}{modello_nome}{Colors.END}
{Colors.YELLOW}Soglia chunk:{Colors.END} {Colors.CYAN}{CHUNK_SIZE} parole{Colors.END}

{Colors.BLUE}{'='*60}{Colors.END}
{Colors.BOLD}📋 COMANDI:{Colors.END}
{Colors.BLUE}{'='*60}{Colors.END}

{Colors.GREEN}📥 INGEST{Colors.END}
  /analizza <file>      Analizza file in raw/ con marcatori >>...<< e ??...??

{Colors.YELLOW}💬 DISCUSSIONE (IBRIDA){Colors.END}
  /chat [file]          Avvia/riprendi discussione
  /salva "risposta"     Salva discussione
  /fine                 Genera riassunto unificato finale
  ℹ️  LLM risponde direttamente a domande fattuali,
     usa approccio socratico per domande concettuali

{Colors.CYAN}📚 WIKI{Colors.END}
  /promuovi "Titolo"    Crea pagina wiki (include sintesi, evidenze, il mio sapere)
  /query "domanda"      Interroga wiki + ricerca web

{Colors.BLUE}🔧 UTILITY{Colors.END}
  /list [cartella]      Mostra file
  /riprendi <file>      Ripristina sandbox archiviato
  /archivia             Archivia discussione
  /lint                 Health-check
  /backup               Backup
  /stato                Mostra stato
  /clear                Pulisce schermo
  /exit                 Esci

{Colors.BLUE}💡 Marcatori:{Colors.END}
  >>...<<  → copia il testo nella sezione EVIDENZE (finisce nel wiki come "Le mie evidenze")
  ??...??  → genera una domanda socratica

{Colors.BLUE}💡 In /chat:{Colors.END}
  /salva "risposta"  /salta  /pausa
""", flush=True)

# ============================================================
# AUTOCOMPLETAMENTO
# ============================================================

class SpbCompleter:
    def __init__(self):
        self.commands = ["/analizza", "/chat", "/salva", "/promuovi", "/riprendi", "/archivia", "/query", "/lint", "/backup", "/stato", "/list", "/clear", "/exit"]
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
                files = [f.name for f in SANDBOX.glob("sdbx_*.md") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        
        return None

# ============================================================
# MAIN
# ============================================================

def main():
    clear_screen()
    
    print("=" * 60, flush=True)
    print("🧠 SISTEMA SOCRATES-PLATO-BAYES (SPB) - VERSIONE IBRIDA", flush=True)
    print("   Supporta: DeepSeek Ufficiale | SiliconFlow", flush=True)
    print("   Chat: risposte dirette + approccio socratico", flush=True)
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

            if cmd == "/analizza":
                if arg:
                    cmd_analizza(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file: /analizza documento.md{Colors.END}", flush=True)
            elif cmd == "/list":
                cmd_list(arg if arg else None)
            elif cmd == "/chat":
                cmd_chat(arg if arg else None)
            elif cmd == "/salva":
                print(f"{Colors.YELLOW}⚠️ Usa /salva durante la chat{Colors.END}", flush=True)
            elif cmd == "/fine":
                cmd_fine()
            elif cmd == "/promuovi":
                if arg:
                    cmd_promuovi(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il titolo: /promuovi \"Titolo\"{Colors.END}", flush=True)
            elif cmd == "/riprendi":
                if arg:
                    cmd_riprendi(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file: /riprendi sdbx_nome.md{Colors.END}", flush=True)
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