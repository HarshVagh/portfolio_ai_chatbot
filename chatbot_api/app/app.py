from app import create_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == "__main__":
    logger.info("Starting Flask application")
    app.run(host=app.config['FLASK_RUN_HOST'], port=int(app.config['FLASK_RUN_PORT']), debug=True)
