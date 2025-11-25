window.onload = async function() {
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('id');

    const response = await fetch(`http://localhost:3000/api/posts/${postId}`);
    const post = await response.json();

    if (post) {
        document.getElementById('post-title').innerText = post.title;
        document.getElementById('post-date').innerText = post.date;
        document.getElementById('post-content').innerText = post.content;
    } else {
        document.getElementById('post-title').innerText = 'Post not found';
        document.getElementById('post-content').innerText = 'The blog post you are looking for does not exist.';
    }
};
