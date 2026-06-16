#!/usr/bin/env python3
"""
Traduttore di file markdown - Supporta DeepSeek Ufficiale e SiliconFlow
Cerca file SOLO in llm-Socrates/clippings/
Traduce in ITALIANO o RUSSO
Salva in vault/raw/
"""

import os
import sys
import time
import re
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from openai import OpenAI
except ImportError:
    print("❌ openai non installata. Esegui: pip install openai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️ python-dotenv non installato. Esegui: pip install python-dotenv")
    sys.exit(1)

# ============================================================
# CARICAMENTO CONFIGURAZIONE
# ============================================================

def carica_api_keys():
    """Carica le API keys da .env"""
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
    
    return {
        "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
        "siliconflow": os.environ.get("SILICONFLOW_API_KEY")
    }

API_KEYS = carica_api_keys()

# ============================================================
# DEFINIZIONE PROVIDER E MODELLI
# ============================================================

PROVIDER_CONFIG = {
    "deepseek": {
        "nome": "DeepSeek Ufficiale",
        "base_url": "https://api.deepseek.com",
        "modelli": [
            ("deepseek-chat", "DeepSeek Chat (standard)"),
            ("deepseek-reasoner", "DeepSeek Reasoner (ragionamento)"),
            ("deepseek-v4-pro", "DeepSeek V4 Pro"),
        ]
    },
    "siliconflow": {
        "nome": "SiliconFlow",
        "base_url": "https://api.siliconflow.com/v1",
        "modelli": [
            ("deepseek-ai/DeepSeek-V3", "DeepSeek V3"),
            ("deepseek-ai/DeepSeek-R1", "DeepSeek R1 (ragionamento)"),
            ("deepseek-ai/DeepSeek-V2", "DeepSeek V2"),
            ("Qwen/Qwen2.5-72B-Instruct", "Qwen 2.5 72B"),
            ("Qwen/Qwen2.5-32B-Instruct", "Qwen 2.5 32B"),
        ]
    }
}

def scegli_provider_e_modello() -> Tuple[str, str, str]:
    """Menu per scegliere provider e modello"""
    
    print("\n" + "=" * 60)
    print("🔧 SCEGLI PROVIDER E MODELLO PER TRADUZIONE")
    print("=" * 60)
    
    provider_keys = list(PROVIDER_CONFIG.keys())
    print("\n📡 Provider disponibili:")
    for i, key in enumerate(provider_keys, 1):
        config = PROVIDER_CONFIG[key]
        has_key = API_KEYS.get(key) is not None
        status = "✅" if has_key else "❌ (chiave mancante)"
        print(f"   {i}. {config['nome']} - {status}")
    
    print(f"   {len(provider_keys)+1}. Esci")
    
    while True:
        try:
            choice = input("\n👉 Scegli provider (numero): ").strip()
            if choice == str(len(provider_keys)+1):
                return None, None, None
            
            idx = int(choice) - 1
            if 0 <= idx < len(provider_keys):
                provider_key = provider_keys[idx]
                provider_config = PROVIDER_CONFIG[provider_key]
                
                api_key = API_KEYS.get(provider_key)
                if not api_key:
                    print(f"   ❌ Chiave API non trovata per {provider_config['nome']}")
                    print(f"   Aggiungi {provider_key.upper()}_API_KEY nel .env")
                    continue
                
                print(f"\n🤖 Modelli disponibili su {provider_config['nome']}:")
                for i, (model_id, model_name) in enumerate(provider_config['modelli'], 1):
                    print(f"   {i}. {model_name} ({model_id})")
                
                while True:
                    try:
                        model_choice = input("\n👉 Scegli modello (numero): ").strip()
                        idx_model = int(model_choice) - 1
                        if 0 <= idx_model < len(provider_config['modelli']):
                            model_id, model_name = provider_config['modelli'][idx_model]
                            return provider_key, model_id, api_key
                        else:
                            print(f"   ❌ Scelta non valida (1-{len(provider_config['modelli'])})")
                    except ValueError:
                        print("   ❌ Inserisci un numero valido")
            else:
                print(f"   ❌ Scelta non valida (1-{len(provider_keys)})")
        except ValueError:
            print("   ❌ Inserisci un numero valido")
        except KeyboardInterrupt:
            return None, None, None

ASSET_DIR = "asset"

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
        return file_trovati
    
    for file in clippings_dir.glob("*.md"):
        if not any(file.name.endswith(suffix) for suffix in ['_it.md', '_ru.md']):
            file_trovati.append(file)
    
    return sorted(file_trovati)

def correggi_percorsi_immagini(testo: str) -> str:
    """Corregge i percorsi delle immagini"""
    pattern = r'\[!\[\[(.*?)\]\]\]\(https://github\.com/karask/satoshi-paper/blob/master/img/.*?\)'
    testo = re.sub(pattern, f'![\\1]({ASSET_DIR}/\\1)', testo)
    return testo

def traduci_con_deepseek(testo: str, lingua: str, api_key: str, base_url: str, model: str) -> Optional[str]:
    """Traduce usando il provider scelto"""
    
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
            api_key=api_key,
            base_url=base_url
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"Sei un traduttore tecnico. Traduci dall'inglese al {lingua_nome} preservando codice e formattazione."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=32000,
        )
        
        traduzione = response.choices[0].message.content
        
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

def traduci_file(file_path: Path, output_dir: Path, lingua: str, 
                 api_key: str, base_url: str, model: str) -> bool:
    """Traduce un singolo file"""
    
    print(f"\n📄 {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            testo = f.read()
        print(f"   📖 {len(testo)} caratteri")
    except Exception as e:
        print(f"   ❌ Errore lettura: {e}")
        return False
    
    lingua_nome = 'italiano' if lingua == 'it' else 'russo'
    print(f"   🤖 Traduzione EN → {lingua_nome}...")
    
    inizio = time.time()
    tradotto = traduci_con_deepseek(testo, lingua, api_key, base_url, model)
    if not tradotto:
        return False
    
    print(f"   ✅ Completata in {time.time()-inizio:.1f}s")
    
    tradotto = correggi_percorsi_immagini(tradotto)
    
    nome_base = file_path.stem.lower().replace(' ', '_')
    suffisso = '_it.md' if lingua == 'it' else '_ru.md'
    output_path = output_dir / f"{nome_base}{suffisso}"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tradotto)
        print(f"   💾 Salvato: {output_path.name}")
        return True
    except Exception as e:
        print(f"   ❌ Errore salvataggio: {e}")
        return False

def scegli_file(file_lista: List[Path]) -> Optional[List[Path]]:
    """Menu interattivo per scegliere i file"""
    
    print(f"\n📁 File disponibili in clippings/ ({len(file_lista)}):")
    print("-" * 50)
    for i, f in enumerate(file_lista, 1):
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
    print("📖 TRADUTTORE MARKDOWN")
    print("   Supporta: DeepSeek Ufficiale | SiliconFlow")
    print("=" * 60)
    
    provider_key, model_id, api_key = scegli_provider_e_modello()
    if provider_key is None:
        print("\n👋 Arrivederci!")
        return
    
    provider_config = PROVIDER_CONFIG[provider_key]
    base_url = provider_config["base_url"]
    
    print(f"\n✅ Provider: {provider_config['nome']}")
    print(f"✅ Modello: {model_id}")
    
    base_dir = trova_base_dir()
    if not base_dir:
        print("\n❌ llm-Socrates non trovata")
        return
    
    print(f"\n📂 Base directory: {base_dir}")
    
    output_dir = base_dir / "vault" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    traduzioni_effettuate = 0
    
    while True:
        file_lista = trova_file_markdown(base_dir)
        
        if not file_lista:
            print("\n❌ Nessun file .md da tradurre in clippings/")
            if traduzioni_effettuate > 0:
                print(f"\n📊 Riepilogo sessione: {traduzioni_effettuate} traduzioni completate")
            break
        
        file_selezionati = scegli_file(file_lista)
        
        if file_selezionati is None:
            break
        
        if not file_selezionati:
            continue
        
        lingua = scegli_lingua()
        if lingua is None:
            continue
        
        print(f"\n📊 Riepilogo:")
        print(f"   Provider: {provider_config['nome']}")
        print(f"   Modello: {model_id}")
        print(f"   File: {len(file_selezionati)}")
        print(f"   Lingua: {'Italiano' if lingua == 'it' else 'Russo'}")
        print(f"   Output: {output_dir}")
        
        conferma = input("\n👉 Procedere? (s/n): ").lower()
        if conferma != 's':
            print("   Annullato")
            continue
        
        print(f"\n🚀 Avvio traduzione...")
        successi = 0
        
        for i, file in enumerate(file_selezionati, 1):
            print(f"\n📌 [{i}/{len(file_selezionati)}]")
            if traduci_file(file, output_dir, lingua, api_key, base_url, model_id):
                successi += 1
                traduzioni_effettuate += 1
            if i < len(file_selezionati):
                time.sleep(1)
        
        print(f"\n✅ Completati: {successi}/{len(file_selezionati)}")
        
        print("\n" + "=" * 40)
        continua = input("📌 Tradurre un altro file? (s/n): ").lower()
        if continua != 's':
            break
    
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