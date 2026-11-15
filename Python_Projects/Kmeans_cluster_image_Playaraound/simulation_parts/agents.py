
import numpy as np
import namer

class Agent:

    def __init__(
        self,
        agent_id,
        home_world,
        speed=1.0,
        jump_range=10.0,
        fallback_jumps=10,
        exploration_drive = 0.8,
        trade_drive = 0.3,
        research_drive = 0.6,
        risk_tolerance = 0.5,
        homesickness = 100,
        mission_type = 'survey',
    ):
        self.id = agent_id

        # Location
        self.rng = np.random.default_rng()
        self.home_world = home_world
        self.current_world = home_world

        # Movement
        self.speed = speed
        self.jump_range = jump_range
        self.fallback_jumps = fallback_jumps
        self.x = None
        self.y = None

        # Internal characteristics
        self.exploration_drive = exploration_drive
        self.trade_drive = trade_drive
        self.research_drive = research_drive
        self.risk_tolerance = risk_tolerance
        self.homesickness = homesickness
        

        # Mission
        self.days_from_home=0
        self.next_star = None
        self.travel_progress = 0.0
        self.mission_type = mission_type
        self.destination=None
        self.target = None
        self.progress = 0
        self.required_survey = 10
        self.required_explore = 50
        self.completed = False
        self.state = "idle"
        # Knowledge
        self.known_stars = {}
        self.visited_stars = set()
        self.scanned_stars = {}


    # ----------------------------------
    # 1. OBSERVE
    # ----------------------------------

    def discover(self, universe, star_id):

        if star_id in self.scanned_stars:
            return 
        star = universe.get_star(star_id)
        self.scanned_stars[star_id] = star

    def observe(self, universe):

        current = self.current_world

        # Discover current star
        self.discover(universe, current)

        # Record visit
        self.visited_stars.add(current)

        # Discover nearby stars
        nearby = universe.find_near(current,self.fallback_jumps)
        for star_id in nearby:
            if star_id not in self.known_stars.keys():
                star = universe.get_star(star_id)
                self.known_stars[star_id]=star.position
            
    # ----------------------------------
    # 2. DECIDE
    # ----------------------------------
    def decide(self, universe):

        if self.completed:
            self.state = "mission_complete"
            self.next_star = None
            self.completed=None
            return
        # Don't interrupt an existing journey
        if self.next_star is not None:
            return
            
        self.choose_next_star(universe)

    
    def get_reachable_stars(self, universe):

        candidates = universe.find_near(
            self.current_world,
            max_distance=self.jump_range
        )

        # Emergency long-distance jumps
        if len(candidates) == 0:
            candidates = universe.find_near(
                self.current_world,
                num_near=self.fallback_jumps
            )

        return candidates
    
    def choose_next_star(self, universe):

        candidates = self.get_reachable_stars(universe)

        # Fixed destination missions
        if self.mission_type in ("courier", "trader", "returner"):

            if self.mission_type == "returner":
                target = self.home_world
            else:
                target = self.destination

            # Already at destination
            if self.current_world == target:
                self.state = "idle"
                return

            current_distance = universe.distances[self.current_world, target]
            distances = universe.distances[candidates, target]
            better = candidates[distances < current_distance]
            if len(better) > 0:
                candidates = better

            self.next_star = candidates[
                np.argmin(universe.distances[candidates, target])
            ]

        # Exploration
        elif self.mission_type == "explorer":
            unexplored = [
                star for star in candidates
                if star not in self.known_stars.keys()
            ]

            if unexplored:
                candidates = unexplored

            self.next_star = max(
                candidates,
                key=lambda star: (
                    10 * universe.stars[star].richness
                    + universe.distances[self.current_world, star]
                )
            )

        # Survey
        elif self.mission_type == "survey":
            unsurveyed = [star for star in candidates if star not in self.visited_stars]

            if unsurveyed:
                candidates = unsurveyed

            self.next_star = max(
                candidates,
                key=lambda star: universe.stars[star].technology
            )

        else:
            self.state = "idle"
            return

        if self.next_star is not None:
            self.state = "travelling"
    

    # ----------------------------------
    # 3. ACT
    # ----------------------------------

    def act(self, universe, dt=1.0):

        if self.completed:
            self.state = "mission_complete"        
            return

        if self.next_star is None:
            return

        start = self.current_world
        destination = self.next_star
        start_pos = universe.get_star(start).position
        destination_pos = universe.get_star(destination).position

        distance = universe.distances[start, destination]
        self.travel_progress += self.speed * dt

        # Still travelling
        if self.travel_progress < distance:
    
            progress = self.travel_progress / distance
    
            position = start_pos + (destination_pos - start_pos) * progress
    
            self.x = position[0]
            self.y = position[1]
            
        else:
            # Arrived
            self.x = destination_pos[0]
            self.y = destination_pos[1]
            self.current_world = destination
            self.observe(universe)
            self.travel_progress = 0.0
            self.next_star = None
            self.state = "idle"

    # ----------------------------------
    # 4. EVALUATE
    # ----------------------------------
    def choose_mission(self, universe):
        
        self.progress=0
        
        if self.mission_type== 'survey':
            self.required_survey += 8
        elif self.mission_type== 'explorer':
            self.required_explore += 30
            
        if self.days_from_home > self.homesickness:
            self.mission_type = 'returner'
            self.destination = self.home_world
            self.speed*=2
            
        preferences = {
            "explorer": self.exploration_drive,
            "trader": self.trade_drive,
            "survey": self.research_drive,
            "courier": self.trade_drive + self.exploration_drive- self.research_drive,
        }
    
        types = list(preferences.keys())
        weights = np.array(list(preferences.values()), dtype=float)
    
        weights /= weights.sum()
        self.mission_type = self.rng.choice(types, p=weights)
        if self.mission_type =='trader':
            candidates = universe.find_near(self.current_world,max_distance=30)
            candidates = [can for can in candidates if can not in self.visited_stars]
            self.destination = self.rng.choice(candidates,1)
        elif self.mission_type =='courier':
            candidates = universe.find_near(self.current_world,num_near=60)
            distances = universe.distances[self.current_world, candidates]
            farthest_index = np.argmax(distances)
            self.destination = candidates[farthest_index]
        elif self.mission_type== 'survey':
            self.required_survey += len(self.visited_stars)+10
        elif self.mission_type== 'explorer':
            self.required_explore += len(self.known_stars) + 30

            
        
    def evaluate(self,universe):

        self.days_from_home += 1       

        if self.mission_type == "explorer":

            self.progress = len(self.known_stars)
            if self.progress >= self.required_explore:
                self.completed = True

        elif self.mission_type == "returner":

            if self.current_world == self.home_world:
                self.completed = True
                self.days_from_home = 0
                self.speed=1
                
        elif self.mission_type == "courier":

            if self.current_world == self.target:
                self.completed = True

        elif self.mission_type == "trader":

            if self.current_world == self.target:
                self.completed = True

        elif self.mission_type == "survey":

            self.progress = len(self.visited_stars)
            if self.progress >= self.required_survey:
                self.completed = True
                
        
        if self.completed:
            self.state = "mission_complete"
            self.choose_mission(universe)    


class AgentSpawner:

    def __init__(self, universe, seed=None):
        self.universe = universe
        self.rng = np.random.default_rng(seed)


        self.mission_types = [
            "explorer",
            "survey",
        ]

    def spawn(self, number=10):

        agents = []

        for i in range(number):

            name = namer.generate()

            # Random home world
            home_world = self.rng.integers(0, len(self.universe.stars))

            # Random agent characteristics
            speed = self.rng.uniform(0.5, 2.0)
            jump_range = self.rng.uniform(5, 15)
            fallback_jumps = self.rng.integers(7, 15)

            exploration_drive = self.rng.uniform(0.5, 1.0)
            trade_drive = self.rng.uniform(0.5, 1.0)
            research_drive = self.rng.uniform(0.5, 1.0)
        

            risk_tolerance = self.rng.random()
            homesickness = self.rng.uniform(20, 150)

            mission_type = self.rng.choice(self.mission_types)

            agent = Agent(
                agent_id=f"{name}",
                home_world=int(home_world),
                speed=speed,
                jump_range=jump_range,
                fallback_jumps=int(fallback_jumps),
                exploration_drive=exploration_drive,
                trade_drive=trade_drive,
                research_drive=research_drive,
                risk_tolerance=risk_tolerance,
                homesickness=homesickness,
                mission_type=mission_type
            )

            agents.append(agent)

        return agents

