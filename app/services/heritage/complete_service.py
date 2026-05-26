# -*- coding: utf-8 -*-
from app.models.heritage import Heritage
from app.models.quiz_record import HeritageQuizRecord
from app.models.game_record import HeritageGameRecord
from app.models import db

class CompletionService:
    @staticmethod
    def get_all_completion_status(user_id):
        """
        全量通关状态获取逻辑（含“无互动自动转全通”逻辑）
        """
        all_heritages = db.session.query(Heritage.id, Heritage.is_interact).all()
        
        if not user_id:
            # 游客状态：无论有没有互动，全部返回 0
            return [{"heritage_id": h.id, "status": 0} for h in all_heritages]

        # 2. 获取该用户已完成的问答和游戏 ID 集合
        quiz_done_ids = {
            r.heritage_id for r in HeritageQuizRecord.query.filter_by(user_id=user_id).all()
        }
        game_done_ids = {
            r.heritage_id for r in HeritageGameRecord.query.filter_by(user_id=user_id).all()
        }

        # 3. 核心逻辑判断
        res_list = []
        for h_id, can_interact in all_heritages:
            has_quiz = h_id in quiz_done_ids
            has_game = h_id in game_done_ids
            
            status = 0
            
            if can_interact:
                # --- 情况 A: 有互动模块的项目 ---
                if has_quiz and has_game:
                    status = 3  # 全通关
                elif has_game:
                    status = 2  # 仅互动
                elif has_quiz:
                    status = 1  # 仅问答
            else:
                # --- 情况 B: 无互动模块的项目 (重点修改) ---
                # 对于没有互动的项目，完成答题即代表全通关
                if has_quiz:
                    status = 3  # 自动晋升为全通关
                else:
                    status = 0  # 未开始
            
            res_list.append({
                "heritage_id": h_id,
                "status": status
            })
            
        return res_list
    
    @staticmethod
    def get_single_status(user_id, heritage_id):
        """
        计算单个非遗项目的通关状态码
        """
        if not user_id:
            return 0
        
        # 获取非遗项目信息
        h = Heritage.query.get(heritage_id)
        if not h: return 0

        # 查询问答和游戏记录
        has_quiz = HeritageQuizRecord.query.filter_by(user_id=user_id, heritage_id=heritage_id).first() is not None
        has_game = HeritageGameRecord.query.filter_by(user_id=user_id, heritage_id=heritage_id).first() is not None

        # 逻辑判定
        if not h.is_interact:
            return 3 if has_quiz else 0
        
        if has_quiz and has_game: return 3
        if has_game: return 2
        if has_quiz: return 1
        return 0