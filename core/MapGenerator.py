import random


class MapGenerator:
    """
    Classe utilitaire pour générer un labyrinthe binaire

    0 = case libre (chemin)
    1 = mur
    """

    def __init__(self, width=21, height=21):
        """
        INPUT:
            - width (int)  : largeur de la grille du labyrinthe (nombre de colonnes)
            - height (int) : hauteur de la grille du labyrinthe (nombre de lignes)
        OUTPUT:
            - Aucun retour. L'objet initialise simplement ses attributs internes
        BUT:
            - Initialiser le générateur de labyrinthe avec une largeur et une hauteur données, ainsi qu'une grille vide qui sera remplie par la suite.
        """
        self.width = width
        self.height = height
        self.grid = []

    def generate(self):
        """
        INPUT:
            - Aucun paramètre (utilise self.width et self.height)
        OUTPUT:
            - grid (list[list[int]]) :
                matrice de taille height x width où :
                0 = case libre (chemin),
                1 = mur.
        BUT:
            - Générer un labyrinthe en utilisant l'algorithme du "Recursive Backtracker".
              Le labyrinthe résultant est essentiellement parfait (un seul chemin entre
              deux cellules), puis on ajoute quelques boucles pour l'enrichir
        """
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]

        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = 0
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack[-1]
            neighbors = []

            # On saute de 2 cases pour creuser des couloirs de largeur 1
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (
                    0 < nx < self.width - 1
                    and 0 < ny < self.height - 1
                    and self.grid[ny][nx] == 1
                ):
                    neighbors.append((nx, ny, dx // 2, dy // 2))

            if neighbors:
                nx, ny, wx, wy = random.choice(neighbors)
                # On casse le mur intermédiaire
                self.grid[y + wy][x + wx] = 0
                # On ouvre la nouvelle cellule
                self.grid[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        # On garantit une entrée et une sortie libres
        self.grid[1][1] = 0
        self.grid[self.height - 2][self.width - 2] = 0

        # On ajoute quelques boucles pour éviter un labyrinthe trop linéaire
        self.add_loops(0.1)

        return self.grid

    def add_loops(self, percentage):
        """
        INPUT:
            - percentage (float) :
                proportion de murs internes à convertir en chemin
                (0.0 = aucune boucle, 1.0 = très dense en boucles).
        OUTPUT:
            - Aucun retour direct. Modifie self.grid en place.
        BUT:
            - Casser aléatoirement certains murs pour créer des cycles (boucles)
              dans le labyrinthe, afin qu'il ne soit pas strictement parfait et
              propose plusieurs chemins possibles.
        """
        walls = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 1:

                    neighbors = 0
                    if self.grid[y - 1][x] == 0:
                        neighbors += 1
                    if self.grid[y + 1][x] == 0:
                        neighbors += 1
                    if self.grid[y][x - 1] == 0:
                        neighbors += 1
                    if self.grid[y][x + 1] == 0:
                        neighbors += 1

                    # On ne considère que les murs entourés d'au moins 2 chemins
                    if neighbors >= 2:
                        walls.append((x, y))

        num_to_remove = int(len(walls) * percentage)
        for _ in range(num_to_remove):
            if not walls:
                break
            wx, wy = random.choice(walls)
            self.grid[wy][wx] = 0
            walls.remove((wx, wy))
