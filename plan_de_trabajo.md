# Ecosystem Simulation (Recursive)

## Overview
This project implements a recursive ecosystem simulation where different organisms (predators, prey, and plants) interact within an NxN grid-based environment. The simulation follows strict recursive logic, with no loops allowed.

## Features
- **Recursive simulation cycle** evaluating organisms' states and interactions.
- **Object-oriented design** following clean code principles.
- **Health bar for organisms** affecting survival and reproduction.
- **Deterministic behavior** ensuring predictable and rule-based interactions.
- **Recursive movement and interaction rules** for each entity type.

## Class Structure

### `Ecosystem` (Main Class)
Manages the overall simulation, including the grid, organisms, and recursive updates.

#### Attributes:
- `grid`: A 2D list representing the NxN environment where each cell can contain an organism or be empty.
- `organisms`: A list of all organisms in the ecosystem.
- `cycle_count`: Tracks the number of simulation cycles.
- `max_cycles`: Defines the termination condition for the simulation.

#### Methods:
- `__init__(self, size: int, max_cycles: int)`: Initializes the ecosystem with an NxN grid and sets up organisms.
- `add_organism(self, organism)`: Adds a new organism to the grid and the organism list.
- `remove_organism(self, organism)`: Removes an organism from the grid and updates the organism list.
- `update_ecosystem(self)`: Recursively updates the state of all organisms in each cycle.
- `is_simulation_over(self) -> bool`: Checks if termination conditions are met (no organisms left or max cycles reached).
- `get_adjacent_cells(self, x: int, y: int) -> list`: Returns available adjacent positions for movement.
- `run_simulation(self)`: Starts the recursive simulation loop until termination conditions are met.

### `Organism` (Abstract Base Class)
- **Attributes:** Position `(x, y)`, health bar, and energy level.
- **Methods:**
  - `update_state()` (abstract, recursive): Defines organism behavior per cycle.
  - `is_alive()`: Returns `True` if health > 0.
  - `move_recursively()`: Defines movement logic recursively.

### `Plant` (Inherits from `Organism`)
- Regenerates in empty cells every set number of cycles (recursive implementation).
- Consumed by prey.

### `Prey` (Inherits from `Organism`)
- Moves randomly to adjacent empty cells (recursively evaluated).
- Eats plants to restore health.
- Reproduces if it has sufficient energy.
- If caught by a predator, it dies.

### `Predator` (Inherits from `Organism`)
- Hunts prey in the same row or column (recursively searches for closest prey).
- Moves randomly if no prey is visible (recursive random movement).
- Dies if it doesn't eat within a certain number of cycles.
- Reproduces when reaching a defined energy threshold.

## Recursive Behavior Implementation
- **State Evaluation:** Each organism updates its state using recursive function calls.
- **Movement:** Implemented via recursive searches for valid adjacent spaces.
- **Interactions:** Predators hunt prey recursively, prey searches for food recursively.
- **Termination:** The simulation stops when either no organisms remain or the cycle limit is reached.

## Best Practices Applied
- **Encapsulation:** Each class has a single responsibility and well-defined behaviors.
- **Polymorphism:** `Organism` serves as an abstract class, allowing `Plant`, `Prey`, and `Predator` to define their own behaviors.
- **Recursion over loops:** All iteration is handled through recursive function calls.
- **Minimal Side Effects:** Functions avoid modifying external state directly, improving maintainability.

## Next Steps
- Implement visualization for better tracking of simulation progress.
- Optimize recursive calls to prevent excessive stack depth issues.
- Introduce additional ecosystem dynamics like aging and disease.

---
This structured plan will help build a clean and maintainable recursive ecosystem simulation. 🚀

