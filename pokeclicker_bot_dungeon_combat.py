import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

class PokeclickerBotDungeonCombat:
    """
    Fonctionnalités de combat dans le donjon
    Gère les combats et interactions avec les coffres/boss
    """
    
    def get_enemy_health_info(self):
        """Récupérer les informations de santé de l'ennemi directement depuis l'élément span"""
        try:
            # Rechercher l'élément span qui contient les informations de santé
            health_span = self.driver.find_element(By.CSS_SELECTOR, "span[data-bind*=\"DungeonBattle.enemyPokemon().health()\"]")
            health_text = health_span.text
            
            # Analyser le texte qui devrait être au format "current / max"
            if "/" in health_text:
                parts = health_text.split("/")
                current_health = parts[0].strip().replace(",", "")
                max_health = parts[1].strip().replace(",", "")
                
                try:
                    current_health = float(current_health)
                    max_health = float(max_health)
                    health_percentage = (current_health / max_health) * 100 if max_health > 0 else 0
                    
                    return {
                        "current": current_health,
                        "max": max_health,
                        "percentage": health_percentage,
                        "text": health_text
                    }
                except ValueError:
                    # Si la conversion en nombre échoue
                    return None
            
            return None
        except Exception as e:
            # self.log(f"Erreur lors de la lecture des informations de santé: {str(e)}")
            return None
    
    def handle_battle(self):
        """Gérer un combat en cliquant sur l'ennemi avec vérification d'efficacité"""
        try:
            self.log("Combat détecté, attaque en cours...")
            battle_start_time = time.time()
            battle_attempts = 0
            max_attempts = 150  # Augmenté pour les combats difficiles
            last_check_time = time.time()
            last_health_info = None
            stuck_counter = 0
            consecutive_errors = 0
            
            while self.is_in_battle() and battle_attempts < max_attempts and self.running:
                current_time = time.time()
                
                # Récupérer les informations de santé actuelles
                current_health_info = self.get_enemy_health_info()
                
                # Vérifier si nous avons des informations de santé valides
                if current_health_info:
                    consecutive_errors = 0  # Réinitialiser le compteur d'erreurs
                    
                    # Vérifier si la santé a changé
                    if last_health_info:
                        # Comparer les valeurs numériques plutôt que le texte
                        if abs(current_health_info["current"] - last_health_info["current"]) < 0.1:
                            # La santé n'a pas changé significativement
                            if (current_time - last_check_time) > 1:  # Réduit à 1 seconde pour une détection plus rapide
                                stuck_counter += 1
                                self.log(f"Combat semble bloqué (HP: {current_health_info['text']}, inchangé après {stuck_counter} vérifications)")
                                
                                if stuck_counter >= 3:
                                    self.log("Tentative de déblocage du combat...")
                                    
                                    # Essayer différentes approches pour débloquer
                                    # Méthode 1: Utiliser directement le JavaScript du jeu avec plus de paramètres
                                    try:
                                        self.driver.execute_script("""
                                            if (typeof DungeonBattle !== 'undefined') {
                                                // Forcer une attaque avec des paramètres différents
                                                DungeonBattle.clickAttack();
                                                
                                                // Essayer également de cibler directement l'ennemi si possible
                                                if (DungeonBattle.enemyPokemon()) {
                                                    DungeonBattle.damage(DungeonBattle.enemyPokemon(), DungeonBattle.playerPokemon().calculateDamage());
                                                }
                                            }
                                        """)
                                        self.log("Tentative d'attaque via script JavaScript avancé")
                                    except Exception as je:
                                        self.log(f"Erreur JavaScript: {str(je)}")
                                    
                                    # Méthode 2: Cliquer directement sur l'élément de santé pour "réveiller" l'interface
                                    try:
                                        health_element = self.driver.find_element(By.CSS_SELECTOR, ".enemyBar.progress-bar")
                                        self.driver.execute_script("arguments[0].click();", health_element)
                                    except:
                                        pass
                                    
                                    # Méthode 3: Cliquer ailleurs puis revenir sur l'ennemi
                                    try:
                                        body = self.driver.find_element(By.TAG_NAME, "body")
                                        self.driver.execute_script("arguments[0].click();", body)
                                        time.sleep(0.2)
                                    except:
                                        pass
                                    
                                    # Réinitialiser les compteurs
                                    stuck_counter = 0
                                    last_check_time = current_time
                        else:
                            # La santé a changé, réinitialiser les compteurs
                            if battle_attempts % 10 == 0 or stuck_counter > 0:
                                self.log(f"Progression du combat: {current_health_info['text']} ({current_health_info['percentage']:.1f}%)")
                            stuck_counter = 0
                            last_check_time = current_time
                    
                    # Mettre à jour les informations de santé
                    last_health_info = current_health_info
                else:
                    consecutive_errors += 1
                    if consecutive_errors > 5:
                        # Si on ne peut pas lire les informations de santé plusieurs fois de suite
                        # vérifier si on est toujours en combat
                        if not self.is_in_battle():
                            self.log("Combat terminé (détecté par absence d'informations de santé)")
                            break
                
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
                
                # Méthode 4: Cliquer sur la barre de santé
                if not attack_succeeded:
                    try:
                        health_bar = self.driver.find_element(By.CSS_SELECTOR, ".enemyBar.progress-bar")
                        self.driver.execute_script("arguments[0].click();", health_bar)
                        attack_succeeded = True
                    except:
                        pass
                
                if attack_succeeded:
                    self.clicks += 1
                else:
                    self.log("Impossible d'attaquer l'ennemi, vérification de l'état du jeu...")
                    time.sleep(0.5)
                
                battle_attempts += 1
                
                # Si le combat dure plus de 20 secondes, journaliser pour surveillance
                if battle_attempts % 50 == 0:
                    battle_duration = int(current_time - battle_start_time)
                    self.log(f"Combat en cours depuis {battle_duration}s, {battle_attempts} attaques effectuées")
                    
                    # Si le combat dure vraiment trop longtemps, essayer une approche plus agressive
                    if battle_duration > 30:
                        try:
                            self.log("Combat très long, tentative avancée de clics rapides...")
                            # Série de clics rapides
                            for _ in range(10):
                                self.driver.execute_script("if (typeof DungeonBattle !== 'undefined') { DungeonBattle.clickAttack(); }")
                                time.sleep(0.05)
                        except:
                            pass
                
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
            
            # Vérifier si un message de récompense est visible
            try:
                reward_text = self.driver.find_element(By.CSS_SELECTOR, ".modal-body")
                if reward_text:
                    reward_content = reward_text.text
                    self.log(f"Récompense obtenue: {reward_content}")
            except:
                pass
                
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