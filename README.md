# Comparador de Guías Docentes da UDC

Programa para comparar guías docentes de distintos anos

## Instalar

Dependencias:

* html2text (2020.1.16)
* bs4 (probado con 4.12.2/bs4==0.0.1)
* requests (2.31.0)

## Uso

* **Código materia**: Código do estilo (Centro, 3 números)G(Materia, 2 números), por exemplo 614G01
* **Anos**: 20AA_BB, para o curso 20AA-20BB
* **Idioma**:
	* eng: Inglés
	* spa: Castelán
	* cat: Galego

O ficheiro opcions.py contén un par de rutas que pode que se queiran modificar, CACHE e SAIDA para o servidor.

### Cliente

`./main.py <código materia> <ano anterior> <ano seguinte> <idioma> [ficheiro de saida]`

O ficheiro de saída estará en formato HTML. Se non se engade un ficheiro imprimirase o HTML pola terminal. Precisan de ter creada o cartafol `cache`.

### Servidor

`./serve.py [ip]:[porto]`

Precisan de ter creados os cartafoles `cache` e `out`.
