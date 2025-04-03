import heapq
from selenium.webdriver.common.by import By

class PokeclickerBotDungeonPathfinding:
    """
    Module d'optimisation des déplacements dans le donjon avec algorithme A* 
    pour trouver le chemin le plus efficace en évitant les ennemis
    """
    
    def analyze_dungeon_map(self):
        """Analyser la carte du donjon pour récupérer toutes les informations nécessaires"""
        try:
            # Structure pour stocker la carte complète
            dungeon_map = {
                "rows": [],
                "player_pos": None,
                "boss_pos": None,
                "chests": [],
                "visible_tiles": [],
                "visited_tiles": [],
                "empty_tiles": [],  # Stocker spécifiquement les cases vides pour optimiser les chemins
                "enemy_tiles": []   # Stocker les cases ennemies pour les éviter
            }
            
            # Récupérer toutes les lignes de la carte
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.dungeon-board tr")
            
            # Parcourir les lignes et colonnes pour construire la carte
            for y, row in enumerate(rows):
                row_data = []
                cells = row.find_elements(By.TAG_NAME, "td")
                
                for x, cell in enumerate(cells):
                    cell_class = cell.get_attribute("class")
                    cell_info = {
                        "element": cell,
                        "x": x,
                        "y": y,
                        "classes": cell_class,
                        "accessible": True,  # Par défaut, supposons que la case est accessible
                        "cost": 1  # Coût de base pour traverser cette case
                    }
                    
                    # Identifier le type de case
                    if "tile-player" in cell_class:
                        dungeon_map["player_pos"] = (x, y)
                        cell_info["type"] = "player"
                        dungeon_map["visited_tiles"].append((x, y))
                        cell_info["cost"] = 1
                    elif "tile-boss" in cell_class:
                        dungeon_map["boss_pos"] = (x, y)
                        cell_info["type"] = "boss"
                        dungeon_map["visible_tiles"].append((x, y))
                        cell_info["cost"] = 1  # Le boss a un coût faible pour favoriser son accès
                    elif "tile-chest" in cell_class:
                        dungeon_map["chests"].append((x, y))
                        cell_info["type"] = "chest"
                        dungeon_map["visible_tiles"].append((x, y))
                        cell_info["cost"] = 1  # Les coffres ont un coût faible pour favoriser leur accès
                    elif "tile-visited" in cell_class:
                        cell_info["type"] = "visited"
                        dungeon_map["visited_tiles"].append((x, y))
                        cell_info["cost"] = 2  # Les cases visitées ont un coût moyen
                    elif "tile-invisible" in cell_class:
                        cell_info["type"] = "invisible"
                        cell_info["accessible"] = False  # Cases invisibles ne sont pas directement accessibles
                        cell_info["cost"] = 999  # Coût élevé pour éviter les cases invisibles
                    elif "tile-enemy" in cell_class:
                        cell_info["type"] = "enemy"
                        cell_info["accessible"] = True  # S'assurer que les ennemis sont considérés comme accessibles
                        dungeon_map["visible_tiles"].append((x, y))
                        dungeon_map["enemy_tiles"].append((x, y))
                        cell_info["cost"] = 5  # Coût élevé pour éviter les ennemis quand possible
                    elif "tile-empty" in cell_class:
                        cell_info["type"] = "empty"
                        dungeon_map["visible_tiles"].append((x, y))
                        dungeon_map["empty_tiles"].append((x, y))
                        cell_info["cost"] = 1  # Coût minimal pour favoriser les cases vides
                    else:
                        cell_info["type"] = "unknown"
                        cell_info["cost"] = 10  # Coût élevé pour les cases de type inconnu
                    
                    row_data.append(cell_info)
                
                dungeon_map["rows"].append(row_data)
            
            # Calculer les dimensions de la carte
            dungeon_map["height"] = len(dungeon_map["rows"])
            dungeon_map["width"] = len(dungeon_map["rows"][0]) if dungeon_map["height"] > 0 else 0
            
            # Déterminer l'état d'exploration du donjon
            dungeon_map["exploration_state"] = self.determine_exploration_state(dungeon_map)
            
            return dungeon_map
        
        except Exception as e:
            self.log(f"Erreur lors de l'analyse de la carte: {str(e)}")
            return None
    
    def determine_exploration_state(self, dungeon_map):
        """
        Déterminer l'état actuel de l'exploration du donjon:
        - "initial": Début d'exploration, peu de cases visibles
        - "chests_visible": Certains coffres sont visibles, mais pas le boss
        - "boss_visible": Le boss est visible, phase finale
        """
        if dungeon_map["boss_pos"]:
            return "boss_visible"
        elif dungeon_map["chests"]:
            return "chests_visible"
        else:
            return "initial"
    
    def is_directly_accessible(self, start_x, start_y, target_x, target_y, dungeon_map):
        """
        Vérifier si une case cible est directement accessible depuis la case de départ
        Une case est directement accessible si:
        1. Elle est adjacente à la case de départ
        2. La case de départ est visitée ou c'est la position du joueur
        """
        # Vérifier si les cases sont adjacentes (pas en diagonale)
        manhattan_distance = abs(target_x - start_x) + abs(target_y - start_y)
        if manhattan_distance != 1:
            return False
        
        # Vérifier si la case de départ est visitée ou c'est la position du joueur
        if (start_x, start_y) in dungeon_map["visited_tiles"] or (start_x, start_y) == dungeon_map["player_pos"]:
            # Vérifier si la case cible est visible (pas invisible)
            target_info = dungeon_map["rows"][target_y][target_x]
            return target_info["accessible"]
        
        return False
    
    def can_click_from_any_visited(self, target_x, target_y, dungeon_map):
        """
        Vérifier si la case cible peut être cliquée depuis n'importe quelle case visitée
        (pas nécessairement depuis la position actuelle du joueur)
        """
        # Vérifier toutes les cases visitées
        for visited_x, visited_y in dungeon_map["visited_tiles"]:
            if self.is_directly_accessible(visited_x, visited_y, target_x, target_y, dungeon_map):
                return (visited_x, visited_y)  # Retourne la position de la case visitée depuis laquelle on peut cliquer
                
        # Vérifier également la position actuelle du joueur
        if dungeon_map["player_pos"]:
            player_x, player_y = dungeon_map["player_pos"]
            if self.is_directly_accessible(player_x, player_y, target_x, target_y, dungeon_map):
                return (player_x, player_y)
                
        return None  # Aucune case visitée ne permet d'accéder directement à la cible
    
    def heuristic(self, x1, y1, x2, y2):
        """
        Heuristique pour l'algorithme A* - Distance de Manhattan
        Estime la distance entre deux points
        """
        return abs(x1 - x2) + abs(y1 - y2)
    
    def find_best_path(self, start_x, start_y, target_x, target_y, dungeon_map):
        """
        Utiliser l'algorithme A* pour trouver le chemin le plus court 
        en priorisant les chemins directs et en évitant les ennemis
        """
        # Si la cible est directement accessible depuis la position actuelle
        if self.is_directly_accessible(start_x, start_y, target_x, target_y, dungeon_map):
            return [(target_x, target_y)]
        
        # Vérifier si la cible est directement accessible depuis une autre case visitée
        access_point = self.can_click_from_any_visited(target_x, target_y, dungeon_map)
        if access_point:
            access_x, access_y = access_point
            
            # Si c'est directement depuis la position du joueur
            if (access_x, access_y) == (start_x, start_y):
                return [(target_x, target_y)]
                
            # Sinon, nous devons d'abord nous déplacer vers cette case visitée
            if (access_x, access_y) in dungeon_map["visited_tiles"]:
                # Vérifier si le point d'accès est directement cliquable
                if self.is_directly_accessible(start_x, start_y, access_x, access_y, dungeon_map):
                    return [(access_x, access_y), (target_x, target_y)]
                
                # Sinon, trouver un chemin vers ce point d'accès
                # et ensuite vers la cible
                path_to_access = self.find_best_path_through_visited(start_x, start_y, access_x, access_y, dungeon_map)
                if path_to_access:
                    return path_to_access + [(target_x, target_y)]
        
        # Définir les nœuds de départ et d'arrivée
        start = (start_x, start_y)
        goal = (target_x, target_y)
        
        # Liste ouverte (nœuds à explorer)
        open_set = []
        heapq.heappush(open_set, (0, start))  # (f_score, position)
        
        # Dictionnaire pour reconstruire le chemin
        came_from = {}
        
        # g_score[n] est le coût du meilleur chemin connu de start à n
        g_score = {start: 0}
        
        # f_score[n] = g_score[n] + heuristic(n, goal)
        f_score = {start: self.heuristic(start_x, start_y, target_x, target_y)}
        
        # Garder une trace des nœuds déjà explorés pour éviter les boucles
        closed_set = set()
        
        while open_set:
            # Récupérer le nœud avec le plus petit f_score
            _, current = heapq.heappop(open_set)
            current_x, current_y = current
            
            # Si on a atteint le but
            if current == goal:
                # Reconstruire le chemin
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                
                # Inverser le chemin pour l'avoir dans le bon ordre (du début à la fin)
                path.reverse()
                return path[1:]  # Exclure la position de départ
            
            # Ajouter le nœud courant à l'ensemble fermé
            closed_set.add(current)
            
            # Examiner les voisins (haut, droite, bas, gauche)
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            
            for dx, dy in directions:
                neighbor_x, neighbor_y = current_x + dx, current_y + dy
                neighbor = (neighbor_x, neighbor_y)
                
                # Vérifier si le voisin est dans les limites de la carte
                if (0 <= neighbor_y < dungeon_map["height"] and 
                    0 <= neighbor_x < dungeon_map["width"]):
                    
                    # Si déjà exploré, passer au suivant
                    if neighbor in closed_set:
                        continue
                    
                    neighbor_info = dungeon_map["rows"][neighbor_y][neighbor_x]
                    
                    # Le chemin doit passer par des cases accessibles
                    # IMPORTANT: Ne pas considérer les cases déjà visitées, sauf si c'est la destination
                    if neighbor_info["accessible"] and (neighbor == goal or "tile-visited" not in neighbor_info["classes"]):
                        # Coût pour atteindre ce voisin
                        temp_g_score = g_score[current] + neighbor_info["cost"]
                        
                        # Si nous avons trouvé un meilleur chemin vers ce voisin
                        if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                            # Mettre à jour les scores
                            came_from[neighbor] = current
                            g_score[neighbor] = temp_g_score
                            f_score_val = temp_g_score + self.heuristic(neighbor_x, neighbor_y, target_x, target_y)
                            f_score[neighbor] = f_score_val
                            
                            # Ajouter le voisin à la liste ouverte
                            heapq.heappush(open_set, (f_score_val, neighbor))
        
        # Si on arrive ici, aucun chemin trouvé
        return None
    
    def find_best_path_through_visited(self, start_x, start_y, target_x, target_y, dungeon_map):
        """
        Trouver le meilleur chemin d'une position à une autre en passant uniquement par des cases déjà visitées
        """
        # Vérifier si la cible est directement accessible
        if self.is_directly_accessible(start_x, start_y, target_x, target_y, dungeon_map):
            return [(target_x, target_y)]
        
        # Définir les nœuds de départ et d'arrivée
        start = (start_x, start_y)
        goal = (target_x, target_y)
        
        # Liste ouverte (nœuds à explorer)
        open_set = []
        heapq.heappush(open_set, (0, start))  # (f_score, position)
        
        # Dictionnaire pour reconstruire le chemin
        came_from = {}
        
        # g_score[n] est le coût du meilleur chemin connu de start à n
        g_score = {start: 0}
        
        # f_score[n] = g_score[n] + heuristic(n, goal)
        f_score = {start: self.heuristic(start_x, start_y, target_x, target_y)}
        
        # Garder une trace des nœuds déjà explorés pour éviter les boucles
        closed_set = set()
        
        while open_set:
            # Récupérer le nœud avec le plus petit f_score
            _, current = heapq.heappop(open_set)
            current_x, current_y = current
            
            # Si on a atteint le but
            if current == goal:
                # Reconstruire le chemin
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                
                # Inverser le chemin pour l'avoir dans le bon ordre (du début à la fin)
                path.reverse()
                return path[1:]  # Exclure la position de départ
            
            # Ajouter le nœud courant à l'ensemble fermé
            closed_set.add(current)
            
            # Examiner les voisins (haut, droite, bas, gauche)
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            
            for dx, dy in directions:
                neighbor_x, neighbor_y = current_x + dx, current_y + dy
                neighbor = (neighbor_x, neighbor_y)
                
                # Vérifier si le voisin est dans les limites de la carte
                if (0 <= neighbor_y < dungeon_map["height"] and 
                    0 <= neighbor_x < dungeon_map["width"]):
                    
                    # Si déjà exploré, passer au suivant
                    if neighbor in closed_set:
                        continue
                    
                    # Ne considérer que la position du joueur et la cible
                    # ÉVITER COMPLÈTEMENT les cases déjà visitées, sauf si on n'a pas d'autre choix
                    if neighbor == dungeon_map["player_pos"] or neighbor == goal:
                        neighbor_info = dungeon_map["rows"][neighbor_y][neighbor_x]
                        
                        # Calculer le coût pour ce voisin
                        temp_g_score = g_score[current] + neighbor_info["cost"]
                        
                        # Si nous avons trouvé un meilleur chemin vers ce voisin
                        if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                            # Mettre à jour les scores
                            came_from[neighbor] = current
                            g_score[neighbor] = temp_g_score
                            f_score_val = temp_g_score + self.heuristic(neighbor_x, neighbor_y, target_x, target_y)
                            f_score[neighbor] = f_score_val
                            
                            # Ajouter le voisin à la liste ouverte
                            heapq.heappush(open_set, (f_score_val, neighbor))
        
        # Si on arrive ici, aucun chemin trouvé via les cases visitées
        return None
    
    def find_next_move(self):
        """
        Déterminer la prochaine case où se déplacer, en fonction de l'état du donjon
        """
        try:
            # Analyser la carte du donjon
            dungeon_map = self.analyze_dungeon_map()
            if not dungeon_map or not dungeon_map["player_pos"]:
                self.log("Impossible d'analyser la carte du donjon ou de trouver la position du joueur")
                return None
            
            player_x, player_y = dungeon_map["player_pos"]
            exploration_state = dungeon_map["exploration_state"]
            
            # PRIORITÉ 1: Si le boss est visible, trouver le chemin optimal vers lui
            if exploration_state == "boss_visible":
                return self.find_path_to_boss(dungeon_map)
            
            # PRIORITÉ 2: Si des coffres sont visibles, trouver le chemin vers le plus proche
            elif exploration_state == "chests_visible":
                return self.find_path_to_nearest_chest(dungeon_map)
            
            # PRIORITÉ 3: Au début, explorer les cases non visitées adjacentes aux cases visitées
            else:
                return self.find_next_exploration_move(dungeon_map)
            
        except Exception as e:
            self.log(f"Erreur lors de la recherche du prochain mouvement: {str(e)}")
            return None
    
    def find_path_to_boss(self, dungeon_map):
        """Trouver le chemin optimal vers le boss"""
        if not dungeon_map["boss_pos"]:
            return None
            
        boss_x, boss_y = dungeon_map["boss_pos"]
        player_x, player_y = dungeon_map["player_pos"]
        
        self.log(f"Boss détecté en ({boss_x}, {boss_y}), calcul du chemin optimal...")
        
        # Vérifier si le boss est directement accessible
        if self.is_directly_accessible(player_x, player_y, boss_x, boss_y, dungeon_map):
            self.log(f"Boss directement accessible! Clic direct.")
            return {
                "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                "type": "boss_direct",
                "direct": True
            }
        
        # Vérifier si le boss est accessible depuis une autre case visitée
        access_point = self.can_click_from_any_visited(boss_x, boss_y, dungeon_map)
        if access_point:
            access_x, access_y = access_point
            self.log(f"Boss accessible depuis la case visitée ({access_x}, {access_y})")
            
            # Si nous sommes déjà sur cette case
            if (access_x, access_y) == (player_x, player_y):
                return {
                    "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                    "type": "boss_from_current",
                    "direct": True
                }
            
            # Sinon, se déplacer d'abord vers la case d'accès
            if self.is_directly_accessible(player_x, player_y, access_x, access_y, dungeon_map):
                return {
                    "element": dungeon_map["rows"][access_y][access_x]["element"],
                    "type": "move_to_boss_access",
                    "direct": True,
                    "next_target": {
                        "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                        "x": boss_x,
                        "y": boss_y
                    }
                }
            
            # Si la case d'accès n'est pas directement accessible,
            # trouver le chemin vers cette case via des cases visitées
            path_to_access = self.find_best_path_through_visited(player_x, player_y, access_x, access_y, dungeon_map)
            if path_to_access:
                next_x, next_y = path_to_access[0]
                return {
                    "element": dungeon_map["rows"][next_y][next_x]["element"],
                    "type": "path_to_boss_access",
                    "direct": False,
                    "path": path_to_access,
                    "final_target": {
                        "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                        "x": boss_x,
                        "y": boss_y
                    }
                }
        
        # Si pas d'accès direct, trouver le meilleur chemin global en évitant les ennemis
        path = self.find_best_path(player_x, player_y, boss_x, boss_y, dungeon_map)
        if path:
            next_x, next_y = path[0]
            self.log(f"Chemin optimal vers le boss trouvé! Prochain mouvement: ({next_x}, {next_y})")
            return {
                "element": dungeon_map["rows"][next_y][next_x]["element"],
                "type": "path_to_boss",
                "path": path,
                "direct": False
            }
        
        return None
    
    def find_path_to_nearest_chest(self, dungeon_map):
        """Trouver le chemin vers le coffre le plus proche"""
        if not dungeon_map["chests"]:
            return None
            
        player_x, player_y = dungeon_map["player_pos"]
        
        # Trouver le coffre le plus proche (par distance de Manhattan)
        nearest_chest = None
        min_distance = float('inf')
        
        for chest_x, chest_y in dungeon_map["chests"]:
            distance = abs(chest_x - player_x) + abs(chest_y - player_y)
            if distance < min_distance:
                min_distance = distance
                nearest_chest = (chest_x, chest_y)
        
        if not nearest_chest:
            return None
            
        chest_x, chest_y = nearest_chest
        self.log(f"Coffre le plus proche détecté en ({chest_x}, {chest_y})")
        
        # Vérifier si le coffre est directement accessible
        if self.is_directly_accessible(player_x, player_y, chest_x, chest_y, dungeon_map):
            self.log(f"Coffre directement accessible! Clic direct.")
            return {
                "element": dungeon_map["rows"][chest_y][chest_x]["element"],
                "type": "chest_direct",
                "direct": True
            }
        
        # Vérifier si le coffre est accessible depuis une autre case visitée
        access_point = self.can_click_from_any_visited(chest_x, chest_y, dungeon_map)
        if access_point:
            access_x, access_y = access_point
            self.log(f"Coffre accessible depuis la case visitée ({access_x}, {access_y})")
            
            # Si nous sommes déjà sur cette case
            if (access_x, access_y) == (player_x, player_y):
                return {
                    "element": dungeon_map["rows"][chest_y][chest_x]["element"],
                    "type": "chest_from_current",
                    "direct": True
                }
            
            # Sinon, se déplacer d'abord vers la case d'accès
            if self.is_directly_accessible(player_x, player_y, access_x, access_y, dungeon_map):
                return {
                    "element": dungeon_map["rows"][access_y][access_x]["element"],
                    "type": "move_to_chest_access",
                    "direct": True,
                    "next_target": {
                        "element": dungeon_map["rows"][chest_y][chest_x]["element"],
                        "x": chest_x,
                        "y": chest_y
                    }
                }
            
            # Si la case d'accès n'est pas directement accessible,
            # trouver le chemin vers cette case via des cases visitées
            path_to_access = self.find_best_path_through_visited(player_x, player_y, access_x, access_y, dungeon_map)
            if path_to_access:
                next_x, next_y = path_to_access[0]
                return {
                    "element": dungeon_map["rows"][next_y][next_x]["element"],
                    "type": "path_to_chest_access",
                    "direct": False,
                    "path": path_to_access,
                    "final_target": {
                        "element": dungeon_map["rows"][chest_y][chest_x]["element"],
                        "x": chest_x,
                        "y": chest_y
                    }
                }
        
        # Si pas d'accès direct, trouver le meilleur chemin global
        path = self.find_best_path(player_x, player_y, chest_x, chest_y, dungeon_map)
        if path:
            next_x, next_y = path[0]
            self.log(f"Chemin vers le coffre trouvé! Prochain mouvement: ({next_x}, {next_y})")
            return {
                "element": dungeon_map["rows"][next_y][next_x]["element"],
                "type": "path_to_chest",
                "path": path,
                "direct": False
            }
        
        return None
    
    def find_next_exploration_move(self, dungeon_map):
        """
        Trouver la prochaine case à explorer quand nous sommes en phase initiale
        ou quand nous cherchons de nouvelles zones
        """
        player_x, player_y = dungeon_map["player_pos"]
        
        # 1. Chercher des cases non visitées directement adjacentes à la position du joueur
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # haut, droite, bas, gauche
        
        # Pour l'exploration initiale, on préfère utiliser un ordre aléatoire
        import random
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = player_x + dx, player_y + dy
            
            # Vérifier si la case est dans les limites
            if (0 <= new_y < dungeon_map["height"] and 
                0 <= new_x < dungeon_map["width"]):
                
                cell_info = dungeon_map["rows"][new_y][new_x]
                
                # Si c'est une case non visitée et accessible (pas invisible)
                if ((new_x, new_y) not in dungeon_map["visited_tiles"] and 
                    cell_info["accessible"]):
                    
                    self.log(f"Case adjacente non visitée trouvée en ({new_x}, {new_y})")
                    return {
                        "element": cell_info["element"],
                        "type": "adjacent_exploration",
                        "direct": True
                    }
        
        # 2. Chercher des cases non visitées accessibles depuis n'importe quelle case visitée
        for y, row in enumerate(dungeon_map["rows"]):
            for x, cell_info in enumerate(row):
                # Si la case n'est pas encore visitée mais est accessible
                if ((x, y) not in dungeon_map["visited_tiles"] and 
                    cell_info["accessible"]):
                    
                    # Vérifier si cette case est accessible depuis une case visitée
                    access_point = self.can_click_from_any_visited(x, y, dungeon_map)
                    if access_point:
                        access_x, access_y = access_point
                        self.log(f"Case non visitée en ({x}, {y}) accessible depuis ({access_x}, {access_y})")
                        
                        # Si nous sommes déjà sur cette case d'accès
                        if (access_x, access_y) == (player_x, player_y):
                            return {
                                "element": cell_info["element"],
                                "type": "non_adjacent_exploration",
                                "direct": True
                            }
                        
                        # Sinon, se déplacer d'abord vers la case d'accès
                        if self.is_directly_accessible(player_x, player_y, access_x, access_y, dungeon_map):
                            return {
                                "element": dungeon_map["rows"][access_y][access_x]["element"],
                                "type": "move_to_exploration_access",
                                "direct": True,
                                "next_target": {
                                    "element": cell_info["element"],
                                    "x": x,
                                    "y": y
                                }
                            }
                        
                        # Si la case d'accès n'est pas directement accessible,
                        # trouver le chemin vers cette case via des cases visitées
                        path_to_access = self.find_best_path_through_visited(player_x, player_y, access_x, access_y, dungeon_map)
                        if path_to_access:
                            next_x, next_y = path_to_access[0]
                            return {
                                "element": dungeon_map["rows"][next_y][next_x]["element"],
                                "type": "path_to_exploration_access",
                                "direct": False,
                                "path": path_to_access,
                                "final_target": {
                                    "element": cell_info["element"],
                                    "x": x,
                                    "y": y
                                }
                            }
        
                        # 3. Chercher des cases visitées avec des voisins non-visités (mais pas invisibles)
        # Priorité aux cases qui ont des voisins directement accessibles non visités
        visited_with_unvisited_neighbors = []
        
        for visited_x, visited_y in dungeon_map["visited_tiles"]:
            # Ne pas considérer la position actuelle du joueur
            if (visited_x, visited_y) == (player_x, player_y):
                continue
                
            # Vérifier si cette case visitée a des cases adjacentes non visitées mais visibles
            unvisited_neighbors = []
            for dx, dy in directions:
                neighbor_x, neighbor_y = visited_x + dx, visited_y + dy
                
                # Vérifier si la case est dans les limites
                if (0 <= neighbor_y < dungeon_map["height"] and 
                    0 <= neighbor_x < dungeon_map["width"]):
                    
                    neighbor_info = dungeon_map["rows"][neighbor_y][neighbor_x]
                    
                    # Si c'est une case visible mais non visitée
                    if ("tile-visited" not in neighbor_info["classes"] and 
                        "tile-player" not in neighbor_info["classes"] and
                        "tile-invisible" not in neighbor_info["classes"]):
                        unvisited_neighbors.append((neighbor_x, neighbor_y))
            
            if unvisited_neighbors:
                # Cette case visitée a des voisins non visités
                visited_with_unvisited_neighbors.append({
                    "x": visited_x,
                    "y": visited_y,
                    "unvisited_count": len(unvisited_neighbors),
                    "distance": abs(visited_x - player_x) + abs(visited_y - player_y)
                })
        
        # Trier les cases visitées par nombre de voisins non visités (décroissant) et distance (croissant)
        visited_with_unvisited_neighbors.sort(key=lambda item: (-item["unvisited_count"], item["distance"]))
        
        # Essayer les cases visitées avec le plus de voisins non visités
        if visited_with_unvisited_neighbors:
            best_visited = visited_with_unvisited_neighbors[0]
            visited_x, visited_y = best_visited["x"], best_visited["y"]
            
            self.log(f"Case visitée avec {best_visited['unvisited_count']} voisins non visités trouvée en ({visited_x}, {visited_y})")
            
            # Vérifier si cette case est directement accessible
            if self.is_directly_accessible(player_x, player_y, visited_x, visited_y, dungeon_map):
                return {
                    "element": dungeon_map["rows"][visited_y][visited_x]["element"],
                    "type": "move_to_unvisited_neighbors",
                    "direct": True
                }
            
            # Sinon, vérifier si elle est accessible depuis une autre case visitée
            access_point = self.can_click_from_any_visited(visited_x, visited_y, dungeon_map)
            if access_point and access_point != (player_x, player_y):
                access_x, access_y = access_point
                
                self.log(f"Case d'accès trouvée en ({access_x}, {access_y}) pour atteindre ({visited_x}, {visited_y})")
                
                if self.is_directly_accessible(player_x, player_y, access_x, access_y, dungeon_map):
                    return {
                        "element": dungeon_map["rows"][access_y][access_x]["element"],
                        "type": "move_to_access_point",
                        "direct": True,
                        "next_target": {
                            "element": dungeon_map["rows"][visited_y][visited_x]["element"],
                            "x": visited_x,
                            "y": visited_y
                        }
                    }
            
            # En dernier recours, utiliser force_exploration_with_javascript
            self.log("Aucun chemin direct trouvé, utilisation de l'exploration JavaScript forcée")
            return None
        
        # 4. Si aucune option précédente n'a fonctionné, faire un déplacement aléatoire
        # vers une case visitée pour tenter de trouver de nouvelles zones
        if len(dungeon_map["visited_tiles"]) > 1:  # Plus d'une case visitée
            import random
            
            # Exclure la position actuelle du joueur
            other_visited = [pos for pos in dungeon_map["visited_tiles"] if pos != (player_x, player_y)]
            
            if other_visited:
                random_visited = random.choice(other_visited)
                visited_x, visited_y = random_visited
                
                self.log(f"Aucune case explorable trouvée, déplacement aléatoire vers ({visited_x}, {visited_y})")
                
                # Vérifier si cette case est directement accessible
                if self.is_directly_accessible(player_x, player_y, visited_x, visited_y, dungeon_map):
                    return {
                        "element": dungeon_map["rows"][visited_y][visited_x]["element"],
                        "type": "random_move",
                        "direct": True
                    }
                
                # Sinon, trouver un chemin vers cette case
                path = self.find_best_path_through_visited(player_x, player_y, visited_x, visited_y, dungeon_map)
                if path:
                    next_x, next_y = path[0]
                    return {
                        "element": dungeon_map["rows"][next_y][next_x]["element"],
                        "type": "random_path",
                        "path": path,
                        "direct": False
                    }
        
        # Si aucune option n'a fonctionné, signaler un problème
        self.log("Aucun mouvement viable trouvé pour l'exploration")
        return None