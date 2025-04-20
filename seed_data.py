from trainingapp import app, db, Usuario, Rutina, Ejercicio
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_database():
    with app.app_context():
        # Limpiar la base de datos
        db.drop_all()
        db.create_all()

        # Crear usuarios de ejemplo
        usuarios = [
            Usuario(
                email='usuario1@example.com',
                password=generate_password_hash('password123', method='pbkdf2:sha256'),
                nombre='Usuario Ejemplo 1',
                tipo_usuario='usuario',
                peso=70.5
            ),
            Usuario(
                email='usuario2@example.com',
                password=generate_password_hash('password123', method='pbkdf2:sha256'),
                nombre='Usuario Ejemplo 2',
                tipo_usuario='usuario',
                peso=75.2
            ),
            Usuario(
                email='entrenador@example.com',
                password=generate_password_hash('password123', method='pbkdf2:sha256'),
                nombre='Entrenador Ejemplo',
                tipo_usuario='entrenador'
            )
        ]

        for usuario in usuarios:
            db.session.add(usuario)
        db.session.commit()

        # Crear rutinas de ejemplo
        rutinas = [
            Rutina(
                nombre='Rutina de Fuerza',
                descripcion='Rutina enfocada en ganancia de fuerza y masa muscular',
                usuario_id=None  # Sin asignar inicialmente
            ),
            Rutina(
                nombre='Rutina de Hipertrofia',
                descripcion='Rutina enfocada en el crecimiento muscular',
                usuario_id=None  # Sin asignar inicialmente
            ),
            Rutina(
                nombre='Rutina de Resistencia',
                descripcion='Rutina enfocada en mejorar la resistencia y quema de grasa',
                usuario_id=None  # Sin asignar inicialmente
            )
        ]

        for rutina in rutinas:
            db.session.add(rutina)
        db.session.commit()

        # Crear ejercicios de ejemplo
        ejercicios = [
            # Ejercicios para Rutina de Fuerza
            Ejercicio(
                nombre='Press de Banca',
                series=4,
                repeticiones_objetivo=6,
                repeticiones_semanales=24,
                tiempo_descanso=3,
                rir=2,
                musculos_trabajados='Pectorales, Tríceps, Hombros',
                imagen_url='https://example.com/press-banca.jpg',
                video_url='https://youtube.com/watch?v=rT7DgCr-3pg',
                rutina_id=rutinas[0].id
            ),
            Ejercicio(
                nombre='Sentadillas',
                series=4,
                repeticiones_objetivo=6,
                repeticiones_semanales=24,
                tiempo_descanso=3,
                rir=2,
                musculos_trabajados='Cuádriceps, Glúteos, Core',
                imagen_url='https://example.com/sentadillas.jpg',
                video_url='https://youtube.com/watch?v=SW_C1A-rejs',
                rutina_id=rutinas[0].id
            ),
            # Ejercicios para Rutina de Hipertrofia
            Ejercicio(
                nombre='Curl de Bíceps',
                series=3,
                repeticiones_objetivo=12,
                repeticiones_semanales=36,
                tiempo_descanso=1,
                rir=1,
                musculos_trabajados='Bíceps',
                imagen_url='https://example.com/curl-biceps.jpg',
                video_url='https://youtube.com/watch?v=ykJmrZ5v0Oo',
                rutina_id=rutinas[1].id
            ),
            Ejercicio(
                nombre='Extensiones de Tríceps',
                series=3,
                repeticiones_objetivo=12,
                repeticiones_semanales=36,
                tiempo_descanso=1,
                rir=1,
                musculos_trabajados='Tríceps',
                imagen_url='https://example.com/extensiones-triceps.jpg',
                video_url='https://youtube.com/watch?v=2-LAMcpzODU',
                rutina_id=rutinas[1].id
            ),
            # Ejercicios para Rutina de Resistencia
            Ejercicio(
                nombre='Burpees',
                series=3,
                repeticiones_objetivo=15,
                repeticiones_semanales=45,
                tiempo_descanso=1,
                rir=0,
                musculos_trabajados='Full Body, Cardio',
                imagen_url='https://example.com/burpees.jpg',
                video_url='https://youtube.com/watch?v=TU8QYVW0gDU',
                rutina_id=rutinas[2].id
            ),
            Ejercicio(
                nombre='Mountain Climbers',
                series=3,
                repeticiones_objetivo=20,
                repeticiones_semanales=60,
                tiempo_descanso=1,
                rir=0,
                musculos_trabajados='Core, Cardio',
                imagen_url='https://example.com/mountain-climbers.jpg',
                video_url='https://youtube.com/watch?v=nmwgirgXLYM',
                rutina_id=rutinas[2].id
            )
        ]

        for ejercicio in ejercicios:
            db.session.add(ejercicio)
        db.session.commit()

        print("✅ Datos de ejemplo creados exitosamente")
        print("\nUsuarios creados:")
        print("1. usuario1@example.com / password123")
        print("2. usuario2@example.com / password123")
        print("3. entrenador@example.com / password123")
        print("\nSe han creado 3 rutinas con 2 ejercicios cada una.")

if __name__ == '__main__':
    seed_database() 