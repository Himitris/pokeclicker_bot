# PokéClicker Automation

Une application pour automatiser certaines tâches dans le jeu [PokéClicker](https://www.pokeclicker.com/).

## Fonctionnalités

- **Farming par route** : Cherche automatiquement un Pokémon spécifique sur une route donnée
- **Auto Clicker** : Clique automatiquement sur les Pokémon à un intervalle défini
- **Automatisation de Donjon** : Explore automatiquement les donjons et combat les boss

## Structure du projet

```
.
├── main.py                      # Point d'entrée principal
├── pokeclicker_bot.py           # Classe de base avec les fonctions communes
├── pokeclicker_bot_farmer.py    # Fonctionnalités de farming
├── pokeclicker_bot_autoclicker.py # Fonctionnalités d'auto-click
├── pokeclicker_bot_dungeon.py   # Fonctionnalités d'exploration de donjons
├── pokeclicker_bot_complete.py  # Classe qui hérite de toutes les fonctionnalités
├── app_ui.py                    # Interface utilisateur CustomTkinter
└── requirements.txt             # Dépendances du projet
```

## Prérequis

- Python 3.7 ou supérieur
- Chrome ou Chromium
- ChromeDriver (compatible avec votre version de Chrome)

## Installation

1. Clonez ce dépôt
2. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```
3. Assurez-vous que ChromeDriver est installé et dans votre PATH

## Utilisation

Lancez l'application en exécutant :

```
python main.py
```

### Mode d'emploi

1. Cliquez sur "Ouvrir PokéClicker" pour lancer le navigateur
2. Chargez ou démarrez votre partie dans PokéClicker
3. Utilisez l'onglet correspondant à la fonctionnalité souhaitée :
   - **Farming par route** : Entrez le nom du Pokémon et la route cible
   - **Auto Clicker** : Ajustez l'intervalle de clic
   - **Automatisation de Donjon** : Configurez le nombre de donjons à compléter

## License

Ce projet est distribué sous licence MIT.