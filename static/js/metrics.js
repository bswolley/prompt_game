function displayResults(data, mode) {
    console.log('Raw data received:', data, 'Mode:', mode);
    
    if (!data) {
        console.error('No data received in displayResults');
        return;
    }
    
    const resultsDiv = document.getElementById(mode === 'practice' ? 'practiceResults' : 'results');
    const datasetType = document.getElementById('datasetSelection').value;

    if (!resultsDiv) {
        console.error(`Results div not found for mode: ${mode}`);
        return;
    }

    // Hide all metric displays first
    const sections = [
        `${mode}WordSortingMetrics`,
        `${mode}LogicalDeductionMetrics`,
        `${mode}CausalJudgementMetrics`,
        `${mode}SummarizationMetrics`,
        `${mode}TranslationMetrics`
    ];

    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('hidden');
        }
    });

    // Update prompt length display if available
    if (data.metrics?.prompt_length !== undefined) {
        const promptLengthElement = document.getElementById(`${mode}PromptLengthChars`);
        if (promptLengthElement) {
            promptLengthElement.textContent = `${data.metrics.prompt_length} chars`;
        }
    }

    // Display appropriate metrics based on dataset type
    try {
        if (datasetType === 'word_sorting') {
            displayWordSortingMetrics(data.metrics, mode);
        } else if (datasetType === 'logical_deduction') {
            displayLogicalDeductionMetrics(data.metrics, mode);
        } else if (datasetType === 'causal_judgement') {
            displayCausalJudgementMetrics(data.metrics, mode);
        } else if (datasetType === 'text_summarization') {
            displaySummarizationMetrics(data.metrics, mode);
        } else if (datasetType === 'translation_task') {
            displayTranslationMetrics(data.metrics, mode);
        }
    } catch (error) {
        console.error('Error displaying metrics:', error);
    }

    // Display examples if they exist
    if (data.examples?.length > 0) {
        try {
            displayExamples(data.examples, mode, datasetType);
        } catch (error) {
            console.error('Error displaying examples:', error);
        }
    }

    resultsDiv.classList.remove('hidden');
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
        if (datasetType === 'translation_task') {
            const finalScore = example.final_score || 0;
            if (finalScore >= 80) {
                qualityClass = 'text-green-700';
                qualityText = 'Well done ✓';
                bgColor = 'bg-green-100';
                borderColor = 'border-green-200';
            } else if (finalScore >= 60) {
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
        } else if (datasetType === 'text_summarization') {
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

        exampleDiv.classList.add(bgColor, borderColor, 'p-4', 'rounded', 'mb-4', 'border');

        // Build the content in the correct order
        let content = `
            <div class="font-bold mb-2">Example ${index + 1}</div>
            <div class="space-y-2">
                <p><strong>Input:</strong> ${example.input}</p>
                <p><strong>Expected:</strong> ${example.expected}</p>
                <p><strong>Model Output:</strong> ${example.raw_prediction || example.model_output || 'No response'}</p>
        `;

        // Add scores section
        content += '<div class="mt-3"><strong>Scores:</strong><ul class="list-none space-y-1">';
        
        if (datasetType === 'translation_task') {
            content += `
                <li>• Final Score: ${example.final_score?.toFixed(1) || 0}%</li>
                <li>• Semantic Score: ${example.semantic_score?.toFixed(1) || 0}%</li>
                <li>• Quality Score: ${example.quality_score?.toFixed(1) || 0}%</li>
                <li>• Efficiency: ${example.efficiency?.toFixed(1) || 0}%</li>
            `;
        } else if (datasetType === 'text_summarization') {
            content += `
                <li>• Final Score: ${example.scores.similarity}%</li>
                <li>• Length Penalty: ${example.scores.length_penalty}%</li>
                <li>• Actual Length: ${example.actual_length}</li>
                <li>• Expected Length: ${example.expected_length}</li>
            `;
        } else if (datasetType === 'word_sorting') {
            content += `
                <li>• Final Score: ${example.scores.final_score}%</li>
                <li>• Word Accuracy: ${example.scores.word_accuracy}%</li>
                <li>• Word Order Distance: ${example.scores.word_order_distance}</li>
                <li>• Efficiency: ${example.scores.efficiency}%</li>
            `;
        } else if (datasetType === 'causal_judgement') {
            content += `
                <li>• Final Score: ${example.scores.final_score}%</li>
                <li>• Base Accuracy: ${example.scores.base_accuracy}%</li>
                <li>• Efficiency: ${example.scores.efficiency}%</li>
            `;
        }
        content += '</ul></div>';

        // Add quality indicator and evaluation together at the end
        if (datasetType === 'translation_task') {
            content += `
                <div class="mt-3">
                    <p>
                        <strong>Quality:</strong> 
                        <span class="${qualityClass} font-bold">${qualityText}</span>
                    </p>
                    ${example.explanation ? `
                        <div class="bg-blue-50 p-3 rounded mt-2">
                            <p><strong>Quality Evaluation:</strong> ${example.explanation}</p>
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            content += `
                <p class="mt-3">
                    <strong>Quality:</strong> 
                    <span class="${qualityClass} font-bold">${qualityText}</span>
                </p>
            `;
        }

        content += '</div>';
        exampleDiv.innerHTML = content;
        examplesDiv.appendChild(exampleDiv);
    });

    examplesDiv.classList.remove('hidden');
}

function displayTranslationMetrics(metrics, prefix) {
    console.log('Displaying translation metrics:', metrics);
    
    const section = document.getElementById(`${prefix}TranslationMetrics`);
    if (!section) {
        console.error('Translation metrics section not found');
        return;
    }

    section.classList.remove('hidden');
    
    const updates = {
        [`${prefix}TranslationFinalScore`]: `${metrics?.final_score?.toFixed(1) || 0}%`,
        [`${prefix}TranslationSemanticScore`]: `${metrics?.semantic_similarity?.toFixed(1) || 0}%`,
        [`${prefix}TranslationQualityScore`]: `${metrics?.language_quality?.toFixed(1) || 0}%`,
        [`${prefix}TranslationEfficiency`]: `${metrics?.efficiency?.toFixed(1) || 0}%`
    };

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
 
function displayComplexTransformationMetrics(metrics, prefix) {
    console.log('Displaying complex transformation metrics:', metrics);
    
    const section = document.getElementById(`${prefix}ComplexTransformationMetrics`);
    if (!section) {
        console.error('Complex transformation metrics section not found');
        return;
    }

    section.classList.remove('hidden');
    
    const updates = {
        [`${prefix}ComplexFinalScore`]: `${metrics?.final_score?.toFixed(1) || 0}%`,
        [`${prefix}RuleAccuracy`]: `${metrics?.rule_accuracy?.toFixed(1) || 0}%`,
        [`${prefix}TransformComplete`]: `${metrics?.completeness?.toFixed(1) || 0}%`,
        [`${prefix}FormatScore`]: `${metrics?.format_adherence?.toFixed(1) || 0}%`,
        [`${prefix}ComplexEfficiency`]: `${metrics?.efficiency?.toFixed(1) || 0}%`
    };

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