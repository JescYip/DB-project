----------------------------------------------------------------
-- SQLite 兼容版本的 jessdb.sql
-- 从 Oracle SQL 转换而来
----------------------------------------------------------------

-- 0) 安全清理（可反复执行）
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS member_customers;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS customer;
PRAGMA foreign_keys = ON;

----------------------------------------------------------------
-- 1) 基础表
----------------------------------------------------------------
CREATE TABLE customer (
  customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  name            VARCHAR(100)   NOT NULL,
  phone           VARCHAR(30),
  email           VARCHAR(120),
  address         VARCHAR(255),
  customer_type   VARCHAR(10)    NOT NULL
    CHECK (customer_type IN ('MEMBER','GUEST'))
);

CREATE TABLE category (
  category_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  category_name   VARCHAR(80) NOT NULL UNIQUE,
  description     VARCHAR(255)
);

CREATE TABLE product (
  product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
  name            VARCHAR(120)  NOT NULL,
  price           DECIMAL(10,2)   NOT NULL CHECK (price >= 0),
  is_active       CHAR(1)        DEFAULT 'Y' NOT NULL CHECK (is_active IN ('Y','N')),
  category_id     INTEGER         NOT NULL,
  FOREIGN KEY (category_id) REFERENCES category(category_id)
);

CREATE TABLE member_customers (
  customer_id        INTEGER       PRIMARY KEY,
  password_hash      VARCHAR(255),
  date_of_birth      DATE,
  registration_date  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE
);

CREATE TABLE orders (
  order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id     INTEGER NOT NULL,
  order_date      DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  status          VARCHAR(20) NOT NULL,
  payment_method  VARCHAR(20) NOT NULL,
  total_amount    DECIMAL(12,2) DEFAULT 0 NOT NULL CHECK (total_amount >= 0),
  FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

CREATE TABLE order_items (
  order_item_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id        INTEGER NOT NULL,
  product_id      INTEGER NOT NULL,
  quantity        INTEGER NOT NULL CHECK (quantity > 0),
  unit_price      DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
  -- SQLite 不支持虚拟列，改为普通列
  line_amount     DECIMAL(10,2),
  FOREIGN KEY (order_id)  REFERENCES orders(order_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES product(product_id)
);

----------------------------------------------------------------
-- 2) orders 的 CHECK 约束
----------------------------------------------------------------
-- SQLite 的 CHECK 约束相对简单，不支持 UPPER() 函数
-- 我们将在应用层处理大小写转换

----------------------------------------------------------------
-- 3) 触发器（SQLite 版本）
----------------------------------------------------------------
-- A) 在 member_customers 插入/更新时，父表类型必须是 MEMBER
CREATE TRIGGER trg_mc_insupd
BEFORE INSERT ON member_customers
FOR EACH ROW
WHEN (SELECT customer_type FROM customer WHERE customer_id = NEW.customer_id) != 'MEMBER'
BEGIN
  SELECT RAISE(ABORT, 'CustomerType must be MEMBER to have member_customers row.');
END;

-- B) 父表改类型时，若已有子表记录，不允许改为 GUEST
CREATE TRIGGER trg_customer_type_guard
BEFORE UPDATE OF customer_type ON customer
FOR EACH ROW
WHEN NEW.customer_type = 'GUEST' AND 
     (SELECT COUNT(*) FROM member_customers WHERE customer_id = OLD.customer_id) > 0
BEGIN
  SELECT RAISE(ABORT, 'Cannot change to GUEST while member record exists.');
END;

-- C) 自动计算 line_amount 的触发器
CREATE TRIGGER trg_order_items_line_amount_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
  UPDATE order_items 
  SET line_amount = NEW.quantity * NEW.unit_price 
  WHERE order_item_id = NEW.order_item_id;
END;

CREATE TRIGGER trg_order_items_line_amount_update
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
  UPDATE order_items 
  SET line_amount = NEW.quantity * NEW.unit_price 
  WHERE order_item_id = NEW.order_item_id;
END;

----------------------------------------------------------------
-- 4) 演示数据
----------------------------------------------------------------
-- 类别
INSERT INTO category(category_name, description) VALUES ('Coffee','Various types of coffee drinks');
INSERT INTO category(category_name, description) VALUES ('Tea','Traditional and specialty teas');
INSERT INTO category(category_name, description) VALUES ('Bakery','Fresh pastries and desserts');

-- 商品
INSERT INTO product(name, price, is_active, category_id)
SELECT 'Americano', 30, 'Y', category_id FROM category WHERE category_name='Coffee';
INSERT INTO product(name, price, is_active, category_id)
SELECT 'Latte', 35, 'Y', category_id FROM category WHERE category_name='Coffee';
INSERT INTO product(name, price, is_active, category_id)
SELECT 'Green Tea', 25, 'Y', category_id FROM category WHERE category_name='Tea';
INSERT INTO product(name, price, is_active, category_id)
SELECT 'Chocolate Cake', 45, 'Y', category_id FROM category WHERE category_name='Bakery';

-- 客户：2 会员 + 2 游客
-- 会员客户 1
INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Wei Zhang', '+85212345678', 'wei.zhang@email.com', NULL, 'MEMBER');

INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'hashed_password_1', '1990-01-15');

-- 会员客户 2
INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Mei Li', '+85287654321', 'mei.li@email.com', NULL, 'MEMBER');

INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'hashed_password_2', '1985-08-22');

-- 游客
INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('San Zhang', '+85255556666', NULL, NULL, 'GUEST');

INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Si Li', '+85299998888', NULL, NULL, 'GUEST');

-- 更多类别
INSERT OR IGNORE INTO category(category_name, description) VALUES ('Smoothies', 'Fruit and yogurt smoothies');
INSERT OR IGNORE INTO category(category_name, description) VALUES ('Sandwiches', 'Freshly made sandwiches');
INSERT OR IGNORE INTO category(category_name, description) VALUES ('Seasonal', 'Limited-time seasonal specials');
INSERT OR IGNORE INTO category(category_name, description) VALUES ('Cold Brew', 'Cold brew coffee selection');

-- 商品（每类 2–3 个）
INSERT INTO product (name, price, is_active, category_id)
SELECT 'Strawberry Smoothie', 38, 'Y', category_id FROM category WHERE category_name='Smoothies';
INSERT INTO product (name, price, is_active, category_id)
SELECT 'Mango Smoothie', 40, 'Y', category_id FROM category WHERE category_name='Smoothies';

INSERT INTO product (name, price, is_active, category_id)
SELECT 'Chicken Sandwich', 42, 'Y', category_id FROM category WHERE category_name='Sandwiches';
INSERT INTO product (name, price, is_active, category_id)
SELECT 'Tuna Sandwich', 39, 'Y', category_id FROM category WHERE category_name='Sandwiches';

INSERT INTO product (name, price, is_active, category_id)
SELECT 'Pumpkin Spice Latte', 48, 'Y', category_id FROM category WHERE category_name='Seasonal';
INSERT INTO product (name, price, is_active, category_id)
SELECT 'Gingerbread Latte', 50, 'Y', category_id FROM category WHERE category_name='Seasonal';

INSERT INTO product (name, price, is_active, category_id)
SELECT 'Classic Cold Brew', 36, 'Y', category_id FROM category WHERE category_name='Cold Brew';
INSERT INTO product (name, price, is_active, category_id)
SELECT 'Nitro Cold Brew', 42, 'Y', category_id FROM category WHERE category_name='Cold Brew';

-- 更多会员客户
INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Li Wei', '+85268001234', 'li.wei@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'pw_liwei', '1992-02-09');

INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Chen Yang', '+85268004567', 'chen.yang@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'pw_cy', '1995-11-23');

INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Wang Yu', '+85268007890', 'wang.yu@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'pw_wy', '1988-05-17');

INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Zhao Ling', '+85268001122', 'zhao.ling@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'pw_zl', '1993-07-02');

INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Liu Mei', '+85268003344', 'liu.mei@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'pw_lm', '1997-03-28');

INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Zhang Qian', '+85268005566', 'zhang.qian@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'pw_zq', '1990-10-10');

INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Sun Hao', '+85268007788', 'sun.hao@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'pw_sh', '1986-12-30');

INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Gao Nan', '+85268009900', 'gao.nan@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth)
VALUES (last_insert_rowid(), 'pw_gn', '1994-06-15');

-- 更多散客
INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Guest A', '+85270110001', NULL, NULL, 'GUEST');
INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Guest B', '+85270110002', NULL, NULL, 'GUEST');
INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Guest C', '+85270110003', NULL, NULL, 'GUEST');
INSERT INTO customer (name, phone, email, address, customer_type)
VALUES ('Guest D', '+85270110004', NULL, NULL, 'GUEST');

----------------------------------------------------------------
-- 6) 订单示例
----------------------------------------------------------------
INSERT INTO orders (customer_id, status, payment_method, total_amount)
SELECT customer_id, 'PLACED', 'CREDIT CARD', 65
FROM customer WHERE name='Wei Zhang';

INSERT INTO orders (customer_id, status, payment_method, total_amount)
SELECT customer_id, 'COMPLETED', 'ALIPAY', 45
FROM customer WHERE name='Mei Li';

-- 订单明细
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT o.order_id, p.product_id, 1, p.price
FROM orders o
JOIN product p ON p.name='Americano'
WHERE o.total_amount >= 0
LIMIT 1;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT o.order_id, p.product_id, 2, p.price
FROM orders o
JOIN product p ON p.name='Latte'
WHERE o.total_amount >= 0
LIMIT 1 OFFSET 1;

----------------------------------------------------------------
-- 7) 校验查询
----------------------------------------------------------------
-- 会员 / 非会员人数
SELECT customer_type, COUNT(*) cnt
FROM customer
GROUP BY customer_type;

-- 检查所有 MEMBER 是否都在子表有记录（应为 0）
SELECT COUNT(*) AS member_without_child
FROM customer c
LEFT JOIN member_customers m ON m.customer_id = c.customer_id
WHERE c.customer_type = 'MEMBER' AND m.customer_id IS NULL;

-- 查看客户 + 会员注册时间（email 来自父表）
SELECT c.customer_id, c.name, c.customer_type, c.phone, c.email, m.registration_date
FROM customer c
LEFT JOIN member_customers m ON m.customer_id = c.customer_id
ORDER BY c.customer_id;

-- 检查订单的状态与支付方式
SELECT order_id, status, payment_method, total_amount
FROM orders
ORDER BY order_id;

-- 明细合计校验（示例）
SELECT oi.order_id,
       SUM(oi.line_amount) AS detail_sum,
       (SELECT total_amount FROM orders o WHERE o.order_id=oi.order_id) AS order_total
FROM order_items oi
GROUP BY oi.order_id;