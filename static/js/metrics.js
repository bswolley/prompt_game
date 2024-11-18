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
    console.log('Raw metrics received:', metrics);
    
    const section = document.getElementById(`${prefix}CausalJudgementMetrics`);
    if (!section) {
        console.error('Causal judgment metrics section not found');
        return;
    }

    section.classList.remove('hidden');
    
    // Log the exact key we're looking for
    console.log(`Looking for metrics.final_score:`, metrics.final_score);
    
    const updates = {
        [`${prefix}CausalFinalScore`]: `${metrics.final_score?.toFixed(1)}%`,
        [`${prefix}CausalAccuracy`]: `${metrics.accuracy?.toFixed(1)}%`,
        [`${prefix}CausalBaseAccuracy`]: `${metrics.base_accuracy?.toFixed(1)}%`,
        [`${prefix}CausalEfficiency`]: `${metrics.efficiency?.toFixed(1)}%`
    };

    console.log('Updates to be made:', updates);

    Object.entries(updates).forEach(([id, value]) => {
        const element = document.getElementById(id);
        console.log(`Updating ${id} with value ${value}`);
        if (element) {
            element.textContent = value;
        } else {
            console.error(`Element not found: ${id}`);
        }
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
        let qualityClass, qualityText, bgColor, borderColor;

        // Quality assessment logic
        if (datasetType === 'text_summarization') {
            const similarityScore = example.scores?.similarity || 0;
            if (similarityScore >= 80) {
                qualityClass = 'text-green-700';
                qualityText = 'Well done ✓';
                bgColor = 'bg-green-100';
                borderColor = 'border-green-200';
            } else if (similarityScore >= 60) {
                qualityClass = 'text-yellow-600';
                qualityText = 'Could be improved ⚠️';
                bgColor = 'bg-yellow-100';
                borderColor = 'border-yellow-200';
            } else {
                qualityClass = 'text-red-700';
                qualityText = 'Needs improvement ✗';
                bgColor = 'bg-red-100';
                borderColor = 'border-red-200';
            }
        } else {
            qualityClass = example.is_correct ? 'text-green-700' : 'text-red-700';
            qualityText = example.is_correct ? 'Good ✓' : 'Needs Improvement ✗';
            bgColor = example.is_correct ? 'bg-green-100' : 'bg-red-100';
            borderColor = example.is_correct ? 'border-green-200' : 'border-red-200';
        }

        // Apply classes to example div
        exampleDiv.classList.add(bgColor, borderColor, 'p-4', 'rounded', 'mb-4', 'border');

        // Base content
        let content = `
            <div class="font-bold mb-2">Example ${index + 1}</div>
            <p class="mb-2"><strong>Input:</strong> ${example.input}</p>
            <p class="mb-2"><strong>Expected:</strong> ${example.expected}</p>
            <p class="mb-2"><strong>Model Output:</strong> ${example.raw_prediction}</p>
        `;

        // Add processed output for word sorting and causal judgment
        if (datasetType === 'word_sorting' || datasetType === 'causal_judgement') {
            content += `<p class="mb-2"><strong>Processed Output:</strong> ${example.processed_prediction}</p>`;
        }

        // Add scores section based on dataset type
        if (datasetType === 'text_summarization') {
            content += `
                <div class="mt-2">
                    <strong>Scores:</strong>
                    <ul class="list-none space-y-1">
                        <li>• Final Score: ${example.scores.similarity}%</li>
                        <li>• Length Penalty: ${example.scores.length_penalty}%</li>
                        <li>• Actual Length: ${example.actual_length}</li>
                        <li>• Expected Length: ${example.expected_length}</li>
                    </ul>
                </div>
            `;
        } else if (datasetType === 'word_sorting') {
            content += `
                <div class="mt-2">
                    <strong>Scores:</strong>
                    <ul class="list-none space-y-1">
                        <li>• Final Score: ${example.scores.final_score}%</li>
                        <li>• Word Accuracy: ${example.scores.word_accuracy}%</li>
                        <li>• Word Order Distance: ${example.scores.word_order_distance}</li>
                        <li>• Efficiency: ${example.scores.efficiency}%</li>
                    </ul>
                </div>
            `;
        } else if (datasetType === 'causal_judgement') {
            content += `
                <div class="mt-2">
                    <strong>Scores:</strong>
                    <ul class="list-none space-y-1">
                        <li>• Final Score: ${example.scores.final_score}%</li>
                        <li>• Base Accuracy: ${example.scores.base_accuracy}%</li>
                        <li>• Efficiency: ${example.scores.efficiency}%</li>
                    </ul>
                </div>
            `;
        }

        // Add quality assessment
        content += `
            <p class="mb-2">
                <strong>Quality:</strong> 
                <span class="${qualityClass} font-bold">
                    ${qualityText}
                </span>
            </p>
        `;

        exampleDiv.innerHTML = content;
        examplesDiv.appendChild(exampleDiv);
    });

    examplesDiv.classList.remove('hidden');
}
