# Gym App

Aplicación web para gestión de rutinas de entrenamiento y seguimiento de progreso.

## Características

- Registro e inicio de sesión de usuarios
- Diferentes tipos de usuarios (administrador, entrenador, usuario)
- Gestión de rutinas de entrenamiento
- Creación y asignación de ejercicios
- Seguimiento del progreso de los usuarios
- Estadísticas y gráficos de rendimiento

## Tecnologías utilizadas

- Python
- Flask
- SQLAlchemy
- HTML/CSS
- JavaScript
- Chart.js

## Instalación

1. Clonar el repositorio:
```
git clone https://github.com/tu-usuario/gym-app.git
cd gym-app
```

2. Crear un entorno virtual e instalar dependencias:
```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar variables de entorno:
Crear un archivo `.env` con las siguientes variables:
```
FLASK_APP=trainingapp.py
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta
DATABASE_URL=sqlite:///gym.db
```

4. Inicializar la base de datos:
```
flask db init
flask db migrate
flask db upgrade
```

5. Ejecutar la aplicación:
```
flask run
```

## Estructura del proyecto

```
gym-app/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
├── templates/
│   ├── admin/
│   ├── auth/
│   └── user/
├── trainingapp.py
├── models.py
├── forms.py
├── requirements.txt
└── README.md
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles. 