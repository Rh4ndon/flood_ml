import csv

# Step 1: Load population data from ph.csv
population_map = {}
with open('ph.csv', 'r', encoding='UTF-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        city_name = row['city']
        # Use 'population_proper' for city-level population
        pop_str = row['population_proper']
        if pop_str:
            population_map[city_name] = float(pop_str)

# Step 2: Calculate damage using population from ph.csv
damage = []
with open('finalfinal.csv', 'r', encoding='UTF-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] == "city":  # Skip header if present
            continue

        city = row[0]                     # e.g., "Manila"
        flood_metric = float(row[3])      # e.g., 30.06
        population = population_map.get(city, 100000)  # Fallback if not found

        # Calculate damage: (flood_metric * population) / 10000
        dam = round(flood_metric * population / 10000, 2)
        damage.append(dam)

# Step 3: Write to damage.csv
with open('damage.csv', 'w', newline='', encoding='UTF-8') as f:
    writer = csv.writer(f)
    for val in damage:
        writer.writerow([val])

print(f"✅ Successfully generated damage.csv with {len(damage)} entries.")