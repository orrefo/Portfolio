
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time


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

mission_colors = {
    "explorer": "cyan",
    "trader": "gold",
    "survey": "lime",
    "courier": "red",
    "returner": "magenta"
}

def record_and_make_gif(
    simulation,
    steps=200,
    filename="universe.gif",
    fps=20
):

    universe = simulation.universe

    # 1. Record positions
    t0 = time.perf_counter()

    history = []
    mission_history=[]

    history.append([[a.x, a.y] for a in simulation.agents])
    mission_history.append([a.mission_type for a in simulation.agents])

    for _ in range(steps):
        simulation.step()

        history.append([[a.x, a.y] for a in simulation.agents])
        mission_history.append([a.mission_type for a in simulation.agents])

    history = np.asarray(history, dtype=np.float32)

    t1 = time.perf_counter()

    # 2. Initialise plot
    fig, ax = plt.subplots(figsize=(6, 6), dpi=80)

    x = [star.x for star in universe.stars]
    y = [star.y for star in universe.stars]

    ax.scatter(
        x, y,
        s=8,
        c="blue",
        alpha=0.7
    )

    n_agents = len(simulation.agents)

    # One scatter object for ALL agents
    cmap = plt.colormaps["tab10"]
    colors = cmap(np.arange(n_agents) % 10)

    agent_plot = ax.scatter(
        history[0, :, 0],
        history[0, :, 1],
        s=35,
        marker="^",
        c=colors,
        zorder=10
    )

    ax.set_xlim(0, universe.area_size)
    ax.set_ylim(0, universe.area_size)
    ax.set_aspect("equal")

    title = ax.set_title("Universe | Step 0")

    t2 = time.perf_counter()

    # 3. Update all agents simultaneously
    def update(frame):

        agent_plot.set_offsets(history[frame])

        current_colors = [
            mission_colors.get(agent.mission_type, "white")
            for agent in simulation.agents
        ]

        agent_plot.set_color(current_colors)

        title.set_text(f"Universe | Step {frame}")

        return agent_plot, title

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(history),
        interval=1000 / fps,
        blit=True,
        repeat=False,
        cache_frame_data=False
    )

    # 4. Save GIF
    ani.save(
        filename,
        writer=animation.PillowWriter(fps=fps),
        dpi=80
    )

    plt.close(fig)

    t3 = time.perf_counter()

    print("Simulation:", round(t1-t0, 2), "seconds")
    print("Plot setup:", round(t2-t1, 2), "seconds")
    print("GIF rendering/saving:", round(t3-t2, 2), "seconds")

    return filename




# Create figure and animation
# ... your plotting code ...




