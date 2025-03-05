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
        self.previous_grid = None  # Guarda el estado anterior del ecosistema
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
        # Guardar el estado actual antes de actualizar
        self.previous_grid = [[cell.get_symbol() if cell else '.' for cell in row] for row in self.grid]
        
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
        current_symbol = self.grid[row][col].get_symbol() if self.grid[row][col] else '.'
        previous_symbol = self.previous_grid[row][col] if self.previous_grid else '.'
        
        # Resaltar cambios con colores
        if current_symbol != previous_symbol:
            print(f"\033[91m{current_symbol}\033[0m", end=' ')  # Rojo para cambios
        else:
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
    eco = Ecosystem(size=5, max_cycles=30)
    eco.run_simulation()