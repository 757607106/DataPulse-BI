-- ============================================================================
-- 进销存 BI 系统 - AI 分析专用宽表视图
-- 目标：为 Vanna AI 提供扁平化的多维度数据，避免复杂 JOIN 操作
-- 设计原则：
--   1. 所有分析维度铺平（分公司、部门、业务员、地区、往来单位、商品等）
--   2. 核心指标预计算（毛利、成本、销售额等）
--   3. 时间维度拆分（年、月、日）
-- ============================================================================


-- ============================================================================
-- 视图1: view_bi_sales_analysis - 销售毛利全景分析视图
-- 用途：支持 AI 回答销售额、毛利、商品、客户、业务员等多维度分析问题
-- 示例问题：
--   - "2024年华东地区的销售额和毛利是多少？"
--   - "张三业务员在电子产品类的毛利率是多少？"
--   - "北京分公司各部门的销售业绩排名？"
-- ============================================================================
CREATE OR REPLACE VIEW view_bi_sales_analysis AS
SELECT 
    -- ===== 主键和订单信息 =====
    o.id AS order_id,
    o.order_no,
    o.order_date,
    EXTRACT(YEAR FROM o.order_date) AS year,
    EXTRACT(MONTH FROM o.order_date) AS month,
    o.status AS order_status,
    
    -- ===== 扁平化维度：组织架构 =====
    d.company_name,                          -- 分公司（关键维度）
    d.name AS dept_name,                     -- 部门名称
    e.name AS salesman_name,                 -- 业务员姓名（关键维度）
    e.id AS salesman_id,
    
    -- ===== 扁平化维度：客户 =====
    p.name AS partner_name,                  -- 客户名称
    p.region,                                -- 客户地区（关键维度：华东/华北等）
    p.type AS partner_type,
    
    -- ===== 扁平化维度：商品 =====
    prod.name AS product_name,               -- 商品名称
    prod.category,                           -- 商品分类（关键维度）
    prod.specification,                      -- 规格型号
    prod.unit,                               -- 计量单位
    
    -- ===== 扁平化维度：仓库 =====
    w.name AS warehouse_name,
    w.location AS warehouse_location,
    
    -- ===== 核心指标：数量和金额 =====
    oi.quantity,                             -- 销售数量
    oi.price AS unit_price,                  -- 成交单价
    oi.subtotal AS sales_amount,             -- 销售额（数量*单价）
    
    -- ===== 核心指标：成本和毛利 =====
    prod.cost_price,                         -- 商品成本单价
    (oi.quantity * prod.cost_price) AS cost_amount,  -- 成本金额
    (oi.subtotal - oi.quantity * prod.cost_price) AS gross_profit,  -- 毛利（销售额-成本）
    CASE 
        WHEN oi.subtotal > 0 THEN 
            ROUND(((oi.subtotal - oi.quantity * prod.cost_price) / oi.subtotal * 100), 2)
        ELSE 0 
    END AS gross_profit_rate,                -- 毛利率（%）
    
    -- ===== 辅助字段 =====
    oi.remark AS item_remark,
    o.created_at,
    o.updated_at

FROM 
    biz_order o
    INNER JOIN biz_order_item oi ON o.id = oi.order_id
    INNER JOIN base_product prod ON oi.product_id = prod.id
    INNER JOIN sys_employee e ON o.salesman_id = e.id
    INNER JOIN sys_department d ON e.dept_id = d.id
    INNER JOIN base_partner p ON o.partner_id = p.id
    INNER JOIN base_warehouse w ON o.warehouse_id = w.id

WHERE 
    o.type = 'SALES'::ordertype                 -- 仅查询销售订单
    AND o.status IN ('CONFIRMED'::orderstatus, 'COMPLETED'::orderstatus)  -- 仅统计已确认/已完成订单
    AND prod.is_active = TRUE                -- 仅统计启用的商品
    AND e.is_active = TRUE;                  -- 仅统计在职业务员


-- ============================================================================
-- 视图2: view_bi_finance_monitor - 资金费用综合监控视图
-- 用途：支持 AI 回答应收应付、费用、欠款等财务分析问题
-- 示例问题：
--   - "北京分公司本月的费用总额是多少？"
--   - "华南地区客户的应收账款余额是多少？"
--   - "差旅费支出最多的部门是哪个？"
-- ============================================================================
CREATE OR REPLACE VIEW view_bi_finance_monitor AS
SELECT 
    -- ===== 主键和财务信息 =====
    f.id AS finance_id,
    f.type AS record_type,                   -- 记录类型：receivable/payable/expense
    f.trans_date,
    EXTRACT(YEAR FROM f.trans_date) AS year,
    EXTRACT(MONTH FROM f.trans_date) AS month,
    
    -- ===== 扁平化维度：组织架构 =====
    d.company_name,                          -- 分公司（关键维度）
    d.name AS dept_name,                     -- 部门名称
    e.name AS salesman_name,                 -- 经办业务员
    e.id AS salesman_id,
    
    -- ===== 扁平化维度：往来单位（应收应付时有效）=====
    p.name AS partner_name,                  -- 往来单位名称
    p.region,                                -- 往来单位地区
    p.type AS partner_type,                  -- customer/supplier
    
    -- ===== 核心指标：金额 =====
    f.amount AS trans_amount,                -- 交易金额（用于统计费用支出）
    f.balance AS current_balance,            -- 当前余额（用于统计应收应付欠款）
    
    -- ===== 费用分类（仅 type=expense 时有效）=====
    f.expense_category,                      -- 费用科目：差旅费、房租、水电费等
    
    -- ===== 辅助字段 =====
    f.description,
    f.created_at

FROM 
    fact_finance f
    INNER JOIN sys_department d ON f.dept_id = d.id
    LEFT JOIN sys_employee e ON f.salesman_id = e.id  -- 费用可能没有业务员
    LEFT JOIN base_partner p ON f.partner_id = p.id   -- 费用没有往来单位

WHERE 
    (e.is_active = TRUE OR e.id IS NULL);    -- 在职业务员或无业务员的记录


-- ============================================================================
-- 视图3: view_bi_inventory_alert - 库存预警分析视图
-- 用途：支持 AI 回答库存不足、滞销商品等问题
-- 示例问题：
--   - "哪些商品的库存低于预警线？"
--   - "上海仓库有哪些商品库存为0？"
--   - "电子产品类的总库存量是多少？"
-- ============================================================================
CREATE OR REPLACE VIEW view_bi_inventory_alert AS
SELECT 
    -- ===== 主键 =====
    s.id AS stock_id,
    
    -- ===== 扁平化维度：仓库 =====
    w.name AS warehouse_name,
    w.location AS warehouse_location,
    w.manager AS warehouse_manager,
    
    -- ===== 扁平化维度：商品 =====
    p.name AS product_name,
    p.category,                              -- 商品分类
    p.specification,
    p.unit,
    
    -- ===== 核心指标：库存 =====
    s.quantity AS current_stock,             -- 当前库存数量
    p.min_stock,                             -- 最低库存预警线
    (s.quantity - COALESCE(p.min_stock, 0)) AS stock_diff,  -- 库存差额
    
    -- ===== 库存状态标识 =====
    CASE 
        WHEN s.quantity <= 0 THEN '缺货'
        WHEN p.min_stock IS NOT NULL AND s.quantity < p.min_stock THEN '库存不足'
        WHEN p.min_stock IS NOT NULL AND s.quantity >= p.min_stock * 3 THEN '库存充足'
        ELSE '正常'
    END AS stock_status,
    
    -- ===== 成本信息 =====
    p.cost_price,
    (s.quantity * p.cost_price) AS total_stock_value,  -- 库存总价值
    
    -- ===== 辅助字段 =====
    s.last_updated,
    p.is_active

FROM 
    inv_current_stock s
    INNER JOIN base_warehouse w ON s.warehouse_id = w.id
    INNER JOIN base_product p ON s.product_id = p.id

WHERE 
    w.is_active = TRUE                       -- 仅统计启用的仓库
    AND p.is_active = TRUE;                  -- 仅统计启用的商品


-- ============================================================================
-- 视图4: view_bi_purchase_analysis - 采购分析视图
-- 用途：支持 AI 回答采购金额、供应商、采购员等分析问题
-- 示例问题：
--   - "2024年从哪个供应商采购最多？"
--   - "华东地区供应商的采购金额是多少？"
--   - "原材料类的采购数量趋势？"
-- ============================================================================
CREATE OR REPLACE VIEW view_bi_purchase_analysis AS
SELECT 
    -- ===== 主键和订单信息 =====
    o.id AS order_id,
    o.order_no,
    o.order_date,
    EXTRACT(YEAR FROM o.order_date) AS year,
    EXTRACT(MONTH FROM o.order_date) AS month,
    o.status AS order_status,
    
    -- ===== 扁平化维度：组织架构 =====
    d.company_name,                          -- 分公司
    d.name AS dept_name,                     -- 部门名称
    e.name AS buyer_name,                    -- 采购员姓名
    e.id AS buyer_id,
    
    -- ===== 扁平化维度：供应商 =====
    p.name AS supplier_name,                 -- 供应商名称
    p.region AS supplier_region,             -- 供应商地区
    p.contact_person,
    
    -- ===== 扁平化维度：商品 =====
    prod.name AS product_name,
    prod.category,
    prod.specification,
    prod.unit,
    
    -- ===== 扁平化维度：仓库 =====
    w.name AS warehouse_name,
    w.location AS warehouse_location,
    
    -- ===== 核心指标：数量和金额 =====
    oi.quantity AS purchase_quantity,
    oi.price AS unit_price,
    oi.subtotal AS purchase_amount,          -- 采购金额
    
    -- ===== 辅助字段 =====
    oi.remark AS item_remark,
    o.created_at,
    o.updated_at

FROM 
    biz_order o
    INNER JOIN biz_order_item oi ON o.id = oi.order_id
    INNER JOIN base_product prod ON oi.product_id = prod.id
    INNER JOIN sys_employee e ON o.salesman_id = e.id
    INNER JOIN sys_department d ON e.dept_id = d.id
    INNER JOIN base_partner p ON o.partner_id = p.id
    INNER JOIN base_warehouse w ON o.warehouse_id = w.id

WHERE 
    o.type = 'PURCHASE'::ordertype               -- 仅查询采购订单
    AND o.status IN ('CONFIRMED'::orderstatus, 'COMPLETED'::orderstatus)
    AND prod.is_active = TRUE
    AND e.is_active = TRUE;


-- ============================================================================
-- 索引建议（在实际表上创建，提升视图查询性能）
-- ============================================================================

-- 订单表索引
-- CREATE INDEX idx_biz_order_date_type ON biz_order(order_date, type);
-- CREATE INDEX idx_biz_order_salesman ON biz_order(salesman_id);
-- CREATE INDEX idx_biz_order_partner ON biz_order(partner_id);

-- 财务表索引
-- CREATE INDEX idx_fact_finance_date_type ON fact_finance(trans_date, type);
-- CREATE INDEX idx_fact_finance_dept ON fact_finance(dept_id);
-- CREATE INDEX idx_fact_finance_expense_cat ON fact_finance(expense_category);

-- 商品表索引
-- CREATE INDEX idx_base_product_category ON base_product(category);

-- 部门表索引
-- CREATE INDEX idx_sys_dept_company ON sys_department(company_name);

-- ============================================================================
-- 使用说明
-- ============================================================================
-- 1. 这些视图专为 Vanna AI 设计，所有维度已扁平化，AI 可以直接查询而无需理解复杂的 JOIN 逻辑
-- 2. 视图中的字段名都具有业务含义，便于 AI 理解用户的自然语言问题
-- 3. 核心指标已预计算（如毛利、毛利率、库存价值等），提升查询效率
-- 4. 时间维度已拆分为 year/month，便于按时间维度聚合分析
-- 5. 建议在生产环境中对基础表创建适当的索引以提升视图性能
-- ============================================================================
