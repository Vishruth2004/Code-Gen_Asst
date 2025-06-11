const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const axios = require('axios');

const app = express();
const port = 5000;

// Increase the payload size limit
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));
app.use(cors());

app.post('/message', async (req, res) => {
  const { message, image } = req.body;

  try {
    const response = await axios.post('http://localhost:8000/process', { message, image });
    const reply = response.data.reply;
    res.json({ reply });
  } catch (error) {
    console.error('Error processing message:', error);
    res.status(500).json({ reply: 'There was an error processing your request.' });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
