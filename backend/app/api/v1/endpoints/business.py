"""
进销存业务操作接口
"""
from datetime import datetime, date
from typing import Annotated
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_active_user
from app.db.session import get_db
from app.models.bi_schema import (
    SysUser,
    BaseProduct,
    BaseWarehouse,
    BasePartner,
    SysEmployee,
    BizOrder,
    BizOrderItem,
    InvCurrentStock,
    FactFinance,
    OrderType,
    OrderStatus,
    FinanceRecordType,
    PartnerType
)
from app.schemas.business import (
    ProductCreate,
    ProductResponse,
    InboundRequest,
    OutboundRequest,
    BusinessOperationResponse,
    OrderResponse
)

router = APIRouter()


def generate_order_no(order_type: OrderType) -> str:
    """生成订单编号"""
    prefix = "PO" if order_type == OrderType.PURCHASE else "SO"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}{timestamp}"


@router.post("/products", response_model=ProductResponse, summary="创建商品")
async def create_product(
    product_data: ProductCreate,
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    创建商品
    
    - **name**: 商品名称
    - **category**: 商品分类
    - **cost_price**: 成本价
    - **min_stock**: 最低库存预警线
    """
    # 创建商品
    new_product = BaseProduct(
        name=product_data.name,
        category=product_data.category,
        specification=product_data.specification,
        unit=product_data.unit,
        cost_price=product_data.cost_price,
        min_stock=product_data.min_stock,
        is_active=True
    )
    
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    return new_product


@router.post("/inbound", response_model=BusinessOperationResponse, summary="采购入库")
async def create_inbound_order(
    request: InboundRequest,
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    采购入库操作（事务处理）
    
    1. 创建采购订单
    2. 增加库存
    3. 记录应付账款
    
    - **supplier_id**: 供应商ID
    - **warehouse_id**: 仓库ID
    - **salesman_id**: 业务员ID
    - **items**: 商品明细列表
    """
    try:
        # 验证供应商
        result = await db.execute(
            select(BasePartner).where(
                BasePartner.id == request.supplier_id,
                BasePartner.type == PartnerType.SUPPLIER
            )
        )
        supplier = result.scalar_one_or_none()
        if not supplier:
            raise HTTPException(status_code=404, detail="供应商不存在")
        
        # 验证仓库
        result = await db.execute(select(BaseWarehouse).where(BaseWarehouse.id == request.warehouse_id))
        warehouse = result.scalar_one_or_none()
        if not warehouse:
            raise HTTPException(status_code=404, detail="仓库不存在")
        
        # 验证业务员
        result = await db.execute(select(SysEmployee).where(SysEmployee.id == request.salesman_id))
        salesman = result.scalar_one_or_none()
        if not salesman:
            raise HTTPException(status_code=404, detail="业务员不存在")
        
        # 计算订单总金额
        total_amount = Decimal(0)
        for item in request.items:
            subtotal = item.quantity * item.price
            total_amount += subtotal
        
        # 1. 创建采购订单
        order = BizOrder(
            order_no=generate_order_no(OrderType.PURCHASE),
            type=OrderType.PURCHASE,
            order_date=date.today(),
            status=OrderStatus.CONFIRMED,
            salesman_id=request.salesman_id,
            partner_id=request.supplier_id,
            warehouse_id=request.warehouse_id,
            total_amount=total_amount,
            remark=request.remark
        )
        db.add(order)
        await db.flush()  # 获取订单ID
        
        # 2. 创建订单明细并更新库存
        for item_data in request.items:
            # 验证商品
            result = await db.execute(select(BaseProduct).where(BaseProduct.id == item_data.product_id))
            product = result.scalar_one_or_none()
            if not product:
                raise HTTPException(status_code=404, detail=f"商品ID {item_data.product_id} 不存在")
            
            # 创建订单明细
            subtotal = item_data.quantity * item_data.price
            order_item = BizOrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=item_data.price,
                subtotal=subtotal
            )
            db.add(order_item)
            
            # 增加库存
            result = await db.execute(
                select(InvCurrentStock).where(
                    InvCurrentStock.warehouse_id == request.warehouse_id,
                    InvCurrentStock.product_id == item_data.product_id
                )
            )
            stock = result.scalar_one_or_none()
            
            if stock:
                stock.quantity += item_data.quantity
            else:
                stock = InvCurrentStock(
                    warehouse_id=request.warehouse_id,
                    product_id=item_data.product_id,
                    quantity=item_data.quantity
                )
                db.add(stock)
        
        # 3. 记录应付账款
        finance_record = FactFinance(
            type=FinanceRecordType.PAYABLE,
            trans_date=date.today(),
            amount=total_amount,
            balance=total_amount,
            partner_id=request.supplier_id,
            dept_id=salesman.dept_id,
            salesman_id=request.salesman_id,
            description=f"采购入库 - 订单号: {order.order_no}"
        )
        db.add(finance_record)
        
        # 提交事务
        await db.commit()
        await db.refresh(order)
        
        # 加载关联数据
        result = await db.execute(
            select(BizOrder).where(BizOrder.id == order.id)
        )
        order_with_items = result.scalar_one()
        
        return BusinessOperationResponse(
            success=True,
            message=f"采购入库成功，订单号: {order.order_no}",
            order=OrderResponse(
                id=order_with_items.id,
                order_no=order_with_items.order_no,
                type=order_with_items.type.value,
                order_date=order_with_items.order_date,
                status=order_with_items.status.value,
                salesman_id=order_with_items.salesman_id,
                partner_id=order_with_items.partner_id,
                warehouse_id=order_with_items.warehouse_id,
                total_amount=order_with_items.total_amount,
                remark=order_with_items.remark,
                created_at=order_with_items.created_at,
                items=[]
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"入库操作失败: {str(e)}"
        )


@router.post("/outbound", response_model=BusinessOperationResponse, summary="销售出库")
async def create_outbound_order(
    request: OutboundRequest,
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    销售出库操作（事务处理）
    
    1. 检查库存
    2. 创建销售订单
    3. 扣减库存
    4. 记录应收账款
    
    - **customer_id**: 客户ID
    - **warehouse_id**: 仓库ID
    - **salesman_id**: 业务员ID
    - **items**: 商品明细列表
    """
    try:
        # 验证客户
        result = await db.execute(
            select(BasePartner).where(
                BasePartner.id == request.customer_id,
                BasePartner.type == PartnerType.CUSTOMER
            )
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="客户不存在")
        
        # 验证仓库
        result = await db.execute(select(BaseWarehouse).where(BaseWarehouse.id == request.warehouse_id))
        warehouse = result.scalar_one_or_none()
        if not warehouse:
            raise HTTPException(status_code=404, detail="仓库不存在")
        
        # 验证业务员
        result = await db.execute(select(SysEmployee).where(SysEmployee.id == request.salesman_id))
        salesman = result.scalar_one_or_none()
        if not salesman:
            raise HTTPException(status_code=404, detail="业务员不存在")
        
        # 1. 检查库存
        for item_data in request.items:
            result = await db.execute(
                select(InvCurrentStock).where(
                    InvCurrentStock.warehouse_id == request.warehouse_id,
                    InvCurrentStock.product_id == item_data.product_id
                )
            )
            stock = result.scalar_one_or_none()
            
            if not stock or stock.quantity < item_data.quantity:
                result = await db.execute(select(BaseProduct).where(BaseProduct.id == item_data.product_id))
                product = result.scalar_one_or_none()
                product_name = product.name if product else f"ID:{item_data.product_id}"
                raise HTTPException(
                    status_code=400,
                    detail=f"商品 {product_name} 库存不足，当前库存: {stock.quantity if stock else 0}"
                )
        
        # 计算订单总金额
        total_amount = Decimal(0)
        for item in request.items:
            subtotal = item.quantity * item.price
            total_amount += subtotal
        
        # 2. 创建销售订单
        order = BizOrder(
            order_no=generate_order_no(OrderType.SALES),
            type=OrderType.SALES,
            order_date=date.today(),
            status=OrderStatus.CONFIRMED,
            salesman_id=request.salesman_id,
            partner_id=request.customer_id,
            warehouse_id=request.warehouse_id,
            total_amount=total_amount,
            remark=request.remark
        )
        db.add(order)
        await db.flush()
        
        # 3. 创建订单明细并扣减库存
        for item_data in request.items:
            # 创建订单明细
            subtotal = item_data.quantity * item_data.price
            order_item = BizOrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=item_data.price,
                subtotal=subtotal
            )
            db.add(order_item)
            
            # 扣减库存
            result = await db.execute(
                select(InvCurrentStock).where(
                    InvCurrentStock.warehouse_id == request.warehouse_id,
                    InvCurrentStock.product_id == item_data.product_id
                )
            )
            stock = result.scalar_one()
            stock.quantity -= item_data.quantity
        
        # 4. 记录应收账款
        finance_record = FactFinance(
            type=FinanceRecordType.RECEIVABLE,
            trans_date=date.today(),
            amount=total_amount,
            balance=total_amount,
            partner_id=request.customer_id,
            dept_id=salesman.dept_id,
            salesman_id=request.salesman_id,
            description=f"销售出库 - 订单号: {order.order_no}"
        )
        db.add(finance_record)
        
        # 提交事务
        await db.commit()
        await db.refresh(order)
        
        return BusinessOperationResponse(
            success=True,
            message=f"销售出库成功，订单号: {order.order_no}",
            order=OrderResponse(
                id=order.id,
                order_no=order.order_no,
                type=order.type.value,
                order_date=order.order_date,
                status=order.status.value,
                salesman_id=order.salesman_id,
                partner_id=order.partner_id,
                warehouse_id=order.warehouse_id,
                total_amount=order.total_amount,
                remark=order.remark,
                created_at=order.created_at,
                items=[]
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"出库操作失败: {str(e)}"
        )


@router.get("/products", response_model=list, summary="获取商品列表")
async def get_products(
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有激活状态的商品列表
    """
    try:
        result = await db.execute(
            select(BaseProduct)
            .where(BaseProduct.is_active == True)
            .order_by(BaseProduct.category, BaseProduct.name)
        )
        products = result.scalars().all()
        
        return [
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "specification": product.specification,
                "unit": product.unit,
                "cost_price": float(product.cost_price),
                "min_stock": float(product.min_stock) if product.min_stock else None,
                "is_active": product.is_active
            }
            for product in products
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取商品列表失败: {str(e)}"
        )


@router.get("/warehouses", response_model=list, summary="获取仓库列表")
async def get_warehouses(
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有激活状态的仓库列表
    """
    try:
        result = await db.execute(
            select(BaseWarehouse)
            .where(BaseWarehouse.is_active == True)
            .order_by(BaseWarehouse.name)
        )
        warehouses = result.scalars().all()
        
        return [
            {
                "id": warehouse.id,
                "name": warehouse.name,
                "address": warehouse.location,  # 注意：模型字段是 location
                "is_active": warehouse.is_active
            }
            for warehouse in warehouses
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仓库列表失败: {str(e)}"
        )


@router.get("/partners", response_model=list, summary="获取合作伙伴列表")
async def get_partners(
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    type: str = None
):
    """
    获取合作伙伴列表
    
    - **type**: 可选，筛选类型 (customer/supplier)
    """
    try:
        query = select(BasePartner)  # BasePartner 模型没有 is_active 字段
        
        if type:
            if type.lower() == 'customer':
                query = query.where(BasePartner.type == PartnerType.CUSTOMER)
            elif type.lower() == 'supplier':
                query = query.where(BasePartner.type == PartnerType.SUPPLIER)
        
        query = query.order_by(BasePartner.name)
        result = await db.execute(query)
        partners = result.scalars().all()
        
        return [
            {
                "id": partner.id,
                "name": partner.name,
                "type": partner.type.value,
                "region": partner.region,
                "is_active": True  # 模型没有此字段，默认返回 True
            }
            for partner in partners
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取合作伙伴列表失败: {str(e)}"
        )


@router.get("/salesmen", response_model=list, summary="获取业务员列表")
async def get_salesmen(
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有激活状态的业务员列表
    """
    try:
        result = await db.execute(
            select(SysEmployee)
            .where(SysEmployee.is_active == True)
            .order_by(SysEmployee.name)
        )
        salesmen = result.scalars().all()
        
        return [
            {
                "id": salesman.id,
                "name": salesman.name,
                "dept_id": salesman.dept_id,
                "is_active": salesman.is_active
            }
            for salesman in salesmen
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取业务员列表失败: {str(e)}"
        )


@router.post("/parse-command", summary="AI 解析自然语言指令")
async def parse_command(
    current_user: Annotated[SysUser, Depends(get_current_active_user)],
    command: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    使用 AI 解析自然语言业务指令
    
    输入示例：
    {
        "command": "从总仓发货 50 个 iPhone 给京东"
    }
    
    输出示例：
    {
        "operation_type": "outbound",
        "items": [{"product_id": 1, "quantity": 50, "price": 5999}],
        "warehouse_id": 1,
        "partner_id": 5,
        "salesman_id": 1,
        "confidence": 0.85,
        "explanation": "检测到销售出库操作，商品：iPhone，数量：50，仓库：总仓，客户：京东"
    }
    """
    try:
        command_text = command.get("command", "")
        if not command_text:
            raise HTTPException(status_code=400, detail="指令不能为空")
        
        # TODO: 集成真实的 AI 模型进行自然语言处理
        # 当前使用简单的规则匹配作为示例
        
        command_lower = command_text.lower()
        
        # 判断操作类型
        operation_type = "outbound"
        if any(keyword in command_lower for keyword in ["采购", "入库", "进货"]):
            operation_type = "inbound"
        elif any(keyword in command_lower for keyword in ["销售", "出库", "发货"]):
            operation_type = "outbound"
        
        # 提取数量
        import re
        quantity_match = re.search(r'(\d+)\s*(个|台|部|件)', command_text)
        quantity = int(quantity_match.group(1)) if quantity_match else 1
        
        # 模拟返回结果（实际应根据 AI 解析结果返回）
        # 这里需要查询数据库匹配商品、仓库、合作伙伴等
        
        # 获取默认数据（示例）
        product_result = await db.execute(
            select(BaseProduct)
            .where(BaseProduct.is_active == True)
            .limit(1)
        )
        product = product_result.scalar_one_or_none()
        
        warehouse_result = await db.execute(
            select(BaseWarehouse)
            .where(BaseWarehouse.is_active == True)
            .limit(1)
        )
        warehouse = warehouse_result.scalar_one_or_none()
        
        partner_type = PartnerType.CUSTOMER if operation_type == "outbound" else PartnerType.SUPPLIER
        partner_result = await db.execute(
            select(BasePartner)
            .where(BasePartner.type == partner_type)  # BasePartner 没有 is_active 字段
            .limit(1)
        )
        partner = partner_result.scalar_one_or_none()
        
        salesman_result = await db.execute(
            select(SysEmployee)
            .where(SysEmployee.is_active == True)
            .limit(1)
        )
        salesman = salesman_result.scalar_one_or_none()
        
        if not all([product, warehouse, partner, salesman]):
            raise HTTPException(
                status_code=400,
                detail="系统数据不完整，请先添加商品、仓库、合作伙伴和业务员数据"
            )
        
        return {
            "operation_type": operation_type,
            "items": [
                {
                    "product_id": product.id,
                    "quantity": quantity,
                    "price": float(product.cost_price * Decimal('1.2'))  # 示例：成本价 * 1.2
                }
            ],
            "warehouse_id": warehouse.id,
            "partner_id": partner.id,
            "salesman_id": salesman.id,
            "confidence": 0.75,  # 示例置信度
            "explanation": f"检测到{'\u9500\u552e\u51fa\u5e93' if operation_type == 'outbound' else '\u91c7\u8d2d\u5165\u5e93'}操作，商品：{product.name}，数量：{quantity}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 解析失败: {str(e)}"
        )
