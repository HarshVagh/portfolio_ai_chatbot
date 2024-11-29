import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from io import BytesIO

def lambda_handler(event, context):
    """
    Lambda function to deploy content as a binary stream to S3.
    """
    try:
        # Extract parameters from the event
        content = event['content']
        s3_key = event['s3_key']
        bucket_name = event['bucket_name']

        # Initialize the S3 client
        s3_client = boto3.client('s3')

        # Upload the content
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=content.encode('utf-8'),
            ContentType='text/html'
        )

        # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        return {"statusCode": 200, "s3_url": s3_url}
    except (NoCredentialsError, ClientError) as e:
        return {"statusCode": 500, "error": str(e)}
