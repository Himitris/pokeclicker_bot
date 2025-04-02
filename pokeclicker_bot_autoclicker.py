import time
import threading

class PokeclickerBotAutoclicker:
    def auto_clicker(self):
        """Fonction d'auto-clicker simple"""
        self.auto_clicking = True
        self.start_time = time.time()
        self.clicks = 0
        
        self.log(f"========== AUTO-CLICKER DÉMARRÉ ==========")
        self.log(f"Intervalle: {self.autoclicker_interval} ms")
        self.update_status("Auto-clicker actif")
        
        # Attendre que le jeu soit chargé
        time.sleep(1)
        
        while self.auto_clicking:
            try:
                # Cliquer sur le Pokémon
                if self.click_on_pokemon():
                    if self.clicks % 100 == 0:
                        elapsed_time = int(time.time() - self.start_time)
                        self.log(f"Auto-clicker: {self.clicks} clics effectués, {elapsed_time}s écoulées")
                
                # Attendre l'intervalle défini
                time.sleep(self.autoclicker_interval / 1000)
                
            except Exception as e:
                self.log(f"Erreur pendant l'auto-click: {str(e)}")
                time.sleep(0.5)
        
        elapsed_time = int(time.time() - self.start_time)
        self.log(f"========== AUTO-CLICKER TERMINÉ ==========")
        self.log(f"Durée totale: {elapsed_time} secondes")
        self.log(f"Clics: {self.clicks}")
    
    def start_autoclicker_thread(self):
        """Démarrer l'auto-clicker dans un thread séparé"""
        if self.driver is None:
            self.log("Erreur: Navigateur non initialisé. Veuillez ouvrir PokéClicker d'abord.")
            return False
        
        # Démarrer l'auto-clicker dans un thread séparé
        threading.Thread(target=self.auto_clicker).start()
        return True
    
    def stop_autoclicker(self):
        """Arrêter l'auto-clicker"""
        self.auto_clicking = False
        self.log("Arrêt de l'auto-clicker...")
        self.update_status("Auto-clicker arrêté")