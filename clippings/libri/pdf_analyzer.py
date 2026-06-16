#!/usr/bin/env python3
"""
pdf_analyzer.py - Analizza e converte PDF in Markdown per llm-Socrates
Supporta: Tesseract (locale, gratuito) o Vision-Language via SiliconFlow (API)
Flusso: PDF → OCR → Markdown strutturato
"""

import fitz
import os
import sys
import re
import time
import base64
import io
from pathlib import Path
from datetime import datetime
from typing import Optional, List

try:
    from pdf2image import convert_from_path
except ImportError:
    print("❌ pdf2image non installata. Esegui: pip install pdf2image")
    sys.exit(1)

try:
    import pytesseract
except ImportError:
    print("⚠️ pytesseract non installata. Esegui: pip install pytesseract")
    print("   (necessaria solo per modalità Tesseract)")

try:
    from openai import OpenAI
except ImportError:
    print("❌ openai non installata. Esegui: pip install openai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️ python-dotenv non installato. Esegui: pip install python-dotenv")

load_dotenv()

# ============================================================
# CONFIGURAZIONE - SILICONFLOW (per OCR via Vision-Language)
# ============================================================

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
if not SILICONFLOW_API_KEY:
    print("❌ SILICONFLOW_API_KEY non trovata nel .env")
    print("   Ottieni una chiave su: https://cloud.siliconflow.cn")
    print("   Aggiungi al .env: SILICONFLOW_API_KEY=sk-...")
    sys.exit(1)

# Endpoint corretto per SiliconFlow
DEEPSEEK_BASE_URL = "https://api.siliconflow.com/v1"

# Modelli testati e funzionanti su SiliconFlow
# Visione (OCR): Qwen3-VL 30B MoE
VISION_MODEL = "Qwen/Qwen3-VL-30B-A3B-Instruct"

# Modello chat per correzioni (opzionale)
CHAT_MODEL = "deepseek-ai/DeepSeek-V3"

# Percorso di Poppler per Windows
POPPLER_PATH = r"C:\poppler\poppler-26.02.0\Library\bin"


def setup_tesseract() -> bool:
    """Configura il percorso di Tesseract in base al sistema operativo."""
    try:
        import shutil
        
        if sys.platform == "win32":
            possibili_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for path in possibili_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    return True
        
        elif sys.platform in ["linux", "linux2", "darwin"]:
            tesseract_path = shutil.which('tesseract')
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                return True
        
        return False
    
    except Exception:
        return False


def get_poppler_path() -> Optional[str]:
    """Restituisce il percorso di Poppler in base al sistema operativo."""
    if sys.platform == "win32":
        if os.path.exists(POPPLER_PATH):
            return POPPLER_PATH
        alternative_paths = [
            r"C:\poppler\bin",
            r"C:\poppler\poppler-26.02.0\bin",
            r"C:\poppler\poppler-26.02.0\Library\bin",
            r"C:\Program Files\poppler\bin",
        ]
        for path in alternative_paths:
            if os.path.exists(path):
                return path
        return None
    else:
        import shutil
        if shutil.which('pdftoppm'):
            return None
    return None


def get_base_dir() -> Path:
    """Trova la directory llm-Socrates"""
    current = Path.cwd()
    if current.name == "llm-Socrates":
        return current
    if (current / "llm-Socrates").exists():
        return current / "llm-Socrates"
    for parent in current.parents:
        if parent.name == "llm-Socrates":
            return parent
    print(f"⚠️ llm-Socrates non trovata, uso: {current}")
    return current


def normalizza_nome(nome: str) -> str:
    """Converte un nome in minuscolo con underscore"""
    return nome.lower().replace(' ', '_').replace('-', '_')


def check_output_exists(output_path: Path) -> bool:
    """Controlla se il file esiste e chiede se sovrascrivere"""
    if output_path.exists():
        print(f"\n⚠️ Il file {output_path.name} esiste già in clippings/")
        choice = input("👉 Sovrascrivere? (s/n): ").strip().lower()
        return choice == 's'
    return True


def estrai_immagini_con_pymupdf(pdf_path: Path, assets_folder: Path, base_name: str) -> List[dict]:
    """Estrae le immagini dal PDF usando PyMuPDF"""
    doc = fitz.open(pdf_path)
    all_images = []
    image_counter = 0
    
    print("\n🖼️ Estrazione immagini...")
    
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
# MODALITÀ 1: TESSERACT OCR (locale, gratuito)
# ============================================================

def estrai_testo_con_tesseract(pdf_path: Path, lingua: str = 'eng+ita') -> List[str]:
    """OCR con Tesseract (locale, gratuito)"""
    print(f"\n🔍 Tesseract OCR (lingua: {lingua})...")
    print("   ⏳ Conversione pagine in immagini (300 DPI)...")
    
    poppler_path = get_poppler_path()
    if poppler_path:
        images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    else:
        images = convert_from_path(pdf_path, dpi=300)
    
    print(f"   📄 {len(images)} pagine trovate")
    
    testo_per_pagina = []
    
    for i, image in enumerate(images):
        print(f"   📄 Pagina {i+1}/{len(images)} - OCR...")
        try:
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, lang=lingua, config=custom_config)
            testo_per_pagina.append(text)
        except Exception as e:
            print(f"      ⚠️ Errore OCR: {e}")
            testo_per_pagina.append("")
        time.sleep(0.05)
    
    return testo_per_pagina


def correggi_con_llm(testo: str, pagina: int) -> str:
    """Corregge errori OCR con LLM (DeepSeek-V3 via SiliconFlow)"""
    if not SILICONFLOW_API_KEY or len(testo.strip()) < 200:
        return testo
    
    client = OpenAI(
        api_key=SILICONFLOW_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )
    
    prompt = f"""Sei un correttore OCR professionista. Il testo seguente è stato estratto con Tesseract OCR.

Correggi SOLO gli errori OCR evidenti:
- Lettere confuse (es. 'wnite' → 'finite')
- Spazi mancanti o errati
- Caratteri speciali mal riconosciuti

PRESERVA:
- Formattazione originale
- Nomi propri, termini tecnici, numeri

TESTO (pagina {pagina}):

{testo}

TESTO CORRETTO:"""

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "Sei un correttore OCR esperto."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000,
        )
        testo_corretto = response.choices[0].message.content
        if testo_corretto.startswith("TESTO CORRETTO:"):
            testo_corretto = testo_corretto[15:]
        return testo_corretto.strip()
    except Exception as e:
        print(f"      ⚠️ Errore correzione: {e}")
        return testo


# ============================================================
# MODALITÀ 2: VISION-LANGUAGE via SILICONFLOW (Qwen3-VL)
# ============================================================

def estrai_testo_con_visione(pdf_path: Path) -> List[str]:
    """
    OCR con Qwen3-VL via SiliconFlow
    Modello testato: Qwen/Qwen3-VL-30B-A3B-Instruct
    """
    if not SILICONFLOW_API_KEY:
        print("   ❌ SILICONFLOW_API_KEY non configurata")
        return []
    
    print(f"\n🔍 OCR via SiliconFlow (Qwen3-VL 30B)...")
    print("   ⏳ Conversione pagine in immagini (200 DPI)...")
    
    poppler_path = get_poppler_path()
    if poppler_path:
        images = convert_from_path(pdf_path, dpi=200, poppler_path=poppler_path)
    else:
        images = convert_from_path(pdf_path, dpi=200)
    
    print(f"   📄 {len(images)} pagine trovate")
    
    client = OpenAI(
        api_key=SILICONFLOW_API_KEY,
        base_url=DEEPSEEK_BASE_URL
    )
    
    testo_per_pagina = []
    
    for i, image in enumerate(images):
        print(f"   📄 Pagina {i+1}/{len(images)} - OCR in corso...")
        
        try:
            # Converti immagine in base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Chiamata al modello visione
            response = client.chat.completions.create(
                model=VISION_MODEL,
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
                                "text": """Extract all text from this document page. 
Preserve the structure and formatting. 
Output in clean markdown format.
Keep headings, lists, tables, and important formatting."""
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1
            )
            
            testo = response.choices[0].message.content
            testo_per_pagina.append(testo)
            print(f"      ✅ {len(testo)} caratteri estratti")
            
        except Exception as e:
            print(f"      ⚠️ Errore OCR pagina {i+1}: {e}")
            testo_per_pagina.append("")
        
        # Pausa per evitare rate limiting
        if i < len(images) - 1:
            time.sleep(0.5)
    
    return testo_per_pagina


# ============================================================
# CREAZIONE MARKDOWN UNIFICATA
# ============================================================

def crea_markdown(testo_per_pagina: List[str], all_images: List[dict], 
                  base_name: str, output_dir: Path, metodo: str) -> Path:
    """Crea il file Markdown dal testo OCR e dalle immagini"""
    md_content = f"""---
title: {base_name}
source: {base_name}.pdf
converted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ocr_method: {metodo}
---

# 📄 {base_name}

## 📝 Contenuto

"""
    
    images_used = 0
    
    print("\n📝 Creazione Markdown...")
    
    # Per Vision-Language (una sola pagina o più pagine)
    if metodo == 'visione':
        for page_num, text in enumerate(testo_per_pagina):
            if not text or not text.strip():
                continue
            
            # Aggiungi separatore pagina se ci sono più pagine
            if len(testo_per_pagina) > 1:
                md_content += f"\n### Pagina {page_num + 1}\n\n"
            
            md_content += text
            md_content += "\n"
            
            # Inserisci immagini della pagina corrente
            while images_used < len(all_images) and all_images[images_used]['page'] == page_num:
                img = all_images[images_used]
                md_content += f"\n![{img['filename']}](/asset/{img['filename']})\n"
                print(f"   🖼️ Immagine {img['filename']} (pag. {page_num + 1})")
                images_used += 1
            
            md_content += "\n---\n"
    
    # Per Tesseract (multipagina)
    else:
        for page_num, text in enumerate(testo_per_pagina):
            if not text or not text.strip():
                continue
            
            md_content += f"\n### Pagina {page_num + 1}\n\n"
            md_content += text
            md_content += "\n"
            
            while images_used < len(all_images) and all_images[images_used]['page'] == page_num:
                img = all_images[images_used]
                md_content += f"\n![{img['filename']}](/asset/{img['filename']})\n"
                print(f"   🖼️ Immagine {img['filename']} (pag. {page_num + 1})")
                images_used += 1
            
            md_content += "\n---\n"
    
    # Immagini residue (senza pagina associata)
    if images_used < len(all_images):
        md_content += "\n## 🖼️ Immagini residue\n\n"
        for i in range(images_used, len(all_images)):
            img = all_images[i]
            md_content += f"![{img['filename']}](/asset/{img['filename']})\n"
    
    nome_file = normalizza_nome(base_name)
    md_path = output_dir / f"{nome_file}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return md_path


# ============================================================
# CONVERSIONE COMPLETA
# ============================================================

def converti_pdf(pdf_path: Path, output_dir: Path, assets_folder: Path,
                 metodo: str = 'tesseract', lingua: str = 'eng+ita',
                 correggi_ocr: bool = False) -> bool:
    """Conversione completa PDF → Markdown"""
    base_name_raw = pdf_path.stem
    base_name_normalizzato = normalizza_nome(base_name_raw)
    
    print(f"\n{'='*60}")
    print(f"📄 CONVERSIONE: {base_name_raw}.pdf")
    print(f"{'='*60}")
    
    assets_folder.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # STEP 1: Estrai immagini (sempre con PyMuPDF)
    all_images = estrai_immagini_con_pymupdf(pdf_path, assets_folder, base_name_normalizzato)
    
    # STEP 2: OCR
    if metodo == 'tesseract':
        testo_per_pagina = estrai_testo_con_tesseract(pdf_path, lingua)
        
        # Correzione opzionale con LLM
        if correggi_ocr and SILICONFLOW_API_KEY:
            print("\n🔍 STEP 2b: Correzione errori OCR con LLM...")
            testo_corretto = []
            for i, testo in enumerate(testo_per_pagina):
                if testo and len(testo.strip()) > 100:
                    print(f"   📄 Pagina {i+1}/{len(testo_per_pagina)} - correzione...")
                    testo_pulito = correggi_con_llm(testo, i+1)
                    testo_corretto.append(testo_pulito)
                    time.sleep(0.3)
                else:
                    testo_corretto.append(testo)
            testo_per_pagina = testo_corretto
        
    elif metodo == 'visione':
        testo_per_pagina = estrai_testo_con_visione(pdf_path)
    else:
        print(f"❌ Metodo sconosciuto: {metodo}")
        return False
    
    if not testo_per_pagina or all(not t.strip() for t in testo_per_pagina):
        print("❌ Nessun testo estratto")
        return False
    
    # STEP 3: Crea Markdown
    md_path = crea_markdown(testo_per_pagina, all_images, base_name_normalizzato, 
                           output_dir, metodo)
    
    # Report
    print(f"\n{'='*60}")
    print(f"✅ CONVERSIONE COMPLETATA!")
    print(f"{'='*60}")
    print(f"📁 PDF sorgente:    {pdf_path}")
    print(f"📝 Markdown:        {md_path}")
    print(f"🖼️ Immagini:        {assets_folder} ({len(all_images)} file)")
    print(f"🔧 OCR:             {metodo}")
    if metodo == 'tesseract' and correggi_ocr:
        print(f"🤖 Correzione:      LLM (DeepSeek-V3)")
    print(f"{'='*60}")
    
    return True


# ============================================================
# MENU INTERATTIVO
# ============================================================

def list_pdf_files(pdf_folder: Path) -> List[Path]:
    pdf_files = []
    if pdf_folder.exists():
        for f in pdf_folder.iterdir():
            if f.suffix.lower() == '.pdf':
                pdf_files.append(f)
    return sorted(pdf_files)


def show_menu(pdf_files: List[Path], pdf_folder: Path):
    print(f"\n{'='*60}")
    print(f"📁 PDF DISPONIBILI in: {pdf_folder}")
    print(f"{'='*60}")
    for i, pdf in enumerate(pdf_files, 1):
        size = pdf.stat().st_size / (1024 * 1024)
        print(f"   {i:2}. {pdf.name:<40} ({size:.1f} MB)")
    print(f"{'='*60}")
    print(f"   0. Esci")
    print(f"{'='*60}")


def get_user_choice(pdf_files: List[Path]) -> Optional[Path]:
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


def scegli_metodo() -> tuple:
    """Sceglie il metodo OCR e restituisce (metodo, lingua, correggi)"""
    print("\n" + "=" * 60)
    print("🔧 SCEGLI IL METODO OCR")
    print("=" * 60)
    print("")
    print("  📍 METODO 1: Tesseract (locale, gratuito)")
    print("     ✅ Veloce, offline, nessun costo")
    print("     ❌ Meno preciso su layout complessi")
    print("")
    print("  📍 METODO 2: Qwen3-VL via SiliconFlow (API, alta qualità)")
    print(f"     ✅ Modello: {VISION_MODEL}")
    print("     ✅ Massima precisione, output Markdown strutturato")
    print("     ✅ Gestisce tabelle, formule, layout complessi")
    print("     💰 Costo: ~$0.29 per milione di token")
    print("     🌐 Richiede connessione internet")
    print("")
    
    while True:
        choice = input("👉 Scegli (1=Tesseract, 2=Qwen3-VL): ").strip()
        
        if choice == '1':
            print("\n🌐 Lingua del PDF:")
            print("   1. Inglese (eng)")
            print("   2. Italiano (ita)")
            print("   3. Entrambe (eng+ita) - consigliato")
            lingua_choice = input("👉 Scegli (1-3): ").strip()
            
            if lingua_choice == '1':
                lingua = 'eng'
            elif lingua_choice == '2':
                lingua = 'ita'
            else:
                lingua = 'eng+ita'
            
            print("\n🔧 Correggere errori OCR con LLM?")
            print("   (usa DeepSeek-V3 via SiliconFlow)")
            correggi = input("👉 (s/n): ").strip().lower() == 's'
            
            return ('tesseract', lingua, correggi)
        
        elif choice == '2':
            if not SILICONFLOW_API_KEY:
                print("   ❌ SILICONFLOW_API_KEY non configurata nel .env")
                print("   Usa Tesseract o configura la chiave.")
                continue
            return ('visione', 'eng+ita', False)
        
        else:
            print("❌ Scelta non valida. Inserisci 1 o 2.")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("📄 PDF ANALYZER - Converte PDF in Markdown")
    print("   Tesseract (locale) o Qwen3-VL via SiliconFlow")
    print(f"   Sistema: {sys.platform}")
    print("=" * 60)
    
    print("\n🔧 Configurazione Tesseract...")
    if setup_tesseract():
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract {version} pronto")
        except Exception:
            print(f"✅ Tesseract disponibile")
    else:
        print("\n⚠️ Tesseract non trovato. La modalità Tesseract non sarà disponibile.")
        if sys.platform == "win32":
            print("   Su Windows, scarica da: https://github.com/UB-Mannheim/tesseract/wiki")
    
    poppler_path = get_poppler_path()
    if poppler_path:
        print(f"✅ Poppler trovato: {poppler_path}")
    elif sys.platform == "win32":
        print("⚠️ Poppler non trovato. Verifica il percorso in POPPLER_PATH")
    
    if SILICONFLOW_API_KEY:
        print(f"✅ SiliconFlow API key configurata")
        print(f"   Modello Visione: {VISION_MODEL}")
        print(f"   Modello Chat: {CHAT_MODEL}")
    else:
        print("⚠️ SiliconFlow API key non trovata. Qwen3-VL non disponibile.")
        print("   Aggiungi SILICONFLOW_API_KEY al .env")
    
    base_dir = get_base_dir()
    print(f"\n📂 Base directory: {base_dir}")
    
    pdf_folder = base_dir / "clippings"
    assets_folder = base_dir / "asset"
    output_dir = base_dir / "clippings"
    
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
    
    nome_atteso = normalizza_nome(selected_pdf.stem)
    md_path = output_dir / f"{nome_atteso}.md"
    if not check_output_exists(md_path):
        print("❌ Operazione annullata")
        sys.exit(0)
    
    metodo, lingua, correggi = scegli_metodo()
    
    converti_pdf(selected_pdf, output_dir, assets_folder, metodo, lingua, correggi)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrotto")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        sys.exit(1)