// elderly/app.js - word-sequence(단어 맞추기) 모드

// JWT 토큰 확인 (URL 파라미터 또는 localStorage에서)
const urlParams = new URLSearchParams(window.location.search);
const jwt = urlParams.get('token') || localStorage.getItem('access_token');

// URL 파라미터로 받은 토큰을 localStorage에 저장
if (urlParams.get('token')) {
  localStorage.setItem('access_token', urlParams.get('token'));
}

if (!jwt) {
  // 로그인 안 된 경우 로그인 페이지로 이동
  window.location.href = 'http://localhost:8000/';
}

// 랜덤 세그먼트 가져오기
async function fetchRandomSegment() {
  try {
    const response = await fetch('http://localhost:8011/api/v0/stories/segments/random', {
      headers: {
        'Authorization': 'Bearer ' + jwt,
        'Content-Type': 'application/json'
      },
      mode: 'cors'
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Random segment loaded:', data.results);
    return data.results;
  } catch (e) {
    console.error('Error loading random segment:', e);
    throw e;
  }
}

// 단어 분리 함수
function splitIntoWords(text) {
  // 한국어 문장을 단어 단위로 분리
  return text.split(/\s+/).filter(word => word.length > 0);
}

// 단어 섞기 함수
function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// 게임 초기화
async function initializeGame() {
  try {
    // 랜덤 세그먼트 가져오기
    const segment = await fetchRandomSegment();
    
    // 단어 분리
    const words = splitIntoWords(segment.segment_text);
    const shuffledWords = shuffleArray(words);
    
    // 게임 데이터 설정
    window.gameData = {
      segment: segment.segment_text,
      words: words,
      shuffled: shuffledWords,
      segmentId: segment.id
    };
    
    // UI 렌더링
    renderFullSentence(segment.segment_text);
    setupDnDWord(window.gameData);
    
    console.log('Game initialized with segment:', segment.segment_text);
  } catch (e) {
    console.error('Error initializing game:', e);
    alert('게임을 초기화하는 중 오류가 발생했습니다: ' + e.message);
  }
}

// 페이지 로드 시 게임 초기화
window.addEventListener('DOMContentLoaded', initializeGame);

function getStoryIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get('story_id');
}

async function fetchWordSequence(storyId) {
  const res = await fetch(`/api/v0/activity/word-sequence/${storyId}`);
  if (!res.ok) throw new Error('이야기 데이터를 불러올 수 없습니다.');
  return await res.json();
}

function renderFullSentence(segment) {
  document.getElementById('fullSentence').textContent = segment;
}

function createDropZones(count) {
  const correctOrder = document.getElementById('correctOrder');
  correctOrder.innerHTML = '';
  for (let i = 0; i < count; i++) {
    const dz = document.createElement('div');
    dz.className = 'drop-zone';
    dz.dataset.position = i + 1;
    dz.innerHTML = `<span class="drop-zone-label">${i + 1}번</span><span class="drop-zone-text">여기에 단어를 놓으세요</span>`;
    correctOrder.appendChild(dz);
  }
}

function createWordFragments(words) {
  const container = document.getElementById('shuffledWords');
  container.innerHTML = '';
  words.forEach((word, idx) => {
    const el = document.createElement('div');
    el.className = 'word-fragment';
    el.draggable = true;
    el.dataset.wordIndex = idx;
    el.textContent = word;
    container.appendChild(el);
  });
}

function setupDnDWord(story) {
  window.gameData = story;
  let currentOrder = Array(story.words.length).fill(null);
  let attempts = 0;
  let startTime = Date.now();
  let timerInterval;

  function updateProgress() {
    const filled = currentOrder.filter(x => x !== null).length;
    const total = story.words.length;
    document.getElementById('progress').textContent = `${filled}/${total}`;
  }

  function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const min = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const sec = String(elapsed % 60).padStart(2, '0');
    document.getElementById('timer').textContent = `${min}:${sec}`;
  }

  function startTimer() {
    timerInterval = setInterval(updateTimer, 1000);
  }

  function stopTimer() {
    clearInterval(timerInterval);
    updateTimer();
  }

  function resetGame() {
    currentOrder = Array(story.words.length).fill(null);
    createWordFragments(story.shuffled);
    createDropZones(story.words.length);
    updateProgress();
    document.getElementById('feedbackMessage').innerHTML = '<p>단어를 드래그하여 올바른 순서로 배치해 보세요!</p>';
    startTime = Date.now();
    stopTimer();
    startTimer();
    setupEvents();
  }

  function showSuccess() {
    stopTimer();
    document.getElementById('successModal').classList.add('show');
    document.getElementById('finalTime').textContent = document.getElementById('timer').textContent;
    document.getElementById('attempts').textContent = attempts;
  }

  function checkOrder() {
    attempts++;
    if (JSON.stringify(currentOrder) === JSON.stringify(story.words)) {
      document.getElementById('feedbackMessage').innerHTML = '<p class="success">정답입니다! 🎉</p>';
      showSuccess();
    } else {
      document.getElementById('feedbackMessage').innerHTML = '<p class="error">순서가 올바르지 않습니다. 다시 시도해보세요.</p>';
    }
  }

  function setupEvents() {
    // 드래그앤드롭 이벤트
    document.querySelectorAll('.word-fragment').forEach(fragment => {
      fragment.addEventListener('dragstart', e => {
        fragment.classList.add('dragging');
        e.dataTransfer.setData('text/plain', fragment.dataset.wordIndex);
      });
      fragment.addEventListener('dragend', e => {
        fragment.classList.remove('dragging');
      });
    });
    document.querySelectorAll('.drop-zone').forEach(zone => {
      zone.addEventListener('dragover', e => {
        e.preventDefault();
        zone.classList.add('drag-over');
      });
      zone.addEventListener('dragleave', e => {
        zone.classList.remove('drag-over');
      });
      zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        const idx = e.dataTransfer.getData('text/plain');
        const word = story.shuffled[idx];
        const pos = parseInt(zone.dataset.position, 10) - 1;
        // 이미 배치된 단어 제거
        const prevIdx = currentOrder.indexOf(word);
        if (prevIdx !== -1) {
          currentOrder[prevIdx] = null;
          document.querySelector(`.drop-zone[data-position="${prevIdx + 1}"] .placed-fragment`)?.remove();
        }
        currentOrder[pos] = word;
        zone.innerHTML = `<span class="drop-zone-label">${pos + 1}번</span><div class="placed-fragment">${word}</div>`;
        updateProgress();
      });
    });
    document.getElementById('checkOrderBtn').onclick = checkOrder;
    document.getElementById('resetBtn').onclick = resetGame;
    document.getElementById('playAgainBtn').onclick = () => {
      document.getElementById('successModal').classList.remove('show');
      resetGame();
    };
    // 힌트 버튼(첫 단어 보여주기)
    document.getElementById('hintBtn').onclick = () => {
      const first = story.words[0];
      document.getElementById('feedbackMessage').innerHTML = `<p class="info">첫 단어는: <b>${first}</b></p>`;
    };
  }

  // 초기화
  createWordFragments(story.shuffled);
  createDropZones(story.words.length);
  updateProgress();
  startTimer();
  setupEvents();
} 