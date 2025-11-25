window.onload = async function() {
    const response = await fetch('http://localhost:3000/api/posts');
    const blogPosts = await response.json();
    const blogList = document.getElementById('blog-list');

    blogPosts.forEach(post => {
        const article = document.createElement('article');
        article.className = 'blog-post';
        article.innerHTML = `
            <h2><a href="blog-post.html?id=${post._id}">${post.title}</a></h2>
            <p class="date">${post.date}</p>
            <p class="excerpt">${post.excerpt} <a href="blog-post.html?id=${post._id}">Read more...</a></p>
        `;
        blogList.appendChild(article);
    });
};
