const newsContainer = document.getElementById('news-container');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const categoryItems = document.querySelectorAll('nav ul li');

let page = 1;
const pageSize = 100;
let currentQuery = '';
let currentCategory = '';
let viewingSaved = false;

// Function to save and retrieve articles from localStorage
function getSavedArticles() {
    const saved = localStorage.getItem('savedArticles');
    return saved ? JSON.parse(saved) : [];
}

function saveArticle(article) {
    const savedArticles = getSavedArticles();
    // Check if article is already saved
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

async function fetchNews(query = '', category = '') {
    const newsApiKey = 'fe5b9311877b43be9a671f831da8dd74';
    const baseUrl = 'https://newsapi.org/v2/';
    const endpoint = query ? 'everything' : 'top-headlines';
    
    let queryParams;
    if (query) {
        queryParams = `q=${query}&pageSize=${pageSize}&page=${page}`;
    } else if (category && category !== 'home') {
        queryParams = `country=us&category=${category}&pageSize=${pageSize}&page=${page}`;
    } else {
        queryParams = `country=us&pageSize=${pageSize}&page=${page}`;
    }

    const url = `${baseUrl}${endpoint}?${queryParams}&apiKey=${newsApiKey}`;
    console.log('Fetching from URL:', url); // Debug log

    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log('API Response:', data); // Debug log
        return data.articles;
    } catch (error) {
        console.error('Error fetching news:', error);
        return [];
    }
}

function displayNews(articles, append = true) {
    console.log('Displaying articles:', articles); // Debug log
    
    if (!append) {
        newsContainer.innerHTML = '';
    }

    articles.forEach(article => {
        const articleElement = document.createElement('div');
        articleElement.classList.add('article');
        
        // Check if article is already saved
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
                // Remove from saved
                removeArticle(articleUrl);
                button.textContent = 'Save';
                button.classList.remove('saved');
                
                // If viewing saved articles, remove this article from view
                if (viewingSaved) {
                    articleElement.remove();
                }
            } else {
                // Find the article object by URL and save it
                const articleToSave = articles.find(a => a.url === articleUrl);
                if (articleToSave && saveArticle(articleToSave)) {
                    button.textContent = 'Saved';
                    button.classList.add('saved');
                }
            }
        });

        newsContainer.appendChild(articleElement);
    });
}

function initializeCategories() {
    const categoryMap = {
        'home': '',
        'world': 'general',
        'business': 'business',
        'technology': 'technology',
        'entertainment': 'entertainment',
        'saved': 'saved' // Add saved category
    };

    categoryItems.forEach(item => {
        item.addEventListener('click', async () => {
            console.log('Category clicked:', item.textContent.trim()); // Debug log
            
            categoryItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            page = 1;
            currentQuery = '';
            searchInput.value = '';

            const categoryText = item.textContent.trim().toLowerCase();
            console.log('Category text:', categoryText); // Debug log
            
            // Handle saved articles category
            if (categoryText === 'saved') {
                viewingSaved = true;
                displaySavedArticles();
                return;
            }
            
            viewingSaved = false;
            currentCategory = categoryMap[categoryText];
            console.log('Mapped category:', currentCategory); // Debug log

            const articles = await fetchNews('', currentCategory);
            displayNews(articles, false);

            // Remove old sentinel if it exists
            const oldSentinel = document.querySelector('.sentinel');
            if (oldSentinel) {
                oldSentinel.remove();
            }

            const sentinel = document.createElement('div');
            sentinel.className = 'sentinel';
            newsContainer.appendChild(sentinel);
            observer.observe(sentinel);
        });
    });
}

// Function to display saved articles
function displaySavedArticles() {
    const savedArticles = getSavedArticles();
    newsContainer.innerHTML = '';
    
    if (savedArticles.length === 0) {
        newsContainer.innerHTML = '<div class="no-saved-articles">No saved articles. Browse news and click "Save" to add articles here.</div>';
        return;
    }
    
    displayNews(savedArticles, false);
    
    // No need for infinite scroll with saved articles
    const oldSentinel = document.querySelector('.sentinel');
    if (oldSentinel) {
        oldSentinel.remove();
    }
}

const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
        console.log('Loading more articles...'); // Debug log
        page++;
        fetchNews(currentQuery, currentCategory).then(articles => displayNews(articles, true));
    }
}, {
    rootMargin: '100px'
});

searchButton.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    if (query) {
        console.log('Searching for:', query); // Debug log
        page = 1;
        currentQuery = query;
        currentCategory = '';
        categoryItems.forEach(item => item.classList.remove('active'));
        const articles = await fetchNews(query);
        displayNews(articles, false);

        // Reset sentinel
        const oldSentinel = document.querySelector('.sentinel');
        if (oldSentinel) {
            oldSentinel.remove();
        }
        const sentinel = document.createElement('div');
        sentinel.className = 'sentinel';
        newsContainer.appendChild(sentinel);
        observer.observe(sentinel);
    }
});

searchInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        searchButton.click();
    }
});

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Initial load
function init() {
    console.log('Initializing...'); // Debug log
    initializeCategories();
    fetchNews().then(articles => {
        displayNews(articles, false);
        const sentinel = document.createElement('div');
        sentinel.className = 'sentinel';
        newsContainer.appendChild(sentinel);
        observer.observe(sentinel);
    });
}

init();

// Toggle functionality for category filters
document.addEventListener('DOMContentLoaded', function() {
    const toggles = document.querySelectorAll('.category-toggles .toggle');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            // If the toggle is already active and it's not "home", just return
            if (this.classList.contains('active') && this.getAttribute('data-category') !== 'home') {
                return;
            }
            
            // Remove active class from all toggles
            toggles.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked toggle
            this.classList.add('active');
            
            // Here you would filter news content based on the selected category
            const category = this.getAttribute('data-category');
            console.log(`Category selected: ${category}`);
            
            // You can add code here to filter the news articles by category
            // For example:
            // filterArticlesByCategory(category);
        });
    });
    
    // Additional code for search functionality, article loading, etc.
    // would go here...
});