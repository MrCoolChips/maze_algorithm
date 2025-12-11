# Labyrinthe / Egemen YAPSIK

Mini-projet de recherche de chemin dans un labyrinthe modélisé comme un graphe d’états, avec :

- Dijkstra (A* avec heuristique nulle),
- A* avec heuristique **Manhattan**,
- A* avec heuristique **Euclidienne**,
- feu **dynamique**, **statique** ou **absent**.

---

## Structure du projet
.
├── Main.py          # Interface graphique (PySide6) + gestion des scénarios
├── Algorithm.py     # A* / Dijkstra + gestion du feu
├── MapGenerator.py  # Générateur de labyrinthes aléatoires (0/1)
└── __pycache__/     # Fichiers compilés Python (générés automatiquement)

## Prérequis & installation

- Python ≥ 3.9
- PySide6:
	pip install PySide6

## Lancement:
	python Main.py

- Une fenêtre s’ouvre avec :
	* à gauche : le labyrinthe,
	* à droite : les boutons de contrôle et les résultats.

## Types de scénarios

En haut à droite :
	* Labyrinthe aléatoire
		- On choisit le nombre de tests.
		- Chaque test génère un labyrinthe 0/1, place D (départ), S (sortie) et entre 1 et 3 feux F.

	* Je définis mon labyrinthe
		- On choisit le nombre de tests.
		- Pour chaque test :
			-- saisie de N (lignes) et M (colonnes),
			-- puis N lignes de M caractères parmi : . (chemin), # (mur), D (départ), S (sortie), F (feu).

Chaque test affiche : Test i/n + les résultats des algorithmes.

## Algorithmes & résultats

Boutons : Dijkstra, Manhattan, Euclidienne

Pour chaque algorithme, le programme affiche :
	- Résultat : Y si un chemin sûr vers S existe,
	- Résultat : N sinon,
	- Noeuds explorés,
	- Temps d’exécution en millisecondes.

On peut changer d’algorithme à tout moment, la recherche et l’animation sont relancées.

## Modes de feu

Feu dynamique :
	- le feu se propage dans le temps ; A* vérifie que le prisonnier n’entre jamais dans une case déjà en feu au moment de son arrivée.

Feu statique :
	- toutes les cases F sont assimilées à des murs #.

Supprimer le feu :
	- toutes les cases F deviennent des chemins . (feu ignoré).

Les messages importants sont aussi affichés dans la console, par exemple :
	- réussite : Le prisonnier s'échappe avec succès à t=..., position=(x,y), algorithme=...
	- labyrinthe bloqué : [INFO] Aucun chemin possible pour ce test (mode de feu = ...). Labyrinthe bloqué.

Code couleur:
	- Noir : mur #
	- Blanc : chemin .
	- Vert : départ D + trace du chemin parcouru
	- Bleu : position actuelle du prisonnier
	- Rouge : sortie S
	- Orange : feu (F ou case déjà enflammée en mode dynamique)