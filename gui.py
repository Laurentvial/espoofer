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
        self.root.title("Espoofer - Configuration GUI")
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
        self.mode_var = tk.StringVar(value="s")
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(mode_frame, text="Server (s)", variable=self.mode_var, value="s").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Client (c)", variable=self.mode_var, value="c").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Manual (m)", variable=self.mode_var, value="m").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Case ID
        ttk.Label(main_frame, text="Case ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.case_id_var = tk.StringVar(value=self.current_config.get("case_id", b"").decode("utf-8"))
        case_id_combo = ttk.Combobox(main_frame, textvariable=self.case_id_var, width=40, state="readonly")
        case_ids = list(testcases.test_cases.keys())
        case_id_combo['values'] = case_ids
        case_id_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Attacker Site (pour mode server)
        ttk.Label(main_frame, text="Attacker Site:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.attacker_site_var = tk.StringVar(value=self.current_config.get("attacker_site", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.attacker_site_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Legitimate Site Address
        ttk.Label(main_frame, text="Legitimate Site Address:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.legitimate_site_var = tk.StringVar(value=self.current_config.get("legitimate_site_address", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.legitimate_site_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Victim Address
        ttk.Label(main_frame, text="Victim Address:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.victim_address_var = tk.StringVar(value=self.current_config.get("victim_address", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.victim_address_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Séparateur - Server Mode
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        ttk.Label(main_frame, text="Server Mode Configuration:", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        server_mode = self.current_config.get("server_mode", {})
        ttk.Label(main_frame, text="Receive Mail Server:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.recv_mail_server_var = tk.StringVar(value=server_mode.get("recv_mail_server", ""))
        ttk.Entry(main_frame, textvariable=self.recv_mail_server_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Receive Mail Server Port:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.recv_mail_server_port_var = tk.StringVar(value=str(server_mode.get("recv_mail_server_port", 25)))
        ttk.Entry(main_frame, textvariable=self.recv_mail_server_port_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        self.starttls_var = tk.BooleanVar(value=server_mode.get("starttls", False))
        ttk.Checkbutton(main_frame, text="Enable STARTTLS", variable=self.starttls_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Séparateur - Client Mode
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        ttk.Label(main_frame, text="Client Mode Configuration:", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        client_mode = self.current_config.get("client_mode", {})
        sending_server = client_mode.get("sending_server", ("", 587))
        ttk.Label(main_frame, text="Sending Server:").grid(row=row, column=0, sticky=tk.W, pady=5)
        sending_server_frame = ttk.Frame(main_frame)
        sending_server_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.sending_server_host_var = tk.StringVar(value=sending_server[0] if isinstance(sending_server, tuple) else "")
        self.sending_server_port_var = tk.StringVar(value=str(sending_server[1] if isinstance(sending_server, tuple) else 587))
        ttk.Entry(sending_server_frame, textvariable=self.sending_server_host_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(sending_server_frame, text=":").pack(side=tk.LEFT)
        ttk.Entry(sending_server_frame, textvariable=self.sending_server_port_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        ttk.Label(main_frame, text="Username:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=client_mode.get("username", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.username_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Password:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=client_mode.get("password", b"").decode("utf-8"))
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, width=40, show="*")
        password_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Séparateur - Email Content
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        ttk.Label(main_frame, text="Email Content:", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Subject Header:").grid(row=row, column=0, sticky=tk.W, pady=5)
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
        
        ttk.Label(main_frame, text="To Header:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.to_header_var = tk.StringVar(value=self.current_config.get("to_header", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.to_header_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Body:").grid(row=row, column=0, sticky=tk.W, pady=5)
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
        
        ttk.Label(main_frame, text="Sender Name:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.sender_name_var = tk.StringVar(value=self.current_config.get("sender_name", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.sender_name_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="From Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.from_email_var = tk.StringVar(value=self.current_config.get("from_email", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.from_email_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Reply-To:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.reply_to_var = tk.StringVar(value=self.current_config.get("reply_to", b"").decode("utf-8"))
        ttk.Entry(main_frame, textvariable=self.reply_to_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Raw Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.raw_email_text = scrolledtext.ScrolledText(main_frame, width=40, height=3)
        self.raw_email_text.insert("1.0", self.current_config.get("raw_email", b"").decode("utf-8"))
        self.raw_email_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Zone d'erreurs
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        ttk.Label(main_frame, text="Errors:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        self.error_text = scrolledtext.ScrolledText(main_frame, width=40, height=4, bg="#ffcccc", fg="#cc0000")
        self.error_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Validate", command=self.validate_config).pack(side=tk.LEFT, padx=5)
        self.send_button = ttk.Button(button_frame, text="Send Email", command=self.send_email)
        self.send_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Errors", command=self.clear_errors).pack(side=tk.LEFT, padx=5)
        
        # Zone de log pour les résultats
        row += 1
        ttk.Label(main_frame, text="Log:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        self.log_text = scrolledtext.ScrolledText(main_frame, width=40, height=6, bg="#f0f0f0")
        self.log_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        
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
        case_id = self.case_id_var.get()
        
        # Vérifier le case_id
        if not case_id:
            errors.append("Case ID est requis")
        elif case_id not in testcases.test_cases:
            errors.append(f"Case ID '{case_id}' non trouvé dans testcases")
        else:
            # Vérifier la cohérence mode/case_id
            if mode == 'c' and not case_id.startswith('client_'):
                errors.append("Case ID doit commencer par 'client_' en mode client")
            elif mode == 's' and not case_id.startswith('server_'):
                errors.append("Case ID doit commencer par 'server_' en mode server")
        
        # Vérifier les champs requis selon le mode
        if mode == 's':
            if not self.victim_address_var.get():
                errors.append("Victim Address est requis en mode server")
            if not self.legitimate_site_var.get():
                errors.append("Legitimate Site Address est requis")
            if not self.attacker_site_var.get():
                errors.append("Attacker Site est requis")
        elif mode == 'c':
            if not self.victim_address_var.get():
                errors.append("Victim Address est requis en mode client")
            if not self.legitimate_site_var.get():
                errors.append("Legitimate Site Address est requis")
            if not self.username_var.get():
                errors.append("Username est requis en mode client")
            if not self.password_var.get():
                errors.append("Password est requis en mode client")
            if not self.sending_server_host_var.get():
                errors.append("Sending Server est requis en mode client")
        
        # Vérifier les ports
        try:
            port = int(self.recv_mail_server_port_var.get())
            if port < 1 or port > 65535:
                errors.append("Port du serveur de réception doit être entre 1 et 65535")
        except ValueError:
            errors.append("Port du serveur de réception doit être un nombre")
        
        try:
            port = int(self.sending_server_port_var.get())
            if port < 1 or port > 65535:
                errors.append("Port du serveur d'envoi doit être entre 1 et 65535")
        except ValueError:
            errors.append("Port du serveur d'envoi doit être un nombre")
        
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
            self.log(f"Mode: {config_dict['mode']}")
            self.log(f"Case ID: {config_dict['case_id'].decode('utf-8')}")
            # Debug: afficher le subject_header et to_header
            if config_dict.get('subject_header'):
                subject_debug = config_dict['subject_header'].decode('utf-8', errors='ignore')
                self.log(f"Subject Header: {repr(subject_debug)}")
            else:
                self.log("Subject Header: (vide)")
            if config_dict.get('to_header'):
                to_debug = config_dict['to_header'].decode('utf-8', errors='ignore')
                self.log(f"To Header: {repr(to_debug)}")
            else:
                self.log("To Header: (vide)")
            
            mode = config_dict['mode']
            
            if mode == "s":
                # Mode server
                mail_server = config_dict["server_mode"]['recv_mail_server']
                if not mail_server:
                    self.log("Résolution du serveur mail depuis l'adresse de la victime...")
                    mail_server = get_mail_server_from_email_address(config_dict["victim_address"])
                if not mail_server:
                    error_msg = "Erreur: Impossible de résoudre le serveur mail, veuillez définir recv_mail_server manuellement."
                    self.log(error_msg)
                    self.root.after(0, lambda: self.error_text.insert("1.0", error_msg))
                    self.root.after(0, lambda: messagebox.showerror("Erreur", error_msg))
                    return
                
                mail_server_port = config_dict["server_mode"]['recv_mail_server_port']
                starttls = config_dict['server_mode']['starttls']
                
                self.log(f"Connexion au serveur: {mail_server}:{mail_server_port}")
                
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
                    error_msg = "Erreur: Serveur d'envoi non configuré."
                    self.log(error_msg)
                    self.root.after(0, lambda: self.error_text.insert("1.0", error_msg))
                    self.root.after(0, lambda: messagebox.showerror("Erreur", error_msg))
                    return
                
                self.log(f"Connexion au serveur: {mail_server[0]}:{mail_server[1]}")
                
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
                error_msg = "Mode manuel non supporté dans la GUI. Utilisez la ligne de commande."
                self.log(error_msg)
                self.root.after(0, lambda: messagebox.showwarning("Mode non supporté", error_msg))
                
        except Exception as e:
            import traceback
            error_msg = f"Erreur: {str(e)}\n{traceback.format_exc()}"
            self.log(error_msg)
            self.root.after(0, lambda: self.error_text.insert("1.0", error_msg))
            self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur: {str(e)}"))
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

