import sys
import random
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsScene, QGraphicsView, QGraphicsRectItem,
    QInputDialog, QMessageBox, QLabel
)
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtCore import QTimer, Qt

from Algorithm import Algorithm, compute_fire_time
from MapGenerator import MapGenerator


class LabyrinthApp(QMainWindow):
    """
    APPLICATION PRINCIPALE (interface graphique)

    - Visualisation d'un labyrinthe avec feu dynamique ou statique.
    - L'utilisateur peut :
        * générer des labyrinthes aléatoires,
        * définir ses propres labyrinthes,
        * lancer plusieurs algorithmes (Dijkstra / A* avec diverses heuristiques),
        * comparer le nombre de noeuds explorés et le temps d'exécution.
    """

    def __init__(self):
        """
        INPUT:
            - Aucun paramètre. La fenêtre est construite sans argument extérieur.
        OUTPUT:
            - Aucun retour. Initialise et affiche les composants principaux.
        BUT:
            - Créer la fenêtre principale de l'application, initialiser les
              structures de données internes (tests, grilles, résultats) et
              préparer l'interface utilisateur.
        """
        super().__init__()
        self.setWindowTitle("Labyrinthe / Egemen YAPSIK")
        self.resize(1200, 700)
        self.setMinimumSize(1000, 600)

        # Modes généraux
        self.mode = None              # "random" ou "custom"
        # Algorithmes visibles : "dijkstra", "manhattan", "euclidean"
        self.algorithm_mode = "manhattan"
        # Modes de feu : "dynamic", "static", "none"
        self.fire_mode = "dynamic"

        # Configuration de la grille
        self.cell_size = 12
        self.rows = 0
        self.cols = 0

        # Couleurs
        self.wall_color = QColor("black")
        self.path_color = QColor("white")
        self.start_color = QColor("green")
        self.end_color = QColor("red")
        self.solution_color = QColor("blue")
        self.fire_color = QColor("orange")

        # Composant algorithmique
        self.algo = Algorithm()

        # Liste de tests :
        # chaque élément est un dict :
        # {'grid': [...], 'rows': N, 'cols': M, 'start': (x,y), 'end': (x,y)}
        self.tests = []
        self.num_tests = 0
        self.current_test_index = 0

        # État courant de la grille
        self.grid = []
        self.start = (0, 0)
        self.end = (0, 0)
        self.fire_time = None
        self.path_to_animate = []
        self.current_time = 0
        self.safe_escape = False

        # Résultats des algorithmes
        self.paths = {}        # mode -> chemin trouvé
        self.node_counts = {}  # mode -> nombre de noeuds développés
        self.results = {}      # mode -> 'Y' (succès) ou 'N' (échec)
        self.times = {}        # mode -> temps en millisecondes

        self.setup_ui()

        # Préparer l'écran initial (aucun test, choix de type de labyrinthe)
        QTimer.singleShot(0, self.initial_setup)

    # ---------- UI SETUP ----------
    def setup_ui(self):
        """
        INPUT:
            - Aucun paramètre.
        OUTPUT:
            - Aucun retour. Configure les widgets de la fenêtre.
        BUT:
            - Construire toute l'interface graphique :
              * zone de dessin à gauche,
              * panneaux de contrôle et d'information à droite
              (type de labyrinthe, boutons d'algorithmes, options feu, etc.).
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QHBoxLayout(central_widget)

        # Partie gauche : vue graphique du labyrinthe
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.view)
        outer_layout.addLayout(left_layout, 3)

        # Partie droite : contrôles et informations
        right_layout = QVBoxLayout()
        outer_layout.addLayout(right_layout, 2)

        # --- Boutons de sélection du type de labyrinthe ---
        mode_buttons_layout = QHBoxLayout()
        right_layout.addLayout(mode_buttons_layout)

        self.btn_random_session = QPushButton("Labyrinthe aléatoire")
        self.btn_random_session.clicked.connect(lambda: self.start_session("random"))
        mode_buttons_layout.addWidget(self.btn_random_session)

        self.btn_custom_session = QPushButton("Je définis mon labyrinthe")
        self.btn_custom_session.clicked.connect(lambda: self.start_session("custom"))
        mode_buttons_layout.addWidget(self.btn_custom_session)

        # Label d'information sur le test courant
        self.test_label = QLabel("Choisissez le type de labyrinthe (Aléatoire / Personnalisé)")
        self.test_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        right_layout.addWidget(self.test_label)

        # Label des résultats (Y/N, noeuds, temps)
        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.results_label.setWordWrap(True)
        right_layout.addWidget(self.results_label)

        # Boutons de sélection d'algorithme
        algo_layout = QHBoxLayout()
        right_layout.addLayout(algo_layout)

        self.btn_dijkstra = QPushButton("Dijkstra")
        self.btn_dijkstra.setCheckable(True)
        self.btn_dijkstra.clicked.connect(lambda: self.change_algorithm("dijkstra"))
        algo_layout.addWidget(self.btn_dijkstra)

        self.btn_manhattan = QPushButton("Manhattan")
        self.btn_manhattan.setCheckable(True)
        self.btn_manhattan.clicked.connect(lambda: self.change_algorithm("manhattan"))
        algo_layout.addWidget(self.btn_manhattan)

        self.btn_euclidean = QPushButton("Euclidienne")
        self.btn_euclidean.setCheckable(True)
        self.btn_euclidean.clicked.connect(lambda: self.change_algorithm("euclidean"))
        algo_layout.addWidget(self.btn_euclidean)

        # Boutons de mode de feu
        fire_layout = QHBoxLayout()
        right_layout.addLayout(fire_layout)

        self.btn_fire_dynamic = QPushButton("Feu dynamique")
        self.btn_fire_dynamic.setCheckable(True)
        self.btn_fire_dynamic.clicked.connect(lambda: self.change_fire_mode("dynamic"))
        fire_layout.addWidget(self.btn_fire_dynamic)

        self.btn_fire_static = QPushButton("Feu statique")
        self.btn_fire_static.setCheckable(True)
        self.btn_fire_static.clicked.connect(lambda: self.change_fire_mode("static"))
        fire_layout.addWidget(self.btn_fire_static)

        self.btn_fire_none = QPushButton("Supprimer le feu")
        self.btn_fire_none.setCheckable(True)
        self.btn_fire_none.clicked.connect(lambda: self.change_fire_mode("none"))
        fire_layout.addWidget(self.btn_fire_none)

        # Navigation entre tests
        nav_layout = QHBoxLayout()
        right_layout.addLayout(nav_layout)

        self.btn_prev_test = QPushButton("Test précédent")
        self.btn_prev_test.clicked.connect(self.prev_test)
        nav_layout.addWidget(self.btn_prev_test)

        self.btn_next_test = QPushButton("Test suivant")
        self.btn_next_test.clicked.connect(self.next_test)
        nav_layout.addWidget(self.btn_next_test)

        # Rejouer + Nouveau scénario
        ctrl_layout = QHBoxLayout()
        right_layout.addLayout(ctrl_layout)

        self.btn_replay = QPushButton("Rejouer l'algorithme")
        self.btn_replay.clicked.connect(self.solve_and_animate)
        ctrl_layout.addWidget(self.btn_replay)

        self.btn_new_session = QPushButton("Nouveau scénario")
        self.btn_new_session.clicked.connect(self.initial_setup)
        ctrl_layout.addWidget(self.btn_new_session)

        # Sélections par défaut
        self.set_algorithm_mode("manhattan")
        self.set_fire_mode("dynamic")

    # ---------- INITIAL / SESSION ----------
    def initial_setup(self):
        """
        INPUT:
            - Aucun paramètre.
        OUTPUT:
            - Aucun retour. Réinitialise simplement l'état interne et la vue.
        BUT:
            - Remettre l'application dans un état "neutre" :
              aucun test chargé, aucune animation en cours,
              et inviter l'utilisateur à choisir un type de labyrinthe.
        """
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

        self.tests = []
        self.num_tests = 0
        self.current_test_index = 0
        self.grid = []
        self.fire_time = None
        self.path_to_animate = []
        self.current_time = 0
        self.safe_escape = False
        self.paths = {}
        self.node_counts = {}
        self.results = {}
        self.times = {}

        self.scene.clear()
        self.test_label.setText("Choisissez le type de labyrinthe (Aléatoire / Personnalisé)")
        self.results_label.setText("")

    def start_session(self, mode):
        """
        INPUT:
            - mode (str) : "random" pour labyrinthe aléatoire,
                           "custom" pour labyrinthe défini par l'utilisateur.
        OUTPUT:
            - Aucun retour direct. Configure les tests et charge le premier.
        BUT:
            - Démarrer une nouvelle série de tests :
              * demander combien de cas l'utilisateur souhaite traiter,
              * générer ou lire les labyrinthes correspondants,
              * charger le premier labyrinthe dans l'interface.
        """
        self.initial_setup()
        self.mode = mode

        num, ok = QInputDialog.getInt(
            self,
            "Nombre de tests",
            "Combien de tests voulez-vous exécuter ?",
            1, 1, 100, 1
        )
        if not ok:
            return

        self.num_tests = num

        if mode == "random":
            self.build_random_tests(num)
        else:
            self.build_custom_tests(num)

        if self.num_tests > 0:
            self.load_test(0)

    # ---------- CRÉATION DES TESTS ----------
    def build_random_tests(self, num_tests):
        """
        INPUT:
            - num_tests (int) : nombre de labyrinthes aléatoires à générer.
        OUTPUT:
            - Aucun retour. Remplit self.tests avec les labyrinthes générés.
        BUT:
            - Créer une série de labyrinthes aléatoires avec :
                * taille fixe (rows x cols),
                * un point de départ 'D' et une sortie 'S',
                * entre 1 et 3 sources de feu 'F' placées aléatoirement.
        """
        self.tests = []

        # Dimensions fixes pour le mode aléatoire
        self.rows = 31
        self.cols = 51

        for _ in range(num_tests):
            mg = MapGenerator(self.cols, self.rows)
            numeric_grid = mg.generate()

            # Conversion 0/1 -> caractères
            grid = []
            for y in range(self.rows):
                row_chars = []
                for x in range(self.cols):
                    if numeric_grid[y][x] == 1:
                        row_chars.append('#')
                    else:
                        row_chars.append('.')
                grid.append(row_chars)

            start = (1, 1)
            end = (self.cols - 2, self.rows - 2)
            sx, sy = start
            ex, ey = end
            grid[sy][sx] = 'D'
            grid[ey][ex] = 'S'

            # Feu : entre 1 et 3 sources aléatoires
            fire_count = random.randint(1, 3)
            self.add_random_fire_to_grid(grid, self.rows, self.cols,
                                         count=fire_count, start=start, end=end)

            self.tests.append({
                "grid": grid,
                "rows": self.rows,
                "cols": self.cols,
                "start": start,
                "end": end
            })

    def build_custom_tests(self, num_tests):
        """
        INPUT:
            - num_tests (int) : nombre de labyrinthes manuels à définir.
        OUTPUT:
            - Aucun retour direct. self.tests est rempli avec les labyrinthes entrés.
        BUT:
            - Permettre à l'utilisateur de définir lui-même plusieurs labyrinthes :
              dimensions (N, M), puis chaque ligne constituée des caractères
              '.', '#', 'D', 'S', 'F'. On vérifie au passage qu'il y a bien
              un 'D' et un 'S' dans chaque labyrinthe.
        """
        self.tests = []

        for t in range(num_tests):
            QMessageBox.information(
                self,
                "Nouveau labyrinthe",
                f"Veuillez définir le labyrinthe n°{t+1}."
            )

            N, ok = QInputDialog.getInt(
                self, "Nombre de lignes (N)", "Nombre de lignes (N) :", 10, 2, 200, 1
            )
            if not ok:
                return

            M, ok = QInputDialog.getInt(
                self, "Nombre de colonnes (M)", "Nombre de colonnes (M) :", 10, 2, 200, 1
            )
            if not ok:
                return

            grid = []
            for r in range(N):
                while True:
                    line, ok2 = QInputDialog.getText(
                        self,
                        f"Labyrinthe {t+1}",
                        f"Ligne {r+1}/{N} - {M} caractères (. # D S F) :"
                    )
                    if not ok2:
                        return
                    line = line.strip()
                    if len(line) != M:
                        QMessageBox.warning(self, "Erreur", f"La longueur de la ligne doit être égale à {M}.")
                        continue
                    if any(c not in ".#DSF" for c in line):
                        QMessageBox.warning(
                            self,
                            "Erreur",
                            "Vous ne pouvez utiliser que les caractères '.', '#', 'D', 'S', 'F'."
                        )
                        continue
                    grid.append(list(line))
                    break

            # Vérification de la présence de D et S
            start = None
            end = None
            for y in range(N):
                for x in range(M):
                    if grid[y][x] == 'D':
                        start = (x, y)
                    elif grid[y][x] == 'S':
                        end = (x, y)

            if start is None or end is None:
                QMessageBox.warning(self, "Erreur", "Chaque labyrinthe doit contenir un 'D' et un 'S'.")
                return

            self.tests.append({
                "grid": grid,
                "rows": N,
                "cols": M,
                "start": start,
                "end": end
            })

    # ---------- NAVIGATION ENTRE TESTS ----------
    def load_test(self, index):
        """
        INPUT:
            - index (int) : indice du test à charger (0 <= index < len(self.tests)).
        OUTPUT:
            - Aucun retour direct. Met à jour self.grid et relance la résolution.
        BUT:
            - Charger dans l'interface le test numéro index :
              * copie de la grille,
              * réinitialisation des variables d'animation,
              * lancement automatique de la résolution.
        """
        if not (0 <= index < len(self.tests)):
            return

        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

        self.current_test_index = index
        t = self.tests[index]

        self.rows = t["rows"]
        self.cols = t["cols"]
        self.grid = [row[:] for row in t["grid"]]
        self.start = t["start"]
        self.end = t["end"]

        self.fire_time = None
        self.path_to_animate = []
        self.current_time = 0
        self.safe_escape = False
        self.paths = {}
        self.node_counts = {}
        self.results = {}
        self.times = {}

        self.test_label.setText(f"Test {index+1}/{self.num_tests}")
        self.draw_grid()
        self.solve_and_animate()

    def prev_test(self):
        """Voir docstring précédente (navigation vers test précédent)."""
        if self.current_test_index > 0:
            self.load_test(self.current_test_index - 1)

    def next_test(self):
        """Voir docstring précédente (navigation vers test suivant)."""
        if self.current_test_index + 1 < self.num_tests:
            self.load_test(self.current_test_index + 1)

    # ---------- CONFIGURATION DES BOUTONS ----------
    def set_algorithm_mode(self, mode):
        """
        INPUT:
            - mode (str) :
                "dijkstra", "manhattan" ou "euclidean".
        OUTPUT:
            - Aucun retour. Met à jour l'état des boutons d'algorithme.
        BUT:
            - Définir quel algorithme/heuristique est actuellement sélectionné
              pour l'animation, et synchroniser l'état visuel des boutons.
        """
        self.algorithm_mode = mode
        self.btn_dijkstra.setChecked(mode == "dijkstra")
        self.btn_manhattan.setChecked(mode == "manhattan")
        self.btn_euclidean.setChecked(mode == "euclidean")

    def change_algorithm(self, mode):
        """
        INPUT:
            - mode (str) :
                "dijkstra", "manhattan" ou "euclidean".
        OUTPUT:
            - Aucun retour. Ré-exécute la résolution avec le nouvel algorithme.
        BUT:
            - Réagir à un clic sur un bouton d'algorithme en :
                * mettant à jour le mode sélectionné,
                * relançant la résolution + l'animation pour ce mode.
        """
        self.set_algorithm_mode(mode)
        self.solve_and_animate()

    def set_fire_mode(self, mode):
        """
        INPUT:
            - mode (str) :
                "dynamic", "static" ou "none".
        OUTPUT:
            - Aucun retour. Met à jour l'état des boutons de feu.
        BUT:
            - Indiquer comment le feu doit être pris en compte :
                * "dynamic" : feu qui se propage dans le temps,
                * "static"  : cases en feu considérées comme des murs,
                * "none"    : feu complètement ignoré.
        """
        self.fire_mode = mode
        self.btn_fire_dynamic.setChecked(mode == "dynamic")
        self.btn_fire_static.setChecked(mode == "static")
        self.btn_fire_none.setChecked(mode == "none")

    def change_fire_mode(self, mode):
        """
        INPUT:
            - mode (str) :
                "dynamic", "static" ou "none".
        OUTPUT:
            - Aucun retour. Relance la résolution avec le nouveau mode de feu.
        BUT:
            - Réagir à un clic sur un bouton de mode de feu en :
                * mettant à jour le mode interne,
                * recalculant les chemins et l'animation.
        """
        self.set_fire_mode(mode)
        self.solve_and_animate()

    def add_random_fire_to_grid(self, grid, rows, cols, count=1, start=None, end=None):
        """
        INPUT:
            - grid (list[list[str]]) :
                matrice de caractères modifiable.
            - rows (int) : nombre de lignes de la grille.
            - cols (int) : nombre de colonnes de la grille.
            - count (int) : nombre de sources de feu 'F' à placer.
            - start (tuple[int, int] | None) : position de départ à ne pas enflammer.
            - end (tuple[int, int] | None)   : position d'arrivée à ne pas enflammer.
        OUTPUT:
            - Aucun retour. grid est modifiée en place.
        BUT:
            - Placer aléatoirement quelques sources de feu 'F' dans les cases libres
              ('.'), en évitant explicitement les positions de départ et d'arrivée.
        """
        candidates = []
        for y in range(rows):
            for x in range(cols):
                if grid[y][x] == '.':
                    if start is not None and (x, y) == start:
                        continue
                    if end is not None and (x, y) == end:
                        continue
                    candidates.append((x, y))
        random.shuffle(candidates)
        for i in range(min(count, len(candidates))):
            x, y = candidates[i]
            grid[y][x] = 'F'

    # ---------- DESSIN DE LA GRILLE ----------
    def draw_grid(self, time_step=None, current_pos=None, trail=None):
        """
        INPUT:
            - time_step (int | None) :
                instant actuel de l'animation (pour le feu dynamique).
            - current_pos (tuple[int, int] | None) :
                position actuelle du prisonnier (cellule bleue).
            - trail (list[tuple[int, int]] | None) :
                liste des positions déjà parcourues (trace verte).
        OUTPUT:
            - Aucun retour. Met à jour la scène graphique.
        BUT:
            - Re-dessiner entièrement la grille selon :
                * l'état du labyrinthe (murs, chemins),
                * le mode de feu (dynamique/statique/aucun),
                * la position courante du prisonnier,
                * la trace de son trajet.
        """
        self.scene.clear()

        for y in range(self.rows):
            for x in range(self.cols):
                if not self.grid:
                    continue
                ch = self.grid[y][x]

                if ch == '#':
                    color = self.wall_color
                else:
                    if (
                        self.fire_mode == "dynamic"
                        and time_step is not None
                        and self.fire_time is not None
                    ):
                        if self.fire_time[y][x] <= time_step:
                            color = self.fire_color
                        else:
                            color = self.path_color
                    elif self.fire_mode == "static":
                        if ch == 'F':
                            color = self.fire_color
                        else:
                            color = self.path_color
                    else:
                        color = self.path_color

                self.draw_cell(x, y, color)

        # Dessin du départ et de l'arrivée
        sx, sy = self.start
        ex, ey = self.end
        self.draw_cell(sx, sy, self.start_color)
        self.draw_cell(ex, ey, self.end_color)

        # Trace verte (cases déjà visitées)
        if trail is not None:
            for (tx, ty) in trail:
                if current_pos is not None and (tx, ty) == current_pos:
                    continue
                if (
                    self.fire_mode == "dynamic"
                    and time_step is not None
                    and self.fire_time is not None
                    and self.fire_time[ty][tx] <= time_step
                ):
                    continue
                self.draw_cell(tx, ty, self.start_color)

        # Position actuelle (bleue)
        if current_pos is not None:
            px, py = current_pos
            self.draw_cell(px, py, self.solution_color)

    def draw_cell(self, x, y, color):
        """
        INPUT:
            - x (int) : colonne dans la grille.
            - y (int) : ligne dans la grille.
            - color (QColor) : couleur de remplissage de la cellule.
        OUTPUT:
            - Aucun retour. Ajoute un rectangle à la scène graphique.
        BUT:
            - Dessiner une cellule de taille fixe (self.cell_size) dans la scène,
              en utilisant la couleur spécifiée et un contour gris.
        """
        rect = QGraphicsRectItem(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        rect.setBrush(QBrush(color))
        rect.setPen(QPen(QColor("gray")))
        self.scene.addItem(rect)

    # ---------- PRÉPARATION DES DONNÉES POUR LES ALGORITHMES ----------
    def prepare_grid_and_fire(self):
        """
        INPUT:
            - Aucun paramètre (utilise self.grid et self.fire_mode).
        OUTPUT:
            - (grid_algo, fire_time) :
                * grid_algo (list[list[str]]) : grille adaptée au mode de feu,
                * fire_time (list[list[float]] | None) : temps d'arrivée du feu,
                  ou None si le feu est statique ou absent.
        BUT:
            - Construire la grille à utiliser pour les algorithmes selon le mode
              de feu choisi :
                * dynamic : feu simulé via compute_fire_time,
                * static  : cases 'F' converties en murs '#',
                * none    : feu ignoré, cases 'F' converties en chemins '.'.
        """
        if not self.grid:
            return None, None

        base = [row[:] for row in self.grid]

        if self.fire_mode == "dynamic":
            fire_time = compute_fire_time(base)
            return base, fire_time
        elif self.fire_mode == "static":
            for y in range(self.rows):
                for x in range(self.cols):
                    if base[y][x] == 'F':
                        base[y][x] = '#'
            return base, None
        else:  # "none"
            for y in range(self.rows):
                for x in range(self.cols):
                    if base[y][x] == 'F':
                        base[y][x] = '.'
            return base, None

    def compute_all_algorithms(self):
        """
        INPUT:
            - Aucun paramètre.
        OUTPUT:
            - Aucun retour. Met à jour self.paths, self.node_counts,
              self.results, self.times pour tous les modes.
        BUT:
            - Pour le labyrinthe courant et le mode de feu sélectionné, exécuter
              successivement les trois variantes :
                * Dijkstra (A* avec heuristique zéro),
                * A* Manhattan,
                * A* Euclidienne,
              afin de comparer résultats, noeuds explorés et temps d'exécution.
        """
        grid_algo, self.fire_time = self.prepare_grid_and_fire()
        if grid_algo is None:
            return

        start = self.start
        end = self.end

        self.paths = {}
        self.node_counts = {}
        self.results = {}
        self.times = {}   # temps en ms

        algos = ["dijkstra", "manhattan", "euclidean"]

        for mode in algos:
            t0 = time.perf_counter()

            if self.fire_mode == "dynamic":
                # Feu dynamique : on utilise a_star_with_fire
                h_mode = "zero" if mode == "dijkstra" else mode
                path = self.algo.a_star_with_fire(
                    grid_algo, start, end, self.fire_time, mode=h_mode
                )
            else:
                # Pas de feu dynamique : A* classique
                h_mode = "zero" if mode == "dijkstra" else mode
                path = self.algo.a_star_no_fire(
                    grid_algo, start, end, mode=h_mode
                )

            t1 = time.perf_counter()
            elapsed_ms = (t1 - t0) * 1000.0

            self.paths[mode] = path
            self.node_counts[mode] = self.algo.expanded_nodes
            self.results[mode] = "Y" if path else "N"
            self.times[mode] = elapsed_ms

    def update_results_label(self):
        """
        INPUT:
            - Aucun paramètre.
        OUTPUT:
            - Aucun retour. Met à jour le texte dans self.results_label.
        BUT:
            - Afficher de façon lisible, pour le test courant :
                * le mode de feu choisi,
                * pour chaque variante d'algorithme, le résultat Y/N,
                  le nombre de noeuds explorés et le temps d'exécution en ms.
        """
        if not self.tests:
            self.results_label.setText("")
            return

        idx = self.current_test_index

        fire_mode_display = {
            "dynamic": "dynamique",
            "static": "statique",
            "none": "aucun"
        }.get(self.fire_mode, self.fire_mode)

        text = f"Test {idx+1}/{self.num_tests}\n"
        text += f"Mode de feu : {fire_mode_display}\n\n"

        pretty = {
            "dijkstra": "Dijkstra",
            "manhattan": "A* (Manhattan)",
            "euclidean": "A* (Euclidienne)",
        }

        for key in ["dijkstra", "manhattan", "euclidean"]:
            res = self.results.get(key, "-")
            nodes = self.node_counts.get(key, 0)
            elapsed_ms = self.times.get(key, None)

            if elapsed_ms is not None:
                text += (
                    f"{pretty[key]} -> Résultat : {res}, "
                    f"Noeuds explorés : {nodes}, "
                    f"Temps : {elapsed_ms:.3f} ms\n"
                )
            else:
                text += (
                    f"{pretty[key]} -> Résultat : {res}, "
                    f"Noeuds explorés : {nodes}\n"
                )

        self.results_label.setText(text)

    def solve_and_animate(self):
        """
        INPUT:
            - Aucun paramètre.
        OUTPUT:
            - Aucun retour. Lance une nouvelle résolution et animation.
        BUT:
            - Pour le test et les options actuels :
                * exécuter tous les algorithmes,
                * mettre à jour les statistiques,
                * animer le chemin correspondant à l'algorithme sélectionné.
        """
        if not self.grid:
            return

        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

        # Tous les algos sur la configuration courante
        self.compute_all_algorithms()
        self.update_results_label()

        # --- 1) Si VRAIMENT aucun algorithme ne trouve de chemin ---
        if all(self.results.get(k) == "N" for k in ["dijkstra", "manhattan", "euclidean"]):
            print(
                f"[INFO] Aucun chemin possible pour ce test "
                f"(mode de feu = {self.fire_mode}). Labyrinthe bloqué."
            )

        # Algorithme sélectionné pour l'animation
        alg = self.algorithm_mode

        # --- 2) Choix du chemin à animer en fonction du mode de feu ---
        if self.fire_mode == "dynamic":
            # Cas feu dynamique : on regarde d'abord le chemin vraiment sûr
            dyn_path = self.paths.get(alg, [])
            if dyn_path:
                path_for_anim = dyn_path
                self.safe_escape = True
            else:
                # Aucun chemin sûr -> on anime quand même un chemin "géométrique"
                # sur une grille sans feu (pour visualiser où ça bloque)
                grid_plain, _ = self.prepare_grid_and_fire_for_plain()
                h_mode = "zero" if alg == "dijkstra" else alg
                path_for_anim = self.algo.a_star_no_fire(
                    grid_plain, self.start, self.end, mode=h_mode
                )
                self.safe_escape = False
        else:
            # Feu statique ou supprimé : on anime directement le chemin calculé
            path_for_anim = self.paths.get(alg, [])
            self.safe_escape = bool(path_for_anim)

        # --- 3) Si l'ALGORITHME SÉLECTIONNÉ n'a pas de chemin ---
        if not path_for_anim:
            # Ici, soit tous les algos sont N, soit juste celui-ci.
            print(
                f"[INFO] Aucun chemin pour l'algorithme = {alg} "
                f"(mode de feu = {self.fire_mode})."
            )
            # On redessine simplement la grille (sans animation)
            self.draw_grid(time_step=0, current_pos=None, trail=None)
            return

        # --- 4) Chemin trouvé -> on lance l'animation ---
        self.animate_path(path_for_anim)


    def prepare_grid_and_fire_for_plain(self):
        """
        INPUT:
            - Aucun paramètre.
        OUTPUT:
            - (base, fire_time) :
                * base : grille identique à self.grid où les 'F' sont convertis en '.'
                * fire_time : la matrice fire_time courante (inchangée).
        BUT:
            - Fournir une grille "sans feu" pour animer malgré tout un chemin
              dans le cas où le feu dynamique rend toute fuite impossible.
        """
        base = [row[:] for row in self.grid]
        for y in range(self.rows):
            for x in range(self.cols):
                if base[y][x] == 'F':
                    base[y][x] = '.'
        return base, self.fire_time

    # ---------- ANIMATION ----------
    def animate_path(self, path):
        """
        INPUT:
            - path (list[tuple[int, int]]) :
                chemin à animer (séquence de positions (x, y)).
        OUTPUT:
            - Aucun retour. Initialise et démarre le QTimer.
        BUT:
            - Démarrer l'animation du chemin, en mettant à jour current_time
              et en programmant des appels réguliers à draw_next_step().
        """
        self.path_to_animate = path
        self.current_time = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.draw_next_step)
        self.timer.start(100)  # 100 ms par étape

    def draw_next_step(self):
        """
        INPUT:
            - Aucun paramètre (utilise self.current_time et self.path_to_animate).
        OUTPUT:
            - Aucun retour. Met à jour l'affichage et éventuellement arrête le timer.
        BUT:
            - À chaque "tick" du timer :
                * faire avancer le prisonnier d'une case le long du chemin,
                * mettre à jour le feu (mode dynamique),
                * dessiner la trace des cases déjà parcourues,
                * arrêter l'animation si le prisonnier atteindrait une case en feu
                  (dans le cas sans fuite possible).
        """
        # 1) Animation terminée : on a parcouru tout le chemin
        if self.current_time >= len(self.path_to_animate):
            self.timer.stop()
            if self.path_to_animate:
                last_index = len(self.path_to_animate) - 1
                last_pos = self.path_to_animate[-1]

                # Dernière image complète
                self.draw_grid(
                    time_step=last_index,
                    current_pos=last_pos,
                    trail=self.path_to_animate
                )

                # ---- MESSAGE DE SUCCÈS / FIN D'ANIMATION ----
                if self.safe_escape:
                    # Chemin réellement sûr (Y)
                    print(
                        f"Le prisonnier s'échappe avec succès à t={last_index}, "
                        f"position={last_pos}, algorithme={self.algorithm_mode}."
                    )
                else:
                    # Chemin dessiné, mais on sait que le feu rend l'évasion impossible (N)
                    print(
                        f"Animation terminée pour l'algorithme={self.algorithm_mode} "
                        f"(résultat global N avec feu dynamique)."
                    )
            return

        # 2) Étape normale de l'animation
        t = self.current_time
        x, y = self.path_to_animate[t]

        # Case en feu au temps t ?
        burned_now = (
            self.fire_mode == "dynamic"
            and self.fire_time is not None
            and self.fire_time[y][x] <= t
        )

        # Si on n'a PAS de chemin sûr (safe_escape=False), on arrête juste avant d'entrer dans le feu
        if burned_now and not self.safe_escape:
            if t == 0:
                self.draw_grid(time_step=0, current_pos=self.path_to_animate[0], trail=[])
            else:
                last_t = t - 1
                last_pos = self.path_to_animate[last_t]
                trail = self.path_to_animate[:last_t]
                self.draw_grid(time_step=t, current_pos=last_pos, trail=trail)

            print(
                f"Le prisonnier brûlerait à t={t}, position=({x},{y}), "
                f"algorithme={self.algorithm_mode} -> arrêt avant d'entrer dans le feu."
            )
            self.timer.stop()
            return

        # 3) Cas normal : on avance d'une case
        trail = self.path_to_animate[:t]
        self.draw_grid(time_step=t, current_pos=(x, y), trail=trail)

        self.current_time += 1



if __name__ == "__main__":
    """
    INPUT:
        - Aucun (les paramètres viennent de la ligne de commande si nécessaire).
    OUTPUT:
        - Aucun retour. Lance la boucle principale Qt.
    BUT:
        - Créer l'application Qt, instancier la fenêtre LabyrinthApp et
          démarrer la boucle d'événements.
    """
    app = QApplication(sys.argv)
    window = LabyrinthApp()
    window.show()
    sys.exit(app.exec())
