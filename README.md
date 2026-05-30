# HappyPaws — Sistema de gestión veterinaria

Aplicación web para clínicas veterinarias construida con Django y PostgreSQL (Cloud SQL en GCP).

## Estructura del proyecto

```
HappyPaws/
├── happypaws/          # Configuración Django (settings, urls, wsgi)
├── clinica/            # App principal — modelos, vistas, formularios, admin
│   └── migrations/
├── templates/clinica/  # Templates HTML (index, login, consulta_detalle)
├── static/             # CSS y JS
├── Dockerfile          # Para despliegue en Cloud Run
├── app.yaml            # Configuración para App Engine (alternativa)
└── .github/workflows/  # CI/CD con GitHub Actions → Cloud Run
```

## Roles de usuario

| Rol | Permisos |
|---|---|
| **Administrador** | Acceso total + crear Veterinarios y Recepcionistas |
| **Veterinario** | Acceso clínico + crear Recepcionistas |
| **Recepcionista** | Solo agendar consultas con datos existentes |

## Configuración local

### 1. Requisitos
- Python 3.12+
- PostgreSQL 17
- Cloud SQL Auth Proxy (para conectar a la BD de GCP en local)

### 2. Variables de entorno

Copia `.env.example` a `.env` y completa los valores:

```
DJANGO_SECRET_KEY=...
DEBUG=True
DB_NAME=happypaws
DB_USER=happypaws_user
DB_PASSWORD=...
DB_HOST=127.0.0.1          # via Cloud SQL Proxy local
CLOUD_SQL_CONNECTION_NAME= # vacío en local
```

### 3. Instalar dependencias y migrar

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Despliegue en GCP (Cloud Run)

### APIs requeridas
Habilitar en GCP Console → proyecto `happypawschl`:
- Cloud Run API
- Cloud SQL Admin API
- Cloud Resource Manager API
- Container Registry API
- Cloud Build API

### Permisos de la cuenta de servicio
Además de los roles ya asignados, agregar:
```bash
gcloud projects add-iam-policy-binding happypawschl \
  --member="serviceAccount:yiokai-as@happypawschl.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

### Crear instancia CloudSQL (primera vez)
```bash
gcloud sql instances create happypaws-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --project=happypawschl

gcloud sql databases create happypaws --instance=happypaws-db
gcloud sql users create happypaws_user --instance=happypaws-db --password=TU_PASSWORD
```

### Secrets en GitHub
Configurar en Settings → Secrets and variables → Actions:

| Secret | Valor |
|---|---|
| `GCP_PROJECT_ID` | `happypawschl` |
| `GCP_SA_KEY` | Contenido de `happypawschl_pass.json` |
| `GCP_REGION` | `us-central1` |
| `CLOUD_SQL_CONNECTION_NAME` | `happypawschl:us-central1:happypaws-db` |
| `DJANGO_SECRET_KEY` | Clave secreta larga |
| `DB_NAME` | `happypaws` |
| `DB_USER` | `happypaws_user` |
| `DB_PASSWORD` | Password elegido |

### Deploy
Cada push a `main` despliega automáticamente via GitHub Actions.
El workflow construye la imagen Docker, la publica en GCR y ejecuta las migraciones.
