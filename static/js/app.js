// 전역 상태
const state = {
    currentUser: null,
    currentPage: 'send'
};

// API 호출 헬퍼
async function apiCall(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include'
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    // 204 No Content 응답은 body가 없으므로 JSON 파싱 건너뛰기
    let data = null;
    if (response.status !== 204) {
        data = await response.json();
    }

    if (!response.ok) {
        // 401 에러 시 자동 로그아웃 처리
        if (response.status === 401 && state.currentUser) {
            console.log('[AUTH] 세션 만료 - 자동 로그아웃');
            state.currentUser = null;
            showLoginPage();
        }
        throw new Error(data?.detail || '요청 실패');
    }

    return data;
}

// 로그인 폼
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    try {
        const result = await apiCall('/api/auth/login', 'POST', data);
        alert('로그인 성공!');
        state.currentUser = result.user;
        showMainPage();
    } catch (error) {
        alert('로그인 실패: ' + error.message);
    }
});

// 회원가입 폼
document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        password: formData.get('password'),
        name: formData.get('name')
    };

    try {
        await apiCall('/api/auth/signup', 'POST', data);
        alert('회원가입 성공! 로그인해주세요.');
        document.getElementById('login-tab').click();
        e.target.reset();
    } catch (error) {
        alert('회원가입 실패: ' + error.message);
    }
});

// 로그아웃
document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await apiCall('/api/auth/logout', 'POST');
        state.currentUser = null;
        showLoginPage();
    } catch (error) {
        alert('로그아웃 실패: ' + error.message);
    }
});

// 페이지 전환
function showLoginPage() {
    document.getElementById('login-page').classList.remove('d-none');
    document.getElementById('main-page').classList.add('d-none');
}

function showMainPage() {
    document.getElementById('login-page').classList.add('d-none');
    document.getElementById('main-page').classList.remove('d-none');
    document.getElementById('user-name').textContent = state.currentUser.name + '님';
    loadPage('send');
}

// 페이지 로드
function loadPage(page) {
    state.currentPage = page;

    // 탭 활성화
    document.querySelectorAll('.nav-tabs .nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });

    const content = document.getElementById('page-content');

    switch(page) {
        case 'send':
            if (typeof loadSendPage === 'function') {
                loadSendPage();
            } else {
                content.innerHTML = '<div class="alert alert-warning">로딩 중...</div>';
                setTimeout(() => loadPage(page), 100);
            }
            break;
        case 'companies':
            if (typeof loadCompaniesPage === 'function') {
                loadCompaniesPage();
            } else {
                content.innerHTML = '<div class="alert alert-warning">로딩 중...</div>';
                setTimeout(() => loadPage(page), 100);
            }
            break;
        case 'templates':
            if (typeof loadTemplatesPage === 'function') {
                loadTemplatesPage();
            } else {
                content.innerHTML = '<div class="alert alert-warning">로딩 중...</div>';
                setTimeout(() => loadPage(page), 100);
            }
            break;
    }
}

// HTML escaping 헬퍼 함수
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 탭 클릭 이벤트
document.querySelectorAll('.nav-tabs .nav-link').forEach(link => {
    link.addEventListener('click', () => {
        loadPage(link.dataset.page);
    });
});

// 페이지 로드 시 로그인 상태 확인
async function checkAuth() {
    try {
        const user = await apiCall('/api/auth/me');
        state.currentUser = user;
        showMainPage();
    } catch (error) {
        showLoginPage();
    }
}

// 초기화
checkAuth();