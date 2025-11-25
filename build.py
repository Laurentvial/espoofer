#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de build pour créer l'exécutable de l'application
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

try:
    import PyInstaller.__main__
except ImportError:
    print("PyInstaller n'est pas installé. Installation...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    import PyInstaller.__main__

import version

def build_application():
    """Construit l'application avec PyInstaller"""
    
    # Nettoyer les anciens builds
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Créer le fichier .spec si nécessaire
    app_name = "Espoofer"
    main_script = "gui.py"  # Point d'entrée principal avec GUI
    
    # Options PyInstaller
    pyinstaller_args = [
        main_script,
        '--name', app_name,
        '--onefile',  # Créer un seul exécutable
        '--windowed',  # Pas de console (pour GUI)
        '--icon', 'NONE',  # Ajoutez votre icône ici si vous en avez une
        '--add-data', 'common;common',  # Inclure le dossier common
        '--add-data', 'dkim;dkim',  # Inclure le dossier dkim
        '--add-data', 'images;images',  # Inclure les images si nécessaire
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.messagebox',
        '--hidden-import', 'tkinter.scrolledtext',
        '--hidden-import', 'dns',
        '--hidden-import', 'simplejson',
        '--hidden-import', 'colorama',
        '--collect-all', 'tkinter',
        '--clean',
    ]
    
    # Ajouter les fichiers de données nécessaires
    data_files = [
        ('testcases.py', '.'),
        ('config.py', '.'),
        ('exploits_builder.py', '.'),
        ('version.py', '.'),
        ('updater.py', '.'),
    ]
    
    for src, dst in data_files:
        if os.path.exists(src):
            pyinstaller_args.extend(['--add-data', f'{src};{dst}'])
    
    print(f"Construction de {app_name} version {version.__version__}...")
    print(f"Arguments: {' '.join(pyinstaller_args)}")
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print(f"\n✓ Build terminé avec succès!")
        print(f"L'exécutable se trouve dans le dossier 'dist/'")
        
        # Créer un package pour la distribution
        create_distribution_package(app_name, version.__version__)
        
    except Exception as e:
        print(f"\n✗ Erreur lors du build: {e}")
        sys.exit(1)


def create_distribution_package(app_name, version_str):
    """Crée un package de distribution (zip)"""
    import zipfile
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("Le dossier dist/ n'existe pas!")
        return
    
    # Trouver l'exécutable
    if sys.platform == "win32":
        exe_name = f"{app_name}.exe"
    else:
        exe_name = app_name
    
    exe_path = dist_dir / exe_name
    
    if not exe_path.exists():
        print(f"L'exécutable {exe_name} n'a pas été trouvé!")
        return
    
    # Créer le package zip
    zip_name = f"{app_name}_v{version_str}_{sys.platform}.zip"
    zip_path = dist_dir / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(exe_path, exe_name)
        # Ajouter un README si nécessaire
        readme_content = f"""# {app_name} v{version_str}

## Installation
1. Extraire ce fichier zip
2. Exécuter {exe_name}

## Mise à jour
L'application vérifie automatiquement les mises à jour au démarrage.
Vous pouvez également vérifier manuellement depuis le menu.

## Support
Pour plus d'informations, consultez le README.md du projet.
"""
        zipf.writestr("README.txt", readme_content)
    
    print(f"✓ Package créé: {zip_path}")
    
    # Afficher la taille
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  Taille: {size_mb:.2f} MB")


if __name__ == "__main__":
    build_application()

