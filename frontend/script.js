// URL da API backend (substitua pela URL do seu backend no Render)
const API_URL = 'https://seu-backend-no-render.onrender.com/api/team-info';

// Elementos da DOM
const teamSelect = document.getElementById('teamSelect');
const searchBtn = document.getElementById('searchBtn');
const loadingElement = document.getElementById('loading');
const resultsElement = document.getElementById('results');
const errorMessageElement = document.getElementById('errorMessage');

// Elementos de resultados
const nextMatchElement = document.getElementById('nextMatch');
const lastMatchesElement = document.getElementById('lastMatches');
const lineupElement = document.getElementById('lineup');
const newsElement = document.getElementById('news');

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
teamSelect.addEventListener('change', () => {
    if (teamSelect.value) {
        handleSearch();
    }
});

// Função principal de busca
async function handleSearch() {
    const team = teamSelect.value;

    if (!team) {
        showError('Por favor, selecione um time.');
        return;
    }

    hideError();
    showLoading();
    hideResults();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ team })
        });

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        displayNextMatch(data.next_match, team);
        displayLastMatches(data.last_matches);
        displayLineup(data.probable_lineup);
        displayNews(data.news);

        hideLoading();
        showResults();
    } catch (error) {
        console.error('Erro ao buscar informações:', error);
        hideLoading();
        showError('Erro ao buscar informações. Tente novamente mais tarde.');
    }
}

// Funções para exibir os dados na interface
function displayNextMatch(match, team) {
    if (!match) {
        nextMatchElement.innerHTML = `<p>Informações não disponíveis</p>`;
        return;
    }

    nextMatchElement.innerHTML = `
        <div class="team">
            <div class="team-name">${team}</div>
        </div>
        <div class="vs">VS</div>
        <div class="team">
            <div class="team-name">${match.opponent || 'Adversário'}</div>
        </div>
        <div class="match-details">
            <p>Data: ${match.date || 'A definir'}</p>
            <p>Horário: ${match.time || 'A definir'}</p>
            <p>Local: ${match.stadium || 'A definir'}</p>
            <p>Competição: ${match.championship || 'Campeonato Brasileiro'}</p>
        </div>
    `;
}

function displayLastMatches(matches) {
    if (!matches || !Array.isArray(matches)) {
        lastMatchesElement.innerHTML = `<p>Dados de confrontos não disponíveis</p>`;
        return;
    }

    let html = '';
    matches.forEach(match => {
        html += `
            <div class="match-item">
                <div>${match.date} - ${match.opponent} - ${match.competition}</div>
                <div class="match-result">${match.result}</div>
            </div>
        `;
    });

    lastMatchesElement.innerHTML = html;
}

function displayLineup(lineup) {
    if (!lineup) {
        lineupElement.innerHTML = `<p>Escalação não disponível</p>`;
        return;
    }

    let html = `<p>Formação: ${lineup.formation || '4-3-3'}</p>`;

    if (lineup.players && Array.isArray(lineup.players)) {
        html += '<ul class="lineup-list">';
        lineup.players.forEach(player => {
            html += `<li>${player}</li>`;
        });
        html += '</ul>';
    } else {
        html += '<p>Escalação não disponível no momento</p>';
    }

    lineupElement.innerHTML = html;
}

function displayNews(newsItems) {
    if (!newsItems || !Array.isArray(newsItems)) {
        newsElement.innerHTML = `<p>Notícias não disponíveis no momento</p>`;
        return;
    }

    let html = '';
    newsItems.forEach(news => {
        html += `
            <div class="news-item">
                <h3>${news.title || 'Título não disponível'}</h3>
                <p>${news.summary || 'Resumo não disponível'}</p>
                <div class="news-date">${news.date || 'Data não disponível'} - ${news.source || 'Fonte não disponível'}</div>
            </div>
        `;
    });

    newsElement.innerHTML = html;
}

// Funções auxiliares de UI
function showLoading() {
    loadingElement.style.display = 'block';
}

function hideLoading() {
    loadingElement.style.display = 'none';
}

function showResults() {
    resultsElement.style.display = 'block';
}

function hideResults() {
    resultsElement.style.display = 'none';
}

function showError(message) {
    errorMessageElement.textContent = message;
    errorMessageElement.style.display = 'block';
}

function hideError() {
    errorMessageElement.style.display = 'none';
}