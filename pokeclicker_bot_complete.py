from selenium.webdriver.common.by import By
from pokeclicker_bot import PokeclickerBot
from pokeclicker_bot_farmer import PokeclickerBotFarmer
from pokeclicker_bot_autoclicker import PokeclickerBotAutoclicker
from pokeclicker_bot_dungeon import PokeclickerBotDungeon

class PokeclickerBotComplete(PokeclickerBot, PokeclickerBotFarmer, PokeclickerBotAutoclicker, PokeclickerBotDungeon):
    """
    Classe complète qui réunit toutes les fonctionnalités du bot
    par héritage multiple des différentes classes de fonctionnalités
    """
    pass