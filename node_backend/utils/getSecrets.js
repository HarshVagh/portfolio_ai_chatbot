import { GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';
import { secretsManagerClient } from './awsClients.js';

async function getSecrets() {
    const secretName = 'PortfolioChatbotSecrets';

    try {
        const command = new GetSecretValueCommand({ SecretId: secretName });
        const response = await secretsManagerClient.send(command);

        const secrets = response.SecretString
            ? JSON.parse(response.SecretString)
            : JSON.parse(Buffer.from(response.SecretBinary, 'base64').toString('utf-8'));

        return secrets;
    } catch (error) {
        console.error('Failed to load secrets to environment:', error.message);
        return "";
    }
}

export default getSecrets;
