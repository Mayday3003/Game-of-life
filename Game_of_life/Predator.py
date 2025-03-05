from dataclasses import dataclass


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
        return 'L'
