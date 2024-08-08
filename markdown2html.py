#!/usr/bin/env python3

import sys
import os
import re
import hashlib

# Verifica si se proporcionaron los argumentos necesarios
if len(sys.argv) < 3:
    sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
    sys.exit(1)

# Asigna los nombres de los archivos a variables
markdown_file = sys.argv[1]
output_file = sys.argv[2]

# Verifica si el archivo Markdown existe
if not os.path.exists(markdown_file):
    sys.stderr.write(f"Missing {markdown_file}\n")
    sys.exit(1)

# Inicializa una lista para almacenar las líneas HTML generadas
html_lines = []

# Variables para manejar listas y párrafos
in_ul_list = False
in_ol_list = False
in_paragraph = False

# Función para reemplazar la sintaxis de negritas, énfasis, MD5 y eliminación de 'c'
def parse_text(text):
    # Reemplaza **texto** con <b>texto</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Reemplaza __texto__ con <em>texto</em>
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)
    # Convierte [[texto]] en su hash MD5
    text = re.sub(r'\[\[(.*?)\]\]', lambda match: hashlib.md5(match.group(1).encode()).hexdigest(), text)
    # Elimina todas las 'c' (insensible a mayúsculas) de ((texto))
    text = re.sub(r'\(\((.*?)\)\)', lambda match: re.sub(r'[cC]', '', match.group(1)), text)
    return text

# Lee el archivo Markdown y procesa las líneas
with open(markdown_file, 'r') as md_file:
    for line in md_file:
        line = line.rstrip()  # Elimina espacios en blanco al final

        # Aplica la función de reemplazo de negritas, énfasis, MD5 y eliminación de 'c'
        line = parse_text(line)

        # Manejo de encabezados
        if line.startswith('#'):
            # Cierra cualquier lista o párrafo abierto
            if in_ul_list:
                html_lines.append("</ul>")
                in_ul_list = False
            if in_ol_list:
                html_lines.append("</ol>")
                in_ol_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False

            heading_level = len(line.split(' ')[0])
            heading_text = line[heading_level:].strip()
            html_lines.append(f"<h{heading_level}>{heading_text}</h{heading_level}>")
        
        # Manejo de listas desordenadas
        elif line.startswith('-'):
            # Cierra la lista ordenada o párrafo si está abierto
            if in_ol_list:
                html_lines.append("</ol>")
                in_ol_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            # Abre una lista desordenada si no está abierta
            if not in_ul_list:
                html_lines.append("<ul>")
                in_ul_list = True
            list_item = line[1:].strip()
            html_lines.append(f"<li>{list_item}</li>")

        # Manejo de listas ordenadas
        elif line.startswith('*'):
            # Cierra la lista desordenada o párrafo si está abierto
            if in_ul_list:
                html_lines.append("</ul>")
                in_ul_list = False
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            # Abre una lista ordenada si no está abierta
            if not in_ol_list:
                html_lines.append("<ol>")
                in_ol_list = True
            list_item = line[1:].strip()
            html_lines.append(f"<li>{list_item}</li>")

        # Manejo de párrafos
        elif line:
            # Cierra cualquier lista abierta
            if in_ul_list:
                html_lines.append("</ul>")
                in_ul_list = False
            if in_ol_list:
                html_lines.append("</ol>")
                in_ol_list = False
            # Abre un párrafo si no está abierto
            if not in_paragraph:
                html_lines.append("<p>")
                in_paragraph = True
            else:
                # Si ya estamos en un párrafo y hay un salto de línea, añadir un <br/>
                html_lines.append("<br/>")
            html_lines.append(line)

        else:
            # Cierra cualquier párrafo abierto si se encuentra una línea en blanco
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False

# Cierra cualquier lista o párrafo abierto al final del archivo
if in_ul_list:
    html_lines.append("</ul>")
if in_ol_list:
    html_lines.append("</ol>")
if in_paragraph:
    html_lines.append("</p>")

# Escribe las líneas HTML en el archivo de salida
with open(output_file, 'w') as out_file:
    out_file.write("\n".join(html_lines))

# Salida exitosa
sys.exit(0)
