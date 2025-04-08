from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import sys
import traceback
from dotenv import load_dotenv
import urllib.parse
from sqlalchemy import inspect

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta-12345')
app.config['DEBUG'] = True  # Activar modo debug

# Configuración de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gym.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Mostrar queries SQL

# Inicializar la base de datos
db = SQLAlchemy(app)

# Configurar el sistema de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Manejo de errores
@app.errorhandler(500)
def internal_error(error):
    print(f"Error 500: {error}", file=sys.stderr)
    traceback.print_exc()
    return render_template('error.html', error=str(error)), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Página no encontrada"), 404

# Modelos
usuario_rutina = db.Table('usuario_rutina',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('rutina_id', db.Integer, db.ForeignKey('rutina.id'), primary_key=True)
)

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    nombre = db.Column(db.String(100))
    tipo_usuario = db.Column(db.String(20), nullable=False)
    rutinas = db.relationship('Rutina', secondary=usuario_rutina, backref=db.backref('usuarios', lazy='dynamic'))

class Rutina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', backref=db.backref('rutinas_propias', lazy=True))

class Ejercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    series = db.Column(db.Integer)
    repeticiones = db.Column(db.Integer)
    tiempo_descanso = db.Column(db.Integer)  # en segundos
    nivel_dificultad = db.Column(db.String(20))  # principiante, intermedio, avanzado
    musculos_trabajados = db.Column(db.String(200))
    imagen_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    rutina_id = db.Column(db.Integer, db.ForeignKey('rutina.id'))
    rutina = db.relationship('Rutina', backref=db.backref('ejercicios', lazy=True))
    progresos = db.relationship('ProgresoEjercicio', backref='ejercicio', lazy=True)

class ProgresoEjercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ejercicio_id = db.Column(db.Integer, db.ForeignKey('ejercicio.id'), nullable=False)
    completado = db.Column(db.Boolean, default=False)
    fecha_completado = db.Column(db.DateTime, nullable=True)
    notas = db.Column(db.Text, nullable=True)
    usuario = db.relationship('Usuario', backref=db.backref('progresos', lazy=True))

    __table_args__ = (db.UniqueConstraint('usuario_id', 'ejercicio_id', name='uix_usuario_ejercicio'),)

# Crear las tablas y datos iniciales
def init_db():
    """Inicializa la base de datos y crea usuarios por defecto si no existen"""
    with app.app_context():
        # Verificar si las tablas ya existen
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            # Crear todas las tablas
            db.create_all()
            print("Tablas creadas exitosamente")
            
            # Crear usuarios por defecto solo si la tabla usuario está vacía
            if Usuario.query.count() == 0:
                # Crear usuario administrador
                admin = Usuario(
                    nombre='Administrador',
                    email='admin@example.com',
                    password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                    es_admin=True
                )
                db.session.add(admin)
                
                # Crear usuario normal
                usuario = Usuario(
                    nombre='Usuario Normal',
                    email='usuario@example.com',
                    password=generate_password_hash('usuario123', method='pbkdf2:sha256'),
                    es_admin=False
                )
                db.session.add(usuario)
                
                db.session.commit()
                print("Usuarios por defecto creados exitosamente")
        else:
            print("Las tablas ya existen, omitiendo creación")

# Inicializar la base de datos
init_db()

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            flash('Usuario no encontrado', 'error')
            print("❌ Usuario no encontrado")
            return redirect(url_for('login'))

        if not check_password_hash(usuario.password, password):
            flash('Contraseña incorrecta', 'error')
            print("❌ Contraseña incorrecta")
            return redirect(url_for('login'))

        login_user(usuario)
        flash('Inicio de sesión exitoso', 'success')
        print(f"✅ Usuario {usuario.email} autenticado correctamente")

        if usuario.tipo_usuario == 'entrenador':
            return redirect(url_for('dashboard_admin'))
        return redirect(url_for('dashboard_usuario'))

    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        tipo_usuario = request.form.get('tipo_usuario')

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            flash('El email ya está registrado')
            return redirect(url_for('registro'))

        nuevo_usuario = Usuario(
            email=email,
            nombre=nombre,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            tipo_usuario=tipo_usuario
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('registro.html')


@app.route('/dashboard_usuario')
@login_required
def dashboard_usuario():
    # Obtener todas las rutinas del usuario (tanto asignadas como propias)
    rutinas_asignadas = current_user.rutinas  # Ya es una lista, no necesita .all()
    rutinas_propias = current_user.rutinas_propias  # Esta ya es una lista
    todas_las_rutinas = list(set(rutinas_asignadas + rutinas_propias))  # Eliminar duplicados si los hay
    return render_template('dashboard_usuario.html', rutinas=todas_las_rutinas)

@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    usuarios = Usuario.query.filter_by(tipo_usuario='usuario').all()
    rutinas = Rutina.query.all()
    
    # Obtener el progreso de todos los usuarios
    progreso_usuarios = {}
    estadisticas = {
        'alto_progreso': 0,
        'medio_progreso': 0,
        'bajo_progreso': 0
    }
    
    for usuario in usuarios:
        total_ejercicios = sum(len(rutina.ejercicios) for rutina in usuario.rutinas)
        ejercicios_completados = sum(1 for p in usuario.progresos if p.completado)
        porcentaje_progreso = (ejercicios_completados / total_ejercicios * 100) if total_ejercicios > 0 else 0
        
        # Clasificar el progreso
        if porcentaje_progreso > 75:
            estadisticas['alto_progreso'] += 1
        elif porcentaje_progreso > 25:
            estadisticas['medio_progreso'] += 1
        else:
            estadisticas['bajo_progreso'] += 1
        
        progreso_usuarios[usuario.id] = {
            'progresos': usuario.progresos,
            'total_ejercicios': total_ejercicios,
            'ejercicios_completados': ejercicios_completados
        }
    
    return render_template('dashboard_admin.html', 
                         usuarios=usuarios, 
                         rutinas=rutinas, 
                         progreso_usuarios=progreso_usuarios,
                         estadisticas=estadisticas)

@app.route('/crear_rutina', methods=['GET', 'POST'])
@login_required
def crear_rutina():
    if current_user.tipo_usuario != 'entrenador':
        return redirect(url_for('dashboard_admin'))
        
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        usuario_id = request.form.get('usuario_id')
        
        nueva_rutina = Rutina(
            nombre=nombre,
            descripcion=descripcion,
            usuario_id=usuario_id
        )
        
        db.session.add(nueva_rutina)
        db.session.commit()
        
        # Asignar la rutina al usuario seleccionado
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            usuario.rutinas.append(nueva_rutina)
            db.session.commit()
            flash('Rutina creada y asignada exitosamente', 'success')
            return redirect(url_for('ver_rutina', rutina_id=nueva_rutina.id))
        else:
            flash('Error al asignar la rutina al usuario', 'error')
            return redirect(url_for('dashboard_admin'))
        
    usuarios = Usuario.query.filter_by(tipo_usuario='usuario').all()
    return render_template('crear_rutina.html', usuarios=usuarios)

@app.route('/editar_rutina/<int:rutina_id>', methods=['GET', 'POST'])
@login_required
def editar_rutina(rutina_id):
    rutina = Rutina.query.get_or_404(rutina_id)
    if current_user.tipo_usuario != 'entrenador':
        return redirect(url_for('dashboard_admin'))
    
    if request.method == 'POST':
        rutina.nombre = request.form.get('nombre')
        rutina.descripcion = request.form.get('descripcion')
        db.session.commit()
        return redirect(url_for('dashboard_admin'))
    
    return render_template('editar_rutina.html', rutina=rutina)

@app.route('/eliminar_rutina/<int:rutina_id>', methods=['POST'])
@login_required
def eliminar_rutina(rutina_id):
    rutina = Rutina.query.get_or_404(rutina_id)
    if current_user.tipo_usuario != 'entrenador':
        return redirect(url_for('dashboard_admin'))
    
    db.session.delete(rutina)
    db.session.commit()
    return redirect(url_for('dashboard_admin'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/crear_ejercicio/<int:rutina_id>', methods=['GET', 'POST'])
@login_required
def crear_ejercicio(rutina_id):
    if current_user.tipo_usuario != 'entrenador':
        return redirect(url_for('dashboard_admin'))
    
    rutina = Rutina.query.get_or_404(rutina_id)
    
    if request.method == 'POST':
        nuevo_ejercicio = Ejercicio(
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion'),
            series=int(request.form.get('series')),
            repeticiones=int(request.form.get('repeticiones')),
            tiempo_descanso=int(request.form.get('tiempo_descanso')),
            nivel_dificultad=request.form.get('nivel_dificultad'),
            musculos_trabajados=request.form.get('musculos_trabajados'),
            imagen_url=request.form.get('imagen_url'),
            video_url=request.form.get('video_url'),
            rutina_id=rutina_id
        )
        
        db.session.add(nuevo_ejercicio)
        db.session.commit()
        
        flash('Ejercicio creado exitosamente', 'success')
        return redirect(url_for('ver_rutina', rutina_id=rutina_id))
    
    return render_template('crear_ejercicio.html', rutina=rutina)

@app.route('/editar_ejercicio/<int:ejercicio_id>', methods=['GET', 'POST'])
@login_required
def editar_ejercicio(ejercicio_id):
    if current_user.tipo_usuario != 'entrenador':
        return redirect(url_for('dashboard_admin'))
    
    ejercicio = Ejercicio.query.get_or_404(ejercicio_id)
    
    if request.method == 'POST':
        ejercicio.nombre = request.form.get('nombre')
        ejercicio.descripcion = request.form.get('descripcion')
        ejercicio.series = int(request.form.get('series'))
        ejercicio.repeticiones = int(request.form.get('repeticiones'))
        ejercicio.tiempo_descanso = int(request.form.get('tiempo_descanso'))
        ejercicio.nivel_dificultad = request.form.get('nivel_dificultad')
        ejercicio.musculos_trabajados = request.form.get('musculos_trabajados')
        ejercicio.imagen_url = request.form.get('imagen_url')
        ejercicio.video_url = request.form.get('video_url')
        
        db.session.commit()
        flash('Ejercicio actualizado exitosamente', 'success')
        return redirect(url_for('ver_rutina', rutina_id=ejercicio.rutina_id))
    
    return render_template('editar_ejercicio.html', ejercicio=ejercicio)

@app.route('/eliminar_ejercicio/<int:ejercicio_id>', methods=['POST'])
@login_required
def eliminar_ejercicio(ejercicio_id):
    if current_user.tipo_usuario != 'entrenador':
        return redirect(url_for('dashboard_admin'))
    
    ejercicio = Ejercicio.query.get_or_404(ejercicio_id)
    rutina_id = ejercicio.rutina_id
    
    db.session.delete(ejercicio)
    db.session.commit()
    
    flash('Ejercicio eliminado exitosamente', 'success')
    return redirect(url_for('ver_rutina', rutina_id=rutina_id))

@app.route('/ver_rutina/<int:rutina_id>')
@login_required
def ver_rutina(rutina_id):
    rutina = Rutina.query.get_or_404(rutina_id)
    # Obtener el progreso de los ejercicios para el usuario actual
    progresos = {p.ejercicio_id: p for p in current_user.progresos if p.ejercicio.rutina_id == rutina_id}
    return render_template('ver_rutina.html', rutina=rutina, progresos=progresos)

@app.route('/marcar_ejercicio/<int:ejercicio_id>', methods=['POST'])
@login_required
def marcar_ejercicio(ejercicio_id):
    ejercicio = Ejercicio.query.get_or_404(ejercicio_id)
    completado = request.form.get('completado') == 'true'
    notas = request.form.get('notas', '')

    # Buscar o crear el progreso del ejercicio
    progreso = ProgresoEjercicio.query.filter_by(
        usuario_id=current_user.id,
        ejercicio_id=ejercicio_id
    ).first()

    if not progreso:
        progreso = ProgresoEjercicio(
            usuario_id=current_user.id,
            ejercicio_id=ejercicio_id
        )
        db.session.add(progreso)

    progreso.completado = completado
    progreso.fecha_completado = datetime.now() if completado else None
    progreso.notas = notas

    db.session.commit()

    if completado:
        flash('¡Ejercicio marcado como completado!', 'success')
    else:
        flash('Ejercicio marcado como no completado', 'info')
    
    return redirect(url_for('ver_rutina', rutina_id=ejercicio.rutina_id))

if __name__ == '__main__':
    # Obtener el puerto del entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
