from simulation import simulate
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from scipy import stats
from parameters import INFINITY



C_values = [2,3,4,5,6,7,8,9]
K_values = [30,40,60,80,100,130,170,INFINITY]
R = 30

Wq_matrix = np.zeros((len(C_values), len(K_values)))
CI_low = np.zeros_like(Wq_matrix)
CI_high = np.zeros_like(Wq_matrix)

for i, c in enumerate(C_values):
    for j, K in enumerate(K_values):
        wq_samples = []

        for _ in range(R):
            result = simulate(C=c, K=K)
            time_in_queue = result[4]
            Wq = np.average(list(time_in_queue.values()))
            wq_samples.append(Wq)

        mean = np.mean(wq_samples)
        std = np.std(wq_samples, ddof=1)

        t = stats.t.ppf(0.975, df=R-1)
        half_width = t * std / np.sqrt(R)

        Wq_matrix[i,j] = mean
        CI_low[i,j] = mean - half_width
        CI_high[i,j] = mean + half_width

K_labels = ['30','40','60','80','100','130','170','∞']
C_labels = [str(c) for c in C_values]

plt.figure(figsize=(10,6))
sb.heatmap(Wq_matrix, 
           xticklabels=K_labels, 
           yticklabels=C_labels,
           annot=True, 
           fmt=".2f",
           cmap="viridis")

plt.xlabel("Capacidad del sistema K")
plt.ylabel("Número de cabinas (c)")
plt.title("Mapa de calor del tiempo promedio en cola Wq")
plt.show()
