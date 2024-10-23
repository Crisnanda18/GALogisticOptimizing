import random
import matplotlib.pyplot as plt

class Product:
    def __init__(self, id, name, weight, destination, dimension):
        self.id = id
        self.name = name
        self.weight = weight
        self.destination = destination
        self.dimension = dimension

class Truck:
    def __init__(self, id, plate_number, fuel_ratio, max_load, dimension):
        self.id = id
        self.plate_number = plate_number
        self.fuel_ratio = fuel_ratio
        self.max_load = max_load
        self.dimension = dimension
        self.route = [] 
        self.load = 0

def calculate_shipping_cost(product, route, distances):
    total_distance = 0
    current_location = "Depot"  # semua truck dimulai dari depot
    
    for destination in route: 
        if current_location in distances and destination in distances[current_location]:
            total_distance += distances[current_location][destination] #berarti ngitung shipping costnya berdasarkan rute (lebih cuan)
        else:
            print(f"Error: jarak dari {current_location} ke {destination} tidak ada") #gak ada di dictionary
            return 0  
        current_location = destination
    
    return product.weight * total_distance * product.dimension

def calculate_fuel_cost(truck, route, distances):
    total_distance = 0
    current_location = "Depot"  # semua truck dimulai dari depot
    
    for destination in route:
        if current_location in distances and destination in distances[current_location]:
            total_distance += distances[current_location][destination]
        else:
            print(f"Error: jarak dari {current_location} ke {destination} tidak ada")
            return 0 
        current_location = destination
        
    return truck.fuel_ratio * total_distance

def fitness(chromosome, products, trucks, distances): #1, 2, 3, 2, 1, 4, 4, 1, 3, 2
    unique_truck_ids = set(truck_id for truck_id in chromosome if truck_id is not None)
    total_profit = 0
    for truck in trucks:
        truck.route = []
        truck.load = 0
        
    for truck_id in unique_truck_ids: #1, 2, 3, 4
        truck = trucks[truck_id - 1]  # truk berdasarkan truck_id
        for i, current_truck_id in enumerate(chromosome):
            if current_truck_id == truck_id: #kalau cur truk id = 1 brti cek semua kromosom yg val e 1
                product = products[i]  # ambil produk dri i skrg
                if product.dimension <= truck.dimension:  # periksa apakah produk bisa diangkut oleh truk
                    truck.route.append(product.destination)  # brti isinya rute dari satu truk
                    truck.load += product.weight  # total berat produk ke muatan truk
                    shipping_cost = calculate_shipping_cost(product, truck.route, distances)  #total biaya pengiriman barang dari semua rute di slh satu truk
                    fuel_cost = calculate_fuel_cost(truck, truck.route, distances)  #total biaya bensin dari semua rute di slh satu truk
                    total_profit += shipping_cost - fuel_cost 
        # print(f"Truck {truck.id}: {truck.route} shipping cost: {shipping_cost} fuel cost: {fuel_cost}") 
                
    for truck in trucks:
        if truck.load > truck.max_load:
            return 100 #kenapa kok gak 0? menghindari NoneType error

    return total_profit


#
def uniform_crossover(parent1, parent2):
    length = len(parent1)
    child1 = [-1] * length  # -1 artinya empty
    child2 = [-1] * length
    
    for i in range(length):
        if random.random() < 0.5:  # 50% probabilitas milih dari parent1
            # print("else",i)
            child1[i] = parent1[i]
            child2[i] = parent2[i]
        else:  # 50% probabilitas milih dari parent2
            # print("else",i)
            child1[i] = parent2[i]
            child2[i] = parent1[i]
    
    return child1, child2

    

def roulette_wheel_selection(population, fitnesses):
    total_fitness = sum(fitnesses)
    pick = random.uniform(0, total_fitness)
    current = 0
    for i, fitness in enumerate(fitnesses):
        current += fitness
        if current > pick:
            return population[i]

#inversion mutation jadi misal start:1 dan end:4 maka nanti index 1-4 akan dibalik(reversed)
def mutate(chromosome, mutation_rate):
    if random.random() < mutation_rate:
        # dua titik acak
        start = random.randint(0, len(chromosome) - 2)
        end = random.randint(start + 1, len(chromosome) - 1)
        
        chromosome[start:end+1] = reversed(chromosome[start:end+1])



def genetic_algorithm(products, trucks, distances, population_size, generations, crossover_rate, mutation_rate):
    population = []
    best_fitness_over_time = []
    average_fitness_over_time = []
    
    population.append([4, 1, 4, 1, 2, 1, 2, 3, 4, 1])
    population.append([1, 2, 3, 4, 1, 2, 3, 4, 4, 4])
    population.append([4, 3, 4, 1, 2, 3, 4, 1, 2, 3])
    population.append([3, 2, 1, 2, 3, 4, 1, 2, 3, 4])

    best_fitness = None

    for generation in range(generations):
        try:
            fitnesses = [fitness(chromosome, products, trucks, distances) for chromosome in population] #cek fitness semua kromosom dalam populasi
            best_fitness = max(fitnesses)
            average_fitness = sum(fitnesses) / len(fitnesses)
            best_fitness_over_time.append(best_fitness)
            average_fitness_over_time.append(average_fitness)
            print(f"Generation {generation+1}: Best fitness = {best_fitness}, Average fitness = {average_fitness}")
            print(f"Population: {population}")
            
            new_population = []
            for _ in range(population_size // 2): #kenapa bagi 2? karena setiap iterasi crossover menghasilkan 2 child
                parent1 = roulette_wheel_selection(population, fitnesses)
                parent2 = roulette_wheel_selection(population, fitnesses)
                
                if random.random() < crossover_rate: #(0 - 1)
                    child1,child2 = uniform_crossover(parent1, parent2)
                
                # if generation < generations - 1: #jangan mutate di generasi terakhir
                #     mutate(child1, mutation_rate)
                #     mutate(child2, mutation_rate)
                    
                mutate(child1, mutation_rate)
                mutate(child2, mutation_rate)
                
                new_population.extend([child1, child2])
                
            population = new_population
            
        except Exception as e:
            continue

    if best_fitness is None:
        print("no valid fitness found.")
        return None
    
    plt.plot(range(generations), best_fitness_over_time, label='Best Fitness')
    plt.plot(range(generations), average_fitness_over_time, label='Average Fitness')
    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.title(f'Grafik Fitness selama {generations} Generasi')
    plt.legend()
    plt.show()
    
    return best_fitness

products = [
    Product(1, "Product1", 10, "CityA", 1), #1 small 2 medium 3 large
    Product(2, "Product2", 20, "CityB", 2),
    Product(3, "Product3", 11, "CityC", 3),
    Product(4, "Product4", 20, "CityD", 1),
    Product(5, "Product5", 35, "CityE", 2),
    Product(6, "Product6", 75, "CityA", 3),
    Product(7, "Product7", 50, "CityB", 1),
    Product(8, "Product8", 40, "CityC", 2),
    Product(9, "Product9", 90, "CityD", 3),
    Product(10, "Product10",55, "CityE", 1)
]

trucks = [
    Truck(1, "L 1234 ABK", 0.5, 200, 3), #mengkonsumsi 0.5 unit bensin per 1 unit jarak
    Truck(2, "L 1812 XYZ", 0.5, 200, 3),
    Truck(3, "L 9101 CL", 0.5, 200, 3),
    Truck(4, "L 1121 CCB", 0.5, 200, 3)
]

# dictionary buat data jarak anatar destinasi (semua truk dimulai dari depot)
distances = {
    "Depot": {"CityA": 100, "CityB": 200, "CityC": 306, "CityD": 400, "CityE": 502}, #misal 502 artinya 502 unit jarak
    "CityA": {"CityB": 150, "CityC": 200, "CityD": 250, "CityE": 300, "CityA": 0}, #kalau sama-sama destinasi e, asumsi jarak 0 aja
    "CityB": {"CityA": 150, "CityC": 100, "CityD": 150, "CityE": 200, "CityB": 0},
    "CityC": {"CityA": 200, "CityB": 100, "CityD": 100, "CityE": 150, "CityC": 0},
    "CityD": {"CityA": 250, "CityB": 150, "CityC": 100, "CityE": 100, "CityD": 0},
    "CityE": {"CityA": 300, "CityB": 200, "CityC": 150, "CityD": 100, "CityE": 0}
}

genetic_algorithm(products, trucks, distances, population_size=10, generations=10, crossover_rate=0.7, mutation_rate=0.2)
