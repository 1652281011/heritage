import json
import time
from werkzeug.datastructures import FileStorage
from flask import current_app, g
from sqlalchemy import or_
from app.models import db
from sqlalchemy.orm import joinedload
from app.models.game_record import HeritageGameRecord
from app.models.heritage import Heritage
from app.models.heritage_collect import HeritageCollect
from app.models.heritage_edit import HeritageRequest
from app.models.heritage_image import HeritageImage
from app.models.quiz_record import HeritageQuizRecord
from app.models.users import User
from app.utils.uploader import Uploader


class HeritageRequestService:
    @staticmethod
    def _save_images_snapshot(args, existing_snap=None):
        """
        内部工具：处理图片上传并生成内容快照字典
        """
        # 1. 提取基础文本字段
        snap = {
            'heritage_name': args.get('heritage_name', '').strip(),
            'heritage_class': args.get('heritage_class'),
            'origin': args.get('origin'),
            'spread_region': args.get('spread_region'),
            'brief_intro': args.get('brief_intro'),
            'introduction': args.get('introduction'),
            'enroll_year': args.get('enroll_year'),
            'tags': args.get('tags')
        }
        
        # 2. 处理封面图 (image_type=1)
        if args.get('cover_image'):
            config_c = {
                "pathFormat": "uploads/h/c/{time}{rand:6}", 
                "maxSize": 2*1024*1024, 
                "allowFiles": [".jpg",".png"], 
                "oriName": args['cover_image'].filename
            }
            up_c = Uploader(args['cover_image'], config_c, current_app.static_folder)
            if up_c.stateInfo == "SUCCESS":
                snap['cover_path'] = up_c.fullName.lstrip('/')
        elif existing_snap:
            # 如果没传新封面，保留旧快照里的路径
            snap['cover_path'] = existing_snap.get('cover_path')

        # 3. 处理详情图列表 (image_type=2)
        if args.get('detail_images'):
            snap['detail_paths'] = []
            for img in args['detail_images']:
                config_d = {
                    "pathFormat": "uploads/h/d/{time}{rand:6}", 
                    "maxSize": 2*1024*1024, 
                    "allowFiles": [".jpg",".png"], 
                    "oriName": img.filename
                }
                up_d = Uploader(img, config_d, current_app.static_folder)
                if up_d.stateInfo == "SUCCESS":
                    snap['detail_paths'].append(up_d.fullName.lstrip('/'))
        elif existing_snap:
            # 如果没传新详情图，保留旧快照里的路径列表
            snap['detail_paths'] = existing_snap.get('detail_paths', [])

        return snap

    @staticmethod
    def submit_request(user_id, args):
        """
        专家投稿/修改申请核心逻辑
        """
        r_id = args.get('request_id')      # 申请单ID (修改已有申请时传)
        h_id = args.get('heritage_id')      # 正式项目ID (修改已上线内容时传)
        req_type = args.get('req_type')     # 前端传来的意图类型
        name = args.get('heritage_name', '').strip()

        # ---------------------------------------------------------
        # 第一阶段：基础存在性与 ID 校验 (防止报错)
        # ---------------------------------------------------------
        
        # 场景 A：用户想修改已经提交过的申请单 (待审核或被驳回的)
        if r_id:
            req_obj = HeritageRequest.query.filter_by(id=r_id, user_id=user_id).first()
            if not req_obj:
                return None, u"错误：找不到对应的申请记录，或您无权操作该记录"
            if req_obj.status == 1:
                return None, u"错误：该申请已审核通过并上线，无法直接修改，请发起‘修改正式项目’申请"
            
            # 确定这条记录的本质类型：
            # 如果这条记录原本就是新增类型(1)，或者它没有关联正式ID，那么它本质依然是新增类型
            target_req_type = req_obj.req_type
            target_heritage_id = req_obj.heritage_id
        
        # 场景 B：用户想发起一个新的申请 (不带 request_id)
        else:
            if not req_type:
                return None, u"错误：未指定操作类型（新增或修改）"
            
            # 如果是修改已上线的项目，必须校验 heritage_id
            if int(req_type) == 2:
                if not h_id:
                    return None, u"错误：修改已上线项目必须提供项目 ID"
                target_heritage = Heritage.query.get(h_id)
                if not target_heritage:
                    return None, u"错误：目标非遗项目不存在，无法发起修改"
                target_heritage_id = h_id
                target_req_type = 2
            else:
                # 新增项目申请
                if not name:
                    return None, u"错误：非遗项目名称不能为空"
                # 检查正式库是否已有同名
                if Heritage.query.filter_by(heritage_name=name).first():
                    return None, u"错误：项目‘{}’已在正式库中，请使用‘修改建议’功能".format(name)
                target_heritage_id = None
                target_req_type = 1

            # ---------------------------------------------------------
            # 第二阶段：个人查重校验 (status=0 锁定)
            # ---------------------------------------------------------
            if target_req_type == 1:
                # 检查本人是否有同名项目正在审核
                pending = HeritageRequest.query.filter_by(
                    user_id=user_id, temp_name=name, status=0, req_type=1
                ).first()
                if pending:
                    return None, u"提示：您提交的‘{}’新增申请正在审核中，请勿重复提交".format(name)
            else:
                # 检查本人是否对该 ID 有正在审核的修改单
                pending = HeritageRequest.query.filter_by(
                    user_id=user_id, heritage_id=target_heritage_id, status=0, req_type=2
                ).first()
                if pending:
                    return None, u"提示：您对该项目的修改申请已在审核中，请勿重复提交"

            req_obj = None # 标记为新建模式

        # ---------------------------------------------------------
        # 第三阶段：处理数据快照与持久化
        # ---------------------------------------------------------
        
        # 获取旧快照用于保留未改动的图片
        old_snap = req_obj.data_snap if req_obj else None
        snapshot_data = HeritageRequestService._save_images_snapshot(args, old_snap)

        try:
            if req_obj:
                # 修改现有申请单：状态重置，性质保持
                req_obj.content_json = json.dumps(snapshot_data, ensure_ascii=False)
                req_obj.temp_name = name
                req_obj.status = 0
                req_obj.review_comment = None
                req_obj.e_time = int(time.time())
                res_obj = req_obj
            else:
                # 创建全新申请单
                res_obj = HeritageRequest(
                    user_id=user_id,
                    req_type=target_req_type,
                    heritage_id=target_heritage_id,
                    temp_name=name,
                    content_json=json.dumps(snapshot_data, ensure_ascii=False)
                )
                db.session.add(res_obj)

            db.session.commit()
            return res_obj, u"申请已成功提交，请等待管理员审核"

        except Exception as e:
            db.session.rollback()
            return None, f"系统错误：{str(e)}"
        
    @staticmethod
    def cancel_request(user_id, req_id):
        """撤销逻辑：支持待审核(0)和已驳回(2)"""
        req = HeritageRequest.query.filter_by(id=req_id, user_id=user_id).first()
        if not req: return False, u"记录不存在或无权操作"
        
        # 修改点：允许撤销驳回的(2)
        if req.status not in [0, 2]:
            return False, u"已通过的申请无法直接撤销"

        try:
            db.session.delete(req)
            db.session.commit()
            return True, u"撤销成功"
        except Exception as e:
            db.session.rollback(); return False, str(e)
        
    @staticmethod
    def audit(req_id, status, comment):
        """管理员：审核非遗项目申请"""
        req = HeritageRequest.query.get(req_id)
        if not req: 
            return None, u"未找到单据"

        try:
            # --- 【日志记录点】设置基础信息 ---
            g.target_id = req_id
            # 动作名称：审核通过 / 审核驳回
            g.log_action = u"审核通过" if int(status) == 1 else u"审核驳回"
            
            # 获取申请中的非遗名称用于展示
            h_name = req.temp_name # 优先使用冗余字段
            if not h_name and req.data_snap:
                h_name = req.data_snap.get('heritage_name')
            g.target_name = h_name or u"未知申请项目"
            # -------------------------------

            req.status = status
            req.review_comment = comment

            if int(status) == 1:
                data = req.data_snap
                
                # --- A. 确定正式表对象 ---
                if req.req_type == 1: # 新增申请
                    h_name_in_snap = data.get('heritage_name')
                    if Heritage.query.filter_by(heritage_name=h_name_in_snap).first():
                        return None, u"审核失败：该项目名称已由他人率先发布"
                    
                    target_h = Heritage(author_id=req.user_id)
                    db.session.add(target_h)
                else: # 修改申请
                    target_h = Heritage.query.get(req.heritage_id)
                    if not target_h: 
                        return None, u"关联正式项目已丢失"

                # --- B. 先赋值 ---
                fields_to_sync = [
                    'heritage_name', 'heritage_class', 'origin', 
                    'spread_region', 'brief_intro', 'introduction', 
                    'enroll_year', 'tags'
                ]
                for f in fields_to_sync:
                    if f in data:
                        setattr(target_h, f, data[f])
                
                target_h.e_time = int(time.time())

                # --- C. flush 拿 ID ---
                db.session.flush() 

                # --- D. 同步图片 ---
                from app.models.heritage_image import HeritageImage
                HeritageImage.query.filter_by(heritage_id=target_h.id).delete()
                if data.get('cover_path'):
                    db.session.add(HeritageImage(heritage_id=target_h.id, image_url=data['cover_path'], image_type=1))
                for p in data.get('detail_paths', []):
                    db.session.add(HeritageImage(heritage_id=target_h.id, image_url=p, image_type=2))

                # --- E. 竞争处理 ---
                if req.req_type == 1:
                    new_h_id = target_h.id
                    others = HeritageRequest.query.filter(
                        HeritageRequest.temp_name == h_name_in_snap,
                        HeritageRequest.status == 0,
                        HeritageRequest.id != req.id,
                        HeritageRequest.req_type == 1
                    ).all()
                    for o_req in others:
                        o_req.req_type = 2
                        o_req.heritage_id = new_h_id
                        o_req.review_comment = u"该项目已由他人发布，您的申请已自动转为修改建议"

            db.session.commit()
            return req, u"审核处理成功"
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return None, f"操作失败: {str(e)}"
        
    @staticmethod
    def get_filtered_list(user_id=None, status=None, user_keyword=None, heritage_keyword=None, page=1, per_page=10):
        """
        统一列表查询服务：支持高级搜索和权限隔离
        :param user_id: 如果传入则锁定该用户的数据（个人模式）；不传则查全量（管理模式）
        :param status: 过滤审核状态 (0-待审, 1-通过, 2-驳回)
        :param user_keyword: 搜索申请人的昵称或账号 (仅管理员有效)
        :param heritage_keyword: 搜索非遗项目名称
        """
        # 1. 建立关联查询 (HeritageRequest 关联 User)
        # 这样我们可以同时通过申请单表和用户表的字段进行过滤
        query = db.session.query(HeritageRequest).join(User, HeritageRequest.user_id == User.id)

        # 2. 【核心隔离逻辑】
        if user_id:
            # 如果提供了 user_id，强制只查询该用户自己的申请
            query = query.filter(HeritageRequest.user_id == user_id)
        
        # 3. 状态过滤
        if status is not None:
            query = query.filter(HeritageRequest.status == status)

        # 4. 管理员搜索：按申请人信息搜索 (只有 user_id 为 None 时才有意义，防止用户越权搜别人)
        if user_keyword and not user_id:
            rule = f'%{user_keyword}%'
            query = query.filter(or_(
                User.nickname.like(rule),
                User.username.like(rule)
            ))

        # 5. 非遗名称搜索
        if heritage_keyword:
            query = query.filter(HeritageRequest.temp_name.like(f'%{heritage_keyword}%'))

        # 6. 执行排序与分页
        # 按创建时间倒序排，最新的申请在最前面
        pagination = query.order_by(HeritageRequest.c_time.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )

        # 7. 组装符合规范的返回字典
        return {
            'list': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }