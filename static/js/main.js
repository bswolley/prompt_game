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

async function runPractice() {
    console.log('Starting practice round...');
    
    const systemPrompt = document.getElementById('practicePrompt').value;
    const datasetType = document.getElementById('datasetSelection').value;
    const targetLanguage = datasetType === 'translation_task' ? getLanguageSelection() : null;

    if (!datasetType) {
        alert('Please select a dataset type');
        return;
    }
    if (!systemPrompt) {
        alert('Please enter a prompt');
        return;
    }
    if (datasetType === 'translation_task' && !targetLanguage) {
        alert('Please select a language for the translation task');
        return;
    }

    const loadingElement = document.getElementById('loading');
    const practiceResultsElement = document.getElementById('practiceResults');
    
    if (loadingElement) loadingElement.classList.remove('hidden');
    if (practiceResultsElement) practiceResultsElement.classList.add('hidden');

    try {
        console.log('Sending request:', {
            system_prompt: systemPrompt,
            dataset_type: datasetType,
            target_language: targetLanguage
        });

        const response = await fetch('/api/pretest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                system_prompt: systemPrompt,
                show_details: true,
                dataset_type: datasetType,
                target_language: targetLanguage
            })
        });

        const responseData = await response.json();
        console.log('Server response:', responseData);

        // Log GROQ evaluations for translation tasks
        if (datasetType === 'translation_task' && responseData.examples) {
            responseData.examples.forEach((example, index) => {
                if (example.explanation) {
                    console.log(`Example ${index + 1} GROQ Evaluation:`, example.explanation);
                }
            });
        }

        if (response.ok) {
            displayResults(responseData, 'practice');
            lastPrompt = systemPrompt;
        } else {
            alert(responseData.error || 'Error running practice round');
        }
    } catch (error) {
        console.error("Error in practice round:", error);
        alert('Error: ' + error.message);
    } finally {
        if (loadingElement) loadingElement.classList.add('hidden');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    await fetchDatasetConfig();
    updateCharCount('practicePrompt', 'practiceCharCount');
    updateCharCount('systemPrompt', 'testCharCount');
    updateInstructions();
});

function updateInstructions() {
    const selectedDataset = document.getElementById('datasetSelection').value;
    const datasetInstructionsDiv = document.getElementById('datasetInstructions');
    const specificInstructions = document.getElementById('specificInstructions');
    const exampleDiv = document.getElementById('exampleDiv');
    const practiceInfo = document.getElementById('practiceInfo');
    const languageSelectionDiv = document.getElementById('languageSelection');

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
        languageSelectionDiv.classList.add('hidden');
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
        <br>
        <strong>Scoring:</strong> ${config.scoring}<br><br>
    `;

    // Display example if available
    if (config.example) {
        if (selectedDataset === 'translation_task') {
            exampleDiv.innerHTML = `
                <strong>Example:</strong><br>
                <div class="bg-gray-100 p-4 rounded mt-2">
                    <strong>Input:</strong> ${config.example.input}<br>
                    <strong>Output:</strong> <span id="exampleOutput">Please select a language</span>
                </div>
            `;
        } else {
            exampleDiv.innerHTML = `
                <strong>Example:</strong><br>
                <div class="bg-gray-100 p-4 rounded mt-2">
                    <strong>Input:</strong> ${config.example.input}<br>
                    <strong>Output:</strong> ${config.example.output}
                </div>
            `;
        }
        exampleDiv.classList.remove('hidden');
    } else {
        exampleDiv.classList.add('hidden');
    }

    // Set practice mode information
    practiceInfo.textContent = config.practice_mode_info || '';

    // Handle language selection
    if (selectedDataset === 'translation_task') {
        languageSelectionDiv.classList.remove('hidden');
        const languageDropdown = document.getElementById('languageSelectionDropdown');
        
        // Update example output when language changes
        languageDropdown.addEventListener('change', function() {
            const selectedLanguage = languageDropdown.value;
            const translations = config.example.translations;
            const exampleOutput = document.getElementById('exampleOutput');
            
            if (selectedLanguage && translations[selectedLanguage]) {
                exampleOutput.textContent = translations[selectedLanguage];
            } else {
                exampleOutput.textContent = 'Please select a language';
            }
        });
    } else {
        languageSelectionDiv.classList.add('hidden');
    }
}

function displayResults(responseData, mode) {
    console.log('Raw data received:', responseData, 'Mode:', mode);
    
    if (!responseData) {
        console.error('No response data received');
        return;
    }
    
    const resultsDiv = document.getElementById(`${mode}Results`);
    if (!resultsDiv) {
        console.error('Results div not found');
        return;
    }

    const datasetType = document.getElementById('datasetSelection').value;

    // Hide all metric sections first
    document.getElementById(`${mode}WordSortingMetrics`)?.classList.add('hidden');
    document.getElementById(`${mode}LogicalDeductionMetrics`)?.classList.add('hidden');
    document.getElementById(`${mode}CausalJudgementMetrics`)?.classList.add('hidden');
    document.getElementById(`${mode}SummarizationMetrics`)?.classList.add('hidden');
    document.getElementById(`${mode}TranslationMetrics`)?.classList.add('hidden');

    // Update prompt length if available
    if (responseData.metrics?.prompt_length !== undefined) {
        const promptLengthElement = document.getElementById(`${mode}PromptLengthChars`);
        if (promptLengthElement) {
            promptLengthElement.textContent = `${responseData.metrics.prompt_length} chars`;
        }
    }

    // Display appropriate metrics based on dataset type
    if (datasetType === 'word_sorting') {
        const section = document.getElementById(`${mode}WordSortingMetrics`);
        if (section) {
            section.classList.remove('hidden');
            
            const updates = {
                [`${mode}CombinedScore`]: `${responseData.metrics.combined_score}%`,
                [`${mode}Accuracy`]: `${responseData.metrics.accuracy}%`,
                [`${mode}WordAccuracy`]: `${responseData.metrics.word_accuracy}%`,
                [`${mode}WordOrderDistance`]: responseData.metrics.word_order_distance,
                [`${mode}PromptEfficiency`]: `${(responseData.metrics.efficiency_modifier * 100).toFixed(0)}%`
            };

            Object.entries(updates).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                }
            });
        }
    } else if (datasetType === 'logical_deduction') {
        const section = document.getElementById(`${mode}LogicalDeductionMetrics`);
        if (section) {
            section.classList.remove('hidden');
            
            const updates = {
                [`${mode}LogicalAccuracy`]: `${responseData.metrics.accuracy}%`,
                [`${mode}BaseAccuracy`]: `${responseData.metrics.base_accuracy}%`,
                [`${mode}LogicalEfficiency`]: `${(responseData.metrics.efficiency_modifier * 100).toFixed(0)}%`
            };

            Object.entries(updates).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                }
            });
        }
    } else if (datasetType === 'causal_judgement') {
        const section = document.getElementById(`${mode}CausalJudgementMetrics`);
        if (section) {
            section.classList.remove('hidden');
            
            const updates = {
                [`${mode}CausalFinalScore`]: `${responseData.metrics.final_score.toFixed(1)}%`,
                [`${mode}CausalAccuracy`]: `${responseData.metrics.accuracy.toFixed(1)}%`,
                [`${mode}CausalBaseAccuracy`]: `${responseData.metrics.base_accuracy.toFixed(1)}%`,
                [`${mode}CausalEfficiency`]: `${responseData.metrics.efficiency.toFixed(1)}%`
            };

            Object.entries(updates).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                }
            });
        }
    } else if (datasetType === 'text_summarization') {
        const section = document.getElementById(`${mode}SummarizationMetrics`);
        if (section) {
            section.classList.remove('hidden');
            
            const updates = {
                [`${mode}SummarizationScore`]: `${responseData.metrics.final_score}%`,
                [`${mode}SemanticSimilarity`]: `${responseData.metrics.similarity}%`,
                [`${mode}LengthPenalty`]: `${responseData.metrics.length_penalty_avg}%`,
                [`${mode}SummaryPromptEfficiency`]: `${responseData.metrics.prompt_efficiency}%`,
                [`${mode}ActualLength`]: responseData.metrics.average_actual_length_chars,
                [`${mode}PromptLengthChars`]: `${responseData.metrics.prompt_length_chars} chars`
            };

            Object.entries(updates).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                }
            });
        }
    } else if (datasetType === 'translation_task') {
        const section = document.getElementById(`${mode}TranslationMetrics`);
        if (section) {
            section.classList.remove('hidden');
        
            const updates = {
                [`${mode}TranslationFinalScore`]: `${responseData.metrics?.final_score?.toFixed(1) || 0}%`,
                [`${mode}TranslationSemanticScore`]: `${responseData.metrics?.semantic_similarity?.toFixed(1) || 0}%`,
                [`${mode}TranslationQualityScore`]: `${responseData.metrics?.language_quality?.toFixed(1) || 0}%`,
                [`${mode}TranslationEfficiency`]: `${responseData.metrics?.efficiency?.toFixed(1) || 0}%`
            };

            Object.entries(updates).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                }
            });
        }
    }

    // Display examples if they exist
    if (responseData.examples?.length > 0) {
        displayExamples(responseData.examples, mode, datasetType);
    }

    resultsDiv.classList.remove('hidden');
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

        let content = `
            <div class="font-bold mb-2">Example ${index + 1}</div>
            <div class="space-y-2">
                <p><strong>Input:</strong> ${example.input}</p>
                <p><strong>Expected:</strong> ${example.expected}</p>
                <p><strong>Model Output:</strong> ${example.raw_prediction || example.model_output || 'No response'}</p>
        `;

        // Add evaluation for translation task
        if (datasetType === 'translation_task' && example.explanation) {
            content += `
                <div class="bg-blue-50 p-3 rounded mt-2 mb-2">
                    <p><strong>Evaluation:</strong> ${example.explanation}</p>
                </div>
            `;
        }

        // Add scores section based on dataset type
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

        content += `
            </ul></div>
            <p class="mt-3">
                <strong>Quality:</strong> 
                <span class="${qualityClass} font-bold">${qualityText}</span>
            </p>
            </div>
        `;

        exampleDiv.innerHTML = content;
        examplesDiv.appendChild(exampleDiv);
    });

    examplesDiv.classList.remove('hidden');
}

function getLanguageSelection() {
    const languageDropdown = document.getElementById('languageSelectionDropdown');
    return languageDropdown ? languageDropdown.value : null;
}