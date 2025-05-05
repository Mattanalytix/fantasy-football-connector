import os
import logging
from flask import render_template, jsonify, request
from app import app

from etl.process.bootstrap_static import get_elements_from_team
from etl.process.element_summary import fetch_and_upload_element_summary
from etl.utils.string_manipulation import list_of_ints


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
        # Get required config from environment variables
        project_id = os.getenv('PROJECT_ID')
        bucket_name = os.getenv('BUCKET_ID')
        dataset_id = os.getenv('DATASET_ID')

        if not project_id or not bucket_name or not dataset_id:
            raise ValueError(
                "PROJECT_ID, BUCKET_NAME, and DATASET_ID must be"
                "set in environment variables.")

        data = request.get_json()

        destination_folder = data.get('destination_folder', 'element_summary')
        team_ids = list_of_ints(data.get('team_ids'))  # Optional
        element_ids = list_of_ints(data.get('element_ids'))  # Optional
        max_workers = data.get('max_workers', 5)

        fetch_and_upload_element_summary(
            project_id=project_id,
            bucket_name=bucket_name,
            dataset_id=dataset_id,
            destination_folder=destination_folder,
            team_ids=team_ids,
            element_ids=element_ids,
            max_workers=max_workers
        )

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(
            f"Error in fetch_and_upload_element_summary_endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get-elements-from-team', methods=['POST'])
def get_elements_from_team_endpoint():
    try:
        data = request.get_json()
        team_id = int(data.get('team_id'))

        logging.info(f"Retrieveing elements for team_id: {team_id}")
        elements = get_elements_from_team(team_id)
        return jsonify({"elements": elements}), 200

    except Exception as e:
        logging.error(
            f"Error in get_elements_from_team_endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
