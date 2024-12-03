import { SecretsManagerClient } from "@aws-sdk/client-secrets-manager";
import { S3Client } from "@aws-sdk/client-s3";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";

const AWS_REGION = 'us-east-1';

const secretsManagerClient = new SecretsManagerClient({ region: AWS_REGION });
const s3Client = new S3Client({ region: AWS_REGION });
const dynamoDBClient = new DynamoDBClient({ region: AWS_REGION });

export { secretsManagerClient, s3Client, dynamoDBClient };