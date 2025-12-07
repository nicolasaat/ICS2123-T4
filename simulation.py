import numpy as np
from parameters import *


GENERATOR = np.random.default_rng(seed=SEED)

class Voter():
    def __init__(self, type:int, arrival_time = None, booth_time = None, exit_time = None):
        self.type = type
        self.arrival_time = arrival_time
        self.booth_time = booth_time
        self.exit_time = exit_time

    def get_time_in_queue(self):
        return self.booth_time - self.arrival_time
    
    def get_time_in_system(self):
        return self.exit_time - self.arrival_time

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
            group.append(Voter(0, time_elapsed))
        elif random <= probabilities[0]+probabilities[1]:
            group.append(Voter(1, time_elapsed))
        else:
            group.append(Voter(2, time_elapsed))
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
    prioritized = list(filter(lambda x: x.type==2, unsorted_queue))
    unprioritized = list(filter(lambda x: x.type!=2, unsorted_queue))

    return prioritized + unprioritized

def fill_empty_booths(booths: dict, queue: list, events: list, time_elapsed: int,
                      time_in_queue: dict, time_in_system: dict):
    '''
    Se llenan las cabinas vacias siempre que haya al menos un votante en la cola.
    Además, cuando entra un nuevo votante se calcula su tiempo de salida segun una
    distribucion Triangular(l,m,r), la que se agrega a los eventos
    '''
    empty_booths = list(filter(lambda x: x[1] == 0, booths.items()))
    block = get_current_block(time_elapsed)
    for booth_number, booth_state in empty_booths:
        if len(queue)>0:
            next_voter = queue.pop(0)
            booths[booth_number] = 1
            left, mode, right = TRI[next_voter.type]
            next_voter.booth_time = time_elapsed
            next_voter.exit_time = time_elapsed + GENERATOR.triangular(left, mode, right)
            time_in_queue[block].append(next_voter.get_time_in_queue())
            time_in_system[block].append(next_voter.get_time_in_system())
            events.append((next_voter.exit_time, "exit"))
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
    
def simulate(C = 4, K = 70):
    time_elapsed = 0
    arrivals = {1: 0, 2: 0, 3:0 , 4:0}
    voted = {1: 0, 2: 0, 3:0 , 4:0}
    rejected = {1: 0, 2: 0, 3:0 , 4:0}
    time_in_queue = {1: [], 2: [], 3:[], 4:[]}
    time_in_system = {1: [], 2: [], 3:[], 4:[]}
    max_queue = {1: 0, 2: 0, 3:0 , 4:0}
    voters_at_closing_time = 0

    queue = []
    booths = {i: 0 for i in range(1, C+1)}
    events = generate_arrivals()

    while len(events) > 0:
        event = events.pop(0)
        time_elapsed = event[0]
        block = get_current_block(time_elapsed)
        if event[1] == "arrival":
            before = len(queue)
            size = get_group_size(time_elapsed)
            process_arrival(queue, K - C, time_elapsed, size)
            after = len(queue)
            if after - before > 0:
                arrivals[block] += size
            else:
                rejected[block] += size
        else:
            over_time = max(0, time_elapsed - TIME_LIMIT)
            if (voters_at_closing_time == 0 and time_elapsed > TIME_LIMIT):
                voters_at_closing_time = len(list(filter(lambda x: x[1] == 0, booths.items())))
            process_exit(booths)
            voted[block] += 1
        queue = get_sorted_queue(queue)
        fill_empty_booths(booths, queue, events, time_elapsed, time_in_queue, time_in_system)
        queue = get_sorted_queue(queue)

        max_queue[block] = max(max_queue[block], len(queue))

        
    for key, value in time_in_queue.items():
        time_in_queue[key] = np.average(value)
    for key, value in time_in_system.items():
        time_in_system[key] = np.average(value)
    return arrivals, rejected, voted, round(over_time, 3), time_in_queue, time_in_system, voters_at_closing_time, max_queue
