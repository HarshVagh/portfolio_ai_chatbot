import boto3
import json
import os

class Config:
    def __init__(self):
        # Initialize AWS Secrets Manager client
        self.secrets_client = boto3.client('secretsmanager', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Load secrets once
        self.secrets = self._fetch_secrets("PortfolioChatbotSecrets")

    def _fetch_secrets(self, secret_name):
        """
        Fetch secrets from AWS Secrets Manager.
        """
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            elif 'SecretBinary' in response:
                return json.loads(response['SecretBinary'].decode('utf-8'))
        except Exception as e:
            print(f"Error fetching secrets: {e}")
            return {}
        
    def __getitem__(self, item):
        """
        Allow dictionary-style access.
        """
        return getattr(self, item, None)

    def __getattr__(self, item):
        """
        Dynamically fetch attributes from secrets or default to None.
        """
        return self.secrets.get(item)

    # Properties for configuration values
    @property
    def AWS_REGION(self):
        return os.getenv('AWS_REGION', 'us-east-1')

    @property
    def DYNAMODB_USERS_TABLE(self):
        return self.secrets.get('DYNAMODB_USERS_TABLE', 'users')

    @property
    def DYNAMODB_CHATS_TABLE(self):
        return self.secrets.get('DYNAMODB_CHATS_TABLE', 'chats')

    @property
    def DYNAMODB_MESSAGES_TABLE(self):
        return self.secrets.get('DYNAMODB_MESSAGES_TABLE', 'messages')

    @property
    def FLASK_APP(self):
        return self.secrets.get('FLASK_APP')

    @property
    def FLASK_ENV(self):
        return self.secrets.get('FLASK_ENV')

    @property
    def FLASK_RUN_HOST(self):
        return self.secrets.get('FLASK_RUN_HOST')

    @property
    def FLASK_RUN_PORT(self):
        return self.secrets.get('FLASK_RUN_PORT')
    
    @property
    def AWS_S3_BUCKET_NAME(self):
        return self.secrets.get('AWS_S3_BUCKET_NAME')

    @property
    def OPENAI_API_KEY(self):
        return self.secrets.get('OPENAI_API_KEY')

    @property
    def OPENAI_INSTRUCTIONS(self):
        return self.secrets.get('OPENAI_INSTRUCTIONS')

    @property
    def JWT_SECRET_KEY(self):
        return self.secrets.get('JWT_SECRET_KEY')
