import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import authRoutes from './routes/authRoutes.js';
import chatRoutes from './routes/chatRoutes.js';
import deployRoutes from './routes/deployRoutes.js';
import getSecrets from './utils/getSecrets.js';

// Create the Express application
const app = express();

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());

const secrets = await getSecrets();

// Define the home route
app.get('/', (req, res) => {
    res.send(
        `Express is running on host: ${secrets.NODE_RUN_HOST}, port: ${secrets.NODE_RUN_PORT}`
    );
});

app.get('/api/health', (req, res) => {
    res.json({ status: 'healthy' });
});

// Register routes
app.use('/api/auth', authRoutes);
app.use('/api/chats', chatRoutes);
app.use('/api/deploy', deployRoutes);

// Start the server
const port = secrets.NODE_RUN_PORT || 5000;
app.listen(port, secrets.NODE_RUN_HOST, () => {
    console.log(`Server running at http://${secrets.NODE_RUN_HOST}:${port}`);
});
