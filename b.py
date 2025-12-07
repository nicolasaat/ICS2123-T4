from simulation import simulate
import numpy as np

def print_overallresults(results: list):
    total_arrivals = 0
    total_rejected = 0
    total_voted = 0
    total_maxqueue = 0
    total_queue_time = []
    total_system_time = []
    for block in range(1,5):
        arrivals_data = list(map(lambda x: x[0][block], results))
        rejected_data = list(map(lambda x: x[1][block], results))
        voted_data = list(map(lambda x: x[2][block], results))
        queue_time_data = list(map(lambda x: x[4][block], results))
        system_time_data = list(map(lambda x: x[5][block], results))
        maxqueue_data = list(map(lambda x: x[7][block], results))
        total_arrivals += np.average(arrivals_data)
        total_rejected += np.average(rejected_data)
        total_voted += np.average(voted_data)
        total_maxqueue = max(total_maxqueue, max(maxqueue_data))
        total_queue_time +=  (queue_time_data)
        total_system_time +=  (system_time_data)
        print(f"Bloque {block}:")
        print_results(np.average(arrivals_data), np.average(rejected_data), 
                      np.average(voted_data), np.average(queue_time_data),
                      np.average(system_time_data), max(maxqueue_data))
        print()
        
    print("Global:")
    print_results(total_arrivals, total_rejected, 
                total_voted, np.average(total_queue_time), 
                np.average(total_system_time), total_maxqueue)
    overtime_data = list(map(lambda x: x[3], results))
    overtime_voters_data = list(map(lambda x: x[6], results))
    print(f"Overtime: {round(np.average(overtime_data),3)}")
    print(f"Votantes presentes despues de las 18:00: {round(np.average(overtime_voters_data),3)}")

def print_results(arrivals, rejected, voted, queue_time, system_time, maxqueue):
    print(f"Entraron a la cola: {round(arrivals,3)}")
    print(f"Lograron votar: {round(voted, 3)}")
    print(f"Rechazados para la cola: {round(rejected, 3)}")
    print(f"Tiempo promedio de espera en cola: {round(queue_time, 3)}")
    print(f"Tiempo promedio en sistema: {round(system_time, 3)}")
    print(f"Cola más larga observada: {maxqueue}")


results = []

for _ in range(300):
    result = simulate()
    results.append(result)
print_overallresults(results)