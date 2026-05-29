# HappyPaws

Aplicación mockup de VetClínica con backend Flask y frontend estático.

## Estructura

- `home/`: front-end estático con `index.html`, `assets/css/style.css` y `assets/js/app.js`.
- `backend/`: servidor Flask que sirve `home/index.html` y los assets.
- `Dockerfile`: contenedor para ejecutar la aplicación.
- `app.yaml`: configuración para desplegar en Google App Engine.
- `.github/workflows/deploy-cloud-run.yml`: despliega automáticamente a Google Cloud Run.

## Configuración recomendada

### 1. Conectar el repositorio a GitHub

Sube el proyecto a GitHub y trabaja en la rama `main`.

### 2. Configurar Google Cloud

1. Crea un proyecto en Google Cloud.
2. Habilita las APIs:
   - Cloud Run
   - Cloud Build
   - Artifact Registry (o Container Registry)
3. Crea una cuenta de servicio con estos roles básicos:
   - `roles/run.admin`
   - `roles/cloudbuild.builds.editor`
   - `roles/storage.admin`
   - `roles/iam.serviceAccountUser`
4. Genera una clave JSON para la cuenta de servicio.

### 3. Añadir secretos de GitHub

En el repositorio de GitHub, agrega:

- `GCP_PROJECT_ID`: ID del proyecto de Google Cloud.
- `GCP_REGION`: región, por ejemplo `us-central1` o `us-west1`.
- `GCP_SA_KEY`: contenido JSON de la cuenta de servicio.

### 4. Despliegue automático con GitHub Actions

Cada vez que empujes a `main`, el workflow en `.github/workflows/deploy-cloud-run.yml` hará:

1. Clonar el repositorio.
2. Configurar `gcloud` con tu cuenta de servicio.
3. Construir la imagen Docker.
4. Publicar la imagen en `gcr.io`.
5. Desplegar a Cloud Run.

### 5. Validación de costo

Google Cloud Run ofrece una capa gratuita generosa para pruebas:

- hasta `2M` solicitudes/mes
- `360,000` vCPU-segundos
- `1 GiB` memoria

Eso es ideal para validar tu app sin gastos significativos.

## Otros despliegues posibles

- `Google App Engine`: usa `app.yaml` si prefieres no trabajar con contenedores.
- `AWS`: también puedes usar el `Dockerfile` con Elastic Beanstalk o ECS.

## Notas

El flujo recomendado para pruebas rápidas es:

1. sube el código a GitHub,
2. configura los secretos de GCP,
3. empuja a `main`,
4. revisa la salida del workflow en GitHub Actions.
