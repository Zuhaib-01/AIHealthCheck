// This script is loaded on every page

document.addEventListener('DOMContentLoaded', () => {
    console.log("AI Symptom Checker page loaded successfully.");

    // Find the symptom form on the index page
    const symptomForm = document.getElementById('symptom-form');

    if (symptomForm) {
        symptomForm.addEventListener('submit', (event) => {
            // Prevent the form from actually submitting for now
            event.preventDefault();

            // Get the user's input
            const symptoms = document.getElementById('symptoms').value;
            const resultsDiv = document.getElementById('results');

            if (symptoms.trim() === '') {
                resultsDiv.innerHTML = '<p class="text-danger">Please enter your symptoms before submitting.</p>';
            } else {
                // Placeholder for AI analysis
                resultsDiv.innerHTML = '<p class="text-info">Analyzing your symptoms... (This is a placeholder - no actual AI call is being made).</p>';
                alert("This is a demonstration. In a real application, this would send your symptoms to an AI model for analysis.");
            }
        });
    }
});
