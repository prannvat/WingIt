// Sample news headlines for preview
const previewHeadlines = [
    "Global Markets Show Strong Recovery in Q4",
    "New Breakthrough in Renewable Energy Technology",
    "Tech Giants Announce Collaborative AI Initiative"
];

// Animate preview cards
function createPreviewCards() {
    const previewCards = document.querySelector('.preview-cards');
    
    previewHeadlines.forEach((headline, index) => {
        const card = document.createElement('div');
        card.className = 'preview-card';
        card.style.animationDelay = `${index * 0.2}s`;
        card.textContent = headline;
        previewCards.appendChild(card);
    });
}

// Initialize landing page
document.addEventListener('DOMContentLoaded', () => {
    createPreviewCards();
});