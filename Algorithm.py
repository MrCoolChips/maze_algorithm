from collections import deque
import heapq
import math

INF = float("inf")


def compute_fire_time(grid):
    """
    INPUT:
        - grid (list[list[str]]) :
            matrice de caractères de taille N x M représentant le labyrinthe.
            Cellules possibles :
                '#' : mur
                '.' : case libre
                'D' : départ du prisonnier
                'S' : sortie
                'F' : source de feu initiale
    OUTPUT:
        - fire_time (list[list[float]]) :
            matrice de même taille où fire_time[y][x] indique le temps minimal
            (en nombre de pas) pour que le feu atteigne la case (x, y).
            Si la valeur est INF, le feu n'atteint jamais cette case.
    BUT:
        - Calculer, via un BFS multi-source, le temps d'arrivée du feu sur chaque
          case du labyrinthe. Ces temps serviront ensuite à vérifier si le
          prisonnier peut ou non passer par une case à un instant donné.
    """
    rows = len(grid)
    cols = len(grid[0])

    fire_time = [[INF] * cols for _ in range(rows)]
    q = deque()

    # Toutes les sources de feu 'F' sont initialement à t = 0
    for y in range(rows):
        for x in range(cols):
            if grid[y][x] == 'F':
                fire_time[y][x] = 0
                q.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < cols and 0 <= y < rows

    while q:
        x, y = q.popleft()
        t = fire_time[y][x]

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny):
                continue
            if grid[ny][nx] == '#':
                continue  # mur : le feu ne passe pas

            # Le feu arrive dans la case voisine au temps t+1
            if fire_time[ny][nx] > t + 1:
                fire_time[ny][nx] = t + 1
                q.append((nx, ny))

    return fire_time


class Algorithm:
    """
    Classe regroupant les différentes variantes d'algorithmes de recherche de chemin :
    - A* sans feu (a_star_no_fire)
    - A* avec feu dynamique (a_star_with_fire)
    """

    def __init__(self):
        """
        INPUT:
            - Aucun paramètre.
        OUTPUT:
            - Aucun retour. Initialise simplement l'attribut expanded_nodes.
        BUT:
            - Préparer un objet Algorithm en initialisant un compteur de noeuds
              développés (expanded_nodes) qui servira à comparer les heuristiques.
        """
        self.expanded_nodes = 0  # Nombre de noeuds développés pendant la recherche

    def heuristic(self, node, end, mode="manhattan"):
        """
        INPUT:
            - node (tuple[int, int]) :
                coordonnées (x, y) du noeud actuel.
            - end (tuple[int, int]) :
                coordonnées (x, y) du noeud but.
            - mode (str) :
                type d'heuristique à utiliser :
                    "manhattan" : distance de Manhattan
                    "euclidean" : distance euclidienne
                    "zero"      : heuristique nulle (équivalent à Dijkstra)
        OUTPUT:
            - h (float) : estimation du coût pour aller de node à end.
        BUT:
            - Fournir une heuristique cohérente (admissible) pour l'algorithme A*,
              permettant d'orienter la recherche vers la sortie plus efficacement
              qu'une exploration uniforme.
        """
        x1, y1 = node
        x2, y2 = end

        if mode == "manhattan":
            return abs(x1 - x2) + abs(y1 - y2)
        elif mode == "euclidean":
            return math.hypot(x1 - x2, y1 - y2)
        elif mode == "zero":
            return 0
        else:
            # Par défaut, on se rabat sur la distance de Manhattan
            return abs(x1 - x2) + abs(y1 - y2)

    # --- 1) A* classique, sans prise en compte du feu ---
    def a_star_no_fire(self, grid, start, end, mode="manhattan"):
        """
        INPUT:
            - grid (list[list[str]]) :
                matrice de caractères représentant le labyrinthe :
                    '#' : mur (infranchissable)
                    '.', 'D', 'S', 'F' : cases franchissables
                      (on peut décider de traiter 'F' comme un mur si besoin).
            - start (tuple[int, int]) :
                coordonnées (x, y) de départ.
            - end (tuple[int, int]) :
                coordonnées (x, y) d'arrivée.
            - mode (str) :
                nom de l'heuristique à utiliser ("manhattan", "euclidean", "zero").
        OUTPUT:
            - path (list[tuple[int, int]]) :
                liste ordonnée des positions (x, y) formant un chemin de start à end.
                Renvoie une liste vide si aucun chemin n'est trouvé.
        BUT:
            - Appliquer l'algorithme A* classique sur le labyrinthe en ignorant
              totalement la dynamique du feu, afin d'obtenir un chemin
              géométriquement le plus court possible entre start et end.
        """
        rows = len(grid)
        cols = len(grid[0])

        open_heap = []
        g_cost = {start: 0}
        f_start = self.heuristic(start, end, mode)
        heapq.heappush(open_heap, (f_start, start))

        previous = {start: None}
        visited = set()
        self.expanded_nodes = 0

        def in_bounds(x, y):
            return 0 <= x < cols and 0 <= y < rows

        while open_heap:
            f_current, current = heapq.heappop(open_heap)
            if current in visited:
                continue
            visited.add(current)

            if current == end:
                break

            self.expanded_nodes += 1
            x, y = current
            current_g = g_cost[current]

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if not in_bounds(nx, ny):
                    continue

                cell = grid[ny][nx]
                if cell == '#':
                    continue  # mur infranchissable

                neighbor = (nx, ny)
                tentative_g = current_g + 1  # coût d'un pas

                if tentative_g < g_cost.get(neighbor, INF):
                    g_cost[neighbor] = tentative_g
                    previous[neighbor] = current
                    f_neighbor = tentative_g + self.heuristic(neighbor, end, mode)
                    heapq.heappush(open_heap, (f_neighbor, neighbor))

        if end not in previous:
            return []

        # Reconstruction du chemin
        path = []
        cur = end
        while cur is not None:
            path.append(cur)
            cur = previous[cur]
        path.reverse()
        return path

    # --- 2) A* avec feu dynamique ---
    def a_star_with_fire(self, grid, start, end, fire_time, mode="manhattan"):
        """
        INPUT:
            - grid (list[list[str]]) :
                matrice de caractères représentant le labyrinthe.
            - start (tuple[int, int]) :
                coordonnées (x, y) de départ du prisonnier ('D').
            - end (tuple[int, int]) :
                coordonnées (x, y) de la sortie ('S').
            - fire_time (list[list[float]]) :
                matrice des temps d'arrivée du feu, typiquement obtenue via
                compute_fire_time(grid).
            - mode (str) :
                type d'heuristique utilisée par A* ("manhattan", "euclidean", "zero").
        OUTPUT:
            - path (list[tuple[int, int]]) :
                chemin sûr (sans se faire rattraper par le feu) de start à end,
                ou liste vide si aucun chemin sûr n'existe.
        BUT:
            - Étendre l'algorithme A* au cas d'un feu dynamique qui se propage
              dans le labyrinthe. Le prisonnier ne peut rester dans une case (x, y)
              au temps t que si fire_time[y][x] > t (le feu n'est pas encore arrivé).
        """
        rows = len(grid)
        cols = len(grid[0])

        sx, sy = start
        ex, ey = end

        # Si le feu est déjà sur la case de départ à t = 0, aucune solution
        if fire_time[sy][sx] <= 0:
            return []

        open_heap = []
        g_cost = {start: 0}
        f_start = self.heuristic(start, end, mode)
        heapq.heappush(open_heap, (f_start, start))

        previous = {start: None}
        visited = set()
        self.expanded_nodes = 0

        def in_bounds(x, y):
            return 0 <= x < cols and 0 <= y < rows

        while open_heap:
            f_current, current = heapq.heappop(open_heap)

            if current in visited:
                continue
            visited.add(current)

            x, y = current
            t = g_cost[current]  # temps courant (nombre de pas depuis le départ)

            # On ne peut pas rester sur une case déjà en feu à l'instant t
            if fire_time[y][x] <= t:
                continue

            if current == end:
                break

            self.expanded_nodes += 1

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if not in_bounds(nx, ny):
                    continue

                cell = grid[ny][nx]
                if cell == '#':
                    continue  # mur

                new_t = t + 1  # temps une fois déplacé dans la case voisine

                # On ne peut pas entrer dans une case en feu à new_t
                if fire_time[ny][nx] <= new_t:
                    continue

                neighbor = (nx, ny)
                if new_t < g_cost.get(neighbor, INF):
                    g_cost[neighbor] = new_t
                    previous[neighbor] = current
                    f_neighbor = new_t + self.heuristic(neighbor, end, mode)
                    heapq.heappush(open_heap, (f_neighbor, neighbor))

        if end not in previous:
            return []

        # Reconstruction du chemin sûr
        path = []
        cur = end
        while cur is not None:
            path.append(cur)
            cur = previous[cur]
        path.reverse()
        return path
