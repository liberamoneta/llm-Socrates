#!/usr/bin/env python3
"""
Traduttore di file markdown usando DeepSeek API
Cerca file SOLO in llm-Socrates/clippings/
Traduce in ITALIANO o RUSSO
Salva in vault/raw/
"""

import os
import sys
import time
import re
from pathlib import Path
from typing import Optional, List

try:
    from openai import OpenAI
except ImportError:
    print("❌ openai non installata. Esegui: pip install openai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv non installato. Esegui: pip install python-dotenv")
    sys.exit(1)

# Configurazione
ASSET_DIR = "asset"

def carica_api_key():
    """Carica DeepSeek API key da .env"""
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
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("\n❌ DEEPSEEK_API_KEY non trovata")
        print("\nCrea file .env con:")
        print("   DEEPSEEK_API_KEY=sk-tua-chiave")
        sys.exit(1)
    
    return api_key

DEEPSEEK_API_KEY = carica_api_key()

def trova_base_dir() -> Optional[Path]:
    """Trova la directory llm-Socrates"""
    possibili_paths = [
        Path.cwd() / "llm-Socrates",
        Path.cwd(),
        Path.home() / "llm-Socrates",
        Path(__file__).parent / "llm-Socrates",
    ]
    
    for path in possibili_paths:
        if path.exists() and (path / "asset").exists() and (path / "clippings").exists():
            return path
    
    return None

def trova_file_markdown(base_dir: Path) -> List[Path]:
    """Trova file markdown SOLO in clippings/"""
    file_trovati = []
    clippings_dir = base_dir / "clippings"
    
    if not clippings_dir.exists():
        print(f"\n⚠️  Directory 'clippings/' non trovata")
        return file_trovati
    
    for file in clippings_dir.glob("*.md"):
        # Escludi già tradotti
        if not any(file.name.endswith(suffix) for suffix in ['-it.md', '-ru.md', '-en.md']):
            file_trovati.append(file)
    
    return sorted(file_trovati)

def correggi_percorsi_immagini(testo: str) -> str:
    """Corregge i percorsi delle immagini per puntare a /asset/"""
    
    # Pattern per: [![transactions.png]](url)
    pattern = r'\[!\[\[(.*?)\]\]\]\(https://github\.com/karask/satoshi-paper/blob/master/img/.*?\)'
    testo = re.sub(pattern, f'![\\1]({ASSET_DIR}/\\1)', testo)
    
    return testo

def traduci_con_deepseek(testo: str, lingua: str) -> Optional[str]:
    """Traduce usando DeepSeek API"""
    
    lingua_nome = 'italiano' if lingua == 'it' else 'russo'
    
    prompt = f"""Traduci il seguente testo dall'inglese al {lingua_nome}.

REGOLE:
1. PRESERVA: blocchi di codice (```), formule ($$), YAML (---), link e immagini
2. TRADUCI: tutto il resto, inclusi titoli e paragrafi

TESTO:
{testo}

Traduzione in {lingua_nome}:"""

    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"Sei un traduttore tecnico. Traduci dall'inglese al {lingua_nome} preservando codice e formattazione."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=32000,
        )
        
        traduzione = response.choices[0].message.content
        
        # Pulizia
        if traduzione.startswith("```markdown"):
            traduzione = traduzione[11:]
        if traduzione.startswith("```"):
            traduzione = traduzione[3:]
        if traduzione.endswith("```"):
            traduzione = traduzione[:-3]
        
        return traduzione.strip()
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return None

def traduci_file(file_path: Path, output_dir: Path, lingua: str) -> bool:
    """Traduce un singolo file"""
    
    print(f"\n📄 {file_path.name}")
    
    # Leggi
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            testo = f.read()
        print(f"   📖 {len(testo)} caratteri")
    except Exception as e:
        print(f"   ❌ {e}")
        return False
    
    # Traduci
    lingua_nome = 'italiano' if lingua == 'it' else 'russo'
    print(f"   🤖 Traduzione EN → {lingua_nome}...")
    
    inizio = time.time()
    tradotto = traduci_con_deepseek(testo, lingua)
    if not tradotto:
        return False
    
    print(f"   ✅ {time.time()-inizio:.1f}s")
    
    # Correggi immagini
    tradotto = correggi_percorsi_immagini(tradotto)
    
    # Salva
    suffisso = '-it.md' if lingua == 'it' else '-ru.md'
    output_path = output_dir / f"{file_path.stem}{suffisso}"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tradotto)
    
    print(f"   💾 {output_path.name}")
    return True

def main():
    print("="*60)
    print("📖 TRADUTTORE MARKDOWN con DEEPSEEK")
    print("="*60)
    
    # Trova base directory
    base_dir = trova_base_dir()
    if not base_dir:
        print("\n❌ llm-Socrates non trovata")
        return
    
    print(f"\n📂 {base_dir}")
    
    # Trova file SOLO in clippings
    file_lista = trova_file_markdown(base_dir)
    
    if not file_lista:
        print("\n❌ Nessun file .md in clippings/")
        return
    
    print(f"\n📁 File in clippings/ ({len(file_lista)}):")
    print("-"*40)
    for i, f in enumerate(file_lista, 1):
        print(f"   {i}. {f.name}")
    print("-"*40)
    print("   0. Esci")
    
    # Scelta
    try:
        scelta = input("\n👉 Scegli file (numero o 'all'): ").strip()
        if scelta == '0':
            return
        
        if scelta.lower() == 'all':
            file_selezionati = file_lista
        else:
            idx = int(scelta) - 1
            file_selezionati = [file_lista[idx]]
    except:
        print("❌ Scelta non valida")
        return
    
    # Lingua
    print("\n🌐 Lingua:")
    print("   1. Italiano")
    print("   2. Русский")
    lingua_choice = input("\n👉 Scegli (1-2): ").strip()
    lingua = 'it' if lingua_choice == '1' else 'ru'
    
    # Output
    output_dir = base_dir / "vault" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📂 Output: {output_dir}")
    
    # Conferma
    print(f"\n📊 Riepilogo:")
    print(f"   File: {len(file_selezionati)}")
    print(f"   Lingua: {'Italiano' if lingua == 'it' else 'Russo'}")
    
    if input("\n👉 Procedere? (s/n): ").lower() != 's':
        return
    
    # Traduci
    successi = 0
    for i, f in enumerate(file_selezionati, 1):
        print(f"\n📌 [{i}/{len(file_selezionati)}]")
        if traduci_file(f, output_dir, lingua):
            successi += 1
        if i < len(file_selezionati):
            time.sleep(1)
    
    print(f"\n✅ Tradotti: {successi}/{len(file_selezionati)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrotto")