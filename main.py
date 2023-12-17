import logging
import re

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

logging.info('Xerando a páxina web')

paxina = """<!DOCTYPE html><html><head><style>
table, th, td {
	border: 1px solid black;
	border-collapse: collapse;
}

.remove {
	color: red;
}
.add {
	color: green;
}</style></head><body>"""

for materia in lista_materias:
	logging.info(f'Procesando {materia}')
	engadir_materia = False
	texto_materia = f'<h1 id="{materia}">{materia}</h1>'
	for i in range(1, 10):
		engadir_seccion = False
		texto_A = comparar.eliminar_ano(comparar.convertir_html_texto(contidos_A[materia][opcions.SECCIONS[i]]), opcions.ANO_A)
		texto_B = comparar.eliminar_ano(comparar.convertir_html_texto(contidos_B[materia][opcions.SECCIONS[i]]), opcions.ANO_B)
		delta = comparar.comparar_a_lista(texto_A, texto_B)
		texto_seccion = f'<h2 id="{materia}_{opcions.SECCIONS[i]}">{opcions.SECCIONS[i]}</h2><table><tr><th>{opcions.ANO_A}</th><th>{opcions.ANO_B}</th></tr>'
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

logging.info('Gardando a páxina web')

with open(opcions.SAIDA, 'w') as f:
	f.write(paxina)
