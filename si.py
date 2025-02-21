import numpy as np
import plotly.graph_objects as go

N = 50
frames = []
grid = np.random.choice([0, 1], size=(N, N))

fig = go.Figure()

for _ in range(100):  # 100 iteraciones
    new_grid = grid.copy()
    for i in range(N):
        for j in range(N):
            neighbors = np.sum(grid[max(0, i-1):min(N, i+2), max(0, j-1):min(N, j+2)]) - grid[i, j]
            if grid[i, j] == 1 and (neighbors < 2 or neighbors > 3):
                new_grid[i, j] = 0
            elif grid[i, j] == 0 and neighbors == 3:
                new_grid[i, j] = 1
    grid = new_grid

    frames.append(go.Frame(data=[go.Heatmap(z=grid, colorscale="gray")]))

fig.add_trace(go.Heatmap(z=np.zeros((N, N)), colorscale="gray"))
fig.update(frames=frames)
fig.update_layout(updatemenus=[{"buttons": [{"label": "Play", "method": "animate", "args": [None]}]}])

fig.show()
