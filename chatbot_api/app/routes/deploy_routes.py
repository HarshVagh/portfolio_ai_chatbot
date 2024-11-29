from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dynamodb_models import User, Chat
from utils.lambda_utils import invoke_lambda
import os
import logging

logger = logging.getLogger(__name__)
deploy_bp = Blueprint('deploy', __name__)

@deploy_bp.route('/api/deploy', methods=['POST'])
@jwt_required()
def deploy_chat():
    data = request.json
    chat_id = data.get('chat_id')
    content = data.get('content')

    if not chat_id or not content:
        return jsonify({'error': 'Chat ID and content are required'}), 400

    # Get the current user from the JWT token
    current_user = get_jwt_identity()
    user = User.get_user_by_email(current_user['email'])

    if not user:
        logger.error("User not found in DynamoDB")
        return jsonify({'error': 'User not found'}), 404

    logger.info(f"Received deployment request for chat {chat_id} from user {user['id']}")

    # Define S3 file path
    s3_file_path = f"pages/{user['id']}/pages-{chat_id}/index.html"

    # Call Lambda to deploy content to S3
    lambda_payload = {
        "content": content,
        "s3_key": s3_file_path,
        "bucket_name": os.getenv('AWS_S3_BUCKET_NAME')
    }
    lambda_response = invoke_lambda("deploy_to_s3", lambda_payload)

    if 'error' in lambda_response or 's3_url' not in lambda_response:
        logger.error("Failed to deploy content via Lambda")
        return jsonify({'error': 'Failed to deploy content'}), 500

    s3_url = lambda_response['s3_url']

    # Update the chat in DynamoDB with the new page_url
    chat = Chat.get_chat_by_id(chat_id)
    if not chat:
        logger.error(f"Chat not found: {chat_id}")
        return jsonify({'error': 'Chat not found'}), 404

    Chat.update_page_url(chat_id=chat_id, page_url=s3_url)

    logger.info(f"Chat {chat_id} updated with page URL: {s3_url}")
    return jsonify({'page_url': s3_url}), 200
