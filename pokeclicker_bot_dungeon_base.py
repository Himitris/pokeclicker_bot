import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class PokeclickerBotDungeonBase:
    """
    Fonctionnalités de base pour l'automatisation des donjons
    Contient les vérifications d'état et les méthodes utilitaires
    """
    
    def is_element_clickable(self, selector, timeout=2):
        """Vérification si un élément est vraiment cliquable"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            return True
        except (TimeoutException, NoSuchElementException):
            return False
        except Exception as e:
            self.log(f"Erreur lors de la vérification du clic: {str(e)}")
            return False
    
    def is_in_dungeon(self):
        """Méthode pour détecter si nous sommes dans un donjon"""
        try:
            dungeon_board = self.driver.find_element(By.CSS_SELECTOR, "table.dungeon-board")
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            self.log(f"Erreur lors de la vérification du donjon: {str(e)}")
            return False
    
    def check_game_state(self):
        """Vérifier l'état actuel du jeu pour déterminer l'action à prendre"""
        try:
            # Vérifier si nous sommes en combat
            if self.is_in_battle():
                return "battle"
            
            # Vérifier si un coffre est visible
            if self.is_chest_visible():
                return "chest"
            
            # Vérifier si le bouton du boss est visible
            if self.has_boss_button():
                return "boss"
            
            # Vérifier si nous sommes dans un donjon mais pas dans un état spécial
            if self.is_in_dungeon():
                return "exploring"
            
            # Si nous ne sommes pas dans un donjon, le donjon pourrait être terminé ou fermé
            self.log("État de jeu indéterminé - vérifier si le donjon est terminé")
            return "unknown"
        
        except Exception as e:
            self.log(f"Erreur lors de la vérification de l'état du jeu: {str(e)}")
            return "error"
    
    def start_dungeon(self):
        """Démarrer un donjon"""
        try:
            # Chercher le bouton de démarrage du donjon
            start_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn[onclick*='DungeonRunner.initializeDungeon']")
            
            # Vérifier que le bouton n'est pas désactivé
            if "disabled" in start_button.get_attribute("class"):
                self.log("Le bouton de démarrage du donjon est désactivé (pas assez de jetons ou donjon verrouillé)")
                return False
            
            # Cliquer sur le bouton
            self.driver.execute_script("arguments[0].click();", start_button)
            self.log("Donjon démarré!")
            
            # Attendre que la carte du donjon soit chargée
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.dungeon-board"))
                )
                return True
            except TimeoutException:
                self.log("Le donjon n'a pas pu être chargé correctement")
                return False
            
        except NoSuchElementException:
            self.log("Bouton de démarrage du donjon non trouvé")
            return False
        except Exception as e:
            self.log(f"Erreur lors du démarrage du donjon: {str(e)}")
            return False
    
    def has_boss_button(self):
        """Vérifier si le bouton de combat contre le boss est présent"""
        try:
            boss_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-danger.dungeon-button")
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            self.log(f"Erreur lors de la vérification du bouton de boss: {str(e)}")
            return False
    
    def is_in_battle(self):
        """Vérifier si le joueur est en combat"""
        try:
            battle_div = self.driver.find_element(By.CSS_SELECTOR, "div[data-bind*='DungeonBattle.enemyPokemon']")
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            self.log(f"Erreur lors de la vérification du combat: {str(e)}")
            return False
    
    def is_chest_visible(self):
        """Vérifier si un coffre est visible"""
        try:
            chest_div = self.driver.find_element(By.CSS_SELECTOR, "div.dungeon-chest")
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            self.log(f"Erreur lors de la vérification du coffre: {str(e)}")
            return False
    
    def get_visible_tiles(self):
        """Obtenir toutes les cases visibles sur la carte du donjon"""
        try:
            # Trouver toutes les cases qui ne sont pas 'tile-invisible'
            tiles = self.driver.find_elements(By.CSS_SELECTOR, "td.tile:not(.tile-invisible)")
            return tiles
        except Exception as e:
            self.log(f"Erreur lors de la récupération des cases visibles: {str(e)}")
            return []
    
    def get_all_tiles(self):
        """Obtenir toutes les cases sur la carte du donjon"""
        try:
            # Trouver toutes les cases
            tiles = self.driver.find_elements(By.CSS_SELECTOR, "td.tile")
            return tiles
        except Exception as e:
            self.log(f"Erreur lors de la récupération des cases: {str(e)}")
            return []
    
    def start_dungeon_automation(self, dungeons_to_run=0):
        """Démarrer l'automatisation des donjons"""
        if self.driver is None:
            self.log("Erreur: Navigateur non initialisé. Veuillez ouvrir PokéClicker d'abord.")
            return False
        
        # Configurer le nombre de donjons à exécuter (0 = illimité)
        self.dungeons_to_run = dungeons_to_run
        
        # Réinitialiser les variables importantes
        self.running = True
        self.dungeons_completed = 0
        
        # Démarrer l'automatisation dans un thread séparé
        threading.Thread(target=self.run_dungeon).start()
        return True
    
    def stop_dungeon_automation(self):
        """Arrêter l'automatisation des donjons"""
        self.running = False
        self.log("Arrêt de l'automatisation des donjons...")
        self.update_status("Donjons arrêtés")