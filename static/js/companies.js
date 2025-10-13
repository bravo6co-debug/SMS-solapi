// 발주사 관리 페이지

let companyList = [];

async function loadCompaniesPage() {
    const content = document.getElementById('page-content');
    content.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4>발주사 관리</h4>
            <div>
                <button class="btn btn-success me-2" onclick="downloadTemplate()">
                    📥 엑셀 템플릿 다운로드
                </button>
                <button class="btn btn-info me-2" onclick="showBulkUploadModal()">
                    📤 엑셀 대량 등록
                </button>
                <button class="btn btn-primary" onclick="showCompanyModal()">
                    <i class="bi bi-plus"></i> 발주사 등록
                </button>
            </div>
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

        <!-- 엑셀 대량 등록 모달 -->
        <div class="modal fade" id="bulkUploadModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">엑셀 대량 등록</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <strong>업로드 방법:</strong><br>
                            1. "엑셀 템플릿 다운로드" 버튼을 클릭하여 템플릿을 다운로드합니다<br>
                            2. 템플릿에 발주사 정보를 입력합니다 (최대 500개)<br>
                            3. 작성한 파일을 업로드합니다<br><br>
                            <strong>필수 항목:</strong> 발주사명, 전화번호, 발주사아이디<br>
                            <strong>전화번호 형식:</strong> 01012345678 (하이픈 없이)
                        </div>

                        <div class="mb-3">
                            <label class="form-label">엑셀 파일 선택</label>
                            <input type="file" class="form-control" id="excel-file" accept=".xlsx,.xls">
                            <div class="form-text">최대 파일 크기: 5MB, 최대 행 수: 500개</div>
                        </div>

                        <div id="upload-progress" style="display: none;">
                            <div class="progress">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%">
                                    업로드 중...
                                </div>
                            </div>
                        </div>

                        <div id="upload-result" style="display: none;">
                            <!-- 업로드 결과가 표시될 영역 -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                        <button type="button" class="btn btn-primary" onclick="uploadExcelFile()" id="upload-btn">업로드</button>
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

// 엑셀 템플릿 다운로드
async function downloadTemplate() {
    try {
        const response = await fetch('/api/companies/template/download', {
            method: 'GET',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('템플릿 다운로드 실패');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'company_upload_template.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert('템플릿 다운로드 실패: ' + error.message);
    }
}

// 대량 등록 모달 표시
function showBulkUploadModal() {
    const modal = new bootstrap.Modal(document.getElementById('bulkUploadModal'));

    // 초기화
    document.getElementById('excel-file').value = '';
    document.getElementById('upload-progress').style.display = 'none';
    document.getElementById('upload-result').style.display = 'none';
    document.getElementById('upload-btn').disabled = false;

    modal.show();
}

// 엑셀 파일 업로드
async function uploadExcelFile() {
    const fileInput = document.getElementById('excel-file');
    const file = fileInput.files[0];

    if (!file) {
        alert('파일을 선택해주세요.');
        return;
    }

    // 파일 확장자 체크
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        alert('엑셀 파일만 업로드 가능합니다 (.xlsx, .xls)');
        return;
    }

    // 파일 크기 체크 (5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('파일 크기는 5MB를 초과할 수 없습니다.');
        return;
    }

    // FormData 생성
    const formData = new FormData();
    formData.append('file', file);

    // UI 업데이트
    document.getElementById('upload-progress').style.display = 'block';
    document.getElementById('upload-result').style.display = 'none';
    document.getElementById('upload-btn').disabled = true;

    try {
        const response = await fetch('/api/companies/bulk-upload', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || '업로드 실패');
        }

        // 결과 표시
        displayUploadResult(result);

        // 성공한 건이 있으면 목록 새로고침
        if (result.success_count > 0) {
            loadCompanies();
        }

    } catch (error) {
        alert('업로드 실패: ' + error.message);
    } finally {
        document.getElementById('upload-progress').style.display = 'none';
        document.getElementById('upload-btn').disabled = false;
    }
}

// 업로드 결과 표시
function displayUploadResult(result) {
    const resultDiv = document.getElementById('upload-result');

    let html = `
        <div class="alert ${result.error_count === 0 ? 'alert-success' : 'alert-warning'}">
            <h6>업로드 완료</h6>
            <p class="mb-0">
                <strong>성공:</strong> ${result.success_count}건<br>
                <strong>실패:</strong> ${result.error_count}건
            </p>
        </div>
    `;

    if (result.errors && result.errors.length > 0) {
        html += `
            <div class="mt-3">
                <h6>오류 상세 (최대 20건 표시)</h6>
                <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                    <table class="table table-sm table-bordered">
                        <thead>
                            <tr>
                                <th>행</th>
                                <th>발주사명</th>
                                <th>전화번호</th>
                                <th>아이디</th>
                                <th>오류 내용</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${result.errors.slice(0, 20).map(err => `
                                <tr>
                                    <td>${err.row}</td>
                                    <td>${escapeHtml(err.name || '')}</td>
                                    <td>${escapeHtml(err.phone || '')}</td>
                                    <td>${escapeHtml(err.company_id || '')}</td>
                                    <td class="text-danger">${escapeHtml(err.error)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                ${result.errors.length > 20 ? `<p class="text-muted small">외 ${result.errors.length - 20}건의 오류가 더 있습니다.</p>` : ''}
            </div>
        `;
    }

    resultDiv.innerHTML = html;
    resultDiv.style.display = 'block';
}