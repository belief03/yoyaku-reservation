const API_BASE = 'http://localhost:8000/api/v1';

// タブ切り替え
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // すべてのタブを非表示
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // すべてのボタンからactiveクラスを削除
        document.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.remove('active');
        });
        
        // 選択されたタブを表示
        document.getElementById(`${tabName}-tab`).classList.add('active');
        btn.classList.add('active');
        
        // タブに応じたデータを読み込む
        if (tabName === 'services') {
            loadServices();
        } else if (tabName === 'reservation') {
            loadServicesForReservation();
            loadStylists();
            setupDatePicker();
        } else if (tabName === 'products') {
            loadProducts();
        } else if (tabName === 'order') {
            loadServicesForOrder();
            loadProductsForOrder();
        } else if (tabName === 'coupons') {
            loadCoupons();
        } else if (tabName === 'campaigns') {
            loadCampaigns();
        } else if (tabName === 'stylists') {
            loadStylists();
        }
    });
});

// サービス一覧を読み込む
async function loadServices() {
    const container = document.getElementById('services-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/services/`);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = data.items.map((service, index) => `
                <div class="service-card" style="animation-delay: ${index * 0.1}s">
                    <h3>${service.name || 'サービス名'}</h3>
                    <div class="service-price">¥${(service.price || 0).toLocaleString()}</div>
                    <div class="service-duration">⏱️ 所要時間: ${service.duration_minutes || 0}分</div>
                    ${service.description ? `<div class="service-description">${service.description}</div>` : ''}
                    ${service.category ? `<div style="margin-top: 12px;"><span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600;">${service.category}</span></div>` : ''}
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="info-text">サービスが見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="info-text error">エラー: ${error.message}</p>`;
    }
}

// 予約フォーム用にサービスを読み込む
async function loadServicesForReservation() {
    const select = document.getElementById('service-select');
    
    try {
        const response = await fetch(`${API_BASE}/services/`);
        const data = await response.json();
        
        select.innerHTML = '<option value="">選択してください</option>';
        if (data.items) {
            data.items.forEach(service => {
                const option = document.createElement('option');
                option.value = service.id;
                option.textContent = `${service.name} - ¥${(service.price || 0).toLocaleString()} (${service.duration_minutes || 0}分)`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('サービス読み込みエラー:', error);
    }
}

// スタイリスト一覧を読み込む
async function loadStylists() {
    const container = document.getElementById('stylists-list');
    if (container) {
        container.innerHTML = '<div class="loading">読み込み中...</div>';
    }
    
    const select = document.getElementById('stylist-select');
    
    try {
        const response = await fetch(`${API_BASE}/stylists/`);
        const data = await response.json();
        
        if (container && data.items && data.items.length > 0) {
            container.innerHTML = data.items.map(stylist => `
                <div class="stylist-card">
                    <h3>${stylist.name || 'スタイリスト名'}</h3>
                    ${stylist.specialty ? `<div class="stylist-specialty">${stylist.specialty}</div>` : ''}
                    ${stylist.bio ? `<p style="margin-top: 10px; color: #666; font-size: 0.9em;">${stylist.bio}</p>` : ''}
                </div>
            `).join('');
        } else if (container) {
            container.innerHTML = '<p class="info-text">スタイリストが見つかりませんでした</p>';
        }
        
        // セレクトボックスに追加
        if (select) {
            select.innerHTML = '<option value="">指定なし</option>';
            if (data.items) {
                data.items.forEach(stylist => {
                    const option = document.createElement('option');
                    option.value = stylist.id;
                    option.textContent = stylist.name || 'スタイリスト名';
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        if (container) {
            container.innerHTML = `<p class="info-text error">エラー: ${error.message}</p>`;
        }
        console.error('スタイリスト読み込みエラー:', error);
    }
}

// 日付ピッカーの設定
function setupDatePicker() {
    const dateInput = document.getElementById('reservation-date');
    const today = new Date();
    const maxDate = new Date();
    maxDate.setDate(today.getDate() + 90); // 90日後まで
    
    dateInput.min = today.toISOString().split('T')[0];
    dateInput.max = maxDate.toISOString().split('T')[0];
    
    dateInput.addEventListener('change', () => {
        loadAvailableTimeSlots(dateInput.value);
    });
}

// 利用可能な時間枠を読み込む
async function loadAvailableTimeSlots(date) {
    const timeSelect = document.getElementById('reservation-time');
    const serviceSelect = document.getElementById('service-select');
    
    if (!date || !serviceSelect.value) {
        timeSelect.innerHTML = '<option value="">まず日付とサービスを選択してください</option>';
        return;
    }
    
    try {
        const serviceId = serviceSelect.value;
        const response = await fetch(`${API_BASE}/reservations/availability/slots?date=${date}&service_id=${serviceId}`);
        const data = await response.json();
        
        timeSelect.innerHTML = '<option value="">選択してください</option>';
        if (data.slots) {
            data.slots.forEach(slot => {
                if (slot.available) {
                    const option = document.createElement('option');
                    const startTime = new Date(slot.start_time);
                    const timeStr = startTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
                    option.value = slot.start_time;
                    option.textContent = timeStr;
                    timeSelect.appendChild(option);
                }
            });
        }
    } catch (error) {
        timeSelect.innerHTML = '<option value="">時間枠の取得に失敗しました</option>';
        console.error('時間枠読み込みエラー:', error);
    }
}

// サービス選択時に時間枠を更新
document.getElementById('service-select')?.addEventListener('change', () => {
    const date = document.getElementById('reservation-date').value;
    if (date) {
        loadAvailableTimeSlots(date);
    }
});

// 予約フォーム送信
document.getElementById('reservation-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const resultDiv = document.getElementById('reservation-result');
    resultDiv.className = 'result-message';
    resultDiv.textContent = '予約処理中...';
    resultDiv.style.display = 'block';
    
    // まず顧客を作成または取得
    const email = document.getElementById('customer-email').value;
    const name = document.getElementById('customer-name').value;
    const phone = document.getElementById('customer-phone').value;
    
    try {
        // 顧客を検索または作成
        let customerId;
        const customerResponse = await fetch(`${API_BASE}/customers/?email=${encodeURIComponent(email)}`);
        const customerData = await customerResponse.json();
        
        if (customerData.items && customerData.items.length > 0) {
            customerId = customerData.items[0].id;
        } else {
            // 新規顧客作成
            const createCustomerResponse = await fetch(`${API_BASE}/customers/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: email,
                    name: name || null,
                    phone: phone || null
                })
            });
            const newCustomer = await createCustomerResponse.json();
            customerId = newCustomer.id;
        }
        
        // サービス情報を取得してduration_minutesを取得
        const serviceId = document.getElementById('service-select').value;
        const serviceResponse = await fetch(`${API_BASE}/services/${serviceId}`);
        const service = await serviceResponse.json();
        
        // 予約を作成
        const reservationData = {
            customer_id: customerId,
            service_id: serviceId,
            stylist_id: document.getElementById('stylist-select').value || null,
            reservation_datetime: document.getElementById('reservation-time').value,
            duration_minutes: service.duration_minutes || 30,
            notes: document.getElementById('notes').value || null
        };
        
        const reservationResponse = await fetch(`${API_BASE}/reservations/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reservationData)
        });
        
        if (reservationResponse.ok) {
            const reservation = await reservationResponse.json();
            resultDiv.className = 'result-message success';
            resultDiv.innerHTML = `
                <strong>✅ 予約が完了しました！</strong><br>
                予約ID: ${reservation.id}<br>
                日時: ${new Date(reservation.reservation_datetime).toLocaleString('ja-JP')}
            `;
            document.getElementById('reservation-form').reset();
        } else {
            const error = await reservationResponse.json();
            resultDiv.className = 'result-message error';
            resultDiv.textContent = `エラー: ${error.detail || error.message || '予約に失敗しました'}`;
        }
    } catch (error) {
        resultDiv.className = 'result-message error';
        resultDiv.textContent = `エラー: ${error.message}`;
    }
});

// 予約履歴検索
document.getElementById('search-history-btn')?.addEventListener('click', async () => {
    const email = document.getElementById('history-email').value;
    const container = document.getElementById('history-list');
    
    if (!email) {
        container.innerHTML = '<p class="info-text">メールアドレスを入力してください</p>';
        return;
    }
    
    container.innerHTML = '<div class="loading">検索中...</div>';
    
    try {
        // 顧客を検索
        const customerResponse = await fetch(`${API_BASE}/customers/?email=${encodeURIComponent(email)}`);
        const customerData = await customerResponse.json();
        
        if (!customerData.items || customerData.items.length === 0) {
            container.innerHTML = '<p class="info-text">該当する顧客が見つかりませんでした</p>';
            return;
        }
        
        const customerId = customerData.items[0].id;
        
        // 予約履歴を取得
        const reservationResponse = await fetch(`${API_BASE}/reservations/?customer_id=${customerId}`);
        const reservationData = await reservationResponse.json();
        
        if (reservationData.items && reservationData.items.length > 0) {
            container.innerHTML = reservationData.items.map(reservation => {
                const date = new Date(reservation.reservation_datetime);
                const statusLabels = {
                    'pending': '保留中',
                    'confirmed': '確認済み',
                    'completed': '完了',
                    'cancelled': 'キャンセル'
                };
                
                return `
                    <div class="history-item">
                        <h3>予約 #${reservation.id}</h3>
                        <div class="info-row">
                            <span>日時:</span>
                            <span>${date.toLocaleString('ja-JP')}</span>
                        </div>
                        <div class="info-row">
                            <span>ステータス:</span>
                            <span class="status ${reservation.status}">${statusLabels[reservation.status] || reservation.status}</span>
                        </div>
                        ${reservation.notes ? `<div class="info-row"><span>備考:</span><span>${reservation.notes}</span></div>` : ''}
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<p class="info-text">予約履歴がありません</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="info-text error">エラー: ${error.message}</p>`;
    }
});

// ページ読み込み時にサービス一覧を読み込む
window.addEventListener('DOMContentLoaded', () => {
    loadServices();
});

