// 템플릿 관리 페이지

let templateList = [];

async function loadTemplatesPage() {
    const content = document.getElementById('page-content');
    content.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4>템플릿 관리</h4>
            <button class="btn btn-primary" onclick="showTemplateModal()" id="add-template-btn">
                <i class="bi bi-plus"></i> 템플릿 등록
            </button>
        </div>

        <div class="alert alert-info">
            <strong>사용 가능한 변수:</strong><br>
            • {발주사명} - 모든 템플릿에서 사용 가능<br>
            • {캠페인명} - 검수완료, 진행률50%, 진행률100%, 기타(캠페인명사용) 템플릿에서만 사용<br>
            • "기타" 카테고리는 {발주사명}만 사용 가능<br>
            <strong>최대 등록 개수:</strong> <span id="template-count">0</span> / 10개
        </div>

        <div id="templates-list">
            <div class="text-center py-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">로딩중...</span>
                </div>
            </div>
        </div>

        <!-- 템플릿 등록/수정 모달 -->
        <div class="modal fade" id="templateModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="templateModalTitle">템플릿 등록</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="template-form">
                            <input type="hidden" id="template-id">
                            <div class="mb-3">
                                <label class="form-label">카테고리 *</label>
                                <select class="form-select" id="template-category" required onchange="onTemplateCategoryChange()">
                                    <option value="">선택하세요</option>
                                    <option value="검수완료">검수완료</option>
                                    <option value="진행률50%">진행률50%</option>
                                    <option value="진행률100%">진행률100%</option>
                                    <option value="기타">기타 (캠페인명 사용 안함)</option>
                                    <option value="기타(캠페인명사용)">기타 (캠페인명 사용함)</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">제목 *</label>
                                <input type="text" class="form-control" id="template-title" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">내용 *</label>
                                <textarea class="form-control" id="template-content" rows="6" required placeholder="예) {발주사명}님, {캠페인명} 검수가 완료되었습니다."></textarea>
                                <div class="form-text" id="template-variable-guide">
                                    변수: {발주사명}, {캠페인명}
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                        <button type="button" class="btn btn-primary" onclick="saveTemplate()">저장</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadTemplates();
}

async function loadTemplates() {
    try {
        templateList = await apiCall('/api/templates');
        const countData = await apiCall('/api/templates/count');

        document.getElementById('template-count').textContent = countData.count;

        // 최대 개수 제한 체크
        const addBtn = document.getElementById('add-template-btn');
        if (addBtn) {
            if (!countData.can_create) {
                addBtn.disabled = true;
                addBtn.title = '템플릿은 최대 10개까지만 등록할 수 있습니다';
            } else {
                addBtn.disabled = false;
                addBtn.title = '';
            }
        }

        renderTemplates();
    } catch (error) {
        document.getElementById('templates-list').innerHTML = `
            <div class="alert alert-danger">
                템플릿 목록을 불러오는데 실패했습니다: ${error.message}
            </div>
        `;
    }
}

function renderTemplates() {
    const listDiv = document.getElementById('templates-list');

    if (templateList.length === 0) {
        listDiv.innerHTML = `
            <div class="alert alert-info">
                등록된 템플릿이 없습니다.
            </div>
        `;
        return;
    }

    const cardsHtml = templateList.map(template => `
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
                <div>
                    <span class="badge bg-primary">${escapeHtml(template.category)}</span>
                    <strong>${escapeHtml(template.title)}</strong>
                </div>
                <div>
                    <button class="btn btn-sm btn-outline-primary" onclick="editTemplate(${template.id})">
                        수정
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTemplate(${template.id}, '${escapeHtml(template.title)}')">
                        삭제
                    </button>
                </div>
            </div>
            <div class="card-body">
                <pre class="mb-0" style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(template.content)}</pre>
                <div class="text-muted small mt-2">
                    등록일: ${new Date(template.created_at).toLocaleString()}
                </div>
            </div>
        </div>
    `).join('');

    listDiv.innerHTML = cardsHtml;
}

function showTemplateModal(templateData = null) {
    const modal = new bootstrap.Modal(document.getElementById('templateModal'));
    const form = document.getElementById('template-form');
    form.reset();

    if (templateData) {
        document.getElementById('templateModalTitle').textContent = '템플릿 수정';
        document.getElementById('template-id').value = templateData.id;
        document.getElementById('template-category').value = templateData.category;
        document.getElementById('template-title').value = templateData.title;
        document.getElementById('template-content').value = templateData.content;
    } else {
        document.getElementById('templateModalTitle').textContent = '템플릿 등록';
        document.getElementById('template-id').value = '';
    }

    modal.show();
}

async function editTemplate(id) {
    const template = templateList.find(t => t.id === id);
    if (template) {
        showTemplateModal(template);
    }
}

async function saveTemplate() {
    const id = document.getElementById('template-id').value;
    const data = {
        category: document.getElementById('template-category').value,
        title: document.getElementById('template-title').value,
        content: document.getElementById('template-content').value
    };

    if (!data.category || !data.title || !data.content) {
        alert('모든 필수 항목을 입력해주세요.');
        return;
    }

    try {
        if (id) {
            await apiCall(`/api/templates/${id}`, 'PUT', data);
            alert('템플릿이 수정되었습니다.');
        } else {
            await apiCall('/api/templates', 'POST', data);
            alert('템플릿이 등록되었습니다.');
        }

        bootstrap.Modal.getInstance(document.getElementById('templateModal')).hide();
        loadTemplates();
    } catch (error) {
        alert('저장 실패: ' + error.message);
    }
}

async function deleteTemplate(id, title) {
    if (!confirm(`"${title}" 템플릿을 삭제하시겠습니까?`)) {
        return;
    }

    try {
        await apiCall(`/api/templates/${id}`, 'DELETE');
        alert('템플릿이 삭제되었습니다.');
        loadTemplates();
    } catch (error) {
        alert('삭제 실패: ' + error.message);
    }
}

// 템플릿 카테고리 변경 시 가이드 업데이트
function onTemplateCategoryChange() {
    const category = document.getElementById('template-category').value;
    const guideDiv = document.getElementById('template-variable-guide');
    const contentTextarea = document.getElementById('template-content');

    if (category === '기타') {
        guideDiv.innerHTML = '변수: {발주사명} (캠페인명 변수는 사용하지 마세요)';
        guideDiv.className = 'form-text text-warning';
        contentTextarea.placeholder = '예) {발주사명}님, 새해 복 많이 받으세요!';
    } else if (category === '기타(캠페인명사용)') {
        guideDiv.innerHTML = '변수: {발주사명}, {캠페인명}';
        guideDiv.className = 'form-text';
        contentTextarea.placeholder = '예) {발주사명}님, {캠페인명} 관련 문의가 있습니다. 전화 요청 드립니다.';
    } else {
        guideDiv.innerHTML = '변수: {발주사명}, {캠페인명}';
        guideDiv.className = 'form-text';
        contentTextarea.placeholder = '예) {발주사명}님, {캠페인명} 검수가 완료되었습니다.';
    }
}