from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dynamodb_models import User, Chat, Message  # Updated to use DynamoDB models
from utils.lambda_utils import invoke_lambda
from utils.pdf_utils import extract_text_from_pdf
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chats', methods=['POST'])
@jwt_required()
def create_chat():
    logger.info("Received create chat request")
    current_user = get_jwt_identity()

    # Fetch user information from DynamoDB
    user = User.get_user_by_email(current_user['email'])
    if not user:
        logger.error("User not found in DynamoDB")
        return jsonify({'error': 'User not found'}), 404

    title = request.form.get('title')
    additional_description = request.form.get('additionalDescription')
    resume = request.files['resume']

    if not title or not resume:
        logger.warning("Chat creation failed: Missing required fields")
        return jsonify({'error': 'Missing required fields'}), 400

    resume_filename = resume.filename
    resume_file = resume.read()  # Read the file content directly

    # Extract text from PDF for initial prompt
    resume_text = extract_text_from_pdf(resume_file)

    # Call Lambda to upload resume to S3
    lambda_payload = {
        "text_content": resume_text,
        "user_id": user['id'],
        "filename": resume_filename,
        "bucket_name": os.getenv('AWS_S3_BUCKET_NAME')
    }
    lambda_response = invoke_lambda("upload_file_to_s3", lambda_payload)

    if 'error' in lambda_response or 'file_url' not in lambda_response:
        logger.error("Failed to upload resume via Lambda")
        return jsonify({'error': 'Failed to upload resume'}), 500

    resume_url = lambda_response['file_url']

    # Create the chat entry in DynamoDB
    chat_id = Chat.create_chat(
        user_id=user['id'],
        title=title,
        additional_description=additional_description,
        resume_url=resume_url
    )
    logger.info(f"Chat {chat_id} created for user {user['email']}")

    # Prepare initial prompt
    initial_prompt = (
        "Using my resume, generate a static HTML and CSS portfolio page with a good-looking UI and CSS. "
        "Only provide the code, no explanations or other text. Keep everything in a single file (index.html) "
        "and use internal CSS and JS.\n"
        f"Additional Description: {additional_description}\n\n"
        f"Resume Text:\n{resume_text}"
    )
    lambda_payload = {
        'prompt': initial_prompt,
        'resume_url': resume_url
    }
    lambda_response = invoke_lambda("call_chatgpt", lambda_payload)
    if 'error' in lambda_response or 'body' not in lambda_response:
        logger.error("Failed to call chat gpt lambda")
        return jsonify({'error': 'Failed to call chat gpt lambda'}), 500
    initial_response = lambda_response['body']

    # Store the initial response as a message in DynamoDB
    Message.add_message(chat_id=chat_id, sender='bot', text=initial_response)

    logger.info(f"Initial response stored in chat {chat_id}: {initial_response}")
    return jsonify({
        'chat': {
            'id': chat_id,
            'title': title,
            'page_url': '',
            'initialMessage': {
                'sender': 'bot',
                'text': initial_response
            },
            'messages': [
                {
                    'sender': 'bot',
                    'text': initial_response,
                    'time': datetime.utcnow().isoformat()
                }
            ]
        }
    }), 201


@chat_bp.route('/api/chats', methods=['GET'])
@jwt_required()
def get_chats():
    logger.info("Fetching chats for current user")
    current_user = get_jwt_identity()

    # Fetch user information from DynamoDB
    user = User.get_user_by_email(current_user['email'])
    if not user:
        logger.error("User not found in DynamoDB")
        return jsonify({'error': 'User not found'}), 404

    # Fetch all chats for the user from DynamoDB
    chats = Chat.get_chats_by_user(user['id'])
    logger.info(f"Found {len(chats)} chats for user {user['email']}")

    # Fetch last messages for each chat
    chat_list = []
    for chat in chats:
        messages = Message.get_messages_by_chat(chat['id'])
        last_message = messages[-1]['text'] if messages else ''
        last_updated = messages[-1]['timestamp'] if messages else ''

        chat_list.append({
            'id': chat['id'],
            'title': chat['title'],
            'page_url': chat['page_url'],
            'lastMessage': last_message,
            'lastUpdated': last_updated
        })

    return jsonify({'chats': chat_list}), 200
