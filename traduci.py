#!/usr/bin/env python3
"""
Traduttore di file markdown usando DeepSeek API
Cerca file SOLO in llm-Socrates/clippings/
Traduce in ITALIANO o RUSSO
Salva in vault/raw/
Supporta traduzioni multiple in sequenza
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
        print(f"   ❌ Errore API: {e}")
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
        print(f"   ❌ Errore lettura: {e}")
        return False
    
    # Traduci
    lingua_nome = 'italiano' if lingua == 'it' else 'russo'
    print(f"   🤖 Traduzione EN → {lingua_nome}...")
    
    inizio = time.time()
    tradotto = traduci_con_deepseek(testo, lingua)
    if not tradotto:
        return False
    
    print(f"   ✅ Completata in {time.time()-inizio:.1f}s")
    
    # Correggi immagini
    tradotto = correggi_percorsi_immagini(tradotto)
    
    # Salva
    suffisso = '-it.md' if lingua == 'it' else '-ru.md'
    output_path = output_dir / f"{file_path.stem}{suffisso}"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tradotto)
        print(f"   💾 Salvato: {output_path.name}")
        return True
    except Exception as e:
        print(f"   ❌ Errore salvataggio: {e}")
        return False

def scegli_file(file_lista: List[Path], base_dir: Path) -> Optional[List[Path]]:
    """Menu interattivo per scegliere i file"""
    
    print(f"\n📁 File disponibili in clippings/ ({len(file_lista)}):")
    print("-" * 50)
    for i, f in enumerate(file_lista, 1):
        # Mostra dimensione
        size = f.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024*1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size/(1024*1024):.1f} MB"
        print(f"   {i:2}. {f.name:<35} ({size_str})")
    print("-" * 50)
    print("   0. Esci dallo script")
    
    try:
        scelta = input("\n👉 Scegli file (numero, 'all' o 0): ").strip()
        
        if scelta == '0':
            return None
        
        if scelta.lower() == 'all':
            return file_lista
        else:
            idx = int(scelta) - 1
            if 0 <= idx < len(file_lista):
                return [file_lista[idx]]
            else:
                print(f"❌ Numero non valido (1-{len(file_lista)})")
                return []
    except ValueError:
        print("❌ Scelta non valida")
        return []
    except KeyboardInterrupt:
        print("\n")
        return None

def scegli_lingua() -> Optional[str]:
    """Menu scelta lingua"""
    print("\n🌐 Lingua di destinazione:")
    print("   1. Italiano")
    print("   2. Русский")
    print("   0. Indietro")
    
    choice = input("\n👉 Scegli (1-2 o 0): ").strip()
    
    if choice == '0':
        return None
    elif choice == '1':
        return 'it'
    elif choice == '2':
        return 'ru'
    else:
        print("❌ Scelta non valida")
        return None

def main():
    print("=" * 60)
    print("📖 TRADUTTORE MARKDOWN con DEEPSEEK")
    print("=" * 60)
    
    # Trova base directory
    base_dir = trova_base_dir()
    if not base_dir:
        print("\n❌ llm-Socrates non trovata")
        print("   Struttura attesa:")
        print("   llm-Socrates/")
        print("   ├── asset/")
        print("   ├── clippings/")
        print("   └── vault/raw/")
        return
    
    print(f"\n📂 Base directory: {base_dir}")
    
    # Output directory
    output_dir = base_dir / "vault" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Loop principale per traduzioni multiple
    traduzioni_effettuate = 0
    totale_traduzioni = 0
    
    while True:
        # Trova file disponibili
        file_lista = trova_file_markdown(base_dir)
        
        if not file_lista:
            print("\n❌ Nessun file .md da tradurre in clippings/")
            if traduzioni_effettuate > 0:
                print(f"\n📊 Riepilogo sessione: {traduzioni_effettuate} traduzioni completate")
            break
        
        # Scegli file
        file_selezionati = scegli_file(file_lista, base_dir)
        
        if file_selezionati is None:
            # Utente ha scelto 0 - esci
            break
        
        if not file_selezionati:
            # Scelta non valida, ricomincia il loop
            continue
        
        # Scegli lingua
        lingua = scegli_lingua()
        if lingua is None:
            # Indietro
            continue
        
        # Riepilogo
        print(f"\n📊 Riepilogo:")
        print(f"   File: {len(file_selezionati)}")
        print(f"   Lingua: {'Italiano' if lingua == 'it' else 'Russo'}")
        print(f"   Output: {output_dir}")
        
        conferma = input("\n👉 Procedere? (s/n): ").lower()
        if conferma != 's':
            print("   Annullato")
            continue
        
        # Traduci
        print(f"\n🚀 Avvio traduzione...")
        successi = 0
        
        for i, file in enumerate(file_selezionati, 1):
            print(f"\n📌 [{i}/{len(file_selezionati)}]")
            if traduci_file(file, output_dir, lingua):
                successi += 1
                traduzioni_effettuate += 1
                totale_traduzioni += 1
            if i < len(file_selezionati):
                time.sleep(1)
        
        print(f"\n✅ Completati: {successi}/{len(file_selezionati)}")
        
        # Chiedi se continuare
        print("\n" + "=" * 40)
        continua = input("📌 Tradurre un altro file? (s/n): ").lower()
        if continua != 's':
            break
    
    # Riepilogo finale
    if traduzioni_effettuate > 0:
        print("\n" + "=" * 60)
        print("📊 SESSIONE COMPLETATA")
        print("=" * 60)
        print(f"   ✅ Traduzioni effettuate: {traduzioni_effettuate}")
        print(f"   📂 Output: {output_dir}")
        print("=" * 60)
    
    print("\n👋 Arrivederci!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrotto dall'utente")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        sys.exit(1)