from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import Flask, render_template, request, jsonify
import random
import numpy as np
import pandas as pd
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
csrf = CSRFProtect(app)

airport_data = pd.read_csv('airportDataset.csv')
cities = airport_data['City'].unique().tolist()

class RoutingForm(FlaskForm):
    starting_location = SelectField('Starting Location', choices=[(city, city) for city in cities])
    aircraft_type = SelectField('Aircraft Type', choices=[('Aircraft 1', 'Aircraft 1'), ('Aircraft 2', 'Aircraft 2'), ('Aircraft 3', 'Aircraft 3'), ('Aircraft 4', 'Aircraft 4'), ('Aircraft 5', 'Aircraft 5')])
    submit = SubmitField('Submit')

@app.route('/')
def home():
    form = RoutingForm()  
    return render_template('index.html', form=form)  

@app.route('/optimize_route', methods=['POST'])
def optimize_route():
    global result
    if request.method == 'POST':
        weather_data = pd.read_csv('weatherdataset.csv')
        airport_data = pd.read_csv('airportDataset.csv')

        starting_location = request.form.get('starting_location')
        aircraft_type = request.form.get('aircraft_type')
        
        airport_data = pd.read_csv('airportDataset.csv')

        population_size = 100
        num_generations = 100
        mutation_rate = 0.01

        cities = airport_data['City'].tolist()
        def generate_random_route(cities):
            route = cities.copy()
            random.shuffle(route)
            return route

        population = [generate_random_route(cities) for _ in range(population_size)]

        def calculate_fitness(route):
            total_distance = 0 
            for i in range(len(route) - 1):
                distance = random.uniform(100, 1000)  # Replace with actual distance calculation
                total_distance += distance
            return 1 / total_distance

        best_route = None
        best_fitness = float('-inf')

        for generation in range(num_generations):
            fitness_scores = [calculate_fitness(route) for route in population]

            generation_best_index = fitness_scores.index(max(fitness_scores))
            generation_best_route = population[generation_best_index]
            generation_best_fitness = fitness_scores[generation_best_index]

            if generation_best_fitness > best_fitness:
                best_route = generation_best_route
                best_fitness = generation_best_fitness

            selected_indices = np.random.choice(range(population_size), size=population_size, p=np.array(fitness_scores) / sum(fitness_scores))
            selected_population = [population[i] for i in selected_indices]

            crossover_population = []
            for i in range(population_size // 2):
                parent1, parent2 = random.choices(selected_population, k=2)
                crossover_point = random.randint(1, len(cities) - 1)
                child1 = parent1[:crossover_point] + [city for city in parent2 if city not in parent1[:crossover_point]]
                child2 = parent2[:crossover_point] + [city for city in parent1 if city not in parent2[:crossover_point]]
                crossover_population.append(child1)
                crossover_population.append(child2)

            mutated_population = []

            for route in crossover_population:
                if random.random() < mutation_rate:
                    mutation_point1, mutation_point2 = random.sample(range(len(cities)), 2)

                    while mutation_point1 == mutation_point2:
                        mutation_point2 = (mutation_point2 + 1) % len(cities)

                    route_copy = route[:]  
                    route_copy[:mutation_point1], route_copy[:mutation_point2] = route_copy[:mutation_point2], route_copy[:mutation_point1]
                    mutated_population.append(route_copy)
                else:
                    mutated_population.append(route)

            population = mutated_population

        total_distance = 0  
        total_fuel_consumption = 0  

        for i in range(len(route) - 1):
            distance = random.uniform(100, 1000)  
            total_distance += distance

            fuel_consumption = random.uniform(10, 100) 
            total_fuel_consumption += fuel_consumption

            print("Total distance:", total_distance)
            print("Total fuel consumption:", total_fuel_consumption)
        
        fitness = 0.6 / total_fuel_consumption + 0.4 / total_distance
        print("Final Fitness:", fitness)

        weather_data = {
            'City': cities,
            'Wind Speed': [random.uniform(5, 20) for _ in cities],
            'Wind Direction': [random.uniform(0, 360) for _ in cities]
        }

        weather_df = pd.DataFrame(weather_data)

        def simulate_weather_changes(weather_df, num_time_steps):
            time_steps = []
            wind_speeds = []
            wind_directions = []

            for _ in range(num_time_steps):
                weather_df['Wind Speed'] = [max(5, ws + random.uniform(-1, 1)) for ws in weather_df['Wind Speed']]
                weather_df['Wind Direction'] = [wd + random.uniform(-10, 10) for wd in weather_df['Wind Direction']]

                time_steps.append(_)  
                wind_speeds.append(weather_df['Wind Speed'].tolist())  
                wind_directions.append(weather_df['Wind Direction'].tolist()) 

            return time_steps, wind_speeds, wind_directions

        num_time_steps = 10  
        time_steps, wind_speeds, wind_directions = simulate_weather_changes(weather_df, num_time_steps)


        result = {
            'starting_location': starting_location,
            'aircraft_type': aircraft_type,
            'optimized_route': best_route,
            'total_distance': total_distance,
            'total_fuel_consumption': total_fuel_consumption,
            'fitness': best_fitness,
            'time_steps': time_steps,
            # 'wind_speeds': wind_speeds,
            # 'wind_directions': wind_directions
        }
        
        return render_template('results.html', result=result)


@app.route('/route_optimizer', methods=['GET', 'POST'])
def route_optimizer():
    form = RoutingForm()
    if form.validate_on_submit():
        starting_location = form.starting_location.data
        aircraft_type = form.aircraft_type.data

        return jsonify({'starting_location': starting_location, 'aircraft_type': aircraft_type, 'result': 'Optimized Route'})

    return render_template('routing_form.html', form=form)

@app.route('/best_route_map')
def show_best_route():
    global result  
    return render_template('best_route_map.html', result=result)

@app.route('/show_results')
def show_results():
    global result  
    return render_template('results.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
