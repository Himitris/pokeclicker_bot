import customtkinter as ctk
import time
from pokeclicker_bot_complete import PokeclickerBotComplete

class PokeclickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("PokéClicker Automation")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Création du bot
        self.bot = PokeclickerBotComplete(self.log_message, self.update_status)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Titre
        self.title_label = ctk.CTkLabel(self.main_frame, text="PokéClicker Automation", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(10, 20))
        
        # Onglets
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Création des onglets
        self.tab_view.add("Farming par route")
        self.tab_view.add("Auto Clicker")
        self.tab_view.add("Automatisation de Donjon")
        
        # Configuration de l'onglet Farming par route
        self.setup_farming_tab()
        
        # Configuration de l'onglet Auto Clicker
        self.setup_autoclicker_tab()
        
        # Configuration de l'onglet Automatisation de Donjon
        self.setup_dungeon_tab()
        
        # Frame du journal (en bas)
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)
        
        # Étiquette du journal
        self.log_label = ctk.CTkLabel(self.log_frame, text="Journal d'exécution:", font=ctk.CTkFont(weight="bold"))
        self.log_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        # Zone de texte du journal
        self.log_textbox = ctk.CTkTextbox(self.log_frame, height=200)
        self.log_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Frame de statut (en bas)
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Mode d'apparence
        self.appearance_label = ctk.CTkLabel(self.status_frame, text="Thème:")
        self.appearance_label.grid(row=0, column=0, padx=(10, 10), pady=0, sticky="w")
        
        self.appearance_menu = ctk.CTkOptionMenu(self.status_frame, values=["System", "Light", "Dark"],
                                              command=self.change_appearance)
        self.appearance_menu.grid(row=0, column=1, padx=10, pady=0, sticky="w")
        self.appearance_menu.set("System")
        
        # Statut
        self.status_label = ctk.CTkLabel(self.status_frame, text="Statut: Non connecté", font=ctk.CTkFont(weight="bold"))
        self.status_label.grid(row=0, column=3, padx=10, pady=0, sticky="e")
        
        # Message initial
        self.log_message("Application démarrée.")
        self.log_message("1. Cliquez sur 'Ouvrir PokéClicker' pour lancer le navigateur")
        self.log_message("2. Utilisez les onglets pour accéder aux différentes fonctionnalités:")
        self.log_message("   - Farming par route: chercher un Pokémon spécifique")
        self.log_message("   - Auto Clicker: cliquer automatiquement sur n'importe quel Pokémon")
        self.log_message("   - Automatisation de Donjon: explorer des donjons automatiquement")
    
    def setup_farming_tab(self):
        """Configurer l'onglet de farming par route"""
        tab = self.tab_view.tab("Farming par route")
        tab.grid_columnconfigure(0, weight=1)
        
        # Frame de configuration
        self.farming_config_frame = ctk.CTkFrame(tab)
        self.farming_config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.farming_config_frame.grid_columnconfigure(1, weight=1)
        self.farming_config_frame.grid_columnconfigure(3, weight=1)
        
        # Pokémon cible
        self.pokemon_label = ctk.CTkLabel(self.farming_config_frame, text="Pokémon cible:")
        self.pokemon_label.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="w")
        self.pokemon_entry = ctk.CTkEntry(self.farming_config_frame, width=150)
        self.pokemon_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.pokemon_entry.insert(0, "Sharpedo")
        
        # Numéro de route
        self.route_label = ctk.CTkLabel(self.farming_config_frame, text="Numéro de route:")
        self.route_label.grid(row=0, column=2, padx=(20, 10), pady=10, sticky="w")
        self.route_entry = ctk.CTkEntry(self.farming_config_frame, width=100)
        self.route_entry.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        self.route_entry.insert(0, "124")
        
        # Description
        self.farming_description = ctk.CTkLabel(tab, text="Cette fonction cherche un Pokémon spécifique sur une route donnée en cliquant automatiquement jusqu'à ce qu'il apparaisse, puis tente de le capturer.", wraplength=700)
        self.farming_description.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Frame des boutons
        self.farming_button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.farming_button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Boutons
        self.open_button = ctk.CTkButton(self.farming_button_frame, text="1. Ouvrir PokéClicker", command=self.open_pokeclicker)
        self.open_button.grid(row=0, column=0, padx=10, pady=10)
        
        self.start_farming_button = ctk.CTkButton(self.farming_button_frame, text="2. Démarrer Farming", command=self.start_farming)
        self.start_farming_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.stop_farming_button = ctk.CTkButton(self.farming_button_frame, text="Arrêter", fg_color="#D22B2B", 
                                      command=self.stop_farming)
        self.stop_farming_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.close_button = ctk.CTkButton(self.farming_button_frame, text="Fermer Navigateur", 
                                       fg_color="transparent", border_width=1, text_color=("gray10", "gray90"),
                                       command=self.close_browser)
        self.close_button.grid(row=0, column=3, padx=10, pady=10)
    
    def setup_autoclicker_tab(self):
        """Configurer l'onglet d'auto-clicker"""
        tab = self.tab_view.tab("Auto Clicker")
        tab.grid_columnconfigure(0, weight=1)
        
        # Frame de configuration
        self.autoclicker_config_frame = ctk.CTkFrame(tab)
        self.autoclicker_config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Intervalle
        self.autoclicker_interval_label = ctk.CTkLabel(self.autoclicker_config_frame, text="Intervalle de clic (ms):")
        self.autoclicker_interval_label.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="w")
        
        self.autoclicker_interval_slider = ctk.CTkSlider(self.autoclicker_config_frame, from_=10, to=500, 
                                                      command=self.update_autoclicker_interval)
        self.autoclicker_interval_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.autoclicker_interval_slider.set(50)
        
        self.autoclicker_interval_value = ctk.CTkLabel(self.autoclicker_config_frame, text="50 ms")
        self.autoclicker_interval_value.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Description
        self.autoclicker_description = ctk.CTkLabel(tab, text="Cette fonction clique automatiquement sur le Pokémon actuel à l'intervalle défini. Utile pour capturer rapidement ou combattre sans chercher un Pokémon spécifique.", wraplength=700)
        self.autoclicker_description.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Frame des boutons
        self.autoclicker_button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.autoclicker_button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Boutons
        self.start_autoclicker_button = ctk.CTkButton(self.autoclicker_button_frame, text="Démarrer Auto Clicker", 
                                                   command=self.start_autoclicker)
        self.start_autoclicker_button.grid(row=0, column=0, padx=10, pady=10)
        
        self.stop_autoclicker_button = ctk.CTkButton(self.autoclicker_button_frame, text="Arrêter", 
                                                  fg_color="#D22B2B", command=self.stop_autoclicker)
        self.stop_autoclicker_button.grid(row=0, column=1, padx=10, pady=10)
    
    def setup_dungeon_tab(self):
        """Configurer l'onglet d'automatisation des donjons"""
        tab = self.tab_view.tab("Automatisation de Donjon")
        tab.grid_columnconfigure(0, weight=1)
        
        # Frame de configuration
        self.dungeon_config_frame = ctk.CTkFrame(tab)
        self.dungeon_config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Nombre de donjons à exécuter
        self.dungeon_count_label = ctk.CTkLabel(self.dungeon_config_frame, text="Nombre de donjons à compléter:")
        self.dungeon_count_label.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="w")
        
        self.dungeon_count_var = ctk.IntVar(value=5)
        self.dungeon_count_entry = ctk.CTkEntry(self.dungeon_config_frame, width=100, textvariable=self.dungeon_count_var)
        self.dungeon_count_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Option pour un nombre illimité de donjons
        self.dungeon_unlimited_var = ctk.BooleanVar(value=False)
        self.dungeon_unlimited_checkbox = ctk.CTkCheckBox(self.dungeon_config_frame, 
                                                      text="Mode illimité", 
                                                      variable=self.dungeon_unlimited_var,
                                                      command=self.toggle_dungeon_count)
        self.dungeon_unlimited_checkbox.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Description
        self.dungeon_description = ctk.CTkLabel(tab, text="Cette fonction explore automatiquement les donjons en recherchant les coffres pour découvrir et battre le boss. Elle peut être exécutée pour un nombre défini de donjons ou en continu.", wraplength=700)
        self.dungeon_description.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Frame des boutons
        self.dungeon_button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.dungeon_button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Boutons
        self.start_dungeon_button = ctk.CTkButton(self.dungeon_button_frame, text="Démarrer Automatisation", 
                                              command=self.start_dungeon_automation)
        self.start_dungeon_button.grid(row=0, column=0, padx=10, pady=10)
        
        self.stop_dungeon_button = ctk.CTkButton(self.dungeon_button_frame, text="Arrêter", 
                                             fg_color="#D22B2B", command=self.stop_dungeon_automation)
        self.stop_dungeon_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Statuts des donjons
        self.dungeon_stats_frame = ctk.CTkFrame(tab)
        self.dungeon_stats_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.dungeon_completed_label = ctk.CTkLabel(self.dungeon_stats_frame, text="Donjons complétés: 0")
        self.dungeon_completed_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.dungeon_progress_label = ctk.CTkLabel(self.dungeon_stats_frame, text="Progression: 0%")
        self.dungeon_progress_label.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        
        self.dungeon_time_label = ctk.CTkLabel(self.dungeon_stats_frame, text="Temps écoulé: 0s")
        self.dungeon_time_label.grid(row=0, column=2, padx=20, pady=10, sticky="w")
    
    def toggle_dungeon_count(self):
        """Activer/désactiver le champ de nombre de donjons selon le mode illimité"""
        if self.dungeon_unlimited_var.get():
            self.dungeon_count_entry.configure(state="disabled")
        else:
            self.dungeon_count_entry.configure(state="normal")
    
    def log_message(self, message):
        """Ajouter un message au journal"""
        self.log_textbox.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_textbox.see("end")
    
    def update_status(self, status):
        """Mettre à jour le statut affiché"""
        self.status_label.configure(text=f"Statut: {status}")
    
    def change_appearance(self, new_appearance_mode):
        """Changer le thème de l'application"""
        ctk.set_appearance_mode(new_appearance_mode)
    
    def update_autoclicker_interval(self, value):
        """Mettre à jour l'affichage de l'intervalle d'auto-click"""
        self.autoclicker_interval_value.configure(text=f"{int(value)} ms")
    
    def open_pokeclicker(self):
        """Ouvrir PokéClicker dans le navigateur"""
        success = self.bot.open_pokeclicker()
        if success:
            self.update_status("Connecté")
    
    def start_farming(self):
        """Démarrer le farming"""
        # Mise à jour des paramètres
        self.bot.target_pokemon = self.pokemon_entry.get().strip()
        self.bot.target_route = self.route_entry.get().strip()
        
        # Vérifications
        if not self.bot.target_pokemon:
            self.log_message("ERREUR: Veuillez entrer un nom de Pokémon")
            return
        
        if not self.bot.target_route:
            self.log_message("ERREUR: Veuillez entrer un numéro de route")
            return
        
        # Démarrer le farming
        success = self.bot.start_farming_thread()
        if success:
            self.update_status("Farming en cours")
    
    def stop_farming(self):
        """Arrêter le farming"""
        self.bot.stop_farming()
    
    def start_autoclicker(self):
        """Démarrer l'auto-clicker"""
        # Mise à jour des paramètres
        self.bot.autoclicker_interval = int(self.autoclicker_interval_slider.get())
        
        # Démarrer l'auto-clicker
        success = self.bot.start_autoclicker_thread()
        if success:
            self.update_status("Auto-clicker actif")
    
    def stop_autoclicker(self):
        """Arrêter l'auto-clicker"""
        self.bot.stop_autoclicker()
    
    def start_dungeon_automation(self):
        """Démarrer l'automatisation des donjons"""
        # Déterminer le nombre de donjons à exécuter
        dungeons_to_run = 0 if self.dungeon_unlimited_var.get() else self.dungeon_count_var.get()
        
        # Vérification des entrées
        if not self.dungeon_unlimited_var.get() and dungeons_to_run <= 0:
            self.log_message("ERREUR: Veuillez entrer un nombre valide de donjons à compléter")
            return
        
        # Lancer l'automatisation
        success = self.bot.start_dungeon_automation(dungeons_to_run)
        if success:
            self.update_status("Donjons en cours")
            self.dungeon_completed_label.configure(text="Donjons complétés: 0")
            
            if dungeons_to_run > 0:
                self.dungeon_progress_label.configure(text=f"Progression: 0/{dungeons_to_run}")
            else:
                self.dungeon_progress_label.configure(text="Progression: Mode illimité")
    
    def stop_dungeon_automation(self):
        """Arrêter l'automatisation des donjons"""
        self.bot.stop_dungeon_automation()
    
    def close_browser(self):
        """Fermer le navigateur"""
        self.bot.close_browser()