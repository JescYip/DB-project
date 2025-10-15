from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database_jessdb import JessDBCoffeeShop
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 初始化数据库
db = JessDBCoffeeShop()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """管理页面"""
    return render_template('admin.html')

# API路由

@app.route('/api/products', methods=['GET'])
def get_products():
    """获取所有产品"""
    try:
        products = db.get_all_products()
        product_list = []
        for product in products:
            product_list.append({
                'id': product[0],
                'name': product[1],
                'price': float(product[2]),
                'is_active': product[3],
                'category': product[4]
            })
        return jsonify({'success': True, 'data': product_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    try:
        categories = db.get_categories()
        category_list = []
        for category in categories:
            category_list.append({
                'id': category[0],
                'name': category[1],
                'description': category[2]
            })
        return jsonify({'success': True, 'data': category_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/customers', methods=['POST'])
def create_customer():
    """创建客户"""
    try:
        data = request.get_json()
        customer_id = db.create_customer(
            name=data['name'],
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            customer_type=data.get('customer_type', 'GUEST')
        )
        
        # 如果是会员类型，创建会员记录
        if data.get('customer_type') == 'MEMBER' and data.get('password'):
            db.create_member_customer(
                customer_id=customer_id,
                password=data['password'],
                date_of_birth=data.get('date_of_birth')
            )
        
        return jsonify({'success': True, 'customer_id': customer_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """获取客户信息"""
    try:
        customer = db.get_customer_by_id(customer_id)
        if customer:
            customer_data = {
                'customer_id': customer[0],
                'name': customer[1],
                'phone': customer[2],
                'email': customer[3],
                'address': customer[4],
                'customer_type': customer[5]
            }
            return jsonify({'success': True, 'data': customer_data})
        else:
            return jsonify({'success': False, 'error': '客户不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members', methods=['GET'])
def get_members():
    """获取会员列表"""
    try:
        members = db.get_member_customers()
        member_list = []
        for member in members:
            member_list.append({
                'customer_id': member[0],
                'name': member[1],
                'phone': member[2],
                'email': member[3],
                'address': member[4],
                'date_of_birth': member[5],
                'registration_date': member[6]
            })
        return jsonify({'success': True, 'data': member_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/login', methods=['POST'])
def member_login():
    """会员登录"""
    try:
        data = request.get_json()
        member = db.verify_member_login(data['email'], data['password'])
        if member:
            return jsonify({'success': True, 'data': member})
        else:
            return jsonify({'success': False, 'error': '邮箱或密码错误'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单"""
    try:
        data = request.get_json()
        
        # 如果没有提供客户ID，创建新客户
        customer_id = data.get('customer_id')
        if not customer_id:
            customer_id = db.create_customer(
                name=data['customer_name'],
                phone=data.get('customer_phone', ''),
                email=data.get('customer_email', ''),
                address=data.get('customer_address', ''),
                customer_type=data.get('customer_type', 'GUEST')
            )
        
        order_id = db.create_order(
            customer_id=customer_id,
            payment_method=data['payment_method'],
            order_items=data['items'],
            status=data.get('status', 'PLACED')
        )
        
        return jsonify({'success': True, 'order_id': order_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """获取订单历史"""
    try:
        customer_id = request.args.get('customer_id')
        orders = db.get_order_history(customer_id)
        
        order_list = []
        for order in orders:
            order_list.append({
                'order_id': order[0],
                'customer_name': order[1],
                'order_date': order[2],
                'status': order[3],
                'payment_method': order[4],
                'total_amount': float(order[5])
            })
        
        return jsonify({'success': True, 'data': order_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    """更新订单状态"""
    try:
        data = request.get_json()
        db.update_order_status(order_id, data['status'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>/details', methods=['GET'])
def get_order_details(order_id):
    """获取订单详情"""
    try:
        items = db.get_order_details(order_id)
        
        item_list = []
        for item in items:
            item_list.append({
                'product_id': item[0],
                'product_name': item[1],
                'quantity': item[2],
                'unit_price': float(item[3]),
                'line_amount': float(item[4]) if item[4] else 0
            })
        
        return jsonify({'success': True, 'data': item_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/sales', methods=['GET'])
def get_sales_report():
    """获取销售报告"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        report = db.get_sales_report(start_date, end_date)
        
        report_data = []
        for row in report:
            report_data.append({
                'date': row[0],
                'order_count': row[1],
                'total_sales': float(row[2]) if row[2] else 0,
                'avg_order_value': float(row[3]) if row[3] else 0
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/products', methods=['GET'])
def get_product_sales_report():
    """获取产品销售报告"""
    try:
        report = db.get_product_sales_report()
        
        report_data = []
        for row in report:
            report_data.append({
                'product_name': row[0],
                'category': row[1],
                'total_quantity': row[2],
                'total_revenue': float(row[3]) if row[3] else 0,
                'order_count': row[4]
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/customers', methods=['GET'])
def get_customer_report():
    """获取客户报告"""
    try:
        report = db.get_customer_report()
        
        report_data = []
        for row in report:
            report_data.append({
                'customer_name': row[0],
                'customer_type': row[1],
                'order_count': row[2] if row[2] else 0,
                'total_spent': float(row[3]) if row[3] else 0,
                'avg_order_value': float(row[4]) if row[4] else 0,
                'last_order_date': row[5]
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 数据库状态检查
@app.route('/api/database/status', methods=['GET'])
def database_status():
    """检查数据库状态"""
    try:
        # 检查各表的记录数
        conn = db.db_manager.get_connection()
        cursor = conn.cursor()
        
        status = {}
        tables = ['customer', 'member_customers', 'category', 'product', 'orders', 'order_items']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status[table] = count
        
        conn.close()
        
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)