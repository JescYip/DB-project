-- SQLite 兼容版本的 jessdb.sql
-- 从 Oracle SQL 转换而来

-- 安全清理
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS member_customers;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS customer;
PRAGMA foreign_keys = ON;

-- 基础表
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
  line_amount     DECIMAL(10,2),
  FOREIGN KEY (order_id)  REFERENCES orders(order_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- 触发器
CREATE TRIGGER trg_mc_insupd
BEFORE INSERT ON member_customers
FOR EACH ROW
WHEN (SELECT customer_type FROM customer WHERE customer_id = NEW.customer_id) != 'MEMBER'
BEGIN
  SELECT RAISE(ABORT, 'CustomerType must be MEMBER to have member_customers row.');
END;

CREATE TRIGGER trg_customer_type_guard
BEFORE UPDATE OF customer_type ON customer
FOR EACH ROW
WHEN NEW.customer_type = 'GUEST' AND 
     (SELECT COUNT(*) FROM member_customers WHERE customer_id = OLD.customer_id) > 0
BEGIN
  SELECT RAISE(ABORT, 'Cannot change to GUEST while member record exists.');
END;

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

-- 演示数据
INSERT INTO category(category_name, description) VALUES ('Coffee','Various types of coffee drinks');
INSERT INTO category(category_name, description) VALUES ('Tea','Traditional and specialty teas');
INSERT INTO category(category_name, description) VALUES ('Bakery','Fresh pastries and desserts');
INSERT INTO category(category_name, description) VALUES ('Smoothies', 'Fruit and yogurt smoothies');
INSERT INTO category(category_name, description) VALUES ('Sandwiches', 'Freshly made sandwiches');
INSERT INTO category(category_name, description) VALUES ('Seasonal', 'Limited-time seasonal specials');
INSERT INTO category(category_name, description) VALUES ('Cold Brew', 'Cold brew coffee selection');

-- 商品
INSERT INTO product(name, price, is_active, category_id) VALUES ('Americano', 30, 'Y', 1);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Latte', 35, 'Y', 1);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Green Tea', 25, 'Y', 2);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Chocolate Cake', 45, 'Y', 3);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Strawberry Smoothie', 38, 'Y', 4);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Mango Smoothie', 40, 'Y', 4);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Chicken Sandwich', 42, 'Y', 5);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Tuna Sandwich', 39, 'Y', 5);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Pumpkin Spice Latte', 48, 'Y', 6);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Gingerbread Latte', 50, 'Y', 6);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Classic Cold Brew', 36, 'Y', 7);
INSERT INTO product(name, price, is_active, category_id) VALUES ('Nitro Cold Brew', 42, 'Y', 7);

-- 客户数据
INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Wei Zhang', '+85212345678', 'wei.zhang@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (1, 'hashed_password_1', '1990-01-15');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Mei Li', '+85287654321', 'mei.li@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (2, 'hashed_password_2', '1985-08-22');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Li Wei', '+85268001234', 'li.wei@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (3, 'pw_liwei', '1992-02-09');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Chen Yang', '+85268004567', 'chen.yang@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (4, 'pw_cy', '1995-11-23');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Wang Yu', '+85268007890', 'wang.yu@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (5, 'pw_wy', '1988-05-17');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Zhao Ling', '+85268001122', 'zhao.ling@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (6, 'pw_zl', '1993-07-02');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Liu Mei', '+85268003344', 'liu.mei@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (7, 'pw_lm', '1997-03-28');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Zhang Qian', '+85268005566', 'zhang.qian@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (8, 'pw_zq', '1990-10-10');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Sun Hao', '+85268007788', 'sun.hao@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (9, 'pw_sh', '1986-12-30');

INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Gao Nan', '+85268009900', 'gao.nan@email.com', NULL, 'MEMBER');
INSERT INTO member_customers (customer_id, password_hash, date_of_birth) VALUES (10, 'pw_gn', '1994-06-15');

-- 散客
INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('San Zhang', '+85255556666', NULL, NULL, 'GUEST');
INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Si Li', '+85299998888', NULL, NULL, 'GUEST');
INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Guest A', '+85270110001', NULL, NULL, 'GUEST');
INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Guest B', '+85270110002', NULL, NULL, 'GUEST');
INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Guest C', '+85270110003', NULL, NULL, 'GUEST');
INSERT INTO customer (name, phone, email, address, customer_type) VALUES ('Guest D', '+85270110004', NULL, NULL, 'GUEST');

-- 示例订单
INSERT INTO orders (customer_id, status, payment_method, total_amount) VALUES (1, 'PLACED', 'CREDIT CARD', 65);
INSERT INTO orders (customer_id, status, payment_method, total_amount) VALUES (2, 'COMPLETED', 'ALIPAY', 45);

-- 订单明细
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (1, 1, 1, 30);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (1, 2, 1, 35);
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (2, 4, 1, 45);