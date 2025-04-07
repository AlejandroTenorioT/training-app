# Training App - Aplicación de Gestión de Rutinas de Ejercicios

Una aplicación web para gestionar rutinas de ejercicios, permitiendo a los entrenadores crear y asignar rutinas a usuarios, y a los usuarios realizar un seguimiento de su progreso.

## Características

- Sistema de autenticación para usuarios y entrenadores
- Creación y gestión de rutinas de ejercicios
- Asignación de rutinas a usuarios
- Seguimiento del progreso de los usuarios
- Interfaz intuitiva y responsiva
- Gráficos de progreso y estadísticas

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona el repositorio:
   ```
   git clone https://github.com/tu-usuario/training-app.git
   cd training-app
   ```

2. Crea un entorno virtual e actívalo:
   ```
   python -m venv venv
   # En Windows
   venv\Scripts\activate
   # En macOS/Linux
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Inicializa la base de datos:
   ```
   python
   >>> from trainingapp import db
   >>> db.create_all()
   >>> exit()
   ```

## Ejecución

1. Asegúrate de que el entorno virtual está activado.

2. Ejecuta la aplicación:
   ```
   python trainingapp.py
   ```

3. Abre tu navegador y visita `http://localhost:5000`

## Estructura del Proyecto

```
training-app/
├── trainingapp.py       # Aplicación principal
├── static/              # Archivos estáticos (CSS, JS)
│   └── styles.css       # Estilos CSS
├── templates/           # Plantillas HTML
│   ├── index.html       # Página principal
│   ├── login.html       # Página de inicio de sesión
│   ├── registro.html    # Página de registro
│   ├── dashboard_admin.html  # Panel de administración
│   ├── dashboard_usuario.html  # Panel de usuario
│   ├── crear_rutina.html  # Formulario para crear rutinas
│   ├── editar_rutina.html  # Formulario para editar rutinas
│   ├── ver_rutina.html  # Vista de rutina
│   ├── crear_ejercicio.html  # Formulario para crear ejercicios
│   └── editar_ejercicio.html  # Formulario para editar ejercicios
├── requirements.txt     # Dependencias del proyecto
└── README.md           # Este archivo
```

## Contribución

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -am 'Añadir nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles. 