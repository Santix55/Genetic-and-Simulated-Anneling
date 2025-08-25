# Cargar el diccionario del json para los multiplicadores de la tabla de tipos
# typeMult['attack_type']['defensive_type']
import json
with open('type-chart.json') as file:
    typeMult = json.load(file)
types = typeMult.keys()


import pypokedex as dex
import math

## ESTADISTICAS INDIVIDUALES ##
import pypokedex as dex
import math

def atkScore(pokemon: dex.Pokemon, t_def:str) -> float:
    atk = pokemon.base_stats.attack
    types_atk = pokemon.types

    if len(pokemon.types)<2:
        t_atk = types_atk[0]
        score = atk * typeMult[t_atk][t_def]
    else:
        t1_atk, t2_atk = types_atk
        score = max(typeMult[t1_atk][t_def], typeMult[t2_atk][t_def]) * atk
    
    return score

def spAtkScore(pokemon: dex.Pokemon, t_def:str) -> float:
    atk = pokemon.base_stats.sp_atk
    types_atk = pokemon.types

    if len(pokemon.types)<2:
        t_atk = types_atk[0]
        score = atk * typeMult[t_atk][t_def]
    else:
        t1_atk, t2_atk = types_atk
        score = max(typeMult[t1_atk][t_def], typeMult[t2_atk][t_def]) * atk

    return score


def defScore(pokemon: dex.Pokemon, t_atk:str) -> float:
    defe = pokemon.base_stats.defense
    hp = pokemon.base_stats.hp
    types_def = pokemon.types

    if len(pokemon.types)<2:
        t_def = types_def[0]
        score = math.sqrt(defe*hp) / typeMult[t_atk][t_def]
    else:
        t1_def, t2_def = types_def
        score = math.sqrt(defe*hp) / (typeMult[t_atk][t1_def] * typeMult[t_atk][t2_def])
    
    return score

def spDefScore(pokemon: dex.Pokemon, t_atk:str) -> float:
    defe = pokemon.base_stats.sp_def
    hp = pokemon.base_stats.hp
    types_def = pokemon.types

    if len(pokemon.types)<2:
        t_def = types_def[0]
        score = math.sqrt(defe*hp) / typeMult[t_atk][t_def]
    else:
        t1_def, t2_def = types_def
        score = math.sqrt(defe*hp) / (typeMult[t_atk][t1_def] * typeMult[t_atk][t2_def])

    return score



## FITNESS GLOBAL ##
import queue as q
def teamScore(team: list[int]) -> float:
    score = 0.0
    minq_vel = q.PriorityQueue()

    T = len(types)
    invT = 1/T

    minq_atkScores:list[q.PriorityQueue] = [q.PriorityQueue() for _ in range(T)]
    minq_spAtkScores:list[q.PriorityQueue] = [q.PriorityQueue() for _ in range(T)]
    minq_defScores:list[q.PriorityQueue] = [q.PriorityQueue() for _ in range(T)]
    minq_spDefScores:list[q.PriorityQueue] = [q.PriorityQueue() for _ in range(T)]

    
    for pokemon_id in team:
        pokemon = dex.get(dex=pokemon_id)

        i=0
        for type in types:
            minq_atkScores[i].put(atkScore(pokemon, type)); minq_spAtkScores[i].put(spAtkScore(pokemon, type))
            minq_defScores[i].put(defScore(pokemon, type)); minq_spDefScores[i].put(spDefScore(pokemon, type))
            i+=1
        minq_vel.put(pokemon.base_stats.speed)

    for rank in range(len(team), 0, -1):
        score_this_rank = 0.0
        for i in range(0,T):
            score_this_rank += (minq_atkScores[i].get() + minq_spAtkScores[i].get() + minq_defScores[i].get() + minq_spDefScores[i].get()) * invT
        score_this_rank *= invT
        score_this_rank += minq_vel.get()/rank/rank
        score_this_rank /= rank
        score += score_this_rank
    return score


## MOSTRAR INFORMACIÓN SOBRE EL EQUIPO
import pypokedex
from io import BytesIO
from IPython.display import display, HTML
import base64
import matplotlib.pyplot as plt

def showTeam (pokemons_ids):

    print(f"teamScore = {teamScore(pokemons_ids)}")


    # Mostrar la información en una tabla
    html = ''' 
    <table border='1'>
        <tr>
            <th>#ID</th>
            <th>Imagen</th>
            <th>Nombre</th>
            <th>Tipo</th>
            <th>Estadísticas </th>
            <th>Atacando frente a tipos</th>
            <th>Defendiendo frente a tipos </th>
        </tr> 
    '''

    # Función para mapear el valor de la estadística a un color
    def get_color(value):
        if value <= 100:
            r = int(255 * (1 - value / 100))
            g = int(255 * (value / 100))
            b = 0
        else:
            r = 0
            g = 255 #int(255 * (1 - (value - 100) / 155))
            b = int(255 * ((value - 100) / 155) * 1.5)
            if b > 255:
                b = 255  # Asegurarse de que el valor no exceda 255
        return f'#{r:02x}{g:02x}{b:02x}'

    # Obtener la información de los Pokémon
    for pokemon_id in pokemons_ids:
        pokemon = pypokedex.get(dex=pokemon_id)
        image_url = pokemon.sprites.front.get('default')
        stats = pokemon.base_stats

        # Crear el gráfico de barras con las estadísticas
        values = [stats.hp, stats.attack, stats.defense, stats.sp_atk, stats.sp_def, stats.speed]
        colors = [get_color(value) for value in values]
        fig, ax = plt.subplots()
        ax.bar(['HP', 'Atk', 'Def', 'Sp.Atk', 'Sp.Def', 'Speed'], values, color=colors)
        
        # Guardar el gráfico como imagen en memoria
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Obtener tabla de tipos de ataque
        good_attacking = []
        bad_attacking = []

        for my_type in pokemon.types:
            for other_type in types:
                if typeMult[my_type][other_type] == 2:
                    good_attacking.append(other_type)
                elif typeMult[my_type][other_type] == 0.5:
                    bad_attacking.append(other_type)

        bad_attacking = [item for item in bad_attacking if item not in good_attacking]
        
        # Obtener tabla de tipos defendiendo
        very_good_defending = []
        good_defending = []
        neutral_defending = []
        bad_defending = []
        very_bad_defending = []

        arrayByMult = {
            25: very_good_defending,
            50: good_defending,
            100: neutral_defending,
            200: bad_defending,
            400: very_bad_defending
        }

        for other_type in types:
            mult1 = typeMult[other_type][pokemon.types[0]]
            mult2 = 1 if len(pokemon.types)<2 else typeMult[other_type][pokemon.types[1]]
            arrayByMult[int(mult1*mult2*100)].append(other_type)

        # Imprimir tabla con la información previamente recopilada
        html += "<tr>"
        html += f"<td>#{pokemon_id}</td>"
        html += f"<td><img src='{image_url}' width='150'></td>"
        html += f"<td><b>{pokemon.name.capitalize()}</b></td>"
        html += f"<td>{pokemon.types}</td>"
        html += f"<td><img src='data:image/png;base64,{img_base64}' width='300'></td>"
        html += f"<td>x2: {good_attacking}<br>x0.5: {bad_attacking}</td>"
        html += f"<td>/4: {very_good_defending}<br>/2: {good_defending}<br>/0.5: {bad_defending} <br>/0.25: {very_bad_defending}</td>"
        html += "</tr>"

    html += "</table>"

    display(HTML(html))