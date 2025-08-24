const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});


// Forward /generate-plan requests to Python backend
const axios = require('axios');
app.post('/generate-plan', async (req, res) => {
    try {
        // Adjust the URL/port if your Python backend runs elsewhere
        const pyRes = await axios.post('http://localhost:5000/generate-plan', req.body);
        res.json(pyRes.data);
    } catch (err) {
        console.error('Error forwarding to Python backend:', err.message);
        res.status(500).json({ success: false, error: 'Python backend error', details: err.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});