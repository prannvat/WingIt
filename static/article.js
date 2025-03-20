document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const articleUrl = urlParams.get('url');

    // Checks for the back button to be clicked
    document.addEventListener('click', (event) => {
        if (event.target.closest('#back-button')) {
            window.history.back();
        }
    });

    if (articleUrl) {
        try {
            const analysisResponse = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: articleUrl })
            });

            const analysisData = await analysisResponse.json();
            console.log('Analysis Data:', analysisData); // Debug log
            displayArticleAndAnalysis(analysisData, articleUrl);
        } catch (error) {
            console.error('Error fetching article:', error);
        }
    }
});

function displayArticleAndAnalysis(data, articleUrl) {
    const articleContent = document.getElementById('article-content');
    const analysisResult = document.getElementById('analysis-result');

    // Display article content
    articleContent.innerHTML = `
        <h2>Article Content</h2>
        <div class="article-text">${data.content}</div>
        <a href="${articleUrl}" target="_blank" class="original-link">
            Read the full article here
        </a>
    `;

    // Display analysis results
    analysisResult.innerHTML = `
        <h2>Analysis Results</h2>
        <div class="analysis-section">
            <h3>Objectivity Analysis</h3>
            <ul>
                ${data.objectivity.map(item => `<li>${item[0]}: ${item[1]}</li>`).join('')}
            </ul>
        </div>
        <div class="analysis-section">
            <h3>Tone Analysis</h3>
            <ul>
                ${data.tone.map(item => `<li>${item[0]}: ${item[1]}</li>`).join('')}
            </ul>
        </div>
    `;
}