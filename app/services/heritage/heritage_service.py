import json
import time
from werkzeug.datastructures import FileStorage
from flask import current_app, g
from sqlalchemy import not_, or_
from app.models import db
from sqlalchemy.orm import joinedload
from app.models.element_binding import ElementBinding
from app.models.game_record import HeritageGameRecord
from app.models.heritage import Heritage
from app.models.heritage_collect import HeritageCollect
from app.models.heritage_edit import HeritageRequest
from app.models.heritage_history import UserBrowsingHistory
from app.models.heritage_image import HeritageImage
from app.models.heritage_question import HeritageQuestion
from app.models.quiz_record import HeritageQuizRecord
from app.utils.uploader import Uploader

class HeritageService:

    @staticmethod
    def get_heritage_list(page=1, per_page=20, keyword=None, heritage_class=None, 
                          origin=None, enroll_year=None, order_by='new', user_id=None):
        query = Heritage.query

        # --- 筛选逻辑 ---
        if keyword:
            like_pattern = f'%{keyword}%'
            query = query.filter(
                or_(
                    Heritage.heritage_name.like(like_pattern),
                    Heritage.brief_intro.like(like_pattern),
                    Heritage.origin.like(like_pattern),
                    Heritage.enroll_year.like(like_pattern)
                )
            )

        if origin:
            query = query.filter(Heritage.origin.like(f'%{origin}%'))

        if heritage_class:
            query = query.filter(Heritage.heritage_class == heritage_class)
        
        if enroll_year:
            query = query.filter(Heritage.enroll_year.like(f'%{enroll_year}%'))

        # --- 排序逻辑 ---
        sort_map = {
            'view': Heritage.view.desc(),
            'collect': Heritage.collect.desc(),
            'new': Heritage.c_time.desc()
        }
        order_rule = sort_map.get(order_by, Heritage.c_time.desc())
        query = query.order_by(order_rule)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = pagination.items

        # --- 批量标注收藏状态 ---
        if user_id and items:
            item_ids = [item.id for item in items]
            collected_records = HeritageCollect.query.filter(
                HeritageCollect.user_id == user_id,
                HeritageCollect.heritage_id.in_(item_ids)
            ).all()
            collected_set = {c.heritage_id for c in collected_records}
            for item in items:
                item.is_collected = item.id in collected_set
        else:
            for item in items:
                item.is_collected = False

        return {
            'list': items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }

    # ==================== 2. 详情获取 (增加收藏判断) ====================
    @staticmethod
    def get_heritage_detail(h_id, user_id=None):
        heritage = Heritage.query.get(h_id)
        if not heritage:
            return None
        
        if user_id:
            HeritageService._add_browsing_history(user_id, h_id)

        # 标注收藏状态
        heritage.is_collected = False
        if user_id:
            exists = HeritageCollect.query.filter_by(
                user_id=user_id, 
                heritage_id=h_id
            ).first()
            heritage.is_collected = True if exists else False

        # 浏览量自增
        try:
            heritage.view = (heritage.view or 0) + 1
            db.session.commit()
        except Exception:
            db.session.rollback()

        return heritage
    
    # ==================== 3. 通关进度 (核心修改：处理无互动逻辑) ====================
    @staticmethod
    def get_user_completion_status(user_id, heritage_id):
        """
        计算用户的通关状态码。
        逻辑：如果没有互动模块，完成问答即算全通关(3)。
        """
        if not user_id:
            return 0
        
        heritage = Heritage.query.get(heritage_id)
        if not heritage:
            return 0
        
        has_quiz = HeritageQuizRecord.query.filter_by(
            user_id=user_id, heritage_id=heritage_id
        ).first() is not None
        
        has_game = HeritageGameRecord.query.filter_by(
            user_id=user_id, heritage_id=heritage_id
        ).first() is not None

        # 如果该项目【没有】互动模块
        if not heritage.is_interact:
            return 3 if has_quiz else 0
            
        # 如果该项目【有】互动模块
        if has_quiz and has_game: return 3
        if has_game: return 2
        if has_quiz: return 1
        return 0

    # ==================== 6. 其他辅助方法 ====================
    @staticmethod
    def get_user_finished_list(user_id, page=1, per_page=10):
        """获取用户通关列表"""
        query = db.session.query(Heritage, HeritageQuizRecord.finish_time).join(
            HeritageQuizRecord, Heritage.id == HeritageQuizRecord.heritage_id
        ).filter(
            HeritageQuizRecord.user_id == user_id
        ).order_by(HeritageQuizRecord.finish_time.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for h, f_time in pagination.items:
            # 挂载格式化时间
            h.finish_time_display = HeritageQuizRecord.format_timestamp(f_time)
            items.append(h)

        return {
            'list': items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }

    @staticmethod
    def finish_game(user_id, heritage_id):
        """记录小游戏完成"""
        heritage = Heritage.query.get(heritage_id)
        if not heritage or not heritage.is_interact:
            return None
            
        record = HeritageGameRecord.query.filter_by(user_id=user_id, heritage_id=heritage_id).first()
        if not record:
            record = HeritageGameRecord(user_id=user_id, heritage_id=heritage_id, finish_time=int(time.time()))
            db.session.add(record)
            db.session.commit()
        return record
    
    @staticmethod
    def _handle_images(heritage_id, cover_file, detail_files):
        """内部辅助：处理图片保存逻辑"""
        # 处理封面 (Type 1)
        if cover_file:
            # 管理员修改通常是替换，先删除旧封面记录
            HeritageImage.query.filter_by(heritage_id=heritage_id, image_type=1).delete()
            config_c = {"pathFormat": "uploads/h/c/{time}", "maxSize": 2*1024*1024, "allowFiles": [".jpg",".png"], "oriName": cover_file.filename}
            up_c = Uploader(cover_file, config_c, current_app.static_folder)
            if up_c.stateInfo == "SUCCESS":
                db.session.add(HeritageImage(heritage_id=heritage_id, image_url=up_c.fullName.lstrip('/'), image_type=1))

        # 处理详情图 (Type 2)
        if detail_files:
            # 策略：管理员传了新图则全量替换旧详情图
            HeritageImage.query.filter_by(heritage_id=heritage_id, image_type=2).delete()
            for f in detail_files:
                config_d = {"pathFormat": "uploads/h/d/{time}", "maxSize": 2*1024*1024, "allowFiles": [".jpg",".png"], "oriName": f.filename}
                up_d = Uploader(f, config_d, current_app.static_folder)
                if up_d.stateInfo == "SUCCESS":
                    db.session.add(HeritageImage(heritage_id=heritage_id, image_url=up_d.fullName.lstrip('/'), image_type=2))

    @staticmethod
    def admin_direct_manage(admin_id, args):
        """管理员直接管理：数据直接进/改 heritage_info 表"""
        h_id = args.get('heritage_id')
        name = args.get('heritage_name', '').strip()

        # --- 核心修改：动态区分动作名称 ---
        if h_id:
            g.log_action = u"直接修改非遗项目"
        else:
            g.log_action = u"直接新增非遗项目"

        try:
            if h_id:
                # --- 修改逻辑 ---
                heritage = Heritage.query.get(h_id)
                if not heritage: return None, u"修改失败：项目不存在"
                # 检查重名（排除自身）
                if Heritage.query.filter(Heritage.heritage_name == name, Heritage.id != h_id).first():
                    return None, u"修改失败：名称‘{}’已存在".format(name)
                msg = u"项目信息已成功更新"
            else:
                # --- 新增逻辑 ---
                if not name:
                    return None, u"新增失败：非遗名称不能为空"
                if Heritage.query.filter_by(heritage_name=name).first():
                    return None, u"创建失败：该名称已存在"
                
                # 【修复点 1】：不要立刻 add 和 flush
                heritage = Heritage(author_id=admin_id) 
                msg = u"新非遗项目已发布"

            # 【修复点 2】：在 flush 之前，先完成所有字段的赋值
            # 尤其是这些 nullable=False 的字段：heritage_name, spread_region
            fields_to_map = [
                'heritage_name', 'heritage_class', 'origin', 
                'spread_region', 'brief_intro', 'introduction', 
                'enroll_year', 'tags'
            ]
            
            for attr in fields_to_map:
                if args.get(attr) is not None:
                    setattr(heritage, attr, args[attr])
            
            # 自动处理其他固定字段
            heritage.e_time = int(time.time())
            if not h_id:
                # 如果是新增，确保 c_time 也有值
                heritage.c_time = int(time.time())
                # 只有新增时才需要 add
                db.session.add(heritage)

            # 【修复点 3】：现在数据完整了，可以安全地同步到数据库获取 ID
            db.session.flush() 

            # 处理图片（此时 heritage.id 已经有了）
            HeritageService._handle_images(heritage.id, args.get('cover_image'), args.get('detail_images'))

            db.session.commit()
            # 同时把 ID 存入 g (如之前讨论)
            g.target_id = heritage.id
            # 把名字也存入 g，方便日志直接显示，不需要去查参数
            g.target_name = heritage.heritage_name

            return True, msg

        except Exception as e:
            db.session.rollback()
            # 调试建议：如果还是报错，打印出具体的堆栈信息
            import traceback
            traceback.print_exc()
            return None, str(e)
        
    @staticmethod
    def _add_browsing_history(user_id, heritage_id):
        """内部方法：保存浏览记录"""
        # 查找是否已经看过
        history = UserBrowsingHistory.query.filter_by(user_id=user_id, heritage_id=heritage_id).first()
        try:
            if history:
                # 已看过：更新时间戳至最新，使其排在历史最前面
                history.view_time = int(time.time())
            else:
                # 没看过：新建记录
                new_h = UserBrowsingHistory(user_id=user_id, heritage_id=heritage_id)
                db.session.add(new_h)
            db.session.commit()
        except:
            db.session.rollback()

    @staticmethod
    def get_user_browsing_history(user_id, page=1, per_page=10):
        """获取用户浏览足迹列表"""
        # 关联查询非遗信息和历史时间
        query = db.session.query(Heritage, UserBrowsingHistory.view_time).join(
            UserBrowsingHistory, Heritage.id == UserBrowsingHistory.heritage_id
        ).filter(
            UserBrowsingHistory.user_id == user_id
        ).order_by(UserBrowsingHistory.view_time.desc())

        pag = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for h, v_time in pag.items:
            # 动态挂载格式化时间，方便 Fields 渲染
            h.history_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v_time))
            items.append(h)

        return {
            'list': items,
            'total': pag.total,
            'page': pag.page,
            'pages': pag.pages
        }
    
    @staticmethod
    def get_unbound_list(keyword=None):
        """
        获取所有尚未绑定到地图板块的非遗项目
        """
        # 1. 查询所有已被绑定的非遗 ID 集合 (子查询)
        # 过滤掉 None 值，确保查询准确
        bound_ids_query = db.session.query(ElementBinding.heritage_id).filter(
            ElementBinding.heritage_id.isnot(None)
        )

        # 2. 在 Heritage 表中过滤出 ID 不在上述集合中的记录
        query = Heritage.query.filter(not_(Heritage.id.in_(bound_ids_query)))

        # 3. 如果有关键词搜索
        if keyword:
            query = query.filter(Heritage.heritage_name.like(f'%{keyword}%'))

        return query.all()
    
    @staticmethod
    def delete_heritage(h_id):
        """管理员：删除已上线的非遗项目"""
        # 1. 查找目标
        heritage = Heritage.query.get(h_id)
        if not heritage:
            return False, u"操作失败：未找到该非遗项目"

        try:
            # --- 【日志记录点】在删除前提取信息 ---
            g.target_id = h_id
            g.target_name = heritage.heritage_name
            g.log_action = u"删除非遗"
            # ------------------------------------

            # 2. 处理关联依赖（手动清理或置空）
            # A. 地图板块解绑 (将 heritage_id 置为 NULL)
            ElementBinding.query.filter_by(heritage_id=h_id).update({ElementBinding.heritage_id: None})
            
            # B. 题目清理 (如果业务要求非遗删了题目也要删，则执行删除)
            HeritageQuestion.query.filter_by(heritage_id=h_id).delete()

            # 3. 执行删除主表 (会触发 HeritageImage 的级联删除)
            db.session.delete(heritage)
            db.session.commit()
            
            return True, u"非遗项目及其关联数据已成功删除"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
