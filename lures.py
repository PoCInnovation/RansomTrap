import os
import shutil
import secrets
from config_loader import load_extensions, load_keywords, load_user_rules, should_copy_file
from database import insert_lure_in_db, lure_exists

def generate_signature():
    return secrets.token_hex(8)

def duplicate_files(file_paths):
    extensions = load_extensions()
    keywords = load_keywords()
    exact_paths, regex_rules = load_user_rules()

    for original_path in file_paths:
        if not os.path.isfile(original_path):
            print(f"[⚠️] File not found : {original_path}")
            continue

        if not should_copy_file(original_path, extensions, keywords, exact_paths, regex_rules):
            print(f"[⛔️] File ignored (doesn't match the rules) : {original_path}")
            continue

        dir_path, filename = os.path.split(original_path)
        name, ext = os.path.splitext(filename)
        copy_filename = f"{name}_copie{ext}"
        copy_path = os.path.join(dir_path, copy_filename)

        if lure_exists(original_path):
            print(f"[⏩] Déjà présent dans la DB : {copy_path}")
            continue

        try:
            if not os.path.exists(copy_path):
                shutil.copy2(original_path, copy_path)
            else:
                print(f"[⏩] Copy already existing : {copy_path}")

            os.chmod(copy_path, 0o600)
            os.chown(copy_path, 0, 0)
            signature = generate_signature()
            insert_lure_in_db(filename, signature, original_path, copy_path)
            print(f"[✅] Copy created : {copy_path} — Signature : {signature}")
        except PermissionError:
            print(f"[❌] Unauthorized permissions to secure the file : {copy_path}")
        except Exception as e:
            print(f"[❌] Error during the copy of {original_path} : {e}")

def collect_all_files():
    root = os.getenv("ROOT_DIR", "test")
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
            print("[⚠️] No files found to duplicate.")
            return
        duplicate_files(files)
    except FileNotFoundError as e:
        print(f"[❌] File not found : {e}")
    except PermissionError as e:
        print(f"[🔒] Permission refused : {e}")
    except Exception as e:
        print(f"[🚨] Unexpecting error during lures creation : {e}")