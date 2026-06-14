#!/usr/bin/env python3
"""
pdf_to_md.py - Converte PDF in Markdown per llm-Socrates
Flusso: Tesseract OCR → DeepSeek correzione fine → Markdown
Struttura:
    Input:  llm-Socrates/clippings/*.pdf
    Output: llm-Socrates/clippings/*.md (stessa cartella del PDF)
    Immagini: llm-Socrates/asset/*.png/.jpg
"""

import fitz
import os
import sys
import re
import time
from pathlib import Path
from datetime import datetime

# OCR libraries
try:
    from pdf2image import convert_from_path
except ImportError:
    print("❌ pdf2image non installata. Esegui: pip install pdf2image")
    sys.exit(1)

try:
    import pytesseract
except ImportError:
    print("❌ pytesseract non installata. Esegui: pip install pytesseract")
    sys.exit(1)

# AI correction
try:
    from openai import OpenAI
except ImportError:
    print("❌ openai non installata. Esegui: pip install openai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv non installato. Esegui: pip install python-dotenv")

# ============================================================
# CONFIGURAZIONE
# ============================================================

DEEPSEEK_API_KEY = None

def carica_api_key():
    """Carica DeepSeek API key da .env"""
    global DEEPSEEK_API_KEY
    
    env_paths = [
        Path.cwd() / ".env",
        Path.cwd() / "llm-Socrates" / ".env",
        Path(__file__).parent / ".env",
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Letto .env da: {env_path}")
            break
    
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
    
    if not DEEPSEEK_API_KEY:
        print("\n⚠️  DEEPSEEK_API_KEY non trovata")
        print("   La correzione con DeepSeek non sarà disponibile")
    
    return DEEPSEEK_API_KEY


def get_base_dir():
    """Trova la directory llm-Socrates"""
    current = Path.cwd()
    
    if current.name == "llm-Socrates":
        return current
    if (current / "llm-Socrates").exists():
        return current / "llm-Socrates"
    for parent in current.parents:
        if parent.name == "llm-Socrates":
            return parent
    
    print(f"⚠️  llm-Socrates non trovata, uso: {current}")
    return current


def check_output_exists(output_path):
    """Controlla se il file esiste e chiede se sovrascrivere"""
    if output_path.exists():
        print(f"\n⚠️  Il file {output_path.name} esiste già in clippings/")
        choice = input("👉 Sovrascrivere? (s/n): ").strip().lower()
        return choice == 's'
    return True


# ============================================================
# STEP 1: TESSERACT OCR
# ============================================================

def estrai_testo_con_tesseract(pdf_path, lingua='eng+ita'):
    """
    Converte ogni pagina PDF in immagine e applica OCR con Tesseract
    """
    print(f"\n🔍 STEP 1: Tesseract OCR (lingua: {lingua})...")
    print("   ⏳ Conversione pagine in immagini (300 DPI)...")
    
    images = convert_from_path(pdf_path, dpi=300)
    
    print(f"   📄 {len(images)} pagine trovate")
    
    testo_per_pagina = []
    
    for i, image in enumerate(images):
        print(f"   📄 Pagina {i+1}/{len(images)} - OCR...")
        
        try:
            # Configura Tesseract per massima qualità
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, lang=lingua, config=custom_config)
            testo_per_pagina.append(text)
        except Exception as e:
            print(f"      ⚠️ Errore OCR: {e}")
            testo_per_pagina.append("")
        
        time.sleep(0.05)  # Pausa leggera
    
    return testo_per_pagina


def estrai_immagini_con_pymupdf(pdf_path, assets_folder, base_name):
    """
    Estrae le immagini dal PDF usando PyMuPDF
    """
    doc = fitz.open(pdf_path)
    all_images = []
    image_counter = 0
    
    print("\n🖼️ STEP 2: Estrazione immagini...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        
        for img in image_list:
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                
                if pix.n - pix.alpha < 4:
                    ext = "png"
                    img_data = pix.tobytes("png")
                else:
                    ext = "jpg"
                    img_data = pix.tobytes("jpeg")
                
                img_filename = f"{base_name}_img_{image_counter}.{ext}"
                img_path = assets_folder / img_filename
                
                with open(img_path, "wb") as f:
                    f.write(img_data)
                
                all_images.append({
                    'page': page_num,
                    'filename': img_filename,
                    'counter': image_counter
                })
                
                print(f"   ✅ {img_filename} (pag. {page_num + 1})")
                image_counter += 1
                pix = None
            except Exception as e:
                print(f"   ⚠️ Errore immagine: {e}")
    
    doc.close()
    print(f"\n📊 Totale immagini: {image_counter}")
    
    return all_images


# ============================================================
# STEP 2: DEEPSEEK CORREZIONE FINE
# ============================================================

def correggi_con_deepseek(testo: str, pagina: int) -> str:
    """
    Usa DeepSeek per correggere errori residui dopo Tesseract
    """
    if not DEEPSEEK_API_KEY or len(testo.strip()) < 200:
        return testo
    
    prompt = f"""Sei un correttore OCR professionista. Il testo seguente è stato estratto con Tesseract OCR da un PDF.

Correggi SOLO gli errori OCR evidenti:
- Lettere confuse (es. 'wnite' → 'finite')
- Spazi mancanti o errati
- Caratteri speciali mal riconosciuti

PRESERVA:
- Formattazione originale
- Nomi propri, termini tecnici, numeri
- Parole che sembrano corrette

TESTO (pagina {pagina}):

{testo}

TESTO CORRETTO:"""

    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Sei un correttore OCR esperto. Correggi solo errori evidenti, preserva il resto."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000,
        )
        
        testo_corretto = response.choices[0].message.content
        
        # Pulizia
        if testo_corretto.startswith("TESTO CORRETTO:"):
            testo_corretto = testo_corretto[15:]
        
        return testo_corretto.strip()
        
    except Exception as e:
        print(f"      ⚠️ Errore DeepSeek: {e}")
        return testo


def correggi_testo_con_deepseek(testo_per_pagina, usa_deepseek=True):
    """
    Corregge ogni pagina con DeepSeek (opzionale)
    """
    if not usa_deepseek or not DEEPSEEK_API_KEY:
        return testo_per_pagina
    
    print("\n🔍 STEP 3: Correzione fine con DeepSeek...")
    
    testo_corretto = []
    
    for i, testo in enumerate(testo_per_pagina):
        if testo and len(testo.strip()) > 100:
            print(f"   📄 Pagina {i+1}/{len(testo_per_pagina)} - correzione...")
            testo_pulito = correggi_con_deepseek(testo, i+1)
            testo_corretto.append(testo_pulito)
            time.sleep(0.3)  # Rate limiting
        else:
            testo_corretto.append(testo)
    
    return testo_corretto


# ============================================================
# STEP 3: CREAZIONE MARKDOWN
# ============================================================

def crea_markdown(testo_per_pagina, all_images, base_name, output_dir):
    """
    Crea il file Markdown unendo testo e immagini
    output_dir = clippings/ (stessa cartella del PDF)
    """
    caption_pattern = re.compile(
        r'(?:Figure|Fig\.|Figura|FIGURE)\s+([\d\.]+)[\s:]*([^\n]+)',
        re.IGNORECASE
    )
    
    md_content = f"""---
title: {base_name}
source: {base_name}.pdf
converted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ocr_engine: Tesseract + DeepSeek
---

# 📄 {base_name}

## 📝 Contenuto

"""
    
    images_used = 0
    
    print("\n📝 STEP 4: Creazione Markdown in clippings/...")
    
    for page_num, text in enumerate(testo_per_pagina):
        if not text or not text.strip():
            continue
        
        md_content += f"\n### Pagina {page_num + 1}\n\n"
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                md_content += "\n"
                continue
            
            caption_match = caption_pattern.search(line)
            
            if caption_match:
                caption_number = caption_match.group(1)
                caption_text = caption_match.group(2).strip()
                
                md_content += f"\n**Figura {caption_number}:** {caption_text}\n\n"
                
                if images_used < len(all_images):
                    img = all_images[images_used]
                    md_content += f"![{img['filename']}](/asset/{img['filename']})\n"
                    print(f"   🔗 Figura {caption_number} → {img['filename']}")
                    images_used += 1
                else:
                    md_content += "\n*[Immagine non trovata]*\n"
            else:
                md_content += f"{line}\n"
        
        md_content += "\n---\n"
    
    # Immagini residue
    if images_used < len(all_images):
        md_content += "\n## 🖼️ Immagini senza didascalia\n\n"
        for i in range(images_used, len(all_images)):
            img = all_images[i]
            md_content += f"![{img['filename']}](/asset/{img['filename']})\n"
    
    # Salva nella stessa cartella del PDF (clippings/)
    md_path = output_dir / f"{base_name}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return md_path


# ============================================================
# CONVERSIONE COMPLETA
# ============================================================

def converti_pdf(pdf_path, output_dir, assets_folder, lingua='eng+ita', usa_deepseek=True):
    """
    Conversione completa PDF → Markdown
    output_dir = clippings/ (dove salvare il .md)
    assets_folder = asset/ (dove salvare le immagini)
    """
    base_name = pdf_path.stem
    
    print(f"\n{'='*60}")
    print(f"📄 CONVERSIONE: {base_name}.pdf")
    print(f"{'='*60}")
    
    # Crea cartelle
    assets_folder.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # STEP 1: Estrai immagini con PyMuPDF
    all_images = estrai_immagini_con_pymupdf(pdf_path, assets_folder, base_name)
    
    # STEP 2: Tesseract OCR
    testo_tesseract = estrai_testo_con_tesseract(pdf_path, lingua)
    
    # STEP 3: DeepSeek correzione (opzionale)
    if usa_deepseek and DEEPSEEK_API_KEY:
        testo_finale = correggi_testo_con_deepseek(testo_tesseract, usa_deepseek)
    else:
        testo_finale = testo_tesseract
    
    # STEP 4: Crea Markdown in clippings/
    md_path = crea_markdown(testo_finale, all_images, base_name, output_dir)
    
    # Report finale
    print(f"\n{'='*60}")
    print(f"✅ CONVERSIONE COMPLETATA!")
    print(f"{'='*60}")
    print(f"📁 PDF sorgente:    {pdf_path}")
    print(f"📝 Markdown:        {md_path}")
    print(f"🖼️ Immagini:        {assets_folder} ({len(all_images)} file)")
    print(f"🔧 OCR:             Tesseract ({lingua})")
    if usa_deepseek and DEEPSEEK_API_KEY:
        print(f"🤖 Correzione:      DeepSeek")
    print(f"{'='*60}")


# ============================================================
# MENU INTERATTIVO
# ============================================================

def list_pdf_files(pdf_folder):
    pdf_files = []
    if pdf_folder.exists():
        for f in pdf_folder.iterdir():
            if f.suffix.lower() == '.pdf':
                pdf_files.append(f)
    return sorted(pdf_files)


def show_menu(pdf_files, pdf_folder):
    print(f"\n{'='*60}")
    print(f"📁 PDF DISPONIBILI in: {pdf_folder}")
    print(f"{'='*60}")
    
    for i, pdf in enumerate(pdf_files, 1):
        size = pdf.stat().st_size / (1024 * 1024)
        print(f"   {i:2}. {pdf.name:<40} ({size:.1f} MB)")
    
    print(f"{'='*60}")
    print(f"   0. Esci")
    print(f"{'='*60}")


def get_user_choice(pdf_files):
    while True:
        try:
            choice = input(f"\n👉 Scegli il numero del PDF da convertire [1-{len(pdf_files)} o 0]: ")
            choice = int(choice)
            
            if choice == 0:
                return None
            if 1 <= choice <= len(pdf_files):
                return pdf_files[choice - 1]
            else:
                print(f"❌ Numero da 1 a {len(pdf_files)}")
        except ValueError:
            print("❌ Inserisci un numero valido")
        except KeyboardInterrupt:
            print("\n")
            return None


def scegli_lingua():
    print("\n🌐 Lingua del PDF per OCR:")
    print("   1. Inglese (eng)")
    print("   2. Italiano (ita)")
    print("   3. Entrambe (eng+ita) - consigliato")
    
    while True:
        choice = input("\n👉 Scegli (1-3): ").strip()
        if choice == '1':
            return 'eng'
        elif choice == '2':
            return 'ita'
        elif choice == '3':
            return 'eng+ita'
        else:
            print("❌ Scelta non valida")


def chiedi_deepseek():
    if not DEEPSEEK_API_KEY:
        return False
    
    print("\n🤖 Correzione fine con DeepSeek:")
    print("   1. Sì, correggi errori residui (consigliato)")
    print("   2. No, usa solo Tesseract (più veloce)")
    
    while True:
        choice = input("\n👉 Scegli (1-2): ").strip()
        if choice == '1':
            return True
        elif choice == '2':
            return False
        else:
            print("❌ Scelta non valida")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("📄 CONVERTITORE PDF → MARKDOWN")
    print("   Tesseract OCR + DeepSeek correzione")
    print("=" * 60)
    
    # Verifica Tesseract
    print("\n🔧 Verifica Tesseract...")
    try:
        version = pytesseract.get_tesseract_version()
        print(f"   ✅ Tesseract {version} installato")
    except Exception:
        print("   ❌ Tesseract non trovato!")
        print("\n   Su Windows, scarica da:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        sys.exit(1)
    
    # Carica API key DeepSeek
    carica_api_key()
    
    # Trova base directory
    base_dir = get_base_dir()
    print(f"\n📂 Base directory: {base_dir}")
    
    # PERCORSI AGGIORNATI
    pdf_folder = base_dir / "clippings"      # PDF input
    assets_folder = base_dir / "asset"       # Immagini output
    output_dir = base_dir / "clippings"      # MARKDOWN output (stessa cartella del PDF)
    
    if not pdf_folder.exists():
        print(f"\n❌ Cartella 'clippings/' non trovata")
        sys.exit(1)
    
    pdf_files = list_pdf_files(pdf_folder)
    
    if not pdf_files:
        print(f"\n❌ Nessun file PDF trovato in: {pdf_folder}")
        sys.exit(1)
    
    show_menu(pdf_files, pdf_folder)
    
    selected_pdf = get_user_choice(pdf_files)
    
    if selected_pdf is None:
        print("\n👋 Arrivederci!")
        sys.exit(0)
    
    print(f"\n✅ Selezionato: {selected_pdf.name}")
    
    # Verifica esistenza del Markdown in clippings/
    md_path = output_dir / f"{selected_pdf.stem}.md"
    if not check_output_exists(md_path):
        print("❌ Operazione annullata")
        sys.exit(0)
    
    # Configurazioni
    lingua = scegli_lingua()
    usa_deepseek = chiedi_deepseek()
    
    # Converti
    converti_pdf(selected_pdf, output_dir, assets_folder, lingua, usa_deepseek)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrotto")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        sys.exit(1)