# PokéClicker Automation

Une application Python pour automatiser diverses tâches dans le jeu [PokéClicker](https://www.pokeclicker.com/), un jeu incrémental basé sur Pokémon.

## Fonctionnalités

- **Farming par route** : Recherche automatique d'un Pokémon spécifique sur une route donnée, avec tentative de capture
- **Auto Clicker** : Clique automatiquement sur les Pokémon à un intervalle défini pour accélérer le farming
- **Automatisation de Donjon** : Explore automatiquement les donjons, trouve et ouvre les coffres, et combat les boss

## Captures d'écran

_À ajouter: Quelques captures d'écran montrant l'interface et les fonctionnalités en action_

## Structure du projet

```
.
├── main.py                      # Point d'entrée principal
├── pokeclicker_bot.py           # Classe de base avec les fonctions communes
├── pokeclicker_bot_farmer.py    # Fonctionnalités de farming par route
├── pokeclicker_bot_autoclicker.py # Fonctionnalités d'auto-click
├── pokeclicker_bot_dungeon.py   # Fonctionnalités d'exploration de donjons
│   ├── pokeclicker_bot_dungeon_base.py       # Fonctions de base pour les donjons
│   ├── pokeclicker_bot_dungeon_combat.py     # Gestion des combats dans les donjons
│   ├── pokeclicker_bot_dungeon_navigation.py # Navigation dans les donjons
│   └── pokeclicker_bot_dungeon_pathfinding.py # Algorithmes de recherche de chemin
├── pokeclicker_bot_complete.py  # Classe qui intègre toutes les fonctionnalités
├── app_ui.py                    # Interface utilisateur CustomTkinter
└── requirements.txt             # Dépendances du projet
```

## Prérequis

- Python 3.7 ou supérieur
- Chrome ou Chromium
- ChromeDriver (compatible avec votre version de Chrome)
- Modules Python requis (voir `requirements.txt`)

## Installation

1. Clonez ce dépôt :

   ```bash
   git clone https://github.com/username/pokeclicker-automation.git
   cd pokeclicker-automation
   ```

2. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

3. Téléchargez ChromeDriver :
   - Rendez-vous sur [le site officiel de ChromeDriver](https://chromedriver.chromium.org/downloads)
   - Téléchargez la version correspondant à votre navigateur Chrome
   - Placez l'exécutable dans un répertoire inclus dans votre PATH système

## Utilisation

Lancez l'application en exécutant :

```bash
python main.py
```

### Guide d'utilisation

1. Cliquez sur "Ouvrir PokéClicker" pour lancer le navigateur avec le jeu
2. Chargez ou démarrez votre partie dans PokéClicker
3. Utilisez l'onglet correspondant à la fonctionnalité souhaitée :

#### Farming par route

- Entrez le nom du Pokémon cible (ex: "Sharpedo")
- Indiquez le numéro de la route où vous souhaitez chercher ce Pokémon (ex: "124")
- Cliquez sur "Démarrer Farming" pour commencer la recherche automatique

#### Auto Clicker

- Ajustez l'intervalle de clic avec le curseur (en millisecondes)
- Cliquez sur "Démarrer Auto Clicker" pour commencer à cliquer automatiquement
- Le bot cliquera sur les Pokémon à l'intervalle défini

#### Automatisation de Donjon

- Indiquez le nombre de donjons à compléter ou activez le mode illimité
- Cliquez sur "Démarrer Automatisation" pour lancer l'exploration automatique des donjons
- Le bot explorera les donjons, ouvrira les coffres et battra les boss automatiquement

### Fonctionnalités avancées

- **Système intelligent de pathfinding** : L'automatisation de donjon utilise un algorithme A\* optimisé pour trouver le chemin le plus efficace vers les coffres et le boss
- **Détection adaptative** : Le bot s'adapte aux différents types de donjons et ajuste sa stratégie en conséquence
- **Gestion des blocages** : Mécanismes intégrés pour détecter et résoudre les situations où le bot pourrait rester bloqué

## Contributions

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des pull requests ou à ouvrir des issues pour signaler des bugs ou proposer des améliorations.

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Avertissement

Cet outil est développé à des fins éducatives et pour une utilisation personnelle. L'automatisation excessive de jeux en ligne peut être contraire aux conditions d'utilisation de certains services. Utilisez ce bot de manière responsable.
