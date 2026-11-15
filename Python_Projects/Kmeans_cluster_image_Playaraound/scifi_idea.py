import marimo
__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():

    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from dataclasses import dataclass,field
    import namer
    import seaborn as sns
    return animation, dataclass, field, mo, np, plt, sns


@app.cell
def _(mo):
    num=mo.ui.number(step=1)
    radius=mo.ui.number(step=0.2)
    return num, radius


@app.cell
def _(radius):
    radius
    return


@app.cell
def _(num):
    num
    return


@app.cell
def _(plt):
    def plot_universe(universe, color_attr:str|None = None, size_attr:str|None = None):

        x = [star.x for star in universe.stars]
        y = [star.y for star in universe.stars]

        if color_attr is not None:
            color = [getattr(star, color_attr)for star in universe.stars]
            cmap="BuPu"
        else:
            color='Black'
            cmap=None

        if size_attr is not None:
            size_attr=[getattr(star, size_attr)for star in universe.stars]
            sa=[1 + sa * 10 for sa in size_attr]
        else:
            sa=3

        plt.scatter(
            x,
            y,
            s=sa,
            c=color,
            cmap=cmap,
            alpha=0.9
        )
        if color_attr is not None:
            plt.colorbar(label=f"{color_attr}")
        plt.show()

    return (plot_universe,)


@app.cell
def _(np):
    def construct_world(
            size: int=500,
            radius: float = 2.0,
            rng: np.random.Generator = np.random.default_rng(),
        )-> np.ndarray:
        grid=rng.uniform(0,100,(size,3))
        keep = []
        for point in grid[:,0:2]:
            if not keep:
                keep.append(point)
                continue
            distances = np.linalg.norm(np.array(keep) - point, axis=1)
            if np.all(distances >= radius):
                keep.append(point)

        grid = np.array(keep)
        grid = np.column_stack((grid, np.zeros(len(grid))))
        grid[:,2]=rng.beta(1.7,2.25,grid.shape[0])
        return grid

    def find_near(
            grid: np.ndarray,
            index:int,
            num_near:int=10,
        )-> np.ndarray:
        distances2 = np.linalg.norm(grid[:,0:2] - grid[index,0:2], axis=1)
        closest=distances2.argsort()[1:num_near+1]
        distances2.sort()
        grid = grid[closest, :]
        grid[:,2]= distances2[1:num_near+1]
        return grid,closest

    return construct_world, find_near


@app.cell
def _(construct_world, find_near, np, plt):
    grid=construct_world(900,1.5)
    rng=np.random.default_rng()
    rand=rng.integers(0,grid.shape[0])
    grid_near,indexes =find_near(grid,rand,15)
    plt.scatter(grid[:,0],grid[:,1],cmap='BuPu',c=grid[:,2],)

    plt.scatter(grid_near[:,0],grid_near[:,1],cmap='summer',c=grid_near[:,2],)
    plt.scatter(grid[rand,0],grid[rand,1],c='Red',)
    plt.title(f"world with {grid.shape[0]} stars")
    return (rng,)


@app.cell
def _(mo):
    num2=mo.ui.slider(0.1,5,0.02,1,label='A')
    num3=mo.ui.slider(0.001,2,0.05,1,label='B',)
    num2,num3

    return num2, num3


@app.cell
def _(num2, num3, plt, rng):
    ratio=round((num2.value/num3.value),2)
    s2=rng.beta(num2.value,ratio,50000)
    count2, bins2, ignored2 = plt.hist(s2, 30, density=True,range=[0,1])
    plt.title(f"beta with A={num2.value}, B={ratio}")
    plt.show()

    habitability=rng.beta(2, 2,50000)
    danger=rng.beta(1.5, 4,50000)
    s2=s2*12
    s2=s2+6
    sd=(habitability+(1-danger))/2
    s2=s2*sd
    count2, bins2, ignored2 = plt.hist(danger, 30, density=True)
    plt.title(f"beta with A={num2.value}, B={ratio}")
    plt.show()



    return


@app.cell
def _(Agent, np):
    class AgentSpawner:

        def __init__(self, universe, seed=None):
            self.universe = universe
            self.rng = np.random.default_rng(seed)

            self.names = [
                "George", "Harry", "Ryan", "Yuki", "Hana",
                "Alex", "Morgan", "Eli", "Nova", "Orion",
                "Mira", "Kai", "Ari", "Zara", "Leo",
                "Vega", "Cass", "Iris", "Atlas", "Rhea"
            ]

            self.mission_types = [
                "explorer",
                "trader",
                "survey",
                "courier",
            ]

        def spawn(self, number=10):

            agents = []

            for i in range(number):

                name = self.rng.choice(self.names)

                # Random home world
                home_world = self.rng.integers(0, len(self.universe.stars))

                # Random agent characteristics
                speed = self.rng.uniform(0.5, 2.0)
                jump_range = self.rng.uniform(5, 20)
                fallback_jumps = self.rng.integers(3, 15)

                exploration_drive = self.rng.random()
                trade_drive = self.rng.random()
                research_drive = self.rng.random()

                risk_tolerance = self.rng.random()
                homesickness = self.rng.uniform(20, 150)

                mission_type = self.rng.choice(self.mission_types)

                agent = Agent(
                    agent_id=f"{name}_{i}",
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

    return


@app.cell
def _(np):
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


    return (Agent,)


@app.cell
def _(dataclass, field, np):
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




    return (Universe,)


@app.class_definition
class Simulation:

    def __init__(self, universe, agents):

        self.universe = universe
        self.agents = agents

        self.time = 0

    def step(self, dt=1.0):

        self.time += dt

        for agent in self.agents:
            
            #0: observe the surounding
            agent.observe(self.universe)
            
            # 1. Agent makes a decision
            agent.decide(self.universe)

            # 2. Agent executes movement
            agent.act(self.universe,dt)
            
            #3. evaluate the condition of mission
            agent.evaluate(self.universe)


    def run(self, steps):

        for _ in range(steps):
            self.step()


@app.cell
def _(plt):


    def initialise_plot(simulation):

        universe = simulation.universe
        fig, ax = plt.subplots(figsize=(6, 6))
        # Plot stars ONCE
        x = [s.x for s in universe.stars]
        y = [s.y for s in universe.stars]
        ax.scatter(
            x, y,
            s=5,
            c="Blue",
            alpha=0.8
        )

        # Create agent markers ONCE
        cmap = plt.colormaps["tab10"]

        agent_plots = []

        for i, agent in enumerate(simulation.agents):
            scatter = ax.scatter(
                [agent.x],
                [agent.y],
                s=25,
                marker="^",
                color=cmap(i),
                label=f"Agent {agent.id}"
            )

            agent_plots.append(scatter)

        ax.set_xlim(0, universe.area_size)
        ax.set_ylim(0, universe.area_size)
        ax.set_aspect("equal")

        ax.legend()
        plt.show(block=False)

        return fig, ax, agent_plots

    def update_plot(simulation, fig, agent_plots):

        for agent, plot in zip(simulation.agents, agent_plots):

            plot.set_offsets([[agent.x, agent.y]])

        fig.canvas.draw_idle()
        fig.canvas.flush_events()

        plt.pause(0.02)

    return


@app.cell
def _(Universe):
    uni=Universe(size=500)
    uni.find_near(15,num_near=10)
    return (uni,)


@app.cell
def _(Agent):
    agents=[Agent('George',123),Agent('Harry',130),Agent('ry',113),Agent('y',3),Agent('Ha',1)]
    return (agents,)


@app.cell
def _(agents, uni):
    sim=Simulation(uni,agents)
    return (sim,)


@app.cell
def _(record_and_make_gif, sim):
    record_and_make_gif(sim)
    return


@app.cell
def _(animation, np, plt):
    def record_and_make_gif(
        simulation,
        steps=200,
        filename="universe.gif",
        fps=20
    ):

        universe = simulation.universe

        # ----------------------------------
        # 1. RECORD AGENT MOVEMENTS
        # ----------------------------------

        history = []

        # Record initial positions
        history.append([
            [agent.x, agent.y]
            for agent in simulation.agents
        ])

        # Run simulation and record positions
        for _ in range(steps):

            simulation.step()

            history.append([
                [agent.x, agent.y]
                for agent in simulation.agents
            ])

        history = np.array(history)

        # ----------------------------------
        # 2. INITIALISE PLOT
        # ----------------------------------

        fig, ax = plt.subplots(figsize=(7, 7))

        # Stars: plotted only once
        x = [star.x for star in universe.stars]
        y = [star.y for star in universe.stars]

        ax.scatter(
            x, y,
            s=8,
            c="blue",
            alpha=0.7
        )

        cmap = plt.colormaps["tab10"]

        # Agent markers
        agent_plots = []

        for i, agent in enumerate(simulation.agents):

            scatter = ax.scatter(
                [], [],
                s=45,
                marker="^",
                color=cmap(i),
                label=f"Agent {agent.id}",
                zorder=10
            )

            agent_plots.append(scatter)

        ax.set_xlim(0, universe.area_size)
        ax.set_ylim(0, universe.area_size)
        ax.set_aspect("equal")

        ax.legend(loc="upper right", fontsize=8)

        title = ax.set_title("Universe Simulation")

        # ----------------------------------
        # 3. ANIMATION UPDATE
        # ----------------------------------

        def update(frame):

            for i, plot in enumerate(agent_plots):

                plot.set_offsets([history[frame, i]])

            title.set_text(f"Universe | Step {frame}")

            return agent_plots + [title]

        ani = animation.FuncAnimation(
            fig,
            update,
            frames=len(history),
            interval=1000 / fps,
            blit=False
        )

        # ----------------------------------
        # 4. SAVE GIF
        # ----------------------------------

        ani.save(
            filename,
            writer=animation.PillowWriter(fps=fps)
        )

        plt.close(fig)

    return (record_and_make_gif,)


@app.cell
def _(plot_universe, uni):
    plot_universe(uni,color_attr='richness')
    return


@app.cell(disabled=True)
def _(construct_world, np, plt, sns):
    star_num=[
        300,
        # 400,500,600,700,800,900,1000,1500,
              # 2000,3000,5000
             ]
    close_num=[
        0.5,0.6,0.7,0.8,
        # 1.0,1.2,1.5,1.8,2.0,2.5,
               # 3.0,4,5,6,8,10,15,20
              ]
    results = np.zeros((len(star_num), len(close_num)))
    for i, star in enumerate(star_num):
        for j, close in enumerate(close_num):
            temp = construct_world(star, close)
            results[i,j] = len(temp)
    percentage = results / np.array(star_num)[:, None] * 100

    plt.figure(figsize=(12,7))
    sns.heatmap(percentage, annot=True, fmt=".0f", cmap="BuPu", xticklabels=close_num, yticklabels=star_num)
    plt.xlabel("Closeness radius")
    plt.ylabel("Initial number of stars")
    plt.title("Stars remaining (% of initial population)")
    plt.show()
    return


if __name__ == "__main__":
    app.run()
