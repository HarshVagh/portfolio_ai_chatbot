import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def lambda_handler(event, context):
    """
    Lambda function to upload text content to S3.
    """
    try:
        # Extract parameters from the event
        text_content = event['text_content']
        user_id = event['user_id']
        filename = event['filename']
        bucket_name = event['bucket_name']

        # Initialize the S3 client
        s3_client = boto3.client('s3')

        # Define the S3 file path
        s3_file_path = f"resumes/{user_id}/{filename}"

        # Upload the file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_file_path,
            Body=text_content,
            ContentType='text/plain'
        )

        # Generate the file URL
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_path}"
        return {"statusCode": 200, "file_url": file_url}
    except (NoCredentialsError, ClientError) as e:
        return {"statusCode": 500, "error": str(e)}
