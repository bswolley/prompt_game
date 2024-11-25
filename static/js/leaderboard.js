// Column configurations for different dataset types
const languageMap = {
    'pt': 'Portuguese',
    'ru': 'Russian',
    'sl': 'Slovenian',
    'es': 'Spanish',
    'sv': 'Swedish'
};

const columnConfigs = {
    text_summarization: [
        { key: 'name', label: 'Name', icon: 'fa-user' },
        { key: 'score', label: 'Score', icon: 'fa-star' },
        { key: 'prompt_length', label: 'Prompt Length', icon: 'fa-text-width' },
        { key: 'similarity', label: 'Similarity', icon: 'fa-equals' },
        { key: 'length_penalty_avg', label: 'Length Penalty', icon: 'fa-ruler' },
        { key: 'prompt_efficiency', label: 'Efficiency', icon: 'fa-bolt' },
        { key: 'timestamp', label: 'Date', icon: 'fa-calendar' }
    ],
    word_sorting: [
        { key: 'name', label: 'Name', icon: 'fa-user' },
        { key: 'score', label: 'Score', icon: 'fa-star' },
        { key: 'prompt_length', label: 'Prompt Length', icon: 'fa-text-width' },
        { key: 'accuracy', label: 'Accuracy', icon: 'fa-bullseye' },
        { key: 'word_accuracy', label: 'Word Accuracy', icon: 'fa-check-double' },
        { key: 'efficiency', label: 'Efficiency', icon: 'fa-bolt' },
        { key: 'timestamp', label: 'Date', icon: 'fa-calendar' }
    ],
    causal_judgement: [
        { key: 'name', label: 'Name', icon: 'fa-user' },
        { key: 'score', label: 'Score', icon: 'fa-star' },
        { key: 'prompt_length', label: 'Prompt Length', icon: 'fa-text-width' },
        { key: 'base_accuracy', label: 'Base Accuracy', icon: 'fa-bullseye' },
        { key: 'efficiency', label: 'Efficiency', icon: 'fa-bolt' },
        { key: 'timestamp', label: 'Date', icon: 'fa-calendar' }
    ],
    translation_task: [
        { key: 'name', label: 'Name', icon: 'fa-user' },
        { key: 'score', label: 'Score', icon: 'fa-star' },
        { key: 'target_language', label: 'Language', icon: 'fa-language' },
        { key: 'prompt_length', label: 'Prompt Length', icon: 'fa-text-width' },
        { key: 'semantic_similarity', label: 'Semantic Score', icon: 'fa-equals' },
        { key: 'language_quality', label: 'Quality', icon: 'fa-check-circle' },
        { key: 'efficiency', label: 'Efficiency', icon: 'fa-bolt' },
        { key: 'timestamp', label: 'Date', icon: 'fa-calendar' }
    ],
};

let activeTab = 'text_summarization';
let sortConfig = { key: 'score', direction: 'desc' };
let leaderboardData = {};

function setActiveTab(tab) {
    activeTab = tab;
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if (btn.dataset.tab === tab) {
            btn.classList.remove('bg-gray-100', 'text-gray-700');
            btn.classList.add('bg-green-500', 'text-white');
        } else {
            btn.classList.remove('bg-green-500', 'text-white');
            btn.classList.add('bg-gray-100', 'text-gray-700');
        }
    });
    
    document.getElementById('leaderboardTitle').textContent = 
        tab.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Leaderboard';
    
    loadLeaderboard(tab);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatValue(value, key) {
    if (value === null || value === undefined) return '-';
    if (key === 'timestamp') return formatDate(value);
    if (key === 'target_language') return languageMap[value] || value;
    if (typeof value === 'number') {
        if (key === 'prompt_length') return Math.round(value);
        if (key === 'score' || key.includes('accuracy') || key.includes('similarity') || 
            key.includes('efficiency') || key.includes('penalty')) {
            return value.toFixed(1) + '%';
        }
        return value.toFixed(2);
    }
    return value;
}

function handleSort(key) {
    sortConfig = {
        key,
        direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    };
    renderLeaderboard();
}

async function loadLeaderboard(dataset) {
    try {
        const response = await fetch(`/api/leaderboard/${dataset}`);
        const data = await response.json();
        leaderboardData[dataset] = data;
        
        const emptyState = document.getElementById('emptyState');
        const table = document.getElementById('mainLeaderboard');
        if (!data || data.length === 0) {
            emptyState.classList.remove('hidden');
            table.classList.add('hidden');
        } else {
            emptyState.classList.add('hidden');
            table.classList.remove('hidden');
            updateStatsCards(data);
            renderLeaderboard();
        }
    } catch (error) {
        console.error('Error loading leaderboard:', error);
        document.getElementById('emptyState').innerHTML = `
            <i class="fas fa-exclamation-circle text-red-500 text-5xl mb-4"></i>
            <p class="text-gray-600">Error loading leaderboard data</p>
        `;
        document.getElementById('emptyState').classList.remove('hidden');
        document.getElementById('mainLeaderboard').classList.add('hidden');
    }
}

function updateStatsCards(data) {
    const stats = {
        totalEntries: data.length,
        avgScore: data.length ? data.reduce((acc, curr) => acc + curr.score, 0) / data.length : 0,
        topScore: data.length ? Math.max(...data.map(entry => entry.score)) : 0
    };

    document.getElementById('statsCards').innerHTML = `
        <div class="bg-white p-6 rounded-lg shadow-md">
            <div class="flex items-center space-x-3">
                <i class="fas fa-users text-green-500 text-2xl"></i>
                <div>
                    <h3 class="text-sm text-gray-600">Total Entries</h3>
                    <p class="text-2xl font-bold">${stats.totalEntries}</p>
                </div>
            </div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md">
            <div class="flex items-center space-x-3">
                <i class="fas fa-chart-line text-green-500 text-2xl"></i>
                <div>
                    <h3 class="text-sm text-gray-600">Average Score</h3>
                    <p class="text-2xl font-bold">${stats.avgScore.toFixed(1)}%</p>
                </div>
            </div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md">
            <div class="flex items-center space-x-3">
                <i class="fas fa-trophy text-green-500 text-2xl"></i>
                <div>
                    <h3 class="text-sm text-gray-600">Top Score</h3>
                    <p class="text-2xl font-bold">${stats.topScore.toFixed(1)}%</p>
                </div>
            </div>
        </div>
    `;
}

function renderLeaderboard() {
    const headers = document.getElementById('columnHeaders');
    headers.innerHTML = columnConfigs[activeTab]
        .map(({ key, label, icon }) => `
            <th class="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                <button onclick="handleSort('${key}')" class="hover:text-gray-900 flex items-center space-x-2">
                    <i class="fas ${icon} text-gray-400"></i>
                    <span>${label}</span>
                    ${sortConfig.key === key ? 
                        `<i class="fas fa-sort-${sortConfig.direction === 'asc' ? 'up' : 'down'} ml-1"></i>` : 
                        ''}
                </button>
            </th>
        `).join('');

    const tbody = document.querySelector('#mainLeaderboard tbody');
    const data = leaderboardData[activeTab] || [];
    
    if (data.length === 0) {
        document.getElementById('emptyState').classList.remove('hidden');
        document.getElementById('mainLeaderboard').classList.add('hidden');
        return;
    }

    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('mainLeaderboard').classList.remove('hidden');

    tbody.innerHTML = data
        .sort((a, b) => {
            const modifier = sortConfig.direction === 'asc' ? 1 : -1;
            if (sortConfig.key === 'timestamp') {
                return (new Date(a[sortConfig.key]) - new Date(b[sortConfig.key])) * modifier;
            }
            const aValue = a[sortConfig.key] ?? -Infinity;
            const bValue = b[sortConfig.key] ?? -Infinity;
            return (aValue - bValue) * modifier;
        })
        .map((entry, index) => `
            <tr class="hover:bg-gray-50 transition-colors duration-150">
                ${columnConfigs[activeTab]
                    .map(({ key }) => `
                        <td class="px-6 py-4 whitespace-nowrap">
                            <div class="flex items-center">
                                ${
                                    key === 'name' && index < 3
                                        ? `<span class="mr-2 text-lg ${
                                            index === 0
                                                ? 'text-yellow-500' // Gold
                                                : index === 1
                                                ? 'text-gray-400' // Silver
                                                : 'text-orange-500' // Bronze
                                        }">
                                            <i class="fas fa-trophy"></i>
                                        </span>`
                                        : ''
                                }
                                <span class="text-sm ${
                                    key === 'score' ? 'font-medium text-gray-900' : 'text-gray-600'
                                }">${formatValue(entry[key], key)}</span>
                            </div>
                        </td>
                    `).join('')}
            </tr>
        `).join('');
}


// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setActiveTab(activeTab);
});