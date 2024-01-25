import json
import random


class AntColonyOptimizer:
    def __init__(self, graph, danger, d_threshold, num_ants, num_iterations, alpha=1, beta=1, evaporation_rate=0.6, q=1):
        self.graph = graph
        self.danger = danger
        self.d_threshold = d_threshold
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.q = q
        self.num_nodes = len(graph)
        self.pheromone = [[1 / self.num_nodes] * self.num_nodes for _ in range(self.num_nodes)]

    def run(self, start_node, end_node, required_nodes):
        best_path = None
        best_path_length = float('inf')

        for _ in range(self.num_iterations):
            paths = []

            for _ in range(self.num_ants):
                path = self.construct_path(start_node, end_node, required_nodes)
                paths.append(path)

                if path[-1] == end_node and len(path) < best_path_length:
                    best_path = path
                    best_path_length = len(path)

            self.update_pheromone(paths)

        return best_path

    def construct_path(self, start_node, end_node, required_nodes):
        path = [start_node]
        visited_nodes = [start_node]

        while path[-1] != end_node or not set(required_nodes).issubset(visited_nodes):
            next_node = self.select_next_node(path[-1], visited_nodes, required_nodes)
            path.append(next_node)
            visited_nodes.append(next_node)

        return path

    def select_next_node(self, current_node, visited_nodes, required_nodes):
        unvisited_nodes = [node for node in range(self.num_nodes) if node not in visited_nodes]
        unvisited_required_nodes = [node for node in unvisited_nodes if node in required_nodes
                                    and self.graph[current_node][node] != 0]

        # Doens't really exclude dangerous points...
        # for node in unvisited_required_nodes:
        #     if self.danger[node] >= self.d_threshold:
        #         unvisited_nodes.remove(node)

        if unvisited_required_nodes:
            next_node = random.choice(unvisited_required_nodes)
        else:
            probabilities = [
                self.pheromone[current_node][node] ** self.alpha * (1 / self.graph[current_node][node]) ** self.beta
                for node in unvisited_nodes]
            total_probability = sum(probabilities)
            probabilities = [prob / total_probability for prob in probabilities]
            next_node = random.choices(unvisited_nodes, probabilities)[0]

        return next_node

    def update_pheromone(self, paths):
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                self.pheromone[i][j] *= self.evaporation_rate

        for path in paths:
            for i in range(len(path) - 1):
                node1 = path[i]
                node2 = path[i + 1]
                self.pheromone[node1][node2] += self.q / len(path)
                self.pheromone[node2][node1] += self.q / len(path)

