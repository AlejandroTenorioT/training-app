from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['DEBUG'] = True  # Activar modo debug
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///gym.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Mostrar queries SQL

# Inicializar la base de datos
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    peso = db.Column(db.Float, nullable=True)  # Peso del usuario en kg
    rutinas = db.relationship('Rutina', secondary=usuario_rutina, backref=db.backref('usuarios', lazy='dynamic'))

class Rutina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    creador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    creador = db.relationship('Usuario', backref=db.backref('rutinas_creadas', lazy=True), foreign_keys=[creador_id])
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activa = db.Column(db.Boolean, default=True)
    usuarios_asignados = db.relationship('Usuario', secondary=usuario_rutina, backref=db.backref('rutinas_asignadas', lazy='dynamic'))

class Ejercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    series = db.Column(db.Integer)
    repeticiones_objetivo = db.Column(db.Integer)  # Repeticiones objetivo por serie
    repeticiones_semanales = db.Column(db.Integer)  # Total de repeticiones por semana
    tiempo_descanso = db.Column(db.Integer)  # en minutos
    rir = db.Column(db.Integer)  # Reps In Reserve (0 = fallo, 1 = 1 rep en reserva, etc.)
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
    repeticiones_realizadas = db.Column(db.Integer, nullable=True)  # Repeticiones que el usuario logró realizar
    notas = db.Column(db.Text, nullable=True)
    usuario = db.relationship('Usuario', backref=db.backref('progresos', lazy=True))

    __table_args__ = (db.UniqueConstraint('usuario_id', 'ejercicio_id', name='uix_usuario_ejercicio'),)

class RepeticionMaxima(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ejercicio_id = db.Column(db.Integer, db.ForeignKey('ejercicio.id'), nullable=False)
    peso = db.Column(db.Float, nullable=False)  # Peso en kg
    repeticiones = db.Column(db.Integer, nullable=False)  # Número de repeticiones realizadas
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario = db.relationship('Usuario', backref=db.backref('rms', lazy=True))
    ejercicio = db.relationship('Ejercicio', backref=db.backref('rms', lazy=True))

    __table_args__ = (db.UniqueConstraint('usuario_id', 'ejercicio_id', name='uix_usuario_ejercicio_rm'),)

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
                    tipo_usuario='admin'
                )
                db.session.add(admin)
                
                # Crear usuario normal
                usuario = Usuario(
                    nombre='Usuario Normal',
                    email='usuario@example.com',
                    password=generate_password_hash('usuario123', method='pbkdf2:sha256'),
                    tipo_usuario='usuario'
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
        
        if not usuario or not check_password_hash(usuario.password, password):
            flash('Email o contraseña incorrectos', 'error')
            return redirect(url_for('login'))
        
        login_user(usuario)
        flash('Inicio de sesión exitoso', 'success')
        
        if usuario.tipo_usuario in ['admin', 'entrenador']:
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
    # Obtener todas las rutinas asignadas al usuario
    rutinas_asignadas = current_user.rutinas_asignadas.all()
    return render_template('dashboard_usuario.html', rutinas=rutinas_asignadas)

@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('dashboard_usuario'))
    
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
        # Obtener todas las rutinas asignadas al usuario
        rutinas_usuario = usuario.rutinas_asignadas.all()
        
        # Calcular el total de ejercicios en todas las rutinas asignadas
        total_ejercicios = sum(len(rutina.ejercicios) for rutina in rutinas_usuario)
        
        # Contar ejercicios completados
        ejercicios_completados = sum(1 for p in usuario.progresos if p.completado)
        
        # Calcular porcentaje de progreso
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
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para crear rutinas', 'error')
        return redirect(url_for('dashboard_usuario'))
        
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        nueva_rutina = Rutina(
            nombre=nombre,
            descripcion=descripcion,
            creador_id=current_user.id
        )
        
        db.session.add(nueva_rutina)
        db.session.commit()
        
        flash('Rutina creada exitosamente', 'success')
        return redirect(url_for('gestionar_rutinas'))
        
    return render_template('crear_rutina.html')

@app.route('/editar_rutina/<int:rutina_id>', methods=['GET', 'POST'])
@login_required
def editar_rutina(rutina_id):
    rutina = Rutina.query.get_or_404(rutina_id)
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para editar rutinas', 'error')
        return redirect(url_for('dashboard_usuario'))
    
    if request.method == 'POST':
        rutina.nombre = request.form.get('nombre')
        rutina.descripcion = request.form.get('descripcion')
        db.session.commit()
        flash('Rutina actualizada exitosamente', 'success')
        return redirect(url_for('gestionar_rutinas'))
    
    return render_template('editar_rutina.html', rutina=rutina)

@app.route('/eliminar_rutina/<int:rutina_id>', methods=['POST'])
@login_required
def eliminar_rutina(rutina_id):
    rutina = Rutina.query.get_or_404(rutina_id)
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para eliminar rutinas', 'error')
        return redirect(url_for('dashboard_usuario'))
    
    db.session.delete(rutina)
    db.session.commit()
    flash('Rutina eliminada exitosamente', 'success')
    return redirect(url_for('gestionar_rutinas'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/crear_ejercicio/<int:rutina_id>', methods=['GET', 'POST'])
@login_required
def crear_ejercicio(rutina_id):
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para crear ejercicios', 'error')
        return redirect(url_for('dashboard_usuario'))
    
    rutina = Rutina.query.get_or_404(rutina_id)
    
    if request.method == 'POST':
        nuevo_ejercicio = Ejercicio(
            nombre=request.form.get('nombre'),
            series=int(request.form.get('series')),
            repeticiones_objetivo=int(request.form.get('repeticiones_objetivo')),
            repeticiones_semanales=int(request.form.get('repeticiones_semanales')),
            tiempo_descanso=int(request.form.get('tiempo_descanso')),
            rir=int(request.form.get('rir')),
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
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para editar ejercicios', 'error')
        return redirect(url_for('dashboard_usuario'))
    
    ejercicio = Ejercicio.query.get_or_404(ejercicio_id)
    
    if request.method == 'POST':
        ejercicio.nombre = request.form.get('nombre')
        ejercicio.series = int(request.form.get('series'))
        ejercicio.repeticiones_objetivo = int(request.form.get('repeticiones_objetivo'))
        ejercicio.repeticiones_semanales = int(request.form.get('repeticiones_semanales'))
        ejercicio.tiempo_descanso = int(request.form.get('tiempo_descanso'))
        ejercicio.rir = int(request.form.get('rir'))
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
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para eliminar ejercicios', 'error')
        return redirect(url_for('dashboard_usuario'))
    
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

    # Actualizar el progreso
    progreso.repeticiones_realizadas = request.form.get('repeticiones_realizadas', type=int)
    progreso.notas = request.form.get('notas', '')
    progreso.completado = True  # El ejercicio se marca como completado automáticamente
    progreso.fecha_completado = datetime.utcnow()

    db.session.commit()
    flash('Progreso guardado correctamente', 'success')
    return redirect(url_for('ver_rutina', rutina_id=ejercicio.rutina_id))

@app.route('/registrar_rm/<int:ejercicio_id>', methods=['GET', 'POST'])
@login_required
def registrar_rm(ejercicio_id):
    ejercicio = Ejercicio.query.get_or_404(ejercicio_id)
    
    if request.method == 'POST':
        peso = float(request.form.get('peso'))
        repeticiones = int(request.form.get('repeticiones'))
        
        # Crear nuevo registro de RM
        nuevo_rm = RepeticionMaxima(
            usuario_id=current_user.id,
            ejercicio_id=ejercicio_id,
            peso=peso,
            repeticiones=repeticiones
        )
        
        db.session.add(nuevo_rm)
        db.session.commit()
        
        flash('RM registrado exitosamente', 'success')
        return redirect(url_for('ver_rutina', rutina_id=ejercicio.rutina_id))
    
    return render_template('registrar_rm.html', ejercicio=ejercicio)

@app.route('/gestionar_rutinas')
@login_required
def gestionar_rutinas():
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('dashboard_usuario'))
    
    rutinas = Rutina.query.all()
    return render_template('gestionar_rutinas.html', rutinas=rutinas)

@app.route('/asignar_rutina/<int:rutina_id>', methods=['GET', 'POST'])
@login_required
def asignar_rutina(rutina_id):
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('dashboard_usuario'))
    
    rutina = Rutina.query.get_or_404(rutina_id)
    usuarios = Usuario.query.filter_by(tipo_usuario='usuario').all()
    
    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        usuario = Usuario.query.get_or_404(usuario_id)
        
        if usuario not in rutina.usuarios_asignados:
            rutina.usuarios_asignados.append(usuario)
            db.session.commit()
            flash(f'Rutina asignada correctamente a {usuario.nombre}', 'success')
        else:
            flash('El usuario ya tiene asignada esta rutina', 'warning')
        
        return redirect(url_for('gestionar_rutinas'))
    
    return render_template('asignar_rutina.html', rutina=rutina, usuarios=usuarios)

@app.route('/desasignar_rutina/<int:rutina_id>/<int:usuario_id>', methods=['POST'])
@login_required
def desasignar_rutina(rutina_id, usuario_id):
    if current_user.tipo_usuario not in ['admin', 'entrenador']:
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('dashboard_usuario'))
    
    rutina = Rutina.query.get_or_404(rutina_id)
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario in rutina.usuarios_asignados:
        rutina.usuarios_asignados.remove(usuario)
        db.session.commit()
        flash(f'Rutina desasignada correctamente de {usuario.nombre}', 'success')
    else:
        flash('El usuario no tiene asignada esta rutina', 'warning')
    
    return redirect(url_for('gestionar_rutinas'))

@app.route('/ver_perfil/<int:usuario_id>')
@login_required
def ver_perfil(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template('ver_perfil.html', usuario=usuario)

if __name__ == '__main__':
    # Obtener el puerto del entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
