
import numpy as np
from dataclasses import dataclass,field

@dataclass
class Star:

    id: int
    x: float
    y: float

    richness: float
    habitability: float
    danger: float
    technology: float
    population: int
    resources: dict = field(default_factory=dict)
    @property
    def position(self):
        return np.array([self.x, self.y])


class Universe:

    def __init__(
        self,
        size=500,
        stars=None,
        area_size=100,
        min_distance=2.0,
        seed=None
    ):

        self.rng = np.random.default_rng(seed)

        self.size = size
        self.area_size = area_size
        self.min_distance = min_distance
        self.stars = [] if stars is None else stars    
        self.generate_stars()
        self.precompute_distances()

    def generate_stars(self):

        positions = []
        for i in range(self.size):
            point = self.rng.uniform(0, self.area_size, size=2)

            if positions:
                distances = np.linalg.norm(np.array(positions) - point,axis=1)
                if np.any(distances < self.min_distance):
                    continue
            positions.append(point)

        positions = np.array(positions)

        for i, (x, y) in enumerate(positions):
            richness = round(self.rng.beta(1.7, 2.25),5)
            habitability = round(self.rng.beta(2, 2),5)
            danger = round(self.rng.beta(1.5, 4),5)
            technology = round(self.rng.beta(0.8, 0.7),5)
            population=(self.rng.beta(1.4, 5)*12)+8
            x2=round(x,4)
            y2=round(y,4)
            star = Star(
                id=i,
                x=x2,
                y=y2,
                richness=richness,
                habitability=habitability,
                danger=danger,
                technology=technology,
                population= int(round(10**(population * ((habitability+(1-danger))/2)),-3)),#edited
                resources={
                    "metals": round(self.rng.random(),5),
                    "crystals": round(self.rng.random(),5),
                    "energy": round(self.rng.random(),5),
                    "food": round(self.rng.random(),5),
                    "tourism": round(self.rng.random(),5),
                    "mystisicm": round(self.rng.random(),5),
                    "religion": round(self.rng.random(),5),
                }
            )
            self.stars.append(star)

    def precompute_distances(self):

        positions = np.array([star.position for star in self.stars])

        self.distances = np.linalg.norm(positions[:, None, :] - positions[None, :, :], axis=2)


    def find_near(self, index, max_distance=None, num_near=None):

        distances = self.distances[index]
        candidates = np.where( np.arange(len(self.stars)) != index)[0]
        if max_distance is not None:
            candidates = candidates[distances[candidates] <= max_distance]
        if num_near is not None:
            candidates = candidates[np.argsort(distances[candidates])[:num_near]]
        return candidates
    
    def get_star(self, star_id):
        return self.stars[star_id]


