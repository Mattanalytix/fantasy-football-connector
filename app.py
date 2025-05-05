import os
import logging

from flask import Flask
from flask import render_template, jsonify, request
from models import (
    ElementSummaryRequest,
    ElementFromTeamRequest
)
from config import Config

from etl.process.bootstrap_static import get_elements_from_team
from etl.process.element_summary import fetch_and_upload_element_summary
from log.logger import setup_logging


# Initialize logging
setup_logging()

# Load and validate configuration early
try:
    config = Config.from_env()
except ValueError as e:
    logging.error(f"Failed to load configuration: {e}")
    raise

# Create Flask app
app = Flask(
    __name__,
    template_folder='ui/templates',
    static_folder='ui/static'
)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
                           message=message,
                           Service=service,
                           Revision=revision)


@app.route('/fetch-and-upload-element-summary', methods=['POST'])
def fetch_and_upload_element_summary_endpoint():
    try:
        data = ElementSummaryRequest(**request.get_json())

        fetch_and_upload_element_summary(
            project_id=config.project_id,
            bucket_name=config.bucket_name,
            dataset_id=config.dataset_id,
            destination_folder=data.destination_folder,
            team_ids=data.team_ids,
            element_ids=data.element_ids,
            max_workers=data.max_workers
        )

        return jsonify({"status": "success"}), 200

    except ValueError as ve:
        logging.error(f"Validation error in "
                      f"fetch_and_upload_element_summary_endpoint: {ve}")
        return jsonify({"status": "error", "message": str(ve)}), 400

    except Exception as e:
        logging.error(
            f"Error in fetch_and_upload_element_summary_endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get-elements-from-team', methods=['POST'])
def get_elements_from_team_endpoint():
    try:
        # Validate input using Pydantic model
        data = ElementFromTeamRequest(**request.get_json())

        logging.info(f"Retrieveing elements for team_id: {data.team_id}")
        elements = get_elements_from_team(data.team_id)
        return jsonify({"elements": elements}), 200

    except ValueError as ve:
        logging.error(f"Validation error in get_elements_from_team_endpoint:"
                      f" {ve}")
        return jsonify({"status": "error", "message": str(ve)}), 400

    except Exception as e:
        logging.error(
            f"Error in get_elements_from_team_endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')
