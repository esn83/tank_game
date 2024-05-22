#https://www.youtube.com/watch?v=-L-WgKMFuhE&list=PLFt_AvWsXl0cq5Umv3pMC9SPnKjfp9eGW&index=1

import pygame as pg
import random

class Node:

    def __init__(self,
                 is_walkable_p,
                 grid_x_p,
                 grid_y_p,
                 world_rect_p,   # (x,y,w,h)
                 color_p=None
                 ):

        self.is_walkable = is_walkable_p
        self.grid_x = grid_x_p
        self.grid_y = grid_y_p
        self.world_rect = world_rect_p
        self.color = color_p

        self.g_cost = 0
        self.h_cost = 0
        self.parent = None

    def f_cost(self):
        return self.g_cost + self.h_cost

    # make nodes support < comparison. Is needed for use with heapq.
    def __lt__(self, other_node):
        compare = self.f_cost() < other_node.f_cost()
        if compare:
            return compare
        else:
            return self.h_cost < other_node.h_cost

class Grid:

    def __init__(self,
                 world_rows_p,
                 world_columns_p,
                 world_grid_size_p,
                 grid_rows_p=None,
                 grid_columns_p=None):

        self.world_rows = world_rows_p
        self.world_columns = world_columns_p
        self.world_grid_size = world_grid_size_p
        #unwalkable layermask?

        if grid_rows_p == None:
            self.grid_rows = world_rows_p
        else:
            self.grid_rows = grid_rows_p
        if grid_columns_p == None:
            self.grid_columns = world_columns_p
        else:
            self.grid_columns = grid_columns_p
        self.grid = []
        self.create_grid()

    def create_grid(self):
        for x in range(self.grid_rows):
            row = []
            for y in range(self.grid_columns):
                # check if node is walkable in world map here and pass it to the node
                # test
                walkable = True
                # blocking = random.randint(0,10)
                # if blocking <= 1:
                #     walkable = False
                if walkable:
                    color = pg.Color(200,200,0)
                else:
                    color = pg.Color(255,0,0)
                # / test

                world_rect = (x * self.world_grid_size[0],
                              y * self.world_grid_size[1],
                              self.world_grid_size[0],
                              self.world_grid_size[1])

                node = Node(walkable,
                            x,
                            y,
                            world_rect,
                            color)
                row.append(node)
            self.grid.append(row)

    def node_from_world_point(self, world_point):
        pct_x = world_point[0] / (self.world_rows*self.world_grid_size[0])
        pct_y = world_point[1] / (self.world_columns*self.world_grid_size[1])
        pct_x = self.clamp(pct_x,0,1)
        pct_y = self.clamp(pct_y,0,1)
        x = int(round((self.grid_rows-1)*pct_x,0))
        y = int(round((self.grid_columns-1)*pct_y,0))
        n = self.grid[x][y]
        return n

    def clamp(self, n, min, max): 
        if n < min: 
            return min
        elif n > max: 
            return max
        else: 
            return n

    def get_neighbors(self, node, allow_diagonal=True):
        if allow_diagonal:
            # check all nodes sourrounding node (8 nodes)
            neighbors = []
            for x in range(-1,2):
                for y in range(-1,2):
                    if x==0 and y==0:
                        continue
                    check_x = node.grid_x + x
                    check_y = node.grid_y + y
                    if check_x >= 0 and check_x < self.grid_rows and check_y >= 0 and check_y < self.grid_columns:
                        n = self.grid[check_x][check_y]
                        neighbors.append(n)
        else:
            #check only nodes over, under, left and right of node (4 nodes) and skip the corners
            neighbors = []
            neighbors_list = [(-1,0),(1,0),(0,-1),(0,1)]
            for neighbor in neighbors_list:
                check_x = node.grid_x + neighbor[0]
                check_y = node.grid_y + neighbor[1]
                if check_x >= 0 and check_x < self.grid_rows and check_y >= 0 and check_y < self.grid_columns:
                    n = self.grid[check_x][check_y]
                    neighbors.append(n)

        return neighbors

    def draw_grid(self, surface):
        if self.grid != None:
            for row in self.grid:
                for node in row:
                    if node.is_walkable:
                        node_rect = pg.Rect(node.world_rect)
                        pg.draw.circle(surface, node.color,node_rect.center,5)
                    #else:
                    #    pg.draw.circle(surface, node.color,node_rect.center,5)

    def draw(self, surface):
        self.draw_grid(surface)

# pathfinding with binary heap
import heapq
class Pathfinding:

    def __init__(self, grid_p):
        self.grid = grid_p

    def find_path(self, start_pos, end_pos, allow_diagonal=True):
        
        start_node = self.grid.node_from_world_point(start_pos)
        end_node = self.grid.node_from_world_point(end_pos)

        if start_node.is_walkable and end_node.is_walkable:

            open_set = []
            closed_set = set([])

            heapq.heappush(open_set, start_node)

            while len(open_set) > 0:
                current_node = heapq.heappop(open_set)
                closed_set.add(current_node)

                if current_node == end_node:
                    path = self.retrace_path(start_node, end_node, allow_diagonal)
                    return path

                for neighbor_node in self.grid.get_neighbors(current_node, allow_diagonal):
                    if not neighbor_node.is_walkable or neighbor_node in closed_set:
                        continue

                    new_move_cost_to_neighbor = current_node.g_cost + self.get_node_distance(current_node, neighbor_node)

                    if new_move_cost_to_neighbor < current_node.g_cost or neighbor_node not in open_set:
                        neighbor_node.g_cost = new_move_cost_to_neighbor
                        neighbor_node.h_cost = self.get_node_distance(neighbor_node, end_node)
                        neighbor_node.parent = current_node

                        if neighbor_node not in open_set:
                            heapq.heappush(open_set, neighbor_node)

    def get_node_distance(self, node_a, node_b):
        dist_x = abs(node_a.grid_x - node_b.grid_x)
        dist_y = abs(node_a.grid_y - node_b.grid_y)
        if dist_x > dist_y:
            return 14 * dist_y + 10 * (dist_x - dist_y)
        return 14 * dist_x + 10 * (dist_y - dist_x)

    def retrace_path(self, start_node, end_node, allow_diagonal=True):
        path = []
        current_node = end_node
        while current_node != start_node:
            path.append(current_node)
            current_node = current_node.parent
        path.reverse()

        simpler_path = self.optimize_path(path, allow_diagonal)
        return simpler_path

    def optimize_path(self, path, allow_diagonal=True):
        if len(path) > 0:
            new_path = [path.pop(0)]
            if allow_diagonal:
                for node in path:
                    node_index = path.index(node)
                    if node_index == len(path)-1:
                        new_path.append(node)
                    elif new_path[-1].grid_x == node.grid_x and node.grid_x == path[node_index+1].grid_x:
                        continue
                    elif new_path[-1].grid_y == node.grid_y and node.grid_y == path[node_index+1].grid_y:
                        continue
                    elif node.grid_x == path[node_index+1].grid_x+1 and node.grid_y == path[node_index+1].grid_y+1:
                        continue
                    elif node.grid_x == path[node_index-1].grid_x+1 and node.grid_y == path[node_index+1].grid_y-1:
                        continue
                    elif node.grid_x == path[node_index-1].grid_x+1 and node.grid_y == path[node_index+1].grid_y+1:
                        continue
                    elif node.grid_x == path[node_index+1].grid_x+1 and node.grid_y == path[node_index-1].grid_y+1:
                        continue
                    else:
                        new_path.append(node)
            else:
                for node in path:
                    node_index = path.index(node)
                    if node_index == len(path)-1:
                        new_path.append(node)
                    elif new_path[-1].grid_x == node.grid_x and node.grid_x == path[node_index+1].grid_x:
                        continue
                    elif new_path[-1].grid_y == node.grid_y and node.grid_y == path[node_index+1].grid_y:
                        continue
                    else:
                        new_path.append(node)

            return new_path




# pathfinding without binary heap
# class Pathfinding:

#     def __init__(self, grid_p):
#         self.grid = grid_p

#     def find_path(self, start_pos, end_pos):
        
#         start_node = self.grid.node_from_world_point(start_pos)
#         end_node = self.grid.node_from_world_point(end_pos)

#         if start_node.is_walkable and end_node.is_walkable:

#             open_set = []
#             closed_set = {}

#             open_set.insert(start_node)

#             while len(open_set) > 0:
#                 current_node = open_set[0]
#                 for x in range(len(open_set)):
#                     x_node = open_set[x]
#                     if (x_node.f_cost() < current_node.f_cost()) or (x_node.f_cost() == current_node.f_cost() and x_node.h_cost < current_node.h_cost):
#                         current_node = x_node

#                 open_set.remove(current_node)
#                 closed_set.append(current_node)

#                 if current_node == end_node:
#                     path = self.retrace_path(start_node, end_node)
#                     return path

#                 for neighbor_node in self.grid.get_neighbors(current_node):
#                     if not neighbor_node.is_walkable or neighbor_node in closed_set:
#                         continue

#                     new_move_cost_to_neighbor = current_node.g_cost + self.get_node_distance(current_node, neighbor_node)

#                     if new_move_cost_to_neighbor < current_node.g_cost or neighbor_node not in open_set:
#                         neighbor_node.g_cost = new_move_cost_to_neighbor
#                         neighbor_node.h_cost = self.get_node_distance(neighbor_node, end_node)
#                         neighbor_node.parent = current_node

#                         if neighbor_node not in open_set:
#                             open_set.append(neighbor_node)

#     def get_node_distance(self, node_a, node_b):
#         dist_x = abs(node_a.grid_x - node_b.grid_x)
#         dist_y = abs(node_a.grid_y - node_b.grid_y)
#         if dist_x > dist_y:
#             return 14 * dist_y + 10 * (dist_x - dist_y)
#         return 14 * dist_x + 10 * (dist_y - dist_x)

#     def retrace_path(self, start_node, end_node):
#         path = []
#         current_node = end_node
#         while current_node != start_node:
#             path.append(current_node)
#             current_node = current_node.parent
#         path.append(start_node)
#         path.reverse()
#         # test
#         for node in path:
#             node.color = pg.Color(230,100,100)
#         return path