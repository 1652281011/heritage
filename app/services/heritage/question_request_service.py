# -*- coding: utf-8 -*-
import json, time
from flask import g
from sqlalchemy import or_
from app.models.base import db
from app.models.heritage_question import HeritageQuestion
from app.models.question_request import HeritageQuestionRequest
from app.models.users import User
from app.models.heritage import Heritage

class QuestionService:

    @staticmethod
    def submit_request(user_id, args):
        """专家：提交题目申请"""
        r_id = args.get('request_id')      # 申请单ID（改驳回件）
        q_id = args.get('question_id')     # 正式题ID（改正式题）
        req_type = int(args.get('req_type', 1))
        stem_text = args.get('stem', '').strip()
        h_id = args['heritage_id']

        # 1. 基础校验 (修改现有的申请单)
        if r_id:
            req = HeritageQuestionRequest.query.filter_by(id=r_id, user_id=user_id).first()
            if not req or req.status == 1: 
                return None, u"申请记录不存在或已审核通过"
        else:
            # 2. 【核心修改】：精细化防重复逻辑
            
            if req_type == 2:
                # 场景：修改正式题目。一个专家对“同一道题”只能有一个在审单。
                if not q_id: return None, u"修改题目必须提供原题目ID"
                already_pending = HeritageQuestionRequest.query.filter_by(
                    user_id=user_id, status=0, question_id=q_id, req_type=2
                ).first()
                if already_pending:
                    return None, u"该题目的修改申请正在审核中，请勿重复提交"
            
            else:
                # 场景：新增题目 (req_type=1)。
                # 允许对同一个非遗提交多道题，但防止提交“题干完全一样”的重复题目。
                # 注意：这里我们根据 temp_name（或是直接在 content_json 里查，但推荐在提交前做校验）
                # 简单做法是查询该用户对该非遗是否有“相同题干”的在审单。
                
                # 我们通过 SQL 的模糊匹配或逻辑判断来识别是否提交了重名题干
                # 如果量大，可以考虑在 HeritageQuestionRequest 增加一个 stem_digest 的哈希字段
                pending_reqs = HeritageQuestionRequest.query.filter_by(
                    user_id=user_id, status=0, heritage_id=h_id, req_type=1
                ).all()
                
                for p in pending_reqs:
                    if p.data_snap.get('stem') == stem_text:
                        return None, u"您已提交过内容完全相同的题目，请勿重复操作"

        # 3. 构造快照
        snap = {
            'q_type': args['q_type'], 
            'stem': stem_text,
            'option_a': args['option_a'], 
            'option_b': args['option_b'],
            'option_c': args.get('option_c'), 
            'option_d': args.get('option_d'),
            'answer': args['answer'].upper().strip(),
            'analysis': args.get('analysis')
        }

        try:
            if r_id: # 更新申请单
                req.content_json = json.dumps(snap, ensure_ascii=False)
                req.status = 0
                req.review_comment = None
                res_obj = req
            else: # 创建新申请
                res_obj = HeritageQuestionRequest(
                    user_id=user_id, req_type=req_type, 
                    heritage_id=h_id, question_id=q_id,
                    content_json=json.dumps(snap, ensure_ascii=False)
                )
                db.session.add(res_obj)
            
            db.session.commit()
            return res_obj, u"提交成功"
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def audit(req_id, status, comment):
        """管理员：审核题目建议/申请"""
        req = HeritageQuestionRequest.query.get(req_id)
        if not req: 
            return None, u"未找到单据"

        try:
            # 1. 基础赋值
            req.status = status
            req.review_comment = comment
            
            # --- 为日志准备动态描述 ---
            # 假设 1 为通过，2 为驳回
            action_name = u"审核通过" if int(status) == 1 else u"审核驳回"
            g.log_action = action_name
            
            # 获取题干信息用于展示在日志中
            data = req.data_snap or {}
            stem_info = data.get('stem', '')
            g.target_name = (stem_info[:20] + '...') if len(stem_info) > 20 else stem_info
            g.target_id = req_id
            # ------------------------

            if int(status) == 1:
                # 处理正式数据同步
                if req.req_type == 1: # 新增申请
                    target_q = HeritageQuestion(heritage_id=req.heritage_id)
                    db.session.add(target_q)
                else: # 修改申请
                    target_q = HeritageQuestion.query.get(req.question_id)
                    if not target_q: 
                        return None, u"正式题目数据已丢失"

                # 同步快照数据
                for f in data:
                    if hasattr(target_q, f):
                        setattr(target_q, f, data[f])

            db.session.commit()
            return True, u"审核处理成功"
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_request_list(user_id=None, args=None):
        """通用列表查询"""
        # query = db.session.query(HeritageQuestionRequest).join(User).join(Heritage)
        query = db.session.query(HeritageQuestionRequest).outerjoin(
            User, HeritageQuestionRequest.user_id == User.id
        ).outerjoin(
            Heritage, HeritageQuestionRequest.heritage_id == Heritage.id # <--- 必须是这个条件
        )
        if user_id: query = query.filter(HeritageQuestionRequest.user_id == user_id)
        if args.get('status') is not None: query = query.filter(HeritageQuestionRequest.status == args['status'])
        if args.get('user_keyword') and not user_id:
            k = f"%{args['user_keyword']}%"
            query = query.filter(or_(User.nickname.like(k), User.username.like(k)))
        if args.get('heritage_keyword'):
            query = query.filter(Heritage.heritage_name.like(f"%{args['heritage_keyword']}%"))
            
        pag = query.order_by(HeritageQuestionRequest.c_time.desc()).paginate(page=args['page'], per_page=10, error_out=False)
        return {'list': pag.items, 'total': pag.total, 'page': pag.page, 'pages': pag.pages}
    
    @staticmethod
    def get_admin_live_list(args):
        """管理员：获取正式库题目列表"""
        query = HeritageQuestion.query.join(Heritage)
        
        if args.get('heritage_id'):
            query = query.filter(HeritageQuestion.heritage_id == args['heritage_id'])
        if args.get('q_type'):
            query = query.filter(HeritageQuestion.q_type == args['q_type'])
        if args.get('keyword'):
            query = query.filter(HeritageQuestion.stem.like(f"%{args['keyword']}%"))
            
        pag = query.order_by(HeritageQuestion.c_time.desc()).paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )
        return {'list': pag.items, 'total': pag.total, 'page': pag.page, 'pages': pag.pages}

    @staticmethod
    def admin_direct_save(args):
        """管理员：直接保存题目（增加防重复提交逻辑）"""
        q_id = args.get('id')
        heritage_id = args.get('heritage_id')
        stem = args.get('stem', '').strip()
        
        if not Heritage.query.get(heritage_id):
            return None, u"关联的非遗项目不存在"

        try:
            # --- 防重复提交逻辑开始 ---
            if not q_id: # 只有新增时才触发强力防重
                # 检查最近 5 分钟内是否有相同题干的题目被创建（或者全表查重）
                duplicate = HeritageQuestion.query.filter_by(
                    heritage_id=heritage_id,
                    stem=stem
                ).first()
                if duplicate:
                    return None, u"请勿重复提交：该非遗项目下已存在相同题干的题目"
            # --- 防重复提交逻辑结束 ---

            if q_id:
                question = HeritageQuestion.query.get(q_id)
                if not question: return None, u"题目不存在"
                msg = u"题目更新成功"
                g.log_action = u"修改题目"
            else:
                question = HeritageQuestion()
                db.session.add(question)
                msg = u"题目直接发布成功"
                g.log_action = u"新增题目"

            # 字段映射
            for f in ['heritage_id', 'q_type', 'stem', 'option_a', 'option_b', 'option_c', 'option_d', 'answer', 'analysis']:
                if args.get(f) is not None:
                    val = args[f]
                    if f == 'answer': val = str(val).upper().strip()
                    setattr(question, f, val)
            
            db.session.commit()

            g.target_id = question.id
            g.target_name = (question.stem[:20] + '...') if len(question.stem) > 20 else question.stem
            
            return question, msg
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def admin_batch_delete(q_ids):
        """管理员：批量删除题目（带存在性校验）"""
        if not q_ids:
            return False, u"未提供任何题目ID"
            
        try:
            # 1. 查询库中实际存在的记录
            existing_questions = HeritageQuestion.query.filter(HeritageQuestion.id.in_(q_ids)).all()
            existing_ids = [q.id for q in existing_questions]
            
            # 2. 找出不存在的 ID
            missing_ids = list(set(q_ids) - set(existing_ids))
            
            if not existing_ids:
                return False, u"操作失败：所选题目在系统中均不存在"

            # 3. 执行删除
            num = HeritageQuestion.query.filter(HeritageQuestion.id.in_(existing_ids)).delete(synchronize_session=False)
            db.session.commit()

            # --- 挂载日志信息 ---
            g.target_id = ",".join(map(str, existing_ids))
            detail_msg = f"成功删除 {num} 道题目。"
            if missing_ids:
                detail_msg += f" 忽略了不存在的ID: {missing_ids}"
            
            g.target_name = detail_msg
            return True, detail_msg
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)