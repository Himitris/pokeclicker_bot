import time
import threading

class PokeclickerBotFarmer:
    def farm_pokemon(self):
        """Fonction principale pour le farming automatisé"""
        self.running = True
        self.start_time = time.time()
        self.clicks = 0
        self.pokemon_found = 0
        self.pokemon_caught = 0
        
        self.log(f"========== FARMING DÉMARRÉ ==========")
        self.log(f"Pokémon cible: {self.target_pokemon}")
        self.log(f"Route: {self.target_route}")
        self.update_status("Farming en cours")
        
        # Attendre que le jeu soit chargé
        time.sleep(2)
        
        # Au lieu de cliquer sur la route, essayons d'appeler directement la fonction JavaScript
        try:
            self.driver.execute_script(f"MapHelper.moveToRoute({self.target_route}, 2);")
            self.log(f"Navigation vers la route {self.target_route} via JavaScript")
        except Exception as e:
            self.log(f"Erreur lors de la navigation vers la route: {str(e)}")
        
        last_pokemon_name = None
        while self.running:
            try:
                # Récupérer le nom du Pokémon actuel
                current_pokemon = self.get_current_pokemon_name()
                
                if current_pokemon:
                    # Éviter de spammer le log si le Pokémon n'a pas changé
                    if current_pokemon != last_pokemon_name:
                        self.log(f"Pokémon actuel: {current_pokemon}")
                        last_pokemon_name = current_pokemon
                    
                    # Vérifier si c'est le Pokémon cible
                    if current_pokemon.lower() == self.target_pokemon.lower():
                        self.log(f"POKÉMON CIBLE TROUVÉ: {self.target_pokemon}!")
                        self.pokemon_found += 1
                        
                        # Cliquer rapidement pour capturer le Pokémon
                        capture_start_time = time.time()
                        capture_clicks = 0
                        captured = False
                        
                        while self.running and not captured and (time.time() - capture_start_time < 10):
                            # Cliquer sur le Pokémon
                            if self.click_on_pokemon():
                                capture_clicks += 1
                                
                                # Vérifier si le Pokémon a été capturé
                                if self.check_capture_notification():
                                    captured = True
                                    self.pokemon_caught += 1
                                    self.log(f"SUCCÈS! {self.target_pokemon} a été capturé après {capture_clicks} clics!")
                                    break
                            
                            # Petite pause entre les clics
                            time.sleep(0.01)
                        
                        if not captured:
                            self.log(f"Échec de la capture après {capture_clicks} clics et 10 secondes")
                    else:
                        # Ce n'est pas le bon Pokémon, essayer d'en générer un nouveau 
                        # en cliquant sur un autre endroit (ou en rafraîchissant l'ennemi)
                        try:
                            # Méthode 1: Essayer d'exécuter directement le code JavaScript pour cliquer sur l'ennemi
                            self.driver.execute_script("Battle.generateNewEnemy();")
                            self.clicks += 1
                        except Exception as e1:
                            try:
                                # Méthode 2: Cliquer sur le bouton de combat (s'il existe)
                                battle_button = self.driver.find_element(By.ID, "battleContainer")
                                self.driver.execute_script("arguments[0].click();", battle_button)
                                self.clicks += 1
                            except Exception as e2:
                                self.log(f"Impossible de générer un nouveau Pokémon: {str(e2)}")
                else:
                    self.log("Aucun Pokémon trouvé, réessai...")
                    # Essayer de revenir sur la route
                    try:
                        self.driver.execute_script(f"MapHelper.moveToRoute({self.target_route}, 2);")
                    except:
                        pass
                
                # Mettre à jour les statistiques toutes les 10 tentatives
                if self.clicks % 10 == 0:
                    elapsed_time = int(time.time() - self.start_time)
                    self.log(f"Statistiques: {self.clicks} clics, {self.pokemon_found} trouvés, {self.pokemon_caught} capturés, {elapsed_time}s écoulées")
                
                # Attendre avant de réessayer
                time.sleep(0.5)
                
            except Exception as e:
                self.log(f"Erreur pendant le farming: {str(e)}")
                time.sleep(1)
        
        elapsed_time = int(time.time() - self.start_time)
        self.log(f"========== FARMING TERMINÉ ==========")
        self.log(f"Durée totale: {elapsed_time} secondes")
        self.log(f"Clics: {self.clicks}")
        self.log(f"Pokémon cible trouvés: {self.pokemon_found}")
        self.log(f"Pokémon capturés: {self.pokemon_caught}")
    
    def start_farming_thread(self):
        """Démarrer le farming dans un thread séparé"""
        if self.driver is None:
            self.log("Erreur: Navigateur non initialisé. Veuillez ouvrir PokéClicker d'abord.")
            return False
        
        if not self.target_pokemon or not self.target_route:
            self.log("Erreur: Veuillez définir un Pokémon cible et une route.")
            return False
        
        # Démarrer le farming dans un thread séparé
        threading.Thread(target=self.farm_pokemon).start()
        return True
    
    def stop_farming(self):
        """Arrêter le farming"""
        self.running = False
        self.log("Arrêt du farming...")
        self.update_status("Farming arrêté")