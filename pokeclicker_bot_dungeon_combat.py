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
        """Gérer un combat en cliquant sur l'ennemi avec vérification d'efficacité et une stratégie adaptative"""
        try:
            self.log("Combat détecté, attaque en cours...")
            battle_start_time = time.time()
            battle_attempts = 0
            max_attempts = 150  # Maximum d'essais pour éviter les blocages
            last_check_time = time.time()
            last_health_info = None
            stuck_counter = 0
            consecutive_errors = 0
            attack_interval = 0.05  # Intervalle initial entre les attaques (50ms)
            
            # Obtenir les infos initiales sur la santé pour déterminer la difficulté du combat
            initial_health_info = self.get_enemy_health_info()
            if initial_health_info:
                # Estimer la difficulté du combat (santé > 10000 = combat difficile)
                difficult_battle = initial_health_info["max"] > 10000
                if difficult_battle:
                    self.log(f"Combat difficile détecté (HP: {initial_health_info['max']}), adapting strategy")
                    # Réduire l'intervalle pour les combats difficiles
                    attack_interval = 0.02
            
            while self.is_in_battle() and battle_attempts < max_attempts and self.running:
                current_time = time.time()
                
                # Récupérer les informations de santé actuelles
                current_health_info = self.get_enemy_health_info()
                
                # Vérifier si nous avons des informations de santé valides
                if current_health_info:
                    consecutive_errors = 0  # Réinitialiser le compteur d'erreurs
                    
                    # Vérifier si la santé a changé depuis la dernière vérification
                    if last_health_info:
                        # Comparer les valeurs numériques plutôt que le texte
                        if abs(current_health_info["current"] - last_health_info["current"]) < 0.1:
                            # La santé n'a pas changé significativement
                            if (current_time - last_check_time) > 0.5:  # Vérification plus fréquente
                                stuck_counter += 1
                                self.log(f"Combat semble bloqué (HP: {current_health_info['text']}, inchangé après {stuck_counter} vérifications)")
                                
                                if stuck_counter >= 2:  # Réagir plus rapidement aux blocages
                                    self.log("Tentative de déblocage du combat...")
                                    
                                    # Stratégie de déblocage adaptative
                                    if stuck_counter >= 5:
                                        # Stratégie avancée pour les blocages persistants
                                        self.try_advanced_unblocking_strategies()
                                    else:
                                        # Stratégies basiques pour les blocages légers
                                        self.try_basic_unblocking_strategies()
                                    
                                    # Réinitialiser les compteurs
                                    stuck_counter = 0
                                    last_check_time = current_time
                        else:
                            # La santé a changé, réinitialiser les compteurs
                            battle_is_progressing = True
                            
                            # Adapter la fréquence des logs en fonction de la progression
                            hp_percentage = current_health_info["percentage"]
                            if battle_attempts % 20 == 0 or hp_percentage < 30 or stuck_counter > 0:
                                self.log(f"Progression du combat: {current_health_info['text']} ({hp_percentage:.1f}%)")
                            
                            # Adapter la stratégie en fonction de la progression du combat
                            if hp_percentage < 20 and attack_interval > 0.02:
                                # Accélérer les attaques en fin de combat
                                attack_interval = 0.02
                                self.log("Phase finale du combat, accélération des attaques")
                            
                            stuck_counter = 0
                            last_check_time = current_time
                    
                    # Mettre à jour les informations de santé
                    last_health_info = current_health_info
                else:
                    consecutive_errors += 1
                    if consecutive_errors > 3:  # Réduit pour réagir plus rapidement
                        # Si on ne peut pas lire les informations de santé plusieurs fois de suite
                        # vérifier si on est toujours en combat
                        if not self.is_in_battle():
                            self.log("Combat terminé (détecté par absence d'informations de santé)")
                            break
                        else:
                            # Essayer de récupérer les informations par d'autres moyens
                            self.try_alternative_health_check()
                
                # Utiliser une stratégie d'attaque multi-méthodes pour maximiser les chances de succès
                self.execute_multi_method_attack()
                
                battle_attempts += 1
                
                # Monitoring avancé pour les combats longs
                battle_duration = int(current_time - battle_start_time)
                if battle_attempts % 30 == 0:
                    self.log(f"Combat en cours depuis {battle_duration}s, {battle_attempts} attaques effectuées")
                    
                    # Si le combat dure vraiment trop longtemps, essayer une approche plus agressive
                    if battle_duration > 20:
                        self.log("Combat prolongé, activation du mode rafale d'attaques")
                        self.execute_burst_attack_mode(5)  # 5 attaques rapides
                
                # Pause adaptative entre les attaques
                time.sleep(attack_interval)
            
            battle_duration = int(time.time() - battle_start_time)
            
            if battle_attempts >= max_attempts:
                self.log(f"Le combat a duré trop longtemps ({battle_duration}s), passage à la suite...")
                return False
            else:
                dps = battle_attempts / max(1, battle_duration)  # Attaques par seconde
                self.log(f"Combat terminé en {battle_duration}s après {battle_attempts} attaques! ({dps:.1f} attaques/s)")
                return True
                
        except Exception as e:
            self.log(f"Erreur pendant le combat: {str(e)}")
            return False

    def execute_multi_method_attack(self):
        """Exécute plusieurs méthodes d'attaque en séquence pour maximiser les chances de succès"""
        attack_succeeded = False
        
        # Méthode 1: API JavaScript directe (la plus fiable)
        if not attack_succeeded:
            try:
                self.driver.execute_script(
                    "if (typeof DungeonBattle !== 'undefined') { DungeonBattle.clickAttack(); }"
                )
                attack_succeeded = True
            except:
                pass
        
        # Méthode 2: Cliquer sur l'ennemi s'il est visible
        if not attack_succeeded:
            try:
                enemy = self.driver.find_element(By.CSS_SELECTOR, "div.dungeon-enemy")
                self.driver.execute_script("arguments[0].click();", enemy)
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
        
        return attack_succeeded

    def try_basic_unblocking_strategies(self):
        """Stratégies de base pour débloquer un combat"""
        # Stratégie 1: Exécuter l'API JavaScript avec plus de force
        try:
            self.driver.execute_script("""
                if (typeof DungeonBattle !== 'undefined') {
                    try {
                        // Forcer plusieurs attaques consécutives
                        for (let i = 0; i < 3; i++) {
                            DungeonBattle.clickAttack();
                        }
                    } catch(e) {}
                }
            """)
            self.log("Stratégie de déblocage: attaques multiples forcées via JavaScript")
        except:
            pass
        
        # Stratégie 2: Cliquer ailleurs puis revenir sur l'ennemi
        try:
            # Cliquer en dehors de l'ennemi
            body = self.driver.find_element(By.TAG_NAME, "body")
            self.driver.execute_script("arguments[0].click();", body)
            time.sleep(0.1)
            
            # Revenir sur l'ennemi
            self.execute_multi_method_attack()
            self.log("Stratégie de déblocage: clic extérieur puis retour sur l'ennemi")
        except:
            pass

    def try_advanced_unblocking_strategies(self):
        """Stratégies avancées pour débloquer un combat persistant"""
        # Stratégie 1: Utiliser l'API JavaScript avancée du jeu
        try:
            self.driver.execute_script("""
                if (typeof DungeonBattle !== 'undefined') {
                    try {
                        // Forcer des dégâts directs si possible
                        if (DungeonBattle.enemyPokemon() && DungeonBattle.playerPokemon()) {
                            const damage = DungeonBattle.playerPokemon().calculateDamage(DungeonBattle.enemyPokemon());
                            DungeonBattle.damage(DungeonBattle.enemyPokemon(), damage);
                            
                            // Puis refaire plusieurs attaques normales
                            for (let i = 0; i < 5; i++) {
                                DungeonBattle.clickAttack();
                            }
                        }
                    } catch(e) {}
                }
            """)
            self.log("Stratégie avancée: tentative de forçage des dégâts via API interne")
        except:
            pass
        
        # Stratégie 2: Rafale d'attaques intensives
        self.execute_burst_attack_mode(10)  # 10 attaques rapides
        
        # Stratégie 3: Vérifier si nous pouvons avancer malgré l'ennemi
        try:
            self.driver.execute_script("""
                if (typeof DungeonRunner !== 'undefined' && typeof DungeonRunner.map !== 'undefined') {
                    // Tenter de poursuivre l'exploration malgré le combat
                    const pos = DungeonRunner.map.playerPosition();
                    if (pos) {
                        const directions = [[0,-1], [1,0], [0,1], [-1,0]];
                        for (const [dx, dy] of directions) {
                            try {
                                DungeonRunner.map.moveToCoordinates(pos.x + dx, pos.y + dy);
                                break;
                            } catch(e) {}
                        }
                    }
                }
            """)
            self.log("Stratégie avancée: tentative d'échappement du combat")
        except:
            pass

    def execute_burst_attack_mode(self, count=5):
        """Exécute une rafale d'attaques rapides pour débloquer ou accélérer un combat"""
        self.log(f"Exécution d'une rafale de {count} attaques rapides")
        
        # Méthode 1: Utiliser directement l'API JavaScript (plus fiable pour les rafales)
        try:
            self.driver.execute_script(f"""
                if (typeof DungeonBattle !== 'undefined') {{
                    for (let i = 0; i < {count}; i++) {{
                        DungeonBattle.clickAttack();
                    }}
                }}
            """)
            self.clicks += count
            return True
        except:
            pass
        
        # Méthode 2: Clicks rapides manuels en séquence
        success = 0
        for _ in range(count):
            if self.execute_multi_method_attack():
                success += 1
            time.sleep(0.01)  # Pause très courte entre les clics
        
        return success > 0

    def try_alternative_health_check(self):
        """Tente de récupérer les informations de santé par des méthodes alternatives"""
        try:
            # Méthode 1: Vérifier directement l'état du combat via JavaScript
            battle_state = self.driver.execute_script("""
                if (typeof DungeonBattle !== 'undefined') {
                    if (DungeonBattle.enemyPokemon()) {
                        return {
                            inBattle: true,
                            currentHP: DungeonBattle.enemyPokemon().health(),
                            maxHP: DungeonBattle.enemyPokemon().maxHealth(),
                            name: DungeonBattle.enemyPokemon().name()
                        };
                    }
                }
                return { inBattle: false };
            """)
            
            if battle_state and battle_state.get('inBattle'):
                self.log(f"Info combat alternative: {battle_state.get('name')} - "
                        f"{battle_state.get('currentHP')}/{battle_state.get('maxHP')} HP")
                return True
        except:
            pass
        
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