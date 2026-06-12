#!/usr/bin/env python3
"""
wiki.py — Sistema Socrates–Plato–Bayes (SPB) - Scrittura immediata su /salva
"""

import os
import sys
import json
import shutil
import zipfile
import re
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

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print(f"{Colors.RED}❌ ERRORE: DEEPSEEK_API_KEY non trovata{Colors.END}")
    sys.exit(1)

CLIENT = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
MODEL = "deepseek-chat"

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
            return {"fase": None, "file_corrente": None, "evidenziazioni": [], "conversazioni": [], "indice": 0}
    return {"fase": None, "file_corrente": None, "evidenziazioni": [], "conversazioni": [], "indice": 0}

def save_stato(stato: dict):
    write_file_safe(STATE_FILE, json.dumps(stato, ensure_ascii=False, indent=2))

def reset_stato():
    save_stato({"fase": None, "file_corrente": None, "evidenziazioni": [], "conversazioni": [], "indice": 0})

def read_agent_md() -> str:
    return read_file_safe(AGENT_MD) if AGENT_MD.exists() else "(agent.md non trovato)"

def call_llm(system: str, messages: list) -> str:
    try:
        print(f"{Colors.DIM}🤖 Chiamata DeepSeek...{Colors.END}", flush=True)
        response = CLIENT.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system}, *messages],
            max_tokens=4000, temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"{Colors.RED}Errore API: {e}{Colors.END}"

def build_system() -> str:
    return f"""Sei l'agente del sistema Socrates–Plato–Bayes (SPB) in lingua italiana.
Regole: Fase INGEST: riassunto ESAUSTIVO. Fase CHAT: conversazione socratica.
Mantieni un tono colloquiale ma rigoroso.
{read_agent_md()}"""

def estrai_evidenziazioni(contenuto: str) -> list:
    return re.findall(r'>([^<]+)<', contenuto)

# --------------------------------------------------------------
# COMANDI
# --------------------------------------------------------------

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
    print()  # riga vuota per separare
    sys.stdout.flush()

def cmd_ingest(filepath: str):
    src = RAW / filepath
    if not src.exists():
        print(f"{Colors.RED}❌ File non trovato in raw/{Colors.END}")
        sys.stdout.flush()
        return
    print(f"{Colors.GREEN}📥 Ingest: {src.name}{Colors.END}")
    testo = read_file_safe(src)
    out_name = f"{src.stem}_V1.md"
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
    
    # Se è stato passato un argomento, imposta quel file come corrente
    if filearg and filearg.strip():
        # Verifica che il file esista in sandbox/
        target_file = filearg.strip()
        # Se non ha estensione .md, aggiungila (per comodità)
        if not target_file.endswith(".md"):
            target_file = target_file + ".md"
        sandbox_path = SANDBOX / target_file
        if not sandbox_path.exists():
            print(f"{Colors.RED}❌ File non trovato in sandbox/: {target_file}{Colors.END}")
            print(f"   File disponibili in sandbox/:")
            for f in SANDBOX.glob("*_V1.md"):
                print(f"     - {f.name}")
            sys.stdout.flush()
            return
        # Imposta il nuovo file corrente
        stato["file_corrente"] = target_file
        stato["fase"] = "INGEST_COMPLETATO"  # resetta lo stato della discussione precedente
        stato["evidenziazioni"] = []
        stato["conversazioni"] = []
        stato["indice"] = 0
        save_stato(stato)
        print(f"{Colors.GREEN}✅ File attivo cambiato in: {target_file}{Colors.END}")
        print()
        sys.stdout.flush()
    
    # Ora procedi con la chat sul file corrente
    if not stato.get("file_corrente"):
        print(f"{Colors.RED}❌ Nessun file attivo. Usa /ingest prima o /chat nomefile.md{Colors.END}")
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
    print(f"\n{Colors.GREEN}📝 DOMANDA:{Colors.END}\n{Colors.CYAN}{domanda}{Colors.END}")
    print(f"\n{Colors.DIM}Dialogo libero. Quando hai la risposta definitiva, usa:{Colors.END}")
    print(f"   {Colors.GREEN}/salva \"la tua risposta\"{Colors.END}")
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
        if user_input.startswith("/salva"):
            match = re.search(r'/salva\s+"([^"]+)"', user_input)
            if not match:
                print(f"{Colors.RED}❌ Formato: /salva \"risposta\"{Colors.END}")
                sys.stdout.flush()
                continue
            risposta_finale = match.group(1)
            # Genera riassunto della conversazione
            storico = stato.get("storico_chat", [])
            testo_conv = "\n".join(storico)
            if testo_conv.strip():
                prompt_riassunto = f"""Riassumi in 3-5 frasi questa conversazione socratica.
Evidenziazione: {ev}
Domanda: {domanda}
Conversazione:
{testo_conv}
Riassunto:"""
                riassunto_conv = call_llm(build_system(), [{"role":"user","content":prompt_riassunto}])
            else:
                riassunto_conv = "(nessuna conversazione)"
            # Scrivi SUBITO nel file
            file_path = SANDBOX / stato["file_corrente"]
            contenuto_attuale = read_file_safe(file_path)
            nuovo_blocco = f"\n\n### Evidenziazione {stato['indice']+1}: {ev}\n"
            nuovo_blocco += f"**Domanda:** {domanda}\n\n"
            nuovo_blocco += f"**Conversazione:**\n```\n{testo_conv}\n```\n\n"
            nuovo_blocco += f"**Riassunto della conversazione:** {riassunto_conv}\n\n"
            nuovo_blocco += f"**Risposta finale:** {risposta_finale}\n\n---\n"
            if "## 🗨️ DISCUSSIONE SOCRATICA" in contenuto_attuale:
                if "## ✅ IL MIO SAPERE" in contenuto_attuale:
                    contenuto_attuale = contenuto_attuale.replace("## ✅ IL MIO SAPERE", nuovo_blocco + "\n## ✅ IL MIO SAPERE")
                else:
                    contenuto_attuale += nuovo_blocco
            else:
                contenuto_attuale += "\n## 🗨️ DISCUSSIONE SOCRATICA\n" + nuovo_blocco
            write_file_safe(file_path, contenuto_attuale)
            print(f"{Colors.GREEN}✅ Salvato nel file: domanda, conversazione, riassunto, risposta.{Colors.END}")
            print()
            sys.stdout.flush()
            stato["indice"] += 1
            stato["conversazioni"].append({})
            save_stato(stato)
            if stato["indice"] < len(stato["evidenziazioni"]):
                avvia_evidenziazione()
            else:
                print(f"\n{Colors.GREEN}🎉 Tutte le evidenziazioni discusse e salvate!{Colors.END}")
                print(f"   Usa /fine per il riassunto finale (opzionale).")
                print()
                sys.stdout.flush()
            return
        elif user_input.lower() == "/abbandono":
            cmd_abbandono()
            return
        else:
            storico = stato.get("storico_chat", [])
            storico.append(f"Utente: {user_input}")
            msg_chat = [{"role":"user","content":f"""Evidenziazione: {ev}
Domanda iniziale: {domanda}
Storico:
{chr(10).join(storico[-15:])}
Ora l'utente dice: "{user_input}"
Rispondi in modo socratico, colloquiale."""}]
            risp_llm = call_llm(build_system(), msg_chat)
            storico.append(f"LLM: {risp_llm}")
            stato["storico_chat"] = storico
            save_stato(stato)
            print(f"\n{Colors.CYAN}🤖 {risp_llm}{Colors.END}")
            print()
            sys.stdout.flush()

def cmd_fine():
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
    evidenze_risposte = []
    blocchi = re.findall(r'### Evidenziazione \d+: (.+?)\n\*\*Domanda:\*\* (.+?)\n\*\*Risposta finale:\*\* (.+?)(?:\n---|$)', contenuto, re.DOTALL)
    for ev, dom, risp in blocchi:
        evidenze_risposte.append(f"- {ev}: {risp.strip()[:200]}")
    if not evidenze_risposte:
        print(f"{Colors.YELLOW}⚠️ Non trovate evidenziazioni salvate. Esegui prima /chat e /salva.{Colors.END}")
        sys.stdout.flush()
        return
    testo_risposte = "\n".join(evidenze_risposte)
    msg = [{"role":"user","content":f"""Genera un RIASSUNTO FINALE del sapere emerso da questa discussione.
Elenco evidenziazioni e risposte finali:
{testo_risposte}
Scrivi in prima persona ("Ho compreso che...", "Emergono questi punti chiave...")."""}]
    riassunto_globale = call_llm(build_system(), msg)
    if "## ✅ IL MIO SAPERE" in contenuto:
        contenuto = re.sub(r'## ✅ IL MIO SAPERE\n.*?(?=\n##|$)', f"## ✅ IL MIO SAPERE\n\n{riassunto_globale}\n", contenuto, flags=re.DOTALL)
    else:
        contenuto += f"\n## ✅ IL MIO SAPERE\n\n{riassunto_globale}\n"
    write_file_safe(file_path, contenuto)
    print(f"{Colors.GREEN}✅ Riassunto finale aggiunto al file.{Colors.END}")
    print()
    sys.stdout.flush()
    stato["fase"] = "COMPLETATA"
    save_stato(stato)

def cmd_promuovi(titolo: str):
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

    match_riassunto = re.search(r'## ✅ IL MIO SAPERE\n\n(.*?)(?=\n##|\n---|\Z)', contenuto_sandbox, re.DOTALL)
    riassunto_finale = match_riassunto.group(1).strip() if match_riassunto else "(nessun riassunto finale trovato. Esegui /fine prima di /promuovi)"

    evidenze_risposte = []
    blocchi = re.findall(r'### Evidenziazione \d+: (.+?)\n\*\*Domanda:\*\* (.+?)\n\*\*Risposta finale:\*\* (.+?)(?:\n---|$)', contenuto_sandbox, re.DOTALL)
    for ev, dom, risp in blocchi:
        evidenze_risposte.append((ev, dom, risp))
    if not evidenze_risposte:
        print(f"{Colors.YELLOW}⚠️ Nessuna discussione salvata nel file. Esegui /chat e /salva prima di promuovere.{Colors.END}")
        sys.stdout.flush()
        return

    print(f"{Colors.CYAN}🤖 Analizzo il contenuto per proporre dominio e tipo...{Colors.END}")
    domini_validi = ["Bitcoin", "Cultura", "Economia", "Generale", "Geopolitica", "Storia", "Tecnologia"]
    tipi_validi = ["appunti", "articolo", "paper", "podcast", "post"]
    prompt_frontmatter = f"""Leggi il seguente riassunto finale e le evidenziazioni discusse, poi proponi un dominio e un tipo per una pagina wiki.

DOMINI DISPONIBILI: {', '.join(domini_validi)}
TIPI DISPONIBILI: {', '.join(tipi_validi)}

RIASSUNTO FINALE:
{riassunto_finale[:1500]}

EVIDENZIAZIONI E RISPOSTE:
{chr(10).join([f"- {ev}: {risp[:200]}" for ev,_,risp in evidenze_risposte])}

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
Riassunto finale: {riassunto_finale[:1000]}

Quali di queste pagine sono semanticamente correlate alla nuova pagina? Per ognuna, spiega brevemente perché (massimo 10 parole).
Restituisci solo un elenco in formato JSON: [{{"pagina": "nome", "ragione": "spiegazione breve"}}, ...]
Solo quelle realmente rilevanti, massimo 5.
"""
        msg_link = [{"role": "user", "content": prompt_link}]
        link_response = call_llm(build_system(), msg_link)
        try:
            collegamenti_trovati = json.loads(link_response)
            if not isinstance(collegamenti_trovati, list):
                collegamenti_trovati = []
        except:
            collegamenti_trovati = []

    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📝 CREAZIONE NUOVA PAGINA WIKI{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    print(f"{Colors.GREEN}Titolo:{Colors.END} {titolo}")

    print(f"\n{Colors.YELLOW}📌 Scegli il DOMINIO (modifica se necessario):{Colors.END}")
    for i, d in enumerate(domini_validi, 1):
        default = " (proposto)" if d == dominio_proposto else ""
        print(f"  {i}. {d}{default}")
    print(f"  {len(domini_validi)+1}. Inserisci manualmente")
    scelta_dom = input(f"{Colors.CYAN}👉 Inserisci numero (invio per accettare {dominio_proposto}): {Colors.END}").strip()
    if scelta_dom == "":
        dominio_finale = dominio_proposto
    elif scelta_dom.isdigit() and 1 <= int(scelta_dom) <= len(domini_validi):
        dominio_finale = domini_validi[int(scelta_dom)-1]
    elif scelta_dom == str(len(domini_validi)+1):
        dominio_finale = input(f"{Colors.CYAN}Inserisci dominio personalizzato: {Colors.END}").strip()
        if not dominio_finale:
            dominio_finale = dominio_proposto
    else:
        print(f"{Colors.RED}Scelta non valida, uso {dominio_proposto}{Colors.END}")
        dominio_finale = dominio_proposto

    print(f"\n{Colors.YELLOW}📌 Scegli il TIPO:{Colors.END}")
    for i, t in enumerate(tipi_validi, 1):
        default = " (proposto)" if t == tipo_proposto else ""
        print(f"  {i}. {t}{default}")
    print(f"  {len(tipi_validi)+1}. Inserisci manualmente")
    scelta_tipo = input(f"{Colors.CYAN}👉 Inserisci numero (invio per accettare {tipo_proposto}): {Colors.END}").strip()
    if scelta_tipo == "":
        tipo_finale = tipo_proposto
    elif scelta_tipo.isdigit() and 1 <= int(scelta_tipo) <= len(tipi_validi):
        tipo_finale = tipi_validi[int(scelta_tipo)-1]
    elif scelta_tipo == str(len(tipi_validi)+1):
        tipo_finale = input(f"{Colors.CYAN}Inserisci tipo personalizzato: {Colors.END}").strip()
        if not tipo_finale:
            tipo_finale = tipo_proposto
    else:
        print(f"{Colors.RED}Scelta non valida, uso {tipo_proposto}{Colors.END}")
        tipo_finale = tipo_proposto

    fonti_match = re.search(r'fonte: (.*?)(?:\n|$)', contenuto_sandbox)
    fonti = [f.strip() for f in fonti_match.group(1).split(',')] if fonti_match else []
    fonti_str = ", ".join([f"[[{f}]]" for f in fonti])
    cicli_spb = len(evidenze_risposte)

    print(f"\n{Colors.BLUE}{'─'*40}{Colors.END}")
    print(f"{Colors.BOLD}📄 Frontmatter proposto:{Colors.END}")
    print(f"  titolo: {titolo}")
    print(f"  dominio: {dominio_finale}")
    print(f"  tipo: {tipo_finale}")
    print(f"  stato: attivo")
    print(f"  data_promozione: {date.today()}")
    print(f"  cicli_spb: {cicli_spb}")
    print(f"  fonti: {fonti_str}")
    print(f"{Colors.BLUE}{'─'*40}{Colors.END}")

    conferma_front = input(f"{Colors.YELLOW}✅ Confermi il frontmatter? (s/n/modifica): {Colors.END}").lower()
    if conferma_front == 'n':
        print(f"{Colors.RED}❌ Promozione annullata.{Colors.END}")
        sys.stdout.flush()
        return
    elif conferma_front == 'modifica':
        nuovo_titolo = input(f"Titolo ({titolo}): ").strip()
        if nuovo_titolo: titolo = nuovo_titolo
        nuovo_dominio = input(f"Dominio ({dominio_finale}): ").strip()
        if nuovo_dominio: dominio_finale = nuovo_dominio
        nuovo_tipo = input(f"Tipo ({tipo_finale}): ").strip()
        if nuovo_tipo: tipo_finale = nuovo_tipo

    collegamenti_scelti = []
    if collegamenti_trovati:
        print(f"\n{Colors.CYAN}🔗 Pagine wiki correlate trovate automaticamente:{Colors.END}")
        for i, link in enumerate(collegamenti_trovati, 1):
            print(f"  {i}. [[{link['pagina']}]] — {link.get('ragione', 'correlata')}")
        print(f"  {len(collegamenti_trovati)+1}. Nessuno")
        scelta_link = input(f"{Colors.YELLOW}👉 Inserisci i numeri dei collegamenti da mantenere (es. 1,3,5) o invio per nessuno: {Colors.END}").strip()
        if scelta_link:
            indici = re.findall(r'\d+', scelta_link)
            for idx in indici:
                num = int(idx)
                if 1 <= num <= len(collegamenti_trovati):
                    collegamenti_scelti.append(collegamenti_trovati[num-1]['pagina'])
    else:
        print(f"{Colors.YELLOW}⚠️ Nessuna pagina wiki correlata trovata automaticamente.{Colors.END}")
        aggiungi_manuale = input(f"{Colors.CYAN}Vuoi aggiungere collegamenti manualmente? (s/n): {Colors.END}").lower()
        if aggiungi_manuale == 's':
            while True:
                manuale = input(f"Nome pagina wiki (vuoto per finire): ").strip()
                if not manuale:
                    break
                collegamenti_scelti.append(manuale)

    argomenti_principali = "\n".join([f"- {ev}" for ev,_,_ in evidenze_risposte])
    discussione = ""
    for ev, dom, risp in evidenze_risposte:
        discussione += f"### {ev}\n\n**Domanda:** {dom}\n\n**Risposta:** {risp}\n\n---\n\n"
    wikilink_list = "\n".join([f"- [[{link}]]" for link in collegamenti_scelti])

    wiki_content = f"""---
titolo: {titolo}
dominio: {dominio_finale}
tipo: {tipo_finale}
stato: attivo
data_promozione: {date.today()}
cicli_spb: {cicli_spb}
fonti: {fonti_str}
---

## Argomenti principali

{argomenti_principali}

## Discussione socratica

{discussione}

## Conclusioni

{riassunto_finale}

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
    print()
    sys.stdout.flush()
    reset_stato()

def cmd_abbandono():
    stato = load_stato()
    if stato.get("file_corrente"):
        src = SANDBOX / stato["file_corrente"]
        if src.exists():
            arch = ARCHIVIATI / f"abbandonato_{src.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            shutil.move(str(src), str(arch))
            print(f"{Colors.YELLOW}🗂️ Archiviato: {arch}{Colors.END}")
    reset_stato()
    print(f"{Colors.GREEN}✅ Discussione archiviata{Colors.END}")
    print()
    sys.stdout.flush()

def cmd_query(domanda: str):
    wiki_pages = {f.stem: read_file_safe(f)[:2000] for f in WIKI.glob("*.md") if f.name not in ["index.md","log.md"]}
    if not wiki_pages:
        print(f"{Colors.YELLOW}⚠️ Wiki vuoto{Colors.END}")
        sys.stdout.flush()
        return
    ctx = "\n".join([f"### {nome}\n{testo[:1500]}" for nome, testo in wiki_pages.items()])
    msg = [{"role":"user","content":f"Domanda: {domanda}\n\nPagine wiki:\n{ctx}\nRispondi in italiano usando [[wikilink]]."}]
    risp = call_llm(build_system(), msg)
    print(f"\n{Colors.CYAN}{risp}{Colors.END}")
    print()
    sys.stdout.flush()

def cmd_lint():
    print(f"\n{Colors.CYAN}🔬 LINT DEL WIKI{Colors.END}")
    wiki_pages = [f.stem for f in WIKI.glob("*.md") if f.name not in ["index.md","log.md"]]
    backlinks = {}
    for f in WIKI.glob("*.md"):
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
    for f in SANDBOX.glob("*.md"):
        if f.name != ".stato_spb.json":
            age = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
            if age>30:
                old.append((f.name,age))
    if old:
        print(f"{Colors.YELLOW}🟡 File sandbox >30gg: {len(old)}{Colors.END}")
    else:
        print(f"{Colors.GREEN}✅ Nessun file vecchio{Colors.END}")
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
    print(f"  Fase: {stato.get('fase','nessuna')}")
    print(f"  File: {stato.get('file_corrente','nessuno')}")
    print(f"  Evidenziazioni: {len(stato.get('evidenziazioni',[]))} trovate, indice {stato.get('indice',0)}")
    print(f"  raw/: {len(list(RAW.glob('*')))} | wiki/: {len(list(WIKI.glob('*.md')))} | sandbox/: {len(list(SANDBOX.glob('*.md')))}")
    print()
    sys.stdout.flush()

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def print_banner():
    print(f"""
{Colors.BLUE}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║     SISTEMA SOCRATES-PLATO-BAYES - Scrittura immediata      ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}Comandi:{Colors.END}

  {Colors.GREEN}/move{Colors.END}      <file>
  {Colors.GREEN}/list{Colors.END}     [cartella]
  {Colors.GREEN}/ingest{Colors.END}   <file>
  {Colors.GREEN}/chat{Colors.END}     [file]
  {Colors.GREEN}/salva{Colors.END}    "risposta"
  {Colors.GREEN}/fine{Colors.END}
  {Colors.GREEN}/abbandono{Colors.END}
  {Colors.GREEN}/promuovi{Colors.END} "Titolo"
  {Colors.GREEN}/query{Colors.END}    "domanda"
  {Colors.GREEN}/lint{Colors.END}
  {Colors.GREEN}/backup{Colors.END}
  {Colors.GREEN}/stato{Colors.END}
  {Colors.GREEN}/clear{Colors.END}
  {Colors.GREEN}/exit{Colors.END}

{Colors.BLUE}💡 >argomento< nel file, poi /chat. Ogni /salva scrive subito domanda+conversazione+riassunto+risposta.{Colors.END}
{Colors.BLUE}💡 /promuovi crea una pagina wiki nel vault/wiki/ con conferma frontmatter e collegamenti.{Colors.END}
{Colors.BLUE}💡 /chat nomefile.md imposta quel file come attivo e avvia la chat.{Colors.END}
""")
    sys.stdout.flush()


# --------------------------------------------------------------
# AUTOCOMPLETAMENTO AVANZATO
# --------------------------------------------------------------

class SpbCompleter:
    def __init__(self):
        self.commands = ["/move", "/list", "/ingest", "/chat", "/salva", "/fine", "/promuovi", "/abbandono", "/query", "/lint", "/backup", "/stato", "/clear", "/exit"]
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
        # Autocompletamento comando stesso
        if len(parts) == 1 and not line.endswith(' '):
            matches = [c for c in self.commands if c.startswith(text)]
            return matches[state] if state < len(matches) else None
        # Autocompletamento per /list
        if cmd == "/list" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            matches = [t for t in self.list_targets if t.startswith(prefix)]
            return matches[state] if state < len(matches) else None
        # Autocompletamento per /move
        if cmd == "/move" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in CLIPPINGS.glob("*") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        # Autocompletamento per /ingest
        if cmd == "/ingest" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in RAW.glob("*") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        # Autocompletamento per /chat: suggerisce file _V1.md in sandbox/
        if cmd == "/chat" and len(parts) <= 2:
            prefix = parts[1] if len(parts) > 1 else ""
            try:
                files = [f.name for f in SANDBOX.glob("*_V1.md") if f.is_file()]
                matches = [f for f in files if f.startswith(prefix)]
                return matches[state] if state < len(matches) else None
            except:
                return None
        return None

# --------------------------------------------------------------
# MAIN
# --------------------------------------------------------------

def main():
    init_vault()
    clear_screen()
    print_banner()

    if readline is not None:
        completer = SpbCompleter()
        readline.set_completer(completer.get_matches)
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims(' \t\n;')
    else:
        print(f"{Colors.YELLOW}⚠️ readline non disponibile, autocompletamento disabilitato{Colors.END}")

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
                    print(f"{Colors.RED}❌ Specifica il file (usa TAB per autocompletare){Colors.END}")
                    sys.stdout.flush()
            elif cmd == "/list":
                cmd_list(arg if arg else None)
            elif cmd == "/ingest":
                if arg:
                    cmd_ingest(arg)
                else:
                    print(f"{Colors.RED}❌ Specifica il file (usa TAB per autocompletare){Colors.END}")
                    sys.stdout.flush()
            elif cmd == "/chat":
                # Ora accetta un argomento opzionale (il file sandbox)
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
            elif cmd == "/abbandono":
                cmd_abbandono()
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