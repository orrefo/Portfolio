import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import noise


def add_color(world, rules):
    color_world = np.zeros(world.shape[:2] + (3,))

    for i in range(world.shape[0]):
        for j in range(world.shape[1]):

            for rule in rules:
                matches = True

                for dimension, limits in rule["conditions"].items():
                    minimum, maximum = limits
                    value = world[i, j, dimension]

                    if not minimum <= value < maximum:
                        matches = False
                        break

                if matches:
                    color_world[i, j] = np.array(rule["color"]) / 255
                    break

    return color_world

rules = [
    {
        "name": "deep_ocean",
        "conditions": {0: (-1, -0.3)},
        "color": [0, 71, 100]
    },
    {
        "name": "ocean",
        "conditions": {0: (-0.3, -0.2)},
        "color": [65, 105, 255]
    },
    {
        "name": "shallow_ocean",
        "conditions": {0: (-0.2, -0.1)},
        "color": [85, 205, 255]
    },
    {
        "name": "coastal_ocean",
        "conditions": {0: (-0.1, -0.05)},
        "color": [105, 204, 225]
    },
    {
        "name": "beach",
        "conditions": {0: (-0.05, 0.02)},
        "color": [238, 214, 175]
    },

    # DESERTS
    {
        "name": "sand_desert",
        "conditions": {0: (0.02, 0.10), 1: (-1, -0.1)},
        "color": [232, 187, 114]
    },    
    {
        "name": "sand_desert",
        "conditions": {0: (0.1, 0.25), 1: (-1, -0.1)},
        "color": [232, 214, 114]
    },
    {
        "name": "rocky_desert",
        "conditions": {0: (0.25, 0.35), 1: (-1, -0.1)},
        "color": [180, 130, 85]
    },
    {
        "name": "high_desert",
        "conditions": {0: (0.35, 1), 1: (-1, -0.1)},
        "color": [150, 120, 100]
    },

    # LAND
    {
        "name": "grassland",
        "conditions": {0: (0.02, 0.1), 1: (-0.1, 0.2)},
        "color": [34, 139, 34]
    },
       {
        "name": "wet_grassland",
        "conditions": {0: (0.02, 0.1), 1: (0.2, 1)},
        "color": [65, 145, 71]
    },
    {
        "name": "dry_grassland",
        "conditions": {0: (0.1, 0.15), 1: (-0.1, 1)},
        "color": [180, 170, 100]
    },
    {
        "name": "wet_grassland",
        "conditions": {0: (0.15, 0.2), 1: (-0.1, 1)},
        "color": [34, 139, 34]
    },
    {
        "name": "mountain",
        "conditions": {0: (0.2, 0.3), 1: (-0.1, 1)},
        "color": [58, 97, 19]
    },
    {
        "name": "mountain_dark",
        "conditions": {0: (0.3, 0.35), 1: (-0.1, 1)},
        "color": [91, 97, 91]
    },
    {
        "name": "mountain_middle",
        "conditions": {0: (0.35, 0.38), 1: (-0.1, 1)},
        "color": [153, 163, 153]
    },
    {
        "name": "mountain_top",
        "conditions": {0: (0.38, 0.5), 1: (-0.1, 1)},
        "color": [211, 224, 215]
    },
    {
        "name": "snow_peak",
        "conditions": {0: (0.5, 1), 1: (-0.1, 1)},
        "color": [241, 234, 235]
    }
]
dimension_settings = {
    "elevation": {
        "scale": 400.0,
        "octaves": 7,
        "persistence": 0.5,
        "lacunarity": 2,
        "seed_offset": 1
    },

    "rain": {
        "scale": 400.0,
        "octaves": 5,
        "persistence": 0.5,
        "lacunarity": 2,
        "seed_offset": 2
    },

    # "temperature": {
    #     "scale": 600.0,
    #     "octaves": 3,
    #     "persistence": 0.4,
    #     "lacunarity": 2,
    #     "seed_offset": 3
    # }
}



shape = (1000, 1000)
seed = np.random.default_rng().integers(1, 400)
world = np.zeros(shape + (len(dimension_settings),))
c=0
for dim, items in dimension_settings.items():
    
    settings = items
    for i in range(shape[0]):
        for j in range(shape[1]):

            world[i, j, c] = noise.pnoise2(
                i / settings["scale"],
                j / settings["scale"],
                octaves=settings["octaves"],
                persistence=settings["persistence"],
                lacunarity=settings["lacunarity"],
                base=int(seed + settings["seed_offset"])
            )
    c+=1


color_world = add_color(world, rules)
plt.imshow(color_world)