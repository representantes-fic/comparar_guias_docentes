#! /usr/bin/env python

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import opcions
import main
from descargar import DescargaFallou

import sys
import socket
import ipaddress
import logging
import re
import os
from threading import Lock, Event

descargas_en_proceso = {}
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
			try:
				evento = descargas_en_proceso[ficheiro]
			except KeyError:
				descargas_en_proceso[ficheiro] = Event()
				descargar = True
		if descargar:
			logging.info(f'{ano_a}a{ano_a}A{materia}I{idioma} non existe, descargando')
			try:
				paxina = main.xerar_paxina_html(materia, ano_a, ano_b, idioma)
			except DescargaFallou as e:
				logging.warn(f'A páxina devolveu {e.valor}')
				with mutex:
					descargas_en_proceso[ficheiro].set()
				raise e
			with open(ficheiro, 'w') as saida:
				saida.write(paxina)
			with mutex:
				descargas_en_proceso[ficheiro].set()
				del descargas_en_proceso[ficheiro]
		else:
			logging.info(f'{ano_a}a{ano_a}A{materia}I{idioma} non existe, agardando a descarga')
			evento.wait()
			try:
				with open(ficheiro, 'r') as saida:
					paxina = saida.read()
			except FileNotFoundError:
				raise DescargaFallou(404)
		return paxina


class ServidorHTTP(BaseHTTPRequestHandler):
	def param_peticion(self, path = None):
		if path is None:
			path = self.path
		parte_parametros = path.split('?')[1]
		return {peticion.split('=')[0]: peticion.split('=')[1]
										for peticion in parte_parametros.split('&')}

	def do_GET(self):
		logging.info(f'Request from {self.client_address}')
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
					try:
						paxina = obter_paxina(materia, ano_a, ano_b, idioma)
						self.send_response(200)
						self.send_header('Content-Type', 'text/html')
						self.end_headers()
						self.wfile.write(str.encode(paxina))
					except DescargaFallou as e:
						if e.valor == 302 or e.valor == 404:
							self.send_response(404)
							self.send_header('Content-Type', 'text/html')
							self.end_headers()
							with open('www/notfound.html', 'rb') as f:
								self.wfile.write(f.read())
						else:
							raise Exception('A descarga fallou')
					except Exception as e:
						raise e

				except (KeyError, IndexError):
					self.send_response(200)
					self.send_header('Content-Type', 'text/html')
					self.end_headers()
					with open(opcions.INDICE, 'rb') as index:
						self.wfile.write(index.read())
				except BrokenPipeError as e:
					raise e
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
	except KeyboardInterrupt:
		logging.warning('Saindo...')
