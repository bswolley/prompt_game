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

async function testPrompt() {
    const name = document.getElementById('name').value;
    const systemPrompt = document.getElementById('systemPrompt').value;
    const datasetType = document.getElementById('datasetSelection').value;
    const numExamples = parseInt(document.getElementById('numExamples').value);
    
    if (!name) {
        alert('Please enter your name');
        return;
    }
    
    if (!systemPrompt) {
        alert('Please enter a system prompt');
        return;
    }

    // Get loading and results elements
    const loadingElement = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    
    // Show loading, hide previous results
    if (loadingElement) loadingElement.classList.remove('hidden');
    if (resultsDiv) resultsDiv.classList.add('hidden');

    let targetLanguage = null;
    if (datasetType === 'translation_task') {
        targetLanguage = document.getElementById('languageSelectionDropdown').value;
        if (!targetLanguage) {
            alert('Please select a target language in the practice section first');
            return;
        }
    }

    try {
        console.log('Sending test request:', {
            name,
            system_prompt: systemPrompt,
            dataset_type: datasetType,
            num_examples: numExamples,
            target_language: targetLanguage
        });

        const response = await fetch('/api/test_prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                system_prompt: systemPrompt,
                dataset_type: datasetType,
                num_examples: numExamples,
                target_language: targetLanguage
            })
        });

        const responseData = await response.json();
        console.log('Server response:', responseData);

        if (response.ok) {
            // Hide loading, show results
            if (loadingElement) loadingElement.classList.add('hidden');
            if (resultsDiv) resultsDiv.classList.remove('hidden');
            
            displayResults(responseData, 'test');
        } else {
            alert(responseData.error || 'Error running test');
        }
    } catch (error) {
        console.error("Error in test:", error);
        alert('Error: ' + error.message);
    } finally {
        // Make absolutely sure loading is hidden even if there's an error
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

function displayResults(data, mode) {
    console.log('Raw data received:', data, 'Mode:', mode);
    
    if (!data) {
        console.error('No data received in displayResults');
        return;
    }
    
    const resultsDiv = document.getElementById(mode === 'practice' ? 'practiceResults' : 'results');
    const datasetType = document.getElementById('datasetSelection').value;
    console.log('Found results div:', resultsDiv, 'for dataset type:', datasetType);

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

    // Update prompt length if available
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
        const examplesDiv = document.getElementById(`${mode}Examples`);
        if (!examplesDiv) {
            console.error('Examples div not found');
            return;
        }

        examplesDiv.innerHTML = '';

        data.examples.forEach((example, index) => {
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

            if (datasetType === 'translation_task' && example.explanation) {
                content += `
                    <div class="bg-blue-50 p-3 rounded mt-2 mb-2">
                        <p><strong>Evaluation:</strong> ${example.explanation}</p>
                    </div>
                `;
            }

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

    // Make sure results div is visible at the end
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