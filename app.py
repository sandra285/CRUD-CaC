from flask import Flask # Importamos el Framework
from flask import render_template, request, redirect, send_from_directory, url_for, flash # Permite mostrar los templates (index, para crear datos, para editar datos...)
from flaskext.mysql import MySQL # Para conectarnos con la base de datos
from datetime import datetime
import os # Módulo para modificar los archivos del sistema operativo (lo necesitamos para poder editar la foto de un empleado)
app = Flask(__name__) # Creamos un objeto de la clase Flask
app.secret_key="Codoacodo"

# Conexión a la base de datos
mysql = MySQL() # Creamos un objeto que es instancia de la clase MySQL, que importamos arriba
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
# app.config['MYSQL_DATABASE_PORT'] = 3307 # En caso de haber cambiado el puerto
app.config['MYSQL_DATABASE_BD'] = 'sistema22517'
mysql.init_app(app) # Iniciamos la conexión con la base de datos

CARPETA = os.path.join('uploads') # os.path.join es un método que va a unir uno o más componentes de ruta (carpetas)
app.config['CARPETA'] = CARPETA

# Generamos el primer ruteo al index.html
@app.route('/')
def index():
    sql = "SELECT * FROM `sistema22517`.`empleados`;" # Para establecer la conexión con la base de datos
    conn = mysql.connect()
    cursor = conn.cursor() # Se usa para el procesamiento de forma individual de las filas que va a devolver el sistema de gestión de bases de datos cuando hagamos una consulta
    cursor.execute(sql) # Ejecutamos la sentencia sql, que definamos arriba
    empleados = cursor.fetchall() # fetchall() recupera todas las filas del resultado de la consulta (definida en sql)
    # print(empleados)
    conn.commit() # Para que los datos se vean reflejados en la base de datos
    return render_template('empleados/index.html', empleados = empleados) # Va a retornar la plantilla index.html. En el segundo argumento declaramos una variable empleados que va a guardar las tuplas q se obtienen con fetchall()

@app.route('/create')
def create():
    return render_template('empleados/create.html')

# Para almacenar la información que viene del formulario en la base de datos
@app.route('/store', methods=['POST'])
def storage(): 
    # Traemos los datos del formulario
    nombre = request.form['txtNombre']
    correo = request.form['txtCorreo']
    foto = request.files['txtFoto']

    if nombre == '' or correo == '' or foto.filename == '':
        flash('Recuerde completar los datos de los campos')
        return redirect(url_for('create'))

    now = datetime.now() # Obtiene la fecha y hora actual
    tiempo = now.strftime("%Y%H%M%S") # Convertimos a string

    if foto.filename != '': # Comprobamos que la persona haya cargado una foto
        nuevoNombreFoto = tiempo + foto.filename # Le damos un nuevo nombre a la foto
        foto.save("uploads/" + nuevoNombreFoto)  # Guardamos la foto. Foto, como objeto, tiene un método save(), que tiene como parámetro la ruta donde vamos a guardarla

    sql = "INSERT INTO `sistema22517`.`empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);" # Con %s reemplazamos los valores fijos por los valores guardados en datos
    datos = (nombre, correo, nuevoNombreFoto)
    conn = mysql.connect()
    cursor = conn.cursor() 
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/') # Para volver al lugar donde estábamos (en este caso, index)

# Para eliminar un empleado
@app.route('/destroy/<int:id>') 
def destroy(id):
    sql = "DELETE FROM `sistema22517`.`empleados` WHERE id=%s"
    conn = mysql.connect()
    cursor = conn.cursor()

    # Para eliminar la foto
    cursor.execute("SELECT foto FROM `sistema22517`.`empleados` WHERE id=%s", id) # Hacemos la consulta
    fila = cursor.fetchall() # Traemos los datos de una foto con fetchall y los guardamos en la variable fila
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) # Con os.remove eliminamos la foto. Le pasamos la carpeta y el nombre del archivo
    
    cursor.execute(sql, id)
    # Ejecuta la sentencia sql y donde dice %s lo reemplaza por el id q recibe como argumento
    conn.commit()
    return redirect('/')

# Para editar un empleado
@app.route('/edit/<int:id>')
def edit(id):
    sql = "SELECT * FROM `sistema22517`.`empleados` WHERE id=%s"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, id)
    empleados = cursor.fetchall() # Acá podríamos poner fetchone(), ya que vamos a editar de un empleado a la vez
    conn.commit()
    return render_template('empleados/edit.html', empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    nombre = request.form['txtNombre']
    correo = request.form['txtCorreo']
    foto = request.files['txtFoto']
    id = request.form['txtID']

    sql = "UPDATE `sistema22517`.`empleados` SET `nombre`=%s, `correo`=%s WHERE id=%s;"
    datos = (nombre, correo, id)

    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now() # Obtiene la fecha y hora actual
    tiempo = now.strftime("%Y%H%M%S") # Convertimos a string

    if foto.filename != '': # Comprobamos que la persona haya cargado una foto
        nuevoNombreFoto = tiempo + foto.filename # Le damos un nuevo nombre a la foto
        foto.save("uploads/" + nuevoNombreFoto)  # Guardamos la foto. Foto, como objeto, tiene un método save(), que tiene como parámetro la ruta donde vamos a guardarla

        cursor.execute("SELECT foto FROM `sistema22517`.`empleados` WHERE id=%s", id) # Hacemos la consulta
        fila = cursor.fetchall() # Traemos los datos de una foto con fetchall y los guardamos en la variable fila
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) # Con os.remove eliminamos la foto. Le pasamos la carpeta y el nombre del archivo

        # Actualizamos la foto en la base de datos
        cursor.execute("UPDATE `sistema22517`.`empleados` SET foto=%s WHERE id=%s;", (nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql, datos)
    conn.commit()

    return redirect('/')

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

# Líneas que requiere Python para empezar a trabajar con la aplicación
if __name__ == '__main__':
    app.run(debug=True)  # Corremos la aplicación con el depurador