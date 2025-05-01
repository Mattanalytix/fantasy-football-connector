# Fantasy Football Connector

The fantasy football connector is an ETL application for ingesting data into GCP from the fantasy.premierleague api.

## Project Tree

```cmd
fantasy-football-connector/
│── fetch_data/                   # Fetchers for API endpoints
│   ├── __init__.py
│   ├── fixtures.py                # Handles /fixtures endpoint
│   ├── element_summary.py         # Handles /element-summary endpoint
│   ├── bootstrap_static.py        # Handles /bootstrap-static endpoint
│── process/                       # Processing & transformation logic
│   ├── __init__.py
│   ├── fixtures.py           # Logic for filtering players based on play history
│   ├── element_summary.py
│── upload/                        # Upload data to BigQuery
│   ├── __init__.py
│   ├── bigquery_uploader.py       # Handles BQ interactions
│── log/                           # Logging utilities
│   ├── __init__.py
│   ├── slack_logger.py            # Slack logging integration
│   ├── logger.py                  # General logging setup
│── config/                        # Configuration management
│   ├── __init__.py
│   ├── settings.py                # Environment variables and settings
│── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_fixtures.py
│   ├── test_element_summary.py
│   ├── test_bigquery_uploader.py
│── app.py                         # Flask app entry point
│── requirements.txt                # Dependencies
│── Dockerfile                      # Docker container setup
│── cloudbuild.yaml                  # Cloud Build configuration (CI/CD)
│── README.md                        # Project documentation
```

## Local Development

Create your local development environment

```cmd
conda create -n fantasy-football-connector pip
conda activate fantasy-football-connector
pip install -r requirements.txt
pip install python-dotenv
```

Before running functions make sure you are logged in and setup to GCP.

```cmd
gcloud auth application-default login
gcloud config set project YOUR_PROJECT
```

Add variables to a file named `.env`

```.env
BUCKET=YOUR_ETL_BUCKET
```

## Pushing to Artifact Registry

```cmd
gcloud auth configure-docker
gcloud auth login
docker compose build
docker compose push
```

## Debugging the Cloud Run Emulator

```cmd
minikube -p cloud-run-dev-internal stop
minikube -p cloud-run-dev-internal start
```