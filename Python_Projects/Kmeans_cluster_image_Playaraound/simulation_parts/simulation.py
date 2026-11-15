










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