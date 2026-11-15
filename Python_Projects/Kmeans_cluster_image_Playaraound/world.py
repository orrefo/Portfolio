import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import noise
    from skimage.graph import route_through_array
    import vnoise

    return np, plt, route_through_array, vnoise


@app.cell
def _(np):

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

    return (add_color,)


@app.cell
def _():

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
            "conditions": {0: (0.02, 0.1), 1: (0.2, 10)},
            "color": [65, 145, 71]
        },
        {
            "name": "dry_grassland",
            "conditions": {0: (0.1, 0.15), 1: (-0.1, 10)},
            "color": [180, 170, 100]
        },
        {
            "name": "wet_grassland",
            "conditions": {0: (0.15, 0.2), 1: (-0.1, 10)},
            "color": [34, 139, 34]
        },
        {
            "name": "mountain",
            "conditions": {0: (0.2, 0.3), 1: (-0.1, 10)},
            "color": [58, 97, 19]
        },
        {
            "name": "mountain_dark",
            "conditions": {0: (0.3, 0.35), 1: (-0.1, 10)},
            "color": [91, 97, 91]
        },
        {
            "name": "mountain_middle",
            "conditions": {0: (0.35, 0.38), 1: (-0.1, 10)},
            "color": [153, 163, 153]
        },
        {
            "name": "mountain_top",
            "conditions": {0: (0.38, 0.4), 1: (-0.1, 10)},
            "color": [211, 224, 215]
        },
        {
            "name": "snow_peak",
            "conditions": {0: (0.4, 1), 1: (-0.1, 10)},
            "color": [241, 234, 235]
        }
    ]
    dimension_settings = {
        "elevation": {
            "scale": 2,
            "octaves": 7,
            "persistence": 0.5,
            "lacunarity": 2.2,
        },

        "rain": {
            "scale": 3,
            "octaves": 4,
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
    shape = (600, 800)
    return dimension_settings, rules, shape


@app.cell
def _(dimension_settings, np, shape, vnoise):
    seed2 = np.random.default_rng().integers(1, 10_000_000)


    pnoise=vnoise.Noise()
    pnoise.seed(int(seed2))
    world2 = np.zeros(shape + (len(dimension_settings),))
    c2=0
    for dim2, items2 in dimension_settings.items():
        settings2 = items2
        x3 = np.linspace(0,settings2['scale'], shape[0],)
        y3 = np.linspace(0,settings2['scale'], shape[1])
        world2[:, :, c2] = pnoise.noise2(
            x3,
            y3,
            octaves=settings2["octaves"],
            persistence=settings2["persistence"],
            lacunarity=settings2["lacunarity"]
        )
        c2+=1


    return pnoise, settings2, world2


@app.cell
def _(add_color, plt, rules, world2):
    color_world2 = add_color(world2, rules)
    plt.imshow(color_world2)
    return (color_world2,)


@app.cell
def _(color_world2, np, plt, route_through_array, world2):

    max_altitude=-0.08
    randomness=20
    chunk_size=60
    area_search_remove=80

    altitude2 = world2[:, :, 0].copy()
    terrain_modify = altitude2.copy()
    rain_modify = world2[:, :, 1].copy()
    altitude_search=altitude2.copy()
    plt.imshow(color_world2)
    all_chunks=[]
    found=True
    while found == True:
        found= False
        # Highest pixel in this quadrant
        lx2, ly2 = np.unravel_index(np.argmax(altitude_search), altitude_search.shape)
    
        start2 = (lx2, ly2)
        x_min = max(0, lx2 - area_search_remove)
        x_max = min(altitude_search.shape[0], lx2 + area_search_remove + 1)
        y_min = max(0, ly2 - area_search_remove)
        y_max = min(altitude_search.shape[1], ly2 + area_search_remove + 1)

        altitude_search[x_min:x_max, y_min:y_max] = 0
        # Find pixels below the threshold in this quadrant
        candidates2 = np.argwhere(altitude2 < max_altitude)
        # Closest eligible pixel to the start
        distances2 = np.linalg.norm(candidates2 - start2, axis=1)
        end2 = tuple(candidates2[np.argmin(distances2)])
    
        # plt.scatter(start2[1], start2[0], s=5,color='deepskyblue')
        # path2 
    
        rows2, cols2 = np.indices(altitude2.shape)
        distance3 = np.sqrt((rows2 - start2[0])**2 +(cols2 - start2[1])**2)
        rnoise3 = np.random.uniform(0, randomness, altitude2.shape)
        # Increase noise with distance
        random_altitude_3 = altitude2 +  (distance3**2) * rnoise3
    
        path3,cost3=route_through_array(random_altitude_3,start2,end2)    
        path3 = np.array(path3)
        chunk_rand = np.random.default_rng().integers(0, randomness)
        chunks = [path3[i:i + chunk_size+chunk_rand] for i in range(0, len(path3), chunk_size+chunk_rand)]
    
        all_chunks.append(chunks)
        for i, chunk in enumerate(chunks):
            size = i + 1
            radius = size * 2
    
            for row, col in chunk:
                r0 = max(0, row - radius)
                r1 = min(terrain_modify.shape[0], row + radius + 1)
                c0 = max(0, col - radius)
                c1 = min(terrain_modify.shape[1], col + radius + 1)
    
                rr, cc = np.ogrid[r0:r1, c0:c1]
    
                mask = (rr - row)**2 + (cc - col)**2 <= radius**2 
                mask2 = (rr - row)**2 + (cc - col)**2 <= radius +55
    
                # Lower the terrain within the circular radius
                terrain_modify[r0:r1, c0:c1][mask] -= 0.02
                rain_modify[r0:r1, c0:c1][mask2] += 0.2
            plt.plot(chunk[:, 1], chunk[:, 0],  color='deepskyblue',linewidth=size)

        if altitude2[start2]>=0.15:
            found=True


    # Extract coordinates from path
    
    plt.show()
    return all_chunks, rain_modify, terrain_modify


@app.cell
def _(add_color, all_chunks, plt, rain_modify, rules, terrain_modify, world2):
    world3= world2.copy()
    world3[:, :, 0]= terrain_modify
    world3[:, :, 1]= rain_modify
    color_world3 = add_color(world3, rules)
    plt.imshow(color_world3)
    for paths in all_chunks:
        for i2, chunk2 in enumerate(paths):
            size2 = i2 + 1
            plt.plot(chunk2[:, 1], chunk2[:, 0],  color='deepskyblue',linewidth=size2)
    plt.show()
    return


@app.cell
def _():
    dimension_settings2 = {
        "elevation": {
            "scale": 2,
            "octaves": 7,
            "persistence": 0.5,
            "lacunarity": 2.2,
            "seed_offset": 0
        },

        "rain": {
            "scale": 3,
            "octaves": 4,
            "persistence": 0.5,
            "lacunarity": 2,
            "seed_offset": 2
        },

        "temperature": {
            "scale": 6.0,
            "octaves": 3,
            "persistence": 0.4,
            "lacunarity": 2,
            "seed_offset": 3
        },

        "variation": {
            "scale": 12.0,
            "octaves": 3,
            "persistence": 0.55,
            "lacunarity": 2,
            "seed_offset": 4
        }
    }
    return (dimension_settings2,)


@app.cell
def _():

    # Noise dimensions:
    # 0 = elevation
    # 1 = rainfall
    # 2 = temperature
    # 3 = variation

    NOISE_MIN = -1.0
    NOISE_MAX = 1.000001  # Include values equal to 1.0


    # --------------------------------------------------
    # 1. CLIMATE BINS
    # --------------------------------------------------

    TEMPERATURE_BINS = [
        ("polar",      -1.0, -0.65),
        ("cold",       -0.65, -0.30),
        ("cool",       -0.30,  0.00),
        ("temperate",   0.00,  0.40),
        ("hot",         0.40,  NOISE_MAX),
    ]

    RAINFALL_BINS = [
        ("arid",       -1.0, -0.45),
        ("dry",        -0.45, -0.15),
        ("moderate",   -0.15,  0.25),
        ("wet",         0.25,  NOISE_MAX),
    ]

    VARIATION_BINS = [
        ("sparse", -1.0, -0.33),
        ("normal", -0.33, 0.33),
        ("dense",   0.33, NOISE_MAX),
    ]

    ELEVATION_BINS = [
        ("lowland",       0.02, 0.20),
        ("foothills",     0.20, 0.30),
        ("mountains",     0.30, 0.40),
        ("high_mountains", 0.40, NOISE_MAX),
    ]


    # --------------------------------------------------
    # 2. CLIMATE -> BIOME
    #
    # Rows: temperature, from cold to hot
    # Columns: rainfall, from arid to wet
    # --------------------------------------------------

    CLIMATE_BIOMES = {
        "polar": [
            "polar_desert",
            "tundra",
            "tundra",
            "wet_tundra",
        ],
        "cold": [
            "cold_desert",
            "cold_steppe",
            "taiga",
            "boreal_forest",
        ],
        "cool": [
            "cold_steppe",
            "grassland",
            "temperate_grassland",
            "temperate_forest",
        ],
        "temperate": [
            "desert",
            "shrubland",
            "grassland",
            "temperate_forest",
        ],
        "hot": [
            "hot_desert",
            "savanna",
            "tropical_dry_forest",
            "tropical_rainforest",
        ],
    }


    # --------------------------------------------------
    # 3. COLORS
    # --------------------------------------------------

    BIOME_COLORS = {
        # Water and coast
        "deep_ocean":       [0, 71, 100],
        "ocean":             [65, 105, 255],
        "shallow_ocean":     [85, 205, 255],
        "coastal_ocean":     [105, 204, 225],
        "beach":             [238, 214, 175],

        # Cold climates
        "polar_desert":      [195, 205, 210],
        "tundra":            [160, 175, 150],
        "wet_tundra":        [115, 145, 130],
        "cold_desert":       [175, 160, 135],
        "cold_steppe":       [150, 160, 115],
        "taiga":             [55, 90, 65],
        "boreal_forest":     [35, 85, 60],

        # Temperate climates
        "grassland":         [140, 170, 80],
        "temperate_grassland": [125, 160, 90],
        "shrubland":         [165, 155, 100],
        "temperate_forest":  [34, 110, 55],

        # Hot climates
        "desert":            [232, 187, 114],
        "hot_desert":        [225, 175, 95],
        "savanna":           [195, 175, 85],
        "tropical_dry_forest": [65, 130, 55],
        "tropical_rainforest": [15, 110, 45],

        # Higher terrain
        "rocky_mountains":   [130, 120, 105],
        "mountain_grassland": [100, 125, 80],
        "mountain_forest":   [65, 95, 70],
        "alpine_tundra":     [155, 165, 155],
        "high_mountain":     [125, 130, 130],
        "snow_peak":         [241, 234, 235],
    }


    # --------------------------------------------------
    # 4. TERRAIN CLASSIFICATION
    # --------------------------------------------------

    def get_land_biome(elevation_name, temp_index, rain_index):
        temp_name = TEMPERATURE_BINS[temp_index][0]
        rain_name = RAINFALL_BINS[rain_index][0]

        # Climate determines the lowland biome.
        biome = CLIMATE_BIOMES[temp_name][rain_index]

        if elevation_name == "lowland":
            return biome

        if elevation_name == "foothills":
            # Foothills retain their climate identity.
            return f"foothill_{biome}"

        if elevation_name == "mountains":
            # Cold high terrain becomes alpine tundra.
            if temp_index <= 1:
                return "alpine_tundra"

            # Dry high terrain is rocky.
            if rain_index <= 1:
                return "rocky_mountains"

            # Wet, relatively warm high terrain supports forests.
            if rain_index == 3 and temp_index <= 3:
                return "mountain_forest"

            return "mountain_grassland"

        if elevation_name == "high_mountains":
            if temp_index <= 1:
                return "snow_peak"

            return "high_mountain"

        raise ValueError(f"Unknown elevation: {elevation_name}")


    # --------------------------------------------------
    # 5. COLOR HELPERS
    # --------------------------------------------------

    def get_biome_color(biome, variation_name):
        # Foothills use their underlying climate biome color.
        color_key = biome

        if biome.startswith("foothill_"):
            color_key = biome[len("foothill_"):]

        base = BIOME_COLORS.get(
            color_key,
            BIOME_COLORS.get(biome, [120, 120, 110])
        )

        # Variation affects the shade as well as the tile name.
        if variation_name == "sparse":
            factor = 1.12
        elif variation_name == "dense":
            factor = 0.88
        else:
            factor = 1.0

        return [
            max(0, min(255, int(channel * factor)))
            for channel in base
        ]


    # --------------------------------------------------
    # 6. GENERATE ALL RULES
    # --------------------------------------------------

    rules1 = [
        # Water and beaches depend on elevation only.
        {
            "name": "deep_ocean",
            "conditions": {0: (-1.0, -0.30)},
            "color": [0, 71, 100],
        },
        {
            "name": "ocean",
            "conditions": {0: (-0.30, -0.20)},
            "color": [65, 105, 255],
        },
        {
            "name": "shallow_ocean",
            "conditions": {0: (-0.20, -0.10)},
            "color": [85, 205, 255],
        },
        {
            "name": "coastal_ocean",
            "conditions": {0: (-0.10, -0.05)},
            "color": [105, 204, 225],
        },
        {
            "name": "beach",
            "conditions": {0: (-0.05, 0.02)},
            "color": [238, 214, 175],
        },
    ]


    # Generate all land combinations.
    for elevation_name, elev_min, elev_max in ELEVATION_BINS:
        for temp_index, (temp_name, temp_min, temp_max) in enumerate(
            TEMPERATURE_BINS
        ):
            for rain_index, (rain_name, rain_min, rain_max) in enumerate(
                RAINFALL_BINS
            ):
                biome = get_land_biome(
                    elevation_name,
                    temp_index,
                    rain_index,
                )

                for variation_name, var_min, var_max in VARIATION_BINS:
                    rules1.append({
                        "name": f"{variation_name}_{biome}",
                        "conditions": {
                            0: (elev_min, elev_max),
                            1: (rain_min, rain_max),
                            2: (temp_min, temp_max),
                            3: (var_min, var_max),
                        },
                        "color": get_biome_color(
                            biome,
                            variation_name,
                        ),
                    })


    print("Total rules:", len(rules1))
    # Expected: 245

    return (rules1,)


@app.cell
def _(dimension_settings2, np, pnoise, settings2, shape):
    world1 = np.zeros(shape + (len(dimension_settings2),))
    c11=0
    for dim11, items11 in dimension_settings2.items():
        settings11 = items11
        x11 = np.linspace(0,settings2['scale'], shape[0],)
        y11= np.linspace(0,settings2['scale'], shape[1])
        world1[:, :, c11] = pnoise.noise2(
            x11,
            y11,
            octaves=settings11["octaves"],
            persistence=settings11["persistence"],
            lacunarity=settings11["lacunarity"]
        )
        c11+=1
    world1[:,:,0]=world1[:,:,0]*2
    world1[:,:,1]=world1[:,:,1]*2
    world1[:,:,2]=world1[:,:,2]*2
    world1[:,:,3]=world1[:,:,3]*2
    return (world1,)


@app.cell
def _(world1):
    world1[:,:,2].min()
    return


@app.cell
def _(add_color, plt, rules1, world1):
    color_world1=add_color(world1,rules1)
    plt.imshow(color_world1)
    return


if __name__ == "__main__":
    app.run()
