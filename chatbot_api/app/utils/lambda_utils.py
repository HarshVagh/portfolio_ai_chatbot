import boto3
import json

def invoke_lambda(function_name, payload):
    try:
        lambda_client = boto3.client('lambda')
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        return response_payload
    except Exception as e:
        return {"error": str(e)}
