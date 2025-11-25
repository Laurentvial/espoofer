#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import re

# Import des modules existants
import config
import testcases
from common.common import *
from common.mail_sender import MailSender
from exploits_builder import ExploitsBuilder

# Configuration des couleurs modernes - Thème sombre
MODERN_COLORS = {
    'bg_primary': '#1a1a1a',  # Fond principal très sombre
    'bg_secondary': '#2d2d2d',  # Fond secondaire (cartes)
    'bg_accent': '#3a3a3a',  # Fond accent
    'bg_hover': '#404040',  # Fond au survol
    'primary': '#4a9eff',  # Bleu moderne pour les éléments principaux
    'primary_hover': '#5aaaff',
    'success': '#28a745',  # Vert pour succès
    'danger': '#dc3545',  # Rouge pour erreurs
    'warning': '#ffc107',  # Jaune pour avertissements
    'info': '#17a2b8',  # Cyan pour info
    'text_primary': '#e0e0e0',  # Texte principal clair
    'text_secondary': '#b0b0b0',  # Texte secondaire
    'text_muted': '#808080',  # Texte atténué
    'border': '#404040',  # Bordures
    'shadow': '#00000080',  # Ombres plus prononcées
    'input_bg': '#252525',  # Fond des champs de saisie
    'input_border': '#404040'  # Bordure des champs
}

class EspooferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Espoofer - Interface de Configuration")
        # Taille minimale
        self.root.minsize(1000, 750)
        # Ouvrir en plein écran par défaut
        self.root.state('zoomed')  # Windows
        # Pour Linux, utiliser: self.root.attributes('-zoomed', True)
        
        # Configuration du style moderne
        self.setup_modern_style()
        
        # Configuration pour le redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Variables pour stocker les valeurs
        self.config_vars = {}
        self.errors = []
        self.attachments_list = []  # Liste des pièces jointes
        
        # Charger la configuration actuelle
        self.load_config()
        
        # Créer le menu
        self.create_menu()
        
        # Créer l'interface
        self.create_widgets()
        
    def setup_modern_style(self):
        """Configure un style moderne sombre pour l'interface"""
        style = ttk.Style()
        
        # Essayer d'utiliser un thème moderne
        try:
            style.theme_use('clam')  # Thème plus moderne que 'default'
        except:
            pass
        
        # Configuration des couleurs de fond
        self.root.configure(bg=MODERN_COLORS['bg_primary'])
        
        # Style pour les boutons principaux
        style.configure('Modern.TButton',
                       padding=(15, 8),
                       font=('Segoe UI', 10, 'normal'),
                       background=MODERN_COLORS['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Modern.TButton',
                 background=[('active', MODERN_COLORS['primary_hover']),
                           ('pressed', MODERN_COLORS['primary']),
                           ('!active', MODERN_COLORS['primary'])],
                 foreground=[('active', 'white'),
                           ('!active', 'white')],
                 bordercolor=[('active', MODERN_COLORS['primary']),
                            ('!active', MODERN_COLORS['primary'])])
        
        # Style pour les boutons de succès
        style.configure('Success.TButton',
                       padding=(15, 8),
                       font=('Segoe UI', 10, 'normal'),
                       background=MODERN_COLORS['success'],
                       foreground='white',
                       borderwidth=0)
        style.map('Success.TButton',
                 background=[('active', '#34ce57'),
                           ('pressed', MODERN_COLORS['success']),
                           ('!active', MODERN_COLORS['success'])],
                 foreground=[('active', 'white'),
                           ('!active', 'white')])
        
        # Style pour les boutons de danger
        style.configure('Danger.TButton',
                       padding=(15, 8),
                       font=('Segoe UI', 10, 'normal'),
                       background=MODERN_COLORS['danger'],
                       foreground='white',
                       borderwidth=0)
        style.map('Danger.TButton',
                 background=[('active', '#e4606d'),
                           ('pressed', MODERN_COLORS['danger']),
                           ('!active', MODERN_COLORS['danger'])],
                 foreground=[('active', 'white'),
                           ('!active', 'white')])
        
        # Style pour les labels standards
        style.configure('TLabel',
                       font=('Segoe UI', 10),
                       foreground=MODERN_COLORS['text_primary'],
                       background=MODERN_COLORS['bg_primary'])
        
        # Style pour les labels de section
        style.configure('Section.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=MODERN_COLORS['text_primary'],
                       background=MODERN_COLORS['bg_secondary'])
        
        # Style pour les frames de carte
        style.configure('Card.TFrame',
                       background=MODERN_COLORS['bg_secondary'],
                       relief='flat',
                       borderwidth=0)
        
        # Style pour les Entry avec thème sombre
        style.configure('Modern.TEntry',
                       fieldbackground=MODERN_COLORS['input_bg'],
                       foreground=MODERN_COLORS['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       padding=5,
                       insertcolor=MODERN_COLORS['text_primary'])
        style.map('Modern.TEntry',
                 fieldbackground=[('focus', MODERN_COLORS['input_bg']),
                               ('!focus', MODERN_COLORS['input_bg'])],
                 bordercolor=[('focus', MODERN_COLORS['primary']),
                            ('!focus', MODERN_COLORS['input_border'])])
        
        # Style pour les Combobox avec thème sombre
        style.configure('Modern.TCombobox',
                       fieldbackground=MODERN_COLORS['input_bg'],
                       foreground=MODERN_COLORS['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       padding=5,
                       arrowcolor=MODERN_COLORS['text_primary'])
        style.map('Modern.TCombobox',
                 fieldbackground=[('focus', MODERN_COLORS['input_bg']),
                               ('!focus', MODERN_COLORS['input_bg'])],
                 bordercolor=[('focus', MODERN_COLORS['primary']),
                            ('!focus', MODERN_COLORS['input_border'])],
                 arrowcolor=[('active', MODERN_COLORS['primary']),
                           ('!active', MODERN_COLORS['text_primary'])])
        
        # Style pour les RadioButton
        style.configure('Modern.TRadiobutton',
                       font=('Segoe UI', 10),
                       background=MODERN_COLORS['bg_secondary'],
                       foreground=MODERN_COLORS['text_primary'],
                       selectcolor=MODERN_COLORS['bg_secondary'])
        style.map('Modern.TRadiobutton',
                 background=[('active', MODERN_COLORS['bg_secondary']),
                           ('selected', MODERN_COLORS['bg_secondary'])],
                 foreground=[('active', MODERN_COLORS['text_primary']),
                           ('selected', MODERN_COLORS['text_primary'])],
                 indicatorcolor=[('selected', MODERN_COLORS['primary']),
                               ('!selected', MODERN_COLORS['input_border'])])
        
        # Style pour les Checkbutton
        style.configure('Modern.TCheckbutton',
                       font=('Segoe UI', 10),
                       background=MODERN_COLORS['bg_secondary'],
                       foreground=MODERN_COLORS['text_primary'],
                       selectcolor=MODERN_COLORS['bg_secondary'])
        style.map('Modern.TCheckbutton',
                 background=[('active', MODERN_COLORS['bg_secondary']),
                           ('selected', MODERN_COLORS['bg_secondary'])],
                 foreground=[('active', MODERN_COLORS['text_primary']),
                           ('selected', MODERN_COLORS['text_primary'])],
                 indicatorcolor=[('selected', MODERN_COLORS['primary']),
                               ('!selected', MODERN_COLORS['input_border'])])
        
        # Style pour les Scrollbar
        style.configure('TScrollbar',
                       background=MODERN_COLORS['bg_accent'],
                       troughcolor=MODERN_COLORS['bg_primary'],
                       borderwidth=0,
                       arrowcolor=MODERN_COLORS['text_secondary'],
                       darkcolor=MODERN_COLORS['bg_accent'],
                       lightcolor=MODERN_COLORS['bg_accent'])
        style.map('TScrollbar',
                 background=[('active', MODERN_COLORS['primary']),
                           ('!active', MODERN_COLORS['bg_accent'])],
                 arrowcolor=[('active', MODERN_COLORS['text_primary']),
                           ('!active', MODERN_COLORS['text_secondary'])])
        
    def create_menu(self):
        """Crée le menu de l'application"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        # Afficher la version
        try:
            import version
            version_str = version.__version__
        except ImportError:
            version_str = "Inconnue"
        
        help_menu.add_command(label=f"Version {version_str}", state=tk.DISABLED)
        help_menu.add_separator()
        
        # Vérifier les mises à jour
        try:
            from updater import UpdateDialog, Updater
            help_menu.add_command(label="Vérifier les mises à jour", command=self.check_updates)
        except ImportError:
            pass
        
        help_menu.add_separator()
        help_menu.add_command(label="À propos", command=self.show_about)
    
    def check_updates(self):
        """Vérifie manuellement les mises à jour"""
        try:
            from updater import UpdateDialog, Updater
            updater = Updater()
            has_update, latest_version, update_info = updater.check_for_updates()
            
            if has_update:
                dialog = UpdateDialog(self.root, updater)
                dialog.show_update_available(latest_version, update_info)
            else:
                messagebox.showinfo("Mise à jour", 
                                   f"Vous utilisez la dernière version ({updater.current_version})")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de vérifier les mises à jour:\n{e}")
    
    def show_about(self):
        """Affiche la boîte À propos"""
        try:
            import version
            version_str = version.__version__
        except ImportError:
            version_str = "Inconnue"
        
        about_text = f"""Espoofer - Outil de test d'usurpation d'email

Version: {version_str}

Cet outil est destiné à des fins de test et d'éducation uniquement.
Utilisez-le de manière responsable et légale.

© 2024"""
        messagebox.showinfo("À propos", about_text)
        
    def load_config(self):
        """Charge la configuration actuelle depuis config.py"""
        self.current_config = config.config.copy()
        
    def create_widgets(self):
        """Crée l'interface utilisateur"""
        # Créer un Canvas avec Scrollbar pour permettre le défilement
        canvas = tk.Canvas(self.root, bg=MODERN_COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview, style='TScrollbar')
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Mettre à jour la largeur du scrollable_frame quand le canvas change de taille
        def configure_scroll_region(event):
            # Ajuster la largeur du scrollable_frame à la largeur du canvas
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
            # Mettre à jour la région de défilement
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            """Gère le redimensionnement du canvas"""
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        scrollable_frame.bind('<Configure>', configure_scroll_region)
        
        # Frame principal avec padding amélioré et fond moderne
        main_frame = ttk.Frame(scrollable_frame, padding="20", style='Card.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # 2 colonnes principales : gauche pour les champs, droite pour erreurs/logs/boutons
        main_frame.columnconfigure(0, weight=2, minsize=500)  # Colonne gauche (champs)
        main_frame.columnconfigure(1, weight=1, minsize=400)  # Colonne droite (erreurs/logs/boutons)
        # S'assurer que le frame principal s'étire avec le canvas
        scrollable_frame.columnconfigure(0, weight=1)
        
        # Frame pour la colonne gauche (tous les champs)
        left_frame = ttk.Frame(main_frame, style='Card.TFrame')
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)  # Une seule colonne qui s'étire
        
        # Frame pour la colonne droite (erreurs, logs, boutons)
        right_frame = ttk.Frame(main_frame, style='Card.TFrame')
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        
        # Lier la molette de la souris au canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # ========== COLONNE GAUCHE : CHAMPS ==========
        left_row = 0
        
        # Section Mode avec style moderne
        mode_section_frame = ttk.Frame(left_frame, style='Card.TFrame')
        mode_section_frame.grid(row=left_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        mode_section_frame.columnconfigure(1, weight=1)
        
        ttk.Label(mode_section_frame, text="⚙️ Mode:", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(8, 4), padx=10)
        self.mode_var = tk.StringVar(value="c")  # Mode client par défaut
        mode_frame = ttk.Frame(mode_section_frame, style='Card.TFrame')
        mode_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10, padx=(5, 10))
        mode_frame.columnconfigure(0, weight=0)
        mode_frame.columnconfigure(1, weight=0)
        mode_frame.columnconfigure(2, weight=0)
        
        # Style moderne pour les radio buttons
        style = ttk.Style()
        style.configure('Modern.TRadiobutton',
                       font=('Segoe UI', 10),
                       background=MODERN_COLORS['bg_secondary'])
        
        ttk.Radiobutton(mode_frame, text="🖥️ Serveur (s)", variable=self.mode_var, value="s", 
                       command=self.on_mode_change, style='Modern.TRadiobutton').grid(row=0, column=0, padx=8)
        ttk.Radiobutton(mode_frame, text="💻 Client (c)", variable=self.mode_var, value="c", 
                       command=self.on_mode_change, style='Modern.TRadiobutton').grid(row=0, column=1, padx=8)
        ttk.Radiobutton(mode_frame, text="✋ Manuel (m)", variable=self.mode_var, value="m", 
                       command=self.on_mode_change, style='Modern.TRadiobutton').grid(row=0, column=2, padx=8)
        left_row += 1
        
        # Case ID avec descriptions en français - style moderne
        case_section_frame = ttk.Frame(left_frame, style='Card.TFrame')
        case_section_frame.grid(row=left_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        case_section_frame.columnconfigure(0, weight=1)
        
        ttk.Label(case_section_frame, text="📋 ID du Cas", font=('Segoe UI', 10)).grid(row=0, column=0, sticky=tk.W, pady=(8, 4), padx=10)
        self.case_id_var = tk.StringVar(value=self.current_config.get("case_id", b"").decode("utf-8"))
        
        # Mapping des cas vers leurs descriptions en français
        self.case_descriptions_fr = {
            "server_a1": "A1: Sous-domaine inexistant dans MAIL FROM",
            "server_a2": "A2: Adresse MAIL FROM vide",
            "server_a3": "A3: Ambiguïté NUL",
            "server_a4": "A4: Injection de résultats DKIM avec apostrophe",
            "server_a5": "A5: Injection de résultats SPF avec parenthèse",
            "server_a6": "A6: Injection de résultats SPF 2",
            "server_a7": "A7: Adresse de routage dans MAIL FROM",
            "server_a8": "A8: En-têtes From multiples",
            "server_a9": "A9: En-têtes From multiples avec espace précédent",
            "server_a10": "A10: En-têtes From multiples avec espace suivant",
            "server_a11": "A11: En-têtes From multiples avec repli de ligne",
            "server_a12": "A12: Ambiguïté From et Sender",
            "server_a13": "A13: Ambiguïté From et Resent-From",
            "server_a14": "A14: Adresses multiples dans l'en-tête From",
            "server_a15": "A15: Encodage d'adresse email",
            "server_a16": "A16: Portion de routage",
            "server_a17": "A17: Paire entre guillemets",
            "server_a18": "A18: Priorité des caractères spéciaux",
            "server_a19": "A19: Incohérences d'analyse nom d'affichage/adresse",
            "client_a1": "Client A1: Usurpation via plusieurs en-têtes From",
            "client_a2": "Client A2: Usurpation via adresses multiples",
            "client_a3": "Client A3: Usurpation via compte de service email",
        }
        
        # Créer les mappings pour le combobox
        case_ids = list(testcases.test_cases.keys())
        self.case_display_values = [self.case_descriptions_fr.get(case_id, case_id) for case_id in case_ids]
        # Mapping: display_value -> case_id (pour convertir la sélection en ID réel)
        self.display_to_case_id = {self.case_descriptions_fr.get(case_id, case_id): case_id for case_id in case_ids}
        # Mapping: case_id -> display_value (pour convertir l'ID en valeur d'affichage)
        self.case_id_to_display = {case_id: self.case_descriptions_fr.get(case_id, case_id) for case_id in case_ids}
        
        # Trouver la valeur d'affichage pour le cas actuel
        current_case_id = self.current_config.get("case_id", b"").decode("utf-8")
        current_display = self.case_id_to_display.get(current_case_id, current_case_id if current_case_id else "")
        
        self.case_id_combo_var = tk.StringVar(value=current_display)
        self.case_id_combo = ttk.Combobox(case_section_frame, textvariable=self.case_id_combo_var, 
                                          values=self.case_display_values, state="readonly",
                                          style='Modern.TCombobox', font=('Segoe UI', 10))
        self.case_id_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        self.case_id_combo.bind("<<ComboboxSelected>>", self.on_case_selected)
        left_row += 1
        
        # Section Informations générales
        self.general_section_frame = ttk.Frame(left_frame, style='Card.TFrame')
        self.general_section_frame.grid(row=left_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.general_section_frame.columnconfigure(0, weight=1)
        self.general_section_frame.columnconfigure(1, weight=1)
        
        general_title = tk.Label(self.general_section_frame,
                                 text="📝 Informations Générales",
                                 font=("Segoe UI", 13, "bold"),
                                 bg=MODERN_COLORS['bg_secondary'],
                                 fg=MODERN_COLORS['primary'])
        general_title.grid(row=0, column=0, sticky=tk.W, pady=(10, 15), padx=10)
        
        gen_row = 1
        
        # Attacker Site (pour mode server)
        self.attacker_site_label = ttk.Label(self.general_section_frame, text="🎯 Site Attaquant:", font=('Segoe UI', 10))
        self.attacker_site_label.grid(row=gen_row, column=0, sticky=tk.W, pady=(8, 4), padx=10)
        self.attacker_site_var = tk.StringVar(value=self.current_config.get("attacker_site", b"").decode("utf-8"))
        self.attacker_site_entry = ttk.Entry(self.general_section_frame, textvariable=self.attacker_site_var,
                                             style='Modern.TEntry', font=('Segoe UI', 10))
        self.attacker_site_entry.grid(row=gen_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        gen_row += 2
        
        # Legitimate Site Address et Victim Address côte à côte
        ttk.Label(self.general_section_frame, text="✅ Adresse du Site Légitime", font=('Segoe UI', 10)).grid(row=gen_row, column=0, sticky=(tk.W, tk.N), pady=(8, 4), padx=10)
        ttk.Label(self.general_section_frame, text="👤 Adresse de la Victime", font=('Segoe UI', 10)).grid(row=gen_row, column=1, sticky=(tk.W, tk.N), pady=(8, 4), padx=10)
        self.legitimate_site_var = tk.StringVar(value=self.current_config.get("legitimate_site_address", b"").decode("utf-8"))
        ttk.Entry(self.general_section_frame, textvariable=self.legitimate_site_var,
                 style='Modern.TEntry', font=('Segoe UI', 10)).grid(row=gen_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        
        victim_frame = ttk.Frame(self.general_section_frame, style='Card.TFrame')
        victim_frame.grid(row=gen_row+1, column=1, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        victim_frame.columnconfigure(0, weight=1)
        self.victim_address_var = tk.StringVar(value=self.current_config.get("victim_address", b"").decode("utf-8"))
        self.victim_address_var.trace_add("write", self.on_victim_address_change)
        self.victim_address_entry = ttk.Entry(victim_frame, textvariable=self.victim_address_var,
                                             style='Modern.TEntry', font=('Segoe UI', 10))
        self.victim_address_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.victim_address_warning_label = tk.Label(victim_frame, text="", 
                                                     foreground=MODERN_COLORS['warning'], 
                                                     font=("Segoe UI", 8), 
                                                     bg=MODERN_COLORS['bg_secondary'])
        self.victim_address_warning_label.grid(row=1, column=0, sticky=tk.W)
        gen_row += 2
        left_row += 1
        
        # Section Server Mode avec style moderne
        self.server_separator = ttk.Separator(left_frame, orient=tk.HORIZONTAL)
        self.server_separator.grid(row=left_row, column=0, sticky=(tk.W, tk.E), pady=20)
        left_row += 1
        
        self.server_section_frame = ttk.Frame(left_frame, style='Card.TFrame')
        self.server_section_frame.grid(row=left_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.server_section_frame.columnconfigure(0, weight=1)
        
        self.server_mode_label = tk.Label(self.server_section_frame, 
                                          text="🖥️ Configuration Mode Serveur", 
                                          font=("Segoe UI", 13, "bold"),
                                          bg=MODERN_COLORS['bg_secondary'],
                                          fg=MODERN_COLORS['primary'])
        self.server_mode_label.grid(row=0, column=0, sticky=tk.W, pady=(10, 15), padx=10)
        
        server_row = 1
        server_mode = self.current_config.get("server_mode", {})
        self.recv_mail_server_label = ttk.Label(self.server_section_frame, text="📡 Serveur de Réception:", font=('Segoe UI', 10))
        self.recv_mail_server_label.grid(row=server_row, column=0, sticky=tk.W, pady=(8, 4), padx=10)
        self.recv_mail_server_var = tk.StringVar(value=server_mode.get("recv_mail_server", ""))
        self.recv_mail_server_entry = ttk.Entry(self.server_section_frame, textvariable=self.recv_mail_server_var,
                                                style='Modern.TEntry', font=('Segoe UI', 10))
        self.recv_mail_server_entry.grid(row=server_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        server_row += 2
        
        self.recv_mail_server_port_label = ttk.Label(self.server_section_frame, text="🔌 Port:", font=('Segoe UI', 10))
        self.recv_mail_server_port_label.grid(row=server_row, column=0, sticky=tk.W, pady=(8, 4), padx=10)
        self.recv_mail_server_port_var = tk.StringVar(value=str(server_mode.get("recv_mail_server_port", 25)))
        self.recv_mail_server_port_entry = ttk.Entry(self.server_section_frame, textvariable=self.recv_mail_server_port_var,
                                                     style='Modern.TEntry', font=('Segoe UI', 10))
        self.recv_mail_server_port_entry.grid(row=server_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        server_row += 2
        
        self.starttls_var = tk.BooleanVar(value=server_mode.get("starttls", False))
        style.configure('Modern.TCheckbutton',
                       font=('Segoe UI', 10),
                       background=MODERN_COLORS['bg_secondary'])
        self.starttls_checkbutton = ttk.Checkbutton(self.server_section_frame, text="🔒 Activer STARTTLS",
                                                    variable=self.starttls_var, style='Modern.TCheckbutton')
        self.starttls_checkbutton.grid(row=server_row, column=0, sticky=tk.W, pady=(8, 8), padx=10)
        left_row += 1
        
        # Section Client Mode avec style moderne
        self.client_separator = ttk.Separator(left_frame, orient=tk.HORIZONTAL)
        self.client_separator.grid(row=left_row, column=0, sticky=(tk.W, tk.E), pady=20)
        left_row += 1
        
        self.client_section_frame = ttk.Frame(left_frame, style='Card.TFrame')
        self.client_section_frame.grid(row=left_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.client_section_frame.columnconfigure(0, weight=1)
        self.client_section_frame.columnconfigure(1, weight=1)
        
        self.client_mode_label = tk.Label(self.client_section_frame,
                                         text="💻 Configuration Mode Client",
                                         font=("Segoe UI", 13, "bold"),
                                         bg=MODERN_COLORS['bg_secondary'],
                                         fg=MODERN_COLORS['primary'])
        self.client_mode_label.grid(row=0, column=0, sticky=tk.W, pady=(10, 15), padx=10)
        
        client_row = 1
        client_mode = self.current_config.get("client_mode", {})
        sending_server = client_mode.get("sending_server", ("", 587))
        self.sending_server_label = ttk.Label(self.client_section_frame, text="📤 Serveur d'Envoi", font=('Segoe UI', 10))
        self.sending_server_label.grid(row=client_row, column=0, sticky=tk.W, pady=(8, 4), padx=10)
        self.sending_server_frame = ttk.Frame(self.client_section_frame, style='Card.TFrame')
        self.sending_server_frame.grid(row=client_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        self.sending_server_frame.columnconfigure(0, weight=3)
        self.sending_server_frame.columnconfigure(2, weight=1)
        self.sending_server_host_var = tk.StringVar(value=sending_server[0] if isinstance(sending_server, tuple) else "")
        self.sending_server_port_var = tk.StringVar(value=str(sending_server[1] if isinstance(sending_server, tuple) else 587))
        self.sending_server_host_entry = ttk.Entry(self.sending_server_frame, textvariable=self.sending_server_host_var,
                                                   style='Modern.TEntry', font=('Segoe UI', 10))
        self.sending_server_host_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Label(self.sending_server_frame, text=":", font=('Segoe UI', 10), 
                 background=MODERN_COLORS['bg_secondary'],
                 foreground=MODERN_COLORS['text_primary']).grid(row=0, column=1, padx=2)
        self.sending_server_port_entry = ttk.Entry(self.sending_server_frame, textvariable=self.sending_server_port_var,
                                                   style='Modern.TEntry', font=('Segoe UI', 10))
        self.sending_server_port_entry.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(5, 0))
        client_row += 2
        
        # Nom d'utilisateur et Mot de passe côte à côte
        self.username_label = ttk.Label(self.client_section_frame, text="👤 Nom d'utilisateur", font=('Segoe UI', 10))
        self.username_label.grid(row=client_row, column=0, sticky=(tk.W, tk.N), pady=(8, 4), padx=10)
        self.password_label = ttk.Label(self.client_section_frame, text="🔑 Mot de passe", font=('Segoe UI', 10))
        self.password_label.grid(row=client_row, column=1, sticky=(tk.W, tk.N), pady=(8, 4), padx=10)
        
        self.username_var = tk.StringVar(value=client_mode.get("username", b"").decode("utf-8"))
        self.username_entry = ttk.Entry(self.client_section_frame, textvariable=self.username_var,
                                       style='Modern.TEntry', font=('Segoe UI', 10))
        self.username_entry.grid(row=client_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        
        self.password_var = tk.StringVar(value=client_mode.get("password", b"").decode("utf-8"))
        self.password_entry = ttk.Entry(self.client_section_frame, textvariable=self.password_var, show="*",
                                       style='Modern.TEntry', font=('Segoe UI', 10))
        self.password_entry.grid(row=client_row+1, column=1, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        client_row += 2
        left_row += 1
        
        # Section Contenu Email avec style moderne
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).grid(row=left_row, column=0, sticky=(tk.W, tk.E), pady=20)
        left_row += 1
        
        self.email_section_frame = ttk.Frame(left_frame, style='Card.TFrame')
        self.email_section_frame.grid(row=left_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.email_section_frame.columnconfigure(0, weight=1)
        self.email_section_frame.columnconfigure(1, weight=1)
        
        email_title = tk.Label(self.email_section_frame,
                              text="✉️ Contenu de l'Email",
                              font=("Segoe UI", 13, "bold"),
                              bg=MODERN_COLORS['bg_secondary'],
                              fg=MODERN_COLORS['primary'])
        email_title.grid(row=0, column=0, sticky=tk.W, pady=(10, 15), padx=10)
        
        email_row = 1
        
        # En-tête Sujet et En-tête À côte à côte
        ttk.Label(self.email_section_frame, text="📌 En-tête Sujet", font=('Segoe UI', 10)).grid(row=email_row, column=0, sticky=(tk.W, tk.N), pady=(8, 4), padx=10)
        ttk.Label(self.email_section_frame, text="📬 En-tête À", font=('Segoe UI', 10)).grid(row=email_row, column=1, sticky=(tk.W, tk.N), pady=(8, 4), padx=10)
        
        # Extraire juste le texte du sujet (sans "Subject: " et "\r\n")
        subject_raw = self.current_config.get("subject_header", b"").decode("utf-8")
        if subject_raw.startswith("Subject:"):
            subject_text = subject_raw.replace("Subject:", "").strip()
            if subject_text.endswith("\r\n"):
                subject_text = subject_text[:-2]
            elif subject_text.endswith("\n"):
                subject_text = subject_text[:-1]
        else:
            subject_text = subject_raw.strip()
        self.subject_header_var = tk.StringVar(value=subject_text)
        ttk.Entry(self.email_section_frame, textvariable=self.subject_header_var,
                 style='Modern.TEntry', font=('Segoe UI', 10)).grid(row=email_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        
        self.to_header_var = tk.StringVar(value=self.current_config.get("to_header", b"").decode("utf-8"))
        ttk.Entry(self.email_section_frame, textvariable=self.to_header_var,
                 style='Modern.TEntry', font=('Segoe UI', 10)).grid(row=email_row+1, column=1, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        email_row += 2
        
        ttk.Label(self.email_section_frame, text="📄 Corps", font=('Segoe UI', 10)).grid(row=email_row, column=0, columnspan=2, sticky=tk.W, pady=(8, 4), padx=10)
        self.body_text = scrolledtext.ScrolledText(self.email_section_frame, height=6, wrap=tk.WORD,
                                                   font=('Segoe UI', 10),
                                                   bg=MODERN_COLORS['input_bg'],
                                                   fg=MODERN_COLORS['text_primary'],
                                                   insertbackground=MODERN_COLORS['primary'],
                                                   selectbackground=MODERN_COLORS['primary'],
                                                   selectforeground='white',
                                                   relief='solid',
                                                   borderwidth=1,
                                                   highlightthickness=1,
                                                   highlightbackground=MODERN_COLORS['input_border'],
                                                   highlightcolor=MODERN_COLORS['primary'])
        # Nettoyer le body lors du chargement pour enlever les en-têtes
        body_raw = self.current_config.get("body", b"").decode("utf-8")
        # Enlever les en-têtes communs qui pourraient être dans le body
        headers_to_remove = [
            "Date:", "Sender:", "Content-Type:", "MIME-Version:", 
            "Message-ID:", "X-Email-Client:", "From:", "To:", "Subject:"
        ]
        lines = body_raw.split('\n')
        cleaned_lines = []
        in_header_section = False
        for line in lines:
            line_stripped = line.strip()
            is_header = any(line_stripped.startswith(header) for header in headers_to_remove)
            if is_header:
                in_header_section = True
                continue
            if in_header_section and line_stripped == "":
                in_header_section = False
                continue
            if not in_header_section:
                cleaned_lines.append(line)
        body_cleaned = '\n'.join(cleaned_lines).strip()
        # Nettoyer aussi les adresses email collées au début
        body_cleaned = re.sub(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', body_cleaned).strip()
        self.body_text.insert("1.0", body_cleaned)
        self.body_text.grid(row=email_row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        email_row += 2
        # Nom de l'Expéditeur et Email Expéditeur côte à côte
        ttk.Label(self.email_section_frame, text="Nom de l'Expéditeur", font=('Segoe UI', 10)).grid(row=email_row, column=0, sticky=(tk.W, tk.N), pady=(8, 4), padx=10)
        ttk.Label(self.email_section_frame, text="Email Expéditeur", font=('Segoe UI', 10)).grid(row=email_row, column=1, sticky=(tk.W, tk.N), pady=(8, 4), padx=10)
        self.sender_name_var = tk.StringVar(value=self.current_config.get("sender_name", b"").decode("utf-8"))
        ttk.Entry(self.email_section_frame, textvariable=self.sender_name_var, style='Modern.TEntry', font=('Segoe UI', 10)).grid(row=email_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        from_email_frame = ttk.Frame(self.email_section_frame, style='Card.TFrame')
        from_email_frame.grid(row=email_row+1, column=1, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        from_email_frame.columnconfigure(0, weight=1)
        self.from_email_var = tk.StringVar(value=self.current_config.get("from_email", b"").decode("utf-8"))
        self.from_email_var.trace_add("write", self.on_from_email_change)
        self.from_email_entry = ttk.Entry(from_email_frame, textvariable=self.from_email_var, style='Modern.TEntry', font=('Segoe UI', 10))
        self.from_email_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.from_email_warning_label = tk.Label(from_email_frame, text="", 
                                                foreground=MODERN_COLORS['warning'],
                                                font=("Segoe UI", 8), 
                                                bg=MODERN_COLORS['bg_secondary'])
        self.from_email_warning_label.grid(row=1, column=0, sticky=tk.W)
        email_row += 2
        
        ttk.Label(self.email_section_frame, text="Répondre à", font=('Segoe UI', 10)).grid(row=email_row, column=0, columnspan=2, sticky=tk.W, pady=(8, 4), padx=10)
        self.reply_to_var = tk.StringVar(value=self.current_config.get("reply_to", b"").decode("utf-8"))
        ttk.Entry(self.email_section_frame, textvariable=self.reply_to_var, style='Modern.TEntry', font=('Segoe UI', 10)).grid(row=email_row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        email_row += 2
        
        # Pièces jointes avec style moderne
        ttk.Label(self.email_section_frame, text="📎 Pièces jointes", font=('Segoe UI', 10)).grid(row=email_row, column=0, columnspan=2, sticky=tk.W, pady=(8, 4), padx=10)
        attachments_frame = ttk.Frame(self.email_section_frame, style='Card.TFrame')
        attachments_frame.grid(row=email_row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        attachments_frame.columnconfigure(0, weight=1)
        
        # Liste des fichiers joints
        self.attachments_list = []  # Liste des chemins de fichiers
        self.attachments_listbox_frame = ttk.Frame(attachments_frame, style='Card.TFrame')
        self.attachments_listbox_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        self.attachments_listbox_frame.columnconfigure(0, weight=1)
        
        scrollbar_att = ttk.Scrollbar(self.attachments_listbox_frame, style='TScrollbar')
        scrollbar_att.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.attachments_listbox = tk.Listbox(self.attachments_listbox_frame, height=4, yscrollcommand=scrollbar_att.set,
                                             font=('Segoe UI', 9),
                                             bg=MODERN_COLORS['input_bg'],
                                             fg=MODERN_COLORS['text_primary'],
                                             selectbackground=MODERN_COLORS['primary'],
                                             selectforeground='white',
                                             relief='solid',
                                             borderwidth=1,
                                             highlightthickness=1,
                                             highlightbackground=MODERN_COLORS['input_border'],
                                             highlightcolor=MODERN_COLORS['primary'])
        self.attachments_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar_att.config(command=self.attachments_listbox.yview)
        
        # Boutons pour gérer les pièces jointes avec style moderne
        attachments_buttons_frame = ttk.Frame(attachments_frame, style='Card.TFrame')
        attachments_buttons_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        attachments_buttons_frame.columnconfigure(0, weight=1)
        attachments_buttons_frame.columnconfigure(1, weight=1)
        attachments_buttons_frame.columnconfigure(2, weight=1)
        ttk.Button(attachments_buttons_frame, text="➕ Ajouter fichier...", command=self.add_attachment,
                  style='Modern.TButton').grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(attachments_buttons_frame, text="➖ Supprimer", command=self.remove_attachment,
                  style='Danger.TButton').grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(attachments_buttons_frame, text="🗑️ Tout supprimer", command=self.clear_attachments,
                  style='Danger.TButton').grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
        email_row += 2
        
        ttk.Label(self.email_section_frame, text="📧 Email Brut", font=('Segoe UI', 10)).grid(row=email_row, column=0, columnspan=2, sticky=tk.W, pady=(8, 4), padx=10)
        self.raw_email_text = scrolledtext.ScrolledText(self.email_section_frame, height=4, wrap=tk.WORD,
                                                        font=('Segoe UI', 10),
                                                        bg=MODERN_COLORS['input_bg'],
                                                        fg=MODERN_COLORS['text_primary'],
                                                        insertbackground=MODERN_COLORS['primary'],
                                                        selectbackground=MODERN_COLORS['primary'],
                                                        selectforeground='white',
                                                        relief='solid',
                                                        borderwidth=1,
                                                        highlightthickness=1,
                                                        highlightbackground=MODERN_COLORS['input_border'],
                                                        highlightcolor=MODERN_COLORS['primary'])
        self.raw_email_text.insert("1.0", self.current_config.get("raw_email", b"").decode("utf-8"))
        self.raw_email_text.grid(row=email_row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        left_row += 1
        
        # Permettre à la colonne gauche de s'étirer verticalement
        left_frame.rowconfigure(left_row, weight=1)
        
        # ========== COLONNE DROITE : ERREURS, LOGS, BOUTONS ==========
        right_row = 0
        
        # Zone d'erreurs avec style moderne
        error_section_frame = ttk.Frame(right_frame, style='Card.TFrame')
        error_section_frame.grid(row=right_row, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 15))
        error_section_frame.columnconfigure(0, weight=1)
        
        error_title = tk.Label(error_section_frame,
                              text="⚠️ Erreurs",
                              font=("Segoe UI", 12, "bold"),
                              bg=MODERN_COLORS['bg_accent'],
                              fg=MODERN_COLORS['danger'])
        error_title.grid(row=0, column=0, sticky=tk.W, pady=(10, 8), padx=10)
        
        self.error_text = scrolledtext.ScrolledText(error_section_frame, height=6, 
                                                   bg=MODERN_COLORS['bg_accent'], 
                                                   fg=MODERN_COLORS['danger'],
                                                   wrap=tk.WORD, font=("Segoe UI", 9),
                                                   relief='flat', borderwidth=0,
                                                   insertbackground=MODERN_COLORS['danger'],
                                                   selectbackground=MODERN_COLORS['danger'],
                                                   selectforeground='white')
        self.error_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10), padx=10)
        right_row += 1
        
        # Zone d'avertissements et conseils avec style moderne
        tips_section_frame = ttk.Frame(right_frame, style='Card.TFrame')
        tips_section_frame.grid(row=right_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        tips_section_frame.columnconfigure(0, weight=1)
        
        tips_label = tk.Label(tips_section_frame,
                             text="💡 Conseils pour éviter les blocages",
                             font=("Segoe UI", 12, "bold"),
                             bg=MODERN_COLORS['bg_accent'],
                             fg=MODERN_COLORS['warning'])
        tips_label.grid(row=0, column=0, sticky=tk.W, pady=(10, 8), padx=10)
        
        tips_text = """• Évitez d'usurper des domaines avec DMARC strict (gmail.com, yahoo.com, outlook.com, etc.)
• Utilisez un domaine que vous contrôlez ou qui n'a pas de politique DMARC stricte
• En mode client, utilisez un serveur SMTP légitime avec authentification
• Les emails vers Gmail sont souvent filtrés - vérifiez le dossier spam
• Testez avec différents cas de test (A1-A19) pour contourner certaines protections"""
        self.tips_text_widget = scrolledtext.ScrolledText(tips_section_frame, height=5, 
                                                          bg=MODERN_COLORS['bg_accent'], 
                                                          fg=MODERN_COLORS['text_primary'],
                                                          wrap=tk.WORD, font=("Segoe UI", 9),
                                                          relief='flat', borderwidth=0,
                                                          insertbackground=MODERN_COLORS['warning'],
                                                          selectbackground=MODERN_COLORS['warning'],
                                                          selectforeground=MODERN_COLORS['bg_primary'])
        self.tips_text_widget.insert("1.0", tips_text)
        self.tips_text_widget.config(state=tk.DISABLED)  # Lecture seule
        self.tips_text_widget.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10), padx=10)
        right_row += 1
        
        # Boutons avec style moderne
        button_frame = ttk.Frame(right_frame, style='Card.TFrame')
        button_frame.grid(row=right_row, column=0, pady=(0, 15), sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        
        buttons_inner_frame = ttk.Frame(button_frame, style='Card.TFrame')
        buttons_inner_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10)
        buttons_inner_frame.columnconfigure(0, weight=1)
        buttons_inner_frame.columnconfigure(1, weight=1)
        
        ttk.Button(buttons_inner_frame, text="✓ Valider", command=self.validate_config, 
                  style='Success.TButton').grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        self.send_button = ttk.Button(buttons_inner_frame, text="📧 Envoyer l'Email", command=self.send_email,
                                      style='Modern.TButton')
        self.send_button.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
        
        buttons_inner_frame2 = ttk.Frame(button_frame, style='Card.TFrame')
        buttons_inner_frame2.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0), padx=10)
        buttons_inner_frame2.columnconfigure(0, weight=1)
        buttons_inner_frame2.columnconfigure(1, weight=1)
        
        ttk.Button(buttons_inner_frame2, text="🗑️ Effacer les Erreurs", command=self.clear_errors,
                  style='Danger.TButton').grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(buttons_inner_frame2, text="🗑️ Vider les Logs", command=self.clear_logs,
                  style='Danger.TButton').grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
        right_row += 1
        
        # Zone de log pour les résultats avec style moderne
        log_section_frame = ttk.Frame(right_frame, style='Card.TFrame')
        log_section_frame.grid(row=right_row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_section_frame.columnconfigure(0, weight=1)
        log_section_frame.rowconfigure(1, weight=1)
        
        log_title = tk.Label(log_section_frame,
                            text="📊 Journal",
                            font=("Segoe UI", 12, "bold"),
                            bg=MODERN_COLORS['bg_accent'],
                            fg=MODERN_COLORS['text_primary'])
        log_title.grid(row=0, column=0, sticky=tk.W, pady=(10, 8), padx=10)
        
        self.log_text = scrolledtext.ScrolledText(log_section_frame, height=10, 
                                                  bg=MODERN_COLORS['bg_accent'], 
                                                  wrap=tk.WORD,
                                                  font=("Segoe UI", 9),
                                                  fg=MODERN_COLORS['text_primary'],
                                                  insertbackground=MODERN_COLORS['primary'],
                                                  selectbackground=MODERN_COLORS['primary'],
                                                  selectforeground='white',
                                                  relief='flat',
                                                  borderwidth=0)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10), padx=10)
        # Permettre au log de s'étirer verticalement
        right_frame.rowconfigure(right_row, weight=1)
        main_frame.rowconfigure(0, weight=1)
        scrollable_frame.rowconfigure(0, weight=1)
        
        # Initialiser la visibilité selon le mode par défaut
        self.on_mode_change()
        
        # Initialiser les avertissements pour les champs existants
        self.on_from_email_change()
        self.on_victim_address_change()
        
    def on_case_selected(self, event=None):
        """Met à jour le case_id interne quand une description est sélectionnée"""
        display_value = self.case_id_combo_var.get()
        if display_value in self.display_to_case_id:
            actual_case_id = self.display_to_case_id[display_value]
            # Mettre à jour la variable interne (mais pas l'affichage)
            self.case_id_var.set(actual_case_id)
    
    def on_from_email_change(self, *args):
        """Affiche un avertissement si l'email expéditeur utilise un domaine avec DMARC strict"""
        from_email = self.from_email_var.get().strip()
        if from_email:
            domain = self.extract_domain(from_email)
            warning = self.check_dmarc_strict_domain(domain)
            if warning:
                self.from_email_warning_label.config(text=f"⚠ {warning}", foreground="orange")
            else:
                self.from_email_warning_label.config(text="")
        else:
            self.from_email_warning_label.config(text="")
    
    def on_victim_address_change(self, *args):
        """Affiche un avertissement si l'adresse victime est Gmail"""
        victim_address = self.victim_address_var.get().strip()
        if victim_address:
            domain = self.extract_domain(victim_address)
            if domain.lower() in ['gmail.com', 'googlemail.com']:
                self.victim_address_warning_label.config(
                    text="⚠ Gmail a des protections DMARC strictes - certains emails peuvent être bloqués", 
                    foreground="orange"
                )
            else:
                self.victim_address_warning_label.config(text="")
        else:
            self.victim_address_warning_label.config(text="")
    
    def extract_domain(self, email):
        """Extrait le domaine d'une adresse email"""
        if '@' in email:
            return email.split('@')[1].strip().lower()
        return ""
    
    def check_dmarc_strict_domain(self, domain):
        """Vérifie si un domaine a des politiques DMARC strictes connues"""
        strict_domains = {
            'gmail.com': 'Gmail bloque les emails spoofés de gmail.com (DMARC p=reject)',
            'googlemail.com': 'Google bloque les emails spoofés de googlemail.com (DMARC p=reject)',
            'yahoo.com': 'Yahoo bloque souvent les emails spoofés (DMARC p=reject)',
            'yahoo.fr': 'Yahoo bloque souvent les emails spoofés (DMARC p=reject)',
            'outlook.com': 'Outlook/Microsoft bloque souvent les emails spoofés (DMARC p=reject)',
            'hotmail.com': 'Hotmail/Microsoft bloque souvent les emails spoofés (DMARC p=reject)',
            'live.com': 'Microsoft bloque souvent les emails spoofés (DMARC p=reject)',
            'msn.com': 'Microsoft bloque souvent les emails spoofés (DMARC p=reject)',
            'aol.com': 'AOL bloque souvent les emails spoofés (DMARC p=reject)',
            'apple.com': 'Apple bloque souvent les emails spoofés (DMARC p=reject)',
            'icloud.com': 'iCloud bloque souvent les emails spoofés (DMARC p=reject)',
            'protonmail.com': 'ProtonMail bloque souvent les emails spoofés (DMARC p=reject)',
            'proton.me': 'ProtonMail bloque souvent les emails spoofés (DMARC p=reject)',
        }
        return strict_domains.get(domain.lower(), None)
    
    def add_attachment(self):
        """Ouvre un dialogue pour sélectionner un fichier à joindre"""
        from tkinter import filedialog
        file_paths = filedialog.askopenfilenames(
            title="Sélectionner des fichiers à joindre",
            filetypes=[
                ("Tous les fichiers", "*.*"),
                ("Documents", "*.pdf;*.doc;*.docx;*.txt"),
                ("Images", "*.jpg;*.jpeg;*.png;*.gif"),
                ("Archives", "*.zip;*.rar;*.7z"),
            ]
        )
        for file_path in file_paths:
            if file_path and file_path not in self.attachments_list:
                self.attachments_list.append(file_path)
                # Afficher seulement le nom du fichier dans la liste
                import os
                filename = os.path.basename(file_path)
                self.attachments_listbox.insert(tk.END, filename)
    
    def remove_attachment(self):
        """Supprime la pièce jointe sélectionnée"""
        selection = self.attachments_listbox.curselection()
        if selection:
            index = selection[0]
            self.attachments_listbox.delete(index)
            self.attachments_list.pop(index)
    
    def clear_attachments(self):
        """Supprime toutes les pièces jointes"""
        self.attachments_listbox.delete(0, tk.END)
        self.attachments_list.clear()
    
    def on_mode_change(self):
        """Met à jour la visibilité des sections selon le mode sélectionné"""
        mode = self.mode_var.get()
        
        # Widgets du mode serveur (utiliser les frames de section stockés)
        server_widgets = [
            self.server_separator,
            self.server_section_frame,
            self.attacker_site_label,
            self.attacker_site_entry,
            self.recv_mail_server_label,
            self.recv_mail_server_entry,
            self.recv_mail_server_port_label,
            self.recv_mail_server_port_entry,
            self.starttls_checkbutton
        ]
        
        # Widgets du mode client
        client_widgets = [
            self.client_separator,
            self.client_section_frame,
            self.sending_server_label,
            self.sending_server_frame,
            self.username_label,
            self.username_entry,
            self.password_label,
            self.password_entry
        ]
        
        if mode == "s":  # Mode serveur
            # Afficher les widgets serveur, masquer les widgets client
            for widget in server_widgets:
                widget.grid()
            for widget in client_widgets:
                widget.grid_remove()
            # Filtrer les cas pour ne montrer que les cas serveur
            server_case_ids = [cid for cid in testcases.test_cases.keys() if cid.startswith('server_')]
            filtered_display_values = [self.case_descriptions_fr.get(cid, cid) for cid in server_case_ids]
            self.case_id_combo['values'] = filtered_display_values
        elif mode == "c":  # Mode client
            # Masquer les widgets serveur, afficher les widgets client
            for widget in server_widgets:
                widget.grid_remove()
            for widget in client_widgets:
                widget.grid()
            # Filtrer les cas pour ne montrer que les cas client
            client_case_ids = [cid for cid in testcases.test_cases.keys() if cid.startswith('client_')]
            filtered_display_values = [self.case_descriptions_fr.get(cid, cid) for cid in client_case_ids]
            self.case_id_combo['values'] = filtered_display_values
        else:  # Mode manuel
            # Afficher tous les widgets
            for widget in server_widgets + client_widgets:
                widget.grid()
            # Afficher tous les cas
            self.case_id_combo['values'] = self.case_display_values
        
        # Réinitialiser la sélection si le cas actuel n'est pas compatible avec le mode
        current_display = self.case_id_combo_var.get()
        if current_display not in self.case_id_combo['values']:
            # Sélectionner le premier cas disponible pour ce mode
            if self.case_id_combo['values']:
                new_display = self.case_id_combo['values'][0]
                self.case_id_combo_var.set(new_display)
                if new_display in self.display_to_case_id:
                    self.case_id_var.set(self.display_to_case_id[new_display])
        
    def clear_errors(self):
        """Efface les erreurs affichées"""
        self.error_text.delete("1.0", tk.END)
        self.errors = []
    
    def clear_logs(self):
        """Vide le journal des logs"""
        self.log_text.delete("1.0", tk.END)
        
    def log(self, message):
        """Ajoute un message au log (thread-safe)"""
        def _log():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        self.root.after(0, _log)
        
    def validate_config(self):
        """Valide la configuration"""
        self.clear_errors()
        errors = []
        
        mode = self.mode_var.get()
        # Récupérer le case_id réel depuis la sélection du combobox
        display_value = self.case_id_combo_var.get()
        if display_value in self.display_to_case_id:
            case_id = self.display_to_case_id[display_value]
            self.case_id_var.set(case_id)
        else:
            case_id = self.case_id_var.get()
        
        # Vérifier le case_id
        if not case_id:
            errors.append("L'ID du cas est requis")
        elif case_id not in testcases.test_cases:
            errors.append(f"L'ID du cas '{case_id}' n'a pas été trouvé dans les cas de test")
        else:
            # Vérifier la cohérence mode/case_id
            if mode == 'c' and not case_id.startswith('client_'):
                errors.append("L'ID du cas doit commencer par 'client_' en mode client")
            elif mode == 's' and not case_id.startswith('server_'):
                errors.append("L'ID du cas doit commencer par 'server_' en mode serveur")
        
        # Vérifier les champs requis selon le mode
        if mode == 's':
            if not self.victim_address_var.get():
                errors.append("L'adresse de la victime est requise en mode serveur")
            if not self.legitimate_site_var.get():
                errors.append("L'adresse du site légitime est requise")
            if not self.attacker_site_var.get():
                errors.append("Le site attaquant est requis")
        elif mode == 'c':
            if not self.victim_address_var.get():
                errors.append("L'adresse de la victime est requise en mode client")
            if not self.legitimate_site_var.get():
                errors.append("L'adresse du site légitime est requise")
            if not self.username_var.get():
                errors.append("Le nom d'utilisateur est requis en mode client")
            if not self.password_var.get():
                errors.append("Le mot de passe est requis en mode client")
            if not self.sending_server_host_var.get():
                errors.append("Le serveur d'envoi est requis en mode client")
        
        # Vérifier les ports
        try:
            port = int(self.recv_mail_server_port_var.get())
            if port < 1 or port > 65535:
                errors.append("Le port du serveur de réception doit être entre 1 et 65535")
        except ValueError:
            errors.append("Le port du serveur de réception doit être un nombre")
        
        try:
            port = int(self.sending_server_port_var.get())
            if port < 1 or port > 65535:
                errors.append("Le port du serveur d'envoi doit être entre 1 et 65535")
        except ValueError:
            errors.append("Le port du serveur d'envoi doit être un nombre")
        
        # Afficher les erreurs
        if errors:
            self.errors = errors
            error_msg = "\n".join(errors)
            self.error_text.insert("1.0", error_msg)
            messagebox.showerror("Erreurs de validation", error_msg)
        else:
            self.error_text.insert("1.0", "✓ Configuration valide!")
            self.error_text.config(bg="#ccffcc", fg="#006600")
            messagebox.showinfo("Validation", "Configuration valide!")
            self.error_text.config(bg="#ffcccc", fg="#cc0000")
        
        return len(errors) == 0
    
    def build_config_dict(self):
        """Construit le dictionnaire de configuration à partir des champs"""
        # Formater le subject_header correctement
        subject_text = self.subject_header_var.get().strip()
        if subject_text:
            # Si le sujet ne commence pas par "Subject: ", l'ajouter
            if not subject_text.startswith("Subject:"):
                subject_header = f"Subject: {subject_text}\r\n".encode("utf-8")
            else:
                # Si ça commence déjà par "Subject:", vérifier qu'il y a \r\n à la fin
                if not subject_text.endswith("\r\n"):
                    subject_header = f"{subject_text}\r\n".encode("utf-8")
                else:
                    subject_header = subject_text.encode("utf-8")
        else:
            subject_header = b""
        
        # Nettoyer le body pour enlever les en-têtes qui ne devraient pas être là
        body_text = self.body_text.get("1.0", tk.END).strip()
        # Enlever les en-têtes communs qui pourraient être dans le body
        headers_to_remove = [
            "Date:", "Sender:", "Content-Type:", "MIME-Version:", 
            "Message-ID:", "X-Email-Client:", "From:", "To:", "Subject:"
        ]
        lines = body_text.split('\n')
        cleaned_lines = []
        in_header_section = False
        for line in lines:
            line_stripped = line.strip()
            # Vérifier si la ligne commence par un en-tête
            is_header = any(line_stripped.startswith(header) for header in headers_to_remove)
            
            if is_header:
                in_header_section = True
                continue
            
            # Si on était dans une section d'en-têtes et qu'on trouve une ligne vide, on peut continuer
            if in_header_section and line_stripped == "":
                in_header_section = False
                continue
            
            # Si on n'est pas dans une section d'en-têtes, ajouter la ligne
            if not in_header_section:
                cleaned_lines.append(line)
        
        body_cleaned = '\n'.join(cleaned_lines).strip()
        # Nettoyer aussi les adresses email qui pourraient être collées au début
        # Si le body commence par une adresse email suivie directement de texte, l'enlever
        body_cleaned = re.sub(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', body_cleaned).strip()
        
        # S'assurer que le body se termine par \r\n
        if body_cleaned and not body_cleaned.endswith("\r\n"):
            body_cleaned = body_cleaned + "\r\n"
        
        # Récupérer le case_id réel depuis la sélection du combobox
        display_value = self.case_id_combo_var.get()
        if display_value in self.display_to_case_id:
            actual_case_id = self.display_to_case_id[display_value]
            self.case_id_var.set(actual_case_id)
        
        config_dict = {
            "attacker_site": self.attacker_site_var.get().encode("utf-8"),
            "legitimate_site_address": self.legitimate_site_var.get().encode("utf-8"),
            "victim_address": self.victim_address_var.get().encode("utf-8"),
            "case_id": self.case_id_var.get().encode("utf-8"),
            "mode": self.mode_var.get(),
            "server_mode": {
                "recv_mail_server": self.recv_mail_server_var.get(),
                "recv_mail_server_port": int(self.recv_mail_server_port_var.get()),
                "starttls": self.starttls_var.get(),
            },
            "client_mode": {
                "sending_server": (self.sending_server_host_var.get(), int(self.sending_server_port_var.get())),
                "username": self.username_var.get().encode("utf-8"),
                "password": self.password_var.get().encode("utf-8"),
            },
            "subject_header": subject_header,
            "to_header": self.to_header_var.get().strip().encode("utf-8") if self.to_header_var.get().strip() else b"",
            "body": body_cleaned.encode("utf-8") if body_cleaned else b"",
            "sender_name": self.sender_name_var.get().encode("utf-8"),
            "from_email": self.from_email_var.get().encode("utf-8"),
            "reply_to": self.reply_to_var.get().strip().encode("utf-8") if self.reply_to_var.get().strip() else b"",
            "raw_email": self.raw_email_text.get("1.0", tk.END).strip().encode("utf-8"),
            "attachments": self.attachments_list.copy(),  # Liste des chemins de fichiers à joindre
        }
        return config_dict
    
    def send_email(self):
        """Envoie l'email avec la configuration actuelle"""
        # Valider d'abord
        if not self.validate_config():
            return
        
        # Désactiver le bouton pendant l'envoi
        self.send_button.config(state="disabled")
        
        # Lancer l'envoi dans un thread séparé
        thread = threading.Thread(target=self._send_email_thread)
        thread.daemon = True
        thread.start()
    
    def _send_email_thread(self):
        """Thread pour l'envoi d'email"""
        # Construire la configuration
        config_dict = self.build_config_dict()
        
        # Mettre à jour la config globale temporairement
        original_config = config.config.copy()
        config.config.update(config_dict)
        
        try:
            self.log("Démarrage de l'envoi d'email...")
            self.log(f"Mode : {config_dict['mode']}")
            self.log(f"ID du Cas : {config_dict['case_id'].decode('utf-8')}")
            # Debug: afficher le subject_header et to_header
            if config_dict.get('subject_header'):
                subject_debug = config_dict['subject_header'].decode('utf-8', errors='ignore')
                self.log(f"En-tête Sujet : {repr(subject_debug)}")
            else:
                self.log("En-tête Sujet : (vide)")
            if config_dict.get('to_header'):
                to_debug = config_dict['to_header'].decode('utf-8', errors='ignore')
                self.log(f"En-tête À : {repr(to_debug)}")
            else:
                self.log("En-tête À : (vide)")
            
            mode = config_dict['mode']
            
            if mode == "s":
                # Mode server
                mail_server = config_dict["server_mode"]['recv_mail_server']
                if not mail_server:
                    self.log("Résolution du serveur mail depuis l'adresse de la victime...")
                    mail_server = get_mail_server_from_email_address(config_dict["victim_address"])
                if not mail_server:
                    error_msg = "Erreur : Impossible de résoudre le serveur mail, veuillez définir recv_mail_server manuellement."
                    self.log(error_msg)
                    self.root.after(0, lambda: self.error_text.insert("1.0", error_msg))
                    self.root.after(0, lambda: messagebox.showerror("Erreur", error_msg))
                    return
                
                mail_server_port = config_dict["server_mode"]['recv_mail_server_port']
                starttls = config_dict['server_mode']['starttls']
                
                self.log(f"Connexion au serveur : {mail_server}:{mail_server_port}")
                
                exploits_builder = ExploitsBuilder(testcases.test_cases, config_dict)
                smtp_seqs = exploits_builder.generate_smtp_seqs()
                
                msg_content = config_dict["raw_email"] if config_dict["raw_email"] else smtp_seqs["msg_content"]
                
                mail_sender = MailSender()
                mail_sender.set_param(
                    (mail_server, mail_server_port),
                    helo=smtp_seqs["helo"],
                    mail_from=smtp_seqs["mailfrom"],
                    rcpt_to=smtp_seqs["rcptto"],
                    email_data=msg_content,
                    starttls=starttls
                )
                
                # Rediriger la sortie vers le log
                import io
                
                class LogCapture:
                    def __init__(self, gui_app):
                        self.gui_app = gui_app
                        self.buffer = ""
                    
                    def write(self, text):
                        self.buffer += text
                        self.gui_app.log(text.rstrip('\n'))
                    
                    def flush(self):
                        pass
                
                old_stdout = sys.stdout
                log_capture = LogCapture(self)
                sys.stdout = log_capture
                
                try:
                    mail_sender.send_email()
                    self.log("✓ Email envoyé avec succès!")
                    self.root.after(0, lambda: messagebox.showinfo("Succès", "Email envoyé avec succès!"))
                except Exception as e:
                    error_msg = f"Erreur lors de l'envoi: {str(e)}"
                    self.log(error_msg)
                    self.root.after(0, lambda: self.error_text.insert("1.0", error_msg))
                    self.root.after(0, lambda: messagebox.showerror("Erreur", error_msg))
                finally:
                    sys.stdout = old_stdout
                    
            elif mode == "c":
                # Mode client
                mail_server = config_dict["client_mode"]["sending_server"]
                
                if not mail_server or not mail_server[0]:
                    error_msg = "Erreur : Serveur d'envoi non configuré."
                    self.log(error_msg)
                    self.root.after(0, lambda: self.error_text.insert("1.0", error_msg))
                    self.root.after(0, lambda: messagebox.showerror("Erreur", error_msg))
                    return
                
                self.log(f"Connexion au serveur : {mail_server[0]}:{mail_server[1]}")
                
                exploits_builder = ExploitsBuilder(testcases.test_cases, config_dict)
                smtp_seqs = exploits_builder.generate_smtp_seqs()
                
                msg_content = config_dict["raw_email"] if config_dict["raw_email"] else smtp_seqs["msg_content"]
                
                mail_sender = MailSender()
                auth_proto = config_dict["client_mode"].get("auth_proto", "LOGIN")
                mail_sender.set_param(
                    mail_server,
                    helo=b"espoofer-MacBook-Pro.local",
                    mail_from=smtp_seqs['mailfrom'],
                    rcpt_to=smtp_seqs["rcptto"],
                    email_data=msg_content,
                    starttls=True,
                    mode="client",
                    username=config_dict["client_mode"]['username'],
                    password=config_dict["client_mode"]['password'],
                    auth_proto=auth_proto
                )
                
                # Rediriger la sortie vers le log
                import io
                
                class LogCapture:
                    def __init__(self, gui_app):
                        self.gui_app = gui_app
                        self.buffer = ""
                    
                    def write(self, text):
                        self.buffer += text
                        self.gui_app.log(text.rstrip('\n'))
                    
                    def flush(self):
                        pass
                
                old_stdout = sys.stdout
                log_capture = LogCapture(self)
                sys.stdout = log_capture
                
                try:
                    mail_sender.send_email()
                    self.log("✓ Email envoyé avec succès!")
                    self.root.after(0, lambda: messagebox.showinfo("Succès", "Email envoyé avec succès!"))
                except Exception as e:
                    error_msg = f"Erreur lors de l'envoi: {str(e)}"
                    self.log(error_msg)
                    self.root.after(0, lambda: self.error_text.insert("1.0", error_msg))
                    self.root.after(0, lambda: messagebox.showerror("Erreur", error_msg))
                finally:
                    sys.stdout = old_stdout
            else:
                error_msg = "Le mode manuel n'est pas supporté dans l'interface graphique. Utilisez la ligne de commande."
                self.log(error_msg)
                self.root.after(0, lambda: messagebox.showwarning("Mode non supporté", error_msg))
                
        except Exception as e:
            import traceback
            error_msg = f"Erreur : {str(e)}\n{traceback.format_exc()}"
            self.log(error_msg)
            self.root.after(0, lambda: self.error_text.insert("1.0", error_msg))
            self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur : {str(e)}"))
        finally:
            # Restaurer la config originale
            config.config = original_config
            # Réactiver le bouton (thread-safe)
            self.root.after(0, lambda: self.send_button.config(state="normal"))

def main():
    root = tk.Tk()
    app = EspooferGUI(root)
    
    # Vérifier les mises à jour au démarrage (en arrière-plan)
    try:
        from updater import check_updates_in_background
        check_updates_in_background(root, show_no_update=False)
    except ImportError:
        # Si le module updater n'est pas disponible, continuer sans vérification
        pass
    
    root.mainloop()

if __name__ == '__main__':
    main()

