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
            self.log("Exploration du donjon...")
            
            # Variables pour suivre l'exploration
            exploration_attempts = 0
            max_exploration_attempts = 150
            found_boss = False
            last_action_time = time.time()
            last_state = None
            stuck_counter = 0
            time_since_new_tile = time.time()
            
            while exploration_attempts < max_exploration_attempts and self.running:
                current_time = time.time()
                
                # Vérifier l'état actuel du jeu
                current_state = self.check_game_state()
                
                # Si l'état n'a pas changé après un certain temps, nous pourrions être bloqués
                if current_state == last_state and (current_time - last_action_time) > 3:
                    stuck_counter += 1
                    self.log(f"Potentiellement bloqué dans l'état '{current_state}' pendant {int(current_time - last_action_time)}s (compteur: {stuck_counter})")
                    
                    # Si nous semblons bloqués trop longtemps, essayer de réinitialiser l'état
                    if stuck_counter >= 3:
                        self.log("Tentative de déblocage...")
                        
                        # Différentes stratégies selon l'état
                        if current_state == "exploring":
                            # Essayer d'utiliser directement l'API JavaScript pour une exploration complète
                            try:
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
                            except Exception as e:
                                self.log(f"Erreur lors du déblocage: {str(e)}")
                        
                        elif current_state == "battle":
                            # Forcer une attaque via JavaScript
                            self.driver.execute_script(
                                "if (typeof DungeonBattle !== 'undefined') { DungeonBattle.clickAttack(); }"
                            )
                            self.log("Forçage d'une attaque via JavaScript")
                        
                        elif current_state == "unknown":
                            # Vérifier si nous sommes sortis du donjon
                            try:
                                if self.is_element_clickable("button.btn[onclick*='DungeonRunner.initializeDungeon']"):
                                    self.log("Donjon terminé ou fermé, retour à la sélection de donjon")
                                    return True  # Considérer comme terminé
                            except:
                                pass
                        
                        # Réinitialiser le compteur
                        stuck_counter = 0
                        last_action_time = current_time
                
                # Traiter l'état actuel
                if current_state == "battle":
                    self.handle_battle()
                    last_action_time = current_time
                    last_state = current_state
                
                elif current_state == "chest":
                    self.handle_chest()
                    last_action_time = current_time
                    last_state = current_state
                    # Un coffre a été trouvé, donc on a fait un progrès
                    time_since_new_tile = current_time
                
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
                    # Utiliser notre nouvel algorithme de pathfinding pour trouver le prochain mouvement optimal
                    next_move = self.find_next_move()
                    
                    if next_move:
                        # Enregistrer l'état de la carte avant le clic (pour vérifier les progrès)
                        visible_tiles_count = len(self.get_visible_tiles())
                        
                        # Exécuter le mouvement
                        move_type = next_move["type"]
                        self.log(f"Mouvement optimisé: {move_type}")
                        
                        # Cliquer sur l'élément
                        self.driver.execute_script("arguments[0].click();", next_move["element"])
                        
                        # Attendre un court instant pour laisser le jeu réagir
                        # Ajuster le temps d'attente selon le type de case
                        if "empty" in move_type or "visited" in move_type:
                            time.sleep(0.1)  # Très court pour les cases vides ou déjà visitées
                        else:
                            time.sleep(0.3)  # Un peu plus long pour les autres types
                        
                        # Vérifier si l'état a changé
                        new_state = self.check_game_state()
                        if new_state != "exploring":
                            self.log(f"État changé après le clic: {new_state}")
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
                                
                                # Si aucun progrès depuis longtemps, essayer quelque chose de différent
                                if (current_time - time_since_new_tile) > 10:
                                    self.log("Aucun progrès depuis longtemps, tentative d'exploration JavaScript")
                                    try:
                                        # Utiliser JavaScript pour explorer la carte entière
                                        self.driver.execute_script("""
                                            if (typeof DungeonRunner !== 'undefined' && DungeonRunner.map) {
                                                var board = DungeonRunner.map.board()[DungeonRunner.map.playerPosition().floor];
                                                for (var y = 0; y < board.length; y++) {
                                                    for (var x = 0; x < board[y].length; x++) {
                                                        // Si la case n'est pas visitée, essayer de s'y déplacer
                                                        if (!board[y][x].isVisited) {
                                                            try {
                                                                DungeonRunner.map.moveToCoordinates(x, y);
                                                                return; // Sortir si on a trouvé
                                                            } catch (e) {}
                                                        }
                                                    }
                                                }
                                            }
                                        """)
                                        time_since_new_tile = current_time  # Réinitialiser le timer
                                    except:
                                        pass
                    else:
                        # Si aucun mouvement optimisé n'est trouvé, revenir à la méthode standard
                        # Trouver d'abord la position du joueur
                        player_position = self.find_player_position()
                        
                        if player_position:
                            player_x, player_y = player_position
                            
                            # Obtenir les cases adjacentes disponibles
                            adjacent_tiles = self.get_adjacent_tiles(player_x, player_y)
                            
                            if adjacent_tiles:
                                # Choisir la première case (priorité aux coffres/boss)
                                tile_to_click = adjacent_tiles[0]
                                
                                # Enregistrer l'état de la carte avant le clic
                                visible_tiles_count = len(self.get_visible_tiles())
                                
                                # Cliquer sur la case adjacente
                                class_name = tile_to_click.get_attribute("class")
                                self.log(f"Clic sur une case adjacente ({class_name})")
                                self.driver.execute_script("arguments[0].click();", tile_to_click)
                                
                                # Ajuster le temps d'attente selon le type de case
                                if "empty" in class_name or "visited" in class_name:
                                    time.sleep(0.1)  # Très court pour les cases vides ou déjà visitées
                                else:
                                    time.sleep(0.3)  # Un peu plus long pour les autres types
                                
                                # Vérifier si l'état a changé
                                new_state = self.check_game_state()
                                if new_state != "exploring":
                                    self.log(f"État changé après le clic: {new_state}")
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
                                self.log("Aucune case adjacente disponible")
                                
                                # Si aucune case adjacente, tenter une exploration JavaScript
                                try:
                                    self.driver.execute_script("""
                                        if (typeof DungeonRunner !== 'undefined' && DungeonRunner.map) {
                                            var visited = DungeonRunner.map.board()[DungeonRunner.map.playerPosition().floor]
                                                .flat()
                                                .filter(cell => cell.isVisited);
                                            
                                            if (visited.length > 0) {
                                                var randomVisited = visited[Math.floor(Math.random() * visited.length)];
                                                DungeonRunner.map.moveToCoordinates(randomVisited.x, randomVisited.y);
                                            }
                                        }
                                    """)
                                    self.log("Déplacement vers une case visitée aléatoire via JavaScript")
                                    last_action_time = current_time
                                except Exception as e:
                                    self.log(f"Erreur lors du déplacement JavaScript: {str(e)}")
                        else:
                            self.log("Position du joueur introuvable")
                
                elif current_state == "unknown" or current_state == "error":
                    # Vérifier si nous sommes sortis du donjon
                    try:
                        if self.is_element_clickable("button.btn[onclick*='DungeonRunner.initializeDungeon']", timeout=1):
                            self.log("Donjon terminé ou fermé, retour à la sélection de donjon")
                            return True  # Considérer comme terminé
                    except:
                        pass
                    
                    self.log(f"État indéterminé ({current_state}), attente...")
                    time.sleep(1)
                    last_action_time = current_time  # Réinitialiser pour éviter de bloquer trop longtemps
                
                exploration_attempts += 1
                
                # Pause courte entre les vérifications d'état
                time.sleep(0.1)  # Réduit pour accélérer l'exploration
            
            if exploration_attempts >= max_exploration_attempts:
                self.log("Exploration trop longue, abandon du donjon.")
                return False
            
            return found_boss
            
        except Exception as e:
            self.log(f"Erreur pendant l'exploration du donjon: {str(e)}")
            return False