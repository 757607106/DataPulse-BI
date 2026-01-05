"""
进销存 BI 系统 - 数据库初始化与数据填充脚本

功能：
1. 重置并创建数据库表结构
2. 创建 AI 分析视图
3. 填充基础维度数据（分公司、部门、人员、仓库、往来单位、商品）
4. 生成核心业务数据（销售订单、库存、财务流水）

使用方法：
    python -m scripts.init_db
"""
import os
import sys
import random
from datetime import datetime, timedelta, date
from decimal import Decimal
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.bi_schema import (
    Base,
    # 维度表
    SysUser,
    SysDepartment, SysEmployee, BasePartner, BaseWarehouse, BaseProduct,
    # 事实表
    BizOrder, BizOrderItem, FactFinance, InvCurrentStock,
    # 枚举类型
    PartnerType, OrderType, OrderStatus, FinanceRecordType
)

# 初始化 Faker (中文)
fake = Faker('zh_CN')
Faker.seed(42)
random.seed(42)


def print_step(step_num: int, message: str):
    """打印步骤信息"""
    print(f"\n{'=' * 70}")
    print(f"步骤 {step_num}: {message}")
    print('=' * 70)


def create_database_tables(engine):
    """步骤1: 重置与建表"""
    print_step(1, "重置与建表")
    
    # 删除所有视图（避免依赖冲突）
    print("🗑️  删除现有视图...")
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS view_bi_sales_analysis CASCADE"))
        conn.execute(text("DROP VIEW IF EXISTS view_bi_finance_monitor CASCADE"))
        conn.execute(text("DROP VIEW IF EXISTS view_bi_inventory_alert CASCADE"))
        conn.execute(text("DROP VIEW IF EXISTS view_bi_purchase_analysis CASCADE"))
        conn.commit()
    
    # 删除所有表
    print("🗑️  删除现有表...")
    Base.metadata.drop_all(bind=engine)
    
    # 创建所有表
    print("📦 创建表结构...")
    Base.metadata.create_all(bind=engine)
    print("✅ 表结构创建完成！")


def create_ai_views(engine):
    """步骤2: 创建 AI 视图"""
    print_step(2, "创建 AI 分析视图")
    
    views_sql_path = Path(__file__).parent.parent / "app" / "db" / "init_views.sql"
    
    if not views_sql_path.exists():
        print(f"❌ 未找到视图 SQL 文件: {views_sql_path}")
        return
    
    print(f"📄 读取 SQL 文件: {views_sql_path}")
    
    # 使用 psql 命令直接执行 SQL 文件（最可靠）
    import subprocess
    
    # 从 settings 获取数据库连接信息
    db_url = settings.database_url_sync
    # 解析: postgresql+psycopg2://postgres:postgres123@localhost:5432/inventory_bi
    if 'postgresql' in db_url:
        parts = db_url.replace('postgresql+psycopg2://', '').replace('postgresql://', '')
        user_pass, host_db = parts.split('@')
        user, password = user_pass.split(':')
        host_port, database = host_db.split('/')
        host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
        
        cmd = [
            'psql',
            '-h', host,
            '-U', user,
            '-d', database,
            '-f', str(views_sql_path)
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ AI 分析视图创建完成！")
                # 统计创建了多少个视图
                view_count = result.stdout.count('CREATE VIEW')
                if view_count > 0:
                    print(f"  ✓ 创建了 {view_count} 个视图")
            else:
                print(f"❌ 视图创建失败: {result.stderr}")
        except FileNotFoundError:
            print("❌ psql 命令未找到，尝试使用 SQLAlchemy 执行...")
            # 备选方案：使用 SQLAlchemy
            _create_views_with_sqlalchemy(engine, views_sql_path)
    else:
        _create_views_with_sqlalchemy(engine, views_sql_path)


def _create_views_with_sqlalchemy(engine, views_sql_path):
    """备选方案：使用 SQLAlchemy 创建视图"""
    with open(views_sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 执行每个 CREATE OR REPLACE VIEW 语句
    with engine.begin() as conn:
        # 使用正则表达式分割 SQL
        import re
        view_pattern = r'CREATE OR REPLACE VIEW.*?;'
        view_statements = re.findall(view_pattern, sql_content, re.DOTALL | re.IGNORECASE)
        
        for statement in view_statements:
            try:
                conn.execute(text(statement))
                # 提取视图名
                match = re.search(r'VIEW\s+(\w+)', statement, re.IGNORECASE)
                if match:
                    print(f"  ✓ 创建视图: {match.group(1)}")
            except Exception as e:
                print(f"  ❌ 视图创建失败: {e}")
    
    print("✅ 视图创建完成")


def populate_dimensions(session):
    """步骤3: 填充基础维度数据"""
    print_step(3, "填充基础维度数据")
    
    # 3.0 创建测试用户（用于登录）
    print("\n👤 创建测试用户...")
    test_users = [
        SysUser(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        ),
        SysUser(
            username="user",
            hashed_password=get_password_hash("user123"),
            role="user",
            is_active=True
        )
    ]
    for user in test_users:
        session.add(user)
    session.commit()
    print(f"  ✓ 创建了 {len(test_users)} 个测试用户")
    print("    - admin/admin123 (管理员)")
    print("    - user/user123 (普通用户)")
    
    # 3.1 创建分公司和部门
    print("\n🏢 创建分公司和部门...")
    companies = ["北京总公司", "上海分公司", "广州分公司"]
    departments = []
    
    for company_name in companies:
        dept_names = ["销售一部", "销售二部"]
        for dept_name in dept_names:
            dept = SysDepartment(
                name=dept_name,
                company_name=company_name
            )
            departments.append(dept)
            session.add(dept)
    
    session.commit()
    print(f"  ✓ 创建了 {len(departments)} 个部门")
    
    # 3.2 创建业务员
    print("\n👥 创建业务员...")
    employees = []
    for dept in departments:
        num_employees = random.randint(3, 5)
        for _ in range(num_employees):
            emp = SysEmployee(
                name=fake.name(),
                dept_id=dept.id,
                email=fake.email(),
                phone=fake.phone_number(),
                is_active=True
            )
            employees.append(emp)
            session.add(emp)
    
    session.commit()
    print(f"  ✓ 创建了 {len(employees)} 名业务员")
    
    # 3.3 创建仓库
    print("\n🏪 创建仓库...")
    warehouses = [
        BaseWarehouse(name="华东一仓", location="上海市浦东新区", manager=fake.name()),
        BaseWarehouse(name="华北二仓", location="北京市朝阳区", manager=fake.name()),
        BaseWarehouse(name="华南三仓", location="广州市天河区", manager=fake.name()),
    ]
    for warehouse in warehouses:
        session.add(warehouse)
    
    session.commit()
    print(f"  ✓ 创建了 {len(warehouses)} 个仓库")
    
    # 3.4 创建往来单位
    print("\n🤝 创建往来单位...")
    regions = ["华东", "华北", "华南", "华中", "西南"]
    partners = []
    
    # 20 个客户
    for i in range(20):
        partner = BasePartner(
            name=f"{fake.company()}有限公司",
            type=PartnerType.CUSTOMER,
            region=random.choice(regions),
            contact_person=fake.name(),
            phone=fake.phone_number(),
            address=fake.address(),
            credit_limit=Decimal(random.randint(100000, 1000000))
        )
        partners.append(partner)
        session.add(partner)
    
    # 10 个供应商
    for i in range(10):
        partner = BasePartner(
            name=f"{fake.company()}供应商",
            type=PartnerType.SUPPLIER,
            region=random.choice(regions),
            contact_person=fake.name(),
            phone=fake.phone_number(),
            address=fake.address(),
            credit_limit=Decimal(random.randint(50000, 500000))
        )
        partners.append(partner)
        session.add(partner)
    
    session.commit()
    print(f"  ✓ 创建了 {len(partners)} 个往来单位 (20客户 + 10供应商)")
    
    # 3.5 创建商品
    print("\n📦 创建商品...")
    categories = {
        "电子产品": ["笔记本电脑", "台式机", "显示器", "键盘", "鼠标", "耳机", "音箱", "摄像头", "路由器", "硬盘"],
        "家居用品": ["办公椅", "办公桌", "书柜", "沙发", "茶几", "台灯", "挂钟", "地毯", "窗帘", "抱枕"],
        "食品饮料": ["咖啡", "茶叶", "矿泉水", "零食", "水果", "饼干", "糖果", "巧克力", "果汁", "牛奶"]
    }
    
    products = []
    for category, product_names in categories.items():
        for name in product_names:
            product = BaseProduct(
                name=name,
                category=category,
                specification=f"{fake.color_name()}/{random.randint(1, 5)}号",
                unit=random.choice(["件", "台", "个", "盒", "瓶"]),
                cost_price=Decimal(random.randint(50, 5000)),
                min_stock=Decimal(random.randint(10, 50))
            )
            products.append(product)
            session.add(product)
    
    session.commit()
    print(f"  ✓ 创建了 {len(products)} 个商品 (3个分类)")
    
    return {
        'departments': departments,
        'employees': employees,
        'warehouses': warehouses,
        'partners': partners,
        'products': products
    }


def generate_sales_orders(session, data_dict):
    """步骤4.1: 生成销售订单"""
    print_step(4, "生成核心业务数据")
    print("\n📊 生成销售订单...")
    
    employees = data_dict['employees']
    customers = [p for p in data_dict['partners'] if p.type == PartnerType.CUSTOMER]
    warehouses = data_dict['warehouses']
    products = data_dict['products']
    
    # 生成过去 90 天的订单
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    orders_count = 0
    items_count = 0
    
    for day_offset in range(90):
        current_date = start_date + timedelta(days=day_offset)
        
        # 周末订单量更多
        is_weekend = current_date.weekday() >= 5
        daily_orders = random.randint(8, 12) if is_weekend else random.randint(3, 7)
        
        for _ in range(daily_orders):
            # 创建订单
            order = BizOrder(
                order_no=f"SO{current_date.strftime('%Y%m%d')}{random.randint(1000, 9999)}",
                type=OrderType.SALES,
                order_date=current_date.date(),
                status=random.choice([OrderStatus.CONFIRMED, OrderStatus.COMPLETED]),
                salesman_id=random.choice(employees).id,
                partner_id=random.choice(customers).id,
                warehouse_id=random.choice(warehouses).id,
                total_amount=Decimal(0)  # 后面计算
            )
            session.add(order)
            session.flush()  # 获取 order.id
            
            # 创建订单明细 (2-5 个商品)
            num_items = random.randint(2, 5)
            order_total = Decimal(0)
            
            for _ in range(num_items):
                product = random.choice(products)
                quantity = Decimal(random.randint(1, 20))
                # 售价 = 成本价 * (1.2 - 1.5)
                price = product.cost_price * Decimal(random.uniform(1.2, 1.5))
                subtotal = quantity * price
                
                item = BizOrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=price,
                    subtotal=subtotal
                )
                session.add(item)
                order_total += subtotal
                items_count += 1
            
            # 更新订单总金额
            order.total_amount = order_total
            orders_count += 1
        
        # 每 10 天提交一次
        if day_offset % 10 == 0:
            session.commit()
            print(f"  进度: {day_offset}/90 天, 已生成 {orders_count} 个订单")
    
    session.commit()
    print(f"  ✓ 生成了 {orders_count} 个销售订单，{items_count} 个订单明细")


def generate_inventory(session, data_dict):
    """步骤4.2: 生成库存数据"""
    print("\n📦 生成库存数据...")
    
    warehouses = data_dict['warehouses']
    products = data_dict['products']
    
    stock_count = 0
    alert_count = 0
    
    for warehouse in warehouses:
        for product in products:
            # 70% 的商品有库存
            if random.random() < 0.7:
                # 30% 的商品库存低于预警线
                if random.random() < 0.3:
                    quantity = Decimal(random.randint(0, int(product.min_stock)))
                    alert_count += 1
                else:
                    quantity = Decimal(random.randint(int(product.min_stock), int(product.min_stock) * 5))
                
                stock = InvCurrentStock(
                    warehouse_id=warehouse.id,
                    product_id=product.id,
                    quantity=quantity
                )
                session.add(stock)
                stock_count += 1
    
    session.commit()
    print(f"  ✓ 生成了 {stock_count} 条库存记录，其中 {alert_count} 条低于预警线")


def generate_finance_records(session, data_dict):
    """步骤4.3: 生成财务流水"""
    print("\n💰 生成财务流水...")
    
    departments = data_dict['departments']
    employees = data_dict['employees']
    customers = [p for p in data_dict['partners'] if p.type == PartnerType.CUSTOMER]
    
    finance_count = 0
    
    # 生成应收账款
    for _ in range(50):
        record = FactFinance(
            type=FinanceRecordType.RECEIVABLE,
            trans_date=(datetime.now() - timedelta(days=random.randint(1, 90))).date(),
            amount=Decimal(random.randint(10000, 100000)),
            balance=Decimal(random.randint(0, 50000)),
            partner_id=random.choice(customers).id,
            dept_id=random.choice(departments).id,
            salesman_id=random.choice(employees).id,
            description=f"销售回款 - {fake.company()}"
        )
        session.add(record)
        finance_count += 1
    
    # 生成费用支出
    expense_categories = ["差旅费", "房租", "招待费", "办公费", "水电费", "通讯费"]
    for _ in range(100):
        record = FactFinance(
            type=FinanceRecordType.EXPENSE,
            trans_date=(datetime.now() - timedelta(days=random.randint(1, 90))).date(),
            amount=Decimal(random.randint(1000, 20000)),
            balance=None,
            partner_id=None,
            dept_id=random.choice(departments).id,
            salesman_id=random.choice(employees).id if random.random() > 0.3 else None,
            expense_category=random.choice(expense_categories),
            description=f"{random.choice(expense_categories)} - {fake.sentence()}"
        )
        session.add(record)
        finance_count += 1
    
    session.commit()
    print(f"  ✓ 生成了 {finance_count} 条财务流水记录 (50应收 + 100费用)")


def print_summary(session):
    """打印数据统计摘要"""
    print_step(5, "数据统计摘要")
    
    stats = {
        "测试用户": session.query(SysUser).count(),
        "部门": session.query(SysDepartment).count(),
        "员工": session.query(SysEmployee).count(),
        "仓库": session.query(BaseWarehouse).count(),
        "往来单位": session.query(BasePartner).count(),
        "商品": session.query(BaseProduct).count(),
        "销售订单": session.query(BizOrder).filter(BizOrder.type == OrderType.SALES).count(),
        "订单明细": session.query(BizOrderItem).count(),
        "库存记录": session.query(InvCurrentStock).count(),
        "财务流水": session.query(FactFinance).count(),
    }
    
    print("\n📊 数据库表记录统计：")
    for table_name, count in stats.items():
        print(f"  {table_name:<12}: {count:>6} 条")
    
    # 查询视图
    print("\n📋 AI 分析视图验证：")
    views = session.execute(text("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'view_bi%'
        ORDER BY table_name
    """)).fetchall()
    
    for view in views:
        print(f"  ✓ {view[0]}")
    
    # 测试视图数据
    print("\n🔍 视图数据测试：")
    
    # 销售分析视图
    sales_count = session.execute(text("SELECT COUNT(*) FROM view_bi_sales_analysis")).scalar()
    print(f"  view_bi_sales_analysis: {sales_count} 条记录")
    
    # 库存预警视图
    stock_count = session.execute(text("SELECT COUNT(*) FROM view_bi_inventory_alert")).scalar()
    print(f"  view_bi_inventory_alert: {stock_count} 条记录")
    
    # 财务监控视图
    finance_count = session.execute(text("SELECT COUNT(*) FROM view_bi_finance_monitor")).scalar()
    print(f"  view_bi_finance_monitor: {finance_count} 条记录")


def main():
    """主函数"""
    print("=" * 70)
    print("进销存 BI 系统 - 数据库初始化与数据填充")
    print("=" * 70)
    
    # 创建数据库引擎
    engine = create_engine(settings.database_url_sync, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 步骤1: 重置与建表
        create_database_tables(engine)
        
        # 步骤2: 创建 AI 视图
        create_ai_views(engine)
        
        # 步骤3: 填充基础维度
        data_dict = populate_dimensions(session)
        
        # 步骤4: 生成核心业务数据
        generate_sales_orders(session, data_dict)
        generate_inventory(session, data_dict)
        generate_finance_records(session, data_dict)
        
        # 步骤5: 打印统计摘要
        print_summary(session)
        
        print("\n" + "=" * 70)
        print("🎉 数据库初始化完成！")
        print("=" * 70)
        print("\n💡 提示：")
        print("  - 可以使用 psql 连接数据库查看数据")
        print("  - 视图已创建，可用于 AI 分析")
        print("  - 业务数据已填充，可以开始测试分析功能")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
