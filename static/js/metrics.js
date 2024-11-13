function displayResults(data, mode) {
    console.log('Raw data received:', data, 'Mode:', mode);
    
    const resultsDiv = document.getElementById(mode === 'practice' ? 'practiceResults' : 'results');
    const datasetType = document.getElementById('datasetSelection').value;
    const prefix = mode === 'practice' ? 'practice' : 'test';

    // Hide all metric displays first, with checks
    const sections = [
        `${prefix}WordSortingMetrics`,
        `${prefix}LogicalDeductionMetrics`,
        `${prefix}CausalJudgementMetrics`,
        `${prefix}SummarizationMetrics`
    ];

    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('hidden');
        } else {
            console.warn(`Element not found: ${sectionId}`);
        }
    });

    // Update prompt length display if available
    if (data.metrics?.prompt_length_chars !== undefined) {
        document.getElementById(`${prefix}PromptLengthChars`).textContent = 
            `Prompt Length: ${data.metrics.prompt_length_chars} chars`;
    }

    // Show appropriate metrics based on dataset type
    try {
        if (datasetType === 'word_sorting') {
            displayWordSortingMetrics(data.metrics, prefix);
        } else if (datasetType === 'logical_deduction') {
            displayLogicalDeductionMetrics(data.metrics, prefix);
        } else if (datasetType === 'causal_judgement') {
            displayCausalJudgementMetrics(data.metrics, prefix);
        } else if (datasetType === 'text_summarization') {
            displaySummarizationMetrics(data.metrics, prefix);
        }
    } catch (error) {
        console.error('Error displaying metrics:', error);
    }

    // Display examples if they exist
    if (data.examples?.length > 0) {
        try {
            displayExamples(data.examples, prefix, datasetType);
        } catch (error) {
            console.error('Error displaying examples:', error);
        }
    }

    if (resultsDiv) {
        resultsDiv.classList.remove('hidden');
    } else {
        console.warn(`Results div not found: ${mode}Results`);
    }
}


function displayWordSortingMetrics(metrics, prefix) {
    console.log('Displaying word sorting metrics:', metrics);
    
    const section = document.getElementById(`${prefix}WordSortingMetrics`);
    if (!section) {
        console.error('Word sorting metrics section not found');
        return;
    }

    section.classList.remove('hidden');

    const updates = {
        [`${prefix}CombinedScore`]: metrics.combined_score || '0%',
        [`${prefix}Accuracy`]: metrics.accuracy || '0%',
        [`${prefix}WordAccuracy`]: metrics.word_accuracy || '0%',
        [`${prefix}WordOrderDistance`]: metrics.word_order_distance !== undefined ? 
            metrics.word_order_distance.toFixed(2) : '0',
        [`${prefix}PromptEfficiency`]: `${((metrics.efficiency_modifier || 0) * 100).toFixed(0)}%`
    };

    Object.entries(updates).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        } else {
            console.error(`Element not found: ${id}`);
        }
    });
}

function displaySummarizationMetrics(metrics, prefix) {
    console.log("Displaying summarization metrics:", metrics);

    const section = document.getElementById(`${prefix}SummarizationMetrics`);
    if (!section) {
        console.error('Summarization metrics section not found');
        return;
    }
    section.classList.remove('hidden');

    const updates = {
        [`${prefix}SummarizationScore`]: `${metrics.final_score}%`,
        [`${prefix}SemanticSimilarity`]: `${metrics.similarity}%`,
        [`${prefix}LengthPenalty`]: `${metrics.length_penalty_avg}%`,
        [`${prefix}SummaryPromptEfficiency`]: `${metrics.prompt_efficiency}%`,  // Updated ID here
        [`${prefix}ActualLength`]: metrics.average_actual_length_chars,
        [`${prefix}PromptLengthChars`]: `${metrics.prompt_length_chars} chars`
    };

    // Debug log each update
    Object.entries(updates).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            console.log(`Updated ${id} to ${value}`);
        } else {
            console.error(`Element not found: ${id}, value would have been: ${value}`);
        }
    });
}



function displayLogicalDeductionMetrics(metrics, prefix) {
    console.log('Displaying logical deduction metrics:', metrics);
    
    const section = document.getElementById(`${prefix}LogicalDeductionMetrics`);
    if (!section) return;

    section.classList.remove('hidden');
    
    const updates = {
        [`${prefix}LogicalAccuracy`]: metrics.accuracy || '0%',
        [`${prefix}BaseAccuracy`]: metrics.base_accuracy || '0%',
        [`${prefix}LogicalEfficiency`]: `${((metrics.efficiency_modifier || 0) * 100).toFixed(0)}%`
    };

    Object.entries(updates).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    });
}

function displayCausalJudgementMetrics(metrics, prefix) {
    console.log('Displaying causal judgment metrics:', metrics);
    
    const section = document.getElementById(`${prefix}CausalJudgementMetrics`);
    if (!section) return;

    section.classList.remove('hidden');
    
    const updates = {
        [`${prefix}CausalAccuracy`]: metrics.accuracy || '0%',
        [`${prefix}CausalBaseAccuracy`]: metrics.base_accuracy || '0%',
        [`${prefix}CausalEfficiency`]: `${((metrics.efficiency_modifier || 0) * 100).toFixed(0)}%`
    };

    Object.entries(updates).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    });
}

function displayExamples(examples, prefix, datasetType) {
    console.log('Displaying examples:', examples);
    
    const examplesDiv = document.getElementById(`${prefix}Examples`);
    if (!examplesDiv) {
        console.error('Examples div not found');
        return;
    }

    examplesDiv.innerHTML = '';

    examples.forEach((example, index) => {
        const exampleDiv = document.createElement('div');
        const bgColor = example.is_correct ? 'bg-green-100' : 'bg-red-100';
        const borderColor = example.is_correct ? 'border-green-200' : 'border-red-200';
        exampleDiv.classList.add(bgColor, borderColor, 'p-4', 'rounded', 'mb-4', 'border');
        
        let content = `
            <div class="font-bold mb-2">Example ${index + 1}</div>
            <p class="mb-2"><strong>Input:</strong> ${example.input}</p>
            <p class="mb-2"><strong>Expected:</strong> ${example.expected}</p>
            <p class="mb-2"><strong>Model Output:</strong> ${example.raw_prediction}</p>
        `;

        // Only show Processed Output for word sorting
        if (datasetType === 'word_sorting') {
            content += `<p class="mb-2"><strong>Processed Output:</strong> ${example.processed_prediction}</p>`;
        }

        // Add dataset-specific metrics
        if (datasetType === 'word_sorting' && example.word_order_distance !== null) {
            content += `<p><strong>Word Order Distance:</strong> ${example.word_order_distance.toFixed(2)}</p>`;
        } else if (datasetType === 'text_summarization' && example.scores) {
            content += `
                <div class="mt-2">
                    <strong>Scores:</strong>
                    <ul class="list-inside list-disc">
                        <li>Similarity: ${example.scores.similarity}%</li>
                        <li>Length Penalty: ${example.scores.length_penalty}%</li>
                        <li>Actual Length: ${example.actual_length}</li>
                        <li>Expected Length: ${example.expected_length}</li>
                    </ul>
                </div>
            `;
        }

        content += `
            <p class="mb-2">
                <strong>Quality:</strong> 
                <span class="${example.is_correct ? 'text-green-700' : 'text-red-700'} font-bold">
                    ${example.is_correct ? 'Good ✓' : 'Needs Improvement ✗'}
                </span>
            </p>
        `;

        exampleDiv.innerHTML = content;
        examplesDiv.appendChild(exampleDiv);
    });

    examplesDiv.classList.remove('hidden');
}