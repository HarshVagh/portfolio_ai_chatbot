from flask import Flask
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """
    Factory function to create and configure the Flask app.
    """
    # Create Flask app instance
    app = Flask(__name__)

    # Load configuration from the Config class
    config = Config()
    app.config.from_object(config)

    @app.route("/")
    def home():
        return (
            f"Flask is running on host: {app.config['FLASK_RUN_HOST']}, "
            f"port: {app.config['FLASK_RUN_PORT']}"
        )

    return app

# Main entry point
if __name__ == "__main__":
    app = create_app()
    
    # Log the startup information
    logger.info("Starting Flask application")
    logger.info(f"Running on http://{app.config['FLASK_RUN_HOST']}:{app.config['FLASK_RUN_PORT']}")
    
    # Run the Flask application with host and port from configuration
    app.run(
        host=app.config['FLASK_RUN_HOST'],
        port=int(app.config['FLASK_RUN_PORT']),
        debug=True
    )
