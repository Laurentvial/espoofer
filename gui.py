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

class EspooferGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Espoofer - Interface de Configuration")
        self.root.geometry("900x800")
        
        # Variables pour stocker les valeurs
        self.config_vars = {}
        self.errors = []
        
        # Charger la configuration actuelle
        self.load_config()
        
        # Créer l'interface
        self.create_widgets()
        
    def load_config(self):
        """Charge la configuration actuelle depuis config.py"""
        self.current_config = config.config.copy()
        
    def create_widgets(self):
        """Crée l'interface utilisateur"""
        # Créer un Canvas avec Scrollbar pour permettre le défilement
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
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
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ajuster la largeur du scrollable_frame à la largeur du canvas
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_scroll_region)
        
        # Frame principal avec padding
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Lier la molette de la souris au canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        row = 0
        
        # Titre
        title_label = ttk.Label(main_frame, text="Configuration Espoofer", font=("Arial", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 20))
        row += 1
        
        # Mode de fonctionnement
        ttk.Label(main_frame, text="Mode:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="c")  # Mode client par défaut
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="Serveur (s)", variable=self.mode_var, value="s", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Client (c)", variable=self.mode_var, value="c", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Manuel (m)", variable=self.mode_var, value="m", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Case ID avec descriptions en français
        ttk.Label(main_frame, text="ID du Cas:").grid(row=row, column=0, sticky=tk.W, pady=5)
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
        self.case_id_combo = ttk.Combobox(main_frame, textvariable=self.case_id_combo_var, 
                                          values=self.case_display_values, width=40, state="readonly")
        self.case_id_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.case_id_combo.bind("<<ComboboxSelected>>", self.on_case_selected)
        row += 1
        
        # Attacker Site (pour mode server)
        self.attacker_site_label = ttk.Label(main_frame, text="Site Attaquant:")
        self.attacker_site_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.attacker_site_var = tk.StringVar(value=self.current_config.get("attacker_site", b"").decode("utf-8"))
        self.attacker_site_entry = ttk.Entry(main_frame, textvariable=self.attacker_site_var, width=40)
        self.attacker_site_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Legitimate Site Address
        ttk.Label(main_frame, text="Adresse du Site Légitime:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.legitimate_site_var = tk.StringVar(value=self.current_config.get("legitimate_site_address", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.legitimate_site_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Victim Address
        ttk.Label(main_frame, text="Adresse de la Victime:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.victim_address_var = tk.StringVar(value=self.current_config.get("victim_address", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.victim_address_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Séparateur - Server Mode
        self.server_separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        self.server_separator.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        self.server_mode_label = ttk.Label(main_frame, text="Configuration Mode Serveur:", font=("Arial", 12, "bold"))
        self.server_mode_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        server_mode = self.current_config.get("server_mode", {})
        self.recv_mail_server_label = ttk.Label(main_frame, text="Serveur de Réception:")
        self.recv_mail_server_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.recv_mail_server_var = tk.StringVar(value=server_mode.get("recv_mail_server", ""))
        self.recv_mail_server_entry = ttk.Entry(main_frame, textvariable=self.recv_mail_server_var, width=40)
        self.recv_mail_server_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        self.recv_mail_server_port_label = ttk.Label(main_frame, text="Port du Serveur de Réception:")
        self.recv_mail_server_port_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.recv_mail_server_port_var = tk.StringVar(value=str(server_mode.get("recv_mail_server_port", 25)))
        self.recv_mail_server_port_entry = ttk.Entry(main_frame, textvariable=self.recv_mail_server_port_var, width=40)
        self.recv_mail_server_port_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        self.starttls_var = tk.BooleanVar(value=server_mode.get("starttls", False))
        self.starttls_checkbutton = ttk.Checkbutton(main_frame, text="Activer STARTTLS", variable=self.starttls_var)
        self.starttls_checkbutton.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Séparateur - Client Mode
        self.client_separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        self.client_separator.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        self.client_mode_label = ttk.Label(main_frame, text="Configuration Mode Client:", font=("Arial", 12, "bold"))
        self.client_mode_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        client_mode = self.current_config.get("client_mode", {})
        sending_server = client_mode.get("sending_server", ("", 587))
        self.sending_server_label = ttk.Label(main_frame, text="Serveur d'Envoi:")
        self.sending_server_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.sending_server_frame = ttk.Frame(main_frame)
        self.sending_server_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.sending_server_host_var = tk.StringVar(value=sending_server[0] if isinstance(sending_server, tuple) else "")
        self.sending_server_port_var = tk.StringVar(value=str(sending_server[1] if isinstance(sending_server, tuple) else 587))
        self.sending_server_host_entry = ttk.Entry(self.sending_server_frame, textvariable=self.sending_server_host_var, width=25)
        self.sending_server_host_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(self.sending_server_frame, text=":").pack(side=tk.LEFT)
        self.sending_server_port_entry = ttk.Entry(self.sending_server_frame, textvariable=self.sending_server_port_var, width=10)
        self.sending_server_port_entry.pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        self.username_label = ttk.Label(main_frame, text="Nom d'utilisateur:")
        self.username_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=client_mode.get("username", b"").decode("utf-8"))
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=40)
        self.username_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        self.password_label = ttk.Label(main_frame, text="Mot de passe:")
        self.password_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=client_mode.get("password", b"").decode("utf-8"))
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, width=40, show="*")
        self.password_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Séparateur - Email Content
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        ttk.Label(main_frame, text="Contenu de l'Email:", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(main_frame, text="En-tête Sujet:").grid(row=row, column=0, sticky=tk.W, pady=5)
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
        ttk.Entry(main_frame, textvariable=self.subject_header_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="En-tête À:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.to_header_var = tk.StringVar(value=self.current_config.get("to_header", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.to_header_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Corps:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.body_text = scrolledtext.ScrolledText(main_frame, width=40, height=5)
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
        self.body_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Nom de l'Expéditeur:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.sender_name_var = tk.StringVar(value=self.current_config.get("sender_name", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.sender_name_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Email Expéditeur:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.from_email_var = tk.StringVar(value=self.current_config.get("from_email", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.from_email_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Répondre à:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.reply_to_var = tk.StringVar(value=self.current_config.get("reply_to", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.reply_to_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Email Brut:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.raw_email_text = scrolledtext.ScrolledText(main_frame, width=40, height=3)
        self.raw_email_text.insert("1.0", self.current_config.get("raw_email", b"").decode("utf-8"))
        self.raw_email_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Zone d'erreurs
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        ttk.Label(main_frame, text="Erreurs:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        self.error_text = scrolledtext.ScrolledText(main_frame, width=40, height=4, bg="#ffcccc", fg="#cc0000")
        self.error_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Valider", command=self.validate_config).pack(side=tk.LEFT, padx=5)
        self.send_button = ttk.Button(button_frame, text="Envoyer l'Email", command=self.send_email)
        self.send_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Effacer les Erreurs", command=self.clear_errors).pack(side=tk.LEFT, padx=5)
        
        # Zone de log pour les résultats
        row += 1
        ttk.Label(main_frame, text="Journal:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        self.log_text = scrolledtext.ScrolledText(main_frame, width=40, height=6, bg="#f0f0f0")
        self.log_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        
        # Initialiser la visibilité selon le mode par défaut
        self.on_mode_change()
        
    def on_case_selected(self, event=None):
        """Met à jour le case_id interne quand une description est sélectionnée"""
        display_value = self.case_id_combo_var.get()
        if display_value in self.display_to_case_id:
            actual_case_id = self.display_to_case_id[display_value]
            # Mettre à jour la variable interne (mais pas l'affichage)
            self.case_id_var.set(actual_case_id)
    
    def on_mode_change(self):
        """Met à jour la visibilité des sections selon le mode sélectionné"""
        mode = self.mode_var.get()
        
        # Widgets du mode serveur
        server_widgets = [
            self.server_separator,
            self.server_mode_label,
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
            self.client_mode_label,
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
    root.mainloop()

if __name__ == '__main__':
    main()

