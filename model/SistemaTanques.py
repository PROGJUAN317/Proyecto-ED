from model.Tanque import Tanque

class SistemasTanques:
    def __init__(self,entrada,k1,k2):
        self.tanque1= Tanque(entrada,k1)
        self.tanque2=Tanque(0,k2) # sin entrada directa

    def actualizar(self,dt):
         flujo = self.tanque1.k* self.tanque1.v # flujo que sale del tanque 1


         self.tanque1.actualizar(dt)# tanque 1 se actualiza con su propia ecuación
          # tanque 2 recibe el flujo del tanque 1 y pierde por su propia válvula

         self.tanque2.v += (flujo - self.tanque2.k* self.tanque2.v)*dt

