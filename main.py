import logging
import difflib
import re

import descargar
import opcions
import comparar

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(funcName)s:%(message)s')

logging.info('Descargando listaxe de materias')
lista_materias = descargar.lista_materias(opcions.CODIGO, opcions.ANO_A, opcions.IDIOMA)

logging.info(f'Descargando materias para o ano {opcions.ANO_A}')
contidos_A = {
	materia: comparar.descargar_seccions(materia, ano=opcions.ANO_A, idioma=opcions.IDIOMA)
	for materia in lista_materias
}
logging.info(f'Descargando materias para o ano {opcions.ANO_B}')
contidos_B = {
	materia: comparar.descargar_seccions(materia, ano=opcions.ANO_B, idioma=opcions.IDIOMA)
	for materia in lista_materias
}

differ = difflib.HtmlDiff()

buscar_ano_A = re.compile(f'.*{opcions.ANO_A}.*')
buscar_ano_B = re.compile(f'.*{opcions.ANO_B}.*')

for materia in lista_materias:
	saida = f'		{materia}:\n'
	amosar = False
	for i in range(1, 10):
		texto_A = [line for line in contidos_A[materia][opcions.SECCIONS[i]].splitlines(keepends=True) if buscar_ano_A.search(line) is None]
		texto_B = [line for line in contidos_B[materia][opcions.SECCIONS[i]].splitlines(keepends=True) if buscar_ano_B.search(line) is None]
		delta = differ.make_file(fromlines=texto_A, tolines=texto_B, fromdesc=opcions.ANO_A, todesc=opcions.ANO_B)
		with open(f'../out/{materia}.htm', 'w') as file:
			file.write(delta)
		#cambios = [cambio for cambio in delta if cambio[0] in ('?', '+', '-')]
		#if len(cambios) > 0:
		#	saida += f'{SECCIONS[i]}\n{cambios}'
		#	amosar = True
	if amosar:
		print(saida)
