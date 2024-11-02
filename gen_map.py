from perlin_noise import PerlinNoise
def generate_grid(rows:int, columns:int, seed:int=1) -> list[list[int]]:
    noise = PerlinNoise(octaves=6, seed=seed)
    grid = []
    for y in range(rows):
        row = []
        for x in range(columns):
            value = noise((x/columns, y/rows)) + 0.4
            if value > 0:
                value *= 10
                value = int(value)
            else:
                value = 0
            row.append(value)
        grid.append(row)
    return grid

maps = {
    "small": (50, 50),
    "medium": (200, 200),
    "big": (500, 500)
}

for map_type in maps:
    seed = int(map_type.encode("utf8").hex(), 16)
    with open(f"maps/{map_type}.txt", "w") as f:
        for row in generate_grid(maps[map_type][0], maps[map_type][1], seed):
            for cell in row:
                f.write(str(cell))
            f.write("\n")