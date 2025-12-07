import numpy as np, os
import seaborn as sb, matplotlib.pyplot as plt
from scipy import stats
import simulation, parameters

OUT = 'entrega_inciso_d'
os.makedirs(OUT, exist_ok=True)

# ... cargar o recalcular experimentos ...
# Para simplicidad: recalcula R=300 emparejadas (puedes reutilizar arrays guardados)
BASE_SEED = parameters.SEED
R = 300
cost_B = np.zeros(R); cost_E = np.zeros(R)
B_c, B_K = 4,70; E_c, E_K = 5,85
TSLA = 10

for r in range(R):
    seed = BASE_SEED + r
    simulation.GENERATOR = np.random.default_rng(seed)
    arrivalsB, rejectedB, votedB, OT_B, timeqB, timesysB, voters_closeB, maxqB = simulation.simulate(C=B_c, K=B_K)
    simulation.GENERATOR = np.random.default_rng(seed)
    arrivalsE, rejectedE, votedE, OT_E, timeqE, timesysE, voters_closeE, maxqE = simulation.simulate(C=E_c, K=E_K)
    Perd_B = sum(rejectedB.values()); Perd_E = sum(rejectedE.values())
    Exc_B = sum(votedB[b] * max(timeqB[b] - TSLA,0) for b in [1,2,3,4])
    Exc_E = sum(votedE[b] * max(timeqE[b] - TSLA,0) for b in [1,2,3,4])
    # compute cost (copy compute_cost code)
    Cc_lin, Cc_quad, COT, CSLA, CL, Kref, Kmax, CK_low, CK_high = 6000,1800,400,20,15000,90,160,2500,700
    def compute_cost_local(c,K,OT,Exc,Perd):
        return Cc_lin*c + Cc_quad*(c**2) + COT*OT + CSLA*Exc + CL*Perd + CK_low*max(Kref-K,0) + CK_high*max(K-Kmax,0)
    cost_B[r] = compute_cost_local(B_c,B_K,OT_B,Exc_B,Perd_B)
    cost_E[r] = compute_cost_local(E_c,E_K,OT_E,Exc_E,Perd_E)

diff = cost_B - cost_E

# Guardar reporte numérico
def CI95(samples):
    n=len(samples); mean=samples.mean(); sd=samples.std(ddof=1)
    t = stats.t.ppf(0.975, df=n-1); half = t*sd/np.sqrt(n)
    return mean, mean-half, mean+half, sd

CB_mean, CB_low, CB_high, _ = CI95(cost_B)
CE_mean, CE_low, CE_high, _ = CI95(cost_E)
D_mean, D_low, D_high, _ = CI95(diff)

with open(os.path.join(OUT,'resultados_inciso_d.txt'),'w') as f:
    f.write(f"C(B)={CB_mean:.2f} IC95=[{CB_low:.2f},{CB_high:.2f}]\n")
    f.write(f"C(E)={CE_mean:.2f} IC95=[{CE_low:.2f},{CE_high:.2f}]\n")
    f.write(f"Delta={D_mean:.2f} IC95=[{D_low:.2f},{D_high:.2f}]\n")

# Histograma Δ
plt.figure(figsize=(8,5))
sb.histplot(diff, kde=True)
plt.axvline(D_mean,color='k',linestyle='--'); plt.axvline(D_low,color='r',linestyle=':'); plt.axvline(D_high,color='r',linestyle=':')
plt.title('Histograma de Δ = C(B)-C(E)')
plt.tight_layout()
plt.savefig(os.path.join(OUT,'hist_delta.png')); plt.close()

# Boxplot costos
plt.figure(figsize=(7,5))
sb.boxplot(data=[cost_B, cost_E])
plt.xticks([0,1],['C(B)','C(E)']); plt.ylabel('Costo'); plt.tight_layout()
plt.savefig(os.path.join(OUT,'box_costs.png')); plt.close()

# Heatmap Wq (inciso c) - recalcula R=30 por combinación
C_values = [2,3,4,5,6,7,8,9]
K_values = [30,40,60,80,100,130,170,parameters.INFINITY]
R_small = 30
Wq_matrix = np.zeros((len(C_values),len(K_values)))
for i,c in enumerate(C_values):
    for j,K in enumerate(K_values):
        wq_samples=[]
        for rr in range(R_small):
            sim_seed = BASE_SEED + 10000 + i*100 + j*10 + rr
            simulation.GENERATOR = np.random.default_rng(sim_seed)
            _,_,_,OT,timeq,_,_,_ = simulation.simulate(C=c,K=K)
            wq_samples.append(np.mean(list(timeq.values())))
        Wq_matrix[i,j]=np.mean(wq_samples)

plt.figure(figsize=(10,6))
sb.heatmap(Wq_matrix, xticklabels=['30','40','60','80','100','130','170','∞'], yticklabels=[str(c) for c in C_values], annot=True, fmt=".2f")
plt.title('Heatmap Wq (R=30)')
plt.tight_layout()
plt.savefig(os.path.join(OUT,'heatmap_Wq.png')); plt.close()

print("Plots y reporte guardados en carpeta:", OUT)