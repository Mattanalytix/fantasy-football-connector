from flask import Flask
from log.logger import setup_logging

app = Flask(__name__)

@app.before_request
def init_logging():
    setup_logging()
