import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def lambda_handler(event, context):
    """
    Lambda function to fetch text content from an S3 object.
    """
    try:
        # Extract S3 URL from the event
        s3_url = event['s3_url']

        # Parse the S3 bucket name and object key from the URL
        parsed_url = s3_url.replace("https://", "").split('.s3.amazonaws.com/')
        bucket_name = parsed_url[0]
        object_key = parsed_url[1]

        # Initialize the S3 client
        s3_client = boto3.client('s3')

        # Fetch the object
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        text_content = response['Body'].read().decode('utf-8')

        return {"statusCode": 200, "text_content": text_content}
    except (NoCredentialsError, ClientError) as e:
        return {"statusCode": 500, "error": str(e)}
