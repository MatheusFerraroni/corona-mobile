import json

import numpy as np


def write_json(p:dict, variable, folder):
    with open(f'{folder}/{variable}.json', 'w') as fp:
        json.dump(p, fp, indent=4)


# Pandemic A
pandemic_a = {
    	"isolamento": 0.0,
    	"chance_infeccao": 0.3,
    	"tempo_infectado": 70,
    	"distancia_infectar": 50,
    	"random_infected": 0.01,
        "nome": "undefined",
        "stationary_infection": [1800, 3600, 5400]
    }

count = 1
# Change isolation
for i in np.arange(0.1, 1.0, 0.1):
    i = "{:.1f}".format(float(i))
    p = pandemic_a.copy()
    p['isolamento'] = float(i)
    p["nome"] = "isolation_"+str(i)
    write_json(p, f'isolation_{i}', 'pandemic_a')

# Change infection chance
for j in np.arange(0.1, 1.0, 0.1):
    j = "{:.1f}".format(float(j))
    p = pandemic_a.copy()
    p['chance_infeccao'] = float(j)
    p["nome"] = "infection_"+str(j)
    write_json(p, f'infeccao_{j}', 'pandemic_a')

# Change tempo infectado time
for k in np.arange(10, 180, 10):
    p = pandemic_a.copy()
    p['tempo_infectado'] = float(k)
    p["nome"] = "infectiontime_"+str(k)
    write_json(p, f'tempo_{k}', 'pandemic_a')
