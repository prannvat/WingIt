const newsContainer = document.getElementById('news-container');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const categoryItems = document.querySelectorAll('nav ul li');

let page = 1;
const pageSize = 100;
let currentQuery = '';
let currentCategory = '';

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

        articleElement.innerHTML = `
            ${article.urlToImage ? `<img src="${article.urlToImage}" alt="${article.title}">` : ''}
            <div class="article-content">
                <h2 class="article-title">${article.title}</h2>
                <p class="article-description">${article.description || 'No description available.'}</p>
                <div class="article-meta">
                    <span>${article.source.name} • ${formatDate(article.publishedAt)}</span>
                    <a href="#" class="read-more" data-url="${article.url}">Read more</a>
                </div>
            </div>
        `;

        articleElement.querySelector('.read-more').addEventListener('click', (event) => {
            event.preventDefault();
            const articleUrl = event.target.getAttribute('data-url');
            window.location.href = `/article?url=${encodeURIComponent(articleUrl)}`;
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
        'entertainment': 'entertainment'
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