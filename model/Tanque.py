class Tanque:
     def __init__(self, entrada, k, volumen=0):
         self.entrada= entrada
         self.k=k
         self.v=volumen

     def derivada(self):
          return self.entrada-self.k*self.v

     def actualizar(self,dt):
          self.v += self.derivada()*dt

