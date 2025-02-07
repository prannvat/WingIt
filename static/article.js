// article.js
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const articleUrl = urlParams.get('url');

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

    // Calculate meter values and colors
    const sentimentValue = ((data.polarity + 1) / 2) * 100; // Convert -1...1 to 0...100
    const objectivityValue = (1 - data.subjectivity) * 100; // Convert to percentage

    analysisResult.innerHTML = `
        <h2>Analysis Results</h2>
        
        <div class="sentiment-container">
            <div class="sentiment-meter">
                <div class="meter-label">Sentiment Analysis</div>
                <div class="meter">
                    <div class="meter-value sentiment" 
                         style="width: ${sentimentValue}%"></div>
                </div>
                <div class="meter-scale">
                    <span>Negative</span>
                    <span>Neutral</span>
                    <span>Positive</span>
                </div>
            </div>

            <div class="sentiment-meter">
                <div class="meter-label">Objectivity Analysis</div>
                <div class="meter">
                    <div class="meter-value objectivity" 
                         style="width: ${objectivityValue}%"></div>
                </div>
                <div class="meter-scale">
                    <span>Subjective</span>
                    <span>Neutral</span>
                    <span>Objective</span>
                </div>
            </div>
        </div>

        <div class="analysis-explanation">
            <h3>Analysis Breakdown</h3>
            <p>Sentiment Score: ${data.polarity.toFixed(2)} - ${getSentimentDescription(data.polarity)}</p>
            <p>Objectivity Score: ${(1 - data.subjectivity).toFixed(2)} - ${getObjectivityDescription(data.subjectivity)}</p>
        </div>

        <div class="analysis-details">
            <div class="analysis-card">
                <h3>Key Findings</h3>
                <ul>
                    <li>Overall tone: ${getSentimentTone(data.polarity)}</li>
                    <li>Writing style: ${getWritingStyle(data.subjectivity)}</li>
                    <li>Confidence level: ${getConfidenceLevel(data.polarity, data.subjectivity)}</li>
                </ul>
            </div>
            <div class="analysis-card">
                <h3>Content Analysis</h3>
                <ul>
                    <li>Bias level: ${getBiasLevel(data.subjectivity)}</li>
                    <li>Expression type: ${getExpressionType(data.polarity)}</li>
                    <li>Reader impact: ${getReaderImpact(data.polarity, data.subjectivity)}</li>
                </ul>
            </div>
        </div>
    `;
}

// Helper functions for analysis descriptions
function getSentimentDescription(score) {
    if (score > 0.5) return "Strongly Positive";
    if (score > 0.1) return "Moderately Positive";
    if (score > -0.1) return "Neutral";
    if (score > -0.5) return "Moderately Negative";
    return "Strongly Negative";
}

function getObjectivityDescription(score) {
    if (score < 0.2) return "Highly Objective";
    if (score < 0.4) return "Mostly Objective";
    if (score < 0.6) return "Balanced";
    if (score < 0.8) return "Somewhat Subjective";
    return "Highly Subjective";
}

function getSentimentTone(polarity) {
    if (Math.abs(polarity) < 0.1) return "Neutral and balanced";
    if (polarity > 0) return "Positive and optimistic";
    return "Critical or cautionary";
}

function getWritingStyle(subjectivity) {
    if (subjectivity < 0.3) return "Fact-based reporting";
    if (subjectivity < 0.7) return "Balanced perspective";
    return "Opinion-driven content";
}

function getConfidenceLevel(polarity, subjectivity) {
    const strength = Math.abs(polarity) + Math.abs(1 - subjectivity);
    if (strength > 1.5) return "Very high";
    if (strength > 1.0) return "High";
    return "Moderate";
}

function getBiasLevel(subjectivity) {
    if (subjectivity < 0.3) return "Minimal bias detected";
    if (subjectivity < 0.6) return "Some bias present";
    return "Significant bias detected";
}

function getExpressionType(polarity) {
    if (Math.abs(polarity) < 0.2) return "Neutral expression";
    if (polarity > 0) return "Supportive language";
    return "Critical language";
}

function getReaderImpact(polarity, subjectivity) {
    if (subjectivity > 0.7) return "May influence reader opinion";
    if (Math.abs(polarity) > 0.5) return "Strong emotional impact";
    return "Informative and balanced";
}