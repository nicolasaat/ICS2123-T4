import numpy as np
from parameters import *


GENERATOR = np.random.default_rng(seed=SEED)

def get_current_block(time: int) -> int:
    '''
    Retorna el numero del bloque dependiendo el tiempo
    que ha pasado
    '''
    if time < 120:
        return 1
    elif time >=120 and time < 240:
        return 2
    elif time >=240 and time < 450:
        return 3
    else:
        return 4
    
def generate_arrivals():
    '''
    Genera llegadas independientes una de otra segun
    una distribucion Erlang(2, theta)
    '''
    times = []
    accum = 0
    while accum <= TIME_LIMIT:
        block = get_current_block(accum)
        arrival = GENERATOR.gamma(2, THETA[block])
        accum += arrival
        if accum <= TIME_LIMIT:
            times.append((accum, "arrival"))
    return times

def get_group_size(time_elapsed: int):
    '''
    Genera la cantidad de votantes que hay en un
    grupo que ha llegado al sistema segun:
    size = 1 + Poisson(lambda)
    '''
    block = get_current_block(time_elapsed)
    return 1 + GENERATOR.poisson(LMBDA[block])

def generate_voters(size: int, time_elapsed: int):
    '''
    Genera los tipo de votantes de un grupo segun ciertas
    probabilidades. Donde 0 son votantes rapidos, 1 medios
    y 2 los que necesitan asistencia
    '''
    group = []
    block = get_current_block(time_elapsed)
    probabilities = TYPE_PROB[block]
    for _ in range(size):
        random = GENERATOR.random()
        if random <= probabilities[0]:
            group.append(0)
        elif random <= probabilities[0]+probabilities[1]:
            group.append(1)
        else:
            group.append(2)
    return group


def process_arrival(queue: list, queue_limit: int, time_elapsed: int, size: int):
    '''
    Se agregan los votantes que han llegado ssi hay espacio en el sistema
    '''
    if len(queue) + size <= queue_limit:
        queue += generate_voters(size, time_elapsed)

def get_sorted_queue(unsorted_queue: list):
    '''
    Se ordena la cola segun prioridad por el tipo de votante. Donde los de
    tipo 2 quedan al principio y luego el resto sigue orden FIFO
    '''
    prioritized = list(filter(lambda x: x==2, unsorted_queue))
    unprioritized = list(filter(lambda x: x!=2, unsorted_queue))

    return prioritized + unprioritized

def fill_empty_booths(booths: dict, queue: list, events: list, time_elapsed: int):
    '''
    Se llenan las cabinas vacias siempre que haya al menos un votante en la cola.
    Además, cuando entra un nuevo votante se calcula su tiempo de salida segun una
    distribucion Triangular(l,m,r), la que se agrega a los eventos
    '''
    empty_booths = list(filter(lambda x: x[1] == 0, booths.items()))
    for booth_number, booth_state in empty_booths:
        if len(queue)>0:
            next_voter = queue.pop(0)
            booths[booth_number] = 1
            left, mode, right = TRI[next_voter]
            next_voter_exit = time_elapsed + GENERATOR.triangular(left, mode, right)
            events.append((next_voter_exit, "exit"))
        else:
            break
    events.sort(key=lambda x: x[0])

def process_exit(booths: dict):
    '''
    Libera arbitrariamente una cabina
    '''
    if sum(booths.values())>0:
        for booth_number, booth_state in booths.items():
            if booth_state == 1:
                booths[booth_number] = 0
                break

def print_header(C, K):
    print("="*30)
    print(f"SIMULACIÓN (C={C}, K={K})")
    print("="*30)

def print_results(arrivals, rejected, voted, over_time):
    print(f"Entraron a la cola: {arrivals}")
    print(f"Rechazados para la cola: {rejected}")
    print(f"Lograron votar: {voted}")
    print(f"Overtime: {over_time}")
    print()

def print_overallresults(results: list):
    arrivals_data = list(map(lambda x: x[0], results))
    rejected_data = list(map(lambda x: x[1], results))
    voted_data = list(map(lambda x: x[2], results))
    overtime_data = list(map(lambda x: x[3], results))
    print("PROMEDIO:")
    print(f"Entraron a la cola: {np.average(arrivals_data)}")
    print(f"Rechazados para la cola: {np.average(rejected_data)}")
    print(f"Lograron votar: {np.average(voted_data)}")
    print(f"Overtime: {np.average(overtime_data)}")
    
def simulate(C = 4, K = 70):
    #print_header(C, K)
    time_elapsed = 0
    arrivals = 0
    voted = 0
    rejected = 0

    queue = []
    booths = {i: 0 for i in range(1, C+1)}
    events = generate_arrivals()

    while len(events) > 0:
        event = events.pop(0)
        time_elapsed = event[0]
        if event[1] == "arrival":
            before = len(queue)
            size = get_group_size(time_elapsed)
            process_arrival(queue, K - C, time_elapsed, size)
            after = len(queue)
            if after - before > 0:
                arrivals += size
            else:
                rejected += size
        else:
            over_time = max(0, time_elapsed - TIME_LIMIT)
            process_exit(booths)
            voted += 1
        queue = get_sorted_queue(queue)
        fill_empty_booths(booths, queue, events, time_elapsed)
        queue = get_sorted_queue(queue)
    return arrivals, rejected, voted, round(over_time, 3)


results = []

for _ in range(300):
    result = simulate()
    results.append(result)
    #print_results(*result)
print_overallresults(results)



