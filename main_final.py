# reproducir experimento emparejado R=300 para inciso (d)
import numpy as np
from scipy import stats
import simulation, parameters
import numpy as np

# Costos
Cc_lin = 6000
Cc_quad = 1800
COT = 400
CSLA = 20
CL = 15000
Kref = 90
Kmax = 160
CK_low = 2500
CK_high = 700
TSLA = 10

def compute_cost(c, K, OT, Exc, Perd):
    cost_cabinas = Cc_lin * c + Cc_quad * (c**2)
    cost_desempeno = COT * OT + CSLA * Exc + CL * Perd
    cost_K = CK_low * max(Kref - K, 0) + CK_high * max(K - Kmax, 0)
    return cost_cabinas + cost_desempeno + cost_K

# Parámetros del experimento
R = 300
BASE_SEED = parameters.SEED
B_c, B_K = 4, 70
E_c, E_K = 5, 85

cost_B = np.zeros(R)
cost_E = np.zeros(R)

for r in range(R):
    seed = BASE_SEED + r
    # emparejado: misma semilla para B y E
    simulation.GENERATOR = np.random.default_rng(seed)
    arrivalsB, rejectedB, votedB, OT_B, timeqB, timesysB, voters_closeB, maxqB = simulation.simulate(C=B_c, K=B_K)
    simulation.GENERATOR = np.random.default_rng(seed)
    arrivalsE, rejectedE, votedE, OT_E, timeqE, timesysE, voters_closeE, maxqE = simulation.simulate(C=E_c, K=E_K)

    Perd_B = sum(rejectedB.values())
    Perd_E = sum(rejectedE.values())

    # Aproximación de Exc usando promedios por bloque (igual que en tu simulador)
    Exc_B = sum(votedB[b] * max(timeqB[b] - TSLA, 0) for b in [1,2,3,4])
    Exc_E = sum(votedE[b] * max(timeqE[b] - TSLA, 0) for b in [1,2,3,4])

    cost_B[r] = compute_cost(B_c, B_K, OT_B, Exc_B, Perd_B)
    cost_E[r] = compute_cost(E_c, E_K, OT_E, Exc_E, Perd_E)

# Función IC95
def CI95(samples):
    n = len(samples)
    mean = samples.mean()
    sd = samples.std(ddof=1)
    t = stats.t.ppf(0.975, df=n-1)
    half = t * sd / np.sqrt(n)
    return mean, mean-half, mean+half, sd

CB_mean, CB_low, CB_high, CB_sd = CI95(cost_B)
CE_mean, CE_low, CE_high, CE_sd = CI95(cost_E)
diff = cost_B - cost_E
D_mean, D_low, D_high, D_sd = CI95(diff)

print("Resultados (R=300 réplicas emparejadas)\n")
print(f"C(B) estimado = {CB_mean:,.2f}   IC95 = [{CB_low:,.2f}, {CB_high:,.2f}]   sd = {CB_sd:,.2f}")
print(f"C(E) estimado = {CE_mean:,.2f}   IC95 = [{CE_low:,.2f}, {CE_high:,.2f}]   sd = {CE_sd:,.2f}")
print(f"Δ = C(B) - C(E) estimado = {D_mean:,.2f}   IC95 = [{D_low:,.2f}, {D_high:,.2f}]   sd = {D_sd:,.2f}\n")

if D_low > 0:
    print(f"Conclusión: con 95% de confianza E es preferible a B. Límite inferior IC95(Δ) = {D_low:,.2f} > 0")
else:
    print("No hay evidencia concluyente (IC95 de Δ incluye 0).")

print("\nRegla práctica: para recuperar inversión I en T días con 95% confianza usar:")
print(f"    I < T * {D_low:,.2f}   (usar D_low, límite inferior del IC de Δ)")