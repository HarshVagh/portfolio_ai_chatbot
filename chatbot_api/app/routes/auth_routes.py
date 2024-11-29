from flask import Blueprint, request, jsonify
from dynamodb_models import User  # Import the DynamoDB User model
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    logger.info("Received signup request")
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Check if the email already exists in DynamoDB
    existing_user = User.get_user_by_email(email)
    if existing_user:
        logger.warning(f"Signup failed: Email {email} already exists")
        return jsonify({'error': 'Email already exists'}), 409

    # Hash the password and store the user in DynamoDB
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user_id = User.create_user(name=name, email=email, password=hashed_password)

    logger.info(f"User {email} signed up successfully with ID {user_id}")

    # Generate a JWT token
    expires = timedelta(days=15)
    access_token = create_access_token(identity={'email': email}, expires_delta=expires)
    return jsonify({'token': access_token}), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    logger.info("Received login request")
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Retrieve the user by email from DynamoDB
    user = User.get_user_by_email(email)
    if user and bcrypt.check_password_hash(user['password'], password):
        logger.info(f"User {email} logged in successfully")

        # Generate a JWT token
        expires = timedelta(days=15)
        access_token = create_access_token(identity={'email': user['email']}, expires_delta=expires)
        return jsonify({'token': access_token}), 200

    logger.warning(f"Login failed for email {email}")
    return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/api/auth/user', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        logger.info("Fetching current user information")

        # Get the current user's identity (email) from the JWT token
        current_user = get_jwt_identity()

        # Retrieve the user by email from DynamoDB
        user = User.get_user_by_email(current_user['email'])

        if not user:
            # Return an error if the user is not found
            logger.warning(f"User not found: {current_user['email']}")
            return jsonify({'error': 'User not found'}), 404

        # Return the user's information as JSON
        user_info = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }

        logger.info(f"User information fetched: {user_info}")
        return jsonify({'user': user_info}), 200

    except Exception as e:
        # Catch any exception and return an error response
        logger.error(f"Error fetching user information: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching user information'}), 500
