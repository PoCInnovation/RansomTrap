#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dummy Filer GUI — generate & distribute fake (non-sensitive) files across folders.

• Cross‑platform (Windows/macOS/Linux). Only needs Python 3.
• No external packages required; uses tkinter for a simple GUI.
• Creates many files with chosen extensions and sizes, and spreads them across folders.
• You can either:
    - Create N new subfolders under a chosen root, or
    - Use the existing subfolders under that root.
• File contents:
    - For .txt/.csv: optional human‑readable placeholder content.
    - For other types (.pdf/.jpg/.docx/.xlsx/.json/.log): random bytes with a minimal header when useful.

Usage (GUI):
    python dummy_filer_gui.py
"""

import os
import sys
import random
import string
import datetime
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "Dummy Filer GUI"
VERSION = "1.0"

DEFAULT_EXTS = [".txt", ".csv", ".pdf", ".jpg", ".json", ".log"]  # simple defaults that don't need extra libs

TYPICAL_NAMES = [
    # finance
    "Releve_Bancaire_{ym}.pdf", "Facture_{company}_{ymd}.pdf", "Budget_{year}.xlsx",
    "Notes_de_frais_{ym}.csv", "RIB_{company}.pdf",
    # HR / CV
    "CV_{name}.pdf", "Lettre_Motivation_{company}.pdf", "Contrat_{company}_{ym}.pdf",
    # admin
    "Attestation_domicile_{ym}.pdf", "Assurance_Habitation_{year}.pdf",
    # misc/docs
    "Notes_cours_{topic}_{ymd}.txt", "Projet_{topic}_{ym}.docx", "Presentation_{topic}_{ym}.pptx",
    # media
    "IMG_{ymd}_{rand}.jpg",
]

TYPICAL_FOLDERS = [
    "Documents", "Documents/Administratif", "Documents/Comptes",
    "Travail", "Travail/Projets", "Ecole/Cours", "Ecole/Notes",
    "Photos/Vacances", "Photos/Evenements", "Téléchargements", "Bureau"
]

COMPANIES = ["EDF", "SFR", "Free", "ENGIE", "AXA", "CPAM", "URSSAF", "Orange", "SNCF", "Decathlon", "Carrefour"]
TOPICS = ["Microeconomie", "Marketing", "Contrat", "Juridique", "Finance", "Data", "ProjetA", "ProjetB"]
NAMES = ["JeanDupont", "MarieDurand", "PaulMartin", "SophieLeroy", "AlexMoreau"]

def rand_token(n=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

def fmt_name(pattern: str):
    now = datetime.datetime.now()
    subs = {
        "ym": now.strftime("%Y-%m"),
        "ymd": now.strftime("%Y-%m-%d"),
        "year": now.strftime("%Y"),
        "rand": rand_token(6),
        "company": random.choice(COMPANIES),
        "topic": random.choice(TOPICS),
        "name": random.choice(NAMES),
    }
    out = pattern
    for k, v in subs.items():
        out = out.replace("{"+k+"}", v)
    return out

def safe_write_bytes(path: Path, size_bytes: int, human_text: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = path.suffix.lower()
    try:
        if ext in [".txt", ".log"] and human_text:
            lorem = (
                "Ce document est un faux fichier de test généré automatiquement.\n"
                "Il ne contient aucune donnée personnelle ou sensible.\n\n"
            )
            # Fill roughly to size by repeating lines.
            while len(lorem.encode("utf-8")) < size_bytes:
                lorem += f"- Ligne de test {rand_token()} {datetime.datetime.now().isoformat()}\n"
            data = lorem.encode("utf-8")[:size_bytes]
            with open(path, "wb") as f:
                f.write(data)
        elif ext == ".csv" and human_text:
            header = "date,libelle,montant,categorie\n"
            rows = []
            while len(header.encode("utf-8")) + sum(len(r.encode("utf-8")) for r in rows) < size_bytes:
                rows.append(f"{datetime.date.today().isoformat()},Transaction {rand_token()},"
                            f"{random.uniform(-150, 150):.2f},"
                            f"{random.choice(['Frais','Salaire','Courses','Loisirs'])}\n")
            data = (header + "".join(rows)).encode("utf-8")[:size_bytes]
            with open(path, "wb") as f:
                f.write(data)
        elif ext == ".json" and human_text:
            items = []
            while True:
                items.append({
                    "id": rand_token(8),
                    "name": random.choice(NAMES),
                    "company": random.choice(COMPANIES),
                    "amount": round(random.uniform(10, 999), 2),
                    "created_at": datetime.datetime.now().isoformat(),
                })
                blob = json.dumps(items, ensure_ascii=False, indent=2)
                if len(blob.encode("utf-8")) >= size_bytes:
                    break
            with open(path, "wb") as f:
                f.write(blob.encode("utf-8")[:size_bytes])
        else:
            # For binary-like types: write minimal header then random bytes.
            header = b""
            if ext == ".pdf":
                header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
            elif ext == ".jpg" or ext == ".jpeg":
                header = b"\xFF\xD8\xFF\xE0" + b"JFIF\x00\x01\x02\x00\x00\x01\x00\x01\x00\x00"
            # Minimal size safety
            size_bytes = max(size_bytes, len(header) + 32)
            payload = os.urandom(size_bytes - len(header))
            with open(path, "wb") as f:
                f.write(header + payload)
    except Exception as e:
        raise e

def pick_extension(exts):
    return random.choice(exts)

def ensure_subfolders(root: Path, count: int) -> list[Path]:
    if count <= 0:
        # Use existing subfolders (1-level deep). If none, create a default set.
        subs = [p for p in root.rglob("*") if p.is_dir()]
        if not subs:
            subs = [root / f for f in TYPICAL_FOLDERS]
    else:
        subs = []
        for i in range(count):
            sub = root / random.choice(TYPICAL_FOLDERS) / rand_token(3)
            subs.append(sub)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for s in subs:
        if str(s) not in seen:
            seen.add(str(s))
            unique.append(s)
    # Make sure they exist
    for s in unique:
        s.mkdir(parents=True, exist_ok=True)
    return unique

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{VERSION}")
        self.minsize(640, 480)

        self.root_dir = tk.StringVar(value=str(Path.home()))
        self.total_files = tk.IntVar(value=100)
        self.new_folders = tk.IntVar(value=10)
        self.use_existing = tk.BooleanVar(value=False)

        self.size_min_kb = tk.IntVar(value=10)
        self.size_max_kb = tk.IntVar(value=200)

        self.human_text = tk.BooleanVar(value=True)

        # extension checkboxes
        self.ext_vars = {}
        for ext in DEFAULT_EXTS:
            self.ext_vars[ext] = tk.BooleanVar(value=True)
        self.custom_ext = tk.StringVar(value=".docx,.xlsx,.pptx")  # not "valid" content, but ok as placeholders

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        frm_top = ttk.LabelFrame(self, text="Emplacement")
        frm_top.pack(fill="x", **pad)

        ttk.Label(frm_top, text="Dossier racine :").pack(side="left", padx=8, pady=8)
        ttk.Entry(frm_top, textvariable=self.root_dir, width=55).pack(side="left", padx=4, pady=8)
        ttk.Button(frm_top, text="Parcourir…", command=self.choose_root).pack(side="left", padx=8, pady=8)

        frm_cfg = ttk.LabelFrame(self, text="Configuration")
        frm_cfg.pack(fill="x", **pad)

        row1 = ttk.Frame(frm_cfg); row1.pack(fill="x", pady=4)
        ttk.Label(row1, text="Nombre total de fichiers à créer :").pack(side="left")
        ttk.Spinbox(row1, from_=1, to=100000, textvariable=self.total_files, width=8).pack(side="left", padx=8)

        ttk.Separator(frm_cfg, orient="horizontal").pack(fill="x", pady=4)

        row2 = ttk.Frame(frm_cfg); row2.pack(fill="x", pady=4)
        ttk.Checkbutton(row2, text="Utiliser les sous‑dossiers existants (sinon créer N nouveaux)", variable=self.use_existing).pack(side="left")
        ttk.Label(row2, text="Nouveaux dossiers à créer :").pack(side="left", padx=12)
        ttk.Spinbox(row2, from_=0, to=10000, textvariable=self.new_folders, width=8).pack(side="left")

        ttk.Separator(frm_cfg, orient="horizontal").pack(fill="x", pady=4)

        row3 = ttk.Frame(frm_cfg); row3.pack(fill="x", pady=4)
        ttk.Label(row3, text="Taille min (KB) :").pack(side="left")
        ttk.Spinbox(row3, from_=1, to=1024*1024, textvariable=self.size_min_kb, width=8).pack(side="left", padx=8)
        ttk.Label(row3, text="Taille max (KB) :").pack(side="left")
        ttk.Spinbox(row3, from_=1, to=1024*1024, textvariable=self.size_max_kb, width=8).pack(side="left", padx=8)
        ttk.Checkbutton(row3, text="Contenu lisible pour .txt/.csv/.json", variable=self.human_text).pack(side="left", padx=12)

        frm_ext = ttk.LabelFrame(self, text="Types de fichiers")
        frm_ext.pack(fill="x", **pad)

        row_ext = ttk.Frame(frm_ext); row_ext.pack(fill="x", pady=4)
        for ext, var in self.ext_vars.items():
            ttk.Checkbutton(row_ext, text=ext, variable=var).pack(side="left", padx=6)

        row_cust = ttk.Frame(frm_ext); row_cust.pack(fill="x", pady=4)
        ttk.Label(row_cust, text="Extensions personnalisées (séparées par des virgules) :").pack(side="left")
        ttk.Entry(row_cust, textvariable=self.custom_ext, width=40).pack(side="left", padx=8)

        frm_actions = ttk.Frame(self); frm_actions.pack(fill="x", **pad)
        ttk.Button(frm_actions, text="Générer", command=self.generate).pack(side="left", padx=6)
        ttk.Button(frm_actions, text="Quitter", command=self.destroy).pack(side="left", padx=6)

        self.status = tk.StringVar(value="Prêt.")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def choose_root(self):
        d = filedialog.askdirectory(initialdir=self.root_dir.get(), title="Sélectionner le dossier racine")
        if d:
            self.root_dir.set(d)

    def parse_exts(self):
        selected = [ext for ext, var in self.ext_vars.items() if var.get()]
        # add custom
        extra = [e.strip() for e in self.custom_ext.get().split(",") if e.strip()]
        for e in extra:
            if not e.startswith("."):
                e = "." + e
            selected.append(e)
        # dedupe
        seen = set(); out = []
        for e in selected:
            if e.lower() not in seen:
                seen.add(e.lower())
                out.append(e.lower())
        return out

    def generate(self):
        try:
            root = Path(self.root_dir.get()).expanduser().resolve()
            if not root.exists():
                messagebox.showerror(APP_NAME, f"Le dossier racine n'existe pas:\n{root}")
                return
            n_files = int(self.total_files.get())
            min_kb = int(self.size_min_kb.get())
            max_kb = int(self.size_max_kb.get())
            if min_kb > max_kb:
                messagebox.showerror(APP_NAME, "La taille minimale ne peut pas dépasser la taille maximale.")
                return
            exts = self.parse_exts()
            if not exts:
                messagebox.showerror(APP_NAME, "Veuillez sélectionner au moins une extension.")
                return

            if self.use_existing.get():
                subfolders = ensure_subfolders(root, 0)
            else:
                subfolders = ensure_subfolders(root, int(self.new_folders.get()))

            self.status.set("Création des fichiers…")
            self.update_idletasks()

            for i in range(1, n_files + 1):
                folder = random.choice(subfolders)
                # generate filename
                base = fmt_name(random.choice(TYPICAL_NAMES))
                ext = random.choice(exts)
                name = f"{base}"
                # replace any existing extension with chosen ext if needed
                if Path(name).suffix:
                    name = str(Path(name).with_suffix(ext))
                else:
                    name = name + ext
                file_path = folder / name

                # avoid overwriting: add counter if exists
                counter = 1
                while file_path.exists():
                    stem = file_path.stem
                    file_path = folder / f"{stem}({counter}){ext}"
                    counter += 1

                size = random.randint(min_kb*1024, max_kb*1024)
                safe_write_bytes(file_path, size, human_text=self.human_text.get())

                if i % max(1, n_files // 100) == 0:
                    self.status.set(f"Créé {i}/{n_files} fichiers…")
                    self.update_idletasks()

            self.status.set(f"Terminé : {n_files} fichiers créés dans {len(subfolders)} dossiers.")
            messagebox.showinfo(APP_NAME, f"✅ Terminé !\n\n{n_files} fichiers créés et répartis dans {len(subfolders)} dossiers.\nRacine : {root}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Erreur : {e}")
            self.status.set("Erreur.")

def main():
    # On some platforms, tkinter may be missing. Give a friendly hint.
    try:
        import tkinter  # noqa: F401
    except Exception:
        print("Erreur : tkinter n'est pas disponible. Installez-le ou utilisez une distribution Python qui l'inclut.", file=sys.stderr)
        sys.exit(1)
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
