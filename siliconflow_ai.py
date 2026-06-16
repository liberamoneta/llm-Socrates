#!/usr/bin/env python3
"""
SiliconFlow AI - Creazione Contenuti Multimediali
Supporta: Chat, Immagini, Analisi, Traduzioni, Presentazioni, Articoli
Lista modelli dinamica da SiliconFlow API
"""

import os
import sys
import json
import time
import base64
import io
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

# Carica .env
load_dotenv()

# ============================================================
# CONFIGURAZIONE
# ============================================================

API_KEY = os.getenv("SILICONFLOW_API_KEY")
BASE_URL = "https://api.siliconflow.com/v1"

if not API_KEY:
    print("❌ SILICONFLOW_API_KEY non trovata nel .env")
    print("   Aggiungi: SILICONFLOW_API_KEY=sk-...")
    sys.exit(1)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ============================================================
# DESCRIZIONI MODELLI
# ============================================================

MODEL_DESCRIPTIONS = {
    # DeepSeek
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
    
    # Immagini
    "FLUX.1-dev": "🎨 Immagini realistiche, arte di alta qualità",
    "FLUX.1-schnell": "⚡ Immagini veloci ed economiche",
    "stabilityai/stable-diffusion-3.5-large": "🎨 Immagini artistiche, stili creativi",
}

# ============================================================
# FUNZIONI DI UTILITÀ
# ============================================================

def print_colored(text, color="white"):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    print_colored("=" * 70, "cyan")
    print_colored(f"  {text}", "bold")
    print_colored("=" * 70, "cyan")

def print_subheader(text):
    print_colored(f"\n📌 {text}", "yellow")
    print_colored("-" * 70, "yellow")

def salva_file(contenuto, nome_base, estensione="md"):
    """Salva il contenuto in un file con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{nome_base}_{timestamp}.{estensione}"
    
    output_dir = Path("siliconflow_output")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(contenuto)
    
    print_colored(f"\n💾 Salvato in: {filepath}", "green")
    return filepath

def ottieni_modelli_da_siliconflow() -> List[Tuple[str, str, str]]:
    """
    Ottiene la lista dei modelli disponibili da SiliconFlow in tempo reale.
    Restituisce una lista di tuple (model_id, model_name, description)
    """
    try:
        url = "https://api.siliconflow.com/v1/models"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        modelli = []
        
        for model in data.get("data", []):
            model_id = model.get("id", "")
            
            # Filtra modelli non utili
            if "embed" in model_id.lower() or "rerank" in model_id.lower():
                continue
            
            # Crea un nome leggibile
            nome = model_id.replace("ai/", "").replace("-Instruct", "")
            
            # Ottieni descrizione dal dizionario
            descrizione = MODEL_DESCRIPTIONS.get(model_id, "💬 Modello generico")
            
            modelli.append((model_id, nome, descrizione))
        
        # Ordina per nome
        modelli.sort(key=lambda x: x[1])
        
        return modelli
        
    except Exception as e:
        print(f"   ⚠️ Errore nel recupero modelli: {e}")
        return []

def scegli_modello_da_lista(modelli: List[Tuple[str, str, str]], titolo: str = "Scegli il modello") -> Optional[Tuple[str, str, str]]:
    """Menu per scegliere un modello da una lista"""
    
    print(f"\n📌 {titolo}")
    print("-" * 60)
    
    # Mostra solo i primi 20 modelli per non sovraccaricare
    modelli_mostrati = modelli[:20]
    for i, (model_id, nome, desc) in enumerate(modelli_mostrati, 1):
        print(f"   {i:2}. {nome:<35} {desc}")
    
    if len(modelli) > 20:
        print(f"   ... e altri {len(modelli)-20} modelli")
    
    print(f"   {len(modelli_mostrati)+1}. Indietro")
    print("-" * 60)
    
    while True:
        try:
            choice = input("\n👉 Scegli modello (numero): ").strip()
            if choice == str(len(modelli_mostrati)+1):
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(modelli_mostrati):
                return modelli_mostrati[idx]
            else:
                print(f"   ❌ Scelta non valida (1-{len(modelli_mostrati)})")
        except ValueError:
            print("   ❌ Inserisci un numero valido")
        except KeyboardInterrupt:
            return None

# ============================================================
# FUNZIONI DEI COMANDI
# ============================================================

def cmd_lista_modelli():
    """Mostra tutti i modelli disponibili da SiliconFlow"""
    print_header("📋 MODELLI DISPONIBILI SU SILICONFLOW")
    
    print("\n🔄 Recupero modelli da SiliconFlow...")
    modelli = ottieni_modelli_da_siliconflow()
    
    if modelli:
        print(f"   ✅ Trovati {len(modelli)} modelli\n")
        print("-" * 70)
        
        # Raggruppa per categoria
        chat_models = []
        vision_models = []
        image_models = []
        altri_models = []
        
        for model_id, nome, desc in modelli:
            if "vl" in model_id.lower() or "vision" in model_id.lower() or "internvl" in model_id.lower():
                vision_models.append((model_id, nome, desc))
            elif "flux" in model_id.lower() or "diffusion" in model_id.lower() or "sd-" in model_id.lower():
                image_models.append((model_id, nome, desc))
            elif "qwen" in model_id.lower() or "deepseek" in model_id.lower() or "llama" in model_id.lower():
                chat_models.append((model_id, nome, desc))
            else:
                altri_models.append((model_id, nome, desc))
        
        # Mostra per categoria
        if chat_models:
            print_colored("\n💬 MODELLI CHAT:", "green")
            for i, (model_id, nome, desc) in enumerate(chat_models, 1):
                print(f"   {i:2}. {nome:<35} {desc}")
        
        if vision_models:
            print_colored("\n👁️ MODELLI VISIONE / OCR:", "green")
            for i, (model_id, nome, desc) in enumerate(vision_models, 1):
                print(f"   {i:2}. {nome:<35} {desc}")
        
        if image_models:
            print_colored("\n🎨 MODELLI IMMAGINI:", "green")
            for i, (model_id, nome, desc) in enumerate(image_models, 1):
                print(f"   {i:2}. {nome:<35} {desc}")
        
        if altri_models:
            print_colored("\n📦 ALTRI MODELLI:", "green")
            for i, (model_id, nome, desc) in enumerate(altri_models, 1):
                print(f"   {i:2}. {nome:<35} {desc}")
        
        print("\n" + "-" * 70)
        print_colored(f"📊 Totale: {len(modelli)} modelli", "yellow")
    else:
        print("   ⚠️ Nessun modello trovato")

def cmd_chat():
    """Chat interattiva con modelli di linguaggio"""
    print_header("💬 CHAT CON SILICONFLOW")
    
    # Ottieni modelli
    print("\n🔄 Recupero modelli...")
    modelli = ottieni_modelli_da_siliconflow()
    
    if not modelli:
        print("   ⚠️ Nessun modello trovato")
        return
    
    # Filtra solo modelli chat (escludi visione e immagini)
    chat_modelli = []
    for model_id, nome, desc in modelli:
        if "vl" not in model_id.lower() and "vision" not in model_id.lower() and "internvl" not in model_id.lower():
            if "flux" not in model_id.lower() and "diffusion" not in model_id.lower():
                chat_modelli.append((model_id, nome, desc))
    
    if not chat_modelli:
        print("   ⚠️ Nessun modello chat trovato")
        return
    
    modello = scegli_modello_da_lista(chat_modelli, "Scegli il modello per la chat")
    if modello is None:
        return
    
    model_id, model_name, desc = modello
    print_colored(f"\n✅ Modello: {model_name}", "green")
    print(f"   {desc}")
    
    print("\n💬 Chat interattiva (scrivi 'exit' per uscire)")
    storico = []
    
    while True:
        user_input = input(f"\ntu> ").strip()
        
        if user_input.lower() in ["exit", "quit", "esci"]:
            break
        
        if not user_input:
            continue
        
        storico.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=storico,
                max_tokens=2048,
                temperature=0.7
            )
            
            risposta = response.choices[0].message.content
            storico.append({"role": "assistant", "content": risposta})
            print_colored(f"\n🤖 {risposta}", "cyan")
            
        except Exception as e:
            print_colored(f"❌ Errore: {e}", "red")

def cmd_genera_immagine():
    """Genera immagini con modelli FLUX o Stable Diffusion"""
    print_header("🎨 GENERAZIONE IMMAGINI")
    
    # Ottieni modelli
    print("\n🔄 Recupero modelli...")
    modelli = ottieni_modelli_da_siliconflow()
    
    if not modelli:
        print("   ⚠️ Nessun modello trovato")
        return
    
    # Filtra solo modelli immagini
    image_modelli = []
    for model_id, nome, desc in modelli:
        if "flux" in model_id.lower() or "diffusion" in model_id.lower() or "sd-" in model_id.lower():
            image_modelli.append((model_id, nome, desc))
    
    if not image_modelli:
        print("   ⚠️ Nessun modello immagini trovato")
        return
    
    # Mostra modelli immagini con costi
    print("\n📌 Modelli disponibili per generazione immagini:")
    print("-" * 60)
    for i, (model_id, nome, desc) in enumerate(image_modelli, 1):
        if "flux.1-dev" in model_id:
            costo = "$0.02/immagine"
        elif "flux.1-schnell" in model_id:
            costo = "$0.01/immagine"
        elif "sd-3.5" in model_id:
            costo = "$0.03/immagine"
        else:
            costo = "$0.02/immagine"
        print(f"   {i}. {nome:<35} {costo} - {desc}")
    print("-" * 60)
    
    try:
        choice = input("\n👉 Scegli modello (numero, 0 per annullare): ").strip()
        if choice == "0":
            return
        
        idx = int(choice) - 1
        if idx < 0 or idx >= len(image_modelli):
            print("❌ Scelta non valida")
            return
        
        model_id, model_name, desc = image_modelli[idx]
        print_colored(f"\n✅ Modello: {model_name}", "green")
        
    except ValueError:
        print("❌ Scelta non valida")
        return
    
    prompt = input("\n📝 Descrizione dell'immagine: ").strip()
    if not prompt:
        print("❌ Descrizione non valida")
        return
    
    size = input("\n📐 Dimensione (default 1024x1024): ").strip()
    if not size:
        size = "1024x1024"
    
    print(f"\n🎨 Generando immagine con {model_name}...")
    print(f"   Prompt: {prompt}")
    print(f"   Dimensione: {size}")
    
    try:
        # Prova a usare images.generate se disponibile
        try:
            response = client.images.generate(
                model=model_id,
                prompt=prompt,
                size=size,
                n=1
            )
            image_url = response.data[0].url
            print_colored(f"\n✅ Immagine generata!", "green")
            print(f"   URL: {image_url}")
            
            contenuto = f"""# Immagine Generata

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Modello:** {model_name} ({model_id})
**Prompt:** {prompt}
**Dimensione:** {size}
**URL:** {image_url}
"""
            salva_file(contenuto, "immagine_generata", "md")
            
        except Exception as e:
            # Fallback: usa chat completions per modelli che non supportano images.generate
            print("   ℹ️ Uso metodo alternativo...")
            
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate an image: {prompt}. Size: {size}"
                    }
                ],
                max_tokens=100
            )
            
            if response.choices and response.choices[0].message:
                print_colored(f"\n✅ Immagine generata!", "green")
                print(f"   {response.choices[0].message.content[:200]}...")
                
                salva_file(
                    f"# Prompt Immagine\n\n{prompt}\n\nDimensione: {size}\n\nModello: {model_name}\n\nData: {datetime.now()}\n\nRisposta:\n{response.choices[0].message.content}",
                    "immagine_prompt",
                    "md"
                )
        
    except Exception as e:
        print_colored(f"❌ Errore: {e}", "red")
        print_colored("   💡 Prova con: FLUX.1-schnell (più economico e veloce)", "yellow")

def cmd_scrivi_articolo():
    """Scrive un articolo completo su un tema"""
    print_header("📝 SCRITTURA ARTICOLO")
    
    # Ottieni modelli chat
    print("\n🔄 Recupero modelli...")
    modelli = ottieni_modelli_da_siliconflow()
    
    if not modelli:
        print("   ⚠️ Nessun modello trovato")
        return
    
    # Filtra modelli chat
    chat_modelli = []
    for model_id, nome, desc in modelli:
        if "vl" not in model_id.lower() and "vision" not in model_id.lower() and "internvl" not in model_id.lower():
            if "flux" not in model_id.lower() and "diffusion" not in model_id.lower():
                chat_modelli.append((model_id, nome, desc))
    
    if not chat_modelli:
        print("   ⚠️ Nessun modello chat trovato")
        return
    
    modello = scegli_modello_da_lista(chat_modelli[:5], "Scegli il modello per scrivere l'articolo")
    if modello is None:
        return
    
    model_id, model_name, desc = modello
    print_colored(f"\n✅ Modello: {model_name}", "green")
    
    tema = input("\n📌 Tema dell'articolo: ").strip()
    if not tema:
        print("❌ Tema non valido")
        return
    
    print("\n🎨 Stile:")
    print("   1. Tecnico")
    print("   2. Popolare")
    print("   3. Scientifico")
    print("   4. Divulgativo")
    
    style_choice = input("\n👉 Scegli stile (1-4): ").strip()
    styles = {"1": "Tecnico", "2": "Popolare", "3": "Scientifico", "4": "Divulgativo"}
    stile = styles.get(style_choice, "Popolare")
    
    print("\n📏 Lunghezza:")
    print("   1. Breve (500-800 parole)")
    print("   2. Medio (1000-1500 parole)")
    print("   3. Lungo (2000-3000 parole)")
    
    len_choice = input("\n👉 Scegli lunghezza (1-3): ").strip()
    lengths = {"1": "Breve (500-800 parole)", "2": "Medio (1000-1500 parole)", "3": "Lungo (2000-3000 parole)"}
    lunghezza = lengths.get(len_choice, "Medio (1000-1500 parole)")
    
    prompt = f"""Scrivi un articolo completo in italiano sul tema: {tema}

STILE: {stile}
LUNGHEZZA: {lunghezza}

STRUTTURA RICHIESTA:
1. Titolo accattivante
2. Introduzione che contestualizza
3. Sviluppo con paragrafi chiari
4. Esempi concreti e dati
5. Conclusione con riflessioni finali
6. Riferimenti o approfondimenti

REGOLE:
- Linguaggio appropriato allo stile scelto
- Struttura logica e progressiva
- Contenuto originale e ben documentato

Scrivi l'articolo completo in markdown."""
    
    print(f"\n📝 Generando articolo su: {tema}")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "Sei uno scrittore professionista. Scrivi articoli di alta qualità."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.7
        )
        
        articolo = response.choices[0].message.content
        print_colored(f"\n✅ Articolo completato!", "green")
        
        print(f"\n📄 Anteprima:")
        print_colored(articolo[:500] + "...\n", "cyan")
        
        salva_file(articolo, f"articolo_{tema.replace(' ', '_')}", "md")
        
    except Exception as e:
        print_colored(f"❌ Errore: {e}", "red")

def cmd_crea_presentazione():
    """Crea struttura per una presentazione"""
    print_header("🎯 CREAZIONE PRESENTAZIONE")
    
    # Modello fisso per presentazioni
    model_id = "deepseek-ai/DeepSeek-V3"
    model_name = "DeepSeek V3"
    
    print_colored(f"\n✅ Modello: {model_name}", "green")
    
    titolo = input("\n📌 Titolo della presentazione: ").strip()
    if not titolo:
        print("❌ Titolo non valido")
        return
    
    numero_slide = input("\n📊 Numero di slide (default 8): ").strip()
    numero_slide = int(numero_slide) if numero_slide.isdigit() else 8
    
    argomenti = input("\n📝 Argomenti principali (separati da virgola): ").strip()
    if not argomenti:
        print("❌ Argomenti non validi")
        return
    
    print("\n🎨 Stile presentazione:")
    print("   1. Professionale (business)")
    print("   2. Creativo (design)")
    print("   3. Accademico (ricerca)")
    print("   4. Divulgativo (semplice)")
    
    style_choice = input("\n👉 Scegli stile (1-4): ").strip()
    styles = {"1": "Professionale", "2": "Creativo", "3": "Accademico", "4": "Divulgativo"}
    stile = styles.get(style_choice, "Professionale")
    
    prompt = f"""Crea una presentazione completa in italiano su: {titolo}

DETTAGLI:
- NUMERO SLIDE: {numero_slide}
- ARGOMENTI: {argomenti}
- STILE: {stile}

STRUTTURA RICHIESTA PER OGNI SLIDE:
1. Titolo della slide
2. Contenuto principale (3-5 punti chiave)
3. Note per il presentatore
4. Immagine consigliata (descrizione)

Inizia con una slide di apertura e termina con una slide di conclusioni.
Restituisci la presentazione in formato markdown."""
    
    print(f"\n📊 Generando presentazione...")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "Sei un esperto di presentazioni. Crea strutture chiare e coinvolgenti."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096,
            temperature=0.7
        )
        
        presentazione = response.choices[0].message.content
        
        if presentazione.startswith("```markdown"):
            presentazione = presentazione[11:]
        if presentazione.startswith("```"):
            presentazione = presentazione[3:]
        if presentazione.endswith("```"):
            presentazione = presentazione[:-3]
        
        print_colored(f"\n✅ Presentazione completata!", "green")
        
        print(f"\n📄 Anteprima:")
        print_colored(presentazione[:500] + "...\n", "cyan")
        
        salva_file(presentazione, f"presentazione_{titolo.replace(' ', '_')}", "md")
        
    except Exception as e:
        print_colored(f"❌ Errore: {e}", "red")

def cmd_analizza_documento():
    """Analizza un documento con OCR"""
    print_header("📄 ANALISI DOCUMENTO")
    
    print("\n📌 Funzionalità:")
    print("   1. Analizza immagine/PDF (OCR)")
    print("   2. Riassumi testo")
    print("   3. Estrai concetti chiave")
    print("   4. Traduci documento")
    print("   5. Indietro")
    
    choice = input("\n👉 Scegli (1-5): ").strip()
    
    if choice == "5":
        return
    
    # Ottieni modelli visione
    print("\n🔄 Recupero modelli visione...")
    modelli = ottieni_modelli_da_siliconflow()
    
    vision_modelli = []
    for model_id, nome, desc in modelli:
        if "vl" in model_id.lower() or "vision" in model_id.lower() or "internvl" in model_id.lower():
            vision_modelli.append((model_id, nome, desc))
    
    if choice == "1":
        if not vision_modelli:
            print("   ⚠️ Nessun modello visione trovato")
            return
        
        # Usa il primo modello visione disponibile
        model_id, model_name, desc = vision_modelli[0]
        print_colored(f"\n✅ Modello OCR: {model_name}", "green")
        
        filepath = input("\n📁 Percorso del file (immagine): ").strip()
        if not filepath or not Path(filepath).exists():
            print("❌ File non trovato")
            return
        
        print(f"\n🔍 Analizzando: {filepath}")
        
        try:
            img = Image.open(filepath)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": f"data:image/png;base64,{img_base64}"
                            },
                            {
                                "type": "text",
                                "text": "Extract all text from this document. Output in markdown format."
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1
            )
            
            testo = response.choices[0].message.content
            print_colored(f"\n✅ Analisi completata!", "green")
            print(f"\n📄 Testo estratto:")
            print_colored(testo[:500] + "...\n", "cyan")
            
            salva_file(testo, "analisi_documento", "md")
            
        except Exception as e:
            print_colored(f"❌ Errore: {e}", "red")
    
    elif choice == "2":
        # Riassumi testo
        modello_chat = "deepseek-ai/DeepSeek-V3"
        
        testo = input("\n📝 Inserisci il testo da riassumere: ").strip()
        if not testo:
            print("❌ Testo non valido")
            return
        
        try:
            response = client.chat.completions.create(
                model=modello_chat,
                messages=[
                    {"role": "system", "content": "Sei un esperto di sintesi. Riassumi il testo in modo chiaro."},
                    {"role": "user", "content": f"Riassumi questo testo:\n\n{testo}"}
                ],
                max_tokens=1024,
                temperature=0.3
            )
            
            riassunto = response.choices[0].message.content
            print_colored(f"\n✅ Riassunto:", "green")
            print_colored(riassunto, "cyan")
            
            salva_file(riassunto, "riassunto", "md")
            
        except Exception as e:
            print_colored(f"❌ Errore: {e}", "red")

def cmd_usa_modello():
    """Usa un modello specifico per un task personalizzato"""
    print_header("🔧 USO MODELLO PERSONALIZZATO")
    
    print("\n🔄 Recupero modelli da SiliconFlow...")
    modelli = ottieni_modelli_da_siliconflow()
    
    if not modelli:
        print("   ⚠️ Nessun modello trovato")
        return
    
    modello = scegli_modello_da_lista(modelli, "Scegli il modello per il task personalizzato")
    if modello is None:
        return
    
    model_id, model_name, desc = modello
    print_colored(f"\n✅ Modello: {model_name}", "green")
    print(f"   {desc}")
    
    prompt = input("\n📝 Prompt: ").strip()
    if not prompt:
        print("❌ Prompt non valido")
        return
    
    print(f"\n🚀 Eseguendo con {model_name}...")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.7
        )
        
        risultato = response.choices[0].message.content
        print_colored(f"\n✅ Risultato:", "green")
        print_colored(risultato, "cyan")
        
        salva_file(risultato, f"output_{model_name.replace(' ', '_')}", "md")
        
    except Exception as e:
        print_colored(f"❌ Errore: {e}", "red")

# ============================================================
# MENU PRINCIPALE
# ============================================================

def main_menu():
    clear_screen()
    print_header("🧠 SILICONFLOW AI - CREAZIONE CONTENUTI MULTIMEDIALI")
    print_colored(f"\n🔑 Chiave: {API_KEY[:10]}...", "yellow")
    print_colored(f"🌐 Endpoint: {BASE_URL}", "yellow")
    
    print("\n📋 COMANDI:")
    print_colored("  1. 📋 Lista modelli disponibili", "cyan")
    print_colored("  2. 💬 Chat interattiva", "cyan")
    print_colored("  3. 🎨 Genera immagine", "cyan")
    print_colored("  4. 📝 Scrivi articolo", "cyan")
    print_colored("  5. 🎯 Crea presentazione", "cyan")
    print_colored("  6. 📄 Analizza documento (OCR)", "cyan")
    print_colored("  7. 🔧 Usa modello personalizzato", "cyan")
    print_colored("  0. 🚪 Esci", "cyan")
    print_colored("-" * 70, "cyan")
    
    choice = input("\n👉 Scegli un'opzione (0-7): ").strip()
    return choice

def main():
    while True:
        choice = main_menu()
        
        if choice == "0":
            print_colored("\n👋 Arrivederci!", "green")
            break
        elif choice == "1":
            cmd_lista_modelli()
        elif choice == "2":
            cmd_chat()
        elif choice == "3":
            cmd_genera_immagine()
        elif choice == "4":
            cmd_scrivi_articolo()
        elif choice == "5":
            cmd_crea_presentazione()
        elif choice == "6":
            cmd_analizza_documento()
        elif choice == "7":
            cmd_usa_modello()
        else:
            print_colored("❌ Comando non valido", "red")
        
        input("\n\n👉 Premi Enter per continuare...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n👋 Interrotto", "yellow")
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ Errore: {e}", "red")
        sys.exit(1)