import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

class PokeclickerBotDungeonCombat:
    """
    Fonctionnalités de combat dans le donjon
    Gère les combats et interactions avec les coffres/boss
    """
    
    def handle_battle(self):
        """Gérer un combat en cliquant sur l'ennemi avec vérification d'efficacité"""
        try:
            self.log("Combat détecté, attaque en cours...")
            battle_start_time = time.time()
            battle_attempts = 0
            max_attempts = 150  # Augmenté pour les combats difficiles
            last_check_time = time.time()
            last_hp = None
            stuck_counter = 0
            
            while self.is_in_battle() and battle_attempts < max_attempts and self.running:
                current_time = time.time()
                
                # Essayer de trouver l'HP actuel de l'ennemi pour suivre les progrès
                try:
                    hp_bar = self.driver.find_element(By.CSS_SELECTOR, ".enemyBar.progress-bar")
                    current_hp = hp_bar.get_attribute("style")  # Généralement contient "width: XX%"
                except:
                    current_hp = None
                
                # Vérifier si nous sommes bloqués (HP ne change pas après plusieurs clics)
                if current_hp == last_hp and (current_time - last_check_time) > 2:
                    stuck_counter += 1
                    self.log(f"Combat semble bloqué (HP inchangé après {stuck_counter} vérifications)")
                    
                    if stuck_counter >= 3:
                        # Essayer différentes approches pour débloquer
                        self.log("Tentative de déblocage du combat...")
                        
                        # Méthode 1: Utiliser directement le JavaScript du jeu
                        try:
                            self.driver.execute_script(
                                "if (typeof DungeonBattle !== 'undefined') { DungeonBattle.clickAttack(); }"
                            )
                        except:
                            pass
                        
                        # Méthode 2: Essayer de cliquer sur l'interface du jeu en général
                        try:
                            body = self.driver.find_element(By.TAG_NAME, "body")
                            self.driver.execute_script("arguments[0].click();", body)
                        except:
                            pass
                        
                        # Réinitialiser le compteur
                        stuck_counter = 0
                
                # Essayer différentes méthodes pour attaquer
                attack_succeeded = False
                
                # Méthode 1: Cliquer sur l'ennemi s'il est visible
                try:
                    enemy = self.driver.find_element(By.CSS_SELECTOR, "div.dungeon-enemy")
                    self.driver.execute_script("arguments[0].click();", enemy)
                    attack_succeeded = True
                except:
                    pass
                
                # Méthode 2: Utiliser le JavaScript du jeu directement
                if not attack_succeeded:
                    try:
                        self.driver.execute_script(
                            "if (typeof DungeonBattle !== 'undefined') { DungeonBattle.clickAttack(); }"
                        )
                        attack_succeeded = True
                    except:
                        pass
                
                # Méthode 3: Cliquer sur l'image de l'ennemi
                if not attack_succeeded:
                    try:
                        enemy_img = self.driver.find_element(By.CSS_SELECTOR, "img.enemy")
                        self.driver.execute_script("arguments[0].click();", enemy_img)
                        attack_succeeded = True
                    except:
                        pass
                
                if attack_succeeded:
                    self.clicks += 1
                    
                    # Toutes les 10 attaques, vérifier si l'HP a changé
                    if battle_attempts % 10 == 0:
                        if current_hp != last_hp:
                            self.log(f"Combat en cours, HP ennemi: {current_hp}")
                            last_hp = current_hp
                            last_check_time = current_time
                        else:
                            self.log("HP inchangé, vérification si toujours en combat...")
                else:
                    self.log("Impossible d'attaquer l'ennemi, vérification de l'état du jeu...")
                    time.sleep(0.5)
                
                battle_attempts += 1
                
                # Si le combat dure plus de 20 secondes, journaliser pour surveillance
                if battle_attempts % 50 == 0:
                    battle_duration = int(current_time - battle_start_time)
                    self.log(f"Combat en cours depuis {battle_duration}s, {battle_attempts} attaques effectuées")
                
                # Pause courte entre les attaques
                time.sleep(0.05)
            
            battle_duration = int(time.time() - battle_start_time)
            
            if battle_attempts >= max_attempts:
                self.log(f"Le combat a duré trop longtemps ({battle_duration}s), passage à la suite...")
                return False
            else:
                self.log(f"Combat terminé en {battle_duration}s après {battle_attempts} attaques!")
                return True
                
        except Exception as e:
            self.log(f"Erreur pendant le combat: {str(e)}")
            return False
    
    def handle_chest(self):
        """Gérer un coffre en l'ouvrant"""
        try:
            self.log("Coffre trouvé, ouverture...")
            # Trouver le bouton d'ouverture du coffre et cliquer dessus
            chest_button = self.driver.find_element(By.CSS_SELECTOR, "button.chest-button")
            self.driver.execute_script("arguments[0].click();", chest_button)
            
            # Attendre que le coffre soit ouvert
            time.sleep(0.5)
            return True
            
        except Exception as e:
            self.log(f"Erreur lors de l'ouverture du coffre: {str(e)}")
            return False
    
    def handle_boss_fight(self):
        """Engager et gérer le combat contre le boss"""
        try:
            self.log("Boss trouvé, engagement du combat...")
            # Cliquer sur le bouton pour commencer le combat contre le boss
            boss_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-danger.dungeon-button")
            self.driver.execute_script("arguments[0].click();", boss_button)
            
            # Attendre que le combat commence
            time.sleep(1)
            
            # Gérer le combat
            return self.handle_battle()
            
        except Exception as e:
            self.log(f"Erreur lors du combat contre le boss: {str(e)}")
            return False