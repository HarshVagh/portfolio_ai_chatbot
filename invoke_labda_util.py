import boto3
import json

def invoke_lambda(function_name, payload):
    """
    Invokes an AWS Lambda function with the given payload.
    
    :param function_name: Name of the Lambda function to invoke
    :param payload: Payload to send to the Lambda function
    :return: Response from the Lambda function
    """
    try:
        # Initialize the Lambda client (IAM role credentials are used automatically)
        lambda_client = boto3.client('lambda')
        
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',  # Synchronous invocation
            Payload=json.dumps(payload)
        )
        
        # Parse the response payload
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        return response_payload
    except Exception as e:
        print(f"Error invoking Lambda function {function_name}: {e}")
        return {"error": str(e)}
