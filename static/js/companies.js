// 발주사 관리 페이지

let companyList = [];

async function loadCompaniesPage() {
    const content = document.getElementById('page-content');
    content.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4>발주사 관리</h4>
            <button class="btn btn-primary" onclick="showCompanyModal()">
                <i class="bi bi-plus"></i> 발주사 등록
            </button>
        </div>

        <div class="mb-3">
            <div class="input-group">
                <input type="text" class="form-control" id="company-search" placeholder="발주사명 또는 아이디로 검색">
                <button class="btn btn-outline-secondary" onclick="searchCompanies()">
                    🔍 검색
                </button>
            </div>
        </div>

        <div id="companies-list">
            <div class="text-center py-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">로딩중...</span>
                </div>
            </div>
        </div>

        <!-- 발주사 등록/수정 모달 -->
        <div class="modal fade" id="companyModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="companyModalTitle">발주사 등록</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="company-form">
                            <input type="hidden" id="company-id">
                            <div class="mb-3">
                                <label class="form-label">발주사명 *</label>
                                <input type="text" class="form-control" id="company-name" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">전화번호 *</label>
                                <input type="tel" class="form-control" id="company-phone" placeholder="01012345678" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">발주사 아이디 *</label>
                                <input type="text" class="form-control" id="company-company-id" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">메모</label>
                                <textarea class="form-control" id="company-memo" rows="3"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                        <button type="button" class="btn btn-primary" onclick="saveCompany()">저장</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadCompanies();
}

async function loadCompanies(search = '') {
    try {
        const url = search
            ? `/api/companies?search=${encodeURIComponent(search)}`
            : '/api/companies';

        companyList = await apiCall(url);
        renderCompanies();
    } catch (error) {
        document.getElementById('companies-list').innerHTML = `
            <div class="alert alert-danger">
                발주사 목록을 불러오는데 실패했습니다: ${error.message}
            </div>
        `;
    }
}

function renderCompanies() {
    const listDiv = document.getElementById('companies-list');

    if (companyList.length === 0) {
        listDiv.innerHTML = `
            <div class="alert alert-info">
                등록된 발주사가 없습니다.
            </div>
        `;
        return;
    }

    const tableHtml = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>발주사명</th>
                        <th>전화번호</th>
                        <th>아이디</th>
                        <th>메모</th>
                        <th>등록일</th>
                        <th>액션</th>
                    </tr>
                </thead>
                <tbody>
                    ${companyList.map(company => `
                        <tr>
                            <td>${escapeHtml(company.name)}</td>
                            <td>${escapeHtml(company.phone)}</td>
                            <td>${escapeHtml(company.company_id)}</td>
                            <td>${company.memo ? escapeHtml(company.memo.substring(0, 20)) + (company.memo.length > 20 ? '...' : '') : '-'}</td>
                            <td>${new Date(company.created_at).toLocaleDateString()}</td>
                            <td class="table-actions">
                                <button class="btn btn-sm btn-outline-primary" onclick="editCompany(${company.id})">
                                    수정
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteCompany(${company.id}, '${escapeHtml(company.name)}')">
                                    삭제
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <div class="text-muted">
            총 ${companyList.length}개
        </div>
    `;

    listDiv.innerHTML = tableHtml;
}

function searchCompanies() {
    const search = document.getElementById('company-search').value;
    loadCompanies(search);
}

function showCompanyModal(companyData = null) {
    const modal = new bootstrap.Modal(document.getElementById('companyModal'));
    const form = document.getElementById('company-form');
    form.reset();

    if (companyData) {
        document.getElementById('companyModalTitle').textContent = '발주사 수정';
        document.getElementById('company-id').value = companyData.id;
        document.getElementById('company-name').value = companyData.name;
        document.getElementById('company-phone').value = companyData.phone;
        document.getElementById('company-company-id').value = companyData.company_id;
        document.getElementById('company-memo').value = companyData.memo || '';
    } else {
        document.getElementById('companyModalTitle').textContent = '발주사 등록';
        document.getElementById('company-id').value = '';
    }

    modal.show();
}

async function editCompany(id) {
    const company = companyList.find(c => c.id === id);
    if (company) {
        showCompanyModal(company);
    }
}

async function saveCompany() {
    const id = document.getElementById('company-id').value;
    const data = {
        name: document.getElementById('company-name').value,
        phone: document.getElementById('company-phone').value,
        company_id: document.getElementById('company-company-id').value,
        memo: document.getElementById('company-memo').value || null
    };

    try {
        if (id) {
            await apiCall(`/api/companies/${id}`, 'PUT', data);
            alert('발주사가 수정되었습니다.');
        } else {
            await apiCall('/api/companies', 'POST', data);
            alert('발주사가 등록되었습니다.');
        }

        bootstrap.Modal.getInstance(document.getElementById('companyModal')).hide();
        loadCompanies();
    } catch (error) {
        alert('저장 실패: ' + error.message);
    }
}

async function deleteCompany(id, name) {
    if (!confirm(`"${name}" 발주사를 삭제하시겠습니까?`)) {
        return;
    }

    try {
        await apiCall(`/api/companies/${id}`, 'DELETE');
        alert('발주사가 삭제되었습니다.');
        loadCompanies();
    } catch (error) {
        alert('삭제 실패: ' + error.message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}