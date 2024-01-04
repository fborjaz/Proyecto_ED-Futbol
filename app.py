import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
import numpy as np

app = Flask(__name__)

# Define un formulario de registro usando Flask-WTF
class RegistrationForm(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])

def cargar_usuarios():
    try:
        with open('users.json', 'r') as f:
            usuarios = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        usuarios = {"usuarios": []}

    return usuarios

def guardar_usuarios(usuarios):
    with open('users.json', 'w') as f:
        json.dump(usuarios, f)

def cargar_equipos():
    try:
        with open('equipos.json', 'r') as f:
            equipos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        equipos = {"equipos": []}

    return equipos

def guardar_equipos(equipos):
    with open('equipos.json', 'w') as f:
        json.dump(equipos, f)

# Función para calcular estadísticas globales de equipos
def calcular_estadisticas_globales(equipo):
    partidos_ganados = equipo.get("partidos_ganados", 0)
    partidos_empatados = equipo.get("partidos_empatados", 0)
    partidos_perdidos = equipo.get("partidos_perdidos", 0)

    total_partidos = partidos_ganados + partidos_empatados + partidos_perdidos
    puntos_totales = equipo.get("puntos_totales", 0)

    if total_partidos == 0:
        return {
            "porcentaje_partidos_ganados": 0,
            "porcentaje_partidos_empatados": 0,
            "porcentaje_partidos_perdidos": 0,
            "puntos_totales": puntos_totales,
        }

    porcentajes = np.array([partidos_ganados, partidos_empatados, partidos_perdidos]) / total_partidos * 100

    estadisticas = {
        "porcentaje_partidos_ganados": round(porcentajes[0], 2),
        "porcentaje_partidos_empatados": round(porcentajes[1], 2),
        "porcentaje_partidos_perdidos": round(porcentajes[2], 2),
        "puntos_totales": puntos_totales,
    }

    return estadisticas
# Función para calcular estadísticas de jugadores
def calcular_estadisticas_jugadores(jugadores):
    if not jugadores:
        return {
            "goles_por_remate": 0,
            "tarjetas_amarillas_por_rojas": 0,
            "mejor_goleador": None,
            "jugador_mayor_riesgo": None,
        }

    datos = np.array([[jugador.get("goles", 0), jugador.get("remates_al_arco", 0),
                       jugador.get("tarjetas_amarillas", 0), jugador.get("tarjetas_rojas", 0)] for jugador in jugadores])

    sumas_totales = datos.sum(axis=0)

    goles_por_remate = sumas_totales[0] / sumas_totales[1] if sumas_totales[1] > 0 else 0
    tarjetas_amarillas_por_rojas = sumas_totales[2] / sumas_totales[3] if sumas_totales[3] > 0 else 0

    # Encontrar jugador con mayor cantidad de goles
    mejor_goleador_index = np.argmax(datos[:, 0])
    mejor_goleador = jugadores[mejor_goleador_index]["nombre"]

    # Encontrar jugador con mayor riesgo de tarjetas rojas
    jugador_mayor_riesgo_index = np.argmax(datos[:, 3])
    jugador_mayor_riesgo = jugadores[jugador_mayor_riesgo_index]["nombre"]

    return {
        "goles_por_remate": round(goles_por_remate, 2),
        "tarjetas_amarillas_por_rojas": round(tarjetas_amarillas_por_rojas, 2),
        "mejor_goleador": mejor_goleador,
        "jugador_mayor_riesgo": jugador_mayor_riesgo,
    }

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    usuarios = cargar_usuarios()

    for usuario in usuarios["usuarios"]:
        if usuario["email"] == email and usuario["password"] == password:
            return redirect(url_for('principal'))

    return render_template('login.html', mensaje_error="Credenciales incorrectas")

@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm(request.form)

    if form.validate():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        usuarios = cargar_usuarios()

        for usuario in usuarios["usuarios"]:
            if usuario["email"] == email:
                return render_template('login.html', mensaje_error="El usuario ya existe")

        nuevo_usuario = {"nombre": name, "email": email, "password": password}
        usuarios["usuarios"].append(nuevo_usuario)

        guardar_usuarios(usuarios)

        return redirect(url_for('index'))
    else:
        return render_template('login.html', mensaje_error="Datos de registro no válidos")

@app.route('/principal')
def principal():
    equipos = cargar_equipos()
    return render_template('principal.html', equipos=equipos)

@app.route('/ingresar_equipos', methods=['GET', 'POST'])
def ingresar_equipos():
    if request.method == 'POST':
        nombre_equipo = request.form.get('nombre_equipo')
        logo_ruta = request.form.get('logo_ruta')

        if not nombre_equipo or not logo_ruta:
            return render_template('ingresar_equipos.html', mensaje_error="Todos los campos son obligatorios")

        equipos = cargar_equipos()

        if any(equipo["nombre"].lower() == nombre_equipo.lower() for equipo in equipos["equipos"]):
            return render_template('ingresar_equipos.html', mensaje_error="El equipo ya está ingresado")

        nuevo_equipo = {"nombre": nombre_equipo, "logo": logo_ruta, "jugadores": []}

        for i in range(1, 12):
            nombre_jugador = request.form.get(f'nombre_jugador_{i}')
            numero_camiseta = request.form.get(f'numero_camiseta_{i}')
            posicion_jugador = request.form.get(f'posicion_jugador_{i}')

            if not nombre_jugador or not numero_camiseta or not posicion_jugador:
                return render_template('ingresar_equipos.html', mensaje_error=f"Todos los campos del jugador {i} son obligatorios")

            nuevo_jugador = {"nombre": nombre_jugador, "numero_camiseta": numero_camiseta, "posicion": posicion_jugador}
            nuevo_equipo["jugadores"].append(nuevo_jugador)

        equipos["equipos"].append(nuevo_equipo)

        guardar_equipos(equipos)

        return redirect(url_for('principal'))

    return render_template('ingresar_equipos.html')

@app.route('/registrar_datos', methods=['GET', 'POST'])
def registrar_datos():
    equipos = cargar_equipos()
    mensaje_error = None

    if request.method == 'POST':
        nombre_equipo = request.form.get('nombre_equipo')
        partidos_ganados = int(request.form.get('partidos_ganados', '0'))
        partidos_empatados = int(request.form.get('partidos_empatados', '0'))
        partidos_perdidos = int(request.form.get('partidos_perdidos', '0'))
        puntos_totales = int(request.form.get('puntos_totales', '0'))

        equipo_seleccionado = next((equipo for equipo in equipos['equipos'] if equipo['nombre'] == nombre_equipo), None)

        if not equipo_seleccionado:
            mensaje_error = f"Equipo '{nombre_equipo}' no encontrado en el archivo JSON"
            print(mensaje_error)
        else:
            equipo_seleccionado['partidos_ganados'] = partidos_ganados
            equipo_seleccionado['partidos_empatados'] = partidos_empatados
            equipo_seleccionado['partidos_perdidos'] = partidos_perdidos
            equipo_seleccionado['puntos_totales'] = puntos_totales

            jugadores_equipo_seleccionado = equipo_seleccionado['jugadores']

            for jugador in jugadores_equipo_seleccionado:
                goles = request.form.get(f'goles_{jugador["numero_camiseta"]}', '0')
                remates_al_arco = request.form.get(f'remates_al_arco_{jugador["numero_camiseta"]}', '0')
                asistencias = request.form.get(f'asistencias_{jugador["numero_camiseta"]}', '0')
                tarjetas_amarillas = request.form.get(f'tarjetas_amarillas_{jugador["numero_camiseta"]}', '0')
                tarjetas_rojas = request.form.get(f'tarjetas_rojas_{jugador["numero_camiseta"]}', '0')

                if not (goles.isdigit() and remates_al_arco.isdigit() and asistencias.isdigit() and tarjetas_amarillas.isdigit() and tarjetas_rojas.isdigit()):
                    mensaje_error = "Ingrese valores numéricos para los datos de los jugadores"
                    print(mensaje_error)
                    return render_template('registrar_datos.html', equipos=equipos, mensaje_error=mensaje_error)

                jugador['goles'] = int(goles)
                jugador['remates_al_arco'] = int(remates_al_arco)
                jugador['asistencias'] = int(asistencias)
                jugador['tarjetas_amarillas'] = int(tarjetas_amarillas)
                jugador['tarjetas_rojas'] = int(tarjetas_rojas)

            guardar_equipos(equipos)

            return redirect(url_for('principal'))

    return render_template('registrar_datos.html', equipos=equipos, mensaje_error=mensaje_error)

@app.route('/obtener_info_jugadores', methods=['POST'])
def obtener_info_jugadores():
    nombre_equipo = request.json.get('nombre_equipo')

    equipos = cargar_equipos()

    equipo_seleccionado = None
    for equipo in equipos['equipos']:
        if equipo['nombre'] == nombre_equipo:
            equipo_seleccionado = equipo
            break

    if not equipo_seleccionado:
        return jsonify({'error': 'Equipo no encontrado en el archivo JSON'})

    jugadores = equipo_seleccionado['jugadores']
    return jsonify({'jugadores': jugadores})

from flask import send_from_directory  # Agrega esta importación

@app.route('/estadisticas_equipos', methods=['GET', 'POST'])
def estadisticas_equipos():
    equipos_data = cargar_equipos()["equipos"]

    selected_equipo = None
    estadisticas = None
    logo_url = None  # Nueva variable para almacenar la URL del logo

    if request.method == 'POST':
        selected_equipo = request.form.get('equipo')

        equipo_seleccionado = next((equipo for equipo in equipos_data if equipo["nombre"] == selected_equipo), None)

        if equipo_seleccionado:
            estadisticas_globales = calcular_estadisticas_globales(equipo_seleccionado)
            estadisticas_jugadores = calcular_estadisticas_jugadores(equipo_seleccionado['jugadores'])

            estadisticas = {
                **estadisticas_globales,
                **estadisticas_jugadores,
            }

            logo_url = equipo_seleccionado.get("logo")  # Obtén la URL del logo del equipo seleccionado

    return render_template('estadisticas_equipos.html', equipos=equipos_data, selected_equipo=selected_equipo, estadisticas=estadisticas, logo_url=logo_url)

@app.route('/obtener_estadisticas_json', methods=['POST'])
def obtener_estadisticas_json():
    nombre_equipo = request.json.get('nombre_equipo')

    equipos = cargar_equipos()

    equipo_seleccionado = None
    for equipo in equipos['equipos']:
        if equipo['nombre'] == nombre_equipo:
            equipo_seleccionado = equipo
            break

    if not equipo_seleccionado:
        return jsonify({'error': 'Equipo no encontrado en el archivo JSON'})

    estadisticas_globales = calcular_estadisticas_globales(equipo_seleccionado)
    return jsonify(estadisticas_globales)

@app.route('/cerrar_sesion')
def cerrar_sesion():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
