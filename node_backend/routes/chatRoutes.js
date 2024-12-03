import express from 'express';
import jwt from 'jsonwebtoken';
import multer from 'multer';
import { User, Chat, Message } from '../models/dynamodbModels.js';
import extractTextFromPdf from '../utils/pdfUtils.js';
import getSecrets from '../utils/getSecrets.js';
import { uploadFileToS3 } from '../utils/uploadFileToS3.js';
import { callChatGPT } from '../utils/callChatGPT.js';
import { getInitialPrompt } from '../utils/prompts/getInitialPrompt.js';
import { getTextFromS3 } from '../utils/getTextFromS3.js';
import { getPrompt } from '../utils/prompts/getPrompt.js';
import { parse } from 'path';

const chatRouter = express.Router();
const secrets = await getSecrets();
const JWT_SECRET_KEY = secrets.JWT_SECRET_KEY;

// setup multer for file uploads
const upload = multer();

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

// Create Chat Route
chatRouter.post('/', authenticate, upload.single('resume'), async (req, res) => {
    console.log("Received create chat request");
    const currentUserEmail = req.user.email;

    // Fetch user information from the database
    const user = await User.getUserByEmail(currentUserEmail);
    if (!user) {
        console.error("User not found in the database");
        return res.status(404).json({ error: 'User not found' });
    }

    const { title, additionalDescription } = req.body;
    const resume = req.file;

    if (!title || !resume) {
        console.warn("Chat creation failed: Missing required fields");
        return res.status(400).json({ error: 'Missing required fields' });
    }

    const resumeFilename = parse(resume.originalname).name + ".txt";
    const resumeFile = resume.buffer;

    // Extract text from PDF
    const resumeText = await extractTextFromPdf(resumeFile);

    const resumeUrl = await uploadFileToS3(resumeText, user.id, resumeFilename, secrets.AWS_S3_INPUT_BUCKET_NAME);

    if (!resumeUrl || resumeUrl.length === "") {
        console.error("Failed to upload resume");
        return res.status(500).json({ error: 'Failed to upload resume' });
    }

    // Create a new chat in the database
    const chatId = await Chat.createChat(
        user.id,
        title,
        additionalDescription,
        resumeUrl
    );
    console.log(`Chat ${chatId} created for user ${user.email}`);

    const initialPrompt = getInitialPrompt(resumeText, additionalDescription.trim());
    const initialResponse = await callChatGPT(initialPrompt);

    if (!initialResponse || initialResponse === "") {
        console.error("Failed to call ChatGPT");
        return res.status(500).json({ error: 'Failed to call ChatGPT' });
    }

    // Store the initial response as a message in the database
    await Message.addMessage(chatId, 'bot', initialResponse);

    console.log(`Initial response stored in chat ${chatId}`);
    return res.status(201).json({
        chat: {
            id: chatId,
            title,
            page_url: '',
            initialMessage: { sender: 'bot', text: initialResponse },
            messages: [
                { sender: 'bot', text: initialResponse, time: new Date().toISOString() },
            ],
        },
    });
});

// Get Chats Route
chatRouter.get('/', authenticate, async (req, res) => {
    console.log("Fetching chats for the current user");
    const currentUserEmail = req.user.email;

    // Fetch user information from the database
    const user = await User.getUserByEmail(currentUserEmail);
    if (!user) {
        console.error("User not found in the database");
        return res.status(404).json({ error: 'User not found' });
    }

    // Fetch all chats for the user
    const chats = await Chat.getChatsByUser(user.id);
    console.log(`Found ${chats.length} chats for user ${user.email}`);

    // Fetch last messages for each chat
    const chatList = await Promise.all(
        chats.map(async (chat) => {
            const messages = await Message.getMessagesByChat(chat.id);
            messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            const lastMessage = messages.length ? messages[messages.length - 1].text : '';
            const lastUpdated = messages.length ? messages[messages.length - 1].timestamp : '';
            return {
                id: chat.id,
                title: chat.title,
                page_url: chat.page_url,
                lastMessage,
                lastUpdated,
            };
        })
    );

    res.status(200).json({ chats: chatList });
});

// Get Chat Messages Route
chatRouter.get('/:chat_id/messages', authenticate, async (req, res) => {
    const chatId = req.params.chat_id;
    const currentUserEmail = req.user.email;

    console.log(`Fetching messages for chat ${chatId}`);

    try {
        // Retrieve the current user from the database
        const user = await User.getUserByEmail(currentUserEmail);
        if (!user) {
            console.warn(`User not found: ${currentUserEmail}`);
            return res.status(404).json({ error: 'User not found' });
        }

        // Retrieve the chat from the database
        const chat = await Chat.getChatById(chatId);
        if (!chat) {
            console.warn(`Chat not found: ${chatId}`);
            return res.status(404).json({ error: 'Chat not found' });
        }

        if (chat.user_id !== user.id) {
            console.warn(`Unauthorized access attempt by user ${currentUserEmail} for chat ${chatId}`);
            return res.status(403).json({ error: 'Unauthorized access' });
        }

        // Retrieve messages for the chat
        const messages = await Message.getMessagesByChat(chatId);
        messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        console.log(`Found ${messages.length} messages for chat ${chatId}`);

        const formattedMessages = messages.map((message) => ({
            sender: message.sender,
            text: message.text,
            time: message.timestamp,
        }));

        return res.status(200).json({ messages: formattedMessages });
    } catch (error) {
        console.error(`Error fetching messages for chat ${chatId}: ${error.message}`);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

// Send Message Route
chatRouter.post('/:chat_id/messages', authenticate, async (req, res) => {
    const chatId = req.params.chat_id;
    const { message: userMessage } = req.body;

    const currentUserEmail = req.user.email;

    console.log(`Received message for chat ${chatId} from user ${currentUserEmail}`);

    const user = await User.getUserByEmail(currentUserEmail);
    if (!user) {
        console.warn(`User not found: ${currentUserEmail}`);
        return res.status(404).json({ error: 'User not found' });
    }

    const chat = await Chat.getChatById(chatId);
    if (!chat) {
        console.warn(`Chat not found: ${chatId}`);
        return res.status(404).json({ error: 'Chat not found' });
    }

    if (chat.user_id !== user.id) {
        console.warn(`Unauthorized access attempt by user ${currentUserEmail} for chat ${chatId}`);
        return res.status(403).json({ error: 'Unauthorized access' });
    }

    await Message.addMessage(chatId, 'user', userMessage);
    console.log(`User message stored in chat ${chatId}: ${userMessage}`);
    
    const allMessages = await Message.getMessagesByChat(chatId);
    allMessages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    const conversationContext = allMessages
        .map((msg) => `${msg.sender}: ${msg.text}`)
        .join('\n');

    const resumeUrl = chat.resume_url;

    if (!resumeUrl) {
        throw new Error("Resume Url is required.");
    }

    const s3UrlPattern = /^https:\/\/([^\.]+)\.s3\.amazonaws\.com\/(.+)$/;
    const match = resumeUrl.match(s3UrlPattern);
    if (!match) {
    throw new Error("Invalid S3 URL format.");
    }
    
    const bucketName = match[1];
    const keyName = match[2];

    const resumeContent = await getTextFromS3(bucketName, keyName);

    const prompt = getPrompt(conversationContext, userMessage.trim(), resumeContent.trim())

    const responseText = await callChatGPT(prompt);

    if (!responseText || responseText === "") {
        console.error("Failed to call ChatGPT");
        return res.status(500).json({ error: 'Failed to call ChatGPT' });
    }

    // Save bot message to the database
    await Message.addMessage(chatId, 'bot', responseText);
    console.log(`Bot response stored in chat ${chatId}: ${responseText}`);

    // Return the new message to the client
    return res.status(201).json({
        message: {
            sender: 'bot',
            text: responseText,
            time: new Date().toISOString(),
        },
    });
});

export default chatRouter;
