import os
import re

CONFIG_DIR = os.getenv("CONFIG_DIR", "config")
BLACKLIST_EXT = {'.exe', '.bin', '.so', '.o', '.a', '.sh', '.py', '.bashrc'}

def load_lines(filename):
    try:
        with open(os.path.join(CONFIG_DIR, filename), "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[⚠️] Fichier {filename} introuvable.")
        return []

def load_extensions():
    return {ext.lower() for ext in load_lines("extensions.txt")}

def load_keywords():
    return {kw.lower() for kw in load_lines("keywords.txt")}

def load_user_rules():
    exact_paths = set()
    regex_rules = []

    for line in load_lines("user_rules.txt"):
        if line in BLACKLIST_EXT:
            continue
        if line.startswith("regex:"):
            try:
                regex = re.compile(line[6:])
                regex_rules.append(regex)
            except re.error as e:
                print(f"[❌] Regex invalide : {line[6:]} ({e})")
        else:
            exact_paths.add(os.path.normpath(line))

    return exact_paths, regex_rules

def should_copy_file(filepath, extensions, keywords, exact_paths, regex_rules):
    if os.path.normpath(filepath) in exact_paths:
        return True

    ext = os.path.splitext(filepath)
    if ext.lower() in extensions:
        return True

    filename = os.path.basename(filepath).lower()
    if any(keyword in filename for keyword in keywords):
        return True

    return any(regex.search(filepath) for regex in regex_rules)
