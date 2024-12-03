import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand, QueryCommand, GetCommand, UpdateCommand } from '@aws-sdk/lib-dynamodb';
import { v4 as uuidv4 } from 'uuid';

const client = new DynamoDBClient({ region: 'us-east-1' });
const dynamodb = DynamoDBDocumentClient.from(client);

// Define table names and indexes
const USERS_TABLE = 'users';
const CHATS_TABLE = 'chats';
const MESSAGES_TABLE = 'messages';

const EMAIL_INDEX = 'email-index';
const USER_INDEX = 'user_id-index';
const CHAT_INDEX = 'chat_id-index';

class User {
    static async createUser(name, email, password) {
        const userId = uuidv4();
        const params = {
            TableName: USERS_TABLE,
            Item: {
                id: userId,
                name,
                email,
                password,
            },
        };
        await dynamodb.send(new PutCommand(params));
        return userId;
    }

    static async getUserByEmail(email) {
        const params = {
            TableName: USERS_TABLE,
            IndexName: EMAIL_INDEX,
            KeyConditionExpression: 'email = :email',
            ExpressionAttributeValues: {
                ':email': email,
            },
        };

        try {
            const response = await dynamodb.send(new QueryCommand(params));
            return response.Items && response.Items.length ? response.Items[0] : null;
        } catch (error) {
            console.error('Error fetching user by email:', error);
            throw error;
        }
    }

    static async getUserById(userId) {
        const params = {
            TableName: USERS_TABLE,
            Key: { id: userId },
        };

        try {
            const response = await dynamodb.send(new GetCommand(params));
            return response.Item || null;
        } catch (error) {
            console.error('Error fetching user by ID:', error);
            throw error;
        }
    }
}

class Chat {
    static async createChat(userId, title, additionalDescription, resumeUrl, pageUrl = '') {
        const chatId = uuidv4();
        const params = {
            TableName: CHATS_TABLE,
            Item: {
                id: chatId,
                user_id: userId,
                title,
                additional_description: additionalDescription,
                resume_url: resumeUrl,
                page_url: pageUrl,
                created_at: new Date().toISOString(),
            },
        };
        await dynamodb.send(new PutCommand(params));
        return chatId;
    }

    static async getChatsByUser(userId) {
        const params = {
            TableName: CHATS_TABLE,
            IndexName: USER_INDEX,
            KeyConditionExpression: 'user_id = :user_id',
            ExpressionAttributeValues: {
                ':user_id': userId,
            },
        };

        try {
            const response = await dynamodb.send(new QueryCommand(params));
            return response.Items || [];
        } catch (error) {
            console.error('Error fetching chats by user:', error);
            throw error;
        }
    }

    static async getChatById(chatId) {
        const params = {
            TableName: CHATS_TABLE,
            Key: { id: chatId },
        };

        try {
            const response = await dynamodb.send(new GetCommand(params));
            return response.Item || null;
        } catch (error) {
            console.error('Error fetching chat by ID:', error);
            throw error;
        }
    }

    static async updatePageUrl(chatId, pageUrl) {
        const params = {
            TableName: CHATS_TABLE,
            Key: { id: chatId },
            UpdateExpression: 'SET page_url = :page_url',
            ExpressionAttributeValues: {
                ':page_url': pageUrl,
            },
        };

        try {
            await dynamodb.send(new UpdateCommand(params));
        } catch (error) {
            console.error('Error updating page URL:', error);
            throw error;
        }
    }
}

class Message {
    static async addMessage(chatId, sender, text) {
        const messageId = uuidv4();
        const params = {
            TableName: MESSAGES_TABLE,
            Item: {
                id: messageId,
                chat_id: chatId,
                sender,
                text,
                timestamp: new Date().toISOString(),
            },
        };

        await dynamodb.send(new PutCommand(params));
        return messageId;
    }

    static async getMessagesByChat(chatId) {
        const params = {
            TableName: MESSAGES_TABLE,
            IndexName: CHAT_INDEX,
            KeyConditionExpression: 'chat_id = :chat_id',
            ExpressionAttributeValues: {
                ':chat_id': String(chatId),
            },
        };

        try {
            const response = await dynamodb.send(new QueryCommand(params));
            return response.Items || [];
        } catch (error) {
            console.error('Error fetching messages by chat:', error);
            throw error;
        }
    }
}

export { User, Chat, Message };
