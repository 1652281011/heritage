# -*- coding: utf-8 -*-
import time
from app.models.base import db
from app.models.achievements import Achievement, UserAchievement, UserStat

# -*- coding: utf-8 -*-
import time
from app.models.base import db
from app.models.achievements import Achievement, UserAchievement, UserStat
from app.models.quiz_record import HeritageQuizRecord
from app.models.game_record import HeritageGameRecord
from app.models.users import User

class AchievementService:
    @staticmethod
    def _increment_stat(user_id, key):
        """累加数值并检查解锁"""
        stat = UserStat.query.filter_by(user_id=user_id, stat_key=key).first()
        if not stat:
            stat = UserStat(user_id=user_id, stat_key=key, current_value=1)
            db.session.add(stat)
        else:
            stat.current_value += 1
        db.session.flush() # 必须，使下方查询可见最新数值

        # 匹配满足条件且未获得的成就
        earned_ids = [ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user_id).all()]
        new_unlocks = Achievement.query.filter(
            Achievement.stat_dimension == key,
            Achievement.target_value <= stat.current_value,
            ~Achievement.id.in_(earned_ids) if earned_ids else True
        ).all()

        medals = []
        for ach in new_unlocks:
            db.session.add(UserAchievement(user_id=user_id, achievement_id=ach.id, unlock_time=int(time.time())))
            medals.append(ach)
        return medals

    @staticmethod
    def trigger_event(user_id, event_type, heritage_id=None):
        """成就触发总入口"""
        new_medals = []
        
        # A. 直接统计累加
        if event_type == 'game':
            new_medals.extend(AchievementService._increment_stat(user_id, 'game_count'))
        elif event_type == 'work':
            new_medals.extend(AchievementService._increment_stat(user_id, 'work_count'))
        # 注：如果是纯 'quiz_count' 成就也可以在这里加

        # B. 【核心】：非遗全通关检查 (finished_count)
        if heritage_id:
            from app.models.heritage import Heritage
            h = Heritage.query.get(heritage_id)
            if h:
                # 获取该用户在该项目的问答和互动记录状态
                has_q = HeritageQuizRecord.query.filter_by(user_id=user_id, heritage_id=heritage_id).first() is not None
                # has_game 指用户是否在该非遗下有任何互动作品记录
                has_g = HeritageGameRecord.query.filter_by(user_id=user_id, heritage_id=heritage_id).first() is not None
                
                # 判断逻辑：有互动则需双通，无互动只需问答通
                is_finished = (h.is_interact and has_q and has_g) or (not h.is_interact and has_q)
                
                if is_finished:
                    # 唯一性标记 Key：防止同一个非遗反复刷分
                    mark_key = f"mark_finished_{heritage_id}"
                    if not UserStat.query.filter_by(user_id=user_id, stat_key=mark_key).first():
                        db.session.add(UserStat(user_id=user_id, stat_key=mark_key, current_value=1))
                        # 核心：增加“全通关非遗数量”的统计
                        new_medals.extend(AchievementService._increment_stat(user_id, 'finished_count'))
        
        return new_medals
    
    @staticmethod
    def _check_privacy(target_user, viewer):
        """
        内部逻辑：校验访问者是否有权查看目标用户的成就
        """
        # 1. 目标开启了公开，任何人(包括游客)都能看
        if target_user.is_public_achievement == 1:
            return True
        
        # 2. 如果是私密状态，校验访问者身份
        if viewer:
            # 访问者是本人
            if viewer.id == target_user.id:
                return True
            # 访问者是管理员
            if str(viewer.role_type) == '3':
                return True
                
        return False

    @staticmethod
    def get_earned_list(target_user_id, viewer):
        """接口1逻辑：仅获取已获得的成就"""
        target_user = User.query.get(target_user_id)
        if not target_user: return None, u"用户不存在"
        
        if not AchievementService._check_privacy(target_user, viewer):
            return None, u"该用户设置了成就列表不公开"

        # 连表查询已解锁的成就
        records = db.session.query(Achievement, UserAchievement.unlock_time).join(
            UserAchievement, Achievement.id == UserAchievement.achievement_id
        ).filter(
            UserAchievement.user_id == target_user_id
        ).order_by(UserAchievement.unlock_time.desc()).all()

        items = []
        for ach, u_time in records:
            ach.is_unlocked = True
            ach.unlock_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(u_time))
            items.append(ach)
        return items, u"获取成功"

    @staticmethod
    def get_full_atlas(target_user_id, viewer):
        """接口2逻辑：获取全量图鉴（含未解锁）"""
        target_user = User.query.get(target_user_id)
        if not target_user: return None, u"用户不存在"

        if not AchievementService._check_privacy(target_user, viewer):
            return None, u"该用户设置了成就列表不公开"

        # 1. 查出系统定义的全部成就
        all_ach = Achievement.query.order_by(Achievement.category.asc()).all()
        # 2. 查出该用户的解锁记录
        unlocked_records = UserAchievement.query.filter_by(user_id=target_user_id).all()
        unlocked_map = {r.achievement_id: r.unlock_time for r in unlocked_records}

        # 3. 动态标注每个成就的解锁状态
        for ach in all_ach:
            if ach.id in unlocked_map:
                ach.is_unlocked = True
                ach.unlock_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(unlocked_map[ach.id]))
            else:
                ach.is_unlocked = False
                ach.unlock_time = ""
        return all_ach, u"获取成功"