# -*- coding: utf-8 -*-
import os
import time
from flask import current_app
from sqlalchemy import or_
from app.models.achievements import Achievement, UserAchievement, UserStat
from app.models.base import db
from app.models.game_record import HeritageGameRecord
from app.models.heritage import Heritage
from app.models.heritage_interaction import HeritageInteraction
from app.models.interactive_history import UserGameHistory
from app.models.users import User
from app.services.achievements.achievement_service import AchievementService
from app.services.heritage.complete_service import CompletionService
from app.utils.uploader import Uploader

class GameService:
    @staticmethod
    def record_interaction_file(user_id, args):
        it_id = args.get('interaction_id')
        inter_config = HeritageInteraction.query.get(it_id)
        
        if not inter_config or inter_config.status != 1:
            return None, u"互动项目不存在或已下架"

        try:
            # --- 1. 记录历史足迹 (无论胜负，进入接口即记) ---
            GameService._record_play_history_logic(user_id, inter_config.id, inter_config.heritage_id)
            from app.services.heritage.heritage_service import HeritageService
            HeritageService._add_browsing_history(user_id, inter_config.heritage_id)
            db.session.commit()

            # --- 2. 预处理作品文件及判定类型 ---
            # 放在“胜负判断”之前，确保失败也能进入处理流程
            local_path = None
            file_type_val = None
            final_work_name = None
            
            file_obj = args.get('work_file')
            passed_status = args.get('passed') == 'true'

            # 如果上传了文件，无论是否通过挑战，都进行保存
            if file_obj and hasattr(file_obj, 'filename') and file_obj.filename:
                ext = file_obj.filename.rsplit('.', 1)[-1].lower()
                if ext in ['mp3', 'wav', 'm4a']: 
                    file_type_val, sub = 2, 'audios'
                elif ext in ['mp4', 'mov', 'avi']: 
                    file_type_val, sub = 3, 'videos'
                else: 
                    file_type_val, sub = 1, 'images'

                config = {
                    "pathFormat": f"uploads/user_works/{sub}/{{time}}{{rand:6}}",
                    "maxSize": 20 * 1024 * 1024,
                    "allowFiles": [".png", ".jpg", ".jpeg", ".mp3", ".wav", ".mp4", ".mov"],
                    "oriName": file_obj.filename
                }
                up = Uploader(file_obj, config, current_app.static_folder)
                
                if up.stateInfo == "SUCCESS":
                    local_path = up.fullName.lstrip('/')
                    user_given_name = (args.get('work_name') or '').strip()
                    default_name = f"我的{inter_config.heritage_title}{inter_config.name}作品"
                    final_work_name = user_given_name if user_given_name else default_name

            # --- 3. 决定是否创建记录 ---
            # 逻辑：如果(通过了挑战) 或者 (没通过但上传了作品)，则需要存入数据库
            if not passed_status and not local_path:
                return {
                    "record": None, "new_medals": [],
                    "completion_status": CompletionService.get_single_status(user_id, inter_config.heritage_id)
                }, u"挑战未通过，且未上传作品"

            # --- 4. 数据库持久化 ---
            new_medals = []
            is_first_play = HeritageGameRecord.query.filter_by(
                user_id=user_id, interaction_id=it_id
            ).count() == 0

            record = HeritageGameRecord(
                user_id=user_id,
                interaction_id=it_id,
                heritage_id=inter_config.heritage_id,
                work_name=final_work_name,
                work_path=local_path,
                file_type=file_type_val,
                finish_time=int(time.time())
            )
            db.session.add(record)
            db.session.flush()

            # --- 5. 触发成就 (仅在通过挑战时) ---
            if passed_status:
                if is_first_play:
                    new_medals.extend(AchievementService.trigger_event(user_id, 'game', inter_config.heritage_id))
                
                if local_path:
                    new_medals.extend(AchievementService.trigger_event(user_id, 'work'))

            db.session.commit()

            # --- 6. 同步进度状态 ---
            current_status = CompletionService.get_single_status(user_id, inter_config.heritage_id)

            msg = u"记录成功" if passed_status else u"挑战未通过，但作品已保存"
            return {
                "record": record,
                "new_medals": new_medals,
                "completion_status": current_status
            }, msg

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Record Interaction Error: {str(e)}")
            return None, f"数据同步失败: {str(e)}"
        
    @staticmethod
    def _record_play_history_logic(user_id, it_id, h_id):
        if not user_id: return
        history = UserGameHistory.query.filter_by(user_id=user_id, interaction_id=it_id).first()
        if history:
            history.last_play_time = int(time.time())
        else:
            new_play = UserGameHistory(user_id=user_id, interaction_id=it_id, heritage_id=h_id)
            db.session.add(new_play)

    @staticmethod
    def get_user_recent_games(user_id, page=1, per_page=10):
        query = db.session.query(HeritageInteraction, UserGameHistory.last_play_time).join(
            UserGameHistory, HeritageInteraction.id == UserGameHistory.interaction_id
        ).filter(
            UserGameHistory.user_id == user_id
        ).order_by(UserGameHistory.last_play_time.desc())

        pag = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for inter, p_time in pag.items:
            inter.recent_play_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(p_time))
            items.append(inter)
        return {'list': items, 'total': pag.total, 'page': pag.page}

    @staticmethod # 确保有这个装饰器
    def get_user_works_advanced(target_user_id, viewer, args):
        """
        高级搜索作品集（带隐私校验）
        :param target_user_id: 想要查看谁的作品
        :param viewer: 当前访问者对象 (g.user 或 None)
        :param args: 搜索/分页参数字典
        """
        # 1. 权限校验
        target_user = User.query.get(target_user_id)
        if not target_user:
            return None, u"目标用户不存在"

        # 判断权限：如果是本人、或者是管理员、或者用户开启了公开
        is_owner = (viewer and viewer.id == target_user_id)
        is_admin = (viewer and str(viewer.role_type) == '3')
        
        if not target_user.is_public_work:
            if not (is_owner or is_admin):
                return None, u"该用户设置了作品集不公开"

        # 2. 查询逻辑
        query = db.session.query(HeritageGameRecord).join(
            Heritage, HeritageGameRecord.heritage_id == Heritage.id
        ).filter(
            HeritageGameRecord.user_id == target_user_id,
            HeritageGameRecord.work_path.isnot(None)
        )

        # 过滤条件
        if args.get('file_type'):
            query = query.filter(HeritageGameRecord.file_type == args['file_type'])
        if args.get('heritage_class'):
            query = query.filter(Heritage.heritage_class == args['heritage_class'])
        if args.get('keyword'):
            rule = f"%{args['keyword']}%"
            query = query.filter(or_(
                HeritageGameRecord.work_name.like(rule), 
                Heritage.heritage_name.like(rule)
            ))

        # 分页
        pag = query.order_by(HeritageGameRecord.finish_time.desc()).paginate(
            page=args.get('page', 1), per_page=args.get('per_page', 10), error_out=False
        )
        
        result = {
            'list': pag.items, 
            'total': pag.total, 
            'page': pag.page, 
            'pages': pag.pages, 
            'per_page': pag.per_page
        }
        return result, u"获取成功"
    
    @staticmethod
    def update_user_work_name(user_id, record_id, new_name):
        """
        修改用户个人作品的名称
        """
        # 1. 权限与存在性校验：必须是本人的作品
        record = HeritageGameRecord.query.filter_by(
            id=record_id, 
            user_id=user_id
        ).first()

        if not record:
            return None, u"作品不存在或您无权修改"

        # 2. 检查该记录是否真的有作品（防止修改纯通关记录的名称，可选）
        if not record.work_path:
            return None, u"该记录不包含作品文件，无需命名"

        try:
            # 3. 更新名称
            record.work_name = new_name.strip()
            db.session.commit()
            return record, u"修改成功"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
        
    @staticmethod
    def delete_user_work(user_id, record_id):
        """
        删除用户个人作品（含物理文件清理）
        """
        # 1. 权限校验：确保只能删除自己的作品
        record = HeritageGameRecord.query.filter_by(
            id=record_id, 
            user_id=user_id
        ).first()

        if not record:
            return False, u"作品不存在或您无权删除"

        # 记录待删除的物理路径，用于后续清理
        work_rel_path = record.work_path

        try:
            # 2. 从数据库删除记录
            db.session.delete(record)
            
            # 3. 物理文件清理逻辑
            if work_rel_path:
                # 拼接绝对路径 (例如: /app/static/uploads/user_works/xxx.png)
                abs_path = os.path.join(current_app.static_folder, work_rel_path)
                # 检查文件是否存在，存在则删除
                if os.path.exists(abs_path):
                    os.remove(abs_path)

            db.session.commit()
            return True, u"作品已成功从您的画廊中移除"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Delete Work Error: {str(e)}")
            return False, u"删除失败，请稍后再试"
        
    @staticmethod
    def get_work_file_data(user_id, record_id):
        """
        获取下载文件所需的物理信息
        """
        # 1. 权限校验
        record = HeritageGameRecord.query.filter_by(
            id=record_id, 
            user_id=user_id
        ).first()

        if not record or not record.work_path:
            return None, u"作品不存在或尚未上传文件"

        # 2. 获取文件的绝对物理路径
        # 你的 work_path 存的是 "uploads/user_works/images/xxx.png"
        abs_path = os.path.join(current_app.static_folder, record.work_path)
        
        if not os.path.exists(abs_path):
            return None, u"物理文件已丢失"

        # 3. 准备下载时的文件名（加上原始后缀）
        ext = record.work_path.rsplit('.', 1)[-1]
        # 例如：我的作品_1778405133.png
        download_name = f"{record.work_name}_{record.finish_time}.{ext}"

        return {
            'abs_path': abs_path,
            'download_name': download_name,
            'directory': os.path.dirname(abs_path),
            'filename': os.path.basename(abs_path)
        }, u"获取成功"