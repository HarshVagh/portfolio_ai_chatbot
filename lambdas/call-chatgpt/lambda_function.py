import os
import boto3
import json
from openai import OpenAI

def get_secret(secret_name):
    """Retrieve a secret from AWS Secrets Manager."""
    secrets_client = boto3.client(
        'secretsmanager',
        region_name="us-east-1"
    )
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

def get_text_from_s3(bucket_name, key_name):
    """Retrieve text content from an S3 object."""
    s3_client = boto3.client('s3', region_name="us-east-1")
    response = s3_client.get_object(Bucket=bucket_name, Key=key_name)
    return response['Body'].read().decode('utf-8')

def lambda_handler(event, context):
    try:
        # Retrieve environment variables
        secret_name = os.environ['SECRETS_ARN']
        
        # Retrieve secrets
        secrets = get_secret(secret_name)
        
        # Extract parameters from the event
        prompt = event.get('prompt', '')
        resume_url = event.get('resume_url', '')

        # Extract bucket name and key from the S3 URL
        parsed_url = resume_url.replace("https://", "").split('.s3.amazonaws.com/')
        if len(parsed_url) != 2:
            raise ValueError("Invalid S3 URL format.")
        bucket_name, key_name = parsed_url
        
        # Retrieve text content from S3
        text_content = get_text_from_s3(bucket_name, key_name)
        
        # Prepare the full prompt
        full_prompt = (
            f"{prompt}\n\nAccess and extract text from my resume for information "
            f"about my portfolio.\n\nHere is an AWS S3 public link to my resume: \n"
            f"---------------------\n{text_content}"
        )
        
        # Initialize OpenAI client
        client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
        
        # Create messages for the ChatGPT API
        messages = [
            {"role": "system", "content": secrets['OPENAI_INSTRUCTIONS']},
            {"role": "user", "content": full_prompt}
        ]
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        # Return the response
        return {
            'statusCode': 200,
            'body': response.choices[0].message.content.strip()
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': "An error occurred while processing the request."
        }
