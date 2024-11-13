// Global variables
let lastPrompt = '';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCharCount('practicePrompt', 'practiceCharCount');
    updateCharCount('systemPrompt', 'testCharCount');
    updateInstructions();
});

function updateInstructions() {
    const selectedDataset = document.getElementById('datasetSelection').value;
    const datasetInstructionsDiv = document.getElementById('datasetInstructions');
    const specificInstructions = document.getElementById('specificInstructions');
    document.getElementById('practiceResults').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('practicePrompt').value = '';
    document.getElementById('systemPrompt').value = '';
    const practiceInfo = document.getElementById('practiceInfo');
    practiceInfo.textContent = '';

    if (selectedDataset === 'word_sorting') {
        datasetInstructionsDiv.classList.remove('hidden');
        specificInstructions.innerHTML = 
            "For Word Sorting:<br><br>" +
            "- Create prompts that sort words in alphabetical order<br>" +
            "- Example input: 'cherry apple dragon baseball elephant'<br>" +
            "- Expected output: 'apple baseball cherry dragon elephant'<br><br>";
        practiceInfo.textContent = "Practice Mode uses 8-word lists. Full Test Mode uses 10-word lists.";
    } 
    else if (selectedDataset === 'logical_deduction') {
        datasetInstructionsDiv.classList.remove('hidden');
        specificInstructions.innerHTML = 
            "For Logical Deduction:<br><br>" +
            "- Create prompts that solve logical puzzles<br>" +
            "- Answer should be in format (A), (B), etc.<br>" +
            "- Practice Mode uses 5-object puzzles<br>" +
            "- Full Test Mode uses 3-object puzzles<br><br>";
        practiceInfo.textContent = "Practice Mode uses 5-object puzzles. Full Test Mode uses 3-object puzzles.";
    }
    else if (selectedDataset === 'causal_judgement') {
        datasetInstructionsDiv.classList.remove('hidden');
        specificInstructions.innerHTML = 
            "For Causal Judgement:<br><br>" +
            "- Create prompts that assess judgement situations<br>" +
            "- Answer should be in yes/no format<br>" +
            "- Practice Mode uses 10 fixed examples<br>" +
            "- Full Test Mode uses 10-100 examples from remaining dataset<br><br>";
        practiceInfo.textContent = "Practice Mode uses first 10 fixed examples. Full Test Mode uses random examples from remaining set.";
    } else {
        datasetInstructionsDiv.classList.add('hidden');
        practiceInfo.textContent = "";
    }
    
    // Reset character counters
    updateCharCount('practicePrompt', 'practiceCharCount');
    updateCharCount('systemPrompt', 'testCharCount');
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