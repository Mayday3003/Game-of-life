from dataclasses import dataclass
from typing import List, Optional, Tuple, Type
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
    def update_state(self, ecosystem: 'Ecosystem') -> None:
        pass

    def is_alive(self) -> bool:
        return self.health > 0

    @abstractmethod
    def move(self, ecosystem: 'Ecosystem') -> None:
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        pass

# ======================= Implementaciones =======================
@dataclass
class Plant(Organism):
    def update_state(self, ecosystem: 'Ecosystem') -> None:
        pass

    def move(self, ecosystem: 'Ecosystem') -> None:
        pass

    def get_symbol(self) -> str:
        return '🌱'  # Símbolo más descriptivo

@dataclass
class Prey(Organism):
    def update_state(self, ecosystem: 'Ecosystem') -> None:
        if ecosystem.num_plants >= ecosystem.num_prey + 2:
            self.reproduce(ecosystem)

    def reproduce(self, ecosystem: 'Ecosystem') -> None:
        empty_positions = self._get_empty_adjacent_positions(ecosystem)
        if empty_positions:
            new_x, new_y = empty_positions[0]
            ecosystem.add_organism(Prey(new_x, new_y, 100, 0))

    def move(self, ecosystem: 'Ecosystem') -> None:
        empty_positions = self._get_empty_adjacent_positions(ecosystem)
        if empty_positions:
            new_x, new_y = empty_positions[0]
            target = ecosystem.grid[new_x][new_y]
            if isinstance(target, Plant):
                ecosystem.delete_organism(target)
                self.energy += 10
            ecosystem.move_organism(self, new_x, new_y)

    def _get_empty_adjacent_positions(self, ecosystem: 'Ecosystem') -> List[Tuple[int, int]]:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return self._check_directions_recursively(ecosystem, directions, 0, [])

    def _check_directions_recursively(self, ecosystem: 'Ecosystem', 
                                    directions: List[Tuple[int, int]], 
                                    current_index: int, 
                                    valid_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if current_index >= len(directions):
            return valid_positions
        dx, dy = directions[current_index]
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < ecosystem.size and 0 <= ny < ecosystem.size:
            if ecosystem.grid[nx][ny] is None or isinstance(ecosystem.grid[nx][ny], Plant):
                valid_positions.append((nx, ny))
        return self._check_directions_recursively(ecosystem, directions, current_index + 1, valid_positions)

    def get_symbol(self) -> str:
        return '🐇'  # Símbolo más descriptivo

@dataclass
class Predator(Organism):
    starvation_time: int = 0
    max_starvation_time: int = 0
    hunting_success_rate: float = 0.6  # 60% de éxito en caza

    def update_state(self, ecosystem: 'Ecosystem') -> None:
        self.starvation_time += 1
        if self.starvation_time >= self.max_starvation_time:
            self.health = 0
        if self.energy >= 75:  # Mayor requerimiento de energía para reproducirse
            self.reproduce(ecosystem)

    def reproduce(self, ecosystem: 'Ecosystem') -> None:
        empty_positions = self._get_empty_adjacent_positions(ecosystem)
        if empty_positions:
            new_x, new_y = empty_positions[0]
            ecosystem.add_organism(Predator(
                new_x, new_y, 
                health=100, 
                energy=25,  # Energía residual después de reproducción
                starvation_time=0,
                max_starvation_time=self.max_starvation_time
            ))
            self.energy = 25  # No se queda sin energía

    def move(self, ecosystem: 'Ecosystem') -> None:
        visible_prey = self._get_visible_prey_positions(ecosystem)
        if visible_prey:
            closest_prey = self._find_closest_prey(visible_prey)
            self._move_towards_prey(ecosystem, closest_prey)
        else:
            self._move_randomly(ecosystem)

    def _get_visible_prey_positions(self, ecosystem: 'Ecosystem') -> List[Tuple[int, int]]:
        visible_prey = []
        
        def scan_row(y: int) -> None:
            if y >= ecosystem.size:
                return
            org = ecosystem.grid[self.x][y]
            if isinstance(org, Prey):
                visible_prey.append((self.x, y))
            scan_row(y + 1)
        
        def scan_column(x: int) -> None:
            if x >= ecosystem.size:
                return
            org = ecosystem.grid[x][self.y]
            if isinstance(org, Prey):
                visible_prey.append((x, self.y))
            scan_column(x + 1)
        
        scan_row(0)
        scan_column(0)
        return visible_prey

    def _find_closest_prey(self, prey_positions: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        def helper(positions: List[Tuple[int, int]], 
                 index: int, 
                 closest: Optional[Tuple[int, int]], 
                 min_distance: int) -> Optional[Tuple[int, int]]:
            if index >= len(positions):
                return closest
            current_distance = abs(positions[index][0] - self.x) + abs(positions[index][1] - self.y)
            if current_distance < min_distance:
                return helper(positions, index + 1, positions[index], current_distance)
            return helper(positions, index + 1, closest, min_distance)
        
        return helper(prey_positions, 0, None, float('inf'))

    def _move_towards_prey(self, ecosystem: 'Ecosystem', target_position: Tuple[int, int]) -> None:
        if target_position is None:
            return
        
        dx = 1 if target_position[0] > self.x else -1 if target_position[0] < self.x else 0
        dy = 1 if target_position[1] > self.y else -1 if target_position[1] < self.y else 0
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 0 <= new_x < ecosystem.size and 0 <= new_y < ecosystem.size:
            target = ecosystem.grid[new_x][new_y]
            if isinstance(target, Prey) and random.random() < self.hunting_success_rate:
                self._hunt_prey(ecosystem, target)
            elif target is None:
                ecosystem.move_organism(self, new_x, new_y)

    def _hunt_prey(self, ecosystem: 'Ecosystem', prey: Prey) -> None:
        ecosystem.delete_organism(prey)
        self.energy += 15  # Mayor energía por caza exitosa
        self.starvation_time = 0
        ecosystem.move_organism(self, prey.x, prey.y)

    def _move_randomly(self, ecosystem: 'Ecosystem') -> None:
        empty_positions = self._get_empty_adjacent_positions(ecosystem)
        if empty_positions:
            new_x, new_y = empty_positions[0]
            ecosystem.move_organism(self, new_x, new_y)

    def _get_empty_adjacent_positions(self, ecosystem: 'Ecosystem') -> List[Tuple[int, int]]:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return self._check_directions_recursively(ecosystem, directions, 0, [])

    def _check_directions_recursively(self, ecosystem: 'Ecosystem', 
                                    directions: List[Tuple[int, int]], 
                                    current_index: int, 
                                    valid_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if current_index >= len(directions):
            return valid_positions
        dx, dy = directions[current_index]
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < ecosystem.size and 0 <= ny < ecosystem.size:
            if ecosystem.grid[nx][ny] is None:
                valid_positions.append((nx, ny))
        return self._check_directions_recursively(ecosystem, directions, current_index + 1, valid_positions)

    def get_symbol(self) -> str:
        return '🐺'  # Símbolo más descriptivo

# ======================= Ecosistema =======================
class Ecosystem:
    def __init__(self, size: int, max_cycles: int):
        self.size = size
        self.max_cycles = max_cycles
        self.grid = self._create_empty_grid()
        self.organisms: List[Organism] = []
        self.num_plants = 0
        self.num_prey = 0
        self.num_predators = 0
        self.cycle_count = 0
        self.plant_regeneration_interval = max_cycles // 3 if max_cycles >= 3 else 1
        self.previous_grid: Optional[List[List[str]]] = None
        self._initialize_organisms()

    def _create_empty_grid(self) -> List[List[Optional[Organism]]]:
        def create_row(remaining: int, row: List[Optional[Organism]] = None) -> List[Optional[Organism]]:
            if row is None:
                row = []
            if remaining == 0:
                return row
            return create_row(remaining - 1, row + [None])
        
        def create_grid(remaining: int, grid: List[List[Optional[Organism]]] = None) -> List[List[Optional[Organism]]]:
            if grid is None:
                grid = []
            if remaining == 0:
                return grid
            return create_grid(remaining - 1, grid + [create_row(self.size)])
        
        return create_grid(self.size)

    def _initialize_organisms(self) -> None:
        total_cells = self.size ** 2
        initial_plants = int(total_cells * 0.4)  # 40% plantas
        initial_prey = int(total_cells * 0.3)    # 30% presas
        initial_predators = int(total_cells * 0.05)  # 5% depredadores
        
        empty_cells = self._get_empty_cells()
        self._add_organisms(initial_plants, Plant, empty_cells)
        self._add_organisms(initial_prey, Prey, empty_cells[initial_plants:])
        self._add_organisms(initial_predators, Predator, empty_cells[initial_plants + initial_prey:])

    def _get_empty_cells(self) -> List[Tuple[int, int]]:
        def collect_cells(x: int = 0, y: int = 0, acc: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
            if acc is None:
                acc = []
            if x >= self.size:
                random.shuffle(acc)
                return acc
            if y >= self.size:
                return collect_cells(x + 1, 0, acc)
            if self.grid[x][y] is None:
                acc.append((x, y))
            return collect_cells(x, y + 1, acc)
        return collect_cells()

    def _add_organisms(self, count: int, organism_type: Type[Organism], cells: List[Tuple[int, int]]) -> None:
        def add_recursive(remaining: int, index: int) -> None:
            if remaining <= 0 or index >= len(cells):
                return
            x, y = cells[index]
            self.add_organism(organism_type(x, y, 100, 0))
            add_recursive(remaining - 1, index + 1)
        add_recursive(count, 0)

    def add_organism(self, organism: Organism) -> None:
        self.grid[organism.x][organism.y] = organism
        self.organisms.append(organism)
        if isinstance(organism, Plant):
            self.num_plants += 1
        elif isinstance(organism, Prey):
            self.num_prey += 1
        elif isinstance(organism, Predator):
            self.num_predators += 1

    def delete_organism(self, organism: Organism) -> None:
        self.grid[organism.x][organism.y] = None
        self.organisms.remove(organism)
        if isinstance(organism, Plant):
            self.num_plants -= 1
        elif isinstance(organism, Prey):
            self.num_prey -= 1
        elif isinstance(organism, Predator):
            self.num_predators -= 1

    def move_organism(self, organism: Organism, new_x: int, new_y: int) -> None:
        self.grid[organism.x][organism.y] = None
        organism.x = new_x
        organism.y = new_y
        self.grid[new_x][new_y] = organism

    def update_ecosystem(self) -> None:
        self.previous_grid = [[cell.get_symbol() if cell else '.' for cell in row] for row in self.grid]
        
        if self.cycle_count % self.plant_regeneration_interval == 0:
            self._regenerate_plants()
        
        self._update_organisms()
        self.cycle_count += 1

    def _regenerate_plants(self) -> None:
        empty_cells = self._get_empty_cells()
        plants_to_add = min(len(empty_cells), (self.size ** 2) // 4)  # Más plantas
        self._add_organisms(plants_to_add, Plant, empty_cells)

    def _update_organisms(self) -> None:
        def update_recursive(index: int) -> None:
            if index >= len(self.organisms):
                return
            organism = self.organisms[index]
            if organism.is_alive():
                organism.update_state(self)
                organism.move(self)
            update_recursive(index + 1)
        update_recursive(0)

    def print_grid(self) -> None:
        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                current_symbol = cell.get_symbol() if cell else '.'
                previous_symbol = self.previous_grid[row_index][col_index] if self.previous_grid else '.'
                color_code = "\033[91m" if current_symbol != previous_symbol else ""
                print(f"{color_code}{current_symbol}\033[0m", end=' ')
            print()
        print(f"Plantas: {self.num_plants} | Presas: {self.num_prey} | Depredadores: {self.num_predators}")
        print(f"Ciclo: {self.cycle_count}/{self.max_cycles}")

    def is_simulation_over(self) -> bool:
        return (self.cycle_count >= self.max_cycles or
                self.num_predators == 0 or
                self.num_prey == 0)

    def run_simulation(self) -> None:
        while not self.is_simulation_over():
            self.print_grid()
            input("Presiona Enter para siguiente ciclo...")
            sys.stdout.write("\033[F\033[K" * (self.size + 3))
            self.update_ecosystem()

if __name__ == "__main__":
    eco = Ecosystem(size=5, max_cycles=30)
    eco.run_simulation()