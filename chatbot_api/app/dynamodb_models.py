import boto3
import uuid
from datetime import datetime

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Define the tables (Make sure these tables exist in your DynamoDB)
USERS_TABLE = 'users'
CHATS_TABLE = 'chats'
MESSAGES_TABLE = 'messages'

class User:
    @staticmethod
    def create_user(name, email, password):
        table = dynamodb.Table(USERS_TABLE)
        user_id = str(uuid.uuid4())
        table.put_item(
            Item={
                'id': user_id,
                'name': name,
                'email': email,
                'password': password
            }
        )
        return user_id

    @staticmethod
    def get_user_by_email(email):
        table = dynamodb.Table(USERS_TABLE)
        response = table.get_item(Key={'email': email})
        return response.get('Item')

    @staticmethod
    def get_user_by_id(user_id):
        table = dynamodb.Table(USERS_TABLE)
        response = table.get_item(Key={'id': user_id})
        return response.get('Item')


class Chat:
    @staticmethod
    def create_chat(user_id, title, additional_description, resume_url, page_url=""):
        table = dynamodb.Table(CHATS_TABLE)
        chat_id = str(uuid.uuid4())
        table.put_item(
            Item={
                'id': chat_id,
                'user_id': user_id,
                'title': title,
                'additional_description': additional_description,
                'resume_url': resume_url,
                'page_url': page_url,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        return chat_id

    @staticmethod
    def get_chats_by_user(user_id):
        table = dynamodb.Table(CHATS_TABLE)
        response = table.query(
            IndexName='user_id-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        return response.get('Items', [])

    @staticmethod
    def get_chat_by_id(chat_id):
        table = dynamodb.Table(CHATS_TABLE)
        response = table.get_item(Key={'id': chat_id})
        return response.get('Item')

    @staticmethod
    def update_page_url(chat_id, page_url):
        table = dynamodb.Table(CHATS_TABLE)
        table.update_item(
            Key={'id': chat_id},
            UpdateExpression='SET page_url = :url',
            ExpressionAttributeValues={':url': page_url}
        )


class Message:
    @staticmethod
    def add_message(chat_id, sender, text):
        table = dynamodb.Table(MESSAGES_TABLE)
        message_id = str(uuid.uuid4())
        table.put_item(
            Item={
                'id': message_id,
                'chat_id': chat_id,
                'sender': sender,
                'text': text,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        return message_id

    @staticmethod
    def get_messages_by_chat(chat_id):
        table = dynamodb.Table(MESSAGES_TABLE)
        response = table.query(
            IndexName='chat_id-index',  # Assumes a secondary index on chat_id
            KeyConditionExpression=boto3.dynamodb.conditions.Key('chat_id').eq(chat_id)
        )
        return response.get('Items', [])
