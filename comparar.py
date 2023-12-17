from bs4 import BeautifulSoup
import difflib
import logging

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
		contido = sacar_contido_seccion(descargar.descargar_paxina_materia(cod_materia, i, ano, idioma))
		contidos[opcions.SECCIONS[i]] = contido
	return contidos
