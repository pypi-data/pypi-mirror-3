import pilas

pilas.iniciar()

a = pilas.musica.cargar("musica/loop.wav")
a.reproducir(True)

pilas.ejecutar()

pilas.terminar()
