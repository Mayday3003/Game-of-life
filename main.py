from dataclasses import dataclass
from typing import List, Optional
from abc import ABC, abstractmethod

@dataclass
class Organism(ABC):
    x: int
    y: int
    health: int
    energy: int

    @abstractmethod
    def update_state(self):
        pass

    def is_alive(self) -> bool:
        return self.health > 0

    @abstractmethod
    def move(self):
        pass

@dataclass
class Plant(Organism):
    pass

@dataclass
class Prey(Organism):
    def eat(self, plant: Plant):
        pass

    def reproduces(self, can_reproduce: bool):
        pass

@dataclass
class Predator(Organism):
    def hunt_prey(self, prey: Prey):
        pass

    def reproduces(self, can_reproduce: bool):
        pass


class Ecosystem:
    grid: List[List[Optional[Organism]]]
    organisms: List[Organism]
    cycle_count: int
    max_cycles: int
    

    def __init__(self, size: int, max_cycles: int):
        if size == 0:
            raise ValueError("The game cannot run if the matrix has no elements.")
        self.grid = self.create_matrix_recursive(size, size)
        self.organisms = []
        self.cycle_count = 0
        self.max_cycles = max_cycles

    def create_matrix_recursive(self, n: int, size: int) -> List[List[Optional[Organism]]]:
        if n == 0:
            return []
        return self.create_matrix_recursive(n - 1, size) + [[None] * size]

    def add_organism(self, organism: Organism):
        pass

    def delete_organism(self, organism: Organism):
        pass

    def update_ecosystem(self):
        pass

    def is_simulation_over(self) -> bool:
        pass

    def available_positions(self, x: int, y: int) -> List[tuple]:
        pass

    def run_simulation(self):
        pass
