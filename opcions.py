import logging
import sys

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

# REXISTROS #

logging.basicConfig(
	filename='logs/info.log',
	level=logging.INFO,
	format='%(levelname)s:%(funcName)s:%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
