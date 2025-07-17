import os
import shutil
import secrets
from config_loader import load_extensions, load_keywords, load_user_rules, should_copy_file
from database import insert_lure_in_db

def generate_signature():
    return secrets.token_hex(8)

def duplicate_files(file_paths):
    extensions = load_extensions()
    keywords = load_keywords()
    exact_paths, regex_rules = load_user_rules()

    for original_path in file_paths:
        if not os.path.isfile(original_path):
            print(f"[⚠️] Fichier introuvable : {original_path}")
            continue

        if not should_copy_file(original_path, extensions, keywords, exact_paths, regex_rules):
            print(f"[⛔️] Fichier ignoré (ne correspond pas aux règles) : {original_path}")
            continue

        dir_path, filename = os.path.split(original_path)
        name, ext = os.path.splitext(filename)
        copy_filename = f"{name}_copie{ext}"
        copy_path = os.path.join(dir_path, copy_filename)

        if os.path.exists(copy_path):
            print(f"[⏩] Copie déjà existante : {copy_path}")
            continue

        try:
            shutil.copy2(original_path, copy_path)
            os.chmod(copy_path, 0o600)
            os.chown(copy_path, 0, 0)
            signature = generate_signature()
            insert_lure_in_db(filename, signature, original_path, copy_path)
            print(f"[✅] Copie créée : {copy_path} — Signature : {signature}")
        except PermissionError:
            print(f"[❌] Permissions insuffisantes pour sécuriser le fichier : {copy_path}")
        except Exception as e:
            print(f"[❌] Erreur lors de la copie de {original_path} : {e}")

def collect_all_files():
    root = os.getenv("ROOT_DIR", "~")
    all_files = []
    for dirpath, _, filenames in os.walk(root):
        for file in filenames:
            full_path = os.path.join(dirpath, file)
            all_files.append(full_path)
    return all_files

def create_lures():
    try:
        files = collect_all_files()
        if not files:
            print("[⚠️] Aucun fichier trouvé à dupliquer.")
            return
        duplicate_files(files)
    except FileNotFoundError as e:
        print(f"[❌] Fichier introuvable : {e}")
    except PermissionError as e:
        print(f"[🔒] Permission refusée : {e}")
    except Exception as e:
        print(f"[🚨] Erreur inattendue pendant la création des leurres : {e}")