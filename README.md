# Training App

Aplicación web para gestión de rutinas de entrenamiento desarrollada con Flask.

## Características

- Sistema de autenticación de usuarios
- Gestión de rutinas de entrenamiento
- Seguimiento de ejercicios
- Panel de administración
- Interfaz responsiva

## Requisitos

- Python 3.9+
- pip (gestor de paquetes de Python)

## Instalación local

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd training-app
```

2. Crear un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Ejecutar la aplicación:
```bash
python trainingapp.py
```

## Despliegue en Render

1. Crear una cuenta en [Render](https://render.com)
2. Crear un nuevo Web Service
3. Conectar con el repositorio de GitHub
4. Configurar las siguientes variables de entorno:
   - `SECRET_KEY`: Una clave secreta para la aplicación
   - `DATABASE_URL`: URL de la base de datos (Render proporcionará una PostgreSQL)
   - `FLASK_ENV`: production
5. Configurar el comando de inicio:
   ```
   gunicorn trainingapp:app
   ```
6. Deploy!

## Usuarios por defecto

- Administrador:
  - Email: admin@example.com
  - Contraseña: admin123
- Usuario normal:
  - Email: usuario@example.com
  - Contraseña: usuario123

## Estructura del proyecto

```
training-app/
├── templates/          # Plantillas HTML
├── static/            # Archivos estáticos (CSS, JS, imágenes)
├── trainingapp.py     # Aplicación principal
├── requirements.txt   # Dependencias
├── .env              # Variables de entorno (no versionado)
└── README.md         # Este archivo
```

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. 