const WISHLIST_KEY = 'movieWishlist';
const POSTER_BASE_URL = 'https://image.tmdb.org/t/p/w500';

const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
const searchStatus = document.getElementById('search-status');
const wishlistResults = document.getElementById('wishlist-results');
const wishlistStatus = document.getElementById('wishlist-status');
const wishlistCount = document.getElementById('wishlist-count');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// ---------- 찜 목록 (localStorage) ----------

function getWishlist() {
  const raw = localStorage.getItem(WISHLIST_KEY);
  return raw ? JSON.parse(raw) : [];
}

function saveWishlist(list) {
  localStorage.setItem(WISHLIST_KEY, JSON.stringify(list));
  updateWishlistCount();
}

function isInWishlist(movieId) {
  return getWishlist().some((movie) => movie.id === movieId);
}

function toggleWishlist(movie) {
  const list = getWishlist();
  const index = list.findIndex((m) => m.id === movie.id);

  if (index === -1) {
    list.push(movie);
  } else {
    list.splice(index, 1);
  }

  saveWishlist(list);
  return index === -1; // true면 새로 추가된 것
}

function updateWishlistCount() {
  wishlistCount.textContent = `(${getWishlist().length})`;
}

// ---------- 카드 렌더링 ----------

function createMovieCard(movie) {
  const card = document.createElement('div');
  card.className = 'movie-card';

  const posterWrap = document.createElement('div');
  posterWrap.className = 'poster-wrap';

  if (movie.poster_path) {
    const img = document.createElement('img');
    img.src = `${POSTER_BASE_URL}${movie.poster_path}`;
    img.alt = movie.title;
    posterWrap.appendChild(img);
  } else {
    const noPoster = document.createElement('div');
    noPoster.className = 'no-poster';
    noPoster.textContent = '포스터 없음';
    posterWrap.appendChild(noPoster);
  }

  const wishBtn = document.createElement('button');
  wishBtn.className = 'wishlist-btn';
  wishBtn.type = 'button';
  wishBtn.setAttribute('aria-label', '찜하기');
  const inWishlist = isInWishlist(movie.id);
  wishBtn.textContent = inWishlist ? '♥' : '♡';
  if (inWishlist) wishBtn.classList.add('active');

  wishBtn.addEventListener('click', () => {
    const added = toggleWishlist({
      id: movie.id,
      title: movie.title,
      poster_path: movie.poster_path,
      release_date: movie.release_date,
      vote_average: movie.vote_average,
    });

    wishBtn.textContent = added ? '♥' : '♡';
    wishBtn.classList.toggle('active', added);

    // 찜 목록 탭이 열려있으면 즉시 갱신
    if (document.getElementById('wishlist-tab').classList.contains('active')) {
      renderWishlist();
    }
  });

  posterWrap.appendChild(wishBtn);

  const info = document.createElement('div');
  info.className = 'movie-info';

  const title = document.createElement('div');
  title.className = 'title';
  title.textContent = movie.title;

  const meta = document.createElement('div');
  meta.className = 'meta';

  const year = document.createElement('span');
  year.textContent = movie.release_date ? movie.release_date.slice(0, 4) : '개봉일 미정';

  const rating = document.createElement('span');
  rating.className = 'rating';
  rating.textContent = `★ ${movie.vote_average ? movie.vote_average.toFixed(1) : '-'}`;

  meta.appendChild(year);
  meta.appendChild(rating);

  info.appendChild(title);
  info.appendChild(meta);

  card.appendChild(posterWrap);
  card.appendChild(info);

  return card;
}

function renderMovies(movies, container) {
  container.innerHTML = '';
  movies.forEach((movie) => container.appendChild(createMovieCard(movie)));
}

// ---------- 검색 ----------

async function searchMovies(query) {
  searchStatus.textContent = '검색 중...';
  searchResults.innerHTML = '';

  try {
    const res = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
    const data = await res.json();

    if (!res.ok) {
      searchStatus.textContent = data.status_message || '검색 중 오류가 발생했습니다.';
      return;
    }

    if (!data.results || data.results.length === 0) {
      searchStatus.textContent = '검색 결과가 없습니다.';
      return;
    }

    searchStatus.textContent = `"${query}" 검색 결과 ${data.total_results}건`;
    renderMovies(data.results, searchResults);
  } catch (err) {
    console.error(err);
    searchStatus.textContent = '서버와 통신 중 오류가 발생했습니다.';
  }
}

async function loadPopularMovies() {
  searchStatus.textContent = '인기 영화를 불러오는 중...';

  try {
    const res = await fetch('/api/popular');
    const data = await res.json();

    if (!res.ok) {
      searchStatus.textContent = data.status_message || '불러오기 중 오류가 발생했습니다.';
      return;
    }

    searchStatus.textContent = '지금 인기 있는 영화';
    renderMovies(data.results, searchResults);
  } catch (err) {
    console.error(err);
    searchStatus.textContent = '서버와 통신 중 오류가 발생했습니다.';
  }
}

searchForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const query = searchInput.value.trim();
  if (query) searchMovies(query);
});

// ---------- 찜 목록 탭 ----------

function renderWishlist() {
  const list = getWishlist();

  if (list.length === 0) {
    wishlistStatus.textContent = '찜한 영화가 없습니다.';
    wishlistResults.innerHTML = '';
    return;
  }

  wishlistStatus.textContent = `찜한 영화 ${list.length}건`;
  renderMovies(list, wishlistResults);
}

// ---------- 탭 전환 ----------

tabButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    tabButtons.forEach((b) => b.classList.remove('active'));
    tabContents.forEach((c) => c.classList.remove('active'));

    btn.classList.add('active');
    document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');

    if (btn.dataset.tab === 'wishlist') {
      renderWishlist();
    }
  });
});

// ---------- 초기 실행 ----------

updateWishlistCount();
loadPopularMovies();
