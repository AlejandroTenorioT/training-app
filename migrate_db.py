from trainingapp import db, app, Ejercicio, Usuario, ProgresoEjercicio
import sqlite3
import os

def migrate_database():
    """Migra la base de datos para adaptarla a los nuevos modelos"""
    print("Iniciando migración de la base de datos...")
    
    # Obtener la ruta de la base de datos
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'gym.db')
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna peso existe en la tabla usuario
        cursor.execute("PRAGMA table_info(usuario)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'peso' not in columns:
            print("Agregando columna 'peso' a la tabla 'usuario'...")
            cursor.execute("ALTER TABLE usuario ADD COLUMN peso FLOAT")
        
        # Verificar si las nuevas columnas existen en la tabla ejercicio
        cursor.execute("PRAGMA table_info(ejercicio)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Crear una nueva tabla ejercicio con la estructura deseada
        print("Creando nueva tabla ejercicio con la estructura actualizada...")
        cursor.execute("""
        CREATE TABLE ejercicio_new (
            id INTEGER PRIMARY KEY,
            nombre VARCHAR(100),
            series INTEGER,
            repeticiones_objetivo INTEGER,
            repeticiones_semanales INTEGER,
            tiempo_descanso INTEGER,
            rir INTEGER,
            musculos_trabajados VARCHAR(200),
            imagen_url VARCHAR(500),
            video_url VARCHAR(500),
            rutina_id INTEGER,
            FOREIGN KEY(rutina_id) REFERENCES rutina(id)
        )
        """)
        
        # Copiar los datos de la tabla antigua a la nueva
        print("Migrando datos a la nueva estructura...")
        cursor.execute("""
        INSERT INTO ejercicio_new (
            id, nombre, series, repeticiones_objetivo, repeticiones_semanales,
            tiempo_descanso, rir, musculos_trabajados, imagen_url, video_url, rutina_id
        )
        SELECT 
            id, nombre, series, 
            COALESCE(repeticiones_objetivo, repeticiones) as repeticiones_objetivo,
            COALESCE(repeticiones_semanales, series * repeticiones) as repeticiones_semanales,
            CAST(tiempo_descanso / 60.0 AS INTEGER) as tiempo_descanso,
            COALESCE(rir, 0) as rir,
            musculos_trabajados, imagen_url, video_url, rutina_id
        FROM ejercicio
        """)
        
        # Eliminar la tabla antigua y renombrar la nueva
        print("Reemplazando tabla antigua con la nueva estructura...")
        cursor.execute("DROP TABLE ejercicio")
        cursor.execute("ALTER TABLE ejercicio_new RENAME TO ejercicio")
        
        # Verificar si la columna repeticiones_realizadas existe en la tabla progreso_ejercicio
        cursor.execute("PRAGMA table_info(progreso_ejercicio)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'repeticiones_realizadas' not in columns:
            print("Agregando columna 'repeticiones_realizadas' a la tabla 'progreso_ejercicio'...")
            cursor.execute("ALTER TABLE progreso_ejercicio ADD COLUMN repeticiones_realizadas INTEGER")
        
        # Guardar los cambios
        conn.commit()
        print("Migración completada con éxito.")
        
    except Exception as e:
        print(f"Error durante la migración: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    with app.app_context():
        migrate_database() 