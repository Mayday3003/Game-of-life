@dataclass
class Plant(Organism):
    def update_state(self, ecosystem: 'Ecosystem'):
        pass

    def move(self, ecosystem: 'Ecosystem'):
        pass

    def get_symbol(self) -> str:
        return 'H'