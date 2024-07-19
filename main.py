#! /usr/bin/env python

import logging
import sys
from bs4 import BeautifulSoup

import descargar
import opcions
import comparar


def color(linea: str) -> BeautifulSoup:
	nodo = BeautifulSoup().new_tag('pre')
	nodo.string = linea
	if linea[0] == '-':
		nodo['class'] = 'remove'
	elif linea[0] == '+':
		nodo['class'] = 'add'
	return nodo


def xerar_paxina_html(codigo: str, ano_a: str, ano_b: str, idioma: str):
	logging.info('Descargando listaxe de materias')
	lista_materias, nomes, titulacion = descargar.lista_materias(codigo, ano_a, idioma)

	logging.info(f'Descargando materias para o ano {ano_a}')
	contidos_A = {
		materia: comparar.descargar_seccions(materia, ano=ano_a, idioma=idioma)
		for materia in lista_materias
	}
	logging.info(f'Descargando materias para o ano {ano_b}')
	contidos_B = {
		materia: comparar.descargar_seccions(materia, ano=ano_b, idioma=idioma)
		for materia in lista_materias
	}

	logging.info('Xerando a páxina web')

	with open('www/modelo.html', 'r') as m:
		paxina = BeautifulSoup(m.read(), 'html.parser')

	if idioma == 'cat':
		paxina.html['lang'] = 'gl'
	elif idioma == 'spa':
		paxina.html['lang'] = 'es'
	elif idioma == 'eng':
		paxina.html['lang'] = 'en'
	titulo = paxina.new_tag('title')
	titulo.string = f'{titulacion} de {ano_a} a {ano_b}, {idioma}'
	paxina.html.head.append(titulo)

	for materia in lista_materias:
		logging.info(f'Procesando {materia}')
		# Se non hai seccións modificadas, non se engade a materia
		engadir_materia = False
		texto_materia = BeautifulSoup()
		cabeceira = texto_materia.new_tag('h1', id=materia)
		cabeceira.string = f'{materia}: {nomes[materia]}'
		texto_materia.append(cabeceira)
		for s in range(1, 10):
			# Obtendo datos
			# Se non hai cambios, non se engade a sección
			engadir_seccion = False
			texto_A = comparar.eliminar_ano(comparar.convertir_html_texto(contidos_A[materia][opcions.SECCIONS[s]]), ano_a)
			texto_B = comparar.eliminar_ano(comparar.convertir_html_texto(contidos_B[materia][opcions.SECCIONS[s]]), ano_b)
			delta = comparar.comparar_a_lista(texto_A, texto_B)
			delta_agrupado = comparar.agrupar_comparacion(delta)

			# Xerando DOM para a sección
			# # Táboa
			texto_seccion = paxina.new_tag('table')
			# # Cabeceira
			texto_seccion.append(paxina.new_tag('tr'))
			texto = paxina.new_tag('th')
			texto.string = f'{ano_a}'
			texto_seccion.tr.append(texto)
			texto = paxina.new_tag('th')
			texto.string = f'{ano_b}'
			texto_seccion.tr.append(texto)
			# # Filas
			for grupo in delta_agrupado:
				for i in range(len(grupo[0])):
					if len(grupo[0][i]) == 0 and len(grupo[1][i]) == 0:
						continue
					engadir_materia = True
					engadir_seccion = True
					comparacion = paxina.new_tag('tr')
					# # # Columna antes
					td_A = paxina.new_tag('td')
					if len(grupo[0][i]) > 0:
						td_A.append(color(grupo[0][i]))
					# # # Columna despois
					td_B = paxina.new_tag('td')
					if len(grupo[1][i]) > 0:
						td_B.append(color(grupo[1][i]))
					comparacion.append(td_A)
					comparacion.append(td_B)
					texto_seccion.append(comparacion)
			if engadir_seccion:
				# # Cabeceira
				cabeceira = paxina.new_tag('h2', id=f'{materia}_{opcions.SECCIONS[s]}')
				cabeceira.string = f'{opcions.SECCIONS[s]}'
				texto_materia.append(cabeceira)
				texto_materia.append(texto_seccion)
		if engadir_materia:
			paxina.html.body.append(texto_materia)
	return str(paxina)


if __name__ == '__main__':
	if len(sys.argv) < 5:
		print('./main.py <código titulación> <ano anterior> <ano seguinte> <idioma> [ficheiro de saida]')
		exit(0)
	else:
		cod_titulacion = sys.argv[1]
		ano_a = sys.argv[2]
		ano_b = sys.argv[3]
		idioma = sys.argv[4]
		ficheiro = sys.argv[5] if len(sys.argv) >= 6 else None
		paxina = xerar_paxina_html(cod_titulacion, ano_a, ano_b, idioma)

		if ficheiro is None:
			print(paxina)
		else:
			logging.info('Gardando a páxina web')
			with open(ficheiro, 'w') as f:
				f.write(paxina)
