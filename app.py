from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
now = datetime.now()
now.strftime('%m/%d/%Y')

# initializations
app = Flask(__name__)

# Mysql conexion
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'admcashdb'
mysql = MySQL(app)
# configuracion
app.secret_key = "hola"
# routes
@app.route('/', methods=['GET', 'POST'])
def login():
    
        
    if request.method == 'POST' and 'email' in request.form and 'passwd' in request.form:
        email = request.form['email']
        passwd = request.form['passwd']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE email = %s AND passwd = %s', (email, passwd))
       
        account = cursor.fetchone()
      
        if account:
          
            session['loggedin'] = True
            session['id_usuario'] = account['id_usuario']
            session['nombre'] = account['nombre']
            session['email'] = account['email']
            session['passwd'] = account['passwd']
            
            return redirect(url_for('gastos'))
        else:
            
              flash('Datos incorrectos')
    #return redirect(url_for('home'))
    return render_template("index.html")

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('nombre', None)
   session.pop('passwd', None)
   return redirect(url_for('login'))
@app.route('/gastoForm')
def gastoForm():
    print('Formulario de registro')
    return render_template('gastoForm.html')
@app.route('/add_gasto', methods=['POST'])
def add_gasto():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios')
        id_usuario=session['id_usuario']
        data = cur.fetchall()
        
        if request.method == 'POST':
            print(id_usuario)
            producto = request.form['nombre']
            print(producto)
            costo = request.form['costo']
            categoria = request.form['categoria']
            
            print(now)
            cur.execute("INSERT INTO gasto (id_usuario,nombre,costo,categoria,fecha) VALUES (%s,%s,%s,%s,%s)", [id_usuario,producto,costo,categoria,now] )
            mysql.connection.commit()
            flash('Agregado correctamente')
        return render_template('gastoForm.html')

@app.route('/registro')
def registro():
    print('Formulario de registro')
    return render_template('registro.html')

@app.route('/CrearUsuario' ,methods = ['GET','POST'])
def CrearUsuario():
    if request.method == 'POST' and 'nombre' in request.form and 'email' in request.form and 'passwd' in request.form and 'genero' in request.form:
        nombre = request.form['nombre']
        email = request.form['email']
        passwd = request.form['passwd']
        genero = request.form['genero']
        cur = mysql.connection.cursor()
        cur.execute( "SELECT * FROM usuarios WHERE email LIKE %s", [email] )
        account = cur.fetchone()
        if account:
            flash('Correo en uso')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Correo invalido')
        elif not re.match(r'[A-Za]+', nombre):
            flash('El nombre con solo letras')
        elif not nombre or not email or not passwd or not genero:
             flash('Completa los datos')
        else:
            cur.execute("INSERT INTO usuarios (nombre, email, passwd,genero) VALUES (%s,%s,%s,%s)", [nombre,email,passwd,genero] )
            mysql.connection.commit()
            flash('Se ha registro con exito')
    return render_template('registro.html')

@app.route('/gastos')
def gastos():
    # Check if user is loggedin
    
    if 'loggedin' in session:
        # User is loggedin show them the home page
        
        cur = mysql.connection.cursor()
        id_usuario=session['id_usuario']
        cur.execute("""select * from gasto where id_usuario = %s """, (id_usuario,))        
        data = cur.fetchall()
        cur.close()
        return render_template('gastos.html', gastos = data, username=session['nombre'])

@app.route('/edit/<id_gasto>', methods = ['POST', 'GET'])
def get_gasto(id_gasto):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM gasto WHERE id_gasto = %s', (id_gasto))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit-gasto.html', gasto = data[0])

@app.route('/actualizar/<id_gasto>', methods=['POST'])
def update_gasto(id_gasto):
    if request.method == 'POST':
        producto = request.form['producto']
        costo = request.form['costo']
        categoria = request.form['categoria']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE gasto
            SET nombre = %s,
                costo = %s,
                categoria = %s
            WHERE id_gasto = %s
        """, (producto,costo,categoria,id_gasto))
        flash('Actualizado correctamente')
        mysql.connection.commit()
        return redirect(url_for('gastos'))

@app.route('/delete/<string:id_gasto>', methods = ['POST','GET'])
def delete_gasto(id_gasto):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM gasto WHERE id_gasto = {0}'.format(id_gasto))
    mysql.connection.commit()
    flash('Eliminado correctamente')
    return redirect(url_for('gastos'))

@app.route('/menor_costo')
def menor_costo():
    # Check if user is loggedin
    
    if 'loggedin' in session:
        # User is loggedin show them the home page
        
        cur = mysql.connection.cursor()
        id_usuario=session['id_usuario']
        cur.execute("""select * from gasto where id_usuario = %s ORDER BY costo ASC;""", (id_usuario,))        
        data = cur.fetchall()
        cur.close()
        return render_template('gastos.html', gastos = data, username=session['nombre'])
@app.route('/mayor_costo')
def mayor_costo():
    # Check if user is loggedin
    
    if 'loggedin' in session:
        # User is loggedin show them the home page
        
        cur = mysql.connection.cursor()
        id_usuario=session['id_usuario']
        cur.execute("""select * from gasto where id_usuario = %s ORDER BY costo DESC;""", (id_usuario,))        
        data = cur.fetchall()
        cur.close()
        return render_template('gastos.html', gastos = data, username=session['nombre'])
@app.route('/mas_reciente')
def mas_reciente():
    # Check if user is loggedin
    
    if 'loggedin' in session:
        # User is loggedin show them the home page
        
        cur = mysql.connection.cursor()
        id_usuario=session['id_usuario']
        cur.execute("""select * from gasto where id_usuario = %s ORDER BY fecha ASC;""", (id_usuario,))        
        data = cur.fetchall()
        cur.close()
        return render_template('gastos.html', gastos = data, username=session['nombre'])

# Iniciar aplicacion
if __name__ == "__main__":
    app.run(port=80, debug=True)