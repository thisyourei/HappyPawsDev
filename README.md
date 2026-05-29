# HappyPaws

HappyPaws es un MVP de clínica veterinaria migrado a Django. Ahora el proyecto gestiona mascotas, tutores, veterinarios e informes clínicos desde una aplicación web completa.

## Qué incluye

- Backend Django con modelos para:
  - `Tutor`
  - `Veterinario`
  - `Mascota`
  - `Informe`
- Interfaz web con páginas de dashboard, listas y creación de registros.
- Admin Django para gestión rápida de datos.
- Contenedor Docker listo para desplegar en Google Cloud Run.

## Archivos clave

- `manage.py`: comandos de Django.
- `happypaws/`: configuración del proyecto Django.
- `clinic/`: app que contiene modelos, vistas, formularios, plantillas y estáticos.
- `requirements.txt`: dependencias de Python.
- `Dockerfile`: empaqueta la aplicación para Cloud Run.
- `app.yaml`: configuración opcional para App Engine.
- `.github/workflows/deploy-cloud-run.yml`: pipeline CI/CD para Cloud Run.

## Preparación local

1. Crear un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Ejecutar migraciones:

```powershell
python manage.py migrate
```

4. Crear un superusuario para acceder al admin:

```powershell
python manage.py createsuperuser
```

5. Iniciar el servidor local:

```powershell
python manage.py runserver
```

La app estará disponible en `http://127.0.0.1:8000/`.

## Despliegue en Google Cloud Run

Asegúrate de configurar los siguientes secretos en GitHub:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_SA_KEY`

El workflow en `.github/workflows/deploy-cloud-run.yml` construye la imagen Docker y despliega a Cloud Run cuando haces push a `main`.

## Notas

- El proyecto usa SQLite por defecto en local y en el contenedor.
- Para producción puedes cambiar a una base de datos administrada (`PostgreSQL`, Cloud SQL, etc.).
- Si quieres usar App Engine, `app.yaml` ya incluye el entrypoint para Gunicorn.
