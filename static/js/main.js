// Global variables
let lastPrompt = '';
let datasetConfig = null;

// Function to fetch dataset configuration
async function fetchDatasetConfig() {
    try {
        const response = await fetch('/config/datasets.json');
        datasetConfig = await response.json();
    } catch (error) {
        console.error('Error loading dataset configuration:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    await fetchDatasetConfig();
    updateCharCount('practicePrompt', 'practiceCharCount');
    updateCharCount('systemPrompt', 'testCharCount');
    updateInstructions();
});

// Function to update dataset-specific instructions and examples
function updateInstructions() {
    const selectedDataset = document.getElementById('datasetSelection').value;
    const datasetInstructionsDiv = document.getElementById('datasetInstructions');
    const specificInstructions = document.getElementById('specificInstructions');
    const exampleDiv = document.getElementById('exampleDiv');
    const practiceInfo = document.getElementById('practiceInfo');

    // Clear previous prompts and results
    document.getElementById('practicePrompt').value = '';
    document.getElementById('systemPrompt').value = '';
    document.getElementById('practiceResults').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    
    // Reset character counters
    updateCharCount('practicePrompt', 'practiceCharCount');
    updateCharCount('systemPrompt', 'testCharCount');

    if (!selectedDataset || !datasetConfig || !datasetConfig[selectedDataset]) {
        datasetInstructionsDiv.classList.add('hidden');
        practiceInfo.textContent = '';
        return;
    }

    // Get dataset configuration
    const config = datasetConfig[selectedDataset];

    // Populate instructions
    datasetInstructionsDiv.classList.remove('hidden');
    specificInstructions.innerHTML = `
        <strong>Description:</strong> ${config.description}<br><br>
        <strong>Instructions:</strong><br>
        ${config.instructions.map(instruction => `- ${instruction}<br>`).join('')}
    `;

    // Display example if available
    if (config.example) {
        exampleDiv.innerHTML = `
            <strong>Example:</strong><br>
            <div class="bg-gray-100 p-4 rounded mt-2">
                <strong>Input:</strong> ${config.example.input}<br>
                <strong>Output:</strong> ${config.example.output}
            </div>
        `;
        exampleDiv.classList.remove('hidden');
    } else {
        exampleDiv.classList.add('hidden');
    }

    // Set practice mode information
    practiceInfo.textContent = config.practice_mode_info || '';
}


async function runPractice() {
    const systemPrompt = document.getElementById('practicePrompt').value;
    const datasetType = document.getElementById('datasetSelection').value;

    if (!datasetType) {
        alert('Please select a dataset type');
        return;
    }
    if (!systemPrompt) {
        alert('Please enter a prompt');
        return;
    }

    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('practiceResults').classList.add('hidden');

    try {
        const response = await fetch('/api/pretest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                system_prompt: systemPrompt,
                show_details: true,
                dataset_type: datasetType
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            displayResults(data, 'practice');
            lastPrompt = systemPrompt;
        } else {
            alert(data.error || 'Error running practice round');
        }
    } catch (error) {
        console.error("Error:", error);
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

async function testPrompt() {
    const systemPrompt = document.getElementById('systemPrompt').value;
    const numExamples = parseInt(document.getElementById('numExamples').value) || 10;
    const datasetType = document.getElementById('datasetSelection').value;

    if (!datasetType) {
        alert('Please select a dataset type');
        return;
    }
    if (!systemPrompt) {
        alert('Please enter a prompt');
        return;
    }

    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');

    try {
        const response = await fetch('/api/test_prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                system_prompt: systemPrompt,
                num_examples: numExamples,
                dataset_type: datasetType
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            displayResults(data, 'test');
        } else {
            alert(data.error || 'Unknown error occurred');
        }
    } catch (error) {
        console.error("Error:", error);
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}