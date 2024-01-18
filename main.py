#! /usr/bin/env python

import logging
import re
import sys

import descargar
import opcions
import comparar


def color(linea: str) -> str:
	if len(linea) <= 0 or linea[0] not in ('-', '+'):
		return linea
	saida = '<span '
	if linea[0] == '-':
		saida += 'class="remove">'
	elif linea[0] == '+':
		saida += 'class="add">'
	else:
		saida += '>'
	nova_linea = re.sub(r'\\(.)', r'\1', linea[1:])
	saida += f'{nova_linea}</span>'
	return saida


def xerar_paxina_html(codigo: str, ano_a: str, ano_b: str, idioma: str):
	logging.info('Descargando listaxe de materias')
	lista_materias, nomes = descargar.lista_materias(codigo, ano_a, idioma)

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

	paxina = """
<!DOCTYPE html>
<html>
	<head>
		<style>
			table, th, td {
				border: 1px solid black;
				border-collapse: collapse;
			}

			.remove {
				color: red;
			}
			.add {
				color: green;
			}
		</style>
		<meta charset="utf-8">
		<link rel="icon" href="favicon.png" type="image/png">
	</head>
	<body>"""

	for materia in lista_materias:
		logging.info(f'Procesando {materia}')
		engadir_materia = False
		texto_materia = f'<h1 id="{materia}">{materia}: {nomes[materia]}</h1>'
		for i in range(1, 10):
			engadir_seccion = False
			texto_A = comparar.eliminar_ano(comparar.convertir_html_texto(contidos_A[materia][opcions.SECCIONS[i]]), ano_a)
			texto_B = comparar.eliminar_ano(comparar.convertir_html_texto(contidos_B[materia][opcions.SECCIONS[i]]), ano_b)
			delta = comparar.comparar_a_lista(texto_A, texto_B)
			texto_seccion = f'<h2 id="{materia}_{opcions.SECCIONS[i]}">{opcions.SECCIONS[i]}</h2><table><tr><th>{ano_a}</th><th>{ano_b}</th></tr>'
			delta_agrupado = comparar.agrupar_comparacion(delta)
			for grupo in delta_agrupado:
				for i in range(len(grupo[0])):
					engadir_materia = True
					engadir_seccion = True
					texto_seccion += f'<tr><td>{color(grupo[0][i])}</td><td>{color(grupo[1][i])}</td></tr>'
			texto_seccion += '</table>'
			if engadir_seccion:
				texto_materia += texto_seccion
		if engadir_materia:
			paxina += f'{texto_materia}'
	paxina += '</body></html>'
	return paxina


if __name__ == '__main__':
	if len(sys.argv) < 5:
		print('./main.py <código materia> <ano anterior> <ano seguinte> <idioma> [ficheiro de saida]')
		exit(0)
	else:
		cod_materia = sys.argv[1]
		ano_a = sys.argv[2]
		ano_b = sys.argv[3]
		idioma = sys.argv[4]
		ficheiro = sys.argv[5] if len(sys.argv) >= 6 else None
		paxina = xerar_paxina_html(cod_materia, ano_a, ano_b, idioma)

		if ficheiro is None:
			print(paxina)
		else:
			logging.info('Gardando a páxina web')
			with open(ficheiro, 'w') as f:
				f.write(paxina)
