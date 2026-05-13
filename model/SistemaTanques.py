# ──────────────────────────────────────────────
#  SistemasTanques.py — Modelo
#
#  Ecuaciones diferenciales:
#    dV1/dt = entrada  - k1 × V1      (T1)
#    dV2/dt = k1 × V1  - k2 × V2      (T2)
#
#  Los parámetros v1_max y v2_max son la capacidad física
#  de cada tanque: el volumen no puede superar ese valor.
# ──────────────────────────────────────────────

from model.Tanque import Tanque


class SistemasTanques:

    def __init__(self, entrada, k1, k2):
        """
        Inicializa el sistema con dos tanques conectados.

        Parámetros
        ----------
        entrada : float
            Flujo de agua que entra al tanque 1 (L/min).
        k1 : float
            Coeficiente de la válvula del tanque 1.
            Flujo_salida_T1 = k1 × V1  →  ese flujo pasa al tanque 2.
        k2 : float
            Coeficiente de la válvula del tanque 2.
            Flujo_salida_T2 = k2 × V2  →  sale al desagüe.
        """
        self.tanque1 = Tanque(entrada, k1)
        self.tanque2 = Tanque(0,       k2)

    def actualizar(self, dt, v1_max=None, v2_max=None):
        """
        Avanza la simulación un paso de tiempo dt.

        Parámetros
        ----------
        dt : float
            Paso de tiempo (min).
        v1_max : float | None
            Capacidad física del tanque 1 (L).
            Si el volumen calculado supera este valor, se recorta.
        v2_max : float | None
            Capacidad física del tanque 2 (L).

        Nota sobre el orden de cálculo
        --------------------------------
        Se calcula el flujo de salida del tanque 1 ANTES de actualizarlo
        para mantener consistencia temporal (método de Euler explícito).
        Si T1 está lleno (v1 == v1_max), el flujo real que entra a T2
        sigue siendo k1 × V1 (la válvula no se cierra, el exceso rebosa).
        """
        # ── Flujo que sale de T1 en este instante (antes de actualizarlo)
        flujo_t1_a_t2 = self.tanque1.k * self.tanque1.v

        # ── Actualizar Tanque 1
        #    dV1/dt = entrada - k1 × V1
        nuevo_v1 = self.tanque1.v + (self.tanque1.entrada - flujo_t1_a_t2) * dt
        self.tanque1.v = max(0.0, nuevo_v1)
        if v1_max is not None:
            self.tanque1.v = min(self.tanque1.v, v1_max)

        # ── Actualizar Tanque 2
        #    dV2/dt = flujo_entrada - k2 × V2
        nuevo_v2 = self.tanque2.v + (flujo_t1_a_t2 - self.tanque2.k * self.tanque2.v) * dt
        self.tanque2.v = max(0.0, nuevo_v2)
        if v2_max is not None:
            self.tanque2.v = min(self.tanque2.v, v2_max)