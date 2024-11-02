import random
from math import sqrt, ceil
from collections import namedtuple, deque
import time
import asyncio
import os

from perlin_noise import PerlinNoise
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.core.node import Node
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.dijkstra import DijkstraFinder
import matplotlib.pyplot as plt

Point = namedtuple("Point", "x y")


def define_start_points(grid:Grid):
    # define start & end points
    start = grid.node(random.randint(0, grid.width-1), random.randint(0, grid.height-1))
    while not start.walkable:
        start = grid.node(random.randint(0, grid.width-1), random.randint(0, grid.height-1))
    end = grid.node(random.randint(0, grid.width-1), random.randint(0, grid.height-1))
    while start == end or not end.walkable:
        end = grid.node(random.randint(0, grid.width-1), random.randint(0, grid.height-1))
    return start, end

def find_distance(point1:Point, point2:Point) -> float:
    x1 = point1.x
    x2 = point2.x
    y1 = point1.y
    y2 = point2.y
    return sqrt((x1-x2)**2+(y1-y2)**2)

def calc_path_length(path:list[Node]) -> float:
    distance = 0.0
    for node_id in range(len(path)-2):
        weight_1 = path[node_id].weight
        weight_2 = path[node_id+1].weight
        distance += (weight_1 + weight_2) / 2
    return distance

def load_map(filename:str="map.txt") -> list[list[int]]:
    grid = []
    with open(filename) as f:
        for line in f.readlines():
            row = []
            for char in line.strip():
                row.append(int(char))
            grid.append(row)
    return grid

def burn_path(matrix:list[list[int]], path:list[Node], replace:int=999) -> list[list[int]]:
    for node in path:
        matrix[node.y][node.x] = replace
    return matrix

def run_pathfinder(grid:Grid, points:list[tuple[int, int]], pathfinder, trials:int=500):
    times = []
    path_lengths = []
    distances = []
    runs_left = trials
    print(f"starting {trials} trials for pathfinder {pathfinder}")
    for start, end in points:
        grid.cleanup()
        inittime = time.time()
        path, _ = pathfinder(start, end, grid)
        times.append(str(time.time()-inittime))
        distances.append(str(find_distance(Point(start.x, start.y),
            Point(end.x, end.y))))
        path_lengths.append(str(calc_path_length(path)))
        runs_left -= 1
    return times, distances, path_lengths


def run_map(map_file:str, pathfinders:dict, trials:int=500):
    print(f"loading map {map_file}")
    grid = Grid(matrix=load_map(f"maps/{map_file}.txt"))
    points = []
    print("calculating start/end points")
    for i in range(trials):
        points.append(define_start_points(grid))
    for pathfinder in pathfinders.keys():
        times, distances, path_lengths = \
            run_pathfinder(grid, points, pathfinders[pathfinder], trials)
        output_dir = os.path.join(os.path.curdir, "output", map_file, pathfinder)
        os.makedirs(output_dir, exist_ok=True)
        print(f"exporting data for pathfinder {pathfinder}, map {map_file}")
        data = {
            "time": times,
            "distance": distances,
            "path_distance": path_lengths
        }
        for data_type in data.keys():
            with open(os.path.join(output_dir, f"{data_type}.csv"), "w") as f:
                f.write(",".join(data[data_type]))

if __name__ == "__main__":
    pathfinders = {
        "A-Star": AStarFinder(diagonal_movement=DiagonalMovement.if_at_most_one_obstacle).find_path,
        "Dijkstra": DijkstraFinder(diagonal_movement=DiagonalMovement.if_at_most_one_obstacle).find_path
    }
    for map_file in ["big", "medium", "small"]:
        run_map(map_file=map_file, pathfinders=pathfinders, trials=10**3)

