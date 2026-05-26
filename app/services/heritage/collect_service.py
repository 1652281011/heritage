# -*- coding: utf-8 -*-
import time
from app.models.base import db
from app.models.heritage_collect import HeritageCollect
from app.models.heritage import Heritage
from app.models.users import User # 假设你之前的非遗模型类名为 Heritage

class HeritageCollectService:
    @staticmethod
    def toggle_collect(user_id, heritage_id):
        """
        切换收藏状态：已收藏则取消，未收藏则添加
        """
        collect_record = HeritageCollect.query.filter_by(
            user_id=user_id, 
            heritage_id=heritage_id
        ).first()

        heritage = Heritage.query.get(heritage_id)
        if not heritage:
            return None, "非遗项目不存在"

        try:
            if collect_record:
                # 1. 取消收藏
                db.session.delete(collect_record)
                # 同步减少非遗表的收藏数
                if heritage.collect > 0:
                    heritage.collect -= 1
                status = False
                msg = "已取消收藏"
            else:
                # 2. 添加收藏
                new_collect = HeritageCollect(user_id=user_id, heritage_id=heritage_id)
                db.session.add(new_collect)
                # 同步增加非遗表的收藏数
                heritage.collect += 1
                status = True
                msg = "收藏成功"
            
            db.session.commit()
            return status, msg
        except Exception as e:
            db.session.rollback()
            return None, f"操作失败: {str(e)}"

    @staticmethod
    def get_user_collect_list(target_user_id, viewer, page=1, per_page=10):
        """
        获取用户收藏列表
        :param target_user_id: 想要查看谁的列表
        :param viewer: 访问者对象 (g.user，游客则为 None)
        """
        # 1. 基础检查
        target_user = User.query.get(target_user_id)
        if not target_user:
            return None, u"目标用户不存在"

        # 2. 权限三级过滤逻辑
        is_public = (target_user.is_public_collect == 1) # 数据库 tinyint(1)
        is_owner = (viewer and viewer.id == target_user_id)
        is_admin = (viewer and str(viewer.role_type) == '3')

        # 拦截判定：如果不公开 且 (既不是本人也不是管理员) -> 拦截
        if not is_public:
            if not (is_owner or is_admin):
                return None, u"该用户设置了收藏列表不公开"

        # 3. 联合查询
        # 这里关联了非遗基本信息和收藏记录表中的时间
        query = db.session.query(Heritage, HeritageCollect.c_time).join(
            HeritageCollect, Heritage.id == HeritageCollect.heritage_id
        ).filter(
            HeritageCollect.user_id == target_user_id
        ).order_by(
            HeritageCollect.c_time.desc()
        )

        # 4. 执行分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 5. 数据组装
        items = []
        for h, c_time in pagination.items:
            # 动态挂载属性供 Fields 序列化
            h.collect_time_display = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(c_time))
            h.is_collected = True 
            items.append(h)

        return {
            'list': items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }, u"获取成功"