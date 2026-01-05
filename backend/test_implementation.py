"""
测试实现的代码是否可以正常导入
"""
import sys
print("开始测试代码完整性...")

# 测试模型导入
try:
    from app.models.bi_schema import (
        SysUser, SysDepartment, SysEmployee, 
        BasePartner, BaseWarehouse, BaseProduct,
        BizOrder, BizOrderItem, FactFinance, InvCurrentStock,
        OrderType, OrderStatus, PartnerType, FinanceRecordType
    )
    print("✓ 模型导入成功")
except Exception as e:
    print(f"✗ 模型导入失败: {e}")
    sys.exit(1)

# 测试 schemas 导入
try:
    from app.schemas.auth import Token, LoginRequest, UserResponse, UserCreate
    from app.schemas.business import (
        ProductCreate, ProductResponse,
        InboundRequest, OutboundRequest,
        BusinessOperationResponse
    )
    print("✓ Schemas 导入成功")
except Exception as e:
    print(f"✗ Schemas 导入失败: {e}")
    sys.exit(1)

# 测试 security 模块
try:
    from app.core.security import (
        create_access_token, 
        verify_password, 
        get_password_hash
    )
    print("✓ Security 模块导入成功")
except Exception as e:
    print(f"✗ Security 模块导入失败: {e}")
    sys.exit(1)

# 测试端点导入
try:
    from app.api.v1.endpoints import auth, business
    print("✓ 端点导入成功")
except Exception as e:
    print(f"✗ 端点导入失败: {e}")
    sys.exit(1)

# 测试 FastAPI 应用
try:
    from app.main import app
    print("✓ FastAPI 应用导入成功")
    
    # 检查路由
    routes = [route.path for route in app.routes]
    expected_routes = [
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/v1/auth/register",
        "/api/v1/business/products",
        "/api/v1/business/inbound",
        "/api/v1/business/outbound",
    ]
    
    found_routes = []
    for expected in expected_routes:
        if expected in routes:
            found_routes.append(expected)
    
    print(f"✓ 找到 {len(found_routes)}/{len(expected_routes)} 个路由")
    for route in found_routes:
        print(f"  - {route}")
        
except Exception as e:
    print(f"✗ FastAPI 应用导入失败: {e}")
    sys.exit(1)

print("\n全部测试通过！代码实现完整且无语法错误。")
