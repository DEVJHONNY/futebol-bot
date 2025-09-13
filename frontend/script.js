// URL da API backend (substitua pela URL do seu backend no Render)
const API_URL = 'https://futebol-bot-backend.onrender.com/api/team-info';
const LINEUP_API_URL = 'https://futebol-bot-backend.onrender.com/api/lineup-only';

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

// Função para buscar escalação atualizada separadamente
async function fetchUpdatedLineup(team) {
    try {
        console.log(`Buscando escalação atualizada para: ${team}`);
        const response = await fetch(LINEUP_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ team })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao buscar escalação atualizada');
        }

        console.log('Escalação atualizada recebida:', data);
        return data;
    } catch (error) {
        console.error('Erro ao buscar escalação atualizada:', error);
        return null;
    }
}

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
        // Buscar informações principais
        console.log(`Buscando informações para: ${team}`);
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ team })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `Erro na API: ${response.status}`);
        }

        // Tentar buscar escalação atualizada separadamente
        console.log('Tentando buscar escalação atualizada...');
        const updatedLineup = await fetchUpdatedLineup(team);
        if (updatedLineup && !updatedLineup.error) {
            console.log('Usando escalação atualizada');
            data.probable_lineup = updatedLineup;
        } else {
            console.log('Usando escalação da resposta principal');
        }

        // Exibir os dados
        displayNextMatch(data.next_match, team);
        displayLastMatches(data.last_matches);
        displayLineup(data.probable_lineup);
        displayNews(data.news);

        hideLoading();
        showResults();

    } catch (error) {
        console.error('Erro ao buscar informações:', error);
        hideLoading();
        showError(error.message || 'Erro ao buscar informações. Tente novamente mais tarde.');
    }
}

// Funções para exibir os dados na interface
function displayNextMatch(match, team) {
    if (!match || match.error) {
        nextMatchElement.innerHTML = `
            <div class="match-info">
                <p>Informações sobre o próximo jogo não disponíveis no momento.</p>
            </div>
        `;
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
    if (!matches || !Array.isArray(matches) || matches.length === 0) {
        lastMatchesElement.innerHTML = `<p>Dados de confrontos recentes não disponíveis.</p>`;
        return;
    }

    let html = '';
    matches.forEach(match => {
        if (match && match.date && match.opponent) {
            const resultClass = getResultClass(match.result);
            html += `
                <div class="match-item">
                    <div>${match.date} - ${match.opponent} - ${match.competition || 'Brasileirão'}</div>
                    <div class="match-result ${resultClass}">${match.result || 'N/D'}</div>
                </div>
            `;
        }
    });

    lastMatchesElement.innerHTML = html || '<p>Dados de confrontos não disponíveis.</p>';
}

function getResultClass(result) {
    if (!result) return '';

    // Tenta determinar se foi vitória, derrota ou empate
    if (typeof result === 'string') {
        if (result.includes('x')) {
            const [home, away] = result.split('x').map(score => parseInt(score.trim()));
            if (!isNaN(home) && !isNaN(away)) {
                if (home > away) return 'victory';
                if (home < away) return 'defeat';
                return 'draw';
            }
        }

        // Verifica por palavras-chave
        if (result.toLowerCase().includes('vitória') || result.toLowerCase().includes('win')) return 'victory';
        if (result.toLowerCase().includes('derrota') || result.toLowerCase().includes('loss')) return 'defeat';
        if (result.toLowerCase().includes('empate') || result.toLowerCase().includes('draw')) return 'draw';
    }

    return '';
}

function displayLineup(lineup) {
    if (!lineup || lineup.error) {
        lineupElement.innerHTML = `
            <p>Escalação não disponível no momento.</p>
            <p class="small-text">Atualizando dados de jogadores...</p>
        `;
        return;
    }

    let html = `<p>Formação: ${lineup.formation || '4-3-3'}</p>`;

    if (lineup.players && Array.isArray(lineup.players)) {
        html += '<ul class="lineup-list">';
        lineup.players.forEach((player, index) => {
            const position = getPositionName(index, lineup.formation);
            html += `<li><span class="position">${position}:</span> ${player || 'A definir'}</li>`;
        });
        html += '</ul>';
    } else {
        html += '<p>Escalação não disponível no momento.</p>';
    }

    html += '<p class="small-text">Escalação provável para o próximo jogo</p>';

    lineupElement.innerHTML = html;
}

function getPositionName(index, formation) {
    const positions = {
        0: 'GOL',
        1: 'LD',
        2: 'ZAG',
        3: 'ZAG',
        4: 'LE',
        5: 'VOL',
        6: 'MC',
        7: 'MC',
        8: 'ATA',
        9: 'ATA',
        10: 'CA'
    };

    return positions[index] || 'JOG';
}

function displayNews(newsItems) {
    if (!newsItems || !Array.isArray(newsItems) || newsItems.length === 0) {
        newsElement.innerHTML = `<p>Notícias recentes não disponíveis no momento.</p>`;
        return;
    }

    let html = '';
    newsItems.forEach(news => {
        if (news && news.title) {
            html += `
                <div class="news-item">
                    <h3>${news.title || 'Título não disponível'}</h3>
                    <p>${news.summary || 'Resumo não disponível'}</p>
                    <div class="news-date">
                        ${news.date || 'Data não disponível'} - ${news.source || 'Fonte não disponível'}
                    </div>
                </div>
            `;
        }
    });

    newsElement.innerHTML = html || '<p>Notícias recentes não disponíveis.</p>';
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

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    console.log('Bot do Brasileirão inicializado');

    // Verifica se a API está respondendo
    fetch('https://futebol-bot-backend.onrender.com/health')
        .then(response => response.json())
        .then(data => {
            console.log('Status do backend:', data);
            if (!data.gemini_configured) {
                showError('API não configurada corretamente. Verifique o backend.');
            }
        })
        .catch(error => {
            console.error('Erro ao conectar com o backend:', error);
            showError('Erro de conexão com o servidor. Tente novamente mais tarde.');
        });
});