// JWT 토큰 확인 (URL 파라미터 또는 localStorage에서)
const urlParams = new URLSearchParams(window.location.search);
const jwt = urlParams.get('token') || localStorage.getItem('access_token');

// URL 파라미터로 받은 토큰을 localStorage에 저장
if (urlParams.get('token')) {
  localStorage.setItem('access_token', urlParams.get('token'));
}

if (!jwt) {
  // 로그인 안 된 경우 user-service로 이동
  window.location.href = 'http://localhost:8000/';
}

// story 목록 불러오기
fetch('http://localhost:8011/api/v0/stories', {
  headers: {
    'Authorization': 'Bearer ' + jwt
  }
})
.then(res => res.json())
.then(data => {
  // 본인 story만 옴!
  console.log(data.results);
  // TODO: story 목록을 화면에 렌더링
})
.catch(error => {
  console.error('Story 목록을 불러오는데 실패했습니다:', error);
  if (error.status === 401) {
    // 인증 실패 시 user-service로 리다이렉트
    localStorage.removeItem('access_token');
    window.location.href = 'http://localhost:8000/';
  }
});

// API 설정
const API_BASE_URL = '/api/v0';

// Application state
let stories = [];

const categories = ["가족 모임", "여행", "생일", "기념일", "일상"];
const difficulties = ["쉬움", "보통", "어려움"];

let selectedStoryId = 1;
let nextId = 4;

// 이미지 업로드 관련 변수
let uploadedImageUrl = null;

// 이미지 업로드 처리
async function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // 파일 크기 검증 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    showMessage('파일 크기는 5MB를 초과할 수 없습니다.', 'error');
    event.target.value = '';
    return;
  }
  
  // 파일 타입 검증
  if (!file.type.startsWith('image/')) {
    showMessage('이미지 파일만 업로드 가능합니다.', 'error');
    event.target.value = '';
    return;
  }
  
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload/image`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + jwt
      },
      body: formData
    });
    
    const data = await response.json();
    
    if (data.results) {
      uploadedImageUrl = data.results.image_url;
      showImagePreview(uploadedImageUrl);
      showMessage('이미지가 성공적으로 업로드되었습니다.', 'success');
    } else {
      showMessage('이미지 업로드에 실패했습니다: ' + (data.error || '알 수 없는 오류'), 'error');
    }
  } catch (error) {
    showMessage('이미지 업로드 중 오류가 발생했습니다: ' + error.message, 'error');
  }
}

// 이미지 미리보기 표시
function showImagePreview(imageUrl) {
  const preview = document.getElementById('image-preview');
  const previewImg = document.getElementById('preview-img');
  
  previewImg.src = imageUrl;
  preview.style.display = 'block';
}

// 이미지 제거
function removeImage() {
  uploadedImageUrl = null;
  document.getElementById('image').value = '';
  document.getElementById('image-preview').style.display = 'none';
}

// API 호출 함수들
async function fetchStories() {
  try {
    const response = await fetch(`${API_BASE_URL}/stories/`, {
      headers: {
        'Authorization': 'Bearer ' + jwt,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    if (data.results) {
      stories = data.results;
    } else {
      stories = [];
    }
  } catch (error) {
    console.error('이야기 목록을 불러오는데 실패했습니다:', error);
    stories = [];
  }
}

async function createStory(storyData) {
  try {
    const response = await fetch(`${API_BASE_URL}/stories/`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + jwt,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(storyData)
    });
    const data = await response.json();
    if (data.results) {
      return data.results;
    } else {
      throw new Error(data.error || '이야기 생성에 실패했습니다.');
    }
  } catch (error) {
    console.error('이야기 생성 실패:', error);
    throw error;
  }
}

async function updateStory(storyId, storyData) {
  try {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}`, {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + jwt,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(storyData)
    });
    const data = await response.json();
    if (data.results) {
      return data.results;
    } else {
      throw new Error(data.error || '이야기 수정에 실패했습니다.');
    }
  } catch (error) {
    console.error('이야기 수정 실패:', error);
    throw error;
  }
}

async function deleteStoryAPI(storyId) {
  try {
    const response = await fetch(`${API_BASE_URL}/stories/${storyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': 'Bearer ' + jwt,
        'Content-Type': 'application/json'
      }
    });
    if (response.ok) {
      return true;
    } else {
      throw new Error('이야기 삭제에 실패했습니다.');
    }
  } catch (error) {
    console.error('이야기 삭제 실패:', error);
    throw error;
  }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', async function() {
  setupEventListeners();
  await fetchStories();
  renderStories();
  updateStats();
  renderPreview();
});

// Initialize form select elements
function initializeFormSelects() {
  const categorySelect = document.getElementById('category');
  const difficultySelect = document.getElementById('difficulty');
  
  categories.forEach(category => {
    const option = document.createElement('option');
    option.value = category;
    option.textContent = category;
    categorySelect.appendChild(option);
  });
  
  difficulties.forEach(difficulty => {
    const option = document.createElement('option');
    option.value = difficulty;
    option.textContent = difficulty;
    difficultySelect.appendChild(option);
  });
}

// Initialize filter selects
function initializeFilters() {
  const filterCategory = document.getElementById('filterCategory');
  const filterDifficulty = document.getElementById('filterDifficulty');
  
  // Add "All" option
  const allCategoryOption = document.createElement('option');
  allCategoryOption.value = '';
  allCategoryOption.textContent = '전체 카테고리';
  filterCategory.appendChild(allCategoryOption);
  
  const allDifficultyOption = document.createElement('option');
  allDifficultyOption.value = '';
  allDifficultyOption.textContent = '전체 난이도';
  filterDifficulty.appendChild(allDifficultyOption);
  
  // Add specific options
  categories.forEach(category => {
    const option = document.createElement('option');
    option.value = category;
    option.textContent = category;
    filterCategory.appendChild(option);
  });
  
  difficulties.forEach(difficulty => {
    const option = document.createElement('option');
    option.value = difficulty;
    option.textContent = difficulty;
    filterDifficulty.appendChild(option);
  });
}

// Setup event listeners
function setupEventListeners() {
  // Form submission
  document.getElementById('story-form').addEventListener('submit', handleFormSubmit);
  
  // Search
  document.getElementById('searchInput').addEventListener('input', handleSearch);
  
  // Image upload
  document.getElementById('image').addEventListener('change', handleImageUpload);
  document.getElementById('remove-image').addEventListener('click', removeImage);
}

// Handle form submission
async function handleFormSubmit(event) {
  event.preventDefault();
  
  const storyData = {
    title: document.getElementById('title').value,
    content: document.getElementById('content').value,
    image_url: uploadedImageUrl || 'default.jpg'
  };
  
  try {
    const newStory = await createStory(storyData);
    stories.unshift(newStory);
    selectedStoryId = newStory.id;
    
    // Reset form
    event.target.reset();
    uploadedImageUrl = null;
    document.getElementById('image-preview').style.display = 'none';
    
    // Update UI
    renderStories();
    updateStats();
    renderPreview();
    
    // Show success message
    showMessage('새 이야기가 성공적으로 등록되었습니다!', 'success');
  } catch (error) {
    showMessage('이야기 등록에 실패했습니다: ' + error.message, 'error');
  }
}

// Handle search
function handleSearch() {
  renderStories();
}

// Get filtered stories
function getFilteredStories() {
  const searchTerm = document.getElementById('searchInput').value.toLowerCase();
  
  return stories.filter(story => {
    const matchesSearch = !searchTerm || 
      story.title.toLowerCase().includes(searchTerm) ||
      story.content.toLowerCase().includes(searchTerm);
    
    return matchesSearch;
  });
}

// Render stories
function renderStories() {
  const container = document.getElementById('story-list');
  const filteredStories = getFilteredStories();
  
  if (filteredStories.length === 0) {
    container.innerHTML = '<div class="preview-placeholder">검색 결과가 없습니다.</div>';
    return;
  }
  
  container.innerHTML = filteredStories.map(story => `
    <div class="story-card" data-id="${story.id}">
      <div class="story-card__header">
        <h3 class="story-card__title">${story.title}</h3>
        <div class="story-card__actions">
          <button class="btn btn--sm btn--edit" onclick="editStory(${story.id})">편집</button>
          <button class="btn btn--sm btn--delete" onclick="deleteStory(${story.id})">삭제</button>
        </div>
      </div>
      <div class="story-card__content">
        ${story.content.substring(0, 100)}${story.content.length > 100 ? '...' : ''}
      </div>
      <div class="story-card__meta">
        <div class="story-card__date">${formatDate(story.created_at)}</div>
      </div>
    </div>
  `).join('');
  
  // Add click listeners to story cards
  container.querySelectorAll('.story-card').forEach(card => {
    card.addEventListener('click', function(e) {
      if (!e.target.classList.contains('btn')) {
        selectedStoryId = parseInt(this.dataset.id);
        updateSelectedCard();
        renderPreview();
      }
    });
  });
  
  updateSelectedCard();
}

// Update selected card styling
function updateSelectedCard() {
  document.querySelectorAll('.story-card').forEach(card => {
    card.classList.remove('story-card--selected');
  });
  
  const selectedCard = document.querySelector(`[data-id="${selectedStoryId}"]`);
  if (selectedCard) {
    selectedCard.classList.add('story-card--selected');
    selectedCard.style.borderColor = 'var(--color-primary)';
    selectedCard.style.backgroundColor = 'rgba(var(--color-primary), 0.05)';
  }
}



// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

// Update statistics
function updateStats() {
  const statsContainer = document.getElementById('stats');
  const totalStories = stories.length;
  const thisWeekStories = stories.filter(story => {
    const storyDate = new Date(story.created_at);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return storyDate >= weekAgo;
  }).length;
  
  statsContainer.innerHTML = `
    <div class="stats-card">
      <div class="stats-card__value">${totalStories}</div>
      <div class="stats-card__label">총 이야기</div>
    </div>
    <div class="stats-card">
      <div class="stats-card__value">${thisWeekStories}</div>
      <div class="stats-card__label">이번 주</div>
    </div>
    <div class="stats-card">
      <div class="stats-card__value">${stories.length > 0 ? stories[0].segments?.length || 0 : 0}</div>
      <div class="stats-card__label">세그먼트</div>
    </div>
  `;
}

// Render preview
function renderPreview() {
  const previewContainer = document.getElementById('preview');
  const selectedStory = stories.find(story => story.id === selectedStoryId);
  
  if (!selectedStory) {
    previewContainer.innerHTML = '<div class="preview-placeholder">이야기를 선택하세요</div>';
    return;
  }
  
  const gameOptions = generateGameOptions(selectedStory);
  
  previewContainer.innerHTML = `
    <div class="preview-container">
      <h3 class="preview-title">${selectedStory.title}</h3>
      <div class="preview-content">${selectedStory.content}</div>
      <div class="preview-game">
        <h4 class="preview-game__title">이야기 순서 맞추기</h4>
        <div class="preview-game__options">
          ${gameOptions.map(option => `
            <button class="preview-game__option">${option}</button>
          `).join('')}
        </div>
      </div>
    </div>
  `;
}

// Generate game options
function generateGameOptions(story) {
  const sentences = story.content.split('.').filter(s => s.trim().length > 0);
  if (sentences.length < 2) {
    return ['이야기를 시작하다', '이야기를 이어가다', '이야기를 마무리하다'];
  }
  
  // Take first few sentences and shuffle them
  const options = sentences.slice(0, Math.min(3, sentences.length)).map(s => s.trim() + '.');
  return shuffleArray([...options]);
}

// Shuffle array utility
function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// Edit story
function editStory(id) {
  const story = stories.find(s => s.id === id);
  if (!story) return;
  
  // Fill form with story data
  document.getElementById('title').value = story.title;
  document.getElementById('content').value = story.content;
  
  // Set image preview if exists
  if (story.image_url && story.image_url !== 'default.jpg') {
    uploadedImageUrl = story.image_url;
    showImagePreview(story.image_url);
  } else {
    uploadedImageUrl = null;
    document.getElementById('image-preview').style.display = 'none';
  }
  
  // Remove story from list (will be re-added when form is submitted)
  stories = stories.filter(s => s.id !== id);
  renderStories();
  updateStats();
  
  showMessage('이야기가 편집 모드로 로드되었습니다.', 'info');
}

// Delete story
async function deleteStory(id) {
  if (confirm('정말로 이 이야기를 삭제하시겠습니까?')) {
    try {
      await deleteStoryAPI(id);
      stories = stories.filter(s => s.id !== id);
      
      // Update selected story if deleted
      if (selectedStoryId === id) {
        selectedStoryId = stories.length > 0 ? stories[0].id : null;
      }
      
      renderStories();
      updateStats();
      renderPreview();
      
      showMessage('이야기가 삭제되었습니다.', 'success');
    } catch (error) {
      showMessage('이야기 삭제에 실패했습니다: ' + error.message, 'error');
    }
  }
}

// Show message
function showMessage(message, type) {
  // Create message element
  const messageEl = document.createElement('div');
  messageEl.className = `status status--${type}`;
  messageEl.textContent = message;
  messageEl.style.position = 'fixed';
  messageEl.style.top = '20px';
  messageEl.style.right = '20px';
  messageEl.style.zIndex = '1000';
  
  document.body.appendChild(messageEl);
  
  // Remove after 3 seconds
  setTimeout(() => {
    if (messageEl.parentNode) {
      messageEl.parentNode.removeChild(messageEl);
    }
  }, 3000);
}