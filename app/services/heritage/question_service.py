# -*- coding: utf-8 -*-
import time
from sqlalchemy import func
from app.models import db
from app.models.heritage import Heritage
from app.models.heritage_question import HeritageQuestion
from app.models.quiz_record import HeritageQuizRecord
from app.services.achievements.achievement_service import AchievementService

class QuestionService:
    @staticmethod
    def get_random_questions(h_id, limit=3):
        """
        核心逻辑：后端随机抽取3道题
        """
        # 注意：MySQL使用 func.rand()，PostgreSQL/SQLite使用 func.random()
        return HeritageQuestion.query.filter_by(heritage_id=h_id)\
            .order_by(func.rand())\
            .limit(limit)\
            .all()

    @staticmethod
    def verify_answer(q_id, user_answer):
        """
        答案校验逻辑
        """
        question = HeritageQuestion.query.get(q_id)
        if not question:
            return None, False

        # 格式化比对：转大写、去空格、字符排序（兼容多选顺序不一致问题）
        db_ans = "".join(sorted(question.answer.upper().strip()))
        usr_ans = "".join(sorted(user_answer.upper().strip()))
        
        is_correct = (db_ans == usr_ans)
        return question, is_correct
    
    @staticmethod
    def verify_and_submit_quiz(user_id, heritage_id, answers_list):
        """
        校验问答并触发成就
        """
        if not answers_list:
            return None, "未提交任何答案"

        results = []
        correct_count = 0
        total_count = len(answers_list)

        # 1. 逐题校验
        for item in answers_list:
            q_id = item.get('q_id')
            u_ans = "".join(sorted(str(item.get('ans', '')).upper().strip()))
            q = HeritageQuestion.query.get(q_id)
            if not q: continue
            
            db_ans = "".join(sorted(q.answer.upper().strip()))
            is_correct = (db_ans == u_ans)
            if is_correct: correct_count += 1
            
            results.append({
                'q_id': q_id, 'is_correct': is_correct,
                'correct_answer': q.answer, 'analysis': q.analysis
            })

        # 2. 计算正确率
        accuracy = round((correct_count / total_count) * 100, 1) if total_count > 0 else 0
        is_all_correct = (correct_count == total_count)

        # 3. 登录用户且全对：记录并触发成就
        record_obj = None
        new_medals = [] 
        
        if user_id and is_all_correct:
            try:
                record_obj = HeritageQuizRecord.query.filter_by(user_id=user_id, heritage_id=heritage_id).first()
                if not record_obj:
                    # 首次通关问答
                    record_obj = HeritageQuizRecord(user_id=user_id, heritage_id=heritage_id, finish_time=int(time.time()))
                    db.session.add(record_obj)
                    # 重要：必须 flush，使下方的 AchievementService 里的数据库查询能看到这条记录
                    db.session.flush()

                    # 【核心埋点】：触发成就系统，检查是否达成“全通关”
                    new_medals = AchievementService.trigger_event(user_id, 'quiz', heritage_id)
                
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Quiz Record/Medal Error: {str(e)}")

        return {
            'correct_count': correct_count,
            'total_count': total_count,
            'accuracy': accuracy,
            'is_all_correct': is_all_correct,
            'details': results,
            'new_achievements': new_medals, # 返回新解锁的成就
            'record': record_obj 
        }, "校验完成"