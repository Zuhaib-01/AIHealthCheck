document.addEventListener('DOMContentLoaded', () => {
    const symptomForm = document.getElementById('symptom-form');
    const resultsDiv = document.getElementById('results');

    if (symptomForm) {
        symptomForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const symptomsSelect = document.getElementById('symptoms');
            const selectedSymptoms = Array.from(symptomsSelect.selectedOptions).map(option => option.value);
            const symptoms = selectedSymptoms.join(',');

            if (symptoms.trim() === '') {
                resultsDiv.innerHTML = '<p class="text-danger">Please select at least one symptom.</p>';
                return;
            }

            resultsDiv.innerHTML = '<p class="text-info">Analyzing your symptoms...</p>';

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symptoms: symptoms }),
                });

                const data = await response.json();

                if (response.ok) {
                    resultsDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h4 class="alert-heading">Preliminary Analysis</h4>
                            <p>Based on the symptoms provided, the model suggests the potential condition is: <strong>${data.prediction}</strong></p>
                            <hr>
                            <p class="mb-0"><strong>Disclaimer:</strong> This is an AI-generated prediction and not a medical diagnosis. Please consult a healthcare professional.</p>
                        </div>
                    `;
                } else {
                    resultsDiv.innerHTML = `<p class="text-danger">Error: ${data.error}</p>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<p class="text-danger">An error occurred while contacting the server. Please try again later.</p>`;
            }
        });
    }
});
