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
            if ecosystem.grid[nx][ny] is None or isinstance(ecosystem.grid[nx][ny], Plant):
                acc.append((nx, ny))
        return self.check_directions(ecosystem, directions, index+1, acc)

    def get_symbol(self) -> str:
        return 'C'
