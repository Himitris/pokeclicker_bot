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
        """Explorer le donjon jusqu'à trouver et battre le boss en utilisant l'algorithme de pathfinding optimisé"""
        try:
            self.log("Exploration du donjon avec l'algorithme optimisé...")
            
            # Variables pour suivre l'exploration
            exploration_attempts = 0
            max_exploration_attempts = 200  # Augmenté pour donner plus de temps aux donjons complexes
            found_boss = False
            last_action_time = time.time()
            last_state = None
            stuck_counter = 0
            time_since_new_tile = time.time()
            consecutive_failures = 0
            
            while exploration_attempts < max_exploration_attempts and self.running:
                current_time = time.time()
                
                # Vérifier l'état actuel du jeu
                current_state = self.check_game_state()
                
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
                
                # Traiter l'état actuel
                if current_state == "battle":
                    self.handle_battle()
                    last_action_time = current_time
                    last_state = current_state
                    consecutive_failures = 0
                
                elif current_state == "chest":
                    self.handle_chest()
                    last_action_time = current_time
                    last_state = current_state
                    time_since_new_tile = current_time
                    consecutive_failures = 0
                
                elif current_state == "boss":
                    self.log("Boss trouvé!")
                    found_boss = True
                    result = self.handle_boss_fight()
                    
                    if result:
                        self.log("Boss vaincu! Donjon terminé!")
                        return True
                    else:
                        self.log("Échec lors du combat contre le boss.")
                        return False
                
                elif current_state == "exploring":
                    # Utiliser notre algorithme de pathfinding amélioré
                    next_move = self.find_next_move()
                    
                    if next_move:
                        consecutive_failures = 0
                        # Enregistrer l'état de la carte avant le mouvement
                        visible_tiles_count = len(self.get_visible_tiles())
                        
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
                            # Vérifier si la carte a été modifiée (nouvelles cases visibles)
                            new_visible_tiles_count = len(self.get_visible_tiles())
                            if new_visible_tiles_count > visible_tiles_count:
                                self.log(f"Carte modifiée: {visible_tiles_count} -> {new_visible_tiles_count} cases visibles")
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
                    self.log("Aucun progrès depuis 15 secondes, tentative de réinitialisation...")
                    self.force_exploration_with_javascript()
                    time_since_new_tile = current_time
                
                # Pause courte entre les vérifications d'état
                time.sleep(0.1)
            
            if exploration_attempts >= max_exploration_attempts:
                self.log("Exploration trop longue, abandon du donjon.")
                return False
            
            return found_boss
            
        except Exception as e:
            self.log(f"Erreur pendant l'exploration du donjon: {str(e)}")
            return False

    def attempt_to_unstuck(self, current_state):
        """Tentative de déblocage selon l'état actuel"""
        try:
            if current_state == "exploring":
                # Essayer d'utiliser directement l'API JavaScript pour explorer dans une direction aléatoire
                self.driver.execute_script("""
                    if (typeof DungeonRunner !== 'undefined' && DungeonRunner.map) {
                        // Explorer dans une direction aléatoire
                        var directions = [[0,-1], [1,0], [0,1], [-1,0]];
                        directions.sort(() => Math.random() - 0.5);
                        
                        var pos = DungeonRunner.map.playerPosition();
                        for (var i = 0; i < directions.length; i++) {
                            try {
                                var newX = pos.x + directions[i][0];
                                var newY = pos.y + directions[i][1];
                                DungeonRunner.map.moveToCoordinates(newX, newY);
                                break;
                            } catch(e) {}
                        }
                    }
                """)
                self.log("Tentative de mouvement aléatoire via JavaScript")
            
            elif current_state == "battle":
                # Forcer une attaque via JavaScript
                self.driver.execute_script(
                    "if (typeof DungeonBattle !== 'undefined') { DungeonBattle.clickAttack(); }"
                )
                self.log("Forçage d'une attaque via JavaScript")
            
            elif current_state == "unknown":
                # Essayer de fermer tout dialogue ouvert
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".modal button.close, .modal .btn-primary")
                    if close_buttons:
                        for button in close_buttons:
                            self.driver.execute_script("arguments[0].click();", button)
                            self.log("Tentative de fermeture d'un dialogue")
                except:
                    pass
                
                # Vérifier si nous sommes sortis du donjon
                self.check_if_dungeon_completed()
        
        except Exception as e:
            self.log(f"Erreur lors de la tentative de déblocage: {str(e)}")

    def check_if_dungeon_completed(self):
        """Vérifier si nous sommes sortis du donjon"""
        try:
            if self.is_element_clickable("button.btn[onclick*='DungeonRunner.initializeDungeon']", timeout=1):
                return True
        except:
            pass
        return False

    def force_exploration_with_javascript(self):
        """Utiliser JavaScript pour explorer la carte de manière plus agressive, en évitant les cases déjà visitées"""
        try:
            # Exploration optimisée pour éviter les cases déjà visitées
            self.driver.execute_script("""
                if (typeof DungeonRunner !== 'undefined' && DungeonRunner.map) {
                    // Récupérer la carte complète
                    var board = DungeonRunner.map.board()[DungeonRunner.map.playerPosition().floor];
                    var visitedPositions = [];
                    var playerPos = DungeonRunner.map.playerPosition();
                    
                    // Collecter toutes les positions visitées adjacentes à des cases non visitées
                    for (var y = 0; y < board.length; y++) {
                        for (var x = 0; x < board[y].length; x++) {
                            if (board[y][x].isVisited) {
                                // Vérifier si cette case visitée a des voisins non visités
                                var directions = [[0,-1], [1,0], [0,1], [-1,0]];
                                var hasUnvisitedNeighbor = false;
                                
                                for (var d = 0; d < directions.length; d++) {
                                    var adjX = x + directions[d][0];
                                    var adjY = y + directions[d][1];
                                    
                                    if (adjY >= 0 && adjY < board.length && 
                                        adjX >= 0 && adjX < board[adjY].length) {
                                        
                                        if (!board[adjY][adjX].isVisited && !board[adjY][adjX].isHidden) {
                                            hasUnvisitedNeighbor = true;
                                            break;
                                        }
                                    }
                                }
                                
                                if (hasUnvisitedNeighbor) {
                                    visitedPositions.push({x: x, y: y, 
                                                        distToPlayer: Math.abs(x - playerPos.x) + Math.abs(y - playerPos.y)});
                                }
                            }
                        }
                    }
                    
                    // Trier les positions par distance au joueur (pour éviter de traverser tout le donjon)
                    visitedPositions.sort(function(a, b) {
                        return a.distToPlayer - b.distToPlayer;
                    });
                    
                    // Pour chaque position visitée, vérifier les cases adjacentes non visitées
                    for (var i = 0; i < visitedPositions.length; i++) {
                        var pos = visitedPositions[i];
                        var directions = [[0,-1], [1,0], [0,1], [-1,0]];
                        
                        // Mélanger les directions pour ne pas favoriser toujours le même côté
                        directions.sort(() => Math.random() - 0.5);
                        
                        for (var j = 0; j < directions.length; j++) {
                            var newX = pos.x + directions[j][0];
                            var newY = pos.y + directions[j][1];
                            
                            // Vérifier si la position est valide
                            if (newY >= 0 && newY < board.length && 
                                newX >= 0 && newX < board[newY].length) {
                                
                                // Si la case n'est pas visitée et est visible
                                if (!board[newY][newX].isVisited && !board[newY][newX].isHidden) {
                                    try {
                                        // Si nous ne sommes pas déjà sur la case d'accès, s'y déplacer d'abord
                                        if (playerPos.x !== pos.x || playerPos.y !== pos.y) {
                                            DungeonRunner.map.moveToCoordinates(pos.x, pos.y);
                                        }
                                        
                                        // Puis se déplacer vers la case non visitée
                                        setTimeout(function() {
                                            try {
                                                DungeonRunner.map.moveToCoordinates(newX, newY);
                                            } catch (e) {}
                                        }, 100);
                                        
                                        return; // Sortir si on a trouvé
                                    } catch (e) {}
                                }
                            }
                        }
                    }
                    
                    // En dernier recours, chercher n'importe quelle case non visitée
                    for (var y = 0; y < board.length; y++) {
                        for (var x = 0; x < board[y].length; x++) {
                            if (!board[y][x].isVisited && !board[y][x].isHidden) {
                                try {
                                    DungeonRunner.map.moveToCoordinates(x, y);
                                    return;
                                } catch (e) {}
                            }
                        }
                    }
                }
            """)
            self.log("Exploration forcée via JavaScript")
        except Exception as e:
            self.log(f"Erreur lors de l'exploration forcée: {str(e)}")