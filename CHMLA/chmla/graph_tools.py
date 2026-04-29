from collections import deque

from matrix import Matrix
from vector import Vector
from slae import SLAE
from band_gauss import BandMatrixVector, BandGaussianSolver


class SparseGraphMatrix:
    def __init__(self, matrix):
        if matrix.rows != matrix.cols:
            raise ValueError("Матриця для графа має бути квадратною.")
        self.matrix = matrix.copy()
        self.n = matrix.rows
        self._build_graph()

    def _build_graph(self):
        self.adj = [[] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if abs(self.matrix.get(i, j)) > 1e-12 or abs(self.matrix.get(j, i)) > 1e-12:
                    self.adj[i].append(j)
                    self.adj[j].append(i)
        for i in range(self.n):
            self.adj[i].sort()

    def degree(self, vertex):
        return len(self.adj[vertex])

    def neighbors(self, vertex):
        return list(self.adj[vertex])

    def connected_components(self):
        visited = [False] * self.n
        components = []
        for start in range(self.n):
            if visited[start]:
                continue
            queue = deque([start])
            visited[start] = True
            component = []
            while queue:
                vertex = queue.popleft()
                component.append(vertex)
                for neighbor in self.adj[vertex]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        queue.append(neighbor)
            components.append(component)
        return components

    def bfs_levels(self, start):
        if start < 0 or start >= self.n:
            raise IndexError("Початкова вершина поза межами графа.")

        visited = [False] * self.n
        parent = [-1] * self.n
        distance = [-1] * self.n
        queue = deque([start])
        visited[start] = True
        distance[start] = 0
        levels = [[]]

        while queue:
            vertex = queue.popleft()
            level = distance[vertex]
            while len(levels) <= level:
                levels.append([])
            levels[level].append(vertex)

            for neighbor in self.adj[vertex]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    parent[neighbor] = vertex
                    distance[neighbor] = level + 1
                    queue.append(neighbor)

        levels = [level for level in levels if level]
        return {
            "levels": levels,
            "parent": parent,
            "distance": distance,
            "visited": visited,
        }

    def shortest_path(self, start, end):
        if start < 0 or start >= self.n or end < 0 or end >= self.n:
            raise IndexError("Вершина поза межами графа.")

        info = self.bfs_levels(start)
        if not info["visited"][end]:
            return {
                "exists": False,
                "length": None,
                "path": [],
            }

        path = []
        current = end
        while current != -1:
            path.append(current)
            current = info["parent"][current]
        path.reverse()

        return {
            "exists": True,
            "length": len(path) - 1,
            "path": path,
        }

    def gibbs_pseudo_peripheral_vertex(self, start=None):
        if self.n == 0:
            raise ValueError("Порожній граф.")

        if start is None:
            start = min(range(self.n), key=lambda v: (self.degree(v), v))

        current = start
        last_levels_count = -1

        while True:
            info = self.bfs_levels(current)
            levels = info["levels"]
            last_level = levels[-1]
            candidate = min(last_level, key=lambda v: (self.degree(v), v))

            if len(levels) <= last_levels_count or candidate == current:
                return {
                    "vertex": current,
                    "levels": levels,
                    "eccentricity": len(levels) - 1,
                }

            last_levels_count = len(levels)
            current = candidate

    def cuthill_mckee_order(self):
        visited = [False] * self.n
        order = []

        for component in self.connected_components():
            component_set = set(component)
            start = min(component, key=lambda v: (self.degree(v), v))
            pseudo = self.gibbs_pseudo_peripheral_vertex(start=start)["vertex"]

            queue = deque([pseudo])
            seen = {pseudo}
            component_order = []

            while queue:
                vertex = queue.popleft()
                component_order.append(vertex)
                neighbors = [n for n in self.adj[vertex] if n in component_set and n not in seen]
                neighbors.sort(key=lambda v: (self.degree(v), v))
                for neighbor in neighbors:
                    seen.add(neighbor)
                    queue.append(neighbor)

            for vertex in component_order:
                if not visited[vertex]:
                    visited[vertex] = True
                    order.append(vertex)

        return order

    def reverse_cuthill_mckee_order(self):
        order = self.cuthill_mckee_order()
        order.reverse()
        return order

    def permute_matrix(self, order):
        if len(order) != self.n:
            raise ValueError("Невірний порядок перестановки.")
        data = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                row.append(self.matrix.get(order[i], order[j]))
            data.append(row)
        return Matrix(data=data)

    def permute_vector(self, vector, order):
        if vector.size != self.n:
            raise ValueError("Розмір вектора не відповідає матриці.")
        return Vector(data=[vector.get(order[i]) for i in range(self.n)])

    def inverse_permute_vector(self, vector, order):
        if vector.size != self.n:
            raise ValueError("Розмір вектора не відповідає матриці.")
        data = [0.0] * self.n
        for new_index, old_index in enumerate(order):
            data[old_index] = vector.get(new_index)
        return Vector(data=data)

    def bandwidth(self, matrix=None):
        mat = matrix if matrix is not None else self.matrix
        lower = 0
        upper = 0
        for i in range(mat.rows):
            for j in range(mat.cols):
                if abs(mat.get(i, j)) > 1e-12 and i != j:
                    if i > j:
                        lower = max(lower, i - j)
                    else:
                        upper = max(upper, j - i)
        return lower, upper

    def solve_full(self, vector):
        system = SLAE(A=self.matrix, b=vector)
        return system.solve_gauss_general()

    def solve_banded(self, vector, order=None):
        if order is None:
            order = self.reverse_cuthill_mckee_order()

        permuted_a = self.permute_matrix(order)
        permuted_b = self.permute_vector(vector, order)
        lower_bw, upper_bw = self.bandwidth(permuted_a)
        band_matrix = BandMatrixVector.from_dense(permuted_a, lower_bw=lower_bw, upper_bw=upper_bw)
        info = BandGaussianSolver(band_matrix, permuted_b).solve()
        restored_x = self.inverse_permute_vector(info["x"], order)

        return {
            "order": order,
            "permuted_a": permuted_a,
            "permuted_b": permuted_b,
            "bandwidth": (lower_bw, upper_bw),
            "storage_vector": info["storage_vector"],
            "x_permuted": info["x"],
            "x": restored_x,
            "residual": info["residual"],
            "residual_norm": info["residual_norm"],
        }
