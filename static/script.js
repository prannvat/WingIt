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
    console.log('Fetching from URL:', url);
    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log('API Response:', data);
        return data.articles;
    } catch (error) {
        console.error('Error fetching news:', error);
        return [];
    }
}

function displayNews(articles, append = true) {
    if (!append) {
        newsContainer.innerHTML = '';
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
                if (viewingSaved) {
                    articleElement.remove();
                }
            } else {
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
        'upload': 'upload',
        'custom': 'custom',
        'saved': 'saved'
    };

    categoryItems.forEach(item => {
        item.addEventListener('click', async (e) => {
            const link = item.querySelector('a');
            if (link) {
                // Let the link handle the navigation
                return;
            }
            
            e.preventDefault();
            const category = item.getAttribute('data-category');
            
            categoryItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            page = 1;
            currentQuery = '';
            searchInput.value = '';

            if (category === 'upload') {
                window.location.href = '/upload';
                return;
            }
            
            if (category === 'custom') {
                window.location.href = '/settings';
                return;
            }

            if (category === 'saved') {
                viewingSaved = true;
                displaySavedArticles();
                return;
            }

            currentCategory = categoryMap[category];
            const articles = await fetchNews('', currentCategory);
            displayNews(articles, false);

            const oldSentinel = document.querySelector('.sentinel');
            if (oldSentinel) oldSentinel.remove();
            const sentinel = document.createElement('div');
            sentinel.className = 'sentinel';
            newsContainer.appendChild(sentinel);
            observer.observe(sentinel);
        });
    });
}

// function initializeCategories() {
//     const categoryMap = {
//         'home': '',
//         'world': 'general',
//         'business': 'business',
//         'technology': 'technology',
//         'entertainment': 'entertainment',
//         'custom': 'custom', // Added category for custom  
//         'saved': 'saved', // Add saved category
//     };

//     categoryItems.forEach(item => {
//         item.addEventListener('click', async () => {
//             console.log('Category clicked:', item.textContent.trim()); // Debug log
            
//             categoryItems.forEach(i => i.classList.remove('active'));
//             item.classList.add('active');

//             page = 1;
//             currentQuery = '';
//             searchInput.value = '';

//             const categoryText = item.textContent.trim().toLowerCase();
//             console.log('Category text:', categoryText); // Debug log
            
//             // Handle saved articles category
//             if (categoryText === 'saved') {
//                 viewingSaved = true;
//                 displaySavedArticles();
//                 return;
//             }
            
//             viewingSaved = false;

//             //Not going to take part in the gaslighting that js is a real language
//             //also wanted to reassign articles 21 lines down (it works liberal)
//             //Realistically JS is so abstracted I doubt this not being const really matters	
//             let articles = [];
//             if (categoryText === 'custom') {

//                 let categories = await getCustomCategories();
//                 let categoryKeysStrings = Object.keys(categories);
//                 let currentCategories = [];

//                 //Get all true categories
//                 for(let i = 0; i < categoryKeysStrings.length; i++) {
//                     category = categoryKeysStrings[i];
//                     if(categories[category]) {
//                         currentCategories.push(category);
//                     }
//                 }

//                 //Grab all articles
//                 let articlesByCategory = [];
//                 for(let i = 0; i < currentCategories.length; i++) {
//                     category = currentCategories[i];
//                     category = categoryMap[category];
//                     articlesByCategory.push(await fetchNews('', category));
//                 }

//                 //Get the length of the longest collection of articles
//                 let longestCategory = 0;
//                 for(let i = 0; i < articlesByCategory.length; i++) {
//                     if(articlesByCategory[i].length > longestCategory) {
//                         longestCategory = articlesByCategory[i].length
//                     }
//                 }

//                 //Then add them alternating to the feed so theres some variance in subject
//                 for(let i = 0; i < longestCategory; i++) {
//                     for(let j = 0; j < articlesByCategory.length; j++) {
//                         try {
//                             if(typeof(articlesByCategory[j][i]) !== "undefined") {
//                                 articles.push(articlesByCategory[j][i]);
//                                 console.log("pushed")
//                             }
//                         } catch {/*This is expected to fail often*/}
//                     }
//                 }
//             } else {
//                 //This is just the old code for most cases
//                 currentCategory = categoryMap[categoryText];
//                 console.log('Mapped category:', currentCategory); // Debug log

//                 articles = articles.concat(await fetchNews('', currentCategory));
//             }
//             displayNews(articles, false);

//             // Remove old sentinel if it exists
//             const oldSentinel = document.querySelector('.sentinel');
//             if (oldSentinel) {
//                 oldSentinel.remove();
//             }

//             const sentinel = document.createElement('div');
//             sentinel.className = 'sentinel';
//             newsContainer.appendChild(sentinel);
//             observer.observe(sentinel);
//         });
//     });
// }

// Function to display saved articles

function displaySavedArticles() {
    const savedArticles = getSavedArticles();
    newsContainer.innerHTML = '';
    
    if (savedArticles.length === 0) {
        newsContainer.innerHTML = '<div class="no-saved-articles">No saved articles. Browse news and click "Save" to add articles here.</div>';
        return;
    }
    
    displayNews(savedArticles, false);
}

// function initializeCategories() {
//     const categoryMap = {
//         'home': '',
//         'world': 'general',
//         'business': 'business',
//         'technology': 'technology',
//         'entertainment': 'entertainment',
//         'upload': 'upload',
//         'saved': 'saved'
//     };

//     if (window.location.pathname === '/news') {
//         categoryItems.forEach(item => {
//             item.addEventListener('click', async (e) => {
//                 e.preventDefault();
//                 const category = item.getAttribute('data-category');
                
//                 categoryItems.forEach(i => i.classList.remove('active'));
//                 item.classList.add('active');
                
//                 page = 1;
//                 currentQuery = '';
//                 searchInput.value = '';

//                 if (category === 'upload') {
//                     window.location.href = '/upload';
//                     return;
//                 }

//                 if (category === 'saved') {
//                     viewingSaved = true;
//                     displaySavedArticles();
//                     return;
//                 }

//                 currentCategory = categoryMap[category];
//                 const articles = await fetchNews('', currentCategory);
//                 displayNews(articles, false);

//                 const oldSentinel = document.querySelector('.sentinel');
//                 if (oldSentinel) oldSentinel.remove();
//                 const sentinel = document.createElement('div');
//                 sentinel.className = 'sentinel';
//                 newsContainer.appendChild(sentinel);
//                 observer.observe(sentinel);
//             });
//         });
//     }
// }

async function getCustomCategories() {
    let output = {
        business: false,
        technology: false,
        entertainment: false,
    }
    try {
        const response = await fetch('/news', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        });
        const data = await response.json();
        output.business = data.business;
        output.technology = data.technology;
        output.entertainment = data.entertainment;
    }
    catch (error) {
        alert("An error occured fetching custom settings " + error);
    }
    return output;
}


const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
        console.log('Loading more articles...');
        page++;
        fetchNews(currentQuery, currentCategory).then(articles => displayNews(articles, true));
    }
}, {
    rootMargin: '100px'
});

searchButton.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    if (query) {
        page = 1;
        currentQuery = query;
        currentCategory = '';
        categoryItems.forEach(item => item.classList.remove('active'));
        const articles = await fetchNews(query);
        displayNews(articles, false);

        const oldSentinel = document.querySelector('.sentinel');
        if (oldSentinel) oldSentinel.remove();
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

function init() {
    console.log('Initializing...');
    initializeCategories();

    if (window.location.pathname === '/news') {
        const urlParams = new URLSearchParams(window.location.search);
        const category = urlParams.get('category');
        if (category === 'saved') {
            viewingSaved = true;
            displaySavedArticles();
        } else {
            currentCategory = category || '';
            fetchNews('', currentCategory).then(articles => {
                displayNews(articles, false);
                const sentinel = document.createElement('div');
                sentinel.className = 'sentinel';
                newsContainer.appendChild(sentinel);
                observer.observe(sentinel);
            });
        }
    }
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



