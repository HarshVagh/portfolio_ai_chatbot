import express from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { User } from '../models/dynamodbModels.js';
import getSecrets from '../utils/getSecrets.js';

const authRouter = express.Router();
const secrets = await getSecrets();

const JWT_SECRET_KEY = secrets.JWT_SECRET_KEY;

// Signup Route
authRouter.post('/signup', async (req, res) => {
    try {
        console.log("Received signup request");
        const { name, email, password } = req.body;

        // Check if the email already exists in the database
        const existingUser = await User.getUserByEmail(email);
        if (existingUser) {
            console.warn(`Signup failed: Email ${email} already exists`);
            return res.status(409).json({ error: 'Email already exists' });
        }

        // Hash the password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Create a new user in the database
        const userId = await User.createUser(name, email, hashedPassword);

        console.log(`User ${email} signed up successfully with ID ${userId}`);

        // Generate a JWT token
        const accessToken = jwt.sign({ email }, JWT_SECRET_KEY, { expiresIn: '15d' });
        res.status(201).json({ token: accessToken });
    } catch (error) {
        console.error(`Error during signup: ${error.message}`);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Login Route
authRouter.post('/login', async (req, res) => {
    try {
        console.log("Received login request");
        const { email, password } = req.body;

        if (!email || typeof email !== 'string') {
            console.error(`Invalid email value: ${email} (type: ${typeof email})`);
            return res.status(400).json({ error: 'Invalid email' });
        }

        if (!password) {
            console.error("Password is missing");
            return res.status(400).json({ error: 'Password is required' });
        }

        // Retrieve the user by email from the database
        const user = await User.getUserByEmail(email);
        if (user && await bcrypt.compare(password, user.password)) {
            console.log(`User ${email} logged in successfully`);

            // Generate a JWT token
            const accessToken = jwt.sign({ email }, JWT_SECRET_KEY, { expiresIn: '15d' });
            return res.status(200).json({ token: accessToken });
        }

        console.warn(`Login failed for email ${email}`);
        res.status(401).json({ error: 'Invalid credentials' });
    } catch (error) {
        console.error(`Error during login: ${error.message}`);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get Current User Route
authRouter.get('/user', async (req, res) => {
    try {
        console.log("Fetching current user information");

        // Get the JWT token from the request header
        const token = req.headers.authorization?.split(' ')[1];
        if (!token) {
            return res.status(401).json({ error: 'Unauthorized' });
        }

        // Verify the JWT token
        const decoded = jwt.verify(token, JWT_SECRET_KEY);
        const currentUserEmail = decoded.email;

        // Retrieve the user by email from the database
        const user = await User.getUserByEmail(currentUserEmail);
        if (!user) {
            console.warn(`User not found: ${currentUserEmail}`);
            return res.status(404).json({ error: 'User not found' });
        }

        // Return the user's information
        const userInfo = {
            id: user.id,
            name: user.name,
            email: user.email,
        };

        console.log(`User information fetched: ${JSON.stringify(userInfo)}`);
        res.status(200).json({ user: userInfo });
    } catch (error) {
        console.error(`Error fetching user information: ${error.message}`);
        res.status(500).json({ error: 'An error occurred while fetching user information' });
    }
});

export default authRouter;
