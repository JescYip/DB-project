// 全局变量
let products = [];
let cart = [];
let currentTab = 'menu';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
async function initializeApp() {
    try {
        await loadProducts();
        setupEventListeners();
        showTab('menu');
    } catch (error) {
        console.error('初始化失败:', error);
        showAlert('系统初始化失败，请刷新页面重试', 'error');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 导航标签点击事件
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            showTab(tabName);
        });
    });

    // 订单表单提交
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', handleOrderSubmit);
    }
}

// 加载产品数据
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const result = await response.json();
        
        if (result.success) {
            products = result.data;
            renderProducts();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('加载产品失败:', error);
        showAlert('加载产品失败', 'error');
    }
}

// 渲染产品列表
function renderProducts() {
    const container = document.getElementById('productsContainer');
    if (!container) return;

    container.innerHTML = '';
    
    // 按分类分组产品
    const categories = {};
    products.forEach(product => {
        if (!categories[product.category]) {
            categories[product.category] = [];
        }
        categories[product.category].push(product);
    });

    // 渲染每个分类的产品
    Object.keys(categories).forEach(categoryName => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'category-section';
        categoryDiv.innerHTML = `
            <h2 style="color: #4a5568; margin: 20px 0 15px 0; font-size: 1.5em;">${categoryName}</h2>
            <div class="products-grid" id="category-${categoryName}"></div>
        `;
        container.appendChild(categoryDiv);

        const categoryGrid = document.getElementById(`category-${categoryName}`);
        categories[categoryName].forEach(product => {
            const productCard = createProductCard(product);
            categoryGrid.appendChild(productCard);
        });
    });
}

// 创建产品卡片
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.innerHTML = `
        <h3>${product.name}</h3>
        <div class="category">${product.category}</div>
        <div class="price">¥${product.price.toFixed(2)}</div>
        <div class="quantity-control">
            <button class="quantity-btn" onclick="changeQuantity(${product.id}, -1)">-</button>
            <input type="number" class="quantity-input" id="qty-${product.id}" value="1" min="1" max="99">
            <button class="quantity-btn" onclick="changeQuantity(${product.id}, 1)">+</button>
        </div>
        <button class="add-to-cart" onclick="addToCart(${product.id})">
            加入购物车
        </button>
    `;
    return card;
}

// 修改数量
function changeQuantity(productId, change) {
    const input = document.getElementById(`qty-${productId}`);
    const currentValue = parseInt(input.value);
    const newValue = Math.max(1, Math.min(99, currentValue + change));
    input.value = newValue;
}

// 添加到购物车
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const quantity = parseInt(document.getElementById(`qty-${productId}`).value);
    
    if (!product) return;

    // 检查购物车中是否已有该产品
    const existingItem = cart.find(item => item.product_id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            product_id: productId,
            name: product.name,
            price: product.price,
            quantity: quantity
        });
    }

    updateCartDisplay();
    showAlert(`${product.name} 已添加到购物车`, 'success');
    
    // 重置数量为1
    document.getElementById(`qty-${productId}`).value = 1;
}

// 更新购物车显示
function updateCartDisplay() {
    const cartContainer = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    if (!cartContainer || !cartTotal) return;

    if (cart.length === 0) {
        cartContainer.innerHTML = '<p style="text-align: center; color: #718096;">购物车为空</p>';
        cartTotal.textContent = '总计: ¥0.00';
        return;
    }

    let total = 0;
    cartContainer.innerHTML = '';

    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div>
                <strong>${item.name}</strong><br>
                <small>¥${item.price.toFixed(2)} x ${item.quantity}</small>
            </div>
            <div>
                <span style="margin-right: 10px;">¥${itemTotal.toFixed(2)}</span>
                <button class="btn-danger" style="padding: 5px 10px; font-size: 0.8em;" onclick="removeFromCart(${index})">
                    删除
                </button>
            </div>
        `;
        cartContainer.appendChild(cartItem);
    });

    cartTotal.textContent = `总计: ¥${total.toFixed(2)}`;
}

// 从购物车移除商品
function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartDisplay();
    showAlert('商品已从购物车移除', 'info');
}

// 清空购物车
function clearCart() {
    cart = [];
    updateCartDisplay();
    showAlert('购物车已清空', 'info');
}

// 处理订单提交
async function handleOrderSubmit(e) {
    e.preventDefault();
    
    if (cart.length === 0) {
        showAlert('购物车为空，请先添加商品', 'error');
        return;
    }

    const formData = new FormData(e.target);
    const orderData = {
        customer_name: formData.get('customer_name'),
        customer_phone: formData.get('customer_phone'),
        customer_email: formData.get('customer_email'),
        customer_address: formData.get('customer_address'),
        payment_method: formData.get('payment_method'),
        items: cart
    };

    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();
        
        if (result.success) {
            showAlert(`订单创建成功！订单号: ${result.order_id}`, 'success');
            clearCart();
            document.getElementById('orderForm').reset();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('创建订单失败:', error);
        showAlert('创建订单失败，请重试', 'error');
    }
}

// 显示标签页
function showTab(tabName) {
    // 更新导航标签
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // 更新内容区域
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');

    currentTab = tabName;

    // 如果切换到订单历史标签，加载订单数据
    if (tabName === 'orders') {
        loadOrderHistory();
    }
}

// 加载订单历史
async function loadOrderHistory() {
    try {
        const response = await fetch('/api/orders');
        const result = await response.json();
        
        if (result.success) {
            renderOrderHistory(result.data);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('加载订单历史失败:', error);
        showAlert('加载订单历史失败', 'error');
    }
}

// 渲染订单历史
function renderOrderHistory(orders) {
    const container = document.getElementById('ordersContainer');
    if (!container) return;

    if (orders.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #718096;">暂无订单记录</p>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>订单号</th>
                <th>客户姓名</th>
                <th>订单日期</th>
                <th>状态</th>
                <th>支付方式</th>
                <th>总金额</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            ${orders.map(order => `
                <tr>
                    <td>#${order.order_id}</td>
                    <td>${order.customer_name}</td>
                    <td>${new Date(order.order_date).toLocaleString('zh-CN')}</td>
                    <td><span class="status-${order.status}">${getStatusText(order.status)}</span></td>
                    <td>${getPaymentMethodText(order.payment_method)}</td>
                    <td>¥${order.total_amount.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 0.8em;" 
                                onclick="viewOrderDetails(${order.order_id})">
                            查看详情
                        </button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;

    container.innerHTML = '';
    container.appendChild(table);
}

// 查看订单详情
async function viewOrderDetails(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}/details`);
        const result = await response.json();
        
        if (result.success) {
            showOrderDetailsModal(orderId, result.data);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('加载订单详情失败:', error);
        showAlert('加载订单详情失败', 'error');
    }
}

// 显示订单详情模态框
function showOrderDetailsModal(orderId, items) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 600px;
        width: 90%;
        max-height: 80%;
        overflow-y: auto;
    `;

    let total = 0;
    items.forEach(item => {
        total += item.line_amount;
    });

    content.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #4a5568;">订单详情 #${orderId}</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>商品名称</th>
                    <th>数量</th>
                    <th>单价</th>
                    <th>小计</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.product_name}</td>
                        <td>${item.quantity}</td>
                        <td>¥${item.unit_price.toFixed(2)}</td>
                        <td>¥${item.line_amount.toFixed(2)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        <div style="text-align: right; margin-top: 20px; font-size: 1.2em; font-weight: bold; color: #4a5568;">
            总计: ¥${total.toFixed(2)}
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">关闭</button>
        </div>
    `;

    modal.className = 'modal';
    modal.appendChild(content);
    document.body.appendChild(modal);

    // 点击背景关闭模态框
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'cancelled': '已取消'
    };
    return statusMap[status] || status;
}

// 获取支付方式文本
function getPaymentMethodText(method) {
    const methodMap = {
        'cash': '现金',
        'card': '银行卡',
        'alipay': '支付宝',
        'wechat': '微信支付'
    };
    return methodMap[method] || method;
}

// 显示提示消息
function showAlert(message, type = 'info') {
    // 移除现有的提示
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    // 插入到内容区域顶部
    const content = document.querySelector('.content');
    content.insertBefore(alert, content.firstChild);

    // 3秒后自动移除
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 3000);
}