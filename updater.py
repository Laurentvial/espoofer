#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Système de mise à jour automatique pour Espoofer
"""

import os
import sys
import json
import urllib.request
import urllib.error
import shutil
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading

try:
    import version
except ImportError:
    # Si version.py n'existe pas, créer une version par défaut
    class version:
        __version__ = "1.0.0"

class Updater:
    """Gère les mises à jour automatiques de l'application"""
    
    def __init__(self, update_url=None, current_version=None):
        """
        Args:
            update_url: URL du fichier JSON contenant les informations de mise à jour
            current_version: Version actuelle de l'application
        """
        self.update_url = update_url or "https://raw.githubusercontent.com/votre-repo/espoofer/main/update_info.json"
        self.current_version = current_version or version.__version__
        self.update_info = None
        
    def check_for_updates(self):
        """Vérifie s'il y a des mises à jour disponibles"""
        try:
            # Télécharger le fichier d'information de mise à jour
            with urllib.request.urlopen(self.update_url, timeout=10) as response:
                self.update_info = json.loads(response.read().decode('utf-8'))
            
            latest_version = self.update_info.get('version', '0.0.0')
            
            # Comparer les versions
            if self._compare_versions(latest_version, self.current_version) > 0:
                return True, latest_version, self.update_info
            else:
                return False, latest_version, None
                
        except urllib.error.URLError as e:
            print(f"Erreur lors de la vérification des mises à jour: {e}")
            return False, None, None
        except json.JSONDecodeError as e:
            print(f"Erreur lors du parsing du fichier de mise à jour: {e}")
            return False, None, None
        except Exception as e:
            print(f"Erreur inattendue: {e}")
            return False, None, None
    
    def _compare_versions(self, v1, v2):
        """Compare deux versions (retourne 1 si v1 > v2, -1 si v1 < v2, 0 si égales)"""
        def version_tuple(v):
            return tuple(map(int, (v.split("."))))
        
        try:
            t1 = version_tuple(v1)
            t2 = version_tuple(v2)
            
            if t1 > t2:
                return 1
            elif t1 < t2:
                return -1
            else:
                return 0
        except:
            # En cas d'erreur, comparer comme des chaînes
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
            else:
                return 0
    
    def download_update(self, progress_callback=None):
        """Télécharge la mise à jour"""
        if not self.update_info:
            raise ValueError("Aucune information de mise à jour disponible")
        
        download_url = self.update_info.get('download_url')
        if not download_url:
            raise ValueError("URL de téléchargement non trouvée dans les informations de mise à jour")
        
        try:
            # Créer un répertoire temporaire
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "update.zip")
            
            # Télécharger le fichier
            def download():
                urllib.request.urlretrieve(download_url, temp_file, reporthook=progress_callback)
            
            download()
            return temp_file
            
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement: {e}")
    
    def install_update(self, update_file_path, backup_dir=None):
        """Installe la mise à jour"""
        try:
            # Créer un backup si nécessaire
            if backup_dir:
                self._create_backup(backup_dir)
            
            # Extraire et installer la mise à jour
            # Note: Cette partie dépend de votre format de distribution (zip, exe, etc.)
            # Pour un exécutable, vous pourriez simplement remplacer le fichier
            # Pour un package, vous devriez extraire le zip
            
            # Exemple pour un exécutable unique
            if sys.platform == "win32":
                exe_name = "espoofer.exe"
            else:
                exe_name = "espoofer"
            
            app_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
            
            # Si c'est un exécutable PyInstaller, on remplace l'exécutable
            if getattr(sys, 'frozen', False):
                # Mode exécutable
                old_exe = sys.executable
                new_exe = os.path.join(tempfile.gettempdir(), exe_name)
                
                # Copier le nouveau fichier
                shutil.copy(update_file_path, new_exe)
                
                # Lancer le script de mise à jour qui remplacera l'ancien
                self._launch_updater_script(old_exe, new_exe)
            else:
                # Mode développement - extraire le zip dans le répertoire actuel
                import zipfile
                with zipfile.ZipFile(update_file_path, 'r') as zip_ref:
                    zip_ref.extractall(app_dir)
            
            return True
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'installation: {e}")
    
    def _create_backup(self, backup_dir):
        """Crée une sauvegarde de l'application actuelle"""
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        app_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
        backup_path = os.path.join(backup_dir, f"backup_{self.current_version}")
        
        if os.path.exists(app_dir):
            shutil.copytree(app_dir, backup_path, dirs_exist_ok=True)
    
    def _launch_updater_script(self, old_exe, new_exe):
        """Lance un script qui remplacera l'ancien exécutable par le nouveau"""
        if sys.platform == "win32":
            script_content = f'''@echo off
timeout /t 2 /nobreak >nul
copy /Y "{new_exe}" "{old_exe}"
start "" "{old_exe}"
del "{new_exe}"
del "%~f0"
'''
            script_path = os.path.join(tempfile.gettempdir(), "update.bat")
            with open(script_path, 'w') as f:
                f.write(script_content)
            os.system(f'start "" "{script_path}"')
        else:
            # Pour Linux/Mac
            script_content = f'''#!/bin/bash
sleep 2
cp "{new_exe}" "{old_exe}"
chmod +x "{old_exe}"
"{old_exe}" &
rm "{new_exe}"
rm "$0"
'''
            script_path = os.path.join(tempfile.gettempdir(), "update.sh")
            with open(script_path, 'w') as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)
            os.system(f'"{script_path}" &')


class UpdateDialog:
    """Interface graphique pour les mises à jour"""
    
    def __init__(self, parent, updater):
        self.parent = parent
        self.updater = updater
        self.dialog = None
        self.progress = None
        
    def show_update_available(self, latest_version, update_info):
        """Affiche une boîte de dialogue pour proposer la mise à jour"""
        changelog = update_info.get('changelog', 'Aucune information disponible')
        download_size = update_info.get('size', 'N/A')
        
        msg = f"""Une nouvelle version est disponible !

Version actuelle: {self.updater.current_version}
Nouvelle version: {latest_version}
Taille: {download_size}

Changements:
{changelog}

Voulez-vous télécharger et installer la mise à jour maintenant ?"""
        
        result = messagebox.askyesno("Mise à jour disponible", msg)
        
        if result:
            self.download_and_install()
    
    def download_and_install(self):
        """Télécharge et installe la mise à jour avec une barre de progression"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Téléchargement de la mise à jour")
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Centrer la fenêtre
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        label = tk.Label(self.dialog, text="Téléchargement en cours...")
        label.pack(pady=10)
        
        self.progress = ttk.Progressbar(self.dialog, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill=tk.X)
        self.progress.start()
        
        status_label = tk.Label(self.dialog, text="")
        status_label.pack(pady=5)
        
        def update_thread():
            try:
                def progress_hook(count, block_size, total_size):
                    if total_size > 0:
                        percent = int(count * block_size * 100 / total_size)
                        self.dialog.after(0, lambda: status_label.config(
                            text=f"Téléchargé: {percent}%"
                        ))
                
                # Télécharger
                status_label.config(text="Téléchargement...")
                update_file = self.updater.download_update(progress_hook)
                
                # Installer
                status_label.config(text="Installation...")
                self.updater.install_update(update_file)
                
                # Succès
                self.dialog.after(0, lambda: self._update_success())
                
            except Exception as e:
                self.dialog.after(0, lambda: self._update_error(str(e)))
        
        thread = threading.Thread(target=update_thread, daemon=True)
        thread.start()
    
    def _update_success(self):
        """Affiche un message de succès"""
        self.progress.stop()
        messagebox.showinfo("Succès", 
                          "La mise à jour a été installée avec succès !\n"
                          "L'application va redémarrer.")
        self.dialog.destroy()
        self.parent.quit()
        # Redémarrer l'application
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    def _update_error(self, error_msg):
        """Affiche un message d'erreur"""
        self.progress.stop()
        messagebox.showerror("Erreur", 
                           f"Une erreur s'est produite lors de la mise à jour:\n{error_msg}")
        self.dialog.destroy()


def check_updates_in_background(parent=None, show_no_update=False):
    """Vérifie les mises à jour en arrière-plan"""
    updater = Updater()
    
    def check():
        has_update, latest_version, update_info = updater.check_for_updates()
        
        if has_update and parent:
            dialog = UpdateDialog(parent, updater)
            parent.after(0, lambda: dialog.show_update_available(latest_version, update_info))
        elif show_no_update and not has_update and parent:
            parent.after(0, lambda: messagebox.showinfo("Mise à jour", 
                                                       f"Vous utilisez la dernière version ({updater.current_version})"))
    
    thread = threading.Thread(target=check, daemon=True)
    thread.start()


if __name__ == "__main__":
    # Test du système de mise à jour
    updater = Updater()
    has_update, latest_version, update_info = updater.check_for_updates()
    
    if has_update:
        print(f"Une mise à jour est disponible: {latest_version}")
        print(f"Changelog: {update_info.get('changelog', 'N/A')}")
    else:
        print(f"Vous utilisez la dernière version ({updater.current_version})")

