import random
from selenium.webdriver.common.by import By

class PokeclickerBotDungeonNavigation:
    """
    Fonctionnalités de navigation dans le donjon
    Gère la détection des cases et le déplacement sur la carte
    """
    
    def find_player_position(self):
        """Trouver la position du joueur dans la grille du donjon"""
        try:
            # Rechercher la case avec la classe 'tile-player'
            player_tile = self.driver.find_element(By.CSS_SELECTOR, "td.tile-player")
            
            # Obtenir les coordonnées à partir de la structure du tableau
            # Trouver la ligne <tr> parent
            tr_parent = player_tile.find_element(By.XPATH, "./..")
            
            # Trouver l'index de la ligne (y)
            tbody = tr_parent.find_element(By.XPATH, "./..")
            all_rows = tbody.find_elements(By.TAG_NAME, "tr")
            y = next((i for i, row in enumerate(all_rows) if row == tr_parent), -1)
            
            # Trouver l'index de la colonne (x)
            all_cells = tr_parent.find_elements(By.TAG_NAME, "td")
            x = next((i for i, cell in enumerate(all_cells) if cell == player_tile), -1)
            
            # self.log(f"Position du joueur trouvée: x={x}, y={y}")
            return x, y
            
        except Exception as e:
            self.log(f"Erreur lors de la recherche de la position du joueur: {str(e)}")
            return None
    
    def get_adjacent_tiles(self, player_x, player_y):
        """Obtenir les cases adjacentes à la position du joueur"""
        try:
            # Définir une liste pour stocker les cases adjacentes avec leurs priorités
            adjacent_tiles = []
            
            # Définir les directions: haut, droite, bas, gauche
            directions = [
                (0, -1),  # haut
                (1, 0),   # droite
                (0, 1),   # bas
                (-1, 0)   # gauche
            ]
            
            # Trouver toutes les lignes
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.dungeon-board tr")
            
            for dx, dy in directions:
                try:
                    # Calculer les nouvelles coordonnées
                    new_x = player_x + dx
                    new_y = player_y + dy
                    
                    # Vérifier si les coordonnées sont valides
                    if new_y >= 0 and new_y < len(rows):
                        # Obtenir la ligne correspondante
                        row = rows[new_y]
                        
                        # Obtenir toutes les cellules de cette ligne
                        cells = row.find_elements(By.TAG_NAME, "td")
                        
                        if new_x >= 0 and new_x < len(cells):
                            # Obtenir la cellule adjacente
                            cell = cells[new_x]
                            
                            # Récupérer les classes de la cellule
                            class_attribute = cell.get_attribute("class")
                            
                            # Ne pas considérer les cases déjà visitées (sauf si c'est un boss ou un coffre)
                            if "tile-visited" in class_attribute and not ("tile-chest" in class_attribute or "tile-boss" in class_attribute):
                                continue
                                
                            # Définir la priorité en fonction du type de case
                            priority = 999  # Priorité par défaut (basse)
                            
                            if "tile-boss" in class_attribute:
                                priority = 1  # Priorité la plus haute pour le boss
                                adjacent_tiles.append({"cell": cell, "priority": priority, "type": "boss"})
                            elif "tile-chest" in class_attribute:
                                priority = 2  # Priorité haute pour les coffres
                                adjacent_tiles.append({"cell": cell, "priority": priority, "type": "chest"})
                            elif "tile-invisible" in class_attribute:
                                priority = 3  # Priorité pour les cases non découvertes
                                adjacent_tiles.append({"cell": cell, "priority": priority, "type": "undiscovered"})
                            
                except Exception as e:
                    self.log(f"Erreur lors de la vérification de la direction {dx},{dy}: {str(e)}")
                    continue
            
            # Trier les cases par priorité (du plus petit au plus grand nombre = priorité plus élevée)
            adjacent_tiles.sort(key=lambda x: x["priority"])
            
            # Extraire uniquement les cellules pour la compatibilité avec le code existant
            sorted_cells = [item["cell"] for item in adjacent_tiles]
            
            if sorted_cells:
                priority_info = ", ".join([f"{item['type']}" for item in adjacent_tiles[:3]])
                self.log(f"Trouvé {len(sorted_cells)} cases adjacentes accessibles. Priorités: {priority_info}")
            
            return sorted_cells
            
        except Exception as e:
            self.log(f"Erreur lors de la recherche des cases adjacentes: {str(e)}")
            return []

    def find_path_to_chest_or_boss(self):
        """Trouver un chemin vers un coffre ou le boss depuis n'importe quelle case visitée"""
        try:
            # 1. Identifier toutes les cases "coffres" et "boss" visibles
            all_chests = self.driver.find_elements(By.CSS_SELECTOR, "td.tile-chest:not(.tile-invisible)")
            boss_tiles = self.driver.find_elements(By.CSS_SELECTOR, "td.tile-boss:not(.tile-invisible)")
            
            # Créer une liste d'objectifs avec priorité (1 pour boss, 2 pour coffres)
            target_tiles = []
            
            # Ajouter le boss avec la priorité la plus élevée s'il est visible
            for boss in boss_tiles:
                target_tiles.append({"tile": boss, "priority": 1, "type": "boss"})
            
            # Ajouter les coffres avec une priorité inférieure
            for chest in all_chests:
                target_tiles.append({"tile": chest, "priority": 2, "type": "chest"})
            
            # Trier par priorité
            target_tiles.sort(key=lambda x: x["priority"])
            
            if not target_tiles:
                return None  # Aucune cible trouvée
                
            # 2. Pour chaque cible, trouver les cases visitées adjacentes
            for target_info in target_tiles:
                target = target_info["tile"]
                
                # Obtenir les coordonnées de la cible
                target_tr = target.find_element(By.XPATH, "./..")
                tbody = target_tr.find_element(By.XPATH, "./..")
                all_rows = tbody.find_elements(By.TAG_NAME, "tr")
                target_y = next((i for i, row in enumerate(all_rows) if row == target_tr), -1)
                
                all_cells = target_tr.find_elements(By.TAG_NAME, "td")
                target_x = next((i for i, cell in enumerate(all_cells) if cell == target), -1)
                
                # Vérifier les cases adjacentes à la cible
                directions = [
                    (0, -1),  # haut
                    (1, 0),   # droite
                    (0, 1),   # bas
                    (-1, 0)   # gauche
                ]
                
                for dx, dy in directions:
                    new_x = target_x + dx
                    new_y = target_y + dy
                    
                    # Vérifier si les coordonnées sont valides
                    if new_y >= 0 and new_y < len(all_rows):
                        row = all_rows[new_y]
                        cells = row.find_elements(By.TAG_NAME, "td")
                        
                        if new_x >= 0 and new_x < len(cells):
                            cell = cells[new_x]
                            class_attribute = cell.get_attribute("class")
                            
                            # Si la case adjacente est visitée, on peut l'utiliser comme point d'accès
                            if "tile-visited" in class_attribute:
                                target_info = {
                                    "target": target,
                                    "target_type": target_info["type"],
                                    "access_point": cell,
                                    "target_x": target_x,
                                    "target_y": target_y,
                                    "access_x": new_x,
                                    "access_y": new_y
                                }
                                return target_info
            
            return None  # Aucun chemin trouvé
            
        except Exception as e:
            self.log(f"Erreur lors de la recherche d'un chemin vers un coffre/boss: {str(e)}")
            return None
    
    def is_tile_directly_clickable(self, target_x, target_y):
        """Vérifier si une case est directement cliquable depuis la position actuelle du joueur"""
        try:
            # Récupérer la position du joueur
            player_pos = self.find_player_position()
            if not player_pos:
                return False
                
            player_x, player_y = player_pos
            
            # Calculer la distance (pour vérifier si on est adjacent)
            distance = abs(player_x - target_x) + abs(player_y - target_y)
            
            # Si la distance est 1, la case est adjacente et directement cliquable
            return distance == 1
        except Exception as e:
            self.log(f"Erreur lors de la vérification de l'accessibilité directe: {str(e)}")
            return False
    
    def find_unvisited_tiles_near_visited(self):
        """Trouver des cases non visitées adjacentes à des cases déjà visitées"""
        try:
            # Obtenir toutes les cases visitées
            visited_tiles = self.driver.find_elements(By.CSS_SELECTOR, "td.tile-visited:not(.tile-player)")
            
            # Pour chaque case visitée, vérifier ses voisins
            for visited_tile in visited_tiles:
                # Obtenir les coordonnées de la case visitée
                visited_tr = visited_tile.find_element(By.XPATH, "./..")
                tbody = visited_tr.find_element(By.XPATH, "./..")
                all_rows = tbody.find_elements(By.TAG_NAME, "tr")
                visited_y = next((i for i, row in enumerate(all_rows) if row == visited_tr), -1)
                
                visited_cells = visited_tr.find_elements(By.TAG_NAME, "td")
                visited_x = next((i for i, cell in enumerate(visited_cells) if cell == visited_tile), -1)
                
                # Vérifier les cases adjacentes
                directions = [
                    (0, -1),  # haut
                    (1, 0),   # droite
                    (0, 1),   # bas
                    (-1, 0)   # gauche
                ]
                
                for dx, dy in directions:
                    new_x = visited_x + dx
                    new_y = visited_y + dy
                    
                    # Vérifier si les coordonnées sont valides
                    if new_y >= 0 and new_y < len(all_rows):
                        row = all_rows[new_y]
                        cells = row.find_elements(By.TAG_NAME, "td")
                        
                        if new_x >= 0 and new_x < len(cells):
                            cell = cells[new_x]
                            class_attribute = cell.get_attribute("class")
                            
                            # Si c'est une case invisible (non découverte) ou spéciale
                            if "tile-invisible" in class_attribute:
                                return {
                                    "unvisited": cell,
                                    "from_visited": visited_tile,
                                    "unvisited_x": new_x,
                                    "unvisited_y": new_y,
                                    "visited_x": visited_x,
                                    "visited_y": visited_y
                                }
                            elif "tile-chest" in class_attribute and "tile-visited" not in class_attribute:
                                # Coffre non visité
                                return {
                                    "unvisited": cell,
                                    "from_visited": visited_tile,
                                    "unvisited_x": new_x,
                                    "unvisited_y": new_y,
                                    "visited_x": visited_x,
                                    "visited_y": visited_y,
                                    "type": "chest"
                                }
                            elif "tile-boss" in class_attribute and "tile-visited" not in class_attribute:
                                # Boss non visité
                                return {
                                    "unvisited": cell,
                                    "from_visited": visited_tile,
                                    "unvisited_x": new_x,
                                    "unvisited_y": new_y,
                                    "visited_x": visited_x,
                                    "visited_y": visited_y,
                                    "type": "boss"
                                }
            
            return None  # Aucune case non visitée adjacente à une case visitée
            
        except Exception as e:
            self.log(f"Erreur lors de la recherche de cases non visitées: {str(e)}")
            return None