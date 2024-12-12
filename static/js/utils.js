function updateCharCount(textareaId, counterId) {
    const textarea = document.getElementById(textareaId);
    const counter = document.getElementById(counterId);
    const count = textarea.value.length;
    counter.textContent = `${count} characters`;
}

function toggleExamples(mode) {
    const examplesDiv = document.getElementById(`${mode}Examples`);
    examplesDiv.classList.toggle('hidden');
}

function useLastPrompt() {
    document.getElementById('testPrompt').value = document.getElementById('practicePrompt').value;
    updateCharCount('testPrompt', 'testCharCount');
}