function displayResults(data, mode) {
    const resultsDiv = document.getElementById(mode === 'practice' ? 'practiceResults' : 'results');
    const datasetType = document.getElementById('datasetSelection').value;
    const prefix = mode === 'practice' ? 'practice' : 'test';

    // Update prompt length display
    document.getElementById(`${prefix}LengthDisplay`).textContent = 
        `Prompt Length: ${data.metrics.prompt_length} chr`;

    // Hide all metric displays first
    document.getElementById(`${prefix}WordSortingMetrics`).classList.add('hidden');
    document.getElementById(`${prefix}LogicalDeductionMetrics`).classList.add('hidden');
    document.getElementById(`${prefix}CausalJudgementMetrics`).classList.add('hidden');

    const metrics = data.metrics;
    
    // Show appropriate metrics based on dataset type
    if (datasetType === 'word_sorting') {
        displayWordSortingMetrics(metrics, prefix);
    } else if (datasetType === 'logical_deduction') {
        displayLogicalDeductionMetrics(metrics, prefix);
    } else if (datasetType === 'causal_judgement') {
        displayCausalJudgementMetrics(metrics, prefix);
    }

    displayExamples(data.examples, prefix);
    resultsDiv.classList.remove('hidden');
}

function displayWordSortingMetrics(metrics, prefix) {
    document.getElementById(`${prefix}WordSortingMetrics`).classList.remove('hidden');
    document.getElementById(`${prefix}CombinedScore`).textContent = `${metrics.combined_score.toFixed(2)}%`;
    document.getElementById(`${prefix}Accuracy`).textContent = `${metrics.accuracy.toFixed(2)}%`;
    document.getElementById(`${prefix}WordAccuracy`).textContent = `${metrics.word_accuracy.toFixed(2)}%`;
    document.getElementById(`${prefix}WordOrderDistance`).textContent = metrics.word_order_distance.toFixed(2);
    document.getElementById(`${prefix}PromptEfficiency`).textContent = `${(metrics.efficiency_modifier * 100).toFixed(0)}%`;
}

function displayLogicalDeductionMetrics(metrics, prefix) {
    document.getElementById(`${prefix}LogicalDeductionMetrics`).classList.remove('hidden');
    document.getElementById(`${prefix}LogicalAccuracy`).textContent = `${metrics.accuracy.toFixed(2)}%`;
    document.getElementById(`${prefix}BaseAccuracy`).textContent = `${metrics.base_accuracy.toFixed(2)}%`;
    document.getElementById(`${prefix}LogicalEfficiency`).textContent = `${(metrics.efficiency_modifier * 100).toFixed(0)}%`;
}

function displayCausalJudgementMetrics(metrics, prefix) {
    document.getElementById(`${prefix}CausalJudgementMetrics`).classList.remove('hidden');
    document.getElementById(`${prefix}CausalAccuracy`).textContent = `${metrics.accuracy.toFixed(2)}%`;
    document.getElementById(`${prefix}CausalBaseAccuracy`).textContent = `${metrics.base_accuracy.toFixed(2)}%`;
    document.getElementById(`${prefix}CausalEfficiency`).textContent = `${(metrics.efficiency_modifier * 100).toFixed(0)}%`;
}

function displayExamples(examples, prefix) {
    const examplesDiv = document.getElementById(`${prefix}Examples`);
    examplesDiv.innerHTML = '';
    examples.forEach((example, index) => {
        const exampleDiv = document.createElement('div');
        const bgColor = example.is_correct ? 'bg-green-100' : 'bg-red-100';
        const borderColor = example.is_correct ? 'border-green-200' : 'border-red-200';
        exampleDiv.classList.add(bgColor, borderColor, 'p-4', 'rounded', 'mb-4', 'border');
        
        exampleDiv.innerHTML = createExampleHTML(example, index);
        examplesDiv.appendChild(exampleDiv);
    });
}

function createExampleHTML(example, index) {
    return `
        <div class="font-bold mb-2">Example ${index + 1}</div>
        <p class="mb-2"><strong>Input:</strong> ${example.input}</p>
        <p class="mb-2"><strong>Expected:</strong> ${example.expected}</p>
        <p class="mb-2"><strong>Model Output:</strong> ${example.raw_prediction}</p>
        <p class="mb-2"><strong>Processed Output:</strong> ${example.processed_prediction}</p>
        <p class="mb-2">
            <strong>Correct:</strong> 
            <span class="${example.is_correct ? 'text-green-700' : 'text-red-700'} font-bold">
                ${example.is_correct ? 'Yes ✓' : 'No ✗'}
            </span>
        </p>
        ${example.word_order_distance !== null ? 
            `<p><strong>Word Order Distance:</strong> ${example.word_order_distance.toFixed(2)}</p>` : 
            ''}
    `;
}