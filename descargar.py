import re
import requests
from bs4 import BeautifulSoup
import logging
import os

import opcions


class DescargaFallou(Exception):
	valor: int = 200

	def __init__(self, valor: int, mensaxe: str = None):
		if mensaxe is not None:
			super(mensaxe)
		else:
			super()
		self.valor = valor


def xerar_url_materias(
	codigo: str, materia: bool, ano: str = None, idioma: str = None) -> str:
	# ano = 20XX_YY
	# idioma = eng, cast, cat
	#   cat é galego
	# materia indica se se vai descargar a páxina da materia (True) ou a listaxe
	#  de materias (False)
	centro = re.compile('([0-9][0-9][0-9])[0-9G].*').search(codigo).group(1)
	cod_materia = re.compile('([0-9][0-9][0-9][0-9G][0-9][0-9]).*')\
		.search(codigo).group(1) if materia else codigo
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
	r = requests.get(url, allow_redirects=False)
	if r.status_code != 200:
		logging.debug(url)
		raise DescargaFallou(r.status_code)
	return r.text


def descargar_paxina_materia(
	cod_materia: str, seccion: int, ano: str, idioma: str):
	# Devolve a sección da materia, mirando en caché se existe
	ficheiro = f'{opcions.CACHE}/{ano}A{cod_materia}S{seccion}I{idioma}'
	try:
		with open(ficheiro, 'r') as file:
			if os.path.getsize(ficheiro) < 10:
				raise FileNotFoundError
			logging.info(f'{ano}A{cod_materia}S{seccion}I{idioma} presente na caché')
			pax = file.read()
	except FileNotFoundError:
		logging.info(f'{ano}A{cod_materia}S{seccion}I{idioma} non dispoñible. Descargando')
		with open(ficheiro, 'w') as file:
			pax = descargar_paxina(
				xerar_url_materias(cod_materia, materia=True, ano=ano, idioma=idioma) + f'&fitxa_apartat={seccion}')
			file.write(pax)
	return pax


def lista_materias(codigo_titulacion, ano, idioma):
	# Descargar contido da páxina
	pax = descargar_paxina(xerar_url_materias(codigo_titulacion, False, ano, idioma))
	# Buscar na páxina o <div> #contingut, e dentro del as etiquetas <a> cuxa URL
	# conteña o parametro assignatura
	regex = re.compile("&assignatura=([0-9][0-9][0-9][0-9G][0-9]+)")
	parser = BeautifulSoup(pax, 'html.parser')
	# Nome da titulación
	nome_titulacion = parser.find_all("a", class_='subapartat_actiu')[0]
	div = parser.find(id="contingut")
	# Devolver listaxe de materias
	materias = []
	nomes = {}
	for url in div.find_all('a'):
		materia = regex.search(url.get('href'))
		if materia is not None:
			materias.append(materia.group(1))
			nomes[materia.group(1)] = url.get_text()
	return materias, nomes, nome_titulacion.string
