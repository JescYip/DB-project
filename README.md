# 咖啡订购系统 ☕

一个功能完整的咖啡店订购系统，包含现代化的用户界面、数据库管理和详细的业务报告功能。

## 🌟 功能特点

### 客户端功能
- **产品浏览**: 按分类展示咖啡和其他产品
- **购物车管理**: 添加、修改、删除商品
- **在线订购**: 完整的订单流程
- **订单历史**: 查看历史订单和详情
- **响应式设计**: 支持手机和桌面设备

### 管理后台
- **实时仪表盘**: 销售概况和关键指标
- **销售报告**: 按日期范围的详细销售分析
- **产品分析**: 产品销售排行和统计
- **客户分析**: 客户消费行为分析
- **订单管理**: 所有订单的统一管理

### 数据库功能
- **完整的关系型数据库设计**: 客户、产品、订单、分类等表
- **数据完整性**: 外键约束和数据验证
- **会员系统**: 支持普通客户和会员客户
- **SQL报告**: 使用复杂SQL查询生成管理报告

## 🚀 快速开始

### 环境要求
- Python 3.7+
- Flask 2.3+
- SQLite3

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd coffee-ordering-system
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动应用**
   ```bash
   python app.py
   ```

4. **访问系统**
   - 客户端: http://localhost:5000
   - 管理后台: http://localhost:5000/admin

## 📊 数据库结构

系统采用关系型数据库设计，包含以下主要表：

- **CYEAE_CUSTOMER**: 客户信息表
- **CYEAE_MEMBER_CUSTOMERS**: 会员客户表
- **CYEAE_CATEGORY**: 产品分类表
- **CYEAE_PRODUCT**: 产品信息表
- **CYEAE_ORDERS**: 订单表
- **CYEAE_ORDER_ITEMS**: 订单项表

## 🎯 主要功能

### 1. 产品管理
- 按分类展示产品（咖啡、茶饮、甜点、轻食）
- 产品价格和库存管理
- 产品销售统计

### 2. 订单处理
- 购物车功能
- 客户信息收集
- 多种支付方式支持
- 订单状态跟踪

### 3. 客户管理
- 客户信息管理
- 会员系统
- 客户消费分析

### 4. 报告系统
- **销售报告**: 按日期统计销售额、订单数、平均订单价值
- **产品报告**: 产品销售排行、收入统计
- **客户报告**: 客户消费排行、忠诚度分析

## 🛠 技术栈

### 后端
- **Flask**: Web框架
- **SQLite**: 数据库
- **Python**: 后端逻辑

### 前端
- **HTML5/CSS3**: 页面结构和样式
- **JavaScript**: 交互逻辑
- **响应式设计**: 适配各种设备

### 数据库
- **SQLite**: 轻量级关系型数据库
- **复杂SQL查询**: 生成各种业务报告

## 📱 界面预览

### 客户端界面
- 现代化的产品展示页面
- 直观的购物车管理
- 简洁的订单流程
- 清晰的订单历史

### 管理后台
- 实时数据仪表盘
- 详细的销售报告
- 产品和客户分析
- 订单管理界面

## 🔧 配置说明

### 数据库配置
系统会自动创建SQLite数据库文件 `coffee_shop.db`，并初始化示例数据。

### 示例数据
系统包含以下示例数据：
- 4个产品分类
- 10种产品
- 3个示例客户
- 1个会员客户（用户名：李四，密码：123456）

## 📈 报告功能

### SQL查询示例

1. **销售报告查询**
   ```sql
   SELECT 
       DATE(o.ORDER_DATE) as order_date,
       COUNT(o.ORDER_ID) as order_count,
       SUM(o.TOTAL_AMOUNT) as total_sales,
       AVG(o.TOTAL_AMOUNT) as avg_order_value
   FROM CYEAE_ORDERS o
   WHERE DATE(o.ORDER_DATE) BETWEEN ? AND ?
   GROUP BY DATE(o.ORDER_DATE)
   ORDER BY order_date DESC
   ```

2. **产品销售分析**
   ```sql
   SELECT 
       p.NAME as product_name,
       c.CATEGORY_NAME,
       SUM(oi.QUANTITY) as total_quantity,
       SUM(oi.LINE_AMOUNT) as total_revenue
   FROM CYEAE_ORDER_ITEMS oi
   JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
   JOIN CYEAE_CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
   GROUP BY p.PRODUCT_ID
   ORDER BY total_revenue DESC
   ```

## 🚀 部署建议

### 开发环境
- 使用内置的Flask开发服务器
- SQLite数据库文件

### 生产环境
- 使用Gunicorn或uWSGI部署
- 考虑使用PostgreSQL或MySQL数据库
- 配置反向代理（Nginx）
- 启用HTTPS

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用MIT许可证。

## 📞 支持

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**享受您的咖啡时光！** ☕✨