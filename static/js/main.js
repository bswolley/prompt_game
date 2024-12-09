// Global variables
let currentTurn = 1;
let previousOutputs = [];
let lastPrompt = '';
let datasetConfig = null;
let promptLengths = []; 


// Function to fetch dataset configuration
async function fetchDatasetConfig() {
    try {
        const response = await fetch('/config/datasets.json');
        datasetConfig = await response.json();
        console.log('Dataset config loaded:', datasetConfig);
    } catch (error) {
        console.error('Error loading dataset configuration:', error);
    }
}

function updateInstructions() {
    const selectedDataset = document.getElementById('datasetSelection').value;
    const languageSelection = document.getElementById('languageSelection');
    const exampleDiv = document.getElementById('exampleDiv');
    const datasetInstructionsDiv = document.getElementById('datasetInstructions');
    const specificInstructions = document.getElementById('specificInstructions');
    
    // Hide all special sections first
    languageSelection.classList.add('hidden');
    exampleDiv.classList.add('hidden');
    
    // Show instructions div if dataset selected
    if (selectedDataset && datasetConfig) {
        datasetInstructionsDiv.classList.remove('hidden');
    } else {
        datasetInstructionsDiv.classList.add('hidden');
        return;
    }

    const dataset = datasetConfig[selectedDataset];
    if (!dataset) return;

    // Update instructions using the config data
    specificInstructions.innerHTML = `
        <strong>Description:</strong> ${dataset.description}<br><br>
        <strong>Instructions:</strong><br>
        ${dataset.instructions.map(i => `• ${i}`).join('<br>')}<br><br>
        <strong>Scoring:</strong> ${dataset.scoring}
    `;

    // Handle special cases
    if (selectedDataset === 'translation_task') {
        languageSelection.classList.remove('hidden');
        const example = dataset.example;
        document.getElementById('exampleInput').textContent = example.input;
        exampleDiv.classList.remove('hidden');
        updateExampleOutput();
    } else if (dataset.example) {
        document.getElementById('exampleInput').textContent = dataset.example.input;
        document.getElementById('exampleOutput').textContent = dataset.example.output;
        exampleDiv.classList.remove('hidden');
    }
}


function updateExampleOutput() {
    const selectedLanguage = document.getElementById('languageSelectionDropdown').value;
    const exampleOutput = document.getElementById('exampleOutput');
    const selectedDataset = document.getElementById('datasetSelection').value;
    
    if (datasetConfig && datasetConfig.translation_task) {
        const translations = datasetConfig.translation_task.example.translations;
        exampleOutput.textContent = selectedLanguage ? 
            translations[selectedLanguage] : 
            'Please select a language';
    }
}

function handleDatasetChange(dataset) {
    // Hide all special sections first
    const sections = [
        'languageSelection',
        'complexTransformationExample',
        'complexTransformationElements',
        'practiceResults'
    ];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.classList.add('hidden');
    });

    // Reset state for complex transformation
    if (dataset === 'complex_transformation') {
        currentTurn = 1;
        previousOutputs = [];
        
        // Show complex-specific elements
        document.getElementById('complexTransformationExample').classList.remove('hidden');
        document.getElementById('complexTransformationElements').classList.remove('hidden');
        
        // Update turn counter
        document.getElementById('turnCounter').textContent = '1';
        
        // Update button text
        document.getElementById('normalButton').classList.add('hidden');
        document.getElementById('complexButton').classList.remove('hidden');
        
        // Load complex practice example
        loadComplexPracticeExample();
    } else {
        // Show normal button for other tasks
        document.getElementById('normalButton').classList.remove('hidden');
        document.getElementById('complexButton').classList.add('hidden');
    }

    // Show language selection for translation task
    if (dataset === 'translation_task') {
        document.getElementById('languageSelection').classList.remove('hidden');
    }

    // Update instructions
    updateInstructions();

    // Clear any existing results
    const promptTextarea = document.getElementById('practicePrompt');
    if (promptTextarea) {
        promptTextarea.value = '';
        promptTextarea.placeholder = dataset === 'complex_transformation' ? 
            'Enter your prompt for turn 1' : 
            'Enter your system prompt for this specific task';
    }
    updateCharCount('practicePrompt', 'practiceCharCount');
}

async function loadComplexPracticeExample() {
    try {
        const response = await fetch('/api/complex_practice');
        const data = await response.json();

        if (data.examples?.length > 0) {
            const example = data.examples[0];
            document.getElementById('taskDescription').innerText = example.task_description;
            document.getElementById('referenceSolution').innerText = example.display_reference;
            
            // Show the example section
            document.getElementById('complexTransformationExample').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading complex practice example:', error);
    }
}

async function runPractice() {
    console.log('Starting practice round...');

    const systemPrompt = document.getElementById('practicePrompt').value; // User's current prompt
    const datasetType = document.getElementById('datasetSelection').value;

    if (!datasetType) {
        alert('Please select a dataset type');
        return;
    }
    if (!systemPrompt) {
        alert('Please enter a prompt');
        return;
    }

    const loadingElement = document.getElementById('loading');
    if (loadingElement) loadingElement.classList.remove('hidden'); // Show spinner

    try {
        const previousTurnOutput = currentTurn > 1 ? previousOutputs[currentTurn - 2] : null;

        // Log previous outputs for debugging
        console.log(`Turn ${currentTurn} Previous Output:`, previousTurnOutput);

        const requestBody = {
            system_prompt: systemPrompt,  // Turn 3 prompt
            dataset_type: datasetType,
            show_details: true,
            turn: currentTurn,
            previous_outputs: previousTurnOutput ? [previousTurnOutput] : [] // Pass Turn 2 output
        };

        console.log(`Turn ${currentTurn} Request Body:`, JSON.stringify(requestBody, null, 2));

        const response = await fetch('/api/pretest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const responseData = await response.json();

        console.log(`Turn ${currentTurn} Model Response:`, responseData);

        if (!response.ok) {
            throw new Error(responseData.error || 'Error running practice round');
        }

        // Save Turn 3 output properly
        const newOutput = responseData.examples[0].raw_prediction; // Extract Turn 3 output
        previousOutputs[currentTurn - 1] = newOutput; // Update Turn 3 slot in previousOutputs
        console.log(`Updated previousOutputs after Turn ${currentTurn}:`, previousOutputs);

        handleComplexResponse(responseData); // Process Turn 3 output for metrics
    } catch (error) {
        console.error("Error in practice round:", error);
        alert('Error: ' + error.message);
    } finally {
        if (loadingElement) loadingElement.classList.add('hidden'); // Hide spinner
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
    
    if (!resultsDiv) {
        console.error(`Results div not found for mode: ${mode}`);
        return;
    }

    // Hide all metric sections first
    const sections = [
        `${mode}WordSortingMetrics`,
        `${mode}LogicalDeductionMetrics`,
        `${mode}CausalJudgementMetrics`,
        `${mode}SummarizationMetrics`,
        `${mode}TranslationMetrics`,
        `${mode}ComplexTransformationMetrics`
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

    // Special handling for complex transformation
    if (datasetType === 'complex_transformation') {
        // Only show metrics if it's the final turn or early submission
        if (data.metrics && Object.keys(data.metrics).length > 0) {
            const metricsDiv = document.getElementById(`${mode}ComplexTransformationMetrics`);
            if (metricsDiv) {
                metricsDiv.classList.remove('hidden');
                // Update metrics display
                document.getElementById(`${mode}ComplexFinalScore`).textContent = 
                    `${data.metrics.final_score?.toFixed(1) || 0}%`;
                document.getElementById(`${mode}RuleAccuracy`).textContent = 
                    `${data.metrics.rule_accuracy?.toFixed(1) || 0}`;
                document.getElementById(`${mode}TransformComplete`).textContent = 
                    `${data.metrics.completeness?.toFixed(1) || 0}`;
                document.getElementById(`${mode}FormatScore`).textContent = 
                    `${data.metrics.format_score?.toFixed(1) || 0}`;
            }

            // Update examples section
            if (data.examples && data.examples.length > 0) {
                const examplesDiv = document.getElementById(`${mode}Examples`);
                if (examplesDiv) {
                    examplesDiv.innerHTML = '';
                    data.examples.forEach((example, index) => {
                        const exampleDiv = document.createElement('div');
                        exampleDiv.className = 'bg-white p-4 rounded shadow mb-4';
                        exampleDiv.innerHTML = `
                            <div class="space-y-2">
                                <p><strong>Task:</strong> ${example.task_description}</p>
                                <p><strong>Reference Solution:</strong> ${example.reference_solution}</p>
                                <p><strong>Model Output:</strong> ${example.raw_prediction || ''}</p>
                                ${example.explanation ? `
                                <div class="bg-blue-50 p-3 rounded mt-2 mb-2">
                                    <p><strong>Evaluation Details:</strong> ${example.explanation}</p>
                                </div>` : ''}
                            </div>
                        `;
                        examplesDiv.appendChild(exampleDiv);
                    });
                    examplesDiv.classList.remove('hidden');
                }
            }
        }
        return;
    }

    // Handle other dataset types
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
        displayExamples(data.examples, mode, datasetType);
    }

    resultsDiv.classList.remove('hidden');
}


function handleComplexResponse(data) {
    console.log("Processing complex response for turn:", currentTurn, data);
    
    if (!data?.examples?.[0]) {
        console.error('Invalid response data:', data);
        return;
    }

    // Get the new output from THIS turn's response
    const newOutput = data.examples[0].raw_prediction;
    if (!newOutput) {
        console.error('Empty output in response');
        return;
    }

    // Store prompt length
    const currentPrompt = document.getElementById('practicePrompt').value;
    promptLengths[currentTurn - 1] = currentPrompt.length;

    // Store this turn's NEW output at the correct index
    console.log(`Storing NEW output for turn ${currentTurn}:`, newOutput);
    previousOutputs[currentTurn - 1] = newOutput;
    console.log('Updated previousOutputs array:', previousOutputs);

    // Handle final turn
    if (currentTurn === 3) {
        // Calculate total prompt length
        const totalPromptLength = promptLengths.reduce((sum, length) => sum + length, 0);
        
        // Update prompt length display
        const promptLengthElement = document.getElementById('practicePromptLengthChars');
        if (promptLengthElement) {
            promptLengthElement.textContent = `${totalPromptLength} chars`;
        }

        // Hide prompt input
        const promptInputSection = document.getElementById('promptInputSection');
        if (promptInputSection) {
            promptInputSection.style.display = 'none';
        }

        // Show results and update metrics
        const resultsDiv = document.getElementById('practiceResults');
        const metricsDiv = document.getElementById('practiceComplexTransformationMetrics');
        if (resultsDiv) resultsDiv.classList.remove('hidden');
        if (metricsDiv) metricsDiv.classList.remove('hidden');

        // Update metrics with final turn results
        if (data.metrics) {
            console.log("Updating final metrics:", data.metrics);
            const metrics = {
                'practiceComplexFinalScore': data.metrics.final_score,
                'practiceRuleAccuracy': data.metrics.rule_accuracy,
                'practiceTransformComplete': data.metrics.completeness,
                'practiceFormatScore': data.metrics.format_score,
                'practiceComplexEfficiency': data.metrics.efficiency
            };

            Object.entries(metrics).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    const formattedValue = value?.toFixed(1) || '0';
                    element.textContent = id === 'practiceComplexEfficiency' ? 
                        `${formattedValue}%` : formattedValue;
                }
            });
        }

        // Update examples with final output
        const examplesDiv = document.getElementById('practiceExamples');
        if (examplesDiv && data.examples) {
            examplesDiv.innerHTML = '';
            data.examples.forEach((example) => {
                const exampleDiv = document.createElement('div');
                exampleDiv.className = 'bg-white p-4 rounded shadow mb-4';
                exampleDiv.innerHTML = `
                    <div class="space-y-2">
                        <p><strong>Task:</strong> ${example.task_description}</p>
                        <p><strong>Reference Solution:</strong> ${example.reference_solution}</p>
                        <p><strong>Model Output:</strong> ${newOutput}</p>
                        ${example.explanation ? `
                        <div class="bg-blue-50 p-3 rounded mt-2 mb-2">
                            <p><strong>Evaluation Details:</strong> ${example.explanation}</p>
                        </div>` : ''}
                    </div>
                `;
                examplesDiv.appendChild(exampleDiv);
            });
            examplesDiv.classList.remove('hidden');
        }
    } else {
        // Move to next turn
        currentTurn++;
        clearPromptInput();
    }

    // Update output history display with all completed turns
    const previousOutputSection = document.getElementById('previousOutputSection');
    const outputHistory = document.getElementById('outputHistory');
    if (previousOutputSection && outputHistory) {
        previousOutputSection.classList.remove('hidden');
        
        const outputHistoryHtml = previousOutputs
            .slice(0, currentTurn)
            .map((turnOutput, index) => {
                if (!turnOutput) return '';
                return `
                    <div class="mb-4">
                        <div class="text-sm font-medium mb-1">Turn ${index + 1}</div>
                        <div class="bg-gray-50 p-2 rounded">${turnOutput}</div>
                    </div>
                `;
            })
            .filter(html => html !== '')
            .join('');
        
        outputHistory.innerHTML = outputHistoryHtml;
    }

    // Update turn counter
    const turnCounter = document.getElementById('turnCounter');
    if (turnCounter) {
        turnCounter.textContent = currentTurn;
    }
}

// 2. Add a new helper function for metrics parsing
function parseComplexMetrics(rawMetrics) {
    if (!rawMetrics) return null;
    
    try {
        return {
            final_score: parseFloat(rawMetrics.final_score) || 0,
            rule_accuracy: parseFloat(rawMetrics.rule_accuracy) || 0,
            completeness: parseFloat(rawMetrics.completeness) || 0,
            format_score: parseFloat(rawMetrics.format_score) || 0,
            efficiency: parseFloat(rawMetrics.efficiency) || 100
        };
    } catch (error) {
        console.error('Error parsing metrics:', error);
        return null;
    }
}

function updateComplexUI() {
    console.log("Updating complex UI, turn:", currentTurn);
    console.log("Previous outputs:", previousOutputs);

    // Update output history
    const previousOutputSection = document.getElementById('previousOutputSection');
    const outputHistory = document.getElementById('outputHistory');
    if (previousOutputSection && outputHistory && previousOutputs.length > 0) {
        previousOutputSection.classList.remove('hidden');
        // Get unique outputs
        const uniqueOutputs = [...new Set(previousOutputs)];
        console.log("Unique outputs:", uniqueOutputs);
        outputHistory.innerHTML = uniqueOutputs.map((output, index) => `
            <div class="mb-4">
                <div class="text-sm font-medium mb-1">Turn ${index + 1}</div>
                <div class="bg-gray-50 p-2 rounded">${output}</div>
            </div>
        `).join('');
    }

    // Don't show current output on turn 3
    const currentOutputSection = document.getElementById('currentOutputSection');
    const currentOutput = document.getElementById('currentOutput');
    if (currentOutputSection && currentOutput) {
        if (currentTurn === 3) {
            currentOutputSection.classList.add('hidden');
        } else {
            currentOutputSection.classList.remove('hidden');
            currentOutput.textContent = previousOutputs[previousOutputs.length - 1];
        }
    }

    // Update turn counter
    const turnCounter = document.getElementById('turnCounter');
    if (turnCounter) {
        turnCounter.textContent = currentTurn;
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
    
    const updates = {
        [`${prefix}CausalFinalScore`]: `${metrics.final_score?.toFixed(1)}%`,
        [`${prefix}CausalAccuracy`]: `${metrics.accuracy?.toFixed(1)}%`,
        [`${prefix}CausalBaseAccuracy`]: `${metrics.base_accuracy?.toFixed(1)}%`,
        [`${prefix}CausalEfficiency`]: `${metrics.efficiency?.toFixed(1)}%`
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
        [`${prefix}SummaryPromptEfficiency`]: `${metrics.prompt_efficiency}%`,
        [`${prefix}ActualLength`]: metrics.average_actual_length_chars,
        [`${prefix}PromptLengthChars`]: `${metrics.prompt_length_chars} chars`
    };

    Object.entries(updates).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        } else {
            console.error(`Element not found: ${id}, value would have been: ${value}`);
        }
    });
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
            [qualityClass, qualityText, bgColor, borderColor] = getQualityIndicators(similarityScore);
        } else {
            [qualityClass, qualityText, bgColor, borderColor] = example.is_correct ? 
                ['text-green-700', 'Good ✓', 'bg-green-100', 'border-green-200'] : 
                ['text-red-700', 'Needs Improvement ✗', 'bg-red-100', 'border-red-200'];
        }

        exampleDiv.classList.add(bgColor, borderColor, 'p-4', 'rounded', 'mb-4', 'border');

        let content = `
            <div class="font-bold mb-2">Example ${index + 1}</div>
            <div class="space-y-2">
                <p><strong>Input:</strong> ${example.input}</p>
                <p><strong>Expected:</strong> ${example.expected}</p>
                <p><strong>Model Output:</strong> ${example.raw_prediction || example.model_output || 'No response'}</p>
        `;

        // Add scores section
        content += '<div class="mt-3"><strong>Scores:</strong><ul class="list-none space-y-1">';
        
        content += getScoresContent(datasetType, example);
        content += '</ul></div>';

        // Add quality indicator
        if (datasetType === 'translation_task' && example.explanation) {
            content += `
                <div class="mt-3">
                    <p>
                        <strong>Quality:</strong> 
                        <span class="${qualityClass} font-bold">${qualityText}</span>
                    </p>
                    <div class="bg-blue-50 p-3 rounded mt-2">
                        <p><strong>Quality Evaluation:</strong> ${example.explanation}</p>
                    </div>
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

function getQualityIndicators(score) {
    if (score >= 80) {
        return ['text-green-700', 'Well done ✓', 'bg-green-100', 'border-green-200'];
    } else if (score >= 60) {
        return ['text-yellow-600', 'Could be improved ⚠️', 'bg-yellow-100', 'border-yellow-200'];
    } else {
        return ['text-red-700', 'Needs improvement ✗', 'bg-red-100', 'border-red-200'];
    }
}

function getScoresContent(datasetType, example) {
    switch (datasetType) {
        case 'translation_task':
            return `
                <li>• Final Score: ${example.final_score?.toFixed(1) || 0}%</li>
                <li>• Semantic Score: ${example.semantic_score?.toFixed(1) || 0}%</li>
                <li>• Quality Score: ${example.quality_score?.toFixed(1) || 0}%</li>
                <li>• Efficiency: ${example.efficiency?.toFixed(1) || 0}%</li>
            `;
        case 'text_summarization':
            return `
                <li>• Final Score: ${example.scores.similarity}%</li>
                <li>• Length Penalty: ${example.scores.length_penalty}%</li>
                <li>• Actual Length: ${example.actual_length}</li>
                <li>• Expected Length: ${example.expected_length}</li>
            `;
        case 'word_sorting':
            return `
                <li>• Final Score: ${example.scores.final_score}%</li>
                <li>• Word Accuracy: ${example.scores.word_accuracy}%</li>
                <li>• Word Order Distance: ${example.scores.word_order_distance}</li>
                <li>• Efficiency: ${example.scores.efficiency}%</li>
            `;
        case 'causal_judgement':
            return `
                <li>• Final Score: ${example.scores.final_score}%</li>
                <li>• Base Accuracy: ${example.scores.base_accuracy}%</li>
                <li>• Efficiency: ${example.scores.efficiency}%</li>
            `;
        default:
            return '';
    }
}

// Helper Functions
function addScoringButton() {
    const submitScoringBtn = document.createElement('button');
    submitScoringBtn.className = 'bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 ml-2';
    submitScoringBtn.textContent = 'Submit Output for Scoring';
    submitScoringBtn.setAttribute('data-scoring-button', 'true');
    submitScoringBtn.onclick = () => submitForScoring('complex_transformation', previousOutputs);
    document.querySelector('button[onclick="runPractice()"]').parentNode.appendChild(submitScoringBtn);
}

function clearPromptInput() {
    const promptTextarea = document.getElementById('practicePrompt');
    if (promptTextarea) {
        promptTextarea.value = '';
        promptTextarea.placeholder = `Enter your prompt for turn ${currentTurn}. Previous output will be used as context.`;
    }
    const charCount = document.getElementById('practiceCharCount');
    if (charCount) {
        charCount.textContent = '0 characters';
    }
}

function updateCharCount(inputId, counterId) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    if (input && counter) {
        counter.textContent = `${input.value.length} characters`;
    }
}

function getLanguageSelection() {
    const languageDropdown = document.getElementById('languageSelectionDropdown');
    return languageDropdown ? languageDropdown.value : null;
}

function toggleExamples(mode) {
    const examplesDiv = document.getElementById(`${mode}Examples`);
    if (examplesDiv) {
        examplesDiv.classList.toggle('hidden');
    }
}
    
// Add a single event listener for DOMContentLoaded
document.addEventListener('DOMContentLoaded', async function () {
    try {
        await fetchDatasetConfig();
        updateCharCount('practicePrompt', 'practiceCharCount');
        
        // Handle dataset selection change
        const datasetSelect = document.getElementById('datasetSelection');
        if (datasetSelect) {
            handleDatasetChange(datasetSelect.value);
            datasetSelect.addEventListener('change', (e) => {
                handleDatasetChange(e.target.value);
                updateInstructions();
            });
        }
        
        // Add language selection change handler
        const languageSelect = document.getElementById('languageSelectionDropdown');
        if (languageSelect) {
            languageSelect.addEventListener('change', updateExampleOutput);
        }
        
        // Initial instructions update
        updateInstructions();
    } catch (error) {
        console.error("Error initializing application:", error);
    }
});