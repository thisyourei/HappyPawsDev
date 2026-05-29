# HappyPaws Backend

A minimal Flask app that serves the static mockup from the `home/` folder.

## Run locally (Windows)

1. Open PowerShell or Command Prompt.
2. Change directory to the backend folder:

```powershell
cd \Users\xhyos\Documents\projects\repos\HappyPaws\backend
```

3. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Start the app:

```powershell
python app.py
```

6. Open http://127.0.0.1:5000/ in your browser.

## Run with Docker

From the repository root, build and run the container:

```powershell
docker build -t happypaws-app .
docker run -p 5000:5000 happypaws-app
```

Then open http://127.0.0.1:5000/.

## Cloud deployment options

### Google Cloud Run

1. Install and authenticate the Google Cloud SDK.
2. From the repository root, build and push the image:

```powershell
gcloud builds submit --tag gcr.io/PROJECT_ID/happypaws-app
```

3. Deploy to Cloud Run:

```powershell
gcloud run deploy happypaws-app --image gcr.io/PROJECT_ID/happypaws-app --platform managed --region REGION --allow-unauthenticated
```

### Google App Engine

This repo already includes `app.yaml` at the root. Deploy with:

```powershell
gcloud app deploy
```

### AWS Elastic Beanstalk / AWS ECS

Use the root `Dockerfile` to containerize the app and deploy it to AWS using Elastic Beanstalk or ECS. You can also use Copilot or the AWS Console to deploy the container image.

### Deploy with GitHub Actions to Google Cloud Run

This repository includes a workflow at `.github/workflows/deploy-cloud-run.yml`.

To use it, configure these GitHub secrets:

- `GCP_PROJECT_ID`: your Google Cloud project ID.
- `GCP_REGION`: Cloud Run region, like `us-central1`.
- `GCP_SA_KEY`: JSON key for a Google Cloud service account with `roles/run.admin`, `roles/cloudbuild.builds.editor`, `roles/storage.admin`, and `roles/iam.serviceAccountUser`.

When you push to `main`, the workflow:

1. checks out the repo,
2. sets up `gcloud`,
3. builds and pushes a Docker image to `gcr.io`,
4. deploys the service to Cloud Run,
5. prints the deployed service URL.
