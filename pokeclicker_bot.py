import threading
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class PokeclickerBot:
    def __init__(self, log_callback=None, status_callback=None):
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.driver = None
        self.running = False
        self.auto_clicking = False
        self.target_pokemon = ""
        self.target_route = ""
        self.autoclicker_interval = 50  # Milliseconds
        self.dungeons_to_run = 0  # Nombre de donjons à exécuter (0 = illimité)
        self.dungeons_completed = 0
        self.clicks = 0
        self.pokemon_found = 0
        self.pokemon_caught = 0
        self.start_time = 0
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def update_status(self, status):
        if self.status_callback:
            self.status_callback(status)
    
    def initialize_browser(self):
        try:
            self.log("Initialisation du navigateur...")
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.log("Navigateur initialisé")
            self.update_status("Navigateur initialisé")
            return True
        except Exception as e:
            self.log(f"Erreur lors de l'initialisation du navigateur: {str(e)}")
            self.update_status("Erreur de navigateur")
            return False
    
    def open_pokeclicker(self, url="https://www.pokeclicker.com/"):
        try:
            if not self.driver:
                if not self.initialize_browser():
                    return False
            
            self.log(f"Ouverture de PokéClicker ({url})...")
            self.driver.get(url)
            self.log("PokéClicker ouvert, veuillez charger ou démarrer votre partie")
            self.update_status("PokéClicker ouvert")
            return True
        except Exception as e:
            self.log(f"Erreur lors de l'ouverture de PokéClicker: {str(e)}")
            self.update_status("Erreur de connexion")
            return False
    
    def close_browser(self):
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.log("Navigateur fermé")
                self.update_status("Déconnecté")
        except Exception as e:
            self.log(f"Erreur lors de la fermeture du navigateur: {str(e)}")
    
    def click_on_route(self, route_number):
        try:
            # Chercher la route par son numéro
            route_selector = f'g[data-bind*="moveToRoute({route_number}"]'
            
            wait = WebDriverWait(self.driver, 5)
            route_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, route_selector)))
            
            # Utiliser directement JavaScript pour déclencher l'événement de clic
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('click'));", route_element)
            
            # Alternative : utiliser le data-bind directement
            # self.driver.execute_script(f"MapHelper.moveToRoute({route_number}, 2);")
            
            self.log(f"Clic sur la route {route_number}")
            return True
        except Exception as e:
            self.log(f"Erreur lors du clic sur la route {route_number}: {str(e)}")
            return False
    
    def get_current_pokemon_name(self):
        try:
            # Sélectionner l'élément qui contient le nom du Pokémon
            pokemon_name_selector = 'knockout[data-bind="text: $data.pokemon.displayName"]'
            
            # Attendre que l'élément soit présent (avec un timeout court)
            try:
                wait = WebDriverWait(self.driver, 2)
                pokemon_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, pokemon_name_selector)))
                
                # Obtenir le nom du Pokémon
                pokemon_name = pokemon_element.text.strip()
                return pokemon_name
            except TimeoutException:
                # Essayer un autre sélecteur (plus générique)
                try:
                    # Vérifier avec le texte
                    elements = self.driver.find_elements(By.XPATH, "//*[contains(@data-bind, 'pokemon.displayName')]")
                    for element in elements:
                        if element.text:
                            return element.text.strip()
                            
                    return None
                except:
                    return None
        except Exception as e:
            self.log(f"Erreur lors de la récupération du nom du Pokémon: {str(e)}")
            return None
    
    def click_on_pokemon(self):
        try:
            # Essayer plusieurs sélecteurs pour trouver l'image du Pokémon
            selectors = [
                'div[data-bind="visible: !Battle.catching()"] img.enemy',  # Premier sélecteur
                'img.enemy',  # Sélecteur plus simple
                'div[data-bind*="Battle.enemyPokemon"] img'  # Autre sélecteur possible
            ]
            
            for selector in selectors:
                try:
                    # Attendre que l'élément soit cliquable
                    wait = WebDriverWait(self.driver, 0.5)  # Temps court pour chaque tentative
                    pokemon_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    # Cliquer sur le Pokémon
                    self.driver.execute_script("arguments[0].click();", pokemon_element)
                    self.clicks += 1
                    return True
                except:
                    continue
            
            # Méthode alternative: utiliser JavaScript pour déclencher un clic sur le Pokémon
            try:
                self.driver.execute_script("Battle.clickAttack();")
                self.clicks += 1
                return True
            except:
                pass
                
            return False  # Aucun sélecteur n'a fonctionné
        except Exception as e:
            self.log(f"Erreur lors du clic sur le Pokémon: {str(e)}")
            return False
    
    def check_capture_notification(self):
        try:
            # Sélectionner la notification de capture spécifique au Pokémon cible
            notification_selector = f'.toast-body:contains("You have captured a {self.target_pokemon}")'
            
            # Vérifier si la notification est présente
            elements = self.driver.find_elements(By.CSS_SELECTOR, '.toast-body')
            for element in elements:
                if f"You have captured a {self.target_pokemon}" in element.text:
                    self.log(f"Notification de capture trouvée pour {self.target_pokemon}")
                    return True
            
            return False
        except Exception as e:
            self.log(f"Erreur lors de la vérification de la notification: {str(e)}")
            return False