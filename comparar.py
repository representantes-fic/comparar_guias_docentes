from bs4 import BeautifulSoup
import re
import logging
import difflib
import html2text

import opcions
import descargar


def sacar_contido_seccion(paxina: str):
	parser = BeautifulSoup(paxina, 'html.parser')
	# Buscar a última táboa dentro do div #contingut
	div = parser.find(id="contingut")
	taboas = div.find_all('table')
	return taboas[len(taboas) - 1].decode_contents()


def descargar_seccions(cod_materia: str, ano: str, idioma: str) -> dict:
	logging.info(f'Descargando materia {cod_materia}')
	contidos = {
		opcions.SECCIONS[1]: '',
		opcions.SECCIONS[2]: '',
		opcions.SECCIONS[3]: '',
		opcions.SECCIONS[4]: '',
		opcions.SECCIONS[5]: '',
		opcions.SECCIONS[6]: '',
		opcions.SECCIONS[7]: '',
		opcions.SECCIONS[8]: '',
		opcions.SECCIONS[9]: '',
	}

	for i in range(1, 10):
		try:
			contido = sacar_contido_seccion(
				descargar.descargar_paxina_materia(cod_materia, i, ano, idioma))
		except descargar.DescargaFallou as e:
			if e.valor == 302:
				contido = ""
		contidos[opcions.SECCIONS[i]] = contido
	return contidos


def convertir_html_texto(paxina: str) -> str:
	return html2text.html2text(paxina)


def eliminar_ano(texto: list, ano: str):
	buscar_ano = re.compile(f'.*{ano}.*')

	out = []
	for line in texto.splitlines(keepends=True):
		if buscar_ano.search(line) is None:
			out.append(line)
	return out


def comparar_a_lista(texto_A: str, texto_B: str) -> list:
	differ = difflib.Differ()

	return differ.compare(texto_A, texto_B)


def comparar_a_html(texto_A: str, texto_B: str) -> str:
	d = difflib.HtmlDiff()
	return d.make_file(texto_A, texto_B, opcions.ANO_A, todesc=opcions.ANO_B)


def agrupar_comparacion(lineas: list) -> list[tuple]:
	# Lista de tuplas de liñas, as tuplas conteñen o antes e o despois.
	lista_cambios = []
	actual = ([], [])
	for linea in lineas:
		if linea[0] == '+':
			actual[0].append('')
			actual[1].append(linea)
		elif linea[0] == '-':
			actual[0].append(linea)
			actual[1].append('')
		else:
			if len(actual[0]) > 0:
				lista_cambios.append(actual)
				actual = ([], [])
	return lista_cambios
