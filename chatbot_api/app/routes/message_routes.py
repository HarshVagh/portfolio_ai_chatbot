from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dynamodb_models import User, Chat, Message
from utils.lambda_utils import invoke_lambda
import logging

logger = logging.getLogger(__name__)
message_bp = Blueprint('message', __name__)

@message_bp.route('/api/chats/<string:chat_id>/messages', methods=['POST'])
@jwt_required()
def send_message(chat_id):
    data = request.json
    user_message = data.get('message')
    current_user = get_jwt_identity()

    logger.info(f"Received message for chat {chat_id} from user {current_user['email']}")

    # Retrieve user from DynamoDB
    user = User.get_user_by_email(current_user['email'])
    if not user:
        logger.warning(f"User not found: {current_user['email']}")
        return jsonify({'error': 'User not found'}), 404

    # Retrieve chat from DynamoDB
    chat = Chat.get_chat_by_id(chat_id)
    if not chat:
        logger.warning(f"Chat not found: {chat_id}")
        return jsonify({'error': 'Chat not found'}), 404

    if chat['user_id'] != user['id']:
        logger.warning(f"Unauthorized access attempt by user {user['email']} for chat {chat_id}")
        return jsonify({'error': 'Unauthorized access'}), 403

    # Save user message to DynamoDB
    Message.add_message(chat_id=chat_id, sender='user', text=user_message)
    logger.info(f"User message stored in chat {chat_id}: {user_message}")

    # Retrieve all messages for the chat
    all_messages = Message.get_messages_by_chat(chat_id)

    # Build the conversation context
    conversation_context = ''
    for msg in all_messages:
        conversation_context += f"{msg['sender']}: {msg['text']}\n"

    # Add user message to the context
    conversation_context += f"user: {user_message}\n"

    # Generate response with full context
    prompt = (
        f"{conversation_context}\n"
        "Using my resume, generate a static HTML and CSS portfolio page with a good-looking UI and CSS. "
        "Only provide the code, no explanations or other text. Keep everything in a single file (index.html) "
        "and use internal CSS and JS."
    )

    lambda_payload = {
        'prompt': prompt,
        'resume_url': chat['resume_url']
    }
    lambda_response = invoke_lambda("call_chatgpt", lambda_payload)
    if 'error' in lambda_response or 'body' not in lambda_response:
        logger.error("Failed to call chat gpt lambda")
        return jsonify({'error': 'Failed to call chat gpt lambda'}), 500
    response_text = lambda_response['body']

    # Save bot message to DynamoDB
    Message.add_message(chat_id=chat_id, sender='bot', text=response_text)
    logger.info(f"Bot response stored in chat {chat_id}: {response_text}")

    # Return the new message to the client
    return jsonify({
        'message': {
            'sender': 'bot',
            'text': response_text,
            'time': all_messages[-1]['timestamp'] if all_messages else None
        }
    }), 201
