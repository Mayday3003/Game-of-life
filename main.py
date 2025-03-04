from dataclasses import dataclass
from typing import List, Optional, Tuple
from abc import ABC, abstractmethod
import random
import sys

# ======================= Clases Base =======================
@dataclass
class Organism(ABC):
    x: int
    y: int
    health: int
    energy: int

    @abstractmethod
    def update_state(self, ecosystem: 'Ecosystem'):
        pass

    def is_alive(self) -> bool:
        return self.health > 0

    @abstractmethod
    def move(self, ecosystem: 'Ecosystem'):
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        pass

# ======================= Implementaciones =======================
@dataclass
class Plant(Organism):
    def update_state(self, ecosystem: 'Ecosystem'):
        pass

    def move(self, ecosystem: 'Ecosystem'):
        pass

    def get_symbol(self) -> str:
        return 'P'

@dataclass
class Prey(Organism):
    def update_state(self, ecosystem: 'Ecosystem'):
        if ecosystem.num_plants >= ecosystem.num_prey + 2:
            self.reproduces(ecosystem)

    def reproduces(self, ecosystem: 'Ecosystem'):
        positions = self.get_empty_adjacent(ecosystem)
        if positions:
            new_x, new_y = positions[0]
            ecosystem.add_organism(Prey(new_x, new_y, 100, 0))

    def move(self, ecosystem: 'Ecosystem'):
        positions = self.get_empty_adjacent(ecosystem)
        if positions:
            new_x, new_y = positions[0]
            target = ecosystem.grid[new_x][new_y]
            if isinstance(target, Plant):
                ecosystem.delete_organism(target)
                self.energy += 10
            ecosystem.move_organism(self, new_x, new_y)

    def get_empty_adjacent(self, ecosystem: 'Ecosystem') -> List[Tuple[int, int]]:
        return self.check_directions(ecosystem, [(0,1),(1,0),(0,-1),(-1,0)], 0, [])

    def check_directions(self, ecosystem, directions, index, acc):
        if index >= len(directions):
            return acc
        dx, dy = directions[index]
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < ecosystem.size and 0 <= ny < ecosystem.size:
            if ecosystem.grid[nx][ny] is None:
                acc.append((nx, ny))
        return self.check_directions(ecosystem, directions, index+1, acc)

    def get_symbol(self) -> str:
        return 'C'

@dataclass
class Predator(Organism):
    starvation_time: int = 0
    max_starvation_time: int = 0

    def update_state(self, ecosystem: 'Ecosystem'):
        self.starvation_time += 1
        if self.starvation_time >= self.max_starvation_time:
            self.health = 0
        if self.energy >= 50:
            self.reproduces(ecosystem)

    def reproduces(self, ecosystem: 'Ecosystem'):
        positions = self.get_empty_adjacent(ecosystem)
        if positions:
            new_x, new_y = positions[0]
            ecosystem.add_organism(Predator(new_x, new_y, 100, 10, 0, self.max_starvation_time))
            self.energy = 0

    def move(self, ecosystem: 'Ecosystem'):
        prey_pos = self.find_prey(ecosystem, 0, 0)
        if prey_pos:
            self.hunt_prey(ecosystem, prey_pos)
        else:
            positions = self.get_empty_adjacent(ecosystem)
            if positions:
                new_x, new_y = positions[0]
                ecosystem.move_organism(self, new_x, new_y)

    def find_prey(self, ecosystem, x, y):
        if x >= ecosystem.size:
            return None
        if y >= ecosystem.size:
            return self.find_prey(ecosystem, x+1, 0)
        org = ecosystem.grid[x][y]
        if isinstance(org, Prey):
            return (x, y)
        return self.find_prey(ecosystem, x, y+1)

    def hunt_prey(self, ecosystem, prey_pos):
        prey = ecosystem.grid[prey_pos[0]][prey_pos[1]]
        ecosystem.delete_organism(prey)
        self.energy += 10
        self.starvation_time = 0
        ecosystem.move_organism(self, prey_pos[0], prey_pos[1])

    def get_empty_adjacent(self, ecosystem):
        return self.check_directions(ecosystem, [(0,1),(1,0),(0,-1),(-1,0)], 0, [])

    def check_directions(self, ecosystem, directions, index, acc):
        if index >= len(directions):
            return acc
        dx, dy = directions[index]
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < ecosystem.size and 0 <= ny < ecosystem.size:
            if ecosystem.grid[nx][ny] is None:
                acc.append((nx, ny))
        return self.check_directions(ecosystem, directions, index+1, acc)

    def get_symbol(self) -> str:
        return 'L'

# ======================= Ecosistema =======================
class Ecosystem:
    def __init__(self, size: int, max_cycles: int):
        self.size = size
        self.max_cycles = max_cycles
        self.grid = self.create_matrix(size, size)
        self.organisms = []
        self.num_plants = 0
        self.num_prey = 0
        self.num_predators = 0
        self.cycle_count = 0
        self.plant_regeneration_interval = max_cycles // 3 if max_cycles >=3 else 1
        self.initialize_organisms()

    def create_matrix(self, rows: int, cols: int, matrix=None) -> list[list[None]]:
        """
        Creates a matrix of NxN size, using a recursive function.

        Inputs:
        - rows: # of rows of the matrix (size)
        - cols: # of columns of the matrix (size)

        Defaults:
        - matrix: default value None

        Return:
        - list of list with None values elements.
        """
        if matrix is None:
            matrix = []
        if len(matrix) == rows:
            return matrix
        
        new_row = self.create_row(cols, 0, [])
        return self.create_matrix(rows, cols, matrix + [new_row])

    def create_row(self, cols: int, current: int, row: list) -> list[None]:
        """
        Creates a row for a matrix, using a recursive function.

        Inputs:
        - cols: # of columns (elements) of the list.
        - current: the current index position of the list.
        - row: an empty list where the elements will be inserted.

        Return:
        - list with None values elements.
        """
        if current == cols:
            return row
        return self.create_row(cols, current+1, row + [None])

    def initialize_organisms(self) -> None:
        """
        Calculates the total of the Organisms will be on the Ecosystem and calculates the total of Plants, Preys and Predators existing on the grid (Ecosystem).
        """
        total = self.size ** 2
        plants = total // 3  # 33% Plants
        prey = total // 5    # 20% Preys
        predators = total // 10  # 10% Predators
        self.add_organisms(plants, Plant, self.get_empty_cells([]))
        self.add_organisms(prey, Prey, self.get_empty_cells([]))
        self.add_organisms(predators, Predator, self.get_empty_cells([]))

    def add_organisms(self, count: int, org_type: type, cells: list, index: int = 0) -> None:
        """
        Add the repective organism on the matrix, using a random list of positions. (Recursive)

        Inputs:
        - count: total of the organism to add at the matrix.
        - org_type: type of organism to add at the matrix random position.
        - cells: list of random empty cells availables to add the organims.

        Default:
        - index: default parameter to control 'cells' index.
        """
        if count <= 0 or index >= len(cells):
            return
        
        x, y = cells[index]
        if org_type == Plant:
            self.add_organism(Plant(x, y, 100, 0))
        elif org_type == Prey:
            self.add_organism(Prey(x, y, 100, 0))
        elif org_type == Predator:
            self.add_organism(Predator(x, y, 100, 0, 0, self.max_cycles // 2))

        self.add_organisms(count - 1, org_type, cells, index + 1)

    def get_empty_cells(self, acc: list, x=0, y=0) -> list[tuple[int]]:
        """
        Checks if the actual cell of the grid is empty and collects the empty cells position of the grid on a list of tuples.

        ### Inputs:
        - **acc:** an empty list to save tuple of positions (x, y)
        
        ### Default:
        - **x:** position on *x* axe of the grid (row)
        - **y:** position on *y* axe of the grid (cols)

        ### Return:
        - list of tuples of positions (x, y)
        """
        if x >= self.size:
            random.shuffle(acc)
            return acc
        if y >= self.size:
            return self.get_empty_cells(acc, x+1, 0)
        
        if self.grid[x][y] is None:
            acc.append((x, y))

        return self.get_empty_cells(acc, x, y+1)

    def add_organism(self, organism: Organism) -> None:
        """
        Add the respective organism on the (x, y) assigned at the creation of the instance, add the organism at the Ecosystem.organisms attribute and update number of each organism (Plants, Prey and Predators).

        ### Inputs:
        - **organism:** Organism instance.
        """
        self.grid[organism.x][organism.y] = organism
        self.organisms.append(organism)

        if isinstance(organism, Plant):
            self.num_plants += 1

        elif isinstance(organism, Prey):
            self.num_prey += 1

        elif isinstance(organism, Predator):
            self.num_predators += 1

    def delete_organism(self, organism: Organism) -> None:
        """
        Delete the respective organism on the (x, y) position where the Target is, remove the organism at the Ecosystem.organisms attribute and update number of each organism (Plants, Prey and Predators).

        ### Inputs:
        - **organism:** Organism instance.
        """
        self.grid[organism.x][organism.y] = None
        self.organisms.remove(organism)

        if isinstance(organism, Plant):
            self.num_plants -= 1

        elif isinstance(organism, Prey):
            self.num_prey -= 1

        elif isinstance(organism, Predator):
            self.num_predators -= 1

    def move_organism(self, organism: Organism, new_x: int, new_y: int) -> None:
        """
        Moves the organism on a new position (x, y), leaving before position with None value element on the matrix.

        ### Inputs:
        - **organism:** Organism instance.
        - **new_x:** new *x* axe position on the matrix (row)
        - **new_y:** new *y* axe position on the matrix (col)
        """
        self.grid[organism.x][organism.y] = None

        organism.x = new_x
        organism.y = new_y

        self.grid[new_x][new_y] = organism

    def update_ecosystem(self):
        """
        Updates the ecosystem, first checks if is time to regenerate plants, next update the organisms on the grid and finally adds one to cycle_count attribute.
        """
        if self.cycle_count % self.plant_regeneration_interval == 0:
            self.regenerate_plants(self.get_empty_cells([]))

        self.update_organisms(0)

        self.cycle_count += 1

    def regenerate_plants(self, cells: list) -> None:
        """
        Regenerates plants every estimaded interval of cycles, it adds a Plant on a None value cells position (x, y).

        ### Inputs:
        - **cells:** list of random empty cells availables on the grid.
        """
        if len(cells) == 0 or self.cycle_count == 0:
            return

        num = min(len(cells), (self.size**2) // 6) # num of plants to add.

        self.add_organisms(num, Plant, cells)

    def update_organisms(self, index: int) -> None:
        """
        Checks if the organism on the organims attribute list is alive, if it is the function will update the state of the organism and will move it.

        ### Inputs:
        - **index:** initial index to start loop through the list.
        """
        if index >= len(self.organisms):
            return
        org = self.organisms[index]
        
        if org.is_alive():
            org.update_state(self)
            org.move(self)

        self.update_organisms(index + 1)

    def print_grid(self, row=0) -> None:
        """
        Print the total grid calling the method print_row() to print each row, it'll stop when the row is equal to the size of the grid.

        ### Default:
        - **row:** the actual index of the row printing.
        """
        if row >= self.size:
            print(f"Plantas: {self.num_plants} | Presas: {self.num_prey} | Depredadores: {self.num_predators}")
            print(f"Ciclo: {self.cycle_count}/{self.max_cycles}")
            return

        self.print_row(row, 0)
        self.print_grid(row + 1)

    def print_row(self, row: int, col: int) -> None:
        """
        Prints each row of the grid with its elements inside (None values or Organims symbols), if it is a None value it prints '.'.

        ### Inputs:
        - **row:** the index of the actual row printing.
        - **col:** the index of the actual column printing.
        """
        if col >= self.size:
            print()
            return

        symbol = self.grid[row][col].get_symbol() if self.grid[row][col] else '.'
        print(symbol, end=' ')
        self.print_row(row, col + 1)

    def is_simulation_over(self) -> bool:
        """
        Checks if the simulation is over if all cycles are completed ot if the number of predators/preys are zero.
        
        ### Return:
        - True or False.
        """
        return (self.cycle_count >= self.max_cycles or 
                self.num_predators == 0 or 
                self.num_prey == 0)

    def run_simulation(self) -> None:
        if self.is_simulation_over():
            return
        self.print_grid()
        input("Enter para siguiente ciclo...")
        sys.stdout.write("\033[F\033[K" * (self.size + 3))
        self.update_ecosystem()
        self.run_simulation()

if __name__ == "__main__":
    eco = Ecosystem(size=15, max_cycles=15)
    eco.run_simulation()