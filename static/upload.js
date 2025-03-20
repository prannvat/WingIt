const uploadForm = document.getElementById('upload-form');
const uploadedArticleContainer = document.getElementById('uploaded-article');

// Function to save and retrieve articles from localStorage
function getSavedArticles() {
    const saved = localStorage.getItem('savedArticles');
    return saved ? JSON.parse(saved) : [];
}

function saveArticle(article) {
    const savedArticles = getSavedArticles();
    if (!savedArticles.some(a => a.url === article.url)) {
        savedArticles.push(article);
        localStorage.setItem('savedArticles', JSON.stringify(savedArticles));
        return true;
    }
    return false;
}

function removeArticle(articleUrl) {
    const savedArticles = getSavedArticles();
    const filtered = savedArticles.filter(a => a.url !== articleUrl);
    localStorage.setItem('savedArticles', JSON.stringify(filtered));
}

function isArticleSaved(articleUrl) {
    const savedArticles = getSavedArticles();
    return savedArticles.some(a => a.url === articleUrl);
}

async function fetchArticleContent(url) {
    try {
        const response = await fetch('/analyzeUpload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        return data;
    } catch (error) {
        console.error('Error fetching article content:', error);
        return null;
    }
}

function displayNews(articles, append = true, container = uploadedArticleContainer) {
    if (!append) {
        container.innerHTML = '';
    }

    articles.forEach(article => {
        const articleElement = document.createElement('div');
        articleElement.classList.add('article');
        
        const isSaved = isArticleSaved(article.url);
        const saveButtonText = isSaved ? 'Saved' : 'Save';
        const saveButtonClass = isSaved ? 'saved' : '';

        articleElement.innerHTML = `
            ${article.urlToImage ? `<img src="${article.urlToImage}" alt="${article.title}">` : ''}
            <div class="article-content">
                <h2 class="article-title">${article.title}</h2>
                <p class="article-description">${article.description || 'No description available.'}</p>
                <div class="article-meta">
                    <span>${article.source.name} • ${formatDate(article.publishedAt)}</span>
                    <div class="article-actions">
                        <a href="#" class="read-more" data-url="${article.url}">Read more</a>
                        <button class="save-article ${saveButtonClass}" data-url="${article.url}">${saveButtonText}</button>
                    </div>
                </div>
            </div>
        `;

        articleElement.querySelector('.read-more').addEventListener('click', (event) => {
            event.preventDefault();
            const articleUrl = event.target.getAttribute('data-url');
            window.location.href = `/article?url=${encodeURIComponent(articleUrl)}`;
        });
        
        articleElement.querySelector('.save-article').addEventListener('click', (event) => {
            event.preventDefault();
            const button = event.target;
            const articleUrl = button.getAttribute('data-url');
            
            if (button.classList.contains('saved')) {
                removeArticle(articleUrl);
                button.textContent = 'Save';
                button.classList.remove('saved');
            } else {
                const articleToSave = articles.find(a => a.url === articleUrl);
                if (articleToSave && saveArticle(articleToSave)) {
                    button.textContent = 'Saved';
                    button.classList.add('saved');
                }
            }
        });

        container.appendChild(articleElement);
    });
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function initUploadPage() {
    const categoryItems = document.querySelectorAll('nav ul li');
    
    // Handle sidebar navigation
    categoryItems.forEach(item => {
        const category = item.getAttribute('data-category');
        item.classList.toggle('active', category === 'upload');
        item.removeEventListener('click', item.onclick);
        const link = item.querySelector('a');
        link.addEventListener('click', (e) => {
            console.log(`Navigating to: ${link.getAttribute('href')}`);
        });
    });

    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(uploadForm);
            const articleUrl = formData.get('article-url');

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData,
                });
                const result = await response.json();

                if (result.success) {
                    // Fetch the article content
                    const article = await fetchArticleContent(result.article_url);
                    if (article) {
                        displayNews([article], false, uploadedArticleContainer);
                    } else {
                        uploadedArticleContainer.innerHTML = '<p>Error loading article.</p>';
                    }
                } else {
                    uploadedArticleContainer.innerHTML = `<p>Error: ${result.error}</p>`;
                }
            } catch (error) {
                console.error('Error submitting article:', error);
                uploadedArticleContainer.innerHTML = '<p>Error submitting article.</p>';
            }
        });
    }

    // Load the most recent article on page load
    if (uploadedArticleContainer) {
        fetch('/recent_article')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.article_url) {
                    fetchArticleContent(data.article_url).then(article => {
                        if (article) {
                            displayNews([article], false, uploadedArticleContainer);
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching recent article:', error);
            });
    }
}

// Initialize the upload page
initUploadPage();