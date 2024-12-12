// Global variables
let currentTurn = 1;
let previousOutputs = [];
let lastPrompt = '';
let datasetConfig = null;
let promptLengths = []; 
let testCurrentTurn = 1;
let testPreviousOutputs = [];
let testPromptLengths = [];


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

function clearAllMetrics() {
    // All possible metric sections to clear
    const metricsToReset = {
        // Word Sorting
        'practiceCombinedScore': '-',
        'practiceAccuracy': '-',
        'practiceWordAccuracy': '-',
        'practiceWordOrderDistance': '-',
        'practicePromptEfficiency': '-',
        
        // Complex Transformation
        'practiceComplexFinalScore': '-',
        'practiceRuleAccuracy': '-',
        'practiceTransformComplete': '-',
        'practiceFormatScore': '-',
        'practiceComplexEfficiency': '-',

        // General
        'practicePromptLengthChars': '0 chars'
    };

    // Reset all metric elements
    Object.entries(metricsToReset).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });

    // Hide all metric sections
    const sections = [
        'practiceWordSortingMetrics',
        'practiceLogicalDeductionMetrics',
        'practiceCausalJudgementMetrics',
        'practiceSummarizationMetrics',
        'practiceTranslationMetrics',
        'practiceComplexTransformationMetrics',
        'practiceResults',
        'practiceExamples'
    ];

    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('hidden');
        }
    });

    // Clear examples section
    const examplesDiv = document.getElementById('practiceExamples');
    if (examplesDiv) {
        examplesDiv.innerHTML = '';
    }
}

function handleDatasetChange(dataset) {
    // Clear all previous metrics first
    clearAllMetrics();

    // Hide all special sections
    const sections = [
        'languageSelection',
        'complexTransformationExample',
        'complexTransformationElements',
        'practiceResults',
        'testComplexTransformationExample',
        'testComplexTransformationElements',
        'results'
    ];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.classList.add('hidden');
    });

    // Reset state for complex transformation
    if (dataset === 'complex_transformation') {
        // Reset practice mode state
        currentTurn = 1;
        previousOutputs = [];
        promptLengths = [];
        
        // Reset test mode state
        testCurrentTurn = 1;
        testPreviousOutputs = [];
        testPromptLengths = [];
        
        // Show complex-specific elements for practice
        document.getElementById('complexTransformationExample').classList.remove('hidden');
        document.getElementById('complexTransformationElements').classList.remove('hidden');
        
        // Show complex-specific elements for test
        document.getElementById('testComplexTransformationExample').classList.remove('hidden');
        document.getElementById('testComplexTransformationElements').classList.remove('hidden');
        
        // Update practice turn counter
        document.getElementById('turnCounter').textContent = '1';
        
        // Update test turn counter
        document.getElementById('testTurnCounter').textContent = '1';
        
        // Update practice button text
        document.getElementById('normalButton').classList.add('hidden');
        document.getElementById('complexButton').classList.remove('hidden');
        
        // Update test button text
        document.getElementById('testNormalButton').classList.add('hidden');
        document.getElementById('testComplexButton').classList.remove('hidden');
        
        // Load examples for both practice and test
        loadComplexPracticeExample();
        loadComplexTestExample();
    } else {
        // Show normal buttons and ensure prompt inputs are visible for other tasks
        document.getElementById('normalButton').classList.remove('hidden');
        document.getElementById('complexButton').classList.add('hidden');
        document.getElementById('testNormalButton').classList.remove('hidden');
        document.getElementById('testComplexButton').classList.add('hidden');
        
        // Ensure prompt input sections are visible and properly styled
        const practicePromptSection = document.getElementById('promptInputSection');
        const testPromptSection = document.getElementById('testPromptInputSection');
        if (practicePromptSection) {
            practicePromptSection.style.display = 'block';
            practicePromptSection.classList.remove('hidden');
        }
        if (testPromptSection) {
            testPromptSection.style.display = 'block';
            testPromptSection.classList.remove('hidden');
        }
    }

    // Show language selection for translation task
    if (dataset === 'translation_task') {
        document.getElementById('languageSelection').classList.remove('hidden');
    }

    // Reset prompt inputs
    const practicePromptTextarea = document.getElementById('practicePrompt');
    const testPromptTextarea = document.getElementById('testPrompt');
    if (practicePromptTextarea) {
        practicePromptTextarea.value = '';
        practicePromptTextarea.placeholder = dataset === 'complex_transformation' ? 
            'Enter your prompt for turn 1' : 
            'Enter your system prompt for this specific task';
    }
    if (testPromptTextarea) {
        testPromptTextarea.value = '';
        testPromptTextarea.placeholder = dataset === 'complex_transformation' ? 
            'Enter your prompt for turn 1' : 
            'Enter your system prompt for this specific task';
    }

    // Update instructions
    updateInstructions();

    // Reset character counts
    updateCharCount('practicePrompt', 'practiceCharCount');
    updateCharCount('testPrompt', 'testCharCount');
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

async function loadComplexTestExample() {
    try {
        const response = await fetch('/api/complex_test');  // Changed from complex_practice
        const data = await response.json();

        if (data.examples?.length > 0) {
            const example = data.examples[0];
            document.getElementById('testTaskDescription').innerText = example.task_description;
            document.getElementById('testReferenceSolution').innerText = example.display_reference;
            
            // Show the example section
            document.getElementById('testComplexTransformationExample').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading complex test example:', error);
    }
}

async function runPractice() {
    console.log('Starting practice round...');
    
    // Clear any previous metrics before starting new round
    clearAllMetrics();
    
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
        // Special handling for complex transformation ONLY
        if (datasetType === 'complex_transformation') {
            const requestBody = {
                system_prompt: systemPrompt,
                show_details: true, 
                dataset_type: datasetType,
                target_language: targetLanguage,
                turn: currentTurn,  // FIXED: Now sends actual current turn
                previous_outputs: currentTurn > 1 ? [previousOutputs[currentTurn - 2]] : []
            };
            
            console.log('Sending complex request:', requestBody);
            
            const response = await fetch('/api/pretest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });
            
            const responseData = await response.json();
            
            if (!response.ok) {
                throw new Error(responseData.error || 'Error running practice round');
            }
            
            handleComplexResponse(responseData);
            return;
        }

        // For ALL OTHER dataset types - unchanged
        const requestBody = {
            system_prompt: systemPrompt,
            show_details: true,
            dataset_type: datasetType,
            target_language: targetLanguage,
            turn: 1
        };
 
        console.log('Sending regular request:', requestBody);
 
        const response = await fetch('/api/pretest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
 
        const responseData = await response.json();
 
        if (!response.ok) {
            throw new Error(responseData.error || 'Error running practice round');
        }
 
        displayResults(responseData, 'practice');
        lastPrompt = systemPrompt;
        
    } catch (error) {
        console.error("Error in practice round:", error);
        alert('Error: ' + error.message);
    } finally {
        if (loadingElement) loadingElement.classList.add('hidden');
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

    // Show ONLY the relevant metrics section
    const relevantMetricsId = `${mode}${datasetType.charAt(0).toUpperCase() + datasetType.slice(1)}Metrics`;
    const metricsSection = document.getElementById(relevantMetricsId);
    
    // Hide all metric sections first
    const allMetricSections = resultsDiv.querySelectorAll('[id$="Metrics"]');
    allMetricSections.forEach(section => section.classList.add('hidden'));
    
    // Show results container
    resultsDiv.classList.remove('hidden');

    // Show relevant metrics section
    if (metricsSection) {
        metricsSection.classList.remove('hidden');
    }

    // Update prompt length if available
    if (data.metrics?.prompt_length !== undefined) {
        const promptLengthElement = document.getElementById(`${mode}PromptLengthChars`);
        if (promptLengthElement) {
            promptLengthElement.textContent = `${data.metrics.prompt_length} chars`;
        }
    }

    // Handle all dataset types
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
        } else if (datasetType === 'complex_transformation') {
            if (data.metrics && Object.keys(data.metrics).length > 0) {
                if (metricsSection) {
                    // Update metrics display
                    document.getElementById(`${mode}ComplexFinalScore`).textContent = 
                        `${data.metrics.final_score?.toFixed(1) || 0}%`;
                    document.getElementById(`${mode}RuleAccuracy`).textContent = 
                        `${data.metrics.rule_accuracy?.toFixed(1) || 0}`;
                    document.getElementById(`${mode}TransformComplete`).textContent = 
                        `${data.metrics.completeness?.toFixed(1) || 0}`;
                    document.getElementById(`${mode}FormatScore`).textContent = 
                        `${data.metrics.format_score?.toFixed(1) || 0}`;
                    document.getElementById(`${mode}ComplexEfficiency`).textContent = 
                        `${data.metrics.efficiency?.toFixed(1) || 100}%`;
                }
            }
        }
    } catch (error) {
        console.error('Error displaying metrics:', error);
    }

    // Display examples if they exist
    if (data.examples?.length > 0) {
        displayExamples(data.examples, mode, datasetType);
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

function resetMetricDisplays(mode) {
    // Hide ALL metrics sections first
    const sections = [
        'WordSortingMetrics',
        'LogicalDeductionMetrics',
        'CausalJudgementMetrics',
        'SummarizationMetrics',
        'TranslationMetrics',
        'ComplexTransformationMetrics'
    ];

    sections.forEach(section => {
        const sectionId = `${mode}${section}`;
        const sectionElement = document.getElementById(sectionId);
        if (sectionElement) {
            sectionElement.classList.add('hidden');
        }
    });

    // Reset all individual metric values
    const metricsToReset = {
        // Word Sorting
        [`${mode}CombinedScore`]: '-',
        [`${mode}Accuracy`]: '-',
        [`${mode}WordAccuracy`]: '-',
        [`${mode}WordOrderDistance`]: '-',
        [`${mode}PromptEfficiency`]: '-',
        
        // Logical Deduction
        [`${mode}LogicalAccuracy`]: '-',
        [`${mode}BaseAccuracy`]: '-',
        [`${mode}LogicalEfficiency`]: '-',
        
        // Causal Judgement
        [`${mode}CausalFinalScore`]: '-',
        [`${mode}CausalAccuracy`]: '-',
        [`${mode}CausalBaseAccuracy`]: '-',
        [`${mode}CausalEfficiency`]: '-',
        
        // Summarization
        [`${mode}SummarizationScore`]: '-',
        [`${mode}SemanticSimilarity`]: '-',
        [`${mode}LengthPenalty`]: '-',
        [`${mode}SummaryPromptEfficiency`]: '-',
        [`${mode}ActualLength`]: '-',
        [`${mode}PromptLengthChars`]: '0 chars',
        
        // Translation
        [`${mode}TranslationFinalScore`]: '-',
        [`${mode}TranslationSemanticScore`]: '-',
        [`${mode}TranslationQualityScore`]: '-',
        [`${mode}TranslationEfficiency`]: '-',
        
        // Complex Transformation
        [`${mode}ComplexFinalScore`]: '-',
        [`${mode}RuleAccuracy`]: '-',
        [`${mode}TransformComplete`]: '-',
        [`${mode}FormatScore`]: '-',
        [`${mode}ComplexEfficiency`]: '-'
    };

    // Reset each metric element
    Object.entries(metricsToReset).forEach(([id, defaultValue]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = defaultValue;
        }
    });

    // Hide and clear examples section
    const examplesDiv = document.getElementById(`${mode}Examples`);
    if (examplesDiv) {
        examplesDiv.innerHTML = '';
        examplesDiv.classList.add('hidden');
    }

    // Hide the main results container initially
    const resultsContainer = document.getElementById(mode === 'practice' ? 'practiceResults' : 'results');
    if (resultsContainer) {
        resultsContainer.classList.add('hidden');
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

async function runTest() {
    // Reset all metrics and results first
    const resultsDiv = document.getElementById('results');
    if (resultsDiv) {
        resultsDiv.classList.add('hidden');
        // Force clear all metric sections
        const metricSections = resultsDiv.querySelectorAll('[id$="Metrics"]');
        metricSections.forEach(section => section.classList.add('hidden'));
    }

    const name = document.getElementById('name').value;
    const systemPrompt = document.getElementById('testPrompt').value;
    const datasetType = document.getElementById('datasetSelection').value;
    const targetLanguage = datasetType === 'translation_task' ? getLanguageSelection() : null;

    if (!name) {
        alert('Please enter your name');
        return;
    }
    if (!systemPrompt) {
        alert('Please enter a prompt');
        return;
    }
    if (datasetType === 'translation_task' && !targetLanguage) {
        alert('Please select a language for translation');
        return;
    }

    const loadingElement = document.getElementById('testLoading');
    const resultsElement = document.getElementById('results');
    
    if (loadingElement) loadingElement.classList.remove('hidden');
    if (resultsElement) resultsElement.classList.add('hidden');

    try {
        // Special handling for complex transformation
        if (datasetType === 'complex_transformation') {
            const previousOutput = testCurrentTurn > 1 ? testPreviousOutputs[testCurrentTurn - 2] : null;
            
            const requestBody = {
                name: name,
                system_prompt: systemPrompt,
                dataset_type: datasetType,
                turn: testCurrentTurn,
                previous_outputs: previousOutput ? [previousOutput] : [],
                prompt_lengths: testPromptLengths
            };
            
            console.log('Sending complex test request:', JSON.stringify(requestBody, null, 2));
            
            const response = await fetch('/api/test_prompt', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server responded with ${response.status}`);
            }
            
            const responseData = await response.json();
            console.log('Received test response data:', JSON.stringify(responseData, null, 2));
            
            handleTestComplexResponse(responseData, name);
            return;
        }

        // Regular non-complex test request
        const requestBody = {
            name: name,
            system_prompt: systemPrompt,
            dataset_type: datasetType,
            target_language: targetLanguage
        };

        const response = await fetch('/api/test_prompt', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server responded with ${response.status}`);
        }

        const responseData = await response.json();
        console.log('Received test response data:', responseData);

        displayResults(responseData, 'test');

    } catch (error) {
        console.error("Error in test:", error);
        alert('Error: ' + error.message);
    } finally {
        if (loadingElement) loadingElement.classList.add('hidden');
    }
}

function handleTestComplexResponse(data, name) {
    console.log("Processing complex test response for turn:", testCurrentTurn, data);
    
    if (!data?.examples?.[0]) {
        console.error('Invalid response data:', data);
        return;
    }

    const newOutput = data.examples[0].raw_prediction;
    if (!newOutput) {
        console.error('Empty output in response');
        return;
    }

    // Store current prompt length for efficiency calculation
    const currentPrompt = document.getElementById('testPrompt').value;
    testPromptLengths[testCurrentTurn - 1] = currentPrompt.length;

    // Store this turn's output
    testPreviousOutputs[testCurrentTurn - 1] = newOutput;
    console.log('Storing output for turn:', testCurrentTurn, newOutput);

    // Show task details
    const taskDescription = data.examples[0].task_description;
    const referenceSolution = data.examples[0].reference_solution || data.examples[0].display_reference;
    
    const taskDescElement = document.getElementById('testTaskDescription');
    const refSolutionElement = document.getElementById('testReferenceSolution');
    
    if (taskDescElement) taskDescElement.textContent = taskDescription;
    if (refSolutionElement) refSolutionElement.textContent = referenceSolution;

    document.getElementById('testComplexTransformationExample').classList.remove('hidden');
    
    // Handle final turn
    if (testCurrentTurn === 3) {
        // Hide prompt input section - place before any results display
        const promptInputSection = document.getElementById('testPromptInputSection');
        if (promptInputSection) {
            promptInputSection.style.display = 'none';
        }
        
        displayResults(data, 'test');
        
        // Show metrics section
        const metricsDiv = document.getElementById('testComplexTransformationMetrics');
        if (metricsDiv) {
            metricsDiv.classList.remove('hidden');
        }

        // Update metrics
        if (data.metrics) {
            console.log("Updating final metrics:", data.metrics);
            const metrics = {
                'testComplexFinalScore': data.metrics.final_score || 0,
                'testRuleAccuracy': data.metrics.rule_accuracy || 0,
                'testTransformComplete': data.metrics.completeness || 0,
                'testFormatScore': data.metrics.format_score || 0,
                'testComplexEfficiency': data.metrics.efficiency || 0
            };

            Object.entries(metrics).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    const formattedValue = typeof value === 'number' ? value.toFixed(1) : '0';
                    element.textContent = id === 'testComplexEfficiency' ? 
                        `${formattedValue}%` : formattedValue;
                }
            });
        }

        // Update examples
        const examplesDiv = document.getElementById('testExamples');
        if (examplesDiv && data.examples) {
            examplesDiv.innerHTML = '';
            data.examples.forEach((example) => {
                const explanation = data.metrics?.individual_scores?.[0]?.explanation || 
                                  'Evaluation feedback not available';
                
                const exampleDiv = document.createElement('div');
                exampleDiv.className = 'bg-white p-4 rounded shadow mb-4';
                exampleDiv.innerHTML = `
                    <div class="space-y-4">
                        <div class="mb-4">
                            <p class="font-bold mb-2">Task:</p>
                            <p>${example.task_description || 'No task description available'}</p>
                        </div>

                        <div class="mb-4">
                            <p class="font-bold mb-2">Reference Solution:</p>
                            <p>${example.reference_solution || 'No reference solution available'}</p>
                        </div>

                        <div class="mb-4">
                            <p class="font-bold mb-2">Your Final Output:</p>
                            <p>${example.raw_prediction || 'No output available'}</p>
                        </div>

                        <div class="bg-blue-50 p-4 rounded">
                            <p class="font-bold mb-2">Evaluation Feedback:</p>
                            <p>${explanation}</p>
                        </div>
                    </div>
                `;
                examplesDiv.appendChild(exampleDiv);
            });
            examplesDiv.classList.remove('hidden');
        }

        // Reset state for next test
        testCurrentTurn = 1;
        testPreviousOutputs = [];
        testPromptLengths = [];
        
        // Reset button text
        document.getElementById('testNormalButton').classList.remove('hidden');
        document.getElementById('testComplexButton').classList.add('hidden');
    } else {
        // Move to next turn
        testCurrentTurn++;
        
        // Clear and show prompt input for next turn
        const promptTextarea = document.getElementById('testPrompt');
        const promptInputSection = document.getElementById('testPromptInputSection');
        if (promptTextarea) {
            promptTextarea.value = '';
            promptTextarea.placeholder = `Enter your prompt for turn ${testCurrentTurn}. Previous output will be used as context.`;
        }
        if (promptInputSection) {
            promptInputSection.style.display = 'block';
        }
        
        // Update button text
        document.getElementById('testNormalButton').classList.add('hidden');
        document.getElementById('testComplexButton').classList.remove('hidden');
    }

    // Update turn counter
    const turnCounter = document.getElementById('testTurnCounter');
    if (turnCounter) {
        turnCounter.textContent = testCurrentTurn;
    }

    // Update output history
    const previousOutputSection = document.getElementById('testPreviousOutputSection');
    const outputHistory = document.getElementById('testOutputHistory');
    if (previousOutputSection && outputHistory) {
        previousOutputSection.classList.remove('hidden');
        
        const outputHistoryHtml = testPreviousOutputs
            .map((output, index) => `
                <div class="mb-4">
                    <div class="text-sm font-medium mb-1">Turn ${index + 1}</div>
                    <div class="bg-gray-50 p-2 rounded">${output}</div>
                </div>
            `)
            .join('');
        
        outputHistory.innerHTML = outputHistoryHtml;
    }
}

function handleTestComplexResponse(data, name) {
    console.log("Processing complex test response for turn:", testCurrentTurn, data);
    
    if (!data?.examples?.[0]) {
        console.error('Invalid response data:', data);
        return;
    }

    const newOutput = data.examples[0].raw_prediction;
    if (!newOutput) {
        console.error('Empty output in response');
        return;
    }

    // Store current prompt length for efficiency calculation
    const currentPrompt = document.getElementById('testPrompt').value;
    testPromptLengths[testCurrentTurn - 1] = currentPrompt.length;

    // Store this turn's output
    testPreviousOutputs[testCurrentTurn - 1] = newOutput;
    console.log('Storing output for turn:', testCurrentTurn, newOutput);

    // Show task details
    const taskDescription = data.examples[0].task_description;
    const referenceSolution = data.examples[0].reference_solution || data.examples[0].display_reference;
    
    const taskDescElement = document.getElementById('testTaskDescription');
    const refSolutionElement = document.getElementById('testReferenceSolution');
    
    if (taskDescElement) taskDescElement.textContent = taskDescription;
    if (refSolutionElement) refSolutionElement.textContent = referenceSolution;

    document.getElementById('testComplexTransformationExample').classList.remove('hidden');
    
    // Handle final turn
    if (testCurrentTurn === 3) {
        const promptInputSection = document.getElementById('testPromptInputSection');
        if (promptInputSection) {
            promptInputSection.style.display = 'none';
            promptInputSection.classList.add('hidden');
            // Also hide the actual textarea inside
            const promptTextarea = document.getElementById('testPrompt');
            if (promptTextarea) {
                promptTextarea.style.display = 'none';
            }
            // And the button
            const testButton = document.querySelector('button[onclick="runTest()"]');
            if (testButton) {
                testButton.style.display = 'none';
            }
        }
    
        displayResults(data, 'test');
        // ... rest of the code

        // Show results and update metrics
        const resultsDiv = document.getElementById('results');
        const metricsDiv = document.getElementById('testComplexTransformationMetrics');
        if (resultsDiv) resultsDiv.classList.remove('hidden');
        if (metricsDiv) metricsDiv.classList.remove('hidden');

        // Update metrics with final turn results
        if (data.metrics) {
            console.log("Updating final metrics:", data.metrics);
            const metrics = {
                'testComplexFinalScore': data.metrics.final_score || 0,
                'testRuleAccuracy': data.metrics.rule_accuracy || 0,
                'testTransformComplete': data.metrics.completeness || 0,
                'testFormatScore': data.metrics.format_score || 0,
                'testComplexEfficiency': data.metrics.efficiency || 0
            };

            Object.entries(metrics).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    const formattedValue = typeof value === 'number' ? value.toFixed(1) : '0';
                    element.textContent = id === 'testComplexEfficiency' ? 
                        `${formattedValue}%` : formattedValue;
                }
            });
        }

        // Update examples with final output
        const examplesDiv = document.getElementById('testExamples');
        if (examplesDiv && data.examples) {
            examplesDiv.innerHTML = '';
            data.examples.forEach((example) => {
                // Get explanation safely
                const explanation = data.metrics?.individual_scores?.[0]?.explanation || 
                                  'Evaluation feedback not available';
                
                const exampleDiv = document.createElement('div');
                exampleDiv.className = 'bg-white p-4 rounded shadow mb-4';
                exampleDiv.innerHTML = `
                    <div class="space-y-4">
                        <div class="mb-4">
                            <p class="font-bold mb-2">Task:</p>
                            <p>${example.task_description || 'No task description available'}</p>
                        </div>

                        <div class="mb-4">
                            <p class="font-bold mb-2">Reference Solution:</p>
                            <p>${example.reference_solution || 'No reference solution available'}</p>
                        </div>

                        <div class="mb-4">
                            <p class="font-bold mb-2">Your Final Output:</p>
                            <p>${example.raw_prediction || 'No output available'}</p>
                        </div>

                        <div class="bg-blue-50 p-4 rounded">
                            <p class="font-bold mb-2">Evaluation Feedback:</p>
                            <p>${explanation}</p>
                        </div>
                    </div>
                `;
                examplesDiv.appendChild(exampleDiv);
            });
            examplesDiv.classList.remove('hidden');
        }

        // Only reset after showing final results
        setTimeout(() => {
            // Reset for next test
            testCurrentTurn = 1;
            testPreviousOutputs = [];
            testPromptLengths = [];
            
            // Show prompt input for next test
            const promptInputSection = document.getElementById('testPromptInputSection');
            if (promptInputSection) {
                promptInputSection.style.display = 'block';
            }
            
            // Reset button text
            document.getElementById('testNormalButton').classList.remove('hidden');
            document.getElementById('testComplexButton').classList.add('hidden');
        }, 1000);
    } else {
        // Move to next turn
        testCurrentTurn++;
        
        // Clear and show prompt input for next turn
        const promptTextarea = document.getElementById('testPrompt');
        const promptInputSection = document.getElementById('testPromptInputSection');
        if (promptTextarea) {
            promptTextarea.value = '';
            promptTextarea.placeholder = `Enter your prompt for turn ${testCurrentTurn}. Previous output will be used as context.`;
        }
        if (promptInputSection) {
            promptInputSection.style.display = 'block';
            promptInputSection.classList.remove('hidden');
        }
        
        // Update button text
        document.getElementById('testNormalButton').classList.add('hidden');
        document.getElementById('testComplexButton').classList.remove('hidden');
    }

    // Update turn counter
    const turnCounter = document.getElementById('testTurnCounter');
    if (turnCounter) {
        turnCounter.textContent = testCurrentTurn;
    }

    // Update output history
    const previousOutputSection = document.getElementById('testPreviousOutputSection');
    const outputHistory = document.getElementById('testOutputHistory');
    if (previousOutputSection && outputHistory) {
        previousOutputSection.classList.remove('hidden');
        
        const outputHistoryHtml = testPreviousOutputs
            .map((output, index) => `
                <div class="mb-4">
                    <div class="text-sm font-medium mb-1">Turn ${index + 1}</div>
                    <div class="bg-gray-50 p-2 rounded">${output}</div>
                </div>
            `)
            .join('');
        
        outputHistory.innerHTML = outputHistoryHtml;
    }
}

function handleComplexResponse(data) {
    console.log("Processing complex response, turn:", currentTurn, data);
    
    if (!data?.examples?.[0]) {
        console.error('Invalid response data:', data);
        return;
    }
 
    // Get the new output from this turn's response
    const output = data.examples[0].raw_prediction;
    if (!output) {
        console.error('Empty output in response');
        return;
    }
 
    // Store the prompt length for this turn
    const currentPrompt = document.getElementById('practicePrompt').value;
    promptLengths[currentTurn - 1] = currentPrompt.length;
 
    // Store this turn's NEW output at the correct index
    console.log(`Storing NEW output for turn ${currentTurn}:`, output);
    previousOutputs[currentTurn - 1] = output;
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
                'practiceComplexFinalScore': data.metrics.final_score || 0,
                'practiceRuleAccuracy': data.metrics.rule_accuracy || 0,
                'practiceTransformComplete': data.metrics.completeness || 0,
                'practiceFormatScore': data.metrics.format_score || 0,
                'practiceComplexEfficiency': data.metrics.efficiency || 0
            };
 
            Object.entries(metrics).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    const formattedValue = typeof value === 'number' ? value.toFixed(1) : '0';
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
                // Get explanation safely
                const explanation = data.metrics?.individual_scores?.[0]?.explanation || 
                                  'Evaluation feedback not available';
                
                const exampleDiv = document.createElement('div');
                exampleDiv.className = 'bg-white p-4 rounded shadow mb-4';
                exampleDiv.innerHTML = `
                    <div class="space-y-4">
                        <div class="mb-4">
                            <p class="font-bold mb-2">Task:</p>
                            <p>${example.task_description || 'No task description available'}</p>
                        </div>
 
                        <div class="mb-4">
                            <p class="font-bold mb-2">Reference Solution:</p>
                            <p>${example.reference_solution || 'No reference solution available'}</p>
                        </div>
 
                        <div class="mb-4">
                            <p class="font-bold mb-2">Your Final Output:</p>
                            <p>${example.raw_prediction || 'No output available'}</p>
                        </div>
 
                        <div class="bg-blue-50 p-4 rounded">
                            <p class="font-bold mb-2">Evaluation Feedback:</p>
                            <p>${explanation}</p>
                        </div>
                    </div>
                `;
                examplesDiv.appendChild(exampleDiv);
            });
            examplesDiv.classList.remove('hidden');
        }
 
        // Reset turn counter for next attempt
        currentTurn = 1;
        previousOutputs = [];
        promptLengths = [];
        
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

 