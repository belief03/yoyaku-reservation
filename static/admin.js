const API_BASE = 'http://localhost:8000/api/v1';
// システム管理者のAPIキー（環境変数から取得、開発環境では設定不要）
const ADMIN_API_KEY = null; // 本番環境では環境変数から設定

// ページナビゲーション
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const page = item.dataset.page;
        showPage(page);
        
        // アクティブ状態を更新
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
    });
});

function showPage(pageName) {
    // すべてのページを非表示
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // 選択されたページを表示
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
        loadPageData(pageName);
    }
}

// ページデータの読み込み
function loadPageData(pageName) {
    switch(pageName) {
        case 'invitations':
            loadInvitations();
            break;
        case 'dashboard':
            loadDashboard();
            break;
        case 'reservations':
            loadReservations();
            break;
        case 'customers':
            loadCustomers();
            break;
        case 'stylists':
            loadStylists();
            break;
        case 'services':
            loadServices();
            break;
        case 'products':
            loadProducts();
            break;
        case 'orders':
            loadOrders();
            break;
        case 'campaigns':
            loadCampaigns();
            break;
        case 'coupons':
            loadCoupons();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'shop-settings':
            loadShopSettings();
            break;
    }
}

// ダッシュボード
async function loadDashboard() {
    // 統計データを読み込む
    const today = new Date().toISOString().split('T')[0];
    
    try {
        // 今日の予約
        const reservationsRes = await fetch(`${API_BASE}/reservations/?date=${today}`);
        const reservationsData = await reservationsRes.json();
        const todayReservations = reservationsData.items?.filter(r => 
            r.reservation_datetime?.startsWith(today)
        ) || [];
        document.getElementById('today-reservations').textContent = todayReservations.length;
        
        // 総顧客数
        const customersRes = await fetch(`${API_BASE}/customers/`);
        const customersData = await customersRes.json();
        document.getElementById('total-customers').textContent = customersData.total || customersData.items?.length || 0;
        
        // 完了予約数（簡易版）
        const completedRes = await fetch(`${API_BASE}/reservations/?status=completed`);
        const completedData = await completedRes.json();
        document.getElementById('completed-reservations').textContent = completedData.total || completedData.items?.length || 0;
        
        // 今月の売上（簡易版）
        const ordersRes = await fetch(`${API_BASE}/orders/`);
        const ordersData = await ordersRes.json();
        const monthlyRevenue = ordersData.items?.reduce((sum, order) => {
            const orderDate = new Date(order.created_at || order.order_date);
            const now = new Date();
            if (orderDate.getMonth() === now.getMonth() && orderDate.getFullYear() === now.getFullYear()) {
                return sum + (order.final_amount || 0);
            }
            return sum;
        }, 0) || 0;
        document.getElementById('monthly-revenue').textContent = `¥${monthlyRevenue.toLocaleString()}`;
        
        // 今日の予約一覧
        displayTodayReservations(todayReservations);
        
    } catch (error) {
        console.error('ダッシュボード読み込みエラー:', error);
    }
}

function displayTodayReservations(reservations) {
    const container = document.getElementById('today-reservations-list');
    
    if (reservations.length === 0) {
        container.innerHTML = '<p style="padding: 20px; text-align: center; color: #7f8c8d;">今日の予約はありません</p>';
        return;
    }
    
    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>時間</th>
                    <th>顧客名</th>
                    <th>サービス</th>
                    <th>スタイリスト</th>
                    <th>ステータス</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                ${reservations.map(r => {
                    const date = new Date(r.reservation_datetime);
                    const statusLabels = {
                        'pending': '保留中',
                        'confirmed': '確認済み',
                        'completed': '完了',
                        'cancelled': 'キャンセル'
                    };
                    return `
                        <tr>
                            <td>${date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}</td>
                            <td>${r.customer_name || '顧客名不明'}</td>
                            <td>${r.service_name || '-'}</td>
                            <td>${r.stylist_name || '-'}</td>
                            <td><span class="status-badge ${r.status}">${statusLabels[r.status] || r.status}</span></td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="viewReservation('${r.id}')">詳細</button>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

// 予約管理
async function loadReservations() {
    const container = document.getElementById('reservations-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const status = document.getElementById('reservation-status-filter')?.value || '';
        const date = document.getElementById('reservation-date-filter')?.value || '';
        
        let url = `${API_BASE}/reservations/`;
        const params = [];
        if (status) params.push(`status=${status}`);
        if (date) params.push(`date=${date}`);
        if (params.length) url += '?' + params.join('&');
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>予約日時</th>
                            <th>顧客名</th>
                            <th>サービス</th>
                            <th>スタイリスト</th>
                            <th>ステータス</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.items.map(r => {
                            const date = new Date(r.reservation_datetime);
                            const statusLabels = {
                                'pending': '保留中',
                                'confirmed': '確認済み',
                                'completed': '完了',
                                'cancelled': 'キャンセル'
                            };
                            return `
                                <tr>
                                    <td>${date.toLocaleString('ja-JP')}</td>
                                    <td>${r.customer_name || '顧客名不明'}</td>
                                    <td>${r.service_name || '-'}</td>
                                    <td>${r.stylist_name || '-'}</td>
                                    <td><span class="status-badge ${r.status}">${statusLabels[r.status] || r.status}</span></td>
                                    <td>
                                        <button class="btn btn-sm btn-primary" onclick="viewReservation('${r.id}')">詳細</button>
                                        ${r.status === 'pending' ? `<button class="btn btn-sm btn-secondary" onclick="confirmReservation('${r.id}')">確認</button>` : ''}
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p style="padding: 40px; text-align: center; color: #7f8c8d;">予約が見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p style="padding: 40px; text-align: center; color: #e74c3c;">エラー: ${error.message}</p>`;
    }
}

// 顧客管理
async function loadCustomers() {
    const container = document.getElementById('customers-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/customers/`);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>名前</th>
                            <th>メール</th>
                            <th>電話番号</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.items.map(c => `
                            <tr>
                                <td>${c.id}</td>
                                <td>${c.name || '-'}</td>
                                <td>${c.email || '-'}</td>
                                <td>${c.phone || '-'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="viewCustomer('${c.id}')">詳細</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p style="padding: 40px; text-align: center; color: #7f8c8d;">顧客が見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p style="padding: 40px; text-align: center; color: #e74c3c;">エラー: ${error.message}</p>`;
    }
}

// スタイリスト管理
async function loadStylists() {
    const container = document.getElementById('stylists-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/stylists/`);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>名前</th>
                            <th>専門分野</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.items.map(s => `
                            <tr>
                                <td>${s.id}</td>
                                <td>${s.name || '-'}</td>
                                <td>${s.specialty || '-'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="viewStylist('${s.id}')">詳細</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p style="padding: 40px; text-align: center; color: #7f8c8d;">スタイリストが見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p style="padding: 40px; text-align: center; color: #e74c3c;">エラー: ${error.message}</p>`;
    }
}

// サービス管理
async function loadServices() {
    const container = document.getElementById('services-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/services/`);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>サービス名</th>
                            <th>価格</th>
                            <th>所要時間</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.items.map(s => `
                            <tr>
                                <td>${s.id}</td>
                                <td>${s.name || '-'}</td>
                                <td>¥${(s.price || 0).toLocaleString()}</td>
                                <td>${s.duration_minutes || 0}分</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="viewService('${s.id}')">詳細</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p style="padding: 40px; text-align: center; color: #7f8c8d;">サービスが見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p style="padding: 40px; text-align: center; color: #e74c3c;">エラー: ${error.message}</p>`;
    }
}

// 商品管理
async function loadProducts() {
    const container = document.getElementById('products-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/products/`);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>商品名</th>
                            <th>価格</th>
                            <th>在庫</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.items.map(p => `
                            <tr>
                                <td>${p.id}</td>
                                <td>${p.name || '-'}</td>
                                <td>¥${(p.price || 0).toLocaleString()}</td>
                                <td>${p.stock_quantity !== null ? p.stock_quantity : '無制限'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="viewProduct('${p.id}')">詳細</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p style="padding: 40px; text-align: center; color: #7f8c8d;">商品が見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p style="padding: 40px; text-align: center; color: #e74c3c;">エラー: ${error.message}</p>`;
    }
}

// 注文管理
async function loadOrders() {
    const container = document.getElementById('orders-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const status = document.getElementById('order-status-filter')?.value || '';
        let url = `${API_BASE}/orders/`;
        if (status) url += `?status=${status}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>注文ID</th>
                            <th>顧客名</th>
                            <th>合計金額</th>
                            <th>ステータス</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.items.map(o => `
                            <tr>
                                <td>${o.id}</td>
                                <td>${o.customer_name || '-'}</td>
                                <td>¥${(o.final_amount || 0).toLocaleString()}</td>
                                <td><span class="status-badge ${o.status}">${o.status}</span></td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="viewOrder('${o.id}')">詳細</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p style="padding: 40px; text-align: center; color: #7f8c8d;">注文が見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p style="padding: 40px; text-align: center; color: #e74c3c;">エラー: ${error.message}</p>`;
    }
}

// キャンペーン管理
async function loadCampaigns() {
    const container = document.getElementById('campaigns-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/campaigns/active`);
        const data = await response.json();
        
        const campaigns = data.campaigns || [];
        if (campaigns.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>名前</th>
                            <th>期間</th>
                            <th>割引</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${campaigns.map(c => `
                            <tr>
                                <td>${c.name || '-'}</td>
                                <td>${new Date(c.start_date).toLocaleDateString('ja-JP')} ～ ${new Date(c.end_date).toLocaleDateString('ja-JP')}</td>
                                <td>${c.discount_value || 0}${c.discount_type === 'percentage' ? '%' : '円'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="viewCampaign('${c.id}')">詳細</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p style="padding: 40px; text-align: center; color: #7f8c8d;">キャンペーンが見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p style="padding: 40px; text-align: center; color: #e74c3c;">エラー: ${error.message}</p>`;
    }
}

// クーポン管理
async function loadCoupons() {
    const container = document.getElementById('coupons-list');
    container.innerHTML = '<div class="loading">読み込み中...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/coupons/`);
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>コード</th>
                            <th>名前</th>
                            <th>割引</th>
                            <th>有効期限</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.items.map(c => `
                            <tr>
                                <td><strong>${c.code || '-'}</strong></td>
                                <td>${c.name || '-'}</td>
                                <td>${c.discount_value || 0}${c.coupon_type === 'percentage' ? '%' : '円'}</td>
                                <td>${new Date(c.valid_until).toLocaleDateString('ja-JP')}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="viewCoupon('${c.id}')">詳細</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p style="padding: 40px; text-align: center; color: #7f8c8d;">クーポンが見つかりませんでした</p>';
        }
    } catch (error) {
        container.innerHTML = `<p style="padding: 40px; text-align: center; color: #e74c3c;">エラー: ${error.message}</p>`;
    }
}

// 売上分析
async function loadAnalytics() {
    // 簡易版の分析データ表示
    document.getElementById('revenue-chart').innerHTML = '<p>売上グラフ機能は今後実装予定です</p>';
    
    try {
        // 人気サービス
        const servicesRes = await fetch(`${API_BASE}/services/`);
        const servicesData = await servicesRes.json();
        const popularServices = servicesData.items?.slice(0, 5) || [];
        document.getElementById('popular-services').innerHTML = popularServices.length > 0 
            ? `<ul style="list-style: none; padding: 0;">${popularServices.map(s => `<li style="padding: 10px; border-bottom: 1px solid #f0f0f0;">${s.name} - ¥${(s.price || 0).toLocaleString()}</li>`).join('')}</ul>`
            : '<p>データがありません</p>';
        
        // 人気商品
        const productsRes = await fetch(`${API_BASE}/products/`);
        const productsData = await productsRes.json();
        const popularProducts = productsData.items?.slice(0, 5) || [];
        document.getElementById('popular-products').innerHTML = popularProducts.length > 0
            ? `<ul style="list-style: none; padding: 0;">${popularProducts.map(p => `<li style="padding: 10px; border-bottom: 1px solid #f0f0f0;">${p.name} - ¥${(p.price || 0).toLocaleString()}</li>`).join('')}</ul>`
            : '<p>データがありません</p>';
    } catch (error) {
        console.error('分析データ読み込みエラー:', error);
    }
}

// フィルターのイベントリスナー
document.getElementById('reservation-status-filter')?.addEventListener('change', loadReservations);
document.getElementById('reservation-date-filter')?.addEventListener('change', loadReservations);
document.getElementById('order-status-filter')?.addEventListener('change', loadOrders);

// 日付表示
document.getElementById('current-date').textContent = new Date().toLocaleDateString('ja-JP', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
});

// 初期化
window.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

// 店舗設定
async function loadShopSettings() {
    try {
        const response = await fetch(`${API_BASE}/settings/`);
        const settings = await response.json();
        
        // フォームに値を設定
        document.getElementById('shop-name').value = settings.shop_name || '';
        document.getElementById('shop-logo-url').value = settings.shop_logo_url || '';
        document.getElementById('shop-phone').value = settings.shop_phone || '';
        document.getElementById('shop-email').value = settings.shop_email || '';
        document.getElementById('shop-address').value = settings.shop_address || '';
        document.getElementById('shop-description').value = settings.shop_description || '';
        
        // カラー設定
        document.getElementById('primary-color').value = settings.primary_color || '#667eea';
        document.getElementById('primary-color-text').value = settings.primary_color || '#667eea';
        document.getElementById('secondary-color').value = settings.secondary_color || '#764ba2';
        document.getElementById('secondary-color-text').value = settings.secondary_color || '#764ba2';
        if (settings.accent_color) {
            document.getElementById('accent-color').value = settings.accent_color;
            document.getElementById('accent-color-text').value = settings.accent_color;
        }
        
        // 営業時間
        document.getElementById('business-hours-start').value = settings.business_hours_start || '09:00';
        document.getElementById('business-hours-end').value = settings.business_hours_end || '20:00';
        
        // 営業日
        document.querySelectorAll('input[name="business_days"]').forEach(cb => {
            cb.checked = settings.business_days?.includes(parseInt(cb.value)) || false;
        });
        
        // 予約設定
        document.getElementById('slot-duration').value = settings.reservation_slot_duration_minutes || 30;
        document.getElementById('max-advance-days').value = settings.max_advance_booking_days || 90;
        document.getElementById('min-advance-hours').value = settings.min_advance_booking_hours || 2;
        document.getElementById('cancellation-hours').value = settings.cancellation_hours_before || 24;
        
        // 通知設定
        document.getElementById('enable-email').checked = settings.enable_email_notifications !== false;
        document.getElementById('enable-sms').checked = settings.enable_sms_notifications === true;
        
        // その他
        document.getElementById('currency').value = settings.currency || 'JPY';
        document.getElementById('timezone').value = settings.timezone || 'Asia/Tokyo';
        
        // カスタムコード
        document.getElementById('custom-css').value = settings.custom_css || '';
        document.getElementById('custom-js').value = settings.custom_js || '';
        
        updateColorPreview();
    } catch (error) {
        console.error('設定読み込みエラー:', error);
        document.getElementById('settings-result').className = 'result-message error';
        document.getElementById('settings-result').textContent = `エラー: ${error.message}`;
        document.getElementById('settings-result').style.display = 'block';
    }
}

// カラープレビュー更新
function updateColorPreview() {
    const primary = document.getElementById('primary-color').value;
    const secondary = document.getElementById('secondary-color').value;
    const preview = document.getElementById('color-preview');
    
    preview.style.background = `linear-gradient(135deg, ${primary}, ${secondary})`;
    preview.querySelector('.preview-btn').style.background = `linear-gradient(135deg, ${primary}, ${secondary})`;
}

// カラー入力の同期
document.getElementById('primary-color')?.addEventListener('input', function() {
    document.getElementById('primary-color-text').value = this.value;
    updateColorPreview();
});

document.getElementById('primary-color-text')?.addEventListener('input', function() {
    if (/^#[0-9A-Fa-f]{6}$/.test(this.value)) {
        document.getElementById('primary-color').value = this.value;
        updateColorPreview();
    }
});

document.getElementById('secondary-color')?.addEventListener('input', function() {
    document.getElementById('secondary-color-text').value = this.value;
    updateColorPreview();
});

document.getElementById('secondary-color-text')?.addEventListener('input', function() {
    if (/^#[0-9A-Fa-f]{6}$/.test(this.value)) {
        document.getElementById('secondary-color').value = this.value;
        updateColorPreview();
    }
});

// 設定保存
document.getElementById('save-settings-btn')?.addEventListener('click', async () => {
    const form = document.getElementById('shop-settings-form');
    const formData = new FormData(form);
    const resultDiv = document.getElementById('settings-result');
    
    resultDiv.className = 'result-message';
    resultDiv.textContent = '保存中...';
    resultDiv.style.display = 'block';
    
    try {
        const settingsData = {};
        
        // フォームデータを収集
        for (const [key, value] of formData.entries()) {
            if (key === 'business_days') {
                if (!settingsData.business_days) settingsData.business_days = [];
                settingsData.business_days.push(parseInt(value));
            } else if (key === 'enable_email_notifications' || key === 'enable_sms_notifications') {
                settingsData[key] = document.getElementById(key.replace('_', '-')).checked;
            } else if (value) {
                settingsData[key] = value;
            }
        }
        
        // 数値フィールドの変換
        if (settingsData.reservation_slot_duration_minutes) {
            settingsData.reservation_slot_duration_minutes = parseInt(settingsData.reservation_slot_duration_minutes);
        }
        if (settingsData.max_advance_booking_days) {
            settingsData.max_advance_booking_days = parseInt(settingsData.max_advance_booking_days);
        }
        if (settingsData.min_advance_booking_hours) {
            settingsData.min_advance_booking_hours = parseInt(settingsData.min_advance_booking_hours);
        }
        if (settingsData.cancellation_hours_before) {
            settingsData.cancellation_hours_before = parseInt(settingsData.cancellation_hours_before);
        }
        
        const response = await fetch(`${API_BASE}/settings/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settingsData)
        });
        
        if (response.ok) {
            resultDiv.className = 'result-message success';
            resultDiv.textContent = '✅ 設定を保存しました！';
            
            // 設定を反映（カスタムCSS/JSを適用）
            applyCustomSettings(settingsData);
        } else {
            const error = await response.json();
            resultDiv.className = 'result-message error';
            resultDiv.textContent = `エラー: ${error.detail || '保存に失敗しました'}`;
        }
    } catch (error) {
        resultDiv.className = 'result-message error';
        resultDiv.textContent = `エラー: ${error.message}`;
    }
});

// 設定リセット
document.getElementById('reset-settings-btn')?.addEventListener('click', async () => {
    if (!confirm('設定をデフォルト値に戻しますか？')) return;
    
    try {
        const response = await fetch(`${API_BASE}/settings/reset`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadShopSettings();
            document.getElementById('settings-result').className = 'result-message success';
            document.getElementById('settings-result').textContent = '✅ 設定をリセットしました';
            document.getElementById('settings-result').style.display = 'block';
        }
    } catch (error) {
        console.error('設定リセットエラー:', error);
    }
});

// カスタム設定の適用
function applyCustomSettings(settings) {
    // カスタムCSSを適用
    if (settings.custom_css) {
        let styleTag = document.getElementById('custom-shop-css');
        if (!styleTag) {
            styleTag = document.createElement('style');
            styleTag.id = 'custom-shop-css';
            document.head.appendChild(styleTag);
        }
        styleTag.textContent = settings.custom_css;
    }
    
    // カスタムJSを適用（注意：既存のスクリプトは削除されない）
    if (settings.custom_js) {
        let scriptTag = document.getElementById('custom-shop-js');
        if (scriptTag) {
            scriptTag.remove();
        }
        scriptTag = document.createElement('script');
        scriptTag.id = 'custom-shop-js';
        scriptTag.textContent = settings.custom_js;
        document.body.appendChild(scriptTag);
    }
}

// プレースホルダー関数
function viewReservation(id) { alert(`予約詳細: ${id}`); }
function confirmReservation(id) { alert(`予約確認: ${id}`); }
function viewCustomer(id) { alert(`顧客詳細: ${id}`); }
function viewStylist(id) { alert(`スタイリスト詳細: ${id}`); }
function viewService(id) { alert(`サービス詳細: ${id}`); }
function viewProduct(id) { alert(`商品詳細: ${id}`); }
function viewOrder(id) { alert(`注文詳細: ${id}`); }
function viewCampaign(id) { alert(`キャンペーン詳細: ${id}`); }
function viewCoupon(id) { alert(`クーポン詳細: ${id}`); }

// 招待管理
async function loadInvitations() {
    const container = document.getElementById('invitations-list');
    const statusFilter = document.getElementById('invitation-status-filter')?.value;
    
    try {
        container.innerHTML = '<div class="loading">読み込み中...</div>';
        
        const headers = {
            'Content-Type': 'application/json'
        };
        if (ADMIN_API_KEY) {
            headers['X-Admin-API-Key'] = ADMIN_API_KEY;
        }
        
        let url = `${API_BASE}/invitations/`;
        if (statusFilter !== '') {
            url += `?used=${statusFilter}`;
        }
        
        const response = await fetch(url, { headers });
        
        if (response.status === 403) {
            container.innerHTML = `
                <div class="error-message" style="padding: 20px; text-align: center;">
                    <p>この機能はシステム管理者のみが使用できます。</p>
                    <p>X-Admin-API-Keyヘッダーを設定してください。</p>
                </div>
            `;
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const invitations = await response.json();
        displayInvitations(invitations);
        
        // 招待作成ボタンのイベントリスナー
        document.getElementById('create-invitation-btn')?.addEventListener('click', () => {
            document.getElementById('invitation-modal').style.display = 'flex';
        });
        
        // フィルターのイベントリスナー
        document.getElementById('invitation-status-filter')?.addEventListener('change', () => {
            loadInvitations();
        });
        
    } catch (error) {
        console.error('招待一覧読み込みエラー:', error);
        container.innerHTML = `<div class="error-message">エラー: ${error.message}</div>`;
    }
}

function displayInvitations(invitations) {
    const container = document.getElementById('invitations-list');
    
    if (invitations.length === 0) {
        container.innerHTML = '<p style="padding: 20px; text-align: center; color: #7f8c8d;">招待がありません</p>';
        return;
    }
    
    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>メールアドレス</th>
                    <th>店舗名</th>
                    <th>招待URL</th>
                    <th>有効期限</th>
                    <th>ステータス</th>
                    <th>作成日</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                ${invitations.map(inv => {
                    const expiresAt = new Date(inv.expires_at);
                    const createdAt = new Date(inv.created_at);
                    const isExpired = expiresAt < new Date();
                    const statusBadge = inv.used 
                        ? '<span class="badge badge-success">使用済み</span>'
                        : isExpired
                        ? '<span class="badge badge-danger">期限切れ</span>'
                        : '<span class="badge badge-info">有効</span>';
                    
                    return `
                        <tr>
                            <td>${inv.email}</td>
                            <td>${inv.shop_name || '-'}</td>
                            <td>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <input type="text" value="${inv.invitation_url}" readonly 
                                           style="flex: 1; padding: 4px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 12px;">
                                    <button class="btn btn-small" onclick="copyInvitationUrl('${inv.invitation_url}')">コピー</button>
                                </div>
                            </td>
                            <td>${expiresAt.toLocaleDateString('ja-JP')}</td>
                            <td>${statusBadge}</td>
                            <td>${createdAt.toLocaleDateString('ja-JP')}</td>
                            <td>
                                ${!inv.used ? `<button class="btn btn-small btn-danger" onclick="deleteInvitation('${inv.token}')">削除</button>` : '-'}
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

function copyInvitationUrl(url) {
    navigator.clipboard.writeText(url).then(() => {
        alert('招待URLをコピーしました');
    }).catch(err => {
        console.error('コピーエラー:', err);
        alert('コピーに失敗しました');
    });
}

function closeInvitationModal() {
    document.getElementById('invitation-modal').style.display = 'none';
    document.getElementById('invitation-form').reset();
}

// 招待作成フォームの送信
document.addEventListener('DOMContentLoaded', () => {
    const invitationForm = document.getElementById('invitation-form');
    if (invitationForm) {
        invitationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('invitation-email').value;
            const shopName = document.getElementById('invitation-shop-name').value;
            const expiresDays = parseInt(document.getElementById('invitation-expires-days').value) || 7;
            
            try {
                const headers = {
                    'Content-Type': 'application/json'
                };
                if (ADMIN_API_KEY) {
                    headers['X-Admin-API-Key'] = ADMIN_API_KEY;
                }
                
                const response = await fetch(`${API_BASE}/invitations/`, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        email: email,
                        shop_name: shopName || null,
                        expires_in_days: expiresDays
                    })
                });
                
                if (response.status === 403) {
                    alert('この操作を実行するにはシステム管理者の権限が必要です。');
                    return;
                }
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || '招待の作成に失敗しました');
                }
                
                const result = await response.json();
                alert(`招待が作成されました！\n招待URL: ${result.invitation_url}`);
                closeInvitationModal();
                loadInvitations();
                
            } catch (error) {
                console.error('招待作成エラー:', error);
                alert(`エラー: ${error.message}`);
            }
        });
    }
});

async function deleteInvitation(token) {
    if (!confirm('この招待を削除しますか？')) {
        return;
    }
    
    try {
        // 注意: 削除APIは実装されていないため、ここでは警告のみ
        alert('削除機能は現在実装されていません。データベースから直接削除してください。');
    } catch (error) {
        console.error('削除エラー:', error);
        alert(`エラー: ${error.message}`);
    }
}

