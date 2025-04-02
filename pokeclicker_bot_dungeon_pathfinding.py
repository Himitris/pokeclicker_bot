import heapq
from selenium.webdriver.common.by import By

class PokeclickerBotDungeonPathfinding:
    """
    Module d'optimisation des déplacements dans le donjon avec algorithme A* pour trouver 
    le chemin le plus court vers un objectif
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
                "visited_tiles": []
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
                        "accessible": True  # Par défaut, supposons que la case est accessible
                    }
                    
                    # Identifier le type de case
                    if "tile-player" in cell_class:
                        dungeon_map["player_pos"] = (x, y)
                        cell_info["type"] = "player"
                        dungeon_map["visited_tiles"].append((x, y))
                    elif "tile-boss" in cell_class:
                        dungeon_map["boss_pos"] = (x, y)
                        cell_info["type"] = "boss"
                        dungeon_map["visible_tiles"].append((x, y))
                    elif "tile-chest" in cell_class:
                        dungeon_map["chests"].append((x, y))
                        cell_info["type"] = "chest"
                        dungeon_map["visible_tiles"].append((x, y))
                    elif "tile-visited" in cell_class:
                        cell_info["type"] = "visited"
                        dungeon_map["visited_tiles"].append((x, y))
                    elif "tile-invisible" in cell_class:
                        cell_info["type"] = "invisible"
                        cell_info["accessible"] = False  # Cases invisibles ne sont pas directement accessibles
                    # Dans analyze_dungeon_map, quand vous traitez les cases d'ennemi
                    elif "tile-enemy" in cell_class:
                        cell_info["type"] = "enemy"
                        cell_info["accessible"] = True  # S'assurer que les ennemis sont considérés comme accessibles
                        dungeon_map["visible_tiles"].append((x, y))
                    elif "tile-empty" in cell_class:
                        cell_info["type"] = "empty"
                        dungeon_map["visible_tiles"].append((x, y))
                    else:
                        cell_info["type"] = "unknown"
                    
                    row_data.append(cell_info)
                
                dungeon_map["rows"].append(row_data)
            
            # Calculer les dimensions de la carte
            dungeon_map["height"] = len(dungeon_map["rows"])
            dungeon_map["width"] = len(dungeon_map["rows"][0]) if dungeon_map["height"] > 0 else 0
            
            return dungeon_map
        
        except Exception as e:
            self.log(f"Erreur lors de l'analyse de la carte: {str(e)}")
            return None
    
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
        if (start_x, start_y) == dungeon_map["player_pos"] or (start_x, start_y) in dungeon_map["visited_tiles"]:
            # Vérifier si la case cible est visible (pas invisible)
            target_info = dungeon_map["rows"][target_y][target_x]
            return target_info["accessible"]
        
        return False
    
    def heuristic(self, x1, y1, x2, y2):
        """
        Heuristique pour l'algorithme A* - Distance de Manhattan
        Estime la distance entre deux points
        """
        return abs(x1 - x2) + abs(y1 - y2)
    
    def find_best_path(self, start_x, start_y, target_x, target_y, dungeon_map):
        """
        Utiliser l'algorithme A* pour trouver le chemin le plus court 
        en priorisant les chemins directs vers les objectifs importants
        """
        # Si la cible est directement accessible depuis la position actuelle
        if self.is_directly_accessible(start_x, start_y, target_x, target_y, dungeon_map):
            return [(target_x, target_y)]
        
        # Vérifier s'il existe un chemin direct et visible vers la cible
        # Utile pour les cas comme le boss visible directement
        dx = target_x - start_x
        dy = target_y - start_y
        
        # Si la cible est à 2 cases de distance seulement (1 case intermédiaire)
        if abs(dx) + abs(dy) <= 2:
            # Vérifier si on peut y aller directement (chemin visible)
            intermediate_x = start_x
            intermediate_y = start_y
            
            # Si la différence est sur l'axe X
            if abs(dx) == 2 and dy == 0:
                intermediate_x = start_x + (1 if dx > 0 else -1)
                
            # Si la différence est sur l'axe Y
            elif abs(dy) == 2 and dx == 0:
                intermediate_y = start_y + (1 if dy > 0 else -1)
            
            # Si c'est en diagonale (1,1), essayer les deux chemins possibles
            elif abs(dx) == 1 and abs(dy) == 1:
                # Option 1: d'abord horizontalement, puis verticalement
                option1_x = start_x + dx
                option1_y = start_y
                option1_valid = False
                
                # Option 2: d'abord verticalement, puis horizontalement
                option2_x = start_x
                option2_y = start_y + dy
                option2_valid = False
                
                # Vérifier si option 1 est valide
                if (0 <= option1_y < dungeon_map["height"] and 
                    0 <= option1_x < dungeon_map["width"]):
                    option1_info = dungeon_map["rows"][option1_y][option1_x]
                    if option1_info["accessible"]:
                        option1_valid = True
                
                # Vérifier si option 2 est valide
                if (0 <= option2_y < dungeon_map["height"] and 
                    0 <= option2_x < dungeon_map["width"]):
                    option2_info = dungeon_map["rows"][option2_y][option2_x]
                    if option2_info["accessible"]:
                        option2_valid = True
                
                # Choisir l'option valide (priorité à l'option 1)
                if option1_valid:
                    self.log(f"Chemin diagonal trouvé via ({option1_x}, {option1_y}) vers ({target_x}, {target_y})")
                    return [(option1_x, option1_y), (target_x, target_y)]
                elif option2_valid:
                    self.log(f"Chemin diagonal trouvé via ({option2_x}, {option2_y}) vers ({target_x}, {target_y})")
                    return [(option2_x, option2_y), (target_x, target_y)]
                
            # Pour les cas non-diagonaux, vérifier si la case intermédiaire est accessible
            else:
                if (0 <= intermediate_y < dungeon_map["height"] and 
                    0 <= intermediate_x < dungeon_map["width"]):
                    
                    intermediate_info = dungeon_map["rows"][intermediate_y][intermediate_x]
                    if intermediate_info["accessible"]:
                        # Retourner ce chemin direct
                        self.log(f"Chemin direct trouvé via ({intermediate_x}, {intermediate_y}) vers ({target_x}, {target_y})")
                        return [(intermediate_x, intermediate_y), (target_x, target_y)]
        
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
                    
                    # Le chemin doit passer par des cases visitées, accessibles ou l'objectif
                    if ((neighbor in dungeon_map["visited_tiles"] or 
                        neighbor == dungeon_map["player_pos"] or 
                        neighbor == goal) and 
                        neighbor_info["accessible"]):
                        
                        # Coût pour atteindre ce voisin
                        # Ajuster le coût selon le type de case
                        temp_g_score = g_score[current]
                        
                        # Ajuster le coût selon le type de case
                        if "empty" in neighbor_info["type"]:
                            temp_g_score += 1  # Coût minimal pour les cases vides
                        elif "enemy" in neighbor_info["type"]:
                            # Si la cible est le boss et que cette case est adjacente au boss,
                            # réduire le coût pour favoriser ce chemin
                            if (goal == dungeon_map["boss_pos"] and 
                                abs(neighbor_x - target_x) + abs(neighbor_y - target_y) == 1):
                                temp_g_score += 1  # Coût réduit pour les ennemis adjacents au boss
                            else:
                                temp_g_score += 3  # Coût plus élevé pour les ennemis standards
                        elif "chest" in neighbor_info["type"] or "boss" in neighbor_info["type"]:
                            temp_g_score += 1  # Priorité aux coffres et boss
                        else:
                            temp_g_score += 2  # Coût standard
                        
                        # Si nous avons trouvé un meilleur chemin vers ce voisin
                        if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                            # Mettre à jour les scores
                            came_from[neighbor] = current
                            g_score[neighbor] = temp_g_score
                            f_score_val = temp_g_score + self.heuristic(neighbor_x, neighbor_y, target_x, target_y)
                            f_score[neighbor] = f_score_val
                            
                            # Donner une forte priorité aux cases adjacentes au boss si c'est notre cible
                            if goal == dungeon_map["boss_pos"] and abs(neighbor_x - target_x) + abs(neighbor_y - target_y) == 1:
                                f_score_val -= 5  # Bonus pour favoriser le chemin vers le boss
                            
                            # Ajouter le voisin à la liste ouverte
                            heapq.heappush(open_set, (f_score_val, neighbor))
        
        # Si on arrive ici, aucun chemin trouvé
        return None
    
    def find_next_move(self):
        """
        Déterminer la prochaine case où se déplacer, en priorisant:
        1. Le boss si visible
        2. Les coffres si visibles
        3. Les cases non visitées mais accessibles
        4. Un mouvement aléatoire vers une case visitée
        """
        try:
            # Analyser la carte du donjon
            dungeon_map = self.analyze_dungeon_map()
            if not dungeon_map or not dungeon_map["player_pos"]:
                self.log("Impossible d'analyser la carte du donjon ou de trouver la position du joueur")
                return None
            
            player_x, player_y = dungeon_map["player_pos"]
            
            # PRIORITÉ 1: Si le boss est visible, trouver le chemin le plus court vers lui
            if dungeon_map["boss_pos"]:
                boss_x, boss_y = dungeon_map["boss_pos"]
                self.log(f"Boss détecté en ({boss_x}, {boss_y}), calcul du chemin...")
                
                # Analyser la situation pour voir si on peut atteindre le boss en peu de mouvements
                player_x, player_y = dungeon_map["player_pos"]
                manhattan_dist = abs(boss_x - player_x) + abs(boss_y - player_y)
                
                # Vérifier si le boss est directement accessible (adjacent)
                if self.is_directly_accessible(player_x, player_y, boss_x, boss_y, dungeon_map):
                    self.log("Boss directement accessible! Clic direct.")
                    return {
                        "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                        "type": "boss",
                        "direct": True
                    }
                
                # Vérifier si le boss est accessible en un seul mouvement (une case intermédiaire)
                if manhattan_dist == 2:
                    # Case adjacente au boss et au joueur
                    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # haut, droite, bas, gauche
                        intermediate_x, intermediate_y = player_x + dx, player_y + dy
                        
                        # Vérifier si cette case est adjacente au boss
                        if abs(intermediate_x - boss_x) + abs(intermediate_y - boss_y) == 1:
                            # Vérifier si cette case est accessible
                            if (0 <= intermediate_y < dungeon_map["height"] and 
                                0 <= intermediate_x < dungeon_map["width"]):
                                
                                intermediate_info = dungeon_map["rows"][intermediate_y][intermediate_x]
                                if intermediate_info["accessible"]:
                                    self.log(f"Chemin rapide vers le boss via ({intermediate_x}, {intermediate_y})! Clic direct.")
                                    return {
                                        "element": intermediate_info["element"],
                                        "type": "path_to_boss_short",
                                        "direct": True,
                                        "next_target": {
                                            "element": dungeon_map["rows"][boss_y][boss_x]["element"],
                                            "x": boss_x,
                                            "y": boss_y
                                        }
                                    }
                
                # Trouver le chemin vers le boss en passant par des cases visitées
                path = self.find_best_path(player_x, player_y, boss_x, boss_y, dungeon_map)
                if path:
                    next_x, next_y = path[0]
                    self.log(f"Chemin vers le boss trouvé! Prochain mouvement: ({next_x}, {next_y})")
                    return {
                        "element": dungeon_map["rows"][next_y][next_x]["element"],
                        "type": "path_to_boss",
                        "path": path,
                        "direct": False
                    }
            
            # PRIORITÉ 2: Si des coffres sont visibles, trouver le chemin le plus court vers le plus proche
            if dungeon_map["chests"]:
                closest_chest = None
                shortest_path = None
                shortest_distance = float('inf')
                
                for chest_x, chest_y in dungeon_map["chests"]:
                    # Vérifier si le coffre est directement accessible
                    if self.is_directly_accessible(player_x, player_y, chest_x, chest_y, dungeon_map):
                        self.log(f"Coffre directement accessible en ({chest_x}, {chest_y})! Clic direct.")
                        return {
                            "element": dungeon_map["rows"][chest_y][chest_x]["element"],
                            "type": "chest",
                            "direct": True
                        }
                    
                    # Sinon, calculer le chemin vers le coffre
                    path = self.find_best_path(player_x, player_y, chest_x, chest_y, dungeon_map)
                    if path:
                        distance = len(path)
                        if distance < shortest_distance:
                            shortest_distance = distance
                            shortest_path = path
                            closest_chest = (chest_x, chest_y)
                
                if shortest_path:
                    next_x, next_y = shortest_path[0]
                    chest_x, chest_y = closest_chest
                    self.log(f"Chemin vers coffre en ({chest_x}, {chest_y}) trouvé! Prochain mouvement: ({next_x}, {next_y})")
                    return {
                        "element": dungeon_map["rows"][next_y][next_x]["element"],
                        "type": "path_to_chest",
                        "path": shortest_path,
                        "direct": False
                    }
            
            # PRIORITÉ 3: Explorer les cases non visitées mais directement accessibles
            # Vérifier les cases adjacentes à la position du joueur ou aux cases visitées
            for y, row in enumerate(dungeon_map["rows"]):
                for x, cell_info in enumerate(row):
                    # Si la case n'est pas visitée mais est visible (ennemis, cases vides)
                    if ((x, y) not in dungeon_map["visited_tiles"] and 
                        cell_info["type"] not in ["player", "visited"] and
                        cell_info["accessible"]):
                        
                        # Vérifier si cette case est directement accessible depuis le joueur
                        if self.is_directly_accessible(player_x, player_y, x, y, dungeon_map):
                            self.log(f"Case non visitée directement accessible en ({x}, {y})! Clic direct.")
                            return {
                                "element": cell_info["element"],
                                "type": "unexplored",
                                "direct": True
                            }
                        
                        # Sinon, vérifier si elle est accessible depuis une autre case visitée
                        for visited_x, visited_y in dungeon_map["visited_tiles"]:
                            if self.is_directly_accessible(visited_x, visited_y, x, y, dungeon_map):
                                # Trouver le chemin vers cette case visitée
                                path_to_visited = self.find_best_path(player_x, player_y, visited_x, visited_y, dungeon_map)
                                if path_to_visited:
                                    next_x, next_y = path_to_visited[0]
                                    self.log(f"Chemin vers case non visitée en ({x}, {y}) via ({visited_x}, {visited_y})! Prochain mouvement: ({next_x}, {next_y})")
                                    return {
                                        "element": dungeon_map["rows"][next_y][next_x]["element"],
                                        "type": "path_to_unexplored",
                                        "path": path_to_visited,
                                        "next_target": {
                                            "element": cell_info["element"],
                                            "x": x,
                                            "y": y
                                        },
                                        "direct": False
                                    }
            
            # PRIORITÉ 4: Déplacement aléatoire vers une case visitée non récente
            # Déjà implémenté dans la méthode explore_dungeon
            
            return None
            
        except Exception as e:
            self.log(f"Erreur lors de la recherche du prochain mouvement: {str(e)}")
            return None