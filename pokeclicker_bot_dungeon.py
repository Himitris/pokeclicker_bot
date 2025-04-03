import time
import random
import threading
from selenium.webdriver.common.by import By

from pokeclicker_bot_dungeon_base import PokeclickerBotDungeonBase
from pokeclicker_bot_dungeon_navigation import PokeclickerBotDungeonNavigation
from pokeclicker_bot_dungeon_combat import PokeclickerBotDungeonCombat
from pokeclicker_bot_dungeon_pathfinding import PokeclickerBotDungeonPathfinding


class PokeclickerBotDungeon(PokeclickerBotDungeonBase, PokeclickerBotDungeonNavigation, PokeclickerBotDungeonCombat, PokeclickerBotDungeonPathfinding):
    """
    Classe principale pour l'automatisation des donjons. 
    Hérite des fonctionnalités de base, de navigation et de combat.
    """
    
    def run_dungeon(self):
        """Fonction pour automatiser l'exploration d'un donjon"""
        self.running = True
        self.start_time = time.time()
        self.clicks = 0
        self.dungeons_completed = 0
        self.target_dungeons = self.dungeons_to_run
        
        self.log(f"========== AUTOMATISATION DE DONJON DÉMARRÉE ==========")
        self.log(f"Nombre de donjons à compléter: {self.target_dungeons if self.target_dungeons > 0 else 'Illimité'}")
        self.update_status("Donjons en cours")
        
        # Boucle principale pour exécuter plusieurs donjons
        while self.running and (self.target_dungeons == 0 or self.dungeons_completed < self.target_dungeons):
            try:
                # 1. Démarrer un nouveau donjon
                self.log(f"Tentative de démarrage du donjon #{self.dungeons_completed + 1}...")
                if not self.start_dungeon():
                    self.log("Impossible de démarrer le donjon. Attente de 5 secondes avant de réessayer...")
                    time.sleep(5)
                    continue
                
                # 2. Explorer le donjon jusqu'à la fin
                if self.explore_dungeon():
                    self.dungeons_completed += 1
                    self.log(f"Donjon #{self.dungeons_completed} terminé avec succès!")
                    self.update_status(f"Donjons: {self.dungeons_completed}/{self.target_dungeons if self.target_dungeons > 0 else '∞'}")
                else:
                    self.log("Échec lors de l'exploration du donjon.")
                
                # 3. Court délai avant de redémarrer
                time.sleep(2)
                
            except Exception as e:
                self.log(f"Erreur pendant l'automatisation du donjon: {str(e)}")
                time.sleep(5)
        
        elapsed_time = int(time.time() - self.start_time)
        self.log(f"========== AUTOMATISATION DE DONJON TERMINÉE ==========")
        self.log(f"Donjons complétés: {self.dungeons_completed}")
        self.log(f"Durée totale: {elapsed_time} secondes")
        self.update_status("Donjons terminés")
    
    def explore_dungeon(self):
        """
        Explorer le donjon de manière stratégique et adaptive en fonction des différentes phases
        d'exploration jusqu'à trouver et battre le boss
        """
        try:
            self.log("Exploration du donjon avec l'algorithme optimisé...")
            
            # Variables pour suivre l'exploration
            exploration_start_time = time.time()
            exploration_attempts = 0
            max_exploration_attempts = 250  # Augmenté pour donner plus de temps aux donjons complexes
            found_boss = False
            last_action_time = time.time()
            last_state = None
            stuck_counter = 0
            time_since_new_tile = time.time()
            consecutive_failures = 0
            last_map_hash = ""
            
            # Statistiques d'exploration
            stats = {
                "chests_opened": 0,
                "enemies_defeated": 0,
                "tiles_explored": 0,
                "phase_changes": 0,
                "current_phase": "initial"
            }
            
            # Détecter le type de donjon pour adapter la stratégie
            dungeon_type = self.detect_dungeon_type()
            self.log(f"Type de donjon détecté: {dungeon_type['name']} (difficulté: {dungeon_type['difficulty']})")
            
            # Initialiser les valeurs en fonction du type de donjon
            min_chests_required = dungeon_type["min_chests"]
            exploration_timeout = 600  # 10 minutes par défaut
            if dungeon_type["difficulty"] == "hard":
                exploration_timeout = 900  # 15 minutes pour les donjons difficiles
                max_exploration_attempts = 350
            elif dungeon_type["difficulty"] == "easy":
                exploration_timeout = 300  # 5 minutes pour les donjons faciles
                max_exploration_attempts = 150
            
            self.log(f"Stratégie adaptée: minimum {min_chests_required} coffres requis, timeout: {exploration_timeout/60:.1f} minutes")
            
            # Boucle principale d'exploration
            while exploration_attempts < max_exploration_attempts and self.running:
                current_time = time.time()
                
                # Vérifier le timeout global
                if current_time - exploration_start_time > exploration_timeout:
                    self.log(f"Exploration trop longue ({int(current_time - exploration_start_time)}s), abandon du donjon.")
                    return False
                
                # Vérifier l'état actuel du jeu
                current_state = self.check_game_state()
                
                # Analyser la carte pour avoir des informations à jour
                dungeon_map = self.analyze_dungeon_map()
                if dungeon_map:
                    # Calculer un "hash" simple de l'état de la carte pour détecter les changements
                    visible_count = len(dungeon_map["visible_tiles"])
                    visited_count = len(dungeon_map["visited_tiles"])
                    chests_count = len(dungeon_map["chests"])
                    current_map_hash = f"{visible_count}_{visited_count}_{chests_count}"
                    
                    # Si la carte a changé depuis la dernière vérification
                    if current_map_hash != last_map_hash:
                        self.log(f"Carte mise à jour: {visible_count} cases visibles, {visited_count} visitées, {chests_count} coffres")
                        time_since_new_tile = current_time
                        last_map_hash = current_map_hash
                    
                    # Déterminer la phase d'exploration actuelle
                    exploration_phase = self.determine_exploration_phase(dungeon_map)
                    
                    # Si la phase a changé, l'enregistrer
                    if exploration_phase != stats["current_phase"]:
                        stats["phase_changes"] += 1
                        stats["current_phase"] = exploration_phase
                        self.log(f"Changement de phase d'exploration: {exploration_phase}")
                        
                        # Réinitialiser certains compteurs lors d'un changement de phase
                        consecutive_failures = 0
                        stuck_counter = 0
                
                # Vérifier si nous sommes bloqués dans le même état
                if current_state == last_state and (current_time - last_action_time) > 3:
                    stuck_counter += 1
                    self.log(f"Potentiellement bloqué dans l'état '{current_state}' pendant {int(current_time - last_action_time)}s (compteur: {stuck_counter})")
                    
                    # Si nous sommes bloqués trop longtemps, essayer de débloquer
                    if stuck_counter >= 3:
                        self.log("Tentative de déblocage...")
                        self.attempt_to_unstuck(current_state)
                        
                        # Augmenter la force de l'intervention à chaque blocage
                        if stuck_counter >= 5:
                            self.log("Blocage persistant détecté, utilisation de l'exploration JavaScript avancée")
                            self.force_exploration_with_javascript()
                        
                        # Réinitialiser les compteurs
                        stuck_counter = 0
                        last_action_time = current_time
                        time_since_new_tile = current_time
                
                # Traiter l'état actuel avec des stratégies optimisées pour chaque état
                if current_state == "battle":
                    battle_result = self.handle_battle()
                    if battle_result:
                        stats["enemies_defeated"] += 1
                    last_action_time = current_time
                    last_state = current_state
                    consecutive_failures = 0
                
                elif current_state == "chest":
                    chest_result = self.handle_chest()
                    if chest_result:
                        stats["chests_opened"] += 1
                    last_action_time = current_time
                    last_state = current_state
                    time_since_new_tile = current_time
                    consecutive_failures = 0
                    
                    # Vérifier si nous avons ouvert suffisamment de coffres pour révéler le boss
                    # en fonction du type de donjon
                    if stats["chests_opened"] >= min_chests_required:
                        self.log(f"Nombre minimum de coffres atteint ({stats['chests_opened']}/{min_chests_required}), recherche du boss prioritaire")
                
                elif current_state == "boss":
                    self.log("Boss trouvé!")
                    found_boss = True
                    result = self.handle_boss_fight()
                    
                    if result:
                        elapsed_time = int(current_time - exploration_start_time)
                        self.log(f"Boss vaincu! Donjon terminé en {elapsed_time}s!")
                        self.log(f"Statistiques: {stats['chests_opened']} coffres, {stats['enemies_defeated']} ennemis, {stats['tiles_explored']} cases")
                        return True
                    else:
                        self.log("Échec lors du combat contre le boss.")
                        return False
                
                elif current_state == "exploring":
                    # Utiliser l'algorithme de pathfinding optimisé en fonction de la phase
                    next_move = None
                    
                    if dungeon_map:
                        # Adapter la stratégie selon la phase d'exploration
                        if exploration_phase == "boss_visible":
                            self.log("Phase Boss: Optimisation du chemin vers le boss")
                            next_move = self.find_optimal_path_to_boss(dungeon_map)
                        elif exploration_phase == "chests_visible":
                            self.log("Phase Coffres: Recherche du coffre le plus stratégique")
                            next_move = self.find_strategic_chest_path(dungeon_map)
                        else:
                            self.log("Phase Exploration: Recherche efficace de nouvelles zones")
                            next_move = self.find_efficient_exploration_move(dungeon_map)
                    
                    if next_move:
                        consecutive_failures = 0
                        # Enregistrer l'état de la carte avant le mouvement
                        visible_tiles_count = len(dungeon_map["visible_tiles"]) if dungeon_map else 0
                        
                        # Exécuter le mouvement
                        move_type = next_move.get("type", "unknown")
                        self.log(f"Mouvement optimisé: {move_type}")
                        
                        # Si le mouvement est direct, cliquer directement sur l'élément
                        if next_move.get("direct", False):
                            self.driver.execute_script("arguments[0].click();", next_move["element"])
                            
                            # Si ce mouvement a un objectif suivant, le traiter
                            if "next_target" in next_move:
                                # Attendre un court instant pour le changement d'état
                                time.sleep(0.3)
                                
                                # Vérifier que l'état n'a pas changé (combat, coffre, etc.)
                                new_state = self.check_game_state()
                                if new_state == "exploring":
                                    # Cliquer sur la cible suivante
                                    self.log(f"Clique sur la cible suivante...")
                                    target = next_move["next_target"]
                                    self.driver.execute_script("arguments[0].click();", target["element"])
                        else:
                            # Pour les chemins plus complexes, suivre étape par étape
                            if "path" in next_move and next_move["path"]:
                                next_x, next_y = next_move["path"][0]
                                next_element = dungeon_map["rows"][next_y][next_x]["element"]
                                self.driver.execute_script("arguments[0].click();", next_element)
                        
                        # Attendre un court instant pour laisser le jeu réagir
                        # Ajuster le temps d'attente selon le type de mouvement
                        if "empty" in move_type or "visited" in move_type:
                            time.sleep(0.1)  # Court pour les cases simples
                        else:
                            time.sleep(0.3)  # Plus long pour les actions importantes
                        
                        # Vérifier si l'état a changé
                        new_state = self.check_game_state()
                        if new_state != "exploring":
                            self.log(f"État changé après le mouvement: {new_state}")
                            last_action_time = current_time
                            last_state = new_state
                            time_since_new_tile = current_time
                        else:
                            # Vérifier si la carte a été modifiée
                            new_dungeon_map = self.analyze_dungeon_map()
                            if new_dungeon_map:
                                new_visible_tiles_count = len(new_dungeon_map["visible_tiles"])
                                if new_visible_tiles_count > visible_tiles_count:
                                    tiles_difference = new_visible_tiles_count - visible_tiles_count
                                    stats["tiles_explored"] += tiles_difference
                                    self.log(f"Carte modifiée: +{tiles_difference} nouvelles cases visibles")
                                    last_action_time = current_time
                                    time_since_new_tile = current_time
                                else:
                                    self.log("L'action n'a pas modifié la carte")
                                    last_action_time = current_time
                    else:
                        consecutive_failures += 1
                        self.log(f"Impossible de trouver un mouvement optimal (échecs consécutifs: {consecutive_failures})")
                        
                        # Si plusieurs échecs consécutifs, essayer une approche plus agressive
                        if consecutive_failures >= 3:
                            self.log("Tentative d'exploration avec JavaScript...")
                            self.force_exploration_with_javascript()
                            consecutive_failures = 0
                            time_since_new_tile = current_time
                
                elif current_state == "unknown" or current_state == "error":
                    # Vérifier si nous sommes sortis du donjon
                    if self.check_if_dungeon_completed():
                        self.log("Donjon terminé ou fermé, retour à la sélection de donjon")
                        return True
                    
                    self.log(f"État indéterminé ({current_state}), attente...")
                    time.sleep(1)
                    last_action_time = current_time
                
                exploration_attempts += 1
                
                # Si aucun progrès depuis longtemps, essayer une approche différente
                if (current_time - time_since_new_tile) > 15:
                    self.log(f"Aucun progrès depuis {int(current_time - time_since_new_tile)}s, tentative de réinitialisation...")
                    
                    # Stratégies adaptatives en fonction du temps passé sans progrès
                    if (current_time - time_since_new_tile) > 40:
                        # Blocage très long - tentative de réinitialisation complète
                        self.log("Blocage majeur détecté, tentative de réinitialisation complète...")
                        self.try_complete_reset()
                    else:
                        # Blocage normal - exploration forcée
                        self.force_exploration_with_javascript()
                    
                    time_since_new_tile = current_time
                
                # Pause courte entre les vérifications d'état
                time.sleep(0.1)
            
            # Si on a dépassé le nombre d'essais maximum, abandonner
            if exploration_attempts >= max_exploration_attempts:
                self.log("Trop de tentatives d'exploration, abandon du donjon.")
                return False
            
            return found_boss
            
        except Exception as e:
            self.log(f"Erreur pendant l'exploration du donjon: {str(e)}")
            return False

    def try_complete_reset(self):
        """
        Tentative de réinitialisation complète en cas de blocage majeur
        """
        try:
            # 1. Essayer de fermer tous les dialogues ou modals ouverts
            try:
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".modal button.close, .modal .btn-primary")
                if close_buttons:
                    for button in close_buttons:
                        self.driver.execute_script("arguments[0].click();", button)
                        self.log("Fermeture d'un dialogue")
                        time.sleep(0.3)
            except:
                pass
            
            # 2. Essayer d'utiliser l'API JavaScript pour réinitialiser l'exploration
            try:
                self.driver.execute_script("""
                    // Tenter de réinitialiser les états internes du jeu
                    if (typeof DungeonRunner !== 'undefined') {
                        // Forcer une mise à jour de la carte
                        if (DungeonRunner.map && DungeonRunner.map.updateVisibility) {
                            DungeonRunner.map.updateVisibility();
                        }
                        
                        // Si nous sommes dans un combat, tenter de le terminer
                        if (typeof DungeonBattle !== 'undefined' && DungeonBattle.catching && DungeonBattle.catching()) {
                            DungeonBattle.forfeit();
                        }
                    }
                """)
                self.log("Tentative de réinitialisation via JavaScript")
            except:
                pass
            
            # 3. Tenter de retourner à la case de départ si possible
            try:
                dungeon_map = self.analyze_dungeon_map()
                if dungeon_map and dungeon_map["player_pos"]:
                    # Trouver la case la plus proche du point de départ
                    start_positions = [(0, 0), (0, 1), (1, 0)]
                    for start_x, start_y in start_positions:
                        if (start_x, start_y) in dungeon_map["visited_tiles"]:
                            self.log(f"Tentative de retour au point de départ ({start_x}, {start_y})")
                            player_x, player_y = dungeon_map["player_pos"]
                            
                            # Si nous pouvons cliquer directement
                            if self.is_directly_accessible(player_x, player_y, start_x, start_y, dungeon_map):
                                start_element = dungeon_map["rows"][start_y][start_x]["element"]
                                self.driver.execute_script("arguments[0].click();", start_element)
                                break
            except:
                pass
            
            # 4. En dernier recours, exploration aléatoire forcée
            self.force_random_exploration_with_javascript()
            
        except Exception as e:
            self.log(f"Erreur lors de la réinitialisation complète: {str(e)}")

    def force_random_exploration_with_javascript(self):
        """
        Force une exploration aléatoire via JavaScript pour sortir des situations de blocage extrêmes
        """
        try:
            self.driver.execute_script("""
                if (typeof DungeonRunner !== 'undefined' && DungeonRunner.map) {
                    // Explorer dans des directions complètement aléatoires
                    function tryRandomMove() {
                        var board = DungeonRunner.map.board();
                        if (!board || !board.length) return;
                        
                        var floorLevel = DungeonRunner.map.playerPosition().floor || 0;
                        var height = board[floorLevel].length;
                        var width = board[floorLevel][0].length;
                        
                        // Générer 10 positions aléatoires et essayer de s'y déplacer
                        for (var i = 0; i < 10; i++) {
                            var randX = Math.floor(Math.random() * width);
                            var randY = Math.floor(Math.random() * height);
                            
                            try {
                                // Tenter de se déplacer vers cette position
                                DungeonRunner.map.moveToCoordinates(randX, randY);
                                break;
                            } catch(e) {
                                // Ignorer et continuer
                            }
                        }
                    }
                    
                    // Essayer plusieurs fois
                    for (var attempt = 0; attempt < 3; attempt++) {
                        setTimeout(tryRandomMove, attempt * 300);
                    }
                }
            """)
            self.log("Exploration aléatoire forcée via JavaScript")
        except Exception as e:
            self.log(f"Erreur lors de l'exploration aléatoire forcée: {str(e)}")

    def run_dungeon(self):
        """Fonction principale pour automatiser l'exploration d'un donjon avec gestion avancée"""
        self.running = True
        self.start_time = time.time()
        self.clicks = 0
        self.dungeons_completed = 0
        self.target_dungeons = self.dungeons_to_run
        
        # Initialiser les statistiques spécifiques aux donjons
        self.reset_dungeon_stats()
        
        self.log(f"========== AUTOMATISATION DE DONJON DÉMARRÉE ==========")
        self.log(f"Nombre de donjons à compléter: {self.target_dungeons if self.target_dungeons > 0 else 'Illimité'}")
        self.update_status("Donjons en cours")
        
        # Boucle principale pour exécuter plusieurs donjons
        while self.running and (self.target_dungeons == 0 or self.dungeons_completed < self.target_dungeons):
            try:
                dungeon_start_time = time.time()
                
                # 1. Démarrer un nouveau donjon
                self.log(f"Tentative de démarrage du donjon #{self.dungeons_completed + 1}...")
                start_result = self.start_dungeon()
                
                if not start_result:
                    self.log("Impossible de démarrer le donjon. Attente de 5 secondes avant de réessayer...")
                    
                    # Vérifier s'il y a un problème connu qui empêcherait le démarrage
                    reason = self.check_dungeon_start_failure()
                    if reason:
                        self.log(f"Raison de l'échec: {reason}")
                        
                        # Si nous n'avons pas assez de jetons, attendre plus longtemps
                        if "tokens" in reason.lower():
                            self.log("Attente prolongée pour régénération des jetons...")
                            time.sleep(60)  # Attendre une minute
                        elif "unlock" in reason.lower():
                            self.log("Ce donjon n'est pas encore débloqué, passage au suivant...")
                            # Essayer de sélectionner un autre donjon
                            if self.select_next_available_dungeon():
                                continue
                    
                    time.sleep(5)
                    continue
                
                # 2. Explorer le donjon jusqu'à la fin
                explore_result = self.explore_dungeon()
                dungeon_duration = int(time.time() - dungeon_start_time)
                
                if explore_result:
                    self.dungeons_completed += 1
                    self.log(f"Donjon #{self.dungeons_completed} terminé avec succès en {dungeon_duration}s!")
                    
                    # Mettre à jour les statistiques
                    self.log(f"Coffres ouverts: {self.chests_found}, Ennemis vaincus: {self.enemies_defeated}")
                    self.total_chests_found += self.chests_found
                    self.total_enemies_defeated += self.enemies_defeated
                    
                    # Mettre à jour le statut d'affichage
                    if self.target_dungeons > 0:
                        progress_percentage = (self.dungeons_completed / self.target_dungeons) * 100
                        self.update_status(f"Donjons: {self.dungeons_completed}/{self.target_dungeons} ({progress_percentage:.0f}%)")
                    else:
                        self.update_status(f"Donjons: {self.dungeons_completed} (∞)")
                else:
                    self.log(f"Échec lors de l'exploration du donjon après {dungeon_duration}s.")
                    # Tenter de fermer les dialogues pour revenir à l'écran de sélection
                    self.exit_dungeon_after_failure()
                
                # 3. Court délai avant de redémarrer
                time.sleep(2)
                
                # Réinitialiser les statistiques pour le prochain donjon
                self.reset_dungeon_stats()
                
            except Exception as e:
                self.log(f"Erreur pendant l'automatisation du donjon: {str(e)}")
                time.sleep(5)
            
        elapsed_time = int(time.time() - self.start_time)
        self.log(f"========== AUTOMATISATION DE DONJON TERMINÉE ==========")
        self.log(f"Donjons complétés: {self.dungeons_completed}")
        self.log(f"Total coffres: {self.total_chests_found}, Total ennemis: {self.total_enemies_defeated}")
        self.log(f"Durée totale: {elapsed_time} secondes")
        self.update_status("Donjons terminés")

    def reset_dungeon_stats(self):
        """Réinitialiser les statistiques pour un nouveau donjon"""
        self.chests_found = 0
        self.rare_chests_found = 0
        self.enemies_defeated = 0
        self.boss_attempts = 0
        
        # Statistiques globales si elles n'existent pas encore
        if not hasattr(self, 'total_chests_found'):
            self.total_chests_found = 0
            self.total_enemies_defeated = 0
            self.total_boss_encounters = 0

    def check_dungeon_start_failure(self):
        """Vérifier la raison de l'échec au démarrage d'un donjon"""
        try:
            # Vérifier s'il y a un message d'erreur visible
            error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".modal-body, button.disabled[onclick*='initializeDungeon']")
            
            for element in error_messages:
                text = element.text
                if "token" in text.lower():
                    return "Not enough dungeon tokens"
                elif "unlock" in text.lower() or "locked" in text.lower():
                    return "Dungeon not unlocked yet"
                elif element.get_attribute("disabled") == "true":
                    return "Button disabled"
            
            return "Unknown reason"
        except:
            return "Could not determine reason"

    def select_next_available_dungeon(self):
        """Essayer de sélectionner le prochain donjon disponible"""
        try:
            # Chercher tous les boutons de donjon
            dungeon_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.dungeon-button:not(.disabled)")
            
            if dungeon_buttons:
                # Cliquer sur le premier donjon disponible
                self.driver.execute_script("arguments[0].click();", dungeon_buttons[0])
                self.log(f"Sélection d'un autre donjon disponible")
                return True
            else:
                self.log("Aucun donjon disponible")
                return False
        except Exception as e:
            self.log(f"Erreur lors de la sélection d'un autre donjon: {str(e)}")
            return False

    def exit_dungeon_after_failure(self):
        """Tenter de sortir proprement d'un donjon après un échec"""
        try:
            # Fermer tous les dialogues possibles
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".modal button.close, .modal .btn-primary")
            if close_buttons:
                for button in close_buttons:
                    self.driver.execute_script("arguments[0].click();", button)
            
            # Tentative de forfait si on est bloqué en combat
            self.driver.execute_script("""
                if (typeof DungeonBattle !== 'undefined') {
                    try {
                        DungeonBattle.forfeit();
                    } catch(e) {}
                }
                
                // Essai de retour à l'écran principal
                if (typeof DungeonRunner !== 'undefined') {
                    try {
                        DungeonRunner.dungeonFinished();
                    } catch(e) {}
                }
            """)
            
            self.log("Tentative de sortie du donjon après échec")
        except Exception as e:
            self.log(f"Erreur lors de la sortie du donjon: {str(e)}")