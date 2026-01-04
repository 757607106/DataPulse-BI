"""
数据库初始化工具
用于创建表结构和初始化视图
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from app.models.bi_schema import Base
from app.core.config import settings  # 假设你的配置在这里


def init_database(drop_existing: bool = False):
    """
    初始化数据库
    
    Args:
        drop_existing: 是否删除现有表（谨慎使用！）
    """
    # 创建数据库引擎（使用同步连接）
    engine = create_engine(
        settings.database_url_sync,
        echo=True  # 打印 SQL 语句，便于调试
    )
    
    # 1. 创建所有表
    if drop_existing:
        print("⚠️  删除现有表...")
        Base.metadata.drop_all(bind=engine)
    
    print("📦 创建表结构...")
    Base.metadata.create_all(bind=engine)
    print("✅ 表结构创建完成！")
    
    # 2. 执行视图创建 SQL
    print("\n📊 创建 AI 分析视图...")
    views_sql_path = Path(__file__).parent / "init_views.sql"
    
    if views_sql_path.exists():
        with open(views_sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 使用 session 执行 SQL
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 分割并执行每个 CREATE VIEW 语句
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            for statement in statements:
                if statement.startswith('CREATE') or statement.startswith('--'):
                    if statement.startswith('CREATE'):
                        session.execute(text(statement))
                        session.commit()
                        
                        # 提取视图名称
                        view_name = statement.split('VIEW')[1].split('AS')[0].strip()
                        print(f"  ✓ 创建视图: {view_name}")
            
            print("✅ AI 分析视图创建完成！")
            
        except Exception as e:
            session.rollback()
            print(f"❌ 视图创建失败: {e}")
            raise
        finally:
            session.close()
    else:
        print(f"⚠️  未找到视图 SQL 文件: {views_sql_path}")
    
    print("\n🎉 数据库初始化完成！")


def init_sample_data():
    """
    初始化示例数据（可选）
    """
    from decimal import Decimal
    from datetime import datetime, date
    
    engine = create_engine(settings.database_url_sync)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        from app.models.bi_schema import (
            SysDepartment, SysEmployee, BasePartner, BaseWarehouse, BaseProduct
        )
        
        print("📝 创建示例数据...")
        
        # 创建分公司和部门
        company_beijing = SysDepartment(
            name="销售部",
            company_name="北京分公司"
        )
        company_shanghai = SysDepartment(
            name="销售部",
            company_name="上海分公司"
        )
        session.add_all([company_beijing, company_shanghai])
        session.commit()
        
        # 创建员工
        emp1 = SysEmployee(
            name="张三",
            dept_id=company_beijing.id,
            email="zhangsan@example.com"
        )
        emp2 = SysEmployee(
            name="李四",
            dept_id=company_shanghai.id,
            email="lisi@example.com"
        )
        session.add_all([emp1, emp2])
        session.commit()
        
        # 创建往来单位
        customer1 = BasePartner(
            name="华东电子有限公司",
            type="customer",
            region="华东",
            contact_person="王经理"
        )
        supplier1 = BasePartner(
            name="深圳供应链公司",
            type="supplier",
            region="华南",
            contact_person="刘经理"
        )
        session.add_all([customer1, supplier1])
        session.commit()
        
        # 创建仓库
        warehouse1 = BaseWarehouse(
            name="北京总仓",
            location="北京市朝阳区"
        )
        warehouse2 = BaseWarehouse(
            name="上海分仓",
            location="上海市浦东新区"
        )
        session.add_all([warehouse1, warehouse2])
        session.commit()
        
        # 创建商品
        product1 = BaseProduct(
            name="笔记本电脑",
            category="电子产品",
            cost_price=Decimal("3000.00"),
            min_stock=Decimal("10")
        )
        product2 = BaseProduct(
            name="办公椅",
            category="办公用品",
            cost_price=Decimal("500.00"),
            min_stock=Decimal("20")
        )
        session.add_all([product1, product2])
        session.commit()
        
        print("✅ 示例数据创建完成！")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 示例数据创建失败: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("进销存 BI 系统 - 数据库初始化工具")
    print("=" * 60)
    
    # 解析命令行参数
    drop_existing = "--drop" in sys.argv
    with_sample = "--sample" in sys.argv
    
    if drop_existing:
        confirm = input("⚠️  确认要删除现有数据库？(yes/no): ")
        if confirm.lower() != "yes":
            print("❌ 取消操作")
            sys.exit(0)
    
    # 初始化数据库
    init_database(drop_existing=drop_existing)
    
    # 初始化示例数据
    if with_sample:
        init_sample_data()
    
    print("\n" + "=" * 60)
    print("使用说明:")
    print("  python init_db.py          # 仅创建表和视图")
    print("  python init_db.py --sample # 创建表、视图和示例数据")
    print("  python init_db.py --drop   # 删除现有表后重新创建")
    print("=" * 60)
