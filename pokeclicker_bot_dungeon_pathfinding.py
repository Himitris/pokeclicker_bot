import heapq
from selenium.webdriver.common.by import By
import random
import time

class PokeclickerBotDungeonPathfinding:
    """
    Module d'optimisation des déplacements dans le donjon avec algorithme A* 
    pour trouver le chemin le plus efficace en évitant les ennemis
    """

    def analyze_dungeon_map(self):
        """
        Analyse la carte du donjon avec une reconnaissance améliorée des éléments
        et une détection plus précise des différents types de coffres
        """
        try:
            # Structure pour stocker la carte complète
            dungeon_map = {
                "rows": [],
                "player_pos": None,
                "boss_pos": None,
                "chests": [],  # Tous les coffres
                "common_chests": [],  # Coffres communs
                "rare_chests": [],    # Coffres rares
                "visible_tiles": [],
                "visited_tiles": [],
                "empty_tiles": [],
                "enemy_tiles": [],
                "wall_tiles": [],     # Murs (infranchissables)
                "exploration_status": {
                    "total_tiles": 0,
                    "visible_tiles_count": 0,
                    "visited_tiles_count": 0,
                    "exploration_percentage": 0
                }
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
                        "cost": 1,  # Coût de base pour traverser cette case
                        "visited": False,
                        "visible": False
                    }
                    
                    # Identifier le type précis de case
                    if "tile-player" in cell_class:
                        dungeon_map["player_pos"] = (x, y)
                        cell_info["type"] = "player"
                        dungeon_map["visited_tiles"].append((x, y))
                        cell_info["cost"] = 1
                        cell_info["visited"] = True
                        cell_info["visible"] = True
                    
                    elif "tile-boss" in cell_class:
                        dungeon_map["boss_pos"] = (x, y)
                        cell_info["type"] = "boss"
                        dungeon_map["visible_tiles"].append((x, y))
                        cell_info["cost"] = 1  # Le boss a un coût faible pour favoriser son accès
                        cell_info["visible"] = True
                    
                    elif "tile-chest" in cell_class:
                        # Distinguer les types de coffres
                        chest_type = "common"
                        if "tile-chest-rare" in cell_class:
                            chest_type = "rare"
                        elif "tile-chest-epic" in cell_class:
                            chest_type = "epic"
                        
                        # Stocker les coordonnées du coffre et ses informations
                        chest_info = {"x": x, "y": y, "type": chest_type}
                        dungeon_map["chests"].append((x, y))
                        
                        # Ajouter aux listes spécifiques
                        if chest_type == "common":
                            dungeon_map["common_chests"].append((x, y))
                        else:
                            dungeon_map["rare_chests"].append((x, y))
                            
                        cell_info["type"] = f"chest_{chest_type}"
                        dungeon_map["visible_tiles"].append((x, y))
                        cell_info["cost"] = 1  # Les coffres ont un coût faible pour favoriser leur accès
                        cell_info["visible"] = True
                    
                    elif "tile-visited" in cell_class:
                        cell_info["type"] = "visited"
                        dungeon_map["visited_tiles"].append((x, y))
                        cell_info["cost"] = 2  # Les cases visitées ont un coût moyen
                        cell_info["visited"] = True
                        cell_info["visible"] = True
                    
                    elif "tile-invisible" in cell_class:
                        cell_info["type"] = "invisible"
                        cell_info["accessible"] = False  # Cases invisibles ne sont pas directement accessibles
                        cell_info["cost"] = 999  # Coût élevé pour éviter les cases invisibles
                        cell_info["visible"] = False
                    
                    elif "tile-enemy" in cell_class:
                        # Distinguer les types d'ennemis si possible
                        enemy_type = "standard"
                        if "tile-enemy-strong" in cell_class:
                            enemy_type = "strong"
                        
                        cell_info["type"] = f"enemy_{enemy_type}"
                        cell_info["accessible"] = True  # S'assurer que les ennemis sont considérés comme accessibles
                        dungeon_map["visible_tiles"].append((x, y))
                        dungeon_map["enemy_tiles"].append((x, y))
                        
                        # Ajuster le coût en fonction du type d'ennemi
                        if enemy_type == "strong":
                            cell_info["cost"] = 8  # Coût très élevé pour les ennemis forts
                        else:
                            cell_info["cost"] = 5  # Coût élevé pour les ennemis standards
                        
                        cell_info["visible"] = True
                    
                    elif "tile-empty" in cell_class:
                        cell_info["type"] = "empty"
                        dungeon_map["visible_tiles"].append((x, y))
                        dungeon_map["empty_tiles"].append((x, y))
                        cell_info["cost"] = 1  # Coût minimal pour favoriser les cases vides
                        cell_info["visible"] = True
                    
                    elif "tile-wall" in cell_class or "tile-exit" in cell_class:
                        # Murs ou sorties qui ne sont pas traversables
                        cell_info["type"] = "wall" if "tile-wall" in cell_class else "exit"
                        cell_info["accessible"] = False
                        dungeon_map["wall_tiles"].append((x, y))
                        dungeon_map["visible_tiles"].append((x, y))
                        cell_info["cost"] = 999  # Coût très élevé pour les murs
                        cell_info["visible"] = True
                    
                    else:
                        cell_info["type"] = "unknown"
                        cell_info["cost"] = 10  # Coût élevé pour les cases de type inconnu
                    
                    row_data.append(cell_info)
                
                dungeon_map["rows"].append(row_data)
            
            # Calculer les dimensions de la carte
            dungeon_map["height"] = len(dungeon_map["rows"])
            dungeon_map["width"] = len(dungeon_map["rows"][0]) if dungeon_map["height"] > 0 else 0
            
            # Calculer les statistiques d'exploration
            total_tiles = dungeon_map["height"] * dungeon_map["width"]
            visible_tiles_count = len(dungeon_map["visible_tiles"])
            visited_tiles_count = len(dungeon_map["visited_tiles"])
            
            exploration_percentage = (visible_tiles_count / total_tiles) * 100 if total_tiles > 0 else 0
            
            dungeon_map["exploration_status"] = {
                "total_tiles": total_tiles,
                "visible_tiles_count": visible_tiles_count,
                "visited_tiles_count": visited_tiles_count,
                "exploration_percentage": exploration_percentage
            }
            
            # Détecter le type de donjon et sa difficulté pour adapter la stratégie
            dungeon_map["dungeon_type"] = self.detect_dungeon_type()
            
            # Déterminer l'état d'exploration du donjon de façon plus précise
            dungeon_map["exploration_phase"] = self.determine_exploration_phase(dungeon_map)
            
            return dungeon_map
        
        except Exception as e:
            self.log(f"Erreur lors de l'analyse de la carte: {str(e)}")
            return None

    def detect_dungeon_type(self):
        """
        Détecte le type de donjon actuel pour adapter la stratégie
        Certains donjons ont des règles spécifiques (plus de coffres nécessaires, etc.)
        """
        try:
            # Essayer de récupérer le nom du donjon depuis l'interface
            dungeon_name_element = self.driver.find_element(By.CSS_SELECTOR, "h4.modal-title")
            if dungeon_name_element:
                dungeon_name = dungeon_name_element.text.strip()
                
                # Détecter les donjons spéciaux
                if "Victory Road" in dungeon_name:
                    return {"name": dungeon_name, "type": "victory_road", "difficulty": "hard", "min_chests": 3}
                elif "Cave" in dungeon_name:
                    return {"name": dungeon_name, "type": "cave", "difficulty": "medium", "min_chests": 2}
                elif "Tower" in dungeon_name or "Temple" in dungeon_name:
                    return {"name": dungeon_name, "type": "tower", "difficulty": "hard", "min_chests": 3}
                elif "Forest" in dungeon_name or "Woods" in dungeon_name:
                    return {"name": dungeon_name, "type": "forest", "difficulty": "easy", "min_chests": 1}
                else:
                    # Donjon standard
                    return {"name": dungeon_name, "type": "standard", "difficulty": "normal", "min_chests": 2}
        except:
            pass
        
        # Détection basée sur les caractéristiques de la carte
        try:
            # Calculer les dimensions de la carte pour estimer le type
            table_element = self.driver.find_element(By.CSS_SELECTOR, "table.dungeon-board")
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            columns = rows[0].find_elements(By.TAG_NAME, "td") if rows else []
            
            width = len(columns)
            height = len(rows)
            
            # Classifier en fonction de la taille
            if width >= 15 or height >= 15:
                return {"name": "Large Dungeon", "type": "large", "difficulty": "hard", "min_chests": 3}
            elif width >= 10 or height >= 10:
                return {"name": "Medium Dungeon", "type": "medium", "difficulty": "normal", "min_chests": 2}
            else:
                return {"name": "Small Dungeon", "type": "small", "difficulty": "easy", "min_chests": 1}
        except:
            pass
        
        # Valeur par défaut si la détection échoue
        return {"name": "Unknown Dungeon", "type": "standard", "difficulty": "normal", "min_chests": 2}

    def determine_exploration_phase(self, dungeon_map):
        """
        Détermine avec plus de précision la phase actuelle d'exploration du donjon
        """
        # Phase Boss: Le boss est visible
        if dungeon_map["boss_pos"]:
            return "boss_visible"
        
        # Phase Coffres: Des coffres sont visibles mais pas le boss
        if dungeon_map["chests"]:
            return "chests_visible"
        
        # Calculer le pourcentage de cases visibles pour mieux évaluer la progression
        exploration_percentage = dungeon_map["exploration_status"]["exploration_percentage"]
        
        # Si plus de 30% de la carte est visible mais pas de coffres ni de boss, on est dans une phase intermédiaire
        if exploration_percentage > 30:
            return "intermediate_exploration"
        
        # Phase initiale: peu de cases sont visibles
        return "initial_exploration"

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

    def find_all_access_points(self, target_x, target_y, dungeon_map):
        """
        Trouve toutes les cases visitées depuis lesquelles on peut accéder directement à la cible
        """
        access_points = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # haut, droite, bas, gauche
        
        for dx, dy in directions:
            adj_x, adj_y = target_x + dx, target_y + dy
            
            # Vérifier si les coordonnées sont valides
            if (0 <= adj_y < dungeon_map["height"] and 
                0 <= adj_x < dungeon_map["width"]):
                
                # Vérifier si cette case adjacente est visitée
                if (adj_x, adj_y) in dungeon_map["visited_tiles"]:
                    access_points.append((adj_x, adj_y))
        
        return access_points

    def heuristic(self, x1, y1, x2, y2):
        """
        Heuristique pour l'algorithme A* - Distance de Manhattan
        Estime la distance entre deux points
        """
        return abs(x1 - x2) + abs(y1 - y2)

    def count_enemies_on_path(self, path, dungeon_map):
        """
        Compte le nombre d'ennemis sur un chemin donné
        """
        enemy_count = 0
        for x, y in path:
            cell_info = dungeon_map["rows"][y][x]
            if "enemy" in cell_info["type"]:
                enemy_count += 1
        return enemy_count

    def find_best_path(self, start_x, start_y, target_x, target_y, dungeon_map, ignore_enemies=False):
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
                    
                    # Ignorer les cases inaccessibles
                    if not neighbor_info["accessible"]:
                        continue
                    
                    # Si ignorer les ennemis est activé, réduire leur coût
                    if ignore_enemies and "enemy" in neighbor_info["type"]:
                        cost = 2  # Coût réduit pour forcer le passage
                    else:
                        cost = neighbor_info["cost"]
                    
                    # Coût pour atteindre ce voisin
                    temp_g_score = g_score[current] + cost
                    
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
                    
                    # Ne considérer que les cases visitées et la position du joueur
                    if neighbor != goal and neighbor not in dungeon_map["visited_tiles"] and neighbor != dungeon_map["player_pos"]:
                        continue
                    
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

    def find_best_path_avoiding_enemies(self, start_x, start_y, target_x, target_y, dungeon_map):
        """
        Trouve le meilleur chemin d'un point à un autre en évitant au maximum les ennemis
        """
        # Augmenter significativement le coût des cases avec des ennemis pour A*
        for y, row in enumerate(dungeon_map["rows"]):
            for x, cell in enumerate(row):
                if "enemy" in cell["type"]:
                    cell["cost"] = 20  # Coût très élevé pour éviter les ennemis si possible
        
        # Utiliser l'algorithme A* existant avec ces coûts ajustés
        return self.find_best_path(start_x, start_y, target_x, target_y, dungeon_map)

    def count_unexplored_around(self, x, y, dungeon_map, radius=2):
        """
        Compte le nombre de cases inexplorées dans un rayon donné autour d'une position
        """
        unexplored_count = 0
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Ignorer la case centrale
                if dx == 0 and dy == 0:
                    continue
                    
                # Calculer les coordonnées de la case à vérifier
                check_x, check_y = x + dx, y + dy
                
                # Vérifier si les coordonnées sont valides
                if (0 <= check_y < dungeon_map["height"] and 
                    0 <= check_x < dungeon_map["width"]):
                    
                    # Une case est considérée comme inexplorée si elle n'est pas visible
                    if (check_x, check_y) not in dungeon_map["visible_tiles"] and (check_x, check_y) not in dungeon_map["visited_tiles"]:
                        unexplored_count += 1
        
        return unexplored_count

    def find_next_move(self):
        """
        Déterminer la prochaine case où se déplacer, en fonction de l'état du donjon
        et en optimisant le chemin par rapport aux phases du donjon
        """
        try:
            # Analyser la carte du donjon
            dungeon_map = self.analyze_dungeon_map()
            if not dungeon_map or not dungeon_map["player_pos"]:
                self.log("Impossible d'analyser la carte du donjon ou de trouver la position du joueur")
                return None
            
            player_x, player_y = dungeon_map["player_pos"]
            exploration_phase = self.determine_exploration_phase(dungeon_map)
            
            # PRIORITÉ 1: Si le boss est visible, trouver le chemin optimal vers lui en évitant les ennemis
            # et en ignorant tous les coffres
            if exploration_phase == "boss_visible":
                self.log("Boss découvert! Ignorer les coffres et se diriger directement vers le boss")
                return self.find_optimal_path_to_boss(dungeon_map)
            
            # PRIORITÉ 2: Si des coffres sont visibles mais pas le boss, chercher le coffre le plus stratégique
            elif exploration_phase == "chests_visible":
                self.log("Phase Coffres: Recherche du coffre le plus stratégique pour révéler le boss")
                return self.find_strategic_chest_path(dungeon_map)
            
            # PRIORITÉ 3: Phase initiale, explorer efficacement les cases adjacentes non visitées
            else:
                self.log("Phase Exploration Initiale: Exploration des zones inconnues")
                return self.find_efficient_exploration_move(dungeon_map)
            
        except Exception as e:
            self.log(f"Erreur lors de la recherche du prochain mouvement: {str(e)}")
            return None

    def find_optimal_path_to_boss(self, dungeon_map):
        """
        Trouve le chemin optimal vers le boss en évitant les ennemis au maximum
        et en exploitant la possibilité de cliquer sur des cases adjacentes à des cases visitées
        """
        if not dungeon_map["boss_pos"]:
            return None
            
        boss_x, boss_y = dungeon_map["boss_pos"]
        player_x, player_y = dungeon_map["player_pos"]
        
        self.log(f"Boss détecté en ({boss_x}, {boss_y}), calcul du chemin optimal...")
        
        # AMÉLIORATION: Vérifier d'abord si on peut cliquer directement sur le boss depuis 
        # n'importe quelle case déjà visitée
        # Cela permet de court-circuiter tout le calcul de chemin si une case visitée
        # est adjacente au boss
        direct_access_from = None
        for visited_x, visited_y in dungeon_map["visited_tiles"]:
            if self.is_directly_accessible(visited_x, visited_y, boss_x, boss_y, dungeon_map):
                direct_access_from = (visited_x, visited_y)
                # Si le joueur est déjà sur cette case, c'est la solution optimale
                if (visited_x, visited_y) == (player_x, player_y):
                    self.log(f"Boss directement accessible depuis la position actuelle! Clic direct.")
                    return {
                        "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                        "type": "boss_direct",
                        "direct": True
                    }
        
        # Si on a trouvé une case visitée qui permet d'accéder directement au boss,
        # déplaçons-nous vers cette case d'abord
        if direct_access_from:
            access_x, access_y = direct_access_from
            self.log(f"Boss accessible directement depuis la case ({access_x}, {access_y}). Optimisation du parcours.")
            
            # Si cette case est adjacente au joueur, on peut s'y déplacer directement
            if self.is_directly_accessible(player_x, player_y, access_x, access_y, dungeon_map):
                self.log(f"Déplacement direct vers la case d'accès, puis clic sur le boss")
                return {
                    "element": dungeon_map["rows"][access_y][access_x]["element"],
                    "type": "move_to_direct_boss_access",
                    "direct": True,
                    "next_target": {
                        "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                        "x": boss_x,
                        "y": boss_y
                    }
                }
            # Sinon, il faut trouver un chemin vers cette case visitée
            else:
                path_to_access = self.find_best_path_through_visited(player_x, player_y, access_x, access_y, dungeon_map)
                if path_to_access:
                    next_x, next_y = path_to_access[0]
                    self.log(f"Optimisation du chemin vers le point d'accès direct au boss")
                    return {
                        "element": dungeon_map["rows"][next_y][next_x]["element"],
                        "type": "path_to_direct_boss_access",
                        "direct": False,
                        "path": path_to_access,
                        "final_target": {
                            "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                            "x": boss_x,
                            "y": boss_y
                        }
                    }
        
        # Si pas d'accès direct possible, on revient à l'algorithme original
        # 1. Vérifier si le boss est directement accessible depuis la position actuelle
        if self.is_directly_accessible(player_x, player_y, boss_x, boss_y, dungeon_map):
            self.log(f"Boss directement accessible depuis la position actuelle! Clic direct.")
            return {
                "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                "type": "boss_direct",
                "direct": True
            }
        
        # 2. Vérifier si le boss est accessible depuis une case visitée (shortcut)
        access_points = self.find_all_access_points(boss_x, boss_y, dungeon_map)
        if access_points:
            # Trier les points d'accès par priorité: 
            # 1. Position actuelle du joueur
            # 2. Cases adjacentes au joueur
            # 3. Cases avec le moins d'ennemis sur le chemin
            # 4. Cases les plus proches du joueur
            
            # Organiser les points d'accès
            categorized_access_points = []
            for ax, ay in access_points:
                # Calculer la distance entre le joueur et ce point d'accès
                distance = abs(player_x - ax) + abs(player_y - ay)
                
                # Déterminer la priorité de cette case
                priority = 999  # Priorité par défaut (basse)
                
                if (ax, ay) == (player_x, player_y):
                    priority = 1  # Le joueur est déjà sur un point d'accès
                elif self.is_directly_accessible(player_x, player_y, ax, ay, dungeon_map):
                    priority = 2  # Point d'accès directement accessible
                else:
                    # Calculer le nombre d'ennemis sur le chemin vers ce point d'accès
                    path = self.find_best_path_through_visited(player_x, player_y, ax, ay, dungeon_map)
                    if path:
                        enemies_count = self.count_enemies_on_path(path, dungeon_map)
                        priority = 3 + enemies_count  # Plus il y a d'ennemis, plus la priorité est basse
                    else:
                        priority = 999  # Pas de chemin trouvé
                
                categorized_access_points.append({
                    "x": ax, 
                    "y": ay,
                    "distance": distance,
                    "priority": priority
                })
            
            # Trier les points d'accès par priorité puis par distance
            categorized_access_points.sort(key=lambda p: (p["priority"], p["distance"]))
            
            # Prendre le meilleur point d'accès
            if categorized_access_points:
                best_access = categorized_access_points[0]
                ax, ay = best_access["x"], best_access["y"]
                
                self.log(f"Meilleur point d'accès au boss trouvé en ({ax}, {ay}) (priorité {best_access['priority']})")
                
                # Si nous sommes déjà sur ce point d'accès
                if (ax, ay) == (player_x, player_y):
                    return {
                        "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                        "type": "boss_from_current_position",
                        "direct": True
                    }
                
                # Si le point d'accès est directement accessible
                if self.is_directly_accessible(player_x, player_y, ax, ay, dungeon_map):
                    return {
                        "element": dungeon_map["rows"][ay][ax]["element"],
                        "type": "move_to_boss_access_direct",
                        "direct": True,
                        "next_target": {
                            "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                            "x": boss_x,
                            "y": boss_y
                        }
                    }
                
                # Si le point d'accès n'est pas directement accessible,
                # trouver le meilleur chemin vers ce point via des cases visitées
                path_to_access = self.find_best_path_avoiding_enemies(player_x, player_y, ax, ay, dungeon_map)
                if path_to_access:
                    next_x, next_y = path_to_access[0]
                    return {
                        "element": dungeon_map["rows"][next_y][next_x]["element"],
                        "type": "path_to_boss_access_point",
                        "direct": False,
                        "path": path_to_access,
                        "final_target": {
                            "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                            "x": boss_x,
                            "y": boss_y
                        }
                    }
        
        # 3. Si pas de raccourci possible, trouver le meilleur chemin complet en évitant les ennemis
        path = self.find_best_path_avoiding_enemies(player_x, player_y, boss_x, boss_y, dungeon_map)
        if path:
            next_x, next_y = path[0]
            self.log(f"Chemin complet vers le boss trouvé! Prochain mouvement: ({next_x}, {next_y})")
            return {
                "element": dungeon_map["rows"][next_y][next_x]["element"],
                "type": "complete_path_to_boss",
                "path": path,
                "direct": False
            }
        
        # 4. En cas d'échec, tenter un chemin direct même avec des ennemis
        direct_path = self.find_best_path(player_x, player_y, boss_x, boss_y, dungeon_map, ignore_enemies=True)
        if direct_path:
            next_x, next_y = direct_path[0]
            self.log(f"Chemin direct vers le boss trouvé (avec ennemis)! Prochain mouvement: ({next_x}, {next_y})")
            return {
                "element": dungeon_map["rows"][next_y][next_x]["element"],
                "type": "direct_path_to_boss_with_enemies",
                "path": direct_path,
                "direct": False
            }
        
        return None
    
    def find_efficient_exploration_move(self, dungeon_map):
        """
        Trouve le meilleur mouvement pour l'exploration initiale
        Privilégie les cases qui maximisent la découverte de nouvelles zones
        """
        player_x, player_y = dungeon_map["player_pos"]
        
        # Phase d'exploration complètement initiale (beaucoup de cases invisibles)
        if len(dungeon_map["visible_tiles"]) < 10:
            # Explorer de manière semi-aléatoire mais systématique
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # haut, droite, bas, gauche
            
            # Trier les directions pour favoriser celles qui n'ont pas encore été explorées
            # et celles qui sont dans la direction du centre du donjon
            center_x, center_y = dungeon_map["width"] // 2, dungeon_map["height"] // 2
            
            # Calculer dans quelle direction se trouve le centre par rapport au joueur
            center_dir_x = 1 if center_x > player_x else (-1 if center_x < player_x else 0)
            center_dir_y = 1 if center_y > player_y else (-1 if center_y < player_y else 0)
            
            # Trier les directions par "intérêt d'exploration"
            direction_scores = []
            for dx, dy in directions:
                new_x, new_y = player_x + dx, player_y + dy
                
                # Vérifier si la case est dans les limites
                if not (0 <= new_y < dungeon_map["height"] and 0 <= new_x < dungeon_map["width"]):
                    continue
                    
                # Facteurs qui augmentent l'intérêt d'une direction:
                # 1. N'a pas encore été visitée
                # 2. Est dans la direction générale du centre du donjon
                # 3. N'est pas invisible (si on peut le savoir)
                
                score = 0
                
                # Pénaliser les cases déjà visitées
                if (new_x, new_y) in dungeon_map["visited_tiles"]:
                    score -= 10
                
                # Favoriser les directions vers le centre
                if (dx * center_dir_x + dy * center_dir_y) > 0:
                    score += 3
                    
                # Favoriser les cases qui ne sont pas invisibles (si connues)
                cell_info = dungeon_map["rows"][new_y][new_x]
                if "tile-invisible" not in cell_info["classes"]:
                    score += 5
                    
                direction_scores.append((dx, dy, score))
            
            # Trier par score (du plus haut au plus bas)
            direction_scores.sort(key=lambda d: -d[2])
            
            # Prendre la direction avec le meilleur score
            if direction_scores:
                best_dx, best_dy, _ = direction_scores[0]
                new_x, new_y = player_x + best_dx, player_y + best_dy
                
                self.log(f"Exploration initiale: direction ({best_dx}, {best_dy}) vers ({new_x}, {new_y})")
                
                return {
                    "element": dungeon_map["rows"][new_y][new_x]["element"],
                    "type": "initial_exploration",
                    "direct": True
                }
        
        # Phase d'exploration plus avancée
        # Chercher des cases non visitées adjacentes aux cases visitées,
        # en priorisant celles qui sont susceptibles de révéler de nouvelles zones
        
        visited_with_neighbors = []
        
        # Pour chaque case visitée
        for visited_x, visited_y in dungeon_map["visited_tiles"]:
            # Ne pas considérer la position actuelle du joueur
            if (visited_x, visited_y) == (player_x, player_y):
                continue
                
            # Chercher les cases adjacentes non visitées
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            for dx, dy in directions:
                adj_x, adj_y = visited_x + dx, visited_y + dy
                
                # Vérifier si la case est dans les limites
                if not (0 <= adj_y < dungeon_map["height"] and 0 <= adj_x < dungeon_map["width"]):
                    continue
                    
                # Vérifier si cette case n'a pas été visitée et n'est pas invisible
                if ((adj_x, adj_y) not in dungeon_map["visited_tiles"]):
                    cell_info = dungeon_map["rows"][adj_y][adj_x]
                    
                    # Si la case est accessible (pas invisible ou déjà visitée)
                    if cell_info["accessible"]:
                        # Calculer la distance entre le joueur et la case visitée
                        distance_to_visited = abs(player_x - visited_x) + abs(player_y - visited_y)
                        
                        # Calculer l'intérêt d'exploration
                        unexplored_around = self.count_unexplored_around(adj_x, adj_y, dungeon_map, radius=1)
                        
                        # Calculer un score qui combine la distance et l'intérêt d'exploration
                        exploration_score = unexplored_around - (distance_to_visited * 0.5)
                        
                        # Ajuster le score en fonction du type de case
                        if "tile-chest" in cell_info["classes"]:
                            exploration_score += 10  # Bonus majeur pour les coffres
                        elif "tile-empty" in cell_info["classes"]:
                            exploration_score += 2   # Bonus pour les cases vides
                        elif "tile-enemy" in cell_info["classes"]:
                            exploration_score -= 1   # Pénalité légère pour les ennemis
                            
                        visited_with_neighbors.append({
                            "visited_x": visited_x,
                            "visited_y": visited_y,
                            "target_x": adj_x,
                            "target_y": adj_y,
                            "distance": distance_to_visited,
                            "exploration_score": exploration_score,
                            "type": cell_info["type"]
                        })
        
        # Trier par score d'exploration (décroissant)
        visited_with_neighbors.sort(key=lambda n: -n["exploration_score"])
        
        # Prendre la meilleure option
        if visited_with_neighbors:
            best_option = visited_with_neighbors[0]
            visited_x, visited_y = best_option["visited_x"], best_option["visited_y"]
            target_x, target_y = best_option["target_x"], best_option["target_y"]
            
            self.log(f"Meilleure option d'exploration: case ({target_x}, {target_y}) "
                    f"depuis ({visited_x}, {visited_y}), score: {best_option['exploration_score']}")
            
            # Si le joueur est déjà sur la case visitée, cliquer directement sur la cible
            if (visited_x, visited_y) == (player_x, player_y):
                return {
                    "element": dungeon_map["rows"][target_y][target_x]["element"],
                    "type": "exploration_from_current",
                    "direct": True
                }
            
            # Si la case visitée est directement accessible
            if self.is_directly_accessible(player_x, player_y, visited_x, visited_y, dungeon_map):
                return {
                    "element": dungeon_map["rows"][visited_y][visited_x]["element"],
                    "type": "move_to_exploration_access",
                    "direct": True,
                    "next_target": {
                        "element": dungeon_map["rows"][target_y][target_x]["element"],
                        "x": target_x,
                        "y": target_y
                    }
                }
            
            # Si la case visitée n'est pas directement accessible, trouver un chemin
            path_to_visited = self.find_best_path_through_visited(player_x, player_y, visited_x, visited_y, dungeon_map)
            if path_to_visited:
                next_x, next_y = path_to_visited[0]
                return {
                    "element": dungeon_map["rows"][next_y][next_x]["element"],
                    "type": "path_to_exploration_access",
                    "direct": False,
                    "path": path_to_visited,
                    "final_target": {
                        "element": dungeon_map["rows"][target_y][target_x]["element"],
                        "x": target_x,
                        "y": target_y
                    }
                }
        
        # Si aucune option d'exploration intéressante n'a été trouvée, chercher une direction aléatoire
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        import random
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = player_x + dx, player_y + dy
            
            # Vérifier si la case est dans les limites
            if not (0 <= new_y < dungeon_map["height"] and 0 <= new_x < dungeon_map["width"]):
                continue
                
            # Vérifier si cette case est accessible
            cell_info = dungeon_map["rows"][new_y][new_x]
            if cell_info["accessible"]:
                self.log(f"Exploration aléatoire vers ({new_x}, {new_y})")
                return {
                    "element": cell_info["element"],
                    "type": "random_exploration",
                    "direct": True
                }
        
        # En dernier recours, utiliser l'API JavaScript pour explorer
        self.log("Aucun mouvement viable trouvé, utilisation de l'exploration JavaScript forcée")
        return None
    
    def find_strategic_chest_path(self, dungeon_map):
        """
        Trouve le chemin vers le coffre le plus stratégique (pas forcément le plus proche)
        Considère la position des autres coffres et l'état d'exploration du donjon
        """
        if not dungeon_map["chests"]:
            return None
            
        player_x, player_y = dungeon_map["player_pos"]
        
        # Calculer l'intérêt stratégique de chaque coffre
        strategic_chests = []
        
        for chest_x, chest_y in dungeon_map["chests"]:
            # Distance du joueur au coffre
            distance = abs(chest_x - player_x) + abs(chest_y - player_y)
            
            # Nombre de cases inexplorées autour du coffre (potentiel de révélation)
            unexplored_around = self.count_unexplored_around(chest_x, chest_y, dungeon_map)
            
            # Distance aux autres coffres (préférer les coffres isolés)
            min_distance_to_other_chests = float('inf')
            for other_x, other_y in dungeon_map["chests"]:
                if (other_x, other_y) != (chest_x, chest_y):
                    dist = abs(other_x - chest_x) + abs(other_y - chest_y)
                    min_distance_to_other_chests = min(min_distance_to_other_chests, dist)
            
            if min_distance_to_other_chests == float('inf'):
                min_distance_to_other_chests = 0
            
            # Calculer le score stratégique (plus il est bas, mieux c'est)
            # Formule: distance au joueur - (potentiel de révélation + distance aux autres coffres)
            strategic_score = distance - (unexplored_around * 2 + min_distance_to_other_chests)
            
            # Vérifier si ce coffre est directement accessible depuis la position actuelle
            direct_access = self.is_directly_accessible(player_x, player_y, chest_x, chest_y, dungeon_map)
            
            # Vérifier s'il est accessible depuis une case visitée
            access_points = self.find_all_access_points(chest_x, chest_y, dungeon_map)
            
            # Vérifier si un chemin est possible vers ce coffre
            # MODIFICATION: vérifier la possibilité d'accès avant d'ajouter le coffre à la liste
            has_possible_path = False
            
            if direct_access:
                has_possible_path = True
            elif access_points:
                has_possible_path = True
            else:
                # Tester si un chemin existe vers ce coffre
                test_path = self.find_best_path(player_x, player_y, chest_x, chest_y, dungeon_map, ignore_enemies=True)
                has_possible_path = (test_path is not None)
            
            # N'ajouter que les coffres accessibles
            if has_possible_path:
                strategic_chests.append({
                    "x": chest_x,
                    "y": chest_y,
                    "distance": distance,
                    "unexplored_around": unexplored_around,
                    "min_distance_to_other_chests": min_distance_to_other_chests,
                    "strategic_score": strategic_score,
                    "direct_access": direct_access,
                    "access_points": access_points
                })
        
        # Si aucun coffre n'est accessible, essayer d'explorer pour révéler de nouvelles zones
        if not strategic_chests:
            self.log("Aucun coffre accessible trouvé, passage en mode exploration pour révéler de nouvelles zones")
            return self.find_efficient_exploration_move(dungeon_map)
        
        # Trier les coffres par score stratégique (ascendant)
        strategic_chests.sort(key=lambda c: c["strategic_score"])
    
        
        # Prendre les 3 meilleurs coffres et choisir celui avec le meilleur accès
        best_chests = strategic_chests[:3] if len(strategic_chests) >= 3 else strategic_chests
        
        # Trier ces meilleurs coffres par facilité d'accès
        for chest in best_chests:
            # Priorité d'accès (plus c'est bas, mieux c'est)
            access_priority = 999
            
            if chest["direct_access"]:
                access_priority = 1  # Accès direct depuis la position actuelle
            elif chest["access_points"]:
                # Vérifier si un des points d'accès est directement accessible
                for ax, ay in chest["access_points"]:
                    if (ax, ay) == (player_x, player_y):
                        access_priority = 2  # Le joueur est déjà sur un point d'accès
                        break
                    elif self.is_directly_accessible(player_x, player_y, ax, ay, dungeon_map):
                        access_priority = 3  # Point d'accès directement accessible
                        break
                
                if access_priority == 999:
                    access_priority = 4  # Points d'accès mais pas directement accessibles
            
            chest["access_priority"] = access_priority
        
        # Trier d'abord par facilité d'accès, puis par score stratégique
        best_chests.sort(key=lambda c: (c["access_priority"], c["strategic_score"]))
        
        # Prendre le meilleur coffre après tous ces critères
        if not best_chests:
            return None
            
        best_chest = best_chests[0]
        chest_x, chest_y = best_chest["x"], best_chest["y"]
        
        self.log(f"Coffre le plus stratégique en ({chest_x}, {chest_y}) " 
                f"(score: {best_chest['strategic_score']}, accès: {best_chest['access_priority']})")
        
        # Construire la réponse en fonction du meilleur accès à ce coffre
        
        # 1. Accès direct depuis la position actuelle
        if best_chest["direct_access"]:
            return {
                "element": dungeon_map["rows"][chest_y][chest_x]["element"],
                "type": "strategic_chest_direct",
                "direct": True
            }
        
        # 2. Accès depuis un point d'accès
        if best_chest["access_points"]:
            # Trouver le meilleur point d'accès
            best_access = None
            best_access_priority = 999
            
            for ax, ay in best_chest["access_points"]:
                priority = 999
                
                if (ax, ay) == (player_x, player_y):
                    priority = 1  # Le joueur est déjà sur ce point d'accès
                    best_access = (ax, ay)
                    best_access_priority = priority
                    break
                elif self.is_directly_accessible(player_x, player_y, ax, ay, dungeon_map):
                    priority = 2  # Point d'accès directement accessible
                else:
                    priority = 3 + abs(player_x - ax) + abs(player_y - ay)  # Distance au point d'accès
                
                if priority < best_access_priority:
                    best_access = (ax, ay)
                    best_access_priority = priority
            
            if best_access:
                ax, ay = best_access
                
                # Si nous sommes déjà sur ce point d'accès
                if (ax, ay) == (player_x, player_y):
                    return {
                        "element": dungeon_map["rows"][chest_y][chest_x]["element"],
                        "type": "strategic_chest_from_current",
                        "direct": True
                    }
                
                # Si le point d'accès est directement accessible
                if self.is_directly_accessible(player_x, player_y, ax, ay, dungeon_map):
                    return {
                        "element": dungeon_map["rows"][ay][ax]["element"],
                        "type": "move_to_chest_access_direct",
                        "direct": True,
                        "next_target": {
                            "element": dungeon_map["rows"][chest_y][chest_x]["element"],
                            "x": chest_x,
                            "y": chest_y
                        }
                    }
                
                # Si le point d'accès n'est pas directement accessible,
                # trouver le meilleur chemin vers ce point via des cases visitées
                path_to_access = self.find_best_path_avoiding_enemies(player_x, player_y, ax, ay, dungeon_map)
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
        
        # 3. En dernier recours, trouver un chemin complet
        path = self.find_best_path_avoiding_enemies(player_x, player_y, chest_x, chest_y, dungeon_map)
        if path:
            next_x, next_y = path[0]
            return {
                "element": dungeon_map["rows"][next_y][next_x]["element"],
                "type": "complete_path_to_chest",
                "path": path,
                "direct": False
            }
        
        return None