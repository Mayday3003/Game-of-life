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
        return '🌱'

@dataclass
class Prey(Organism):
    def update_state(self, ecosystem: 'Ecosystem'):
        if ecosystem.num_plants >= ecosystem.num_prey + 2:
            self.reproduces(ecosystem)

    def reproduces(self, ecosystem: 'Ecosystem'):
        positions = self.get_empty_adjacent(ecosystem)
        is_prey = self.is_prey_adjacent(ecosystem)

        if is_prey:
            if positions:
                new_x, new_y = positions[0]
                ecosystem.add_organism(Prey(new_x, new_y, 100, 0))

    def move(self, ecosystem: 'Ecosystem'):
        positions = self.get_move_adjacent(ecosystem)
        if positions:
            new_x, new_y = positions[0]
            target = ecosystem.grid[new_x][new_y]

            if isinstance(target, Plant):
                ecosystem.delete_organism(target)
                self.energy += 10
            ecosystem.move_organism(self, new_x, new_y)

    def get_move_adjacent(self, ecosystem: 'Ecosystem') -> List[Tuple[int, int]]:
        return self.check_move_directions(ecosystem, [(0,1),(1,0),(0,-1),(-1,0)], 0, [])
    
    def get_empty_adjacent(self, ecosystem: 'Ecosystem') -> List[Tuple[int, int]]:
        return self.check_empty_directions(ecosystem, [(0,1),(1,0),(0,-1),(-1,0)], 0, [])
    
    def is_prey_adjacent(self, ecosystem: 'Ecosystem') -> List[Tuple[int, int]]:
        if not self.check_reproduce_prey(ecosystem, [(0,1),(1,0),(0,-1),(-1,0)], 0, []):
            return False
        
        return True

    def check_move_directions(self, ecosystem, directions, index, acc):
        if index >= len(directions):
            return acc
        
        dx, dy = directions[index]
        nx, ny = self.x + dx, self.y + dy

        if 0 <= nx < ecosystem.size and 0 <= ny < ecosystem.size:
            if ecosystem.grid[nx][ny] is None or isinstance(ecosystem.grid[nx][ny], Plant):
                acc.append((nx, ny))

        return self.check_move_directions(ecosystem, directions, index+1, acc)
    
    def check_empty_directions(self, ecosystem, directions, index, acc):
        if index >= len(directions):
            return acc
        
        dx, dy = directions[index]
        nx, ny = self.x + dx, self.y + dy

        if 0 <= nx < ecosystem.size and 0 <= ny < ecosystem.size:
            if ecosystem.grid[nx][ny] is None:
                acc.append((nx, ny))

        return self.check_empty_directions(ecosystem, directions, index + 1, acc)
    
    def check_reproduce_prey(self, ecosystem, directions, index, preys):
        if index >= len(directions):
            return preys
        
        dx, dy = directions[index]
        nx, ny = self.x + dx, self.y + dy

        if 0 <= nx < ecosystem.size and 0 <= ny < ecosystem.size:
            if isinstance(ecosystem.grid[nx][ny], Prey):
                preys.append((nx, ny))

        return self.check_reproduce_prey(ecosystem, directions, index + 1, preys)

    def get_symbol(self) -> str:
        return '🐔'

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

    def find_visible_prey(self, ecosystem: 'Ecosystem') -> List[Tuple[int, int]]:
        prey = []
        
        def check_row(y: int):
            if y >= ecosystem.size:
                return
            org = ecosystem.grid[self.x][y]
            if isinstance(org, Prey):
                prey.append((self.x, y))
            check_row(y + 1)
        
        def check_col(x: int):
            if x >= ecosystem.size:
                return
            org = ecosystem.grid[x][self.y]
            if isinstance(org, Prey):
                prey.append((x, self.y))
            check_col(x + 1)
        
        check_row(0)
        check_col(0)
        return prey

    def get_closest_prey(self, prey_list: List[Tuple[int, int]]):
        def helper(lst, idx, closest, min_dist):
            if idx >= len(lst):
                return closest
            x, y = lst[idx]
            dist = abs(x - self.x) + abs(y - self.y)
            if dist < min_dist:
                return helper(lst, idx+1, (x,y), dist)
            return helper(lst, idx+1, closest, min_dist)
        return helper(prey_list, 0, None, float('inf'))

    def get_direction(self, target: Tuple[int, int]) -> Tuple[int, int]:
        if target[0] != self.x:  # Mover en eje X
            return (1 if target[0] > self.x else -1, 0)
        else:  # Mover en eje Y
            return (0, 1 if target[1] > self.y else -1)

    def move(self, ecosystem: 'Ecosystem'):
        visible_prey = self.find_visible_prey(ecosystem)
        if visible_prey:
            closest_pos = self.get_closest_prey(visible_prey)
            if closest_pos:
                direction = self.get_direction(closest_pos)
                new_x = self.x + direction[0]
                new_y = self.y + direction[1]
                
                if 0 <= new_x < ecosystem.size and 0 <= new_y < ecosystem.size:
                    target = ecosystem.grid[new_x][new_y]
                    if isinstance(target, Prey):
                        self.hunt_prey(ecosystem, target)
                    elif target is None:
                        ecosystem.move_organism(self, new_x, new_y)
        else:
            positions = self.get_empty_adjacent(ecosystem)
            if positions:
                new_x, new_y = positions[0]
                ecosystem.move_organism(self, new_x, new_y)

    def hunt_prey(self, ecosystem: 'Ecosystem', prey: Prey):
        ecosystem.delete_organism(prey)
        self.energy += 10
        self.starvation_time = 0
        ecosystem.move_organism(self, prey.x, prey.y)

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
        return '🦊'

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

    def create_matrix(self, rows: int, cols: int, matrix=None):
        if matrix is None:
            matrix = []
        if len(matrix) == rows:
            return matrix
        new_row = self.create_row(cols, 0, [])
        return self.create_matrix(rows, cols, matrix + [new_row])

    def create_row(self, cols: int, current: int, row: list):
        if current == cols:
            return row
        return self.create_row(cols, current+1, row + [None])

    def initialize_organisms(self):
        total = self.size ** 2
        plants = total // 3  # 33% plantas
        prey = total // 5    # 20% presas
        predators = total // 10  # 10% depredadores
        self.add_organisms(plants, Plant, self.get_empty_cells([]))
        self.add_organisms(prey, Prey, self.get_empty_cells([]))
        self.add_organisms(predators, Predator, self.get_empty_cells([]))

    def add_organisms(self, count: int, org_type: type, cells: list, index: int = 0):
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

    def get_empty_cells(self, acc: list, x=0, y=0):
        if x >= self.size:
            random.shuffle(acc)
            return acc
        if y >= self.size:
            return self.get_empty_cells(acc, x+1, 0)
        if self.grid[x][y] is None:
            acc.append((x, y))
        return self.get_empty_cells(acc, x, y+1)

    def add_organism(self, organism: Organism):
        self.grid[organism.x][organism.y] = organism
        self.organisms.append(organism)
        if isinstance(organism, Plant):
            self.num_plants += 1
        elif isinstance(organism, Prey):
            self.num_prey += 1
        elif isinstance(organism, Predator):
            self.num_predators += 1

    def delete_organism(self, organism: Organism):
        self.grid[organism.x][organism.y] = None
        self.organisms.remove(organism)
        if isinstance(organism, Plant):
            self.num_plants -= 1
        elif isinstance(organism, Prey):
            self.num_prey -= 1
        elif isinstance(organism, Predator):
            self.num_predators -= 1

    def move_organism(self, organism: Organism, new_x: int, new_y: int):
        self.grid[organism.x][organism.y] = None
        organism.x = new_x
        organism.y = new_y
        self.grid[new_x][new_y] = organism

    def update_ecosystem(self):
        if self.cycle_count % self.plant_regeneration_interval == 0:
            self.regenerate_plants(self.get_empty_cells([]))
        self.update_organisms(0)
        self.cycle_count += 1

    def regenerate_plants(self, cells: list):
        if len(cells) == 0 or self.cycle_count == 0:
            return
        num = min(len(cells), (self.size**2) // 6)
        self.add_organisms(num, Plant, cells)

    def update_organisms(self, index: int):
        if index >= len(self.organisms):
            return
        org = self.organisms[index]
        if org.is_alive():
            org.update_state(self)
            org.move(self)
        self.update_organisms(index + 1)

    def print_grid(self, row=0):
        if row >= self.size:
            print(f"Plantas: {self.num_plants} | Presas: {self.num_prey} | Depredadores: {self.num_predators}")
            print(f"Ciclo: {self.cycle_count}/{self.max_cycles}")
            return
        self.print_row(row, 0)
        self.print_grid(row + 1)

    def print_row(self, row: int, col: int):
        if col >= self.size:
            print()
            return
        current_symbol = self.grid[row][col].get_symbol() if self.grid[row][col] else '🤍'
        
        print(current_symbol, end=' ')
        self.print_row(row, col + 1)

    def is_simulation_over(self):
        return (self.cycle_count >= self.max_cycles or 
                self.num_predators == 0 or 
                self.num_prey == 0)

    def run_simulation(self):
        if self.is_simulation_over():
            return
        self.print_grid()
        input("Enter para siguiente ciclo...")
        sys.stdout.write("\033[F\033[K" * (self.size + 3))
        self.update_ecosystem()
        self.run_simulation()

if __name__ == "__main__":
    eco = Ecosystem(size=15, max_cycles=30)
    eco.run_simulation()