import re
import requests
from bs4 import BeautifulSoup
import difflib
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

# TODO: Configurable
CODIGO = "614G01"
ANO_A = "2023_24"
ANO_B = "2022_23"
IDIOMA = "cat"


# FUNCIÓNS #


def xerar_url_materias(codigo: str, materia: bool, ano: str = None, idioma: str = None) -> str:
	# ano = 20XX_YY
	# idioma = eng, cast, cat
	#   cat é galego
	# materia indica se se vai descargar a páxina da materia (True) ou a listaxe
	#  de materias (False)
	centro = re.compile('([0-9]+)G.*').search(codigo).group(1)
	cod_materia = re.compile('([0-9]+G[0-9][0-9]).*').search(codigo).group(1) if materia else codigo
	url = f'https://guiadocente.udc.es/guia_docent/index.php?centre={centro}&ensenyament={cod_materia}'
	if ano is not None:
		url += f'&any_academic={ano}'
	if idioma is not None:
		url += f'&idioma={idioma}'
	if materia:
		url += f'&assignatura={codigo}'
	else:
		url += '&consulta=assignatures'
	return url


def descargar_paxina(url: str) -> str:
	r = requests.get(url)
	if r.status_code != 200:
		raise Exception()
	return r.text


def descargar_paxina_materia(cod_materia: str, seccion: int, ano: str, idioma: str):
	# Devolve a sección da materia, mirando en caché se existe
	ficheiro = f'{CACHE}/{ano}A{cod_materia}S{seccion}'
	try:
		with open(ficheiro, 'r') as file:
			logging.info(f'{ano}A{cod_materia}S{seccion} presente na caché')
			pax = file.read()
	except FileNotFoundError:
		logging.info(f'{ano}A{cod_materia}S{seccion} non dispoñible. Descargando')
		with open(ficheiro, 'w') as file:
			pax = descargar_paxina(
				xerar_url_materias(cod_materia, materia=True, ano=ano, idioma=idioma) + f'&fitxa_apartat={seccion}')
			file.write(pax)
	parser = BeautifulSoup(pax, 'html.parser')
	# Buscar a última táboa dentro do div #contingut
	div = parser.find(id="contingut")
	try:
		taboas = div.find_all('table')
		return taboas[len(taboas) - 1].decode_contents()
	except AttributeError:
		logging.error(f'Exception on {ficheiro}')
		raise AttributeError


def lista_materias(codigo_titulacion, ano, idioma):
	# Descargar contido da páxina
	pax = descargar_paxina(xerar_url_materias(codigo_titulacion, False, ano, idioma))
	# Buscar na páxina o <div> #contingut, e dentro del as etiquetas <a> cuxa URL
	# conteña o parametro assignatura
	regex = re.compile("&assignatura=([0-9]+G[0-9]+)")
	parser = BeautifulSoup(pax, 'html.parser')
	div = parser.find(id="contingut")
	# Devolver listaxe de materias
	return [materia.group(1) for materia in [regex.search(url.get('href')) for url in div.find_all('a')] if materia is not None]


def descargar_seccions(cod_materia: str, ano: str, idioma: str) -> dict:
	logging.info(f'Descargando materia {cod_materia}')
	contidos = {
		SECCIONS[1]: '',
		SECCIONS[2]: '',
		SECCIONS[3]: '',
		SECCIONS[4]: '',
		SECCIONS[5]: '',
		SECCIONS[6]: '',
		SECCIONS[7]: '',
		SECCIONS[8]: '',
		SECCIONS[9]: '',
	}

	for i in range(1, 10):
		contido = descargar_paxina_materia(cod_materia, i, ano, idioma)
		contidos[SECCIONS[i]] = contido
	return contidos


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(funcName)s:%(message)s')

	logging.info('Descargando listaxe de materias')
	lista_materias = lista_materias(CODIGO, ANO_A, IDIOMA)

	logging.info(f'Descargando materias para o ano {ANO_A}')
	contidos_A = {
		materia: descargar_seccions(materia, ano=ANO_A, idioma=IDIOMA)
		for materia in lista_materias
	}
	logging.info(f'Descargando materias para o ano {ANO_B}')
	contidos_B = {
		materia: descargar_seccions(materia, ano=ANO_B, idioma=IDIOMA)
		for materia in lista_materias
	}

	differ = difflib.HtmlDiff()

	buscar_ano_A = re.compile(f'.*{ANO_A}.*')
	buscar_ano_B = re.compile(f'.*{ANO_B}.*')

	for materia in lista_materias:
		saida = f'		{materia}:\n'
		amosar = False
		for i in range(1, 10):
			texto_A = [line for line in contidos_A[materia][SECCIONS[i]].splitlines(keepends=True) if buscar_ano_A.search(line) is None]
			texto_B = [line for line in contidos_B[materia][SECCIONS[i]].splitlines(keepends=True) if buscar_ano_B.search(line) is None]
			delta = differ.make_file(fromlines=texto_A, tolines=texto_B, fromdesc=ANO_A, todesc=ANO_B)
			with open(f'out/{materia}.htm', 'w') as file:
				file.write(delta)
			#cambios = [cambio for cambio in delta if cambio[0] in ('?', '+', '-')]
			#if len(cambios) > 0:
			#	saida += f'{SECCIONS[i]}\n{cambios}'
			#	amosar = True
		if amosar:
			print(saida)
