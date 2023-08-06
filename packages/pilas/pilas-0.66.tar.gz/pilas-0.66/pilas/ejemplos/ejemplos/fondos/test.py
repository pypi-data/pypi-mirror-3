import pilas
pilas.iniciar(usar_motor='qtgl')

cielo = pilas.actores.Actor("cielo.png")
montes = pilas.actores.Actor("montes.png")
arboles = pilas.actores.Actor("arboles.png")
pasto = pilas.actores.Actor("pasto.png")

cielo.z = 10
montes.z = 5
arboles.z = 0
pasto.z = -10

fondo = pilas.fondos.Desplazamiento()

fondo.agregar(cielo, 0)
fondo.agregar(montes, 0.5)
fondo.agregar(arboles, 0.9)
fondo.agregar(pasto, 2)

"""
# Mueve la posicion con un temporizador.
def mover():
    fondo.posicion += 3
    return True
                    
pilas.mundo.tareas.siempre(1/15.0, mover)
"""

pilas.mundo.camara.x = [200], 10


pilas.ejecutar()
