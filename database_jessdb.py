import sqlite3
import hashlib
from datetime import datetime, date
import os

class JessDBManager:
    def __init__(self, db_path='jessdb.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """使用 jessdb_sqlite.sql 初始化数据库"""
        # 如果数据库文件已存在且有数据，跳过初始化
        if os.path.exists(self.db_path):
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customer'")
            if cursor.fetchone():
                conn.close()
                return
            conn.close()
        
        # 读取并执行 SQL 脚本
        with open('jessdb_sqlite_fixed.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 使用 executescript 执行整个脚本
        try:
            cursor.executescript(sql_script)
        except sqlite3.Error as e:
            print(f"执行 SQL 脚本时出错: {e}")
            # 如果脚本执行失败，尝试手动创建基本结构
            self._create_basic_structure(cursor)
        
        conn.commit()
        conn.close()
    
    def _create_basic_structure(self, cursor):
        """手动创建基本数据库结构"""
        # 清理
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DROP TABLE IF EXISTS order_items")
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS member_customers")
        cursor.execute("DROP TABLE IF EXISTS product")
        cursor.execute("DROP TABLE IF EXISTS category")
        cursor.execute("DROP TABLE IF EXISTS customer")
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 创建表
        cursor.execute("""
            CREATE TABLE customer (
              customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
              name            VARCHAR(100)   NOT NULL,
              phone           VARCHAR(30),
              email           VARCHAR(120),
              address         VARCHAR(255),
              customer_type   VARCHAR(10)    NOT NULL
                CHECK (customer_type IN ('MEMBER','GUEST'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE category (
              category_id     INTEGER PRIMARY KEY AUTOINCREMENT,
              category_name   VARCHAR(80) NOT NULL UNIQUE,
              description     VARCHAR(255)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE product (
              product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
              name            VARCHAR(120)  NOT NULL,
              price           DECIMAL(10,2)   NOT NULL CHECK (price >= 0),
              is_active       CHAR(1)        DEFAULT 'Y' NOT NULL CHECK (is_active IN ('Y','N')),
              category_id     INTEGER         NOT NULL,
              FOREIGN KEY (category_id) REFERENCES category(category_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE member_customers (
              customer_id        INTEGER       PRIMARY KEY,
              password_hash      VARCHAR(255),
              date_of_birth      DATE,
              registration_date  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
              FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE orders (
              order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
              customer_id     INTEGER NOT NULL,
              order_date      DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
              status          VARCHAR(20) NOT NULL,
              payment_method  VARCHAR(20) NOT NULL,
              total_amount    DECIMAL(12,2) DEFAULT 0 NOT NULL CHECK (total_amount >= 0),
              FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE order_items (
              order_item_id   INTEGER PRIMARY KEY AUTOINCREMENT,
              order_id        INTEGER NOT NULL,
              product_id      INTEGER NOT NULL,
              quantity        INTEGER NOT NULL CHECK (quantity > 0),
              unit_price      DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
              line_amount     DECIMAL(10,2),
              FOREIGN KEY (order_id)  REFERENCES orders(order_id) ON DELETE CASCADE,
              FOREIGN KEY (product_id) REFERENCES product(product_id)
            )
        """)
        
        # 插入基础数据
        categories = [
            ('Coffee', 'Various types of coffee drinks'),
            ('Tea', 'Traditional and specialty teas'),
            ('Bakery', 'Fresh pastries and desserts'),
            ('Smoothies', 'Fruit and yogurt smoothies'),
            ('Sandwiches', 'Freshly made sandwiches'),
            ('Seasonal', 'Limited-time seasonal specials'),
            ('Cold Brew', 'Cold brew coffee selection')
        ]
        cursor.executemany("INSERT INTO category(category_name, description) VALUES (?, ?)", categories)
        
        products = [
            ('Americano', 30, 'Y', 1),
            ('Latte', 35, 'Y', 1),
            ('Green Tea', 25, 'Y', 2),
            ('Chocolate Cake', 45, 'Y', 3),
            ('Strawberry Smoothie', 38, 'Y', 4),
            ('Mango Smoothie', 40, 'Y', 4),
            ('Chicken Sandwich', 42, 'Y', 5),
            ('Tuna Sandwich', 39, 'Y', 5),
            ('Pumpkin Spice Latte', 48, 'Y', 6),
            ('Gingerbread Latte', 50, 'Y', 6),
            ('Classic Cold Brew', 36, 'Y', 7),
            ('Nitro Cold Brew', 42, 'Y', 7)
        ]
        cursor.executemany("INSERT INTO product(name, price, is_active, category_id) VALUES (?, ?, ?, ?)", products)
        
        # 示例客户
        customers = [
            ('Wei Zhang', '+85212345678', 'wei.zhang@email.com', None, 'MEMBER'),
            ('Mei Li', '+85287654321', 'mei.li@email.com', None, 'MEMBER'),
            ('Li Wei', '+85268001234', 'li.wei@email.com', None, 'MEMBER'),
            ('Chen Yang', '+85268004567', 'chen.yang@email.com', None, 'MEMBER'),
            ('Wang Yu', '+85268007890', 'wang.yu@email.com', None, 'MEMBER'),
            ('San Zhang', '+85255556666', None, None, 'GUEST'),
            ('Si Li', '+85299998888', None, None, 'GUEST'),
            ('Guest A', '+85270110001', None, None, 'GUEST'),
            ('Guest B', '+85270110002', None, None, 'GUEST'),
            ('Guest C', '+85270110003', None, None, 'GUEST')
        ]
        cursor.executemany("INSERT INTO customer (name, phone, email, address, customer_type) VALUES (?, ?, ?, ?, ?)", customers)
        
        # 会员数据
        members = [
            (1, 'hashed_password_1', '1990-01-15'),
            (2, 'hashed_password_2', '1985-08-22'),
            (3, 'pw_liwei', '1992-02-09'),
            (4, 'pw_cy', '1995-11-23'),
            (5, 'pw_wy', '1988-05-17')
        ]
        cursor.executemany("INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (?, ?, ?)", members)
        
        # 示例订单
        cursor.execute("INSERT INTO orders (customer_id, status, payment_method, total_amount) VALUES (1, 'PLACED', 'CREDIT CARD', 65)")
        cursor.execute("INSERT INTO orders (customer_id, status, payment_method, total_amount) VALUES (2, 'COMPLETED', 'ALIPAY', 45)")
        
        # 订单明细
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_amount) VALUES (1, 1, 1, 30, 30)")
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_amount) VALUES (1, 2, 1, 35, 35)")
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_amount) VALUES (2, 4, 1, 45, 45)")
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hash_value):
        """验证密码"""
        return self.hash_password(password) == hash_value

# 数据库操作类 - 适配 jessdb 表结构
class JessDBCoffeeShop:
    def __init__(self):
        self.db_manager = JessDBManager()
    
    def get_all_products(self):
        """获取所有产品"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.product_id, p.name, p.price, p.is_active, c.category_name
            FROM product p
            LEFT JOIN category c ON p.category_id = c.category_id
            WHERE p.is_active = 'Y'
            ORDER BY c.category_name, p.name
        """)
        products = cursor.fetchall()
        conn.close()
        return products
    
    def get_categories(self):
        """获取所有分类"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, category_name, description FROM category ORDER BY category_name")
        categories = cursor.fetchall()
        conn.close()
        return categories
    
    def create_customer(self, name, phone, email, address, customer_type='GUEST'):
        """创建客户"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customer (name, phone, email, address, customer_type)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, address, customer_type))
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return customer_id
    
    def create_member_customer(self, customer_id, password, date_of_birth=None):
        """为现有客户创建会员记录"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 首先确保客户类型是 MEMBER
        cursor.execute("UPDATE customer SET customer_type = 'MEMBER' WHERE customer_id = ?", (customer_id,))
        
        password_hash = self.db_manager.hash_password(password)
        cursor.execute("""
            INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
            VALUES (?, ?, ?)
        """, (customer_id, password_hash, date_of_birth))
        
        conn.commit()
        conn.close()
    
    def create_order(self, customer_id, payment_method, order_items, status='PLACED'):
        """创建订单"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # 计算总金额
            total_amount = 0
            for item in order_items:
                cursor.execute("SELECT price FROM product WHERE product_id = ?", (item['product_id'],))
                price = cursor.fetchone()[0]
                total_amount += price * item['quantity']
            
            # 创建订单
            cursor.execute("""
                INSERT INTO orders (customer_id, status, payment_method, total_amount)
                VALUES (?, ?, ?, ?)
            """, (customer_id, status.upper(), payment_method.upper(), total_amount))
            
            order_id = cursor.lastrowid
            
            # 添加订单项
            for item in order_items:
                cursor.execute("SELECT price FROM product WHERE product_id = ?", (item['product_id'],))
                unit_price = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (?, ?, ?, ?)
                """, (order_id, item['product_id'], item['quantity'], unit_price))
            
            conn.commit()
            return order_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_order_history(self, customer_id=None):
        """获取订单历史"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        if customer_id:
            cursor.execute("""
                SELECT o.order_id, c.name, o.order_date, o.status, o.payment_method, o.total_amount
                FROM orders o
                JOIN customer c ON o.customer_id = c.customer_id
                WHERE o.customer_id = ?
                ORDER BY o.order_date DESC
            """, (customer_id,))
        else:
            cursor.execute("""
                SELECT o.order_id, c.name, o.order_date, o.status, o.payment_method, o.total_amount
                FROM orders o
                JOIN customer c ON o.customer_id = c.customer_id
                ORDER BY o.order_date DESC
            """)
        
        orders = cursor.fetchall()
        conn.close()
        return orders
    
    def get_order_details(self, order_id):
        """获取订单详情"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT oi.product_id, p.name, oi.quantity, oi.unit_price, oi.line_amount
            FROM order_items oi
            JOIN product p ON oi.product_id = p.product_id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        items = cursor.fetchall()
        conn.close()
        return items
    
    def get_sales_report(self, start_date=None, end_date=None):
        """获取销售报告"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        base_query = """
            SELECT 
                DATE(o.order_date) as order_date,
                COUNT(o.order_id) as order_count,
                SUM(o.total_amount) as total_sales,
                AVG(o.total_amount) as avg_order_value
            FROM orders o
            WHERE 1=1
        """
        
        params = []
        if start_date:
            base_query += " AND DATE(o.order_date) >= ?"
            params.append(start_date)
        if end_date:
            base_query += " AND DATE(o.order_date) <= ?"
            params.append(end_date)
            
        base_query += " GROUP BY DATE(o.order_date) ORDER BY order_date DESC"
        
        cursor.execute(base_query, params)
        report = cursor.fetchall()
        conn.close()
        return report
    
    def get_product_sales_report(self):
        """获取产品销售报告"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.name as product_name,
                c.category_name,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.line_amount) as total_revenue,
                COUNT(DISTINCT oi.order_id) as order_count
            FROM order_items oi
            JOIN product p ON oi.product_id = p.product_id
            JOIN category c ON p.category_id = c.category_id
            GROUP BY p.product_id, p.name, c.category_name
            ORDER BY total_revenue DESC
        """)
        
        report = cursor.fetchall()
        conn.close()
        return report
    
    def get_customer_report(self):
        """获取客户报告"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.name as customer_name,
                c.customer_type,
                COUNT(o.order_id) as order_count,
                SUM(o.total_amount) as total_spent,
                AVG(o.total_amount) as avg_order_value,
                MAX(o.order_date) as last_order_date
            FROM customer c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.name, c.customer_type
            ORDER BY total_spent DESC
        """)
        
        report = cursor.fetchall()
        conn.close()
        return report
    
    def get_member_customers(self):
        """获取会员客户信息"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.customer_id, c.name, c.phone, c.email, c.address,
                   m.date_of_birth, m.registration_date
            FROM customer c
            JOIN member_customers m ON c.customer_id = m.customer_id
            ORDER BY m.registration_date DESC
        """)
        
        members = cursor.fetchall()
        conn.close()
        return members
    
    def verify_member_login(self, email, password):
        """验证会员登录"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.customer_id, c.name, m.password_hash
            FROM customer c
            JOIN member_customers m ON c.customer_id = m.customer_id
            WHERE c.email = ? AND c.customer_type = 'MEMBER'
        """, (email,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and self.db_manager.verify_password(password, result[2]):
            return {'customer_id': result[0], 'name': result[1]}
        return None
    
    def update_order_status(self, order_id, status):
        """更新订单状态"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", 
                      (status.upper(), order_id))
        
        conn.commit()
        conn.close()
        
    def get_customer_by_id(self, customer_id):
        """根据ID获取客户信息"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT customer_id, name, phone, email, address, customer_type
            FROM customer
            WHERE customer_id = ?
        """, (customer_id,))
        
        customer = cursor.fetchone()
        conn.close()
        return customer