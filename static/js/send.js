// 문자 발송 페이지

let sendTemplates = [];
let sendCompanies = [];
let sendList = [];

async function loadSendPage() {
    const content = document.getElementById('page-content');
    content.innerHTML = `
        <h4>문자 발송</h4>

        <!-- 1. 템플릿 선택 -->
        <div class="card mb-3">
            <div class="card-header">
                <strong>1. 템플릿 선택</strong>
            </div>
            <div class="card-body">
                <select class="form-select" id="send-template" onchange="onTemplateChange()">
                    <option value="">템플릿을 선택하세요</option>
                </select>
                <div id="template-preview" class="mt-3" style="display: none;">
                    <div class="preview-box">
                        <div class="text-muted small mb-2">템플릿 내용:</div>
                        <pre id="template-content-preview" style="white-space: pre-wrap; font-family: inherit;"></pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- 2. 발송 대상 추가 -->
        <div class="card mb-3">
            <div class="card-header">
                <strong>2. 발송 대상 추가</strong>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-md-5">
                        <label class="form-label">발주사</label>
                        <input type="text" class="form-control" id="company-search-input" placeholder="발주사명 검색..." oninput="searchCompaniesForSend()">
                        <div id="company-search-results" class="list-group mt-2" style="max-height: 200px; overflow-y: auto; display: none;"></div>
                        <input type="hidden" id="selected-company-id">
                        <input type="text" class="form-control mt-2" id="selected-company-name" placeholder="선택된 발주사" readonly>
                    </div>
                    <div class="col-md-5">
                        <label class="form-label">캠페인명</label>
                        <input type="text" class="form-control" id="campaign-name" placeholder="캠페인명 입력">
                    </div>
                    <div class="col-md-2 d-flex align-items-end">
                        <button class="btn btn-primary w-100" onclick="addToSendList()">추가</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. 발송 목록 -->
        <div class="card mb-3">
            <div class="card-header d-flex justify-content-between align-items-center">
                <strong>3. 발송 목록 (<span id="send-list-count">0</span>건)</strong>
                <div>
                    <button class="btn btn-sm btn-outline-secondary" onclick="loadDraft()">불러오기</button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="saveDraft()">임시저장</button>
                </div>
            </div>
            <div class="card-body">
                <div id="send-list">
                    <div class="alert alert-info">
                        템플릿을 선택하고 발송 대상을 추가하세요.
                    </div>
                </div>
            </div>
        </div>

        <!-- 발송 버튼 -->
        <div class="text-end">
            <button class="btn btn-success btn-lg" onclick="sendBulkMessages()" id="send-btn" disabled>
                📱 일괄 발송
            </button>
        </div>

        <!-- 미리보기 모달 -->
        <div class="modal fade" id="previewModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">미리보기</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <strong>수신자:</strong> <span id="preview-company"></span> (<span id="preview-phone"></span>)
                        </div>
                        <div class="mb-3">
                            <strong>발송 내용:</strong>
                            <div class="preview-box mt-2">
                                <pre id="preview-message" style="white-space: pre-wrap; font-family: inherit;"></pre>
                            </div>
                        </div>
                        <div class="text-muted small">
                            글자수: <span id="preview-chars"></span>자 / 바이트: <span id="preview-bytes"></span>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    await loadTemplatesForSend();
    await loadCompaniesForSend();
}

async function loadTemplatesForSend() {
    try {
        sendTemplates = await apiCall('/api/templates');
        const select = document.getElementById('send-template');
        sendTemplates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = `[${template.category}] ${template.title}`;
            select.appendChild(option);
        });
    } catch (error) {
        alert('템플릿 목록을 불러오는데 실패했습니다: ' + error.message);
    }
}

async function loadCompaniesForSend() {
    try {
        sendCompanies = await apiCall('/api/companies');
    } catch (error) {
        alert('발주사 목록을 불러오는데 실패했습니다: ' + error.message);
    }
}

function onTemplateChange() {
    const templateId = document.getElementById('send-template').value;
    const previewDiv = document.getElementById('template-preview');

    if (templateId) {
        const template = sendTemplates.find(t => t.id == templateId);
        if (template) {
            document.getElementById('template-content-preview').textContent = template.content;
            previewDiv.style.display = 'block';
        }
    } else {
        previewDiv.style.display = 'none';
    }

    updateSendButton();
}

function searchCompaniesForSend() {
    const input = document.getElementById('company-search-input');
    const resultsDiv = document.getElementById('company-search-results');
    const query = input.value.toLowerCase();

    if (!query) {
        resultsDiv.style.display = 'none';
        return;
    }

    const filtered = sendCompanies.filter(c =>
        c.name.toLowerCase().includes(query) ||
        c.company_id.toLowerCase().includes(query)
    );

    if (filtered.length === 0) {
        resultsDiv.innerHTML = '<div class="list-group-item">검색 결과가 없습니다</div>';
        resultsDiv.style.display = 'block';
        return;
    }

    resultsDiv.innerHTML = filtered.map(company => `
        <button type="button" class="list-group-item list-group-item-action" onclick="selectCompany(${company.id}, '${escapeHtml(company.name)}')">
            ${escapeHtml(company.name)} (${escapeHtml(company.company_id)})
        </button>
    `).join('');
    resultsDiv.style.display = 'block';
}

function selectCompany(id, name) {
    document.getElementById('selected-company-id').value = id;
    document.getElementById('selected-company-name').value = name;
    document.getElementById('company-search-input').value = '';
    document.getElementById('company-search-results').style.display = 'none';
}

function addToSendList() {
    const templateId = document.getElementById('send-template').value;
    const companyId = document.getElementById('selected-company-id').value;
    const campaignName = document.getElementById('campaign-name').value;

    if (!templateId) {
        alert('템플릿을 선택하세요.');
        return;
    }

    if (!companyId) {
        alert('발주사를 선택하세요.');
        return;
    }

    if (!campaignName) {
        alert('캠페인명을 입력하세요.');
        return;
    }

    // 중복 체크
    const exists = sendList.find(item => item.company_id == companyId);
    if (exists) {
        if (!confirm('같은 발주사가 이미 목록에 있습니다. 추가하시겠습니까?')) {
            return;
        }
    }

    const company = sendCompanies.find(c => c.id == companyId);
    sendList.push({
        company_id: parseInt(companyId),
        company_name: company.name,
        campaign_name: campaignName
    });

    // 입력 초기화
    document.getElementById('selected-company-id').value = '';
    document.getElementById('selected-company-name').value = '';
    document.getElementById('campaign-name').value = '';

    renderSendList();
    updateSendButton();
}

function renderSendList() {
    const listDiv = document.getElementById('send-list');
    document.getElementById('send-list-count').textContent = sendList.length;

    if (sendList.length === 0) {
        listDiv.innerHTML = '<div class="alert alert-info">발송 대상이 없습니다.</div>';
        return;
    }

    listDiv.innerHTML = sendList.map((item, index) => `
        <div class="send-list-item d-flex justify-content-between align-items-center">
            <div>
                <strong>${index + 1}.</strong>
                ${escapeHtml(item.company_name)} - ${escapeHtml(item.campaign_name)}
            </div>
            <div>
                <button class="btn btn-sm btn-outline-primary" onclick="previewMessage(${index})">미리보기</button>
                <button class="btn btn-sm btn-outline-danger" onclick="removeFromSendList(${index})">삭제</button>
            </div>
        </div>
    `).join('');
}

function removeFromSendList(index) {
    sendList.splice(index, 1);
    renderSendList();
    updateSendButton();
}

async function previewMessage(index) {
    const templateId = document.getElementById('send-template').value;
    const item = sendList[index];

    try {
        const preview = await apiCall('/api/send/preview', 'POST', {
            template_id: parseInt(templateId),
            company_id: item.company_id,
            campaign_name: item.campaign_name
        });

        document.getElementById('preview-company').textContent = preview.company_name;
        document.getElementById('preview-phone').textContent = preview.phone;
        document.getElementById('preview-message').textContent = preview.message_content;
        document.getElementById('preview-chars').textContent = preview.char_count;
        document.getElementById('preview-bytes').textContent = preview.byte_count;

        new bootstrap.Modal(document.getElementById('previewModal')).show();
    } catch (error) {
        alert('미리보기 실패: ' + error.message);
    }
}

function updateSendButton() {
    const btn = document.getElementById('send-btn');
    const templateId = document.getElementById('send-template').value;

    btn.disabled = !templateId || sendList.length === 0;
}

async function sendBulkMessages() {
    const templateId = document.getElementById('send-template').value;

    if (!templateId || sendList.length === 0) {
        alert('템플릿과 발송 대상을 확인하세요.');
        return;
    }

    if (!confirm(`${sendList.length}건의 문자를 발송하시겠습니까?`)) {
        return;
    }

    try {
        const result = await apiCall('/api/send/bulk', 'POST', {
            template_id: parseInt(templateId),
            items: sendList
        });

        alert(`발송 완료\n성공: ${result.success}건\n실패: ${result.fail}건`);

        // 발송 목록 초기화
        sendList = [];
        renderSendList();
        updateSendButton();
    } catch (error) {
        alert('발송 실패: ' + error.message);
    }
}

async function saveDraft() {
    const templateId = document.getElementById('send-template').value;

    if (!templateId || sendList.length === 0) {
        alert('템플릿과 발송 대상을 먼저 설정하세요.');
        return;
    }

    try {
        await apiCall('/api/draft', 'POST', {
            template_id: parseInt(templateId),
            items: sendList
        });

        alert('임시저장되었습니다.');
    } catch (error) {
        alert('임시저장 실패: ' + error.message);
    }
}

async function loadDraft() {
    if (sendList.length > 0) {
        if (!confirm('현재 작업 내용이 사라집니다. 불러오시겠습니까?')) {
            return;
        }
    }

    try {
        const draft = await apiCall('/api/draft');
        const items = JSON.parse(draft.items);

        // 템플릿 설정
        document.getElementById('send-template').value = draft.template_id;
        onTemplateChange();

        // 발송 목록 설정
        sendList = items.map(item => {
            const company = sendCompanies.find(c => c.id === item.company_id);
            return {
                company_id: item.company_id,
                company_name: company ? company.name : '알 수 없음',
                campaign_name: item.campaign_name
            };
        });

        renderSendList();
        updateSendButton();

        alert('임시저장 내용을 불러왔습니다.');
    } catch (error) {
        alert('불러오기 실패: ' + error.message);
    }
}