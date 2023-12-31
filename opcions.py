import logging

# CONSTANTES #

SECCIONS = {
	1: 'Competencias',
	2: 'Resultados',
	3: 'Contidos',
	4: 'Planificacion',
	5: 'Metodoloxias',
	6: 'Atencion',
	7: 'Avaliacion',
	8: 'Fontes',
	9: 'Recomendacions'
}
CACHE = 'cache'
SAIDA = 'out'
INDICE = 'www/index.html'

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(funcName)s:%(message)s')
