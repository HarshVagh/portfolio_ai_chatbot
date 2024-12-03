import express from 'express';
import jwt from 'jsonwebtoken';
import { User, Chat } from '../models/dynamodbModels.js';
import getSecrets from '../utils/getSecrets.js';
import { deployToS3 } from '../utils/deployToS3.js';

const deployRouter = express.Router();
const secrets = await getSecrets();
const JWT_SECRET_KEY = secrets.JWT_SECRET_KEY;

// Middleware to verify JWT token and extract user identity
const authenticate = (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'Unauthorized' });

    try {
        const decoded = jwt.verify(token, JWT_SECRET_KEY);
        req.user = decoded; // Attach user data to the request
        next();
    } catch (error) {
        return res.status(401).json({ error: 'Invalid token' });
    }
};

// Deploy Chat Route
deployRouter.post('/', authenticate, async (req, res) => {
    const { chat_id: chatId, content } = req.body;

    if (!chatId || !content) {
        return res.status(400).json({ error: 'Chat ID and content are required' });
    }

    const currentUserEmail = req.user.email;

    // Fetch the user from the database
    const user = await User.getUserByEmail(currentUserEmail);
    if (!user) {
        console.error("User not found in the database");
        return res.status(404).json({ error: 'User not found' });
    }

    console.log(`Received deployment request for chat ${chatId} from user ${user.id}`);

    const s3FilePath = `pages/${user.id}/pages-${chatId}/index.html`;
    const s3Url = await deployToS3(content, secrets.AWS_S3_OUTPUT_BUCKET_NAME, s3FilePath);

    if (!s3Url || s3Url === "") {
        console.error("Failed to deploy content");
        return res.status(500).json({ error: 'Failed to deploy content' });
    }

    // Update the chat in the database with the new page URL
    const chat = await Chat.getChatById(chatId);
    if (!chat) {
        console.error(`Chat not found: ${chatId}`);
        return res.status(404).json({ error: 'Chat not found' });
    }

    await Chat.updatePageUrl(chatId, s3Url);

    console.log(`Chat ${chatId} updated with page URL: ${s3Url}`);
    return res.status(200).json({ page_url: s3Url });
});

export default deployRouter;
