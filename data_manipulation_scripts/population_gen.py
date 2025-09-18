import csv

# Step 1: Load population data from your local ph.csv
population_map = {}
with open('ph.csv', 'r', encoding='UTF-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        city_name = row['city']
        # Use 'population_proper' for city-level population
        pop_str = row['population_proper']
        if pop_str:
            population_map[city_name] = int(float(pop_str))
        else:
            population_map[city_name] = 0

# Step 2: Read finalfinal.csv and get population for each city
population = []
with open('finalfinal.csv', 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # Skip header if exists
    for row in reader:
        city = row[0]
        pop = population_map.get(city, 0)  # Fallback to 0 if not found
        population.append(pop)

# Step 3: Write to pop.csv
with open('pop.csv', 'w', newline='', encoding='UTF-8') as f:
    writer = csv.writer(f)
    for val in population:
        writer.writerow([val])

print(f"✅ Successfully generated pop.csv with {len(population)} entries.")