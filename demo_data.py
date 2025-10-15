#!/usr/bin/env python3
"""
演示数据生成脚本
为咖啡订购系统生成更多的演示数据
"""

from database import CoffeeShopDB
from datetime import datetime, timedelta
import random

def generate_demo_data():
    """生成演示数据"""
    db = CoffeeShopDB()
    
    print("🎭 生成演示数据...")
    
    # 创建更多客户
    customers = [
        ('王小明', '13912345678', 'wangxm@example.com', '北京市海淀区中关村大街1号', 'regular'),
        ('李小红', '13823456789', 'lixh@example.com', '上海市黄浦区南京路100号', 'member'),
        ('张小华', '13734567890', 'zhangxh@example.com', '广州市天河区珠江新城', 'regular'),
        ('刘小刚', '13645678901', 'liuxg@example.com', '深圳市南山区科技园', 'member'),
        ('陈小美', '13556789012', 'chenxm@example.com', '杭州市西湖区文三路', 'regular'),
        ('赵小强', '13467890123', 'zhaoxq@example.com', '成都市锦江区春熙路', 'regular'),
        ('孙小丽', '13378901234', 'sunxl@example.com', '武汉市武昌区中南路', 'member'),
        ('周小伟', '13289012345', 'zhouxw@example.com', '西安市雁塔区高新路', 'regular'),
    ]
    
    customer_ids = []
    for customer in customers:
        try:
            customer_id = db.create_customer(*customer)
            customer_ids.append(customer_id)
            print(f"✅ 创建客户: {customer[0]}")
        except Exception as e:
            print(f"⚠️  客户 {customer[0]} 可能已存在")
    
    # 获取所有产品
    products = db.get_all_products()
    product_ids = [p[0] for p in products]
    
    # 生成历史订单（过去30天）
    print("\n📦 生成历史订单...")
    payment_methods = ['cash', 'card', 'alipay', 'wechat']
    
    for i in range(50):  # 生成50个订单
        # 随机选择日期（过去30天内）
        days_ago = random.randint(0, 30)
        order_date = datetime.now() - timedelta(days=days_ago)
        
        # 随机选择客户
        customer_id = random.choice(customer_ids + [1, 2, 3])  # 包括原有客户
        
        # 随机生成订单项
        num_items = random.randint(1, 5)
        order_items = []
        
        for _ in range(num_items):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 3)
            
            # 避免重复产品
            if not any(item['product_id'] == product_id for item in order_items):
                order_items.append({
                    'product_id': product_id,
                    'quantity': quantity
                })
        
        if order_items:  # 确保有订单项
            try:
                payment_method = random.choice(payment_methods)
                order_id = db.create_order(customer_id, payment_method, order_items)
                
                # 更新订单日期（模拟历史订单）
                conn = db.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE CYEAE_ORDERS SET ORDER_DATE = ? WHERE ORDER_ID = ?",
                    (order_date.strftime('%Y-%m-%d %H:%M:%S'), order_id)
                )
                conn.commit()
                conn.close()
                
                print(f"✅ 创建订单 #{order_id} ({order_date.strftime('%Y-%m-%d')})")
                
            except Exception as e:
                print(f"❌ 创建订单失败: {e}")
    
    print("\n🎉 演示数据生成完成！")
    print("\n📊 数据统计:")
    
    # 显示统计信息
    sales_report = db.get_sales_report()
    total_sales = sum(row[2] if row[2] else 0 for row in sales_report)
    total_orders = sum(row[1] for row in sales_report)
    
    print(f"📈 总销售额: ¥{total_sales:.2f}")
    print(f"📦 总订单数: {total_orders}")
    print(f"💰 平均订单价值: ¥{total_sales/total_orders if total_orders > 0 else 0:.2f}")
    
    product_report = db.get_product_sales_report()
    print(f"🏆 最受欢迎产品: {product_report[0][0] if product_report else '无'}")
    
    customer_report = db.get_customer_report()
    active_customers = len([c for c in customer_report if c[2] > 0])
    print(f"👥 活跃客户数: {active_customers}")

if __name__ == '__main__':
    generate_demo_data()