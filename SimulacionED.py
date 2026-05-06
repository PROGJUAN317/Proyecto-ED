import sys
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# Parámetros del modelo

entrada = 5        # L/min
k = 0.2            # coeficiente de salida
dt = 0.1           # paso de tiempo (min)
tiempo_total = 30  # minutos

# Condición inicial
V = 0

# Listas para graficar
tiempos = []
volumenes = []

t = 0
while t <= tiempo_total:
    tiempos.append(t)
    volumenes.append(V)

    # Ecuación diferencial (Euler)
    dVdt = entrada - k * V
    V = V + dVdt * dt
    t += dt

# Gráfica
if plt is not None:
    plt.plot(tiempos, volumenes)
    plt.xlabel("Tiempo (min)")
    plt.ylabel("Volumen (L)")
    plt.title("Llenado del tanque")
    plt.grid()
    plt.show()
else:
    print("matplotlib no está disponible. Resultados:")
    for tiempo, volumen in zip(tiempos, volumenes):
        print(f"{tiempo:.1f} min -> {volumen:.2f} L")