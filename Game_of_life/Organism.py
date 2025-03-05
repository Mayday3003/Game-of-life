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