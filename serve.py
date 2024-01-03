#! /usr/bin/env python

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import opcions
import main
import sys
import socket
import ipaddress
import logging
import re
import os
from threading import Lock

descargas_en_proceso = []
mutex = Lock()


def obter_paxina(materia: str, ano_a: str, ano_b: str, idioma: str):
	ficheiro = f'{opcions.SAIDA}/{ano_a}a{ano_a}A{materia}I{idioma}.htm'
	logging.info(f'Devolvendo {ano_a}a{ano_a}A{materia}I{idioma}')
	try:
		with open(ficheiro, 'r') as f:
			return f.read()
	except FileNotFoundError:
		# Mira se xa hai algunha descarga en proceso
		descargar = False
		paxina = None
		with mutex:
			if ficheiro not in descargas_en_proceso:
				descargas_en_proceso.append(ficheiro)
				descargar = True
		if descargar:
			logging.info(f'{ano_a}a{ano_a}A{materia}I{idioma} non existe, descargando')
			paxina = main.xerar_paxina_html(materia, ano_a, ano_b, idioma)
			with open(ficheiro, 'w') as saida:
				saida.write(paxina)
			with mutex:
				descargas_en_proceso.remove(ficheiro)
		else:
			logging.info(
				f'{ano_a}a{ano_a}A{materia}I{idioma} non existe, agardando a descarga')
			while ficheiro in descargas_en_proceso:
				pass
			with open(ficheiro, 'r') as saida:
				paxina = saida.read()
		return paxina


class ServidorHTTP(BaseHTTPRequestHandler):
	def param_peticion(self, path = None):
		if path is None:
			path = self.path
		parte_parametros = path.split('?')[1]
		return {peticion.split('=')[0]: peticion.split('=')[1]
										for peticion in parte_parametros.split('&')}

	def do_GET(self):
		try:
			if re.compile('favicon').search(self.path) is not None:
				logging.info('Enviando icona')
				with open('www/favicon.png', 'rb') as icona:
					self.send_response(200)
					self.send_header('Content-Type', 'image/png')
					self.send_header(
						'Content-Length', str(os.path.getsize('www/favicon.png')))
					self.end_headers()
					self.wfile.write(icona.read())
			else:
				try:
					parametros = self.param_peticion()
					materia = parametros['materia']
					ano_a = parametros['anterior']
					ano_b = parametros['seguinte']
					idioma = parametros['idioma']
					paxina = obter_paxina(materia, ano_a, ano_b, idioma)
					self.send_response(200)
					self.send_header('Content-Type', 'text/html')
					self.end_headers()
					self.wfile.write(str.encode(paxina))
				except (KeyError, IndexError):
					self.send_response(200)
					self.send_header('Content-Type', 'text/html')
					self.end_headers()
					with open(opcions.INDICE, 'r') as index:
						self.wfile.write(str.encode(index.read()))
				except Exception as e:
					self.send_error(500)
					logging.exception(e)
		except BrokenPipeError:
			pass


class ServidorIPv6(ThreadingHTTPServer):
	address_family = socket.AF_INET6


if __name__ == '__main__':
	try:
		ops = (sys.argv[1], int(sys.argv[2]))
		logging.info(f'Executando servidor en {ops[0]}:{ops[1]}')
		httpd = ThreadingHTTPServer(ops, ServidorHTTP) \
			if type(ipaddress.ip_address(ops[0])) != ipaddress.IPv6Address \
			else ServidorIPv6(ops, ServidorHTTP)
		httpd.serve_forever()
	except IndexError:
		print('Uso: ./serve.py [IP] [porto]')
