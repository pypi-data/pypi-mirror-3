all: test

actualizar_documentacion_en_la_web:
	cd doc; make html; cp -R build/html/ ~/proyectos/web_pilasengine/data/doc/
	cd ~/proyectos/web_pilasengine/data/doc/; hg pull; hg update; hg add html; hg ci html -m "actualizando la documentacion de on-line de pilas (pseudo-automaticamente)"; hg push

upload:
	python utils/actualizar_pypi.py

test:
	cd pilas/test; python test.py

resumen:
	cd utils; python generar_resumen_api.py; vicente resumen_api.rst -o resumen_api.pdf
