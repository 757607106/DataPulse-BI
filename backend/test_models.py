"""
测试数据库模型和视图
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.bi_schema import (
    SysDepartment, SysEmployee, BasePartner, BaseWarehouse, BaseProduct,
    BizOrder, BizOrderItem, FactFinance, InvCurrentStock
)

def test_models():
    """测试模型导入和查询"""
    print("=" * 60)
    print("进销存 BI 系统 - 数据库模型测试")
    print("=" * 60)
    
    # 创建数据库会话
    engine = create_engine(settings.database_url_sync, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. 测试查询部门
        print("\n📊 测试查询 1: 查询所有部门")
        depts = session.query(SysDepartment).all()
        for dept in depts:
            print(f"  - {dept.company_name} / {dept.name}")
        
        # 2. 测试查询员工
        print("\n👥 测试查询 2: 查询所有员工")
        employees = session.query(SysEmployee).all()
        for emp in employees:
            print(f"  - {emp.name} ({emp.department.name})")
        
        # 3. 测试查询商品
        print("\n📦 测试查询 3: 查询所有商品")
        products = session.query(BaseProduct).all()
        for prod in products:
            print(f"  - {prod.name} [{prod.category}] 成本: ¥{prod.cost_price}")
        
        # 4. 测试查询往来单位
        print("\n🏢 测试查询 4: 查询所有往来单位")
        partners = session.query(BasePartner).all()
        for partner in partners:
            print(f"  - {partner.name} ({partner.type.value}) - {partner.region}")
        
        # 5. 测试视图查询
        print("\n📈 测试查询 5: 查询销售分析视图（前5条）")
        result = session.execute(text("""
            SELECT salesman_name, product_name, sales_amount, gross_profit
            FROM view_bi_sales_analysis
            LIMIT 5
        """))
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"  - 业务员: {row[0]}, 商品: {row[1]}, 销售额: ¥{row[2]}, 毛利: ¥{row[3]}")
        else:
            print("  暂无销售数据（需要创建订单数据）")
        
        # 6. 测试视图列表
        print("\n📋 测试查询 6: 验证所有 AI 分析视图")
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'view_bi%'
            ORDER BY table_name
        """))
        views = result.fetchall()
        for view in views:
            print(f"  ✓ {view[0]}")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！数据库模型工作正常！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    test_models()
