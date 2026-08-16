import sys
import os
import sqlite3

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src', 'backend'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src', 'database'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src', 'frontend'))

def test_imports():
    print("=== Import Testleri ===\n")
    
    try:
        from llm_manager import llm_sorgu_zinciri_kur
        print("[PASS] Backend import: llm_manager")
    except Exception as e:
        print(f"[FAIL] Backend import: {e}")
        return False
    
    try:
        from chat_db import init_db, create_session, get_sessions, get_messages, add_message
        print("[PASS] Veritabani import: chat_db")
    except Exception as e:
        print(f"[FAIL] Veritabani import: {e}")
        return False
    
    try:
        import app as frontend_app
        print("[PASS] Frontend import: app")
    except Exception as e:
        if "ScriptRunContext" in str(e) or "NoSessionContext" in str(e) or "API key" in str(e):
            print("[PASS] Frontend import: app (Streamlit calisma zamanı hatalari beklenir)")
        else:
            print(f"[FAIL] Frontend import: {e}")
            return False
    
    return True

def test_database_paths():
    print("\n=== Veritabani Yolu Testleri ===\n")
    
    db_path = os.path.normpath(os.path.join(PROJECT_ROOT, 'data', 'eticaret_analiz.db'))
    if os.path.exists(db_path):
        print(f"[PASS] Ana veritabani bulundu: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            print(f"[PASS] Ana veritabani tablolari: {[t[0] for t in tables]}")
        except Exception as e:
            print(f"[FAIL] Ana veritabani erisimi: {e}")
            return False
    else:
        print(f"[FAIL] Ana veritabani bulunamadi: {db_path}")
        return False
    
    chat_db_path = os.path.normpath(os.path.join(PROJECT_ROOT, 'data', 'sohbet_gecmisi.db'))
    if os.path.exists(chat_db_path):
        print(f"[PASS] Sohbet veritabani bulundu: {chat_db_path}")
        try:
            conn = sqlite3.connect(chat_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            print(f"[PASS] Sohbet veritabani tablolari: {[t[0] for t in tables]}")
        except Exception as e:
            print(f"[FAIL] Sohbet veritabani erisimi: {e}")
            return False
    else:
        print(f"[BILGI] Sohbet veritabani bulunamadi (ilk calistirmada olusturulacak): {chat_db_path}")
    
    return True

def test_directory_structure():
    print("\n=== Klasor Yapisi Testleri ===\n")
    
    required_dirs = [
        'src/frontend',
        'src/backend',
        'src/database',
        'src/api',
        'tests',
        'scripts',
        'data',
    ]
    
    for dir_path in required_dirs:
        full_path = os.path.join(PROJECT_ROOT, dir_path)
        if os.path.isdir(full_path):
            print(f"[PASS] Klasor var: {dir_path}")
        else:
            print(f"[FAIL] Klasor eksik: {dir_path}")
            return False
    
    required_files = [
        'src/frontend/app.py',
        'src/backend/llm_manager.py',
        'src/database/chat_db.py',
        'src/database/seeder.py',
        'src/api/main.py',
        'data/eticaret_analiz.db',
    ]
    
    for file_path in required_files:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        if os.path.isfile(full_path):
            print(f"[PASS] Dosya var: {file_path}")
        else:
            print(f"[FAIL] Dosya eksik: {file_path}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Enterprise Yapi Dogrulama Testleri")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_directory_structure()
    all_passed &= test_imports()
    all_passed &= test_database_paths()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("[BASARILI] Tum testler gecti!")
    else:
        print("[BASARISIZ] Bazı testler basarisiz oldu!")
    print("=" * 50)
    
    sys.exit(0 if all_passed else 1)
