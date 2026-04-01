const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const port = 3000;

// Enable CORS for all routes (for development)
app.use(cors());

// Your Naver API Credentials
const CLIENT_ID = 'KfgaSIkWNVGJ_YSZcffs';
const CLIENT_SECRET = 'CSYMZPGOdP';

// Route to fetch blog search results
app.get('/api/naver-blogs', async (req, res) => {
    try {
        const query = encodeURI('남양주 백병원 혈관클리닉');
        const api_url = `https://openapi.naver.com/v1/search/blog?query=${query}&display=3`; // Fetch top 3 results

        const response = await axios.get(api_url, {
            headers: {
                'X-Naver-Client-Id': CLIENT_ID,
                'X-Naver-Client-Secret': CLIENT_SECRET
            }
        });

        res.json(response.data);
    } catch (error) {
        console.error('Error fetching data from Naver API:', error);
        res.status(500).json({ error: 'Failed to fetch data' });
    }
});

app.listen(port, () => {
    console.log(`Naver API Proxy Server running at http://localhost:${port}`);
});
