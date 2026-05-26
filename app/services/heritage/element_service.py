from flask import g
from app.models.element_binding import ElementBinding
from app.models import db
from app.models.heritage import Heritage


class ElementService:
    @staticmethod
    def get_element_list(user_role):
        """
        获取板块列表
        :param user_role: 用户角色类型 ("3" 为管理员)
        """
        query = ElementBinding.query
        
        # 权限逻辑：如果不是管理员 (role_type != "3")，则只返回已激活的数据
        if str(user_role) != "3":
            query = query.filter(ElementBinding.is_active == True)
        
        # 管理员可以获取全部数据（包括 is_active 为 False 的）
        return query.all()
    
    @staticmethod
    def add_element(bind_element_id, is_active=True):
        """
        管理员新增地图板块
        :return: (bool, data_or_msg)
        """
        # 1. 检查标识符是否已存在（避免数据库 Unique 约束报错）
        existing = ElementBinding.query.filter_by(bind_element_id=bind_element_id).first()
        if existing:
            return False, u"该板块标识符已存在，请勿重复添加"

        # 2. 创建新记录（此时 heritage_id 默认为空）
        try:
            new_element = ElementBinding(
                bind_element_id=bind_element_id,
                is_active=bool(is_active)
            )
            db.session.add(new_element)
            db.session.commit()

            g.target_id = bind_element_id
            g.target_name = f"新板块:{bind_element_id}"
            return True, new_element
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    @staticmethod
    def update_binding(bind_id, heritage_id=None, is_active=None):
        """
        管理员修改板块绑定关系
        :param bind_id: 板块标识符
        :param heritage_id: 关联的非遗ID
        :param is_active: 是否激活状态
        """
        # 1. 查找板块是否存在
        element = ElementBinding.query.filter_by(bind_element_id=bind_id).first()
        if not element:
            return False, u"未找到该板块标识，请先添加板块"

        # 2. 如果提供了 heritage_id，校验该非遗是否存在
        if heritage_id:
            h_exists = Heritage.query.get(heritage_id)
            if not h_exists:
                return False, u"指定的非遗项目不存在，无法绑定"
            element.heritage_id = heritage_id
            h_name = h_exists.heritage_name
        elif heritage_id == 0: 
            # 约定传 0 为解绑
            element.heritage_id = None

        # 3. 如果提供了激活状态，进行修改
        if is_active is not None:
            element.is_active = bool(is_active)

        try:
            db.session.commit()

            # --- 为日志装饰器赋值 ---
            g.target_id = bind_id
            # 记录更详细的名称信息：板块ID + 绑定的非遗名
            g.target_name = f"板块:{bind_id} -> 绑定:{h_name}"
            return True, element
        except Exception as e:
            db.session.rollback()
            return False, str(e)