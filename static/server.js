const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/blog', { useNewUrlParser: true, useUnifiedTopology: true });

// Define a schema and model
const blogSchema = new mongoose.Schema({
    title: String,
    date: String,
    excerpt: String,
    content: String
});

const Blog = mongoose.model('Blog', blogSchema);

// Routes
app.get('/api/posts', async (req, res) => {
    const posts = await Blog.find();
    res.json(posts);
});

app.get('/api/posts/:id', async (req, res) => {
    const post = await Blog.findById(req.params.id);
    if (post) {
        res.json(post);
    } else {
        res.status(404).send('Post not found');
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
