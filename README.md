# Fantasy Football Connector

The fantasy football connector is an ETL application for ingesting data into GCP from the fantasy.premierleague api. 

## Project Tree

The main application code sits in the etl folder and the flask app sits in the app folder. The project is structured as follows:

```cmd
fantasy-football-connector/
├── app/                           # Flask web application
│   ├── __init__.py               # Flask app initialization
│   ├── routes.py                 # Route definitions
│   ├── static/                   # Static assets (CSS, JS, images)
│   └── templates/                # HTML templates
├── etl/                          # ETL modules
│   ├── fetch/                    # Data fetching modules
│   │   ├── __init__.py
│   │   ├── bootstrap_static.py   # Bootstrap static data fetching
│   │   └── element_summary.py    # Element summary data fetching
│   ├── process/                  # Data processing modules
│   │   ├── __init__.py
│   │   ├── bootstrap_static.py   # Bootstrap static data processing
│   │   └── element_summary.py    # Element summary data processing
│   ├── upload/                   # Data upload modules
│   │   ├── __init__.py
│   │   ├── storage.py           # Cloud Storage interactions
│   │   └── bigquery.py          # BigQuery interactions
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── string_manipulation.py
├── log/                          # Logging utilities
│   ├── __init__.py
│   └── logger.py                 # General logging setup
├── tests/                        # Test modules
│   ├── __init__.py
│   ├── test_bootstrap_static.py
│   └── test_element_summary.py
├── __init__.py
├── app.py                        # Application entry point
├── requirements.txt              # Project dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── Procfile                      # Heroku deployment configuration
├── pytest.ini                    # Pytest configuration
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── .dockerignore                 # Docker ignore rules
├── .vscode/                      # VS Code configuration
├── .idea/                        # PyCharm configuration
├── .pytest_cache/                # Pytest cache
├── img/                          # Documentation images
└── README.md                     # Project documentation
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
LOCAL_ENV=true
PROJECT_ID=YOUR_PROJECT
DATASET_ID=YOUR_DATASET
BUCKET_ID=YOUR_BUCKET
```

## Running the Web Server

To run the web server locally using vscode make sure you have installed and enabled all of the extensions in the `.vscode/extensions.json` file.

Then to run the app in the Cloud Run Emulator click onto the cloud code extension in the left hand side of vscode and select `Run on Cloud Run Emulator`. This will start the emulator and deploy the app to it.

You can test the app is working by going to `http://localhost:8080/` in your browser. You should see the Hello World index page. You can then test the endpoints using an extension such as Thunder Client or Postman.

## Pushing to Artifact Registry

```cmd
gcloud auth configure-docker
gcloud auth login
docker compose build
docker compose push
```

## Debugging the Cloud Run Emulator

There is currently a bug in the Cloud Run Emulator that causes the `gcp-auth` addon to not work properly. If you come across this issue you can fix it by running the following commands:

```cmd
minikube -p cloud-run-dev-internal stop
minikube -p cloud-run-dev-internal start
```