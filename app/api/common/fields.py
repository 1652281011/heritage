#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/29 上午12:01
# @Software：PyCharm
# @Author  : scott
from flask_restful import fields


def common_fields(data_fileds=None, is_list=False):
    """
        公共数据
        :param resid: 错误码
        :param msg: 错误消息
        :param status: 处理结果状态
        :param data: 返回数据
        :param data_fileds: 返回数据字段
        :return:
    """
    _common_fields = {
        "resid": fields.Integer(default=200),
        "msg": fields.String(default=u'请求成功'),
        "status": fields.String(default=u'success')
    }
    if data_fileds:
        if not is_list:
            _common_fields.update(data=fields.Nested(data_fileds))
        else:
            _common_fields.update(data=fields.List(fields.Nested(data_fileds)))
    return _common_fields


def test_fields():
    data_fields = {
        'data': fields.String
    }
    return common_fields(data_fields)

def user_login_fields():
    """
    定义登录成功后返回给前端的字段模板
    """
    data_fields = {
        'username': fields.String,
        'nickname': fields.String,
        'e_time': fields.String,
        'role_type': fields.String,
        'auth_token': fields.String
    }
    return common_fields(data_fields)

def user_uodate_fields():
    # 隐私设置嵌套结构
    privacy_fields = {
        'is_public_collect': fields.Boolean,
        'is_public_like': fields.Boolean,
        'is_public_work': fields.Boolean,
        'is_public_achievement': fields.Boolean,
    }

    data_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'nickname': fields.String,
        'avatar': fields.String,
        'bio': fields.String,
        'role_type': fields.String,
        'privacy': fields.Nested(privacy_fields)
    }
    return common_fields(data_fields)

def user_fields():
    # 隐私设置嵌套结构
    privacy_fields = {
        'is_public_collect': fields.Boolean,
        'is_public_like': fields.Boolean,
        'is_public_work': fields.Boolean,
        'is_public_achievement': fields.Boolean,
    }

    data_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'nickname': fields.String,
        'avatar': fields.String,
        'bio': fields.String,
        'medal_count': fields.Integer,
        'heritage_coin': fields.Integer,
        'experience_progress': fields.Integer,
        'checkin_days': fields.Integer,
        'role_type': fields.String,
        'privacy': fields.Nested(privacy_fields), # 嵌套展示
        'last_login': fields.String(attribute='last_login')
    }
    return common_fields(data_fields)

def heritage_list_fields():
    item_fields = {
        'id': fields.Integer,
        'heritage_name': fields.String,
        'heritage_class': fields.String,
        'cover': fields.String(attribute='cover_url'),
        'view': fields.Integer,
        'collect': fields.Integer,
        'is_interact': fields.Integer,
        'is_collected': fields.Boolean,
    }

    data_dict_fields = {
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer,
        'per_page': fields.Integer,
        'pages': fields.Integer,
    }

    return common_fields(data_dict_fields)

def heritage_detail_fields():
    data_fields = {
        'id': fields.Integer,
        'heritage_name': fields.String,
        'heritage_class': fields.String,
        'origin': fields.String,
        'spread_region': fields.String,
        'enroll_year': fields.String,
        'brief_intro': fields.String,
        'introduction': fields.String,
        'cover': fields.String(attribute='cover_url'),
        'images': fields.List(fields.String, attribute='image_list'),
        'view': fields.Integer,
        'collect': fields.Integer,
        'is_interact': fields.Boolean,
        'is_collected': fields.Boolean,
        'tags': fields.List(fields.String, attribute='tag_list'),
        'create_time': fields.String(attribute='create_time_str')
    }
    return common_fields(data_fields)

def question_fields():
    """列表字段：不包含答案和解析，保证安全"""
    data_fields = {
        'id': fields.Integer,
        'heritage_id': fields.Integer,
        'q_type': fields.Integer,
        'stem': fields.String,
        'option_a': fields.String,
        'option_b': fields.String,
        'option_c': fields.String,
        'option_d': fields.String,
        'option_count': fields.Integer
    }
    return common_fields(data_fields)

def question_detail_fields():
    data_fields = {
        'id': fields.Integer,
        'heritage_id': fields.Integer,
        'q_type': fields.Integer,
        'stem': fields.String,
        'option_a': fields.String,
        'option_b': fields.String,
        'option_c': fields.String,
        'option_d': fields.String,
        'option_count': fields.Integer,
        'answer': fields.String,
        'analysis': fields.String
    }
    return common_fields(data_fields)

def verify_result_fields():
    """结果字段：包含正确答案和解析"""
    data_fields = {
        'is_correct': fields.Boolean,
        'correct_answer': fields.String(attribute='answer'),
        'analysis': fields.String
    }
    return common_fields(data_fields)

def quiz_complete_result_fields():

    medal_item_fields = {
        'name': fields.String,
        'icon': fields.String(attribute='icon_url'), # 自动调用模型中的动态 IP 逻辑
        'description': fields.String
    }

    data_fields = {
        'correct_count': fields.Integer,
        'total_count': fields.Integer,
        'accuracy': fields.Float,      # 正确率 (如 66.7)
        'is_all_correct': fields.Boolean,
        # 对应 Service 返回字典中的 new_achievements 键
        'new_achievements': fields.List(fields.Nested(medal_item_fields)),
        
        # 通关记录信息（如果 record 对象存在，映射其 finish_time_str 属性）
        'finish_time': fields.String(attribute='record.finish_time_str', default=None)
    }
    
    return common_fields(data_fields)

def user_finished_fields():

    item_fields = {
        'id': fields.Integer,
        'heritage_name': fields.String,
        'heritage_class': fields.String,
        'cover': fields.String(attribute='cover_url'),
        'finish_time': fields.String(attribute='finish_time_display') 
    }

    data_fields = {
        'list': fields.List(fields.Nested(item_fields)), # 关键点：使用 List 和 Nested
        'total': fields.Integer,
        'page': fields.Integer,
        'pages': fields.Integer
    }
    
    return common_fields(data_fields)

def heritage_completed_detail_fields():
    data_fields = {
        'id': fields.Integer,
        'heritage_name': fields.String,
        'is_interact': fields.Boolean, # 该非遗是否有小游戏
        'is_collected': fields.Boolean,
        'completion_status': fields.Integer, 
    }
    return common_fields(data_fields)

def collect_list_fields():
    data_fields = {
        'heritage_id': fields.Integer,
        'heritage_name': fields.String,
        'cover': fields.String,
        'collect_time': fields.String
    }
    return common_fields(data_fields)

# def achievement_list_fields():
#     """定义全量成就列表字段"""
#     item_fields = {
#         'id': fields.Integer,
#         'category': fields.Integer,
#         'category_name': fields.String,
#         'name': fields.String,
#         'description': fields.String,
#         'icon': fields.String(attribute='icon_url'),
#         'target_value': fields.Integer,
#         'is_unlocked': fields.Boolean,  # 是否解锁
#         'unlock_time': fields.String    # 解锁时间(未解锁为空)
#     }
#     # 嵌套进 list 中
#     return common_fields({'list': fields.List(fields.Nested(item_fields))})

def achievement_item_fields():
    """单个成就项的字段定义"""
    return {
        'id': fields.Integer,
        'name': fields.String,
        'description': fields.String,
        'category': fields.String,
        'target_value': fields.Integer,
        'icon_url': fields.String,
        # 动态生成的属性
        'is_unlocked': fields.Boolean,
        'unlock_time': fields.String
    }

def achievement_list_fields():
    """成就列表接口唯一的 Fields 定义"""
    # 使用你提供的 common_fields 包装格式
    return common_fields(data_fileds=achievement_item_fields(), is_list=True)

def all_completion_fields():
    """
    全量状态返回格式规范
    """
    item_fields = {
        'heritage_id': fields.Integer,
        'status': fields.Integer
    }
    
    data_fields = {
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer
    }
    return common_fields(data_fields)

def _inter_base():
    return {
        'id': fields.Integer,
        'name': fields.String,
        'heritage_title': fields.String,
        'cover_url': fields.String(attribute='full_cover_url'),
        'author_name': fields.String,
        'view_count': fields.Integer
    }

# 列表展示 (通用)
def interaction_list_fields():
    item = _inter_base()
    item.update({'status': fields.Integer, 'create_time': fields.String(attribute='create_time_format')})
    return common_fields({'list': fields.List(fields.Nested(item)), 'total': fields.Integer})

def _get_interaction_base_dict():
    return {
        'id': fields.Integer,
        'name': fields.String,
        'heritage_title': fields.String,
        'cover_url': fields.String(attribute='full_cover_url'),
        'author_name': fields.String,
        'view_count': fields.Integer,
        # 使用标准时间格式字符串
        'create_time': fields.String(attribute='create_time_str') 
    }

# 2. 用户端详情字段 (公开信息)
def interaction_user_detail_fields():
    data = _get_interaction_base_dict().copy()
    data.update({
        'description': fields.String,
        'entry_url': fields.String
    })
    # 统一包装返回
    return common_fields(data)

# 3. 管理端/专家端详情字段 (全量信息)
def interaction_manage_detail_fields():
    # 核心修复：从原始字典开始拷贝，而不是从包装后的 Nested 对象拷贝
    data = _get_interaction_base_dict().copy()
    data.update({
        'description': fields.String,
        'entry_url': fields.String,
        'status': fields.Integer,
        'review_comment': fields.String,
        'heritage_id': fields.Integer,
        'author_id': fields.Integer
    })
    # 统一包装返回
    return common_fields(data)

def _interaction_base_item():
    return {
        'id': fields.Integer,
        'name': fields.String,
        'heritage_title': fields.String,
        'cover_url': fields.String(attribute='full_cover_url'), # 自动处理动态IP
        'status': fields.Integer,
    }

# 1. 专家投稿返回字段 (InteractionContributeResource)
def interaction_contribute_result_fields():
    data = _interaction_base_item()
    data.update({
        'description': fields.String,
        'entry_url': fields.String,
        'create_time': fields.String(attribute='create_time_format')
    })
    return common_fields(data)

# 2. 管理员审核结果返回字段 (InteractionReviewResource)
def interaction_review_result_fields():
    data = _interaction_base_item()
    data.update({
        'review_comment': fields.String,
        'heritage_id': fields.Integer,
        'author_name': fields.String
    })
    return common_fields(data)

# 申请单简略列表
def request_list_fields():
    item_fields = {
        'id': fields.Integer,
        'req_type': fields.Integer,
        'temp_name': fields.String,
        'status': fields.Integer,
        'review_comment': fields.String,
        'author_nickname': fields.String(attribute='user.nickname'),
        'create_time': fields.String(attribute='create_time_str')
    }
    
    # 整体响应结构
    data_fields = {
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,      # 总记录数
        'page': fields.Integer,       # 当前页码 (核心修复点)
        'pages': fields.Integer,      # 总页码 (核心修复点)
        'per_page': fields.Integer    # 每页大小
    }
    
    return common_fields(data_fields)

# 申请单详细信息
def request_detail_fields():
    return common_fields({
        'id': fields.Integer,
        'req_type': fields.Integer,
        'status': fields.Integer,
        'review_comment': fields.String,
        'applicant_nickname': fields.String(attribute='user.nickname'),
        'content': fields.Raw(attribute='data_snap'),
        'create_time': fields.String(attribute='create_time_str')
    })

def question_request_list_fields():
    item = {
        'id': fields.Integer,
        'req_type': fields.Integer,
        'status': fields.Integer,
        'heritage_title': fields.String(attribute='heritage.heritage_name'),
        'author_nickname': fields.String(attribute='user.nickname'),
        'create_time': fields.String(attribute='create_time_str')
    }
    return common_fields({'list': fields.List(fields.Nested(item)), 'total': fields.Integer, 'page': fields.Integer, 'pages': fields.Integer})

def question_request_detail_fields():
    return common_fields({
        'id': fields.Integer,
        'req_type': fields.Integer,
        'status': fields.Integer,
        'review_comment': fields.String,
        'content': fields.Raw(attribute='data_snap'),
        'create_time': fields.String(attribute='create_time_str')
    })

# 管理员查看正式题库的详情字段
def admin_question_detail_fields():
    data = {
        'id': fields.Integer,
        'heritage_id': fields.Integer,
        'heritage_title': fields.String(attribute='heritage.heritage_name'),
        'q_type': fields.Integer,
        'stem': fields.String,
        'options': {
            'A': fields.String(attribute='option_a'),
            'B': fields.String(attribute='option_b'),
            'C': fields.String(attribute='option_c'),
            'D': fields.String(attribute='option_d'),
        },
        'answer': fields.String,
        'analysis': fields.String,
        'create_time': fields.String(attribute='create_time_format'), # 调用模型属性
        'update_time': fields.Integer(attribute='e_time')
    }
    return common_fields(data)

# 管理员题库列表字段
def admin_question_list_fields():
    # 复用上面的结构的一部分
    item = {
        'id': fields.Integer,
        'heritage_title': fields.String(attribute='heritage.heritage_name'),
        'q_type': fields.Integer,
        'stem': fields.String,
        'answer': fields.String,
        'create_time': fields.String(attribute='create_time_format')
    }
    return common_fields({
        'list': fields.List(fields.Nested(item)),
        'total': fields.Integer,
        'page': fields.Integer,
        'pages': fields.Integer
    })

def game_submit_result_fields():
    medal_fields = {
        'name': fields.String,
        'icon': fields.String(attribute='icon_url'),
        'description': fields.String
    }
    
    data = {
        # 注意：这里的 attribute 必须指向 Service 返回字典中的 key
        'work_name': fields.String(attribute='record.work_name'),
        'work_url': fields.String(attribute='record.full_work_url'),
        'finish_time': fields.String(attribute='record.finish_time_str'),
        
        # 【修正点】：增加 attribute='new_medals'
        'new_achievements': fields.List(fields.Nested(medal_fields), attribute='new_medals'),
        
        'completion_status': fields.Integer 
    }
    return common_fields(data)

def heritage_history_fields():
    item_fields = {
        'id': fields.Integer,
        'heritage_name': fields.String,
        'cover': fields.String(attribute='cover_url'),
        'heritage_class': fields.String,
        # 重点：展示当时浏览的时间
        'view_time': fields.String(attribute='history_time') 
    }
    return common_fields({
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer
    })

def user_recent_game_fields():
    item_fields = {
        'interaction_id': fields.Integer(attribute='id'),
        'interaction_name': fields.String(attribute='name'),
        'heritage_title': fields.String,       # 来源于模型 property
        'cover_url': fields.String(attribute='full_cover_url'), # 动态IP适配
        'play_time': fields.String(attribute='recent_play_time') # 对应 Service 挂载的属性
    }
    return common_fields({
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer
    })

def user_work_advanced_list_fields():
    """带分类信息的作品列表字段"""
    item_fields = {
        'id': fields.Integer,
        'work_name': fields.String,
        'file_type': fields.Integer,         # 1-图片, 2-音频, 3-视频
        'work_url': fields.String(attribute='full_work_url'),
        
        # 归属信息
        'heritage_name': fields.String(attribute='heritage.heritage_name'),
        'heritage_class': fields.String(attribute='heritage.heritage_class'),
        'interaction_name': fields.String(attribute='interaction.name'),
        
        'finish_time': fields.String(attribute='finish_time_str')
    }
    
    return common_fields({
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer,
        'pages': fields.Integer
    })

def element_list_fields():
    item_fields = {
        'id': fields.Integer,
        'bind_element_id': fields.String,
        'heritage_id': fields.Integer,
        'is_active': fields.Boolean,
        'heritage_name': fields.String(attribute='heritage.heritage_name')
    }
    return common_fields(data_fileds=item_fields, is_list=True)

def element_create_fields():
    """新增板块后的返回字段定义（单一Fields）"""
    item_fields = {
        'id': fields.Integer,
        'bind_element_id': fields.String,
        'is_active': fields.Boolean,
        'heritage_id': fields.Integer # 新增时通常为 null
    }
    # 调用公共包装函数，返回单条数据格式
    return common_fields(data_fileds=item_fields, is_list=False)

def element_update_fields():
    """修改绑定后的单一 Fields 定义"""
    item_fields = {
        'id': fields.Integer,
        'bind_element_id': fields.String,
        'heritage_id': fields.Integer,
        'is_active': fields.Boolean,
        'heritage_name': fields.String(attribute='heritage.heritage_name') # 返回更新后的绑定名称
    }
    return common_fields(data_fileds=item_fields, is_list=False)

def unbound_heritage_fields():
    """获取未绑定非遗列表的单一 Fields"""
    item_fields = {
        'id': fields.Integer,
        'heritage_name': fields.String
    }
    return common_fields(data_fileds=item_fields, is_list=True)

def post_fields():
    data_fields = {
        'post_id': fields.Integer(attribute='id', default=0), # 帖子ID (映射模型里的id)
        'title': fields.String(default=''),                    # 标题
        'content': fields.String(default=''),                  # 内容
        'images': fields.List(fields.String, default=[]),      # 图片URL列表
        'author': fields.String(attribute='author_nickname', default=''), # 作者昵称
        'c_time': fields.String(attribute='create_time', default=''),     # 创建时间
        'is_public': fields.Integer(default=1),
        'view_count': fields.Integer(default=0),               # 阅读数
        'like_count': fields.Integer(default=0),               # 点赞数
        'comment_count': fields.Integer(default=0)             # 评论数
    }
    return common_fields(data_fields)

def post_list_fields():
    # 单个帖子的格式定义
    item_fields = {
        'id': fields.Integer,
        'title': fields.String,
        'author': fields.String(attribute='author_nickname'),
        'cover': fields.String(attribute='cover_url'),
        'like_count': fields.Integer,
        'comment_count': fields.Integer,
        'view_count': fields.Integer,    # <--- 【新增】添加浏览量字段
        'create_time': fields.String(attribute='c_time_str')
    }

    data_dict_fields = {
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer
    }

    return common_fields(data_dict_fields)

def post_detail_fields():
    # 1. 评论项格式
    comment_item = {
        'id': fields.Integer,
        'content': fields.String,
        'nickname': fields.String(attribute='user.nickname'), # 关联获取评论者昵称
        'avatar': fields.String(attribute='user.avatar_url'),       
        'create_time': fields.String(attribute='c_time_str')
    }

    # 2. 详情主体格式
    data_dict_fields = {
        'id': fields.Integer,
        'title': fields.String,
        'content': fields.String,
        'view_count': fields.Integer,
        'like_count': fields.Integer,
        'comment_count': fields.Integer,
        'is_liked': fields.Boolean,          # 当前用户是否已点赞
        'images': fields.List(fields.String(attribute='url')), # 图片URL列表
        'author': {
            'nickname': fields.String(attribute='author.nickname'),
            'avatar': fields.String(attribute='author.avatar_url'),
        },
        'comments': fields.List(fields.Nested(comment_item)), # 评论列表嵌套
        'create_time': fields.String(attribute='c_time_str')
    }

    # 使用 common_fields 包装成统一的 {resid, msg, status, data}
    return common_fields(data_dict_fields)

def log_list_fields():
    """日志列表单一输出格式"""
    item_fields = {
        'id': fields.Integer,
        'admin_id': fields.Integer,
        'module': fields.String,
        'action': fields.String,
        'target_id': fields.String,
        'target_name': fields.String,
        'params': fields.String,         # 存储的 JSON 参数内容
        'status': fields.Integer,        # 1-成功, 0-失败
        'error_msg': fields.String,      # 错误原因
        'ip_address': fields.String,
        'create_time': fields.String(attribute='create_time_str') # 调用 Model 里的 property
    }
    # 使用公共包装函数，增加分页元数据
    return common_fields({
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer,
        'per_page': fields.Integer
    }, is_list=False) # 这里的 data 对应一个包含 list 和 pagination 的字典

def creator_app_fields():
    """申请记录详情输出"""
    item_fields = {
        'id': fields.Integer,
        'user_id': fields.Integer,
        'real_name': fields.String,
        'specialty': fields.String,
        'reason': fields.String,
        'evidence_url': fields.String,
        'status': fields.Integer,
        'admin_comment': fields.String,
        'c_time': fields.String(attribute='create_time_str')
    }
    return common_fields(data_fileds=item_fields, is_list=False)

def creator_progress_fields():
    """查看申请进度的单一 Fields"""
    item_fields = {
        'id': fields.Integer,
        'status': fields.Integer,        # 0-待审核, 1-通过, 2-驳回
        'real_name': fields.String,
        'specialty': fields.String,
        'admin_comment': fields.String,  # 如果被驳回，这里显示原因
        'c_time': fields.String(attribute='create_time_str'),
        'e_time': fields.String(attribute='update_time_str')
    }
    # 返回包装后的公共格式
    return common_fields(data_fileds=item_fields, is_list=False)

def creator_detail_admin_fields():
    """管理员查看详情的单一 Fields"""
    item_fields = {
        'id': fields.Integer,
        'user_id': fields.Integer,
        'nickname': fields.String(attribute='user.nickname'),
        
        'avatar': fields.String(attribute='user.avatar_url'), 
        
        'real_name': fields.String,
        'specialty': fields.String,
        'reason': fields.String,
        'evidence_url': fields.String,
        'status': fields.Integer,
        'admin_comment': fields.String,
        'c_time': fields.String(attribute='create_time_str'),
        'e_time': fields.String(attribute='update_time_str')
    }
    return common_fields(data_fileds=item_fields, is_list=False)

def admin_user_list_fields():
    """管理员查看用户列表的单一 Fields"""
    item_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'nickname': fields.String,
        'avatar': fields.String(attribute='avatar_url'), # 使用模型中的拼接逻辑
        'role_type': fields.String,
        'status': fields.Integer,
        # 时间格式化
        'register_time': fields.String(attribute='create_time_str'),
        'last_login_time': fields.String(attribute='update_time_str')
    }
    # 包装成分页格式
    return common_fields({
        'list': fields.List(fields.Nested(item_fields)),
        'total': fields.Integer,
        'page': fields.Integer,
        'per_page': fields.Integer
    }, is_list=False)

def game_user_ranking_fields():
    data_field = {
        'uid': fields.Integer(default=0),
        'score': fields.Integer(default=0),
        'user_name': fields.String(default=''),
        'user_mobile': fields.String(default=''),

    }
    data_fields = {
        'data': fields.List(fields.Nested(data_field))
    }
    return common_fields(data_fields)


def user_history_record_fields():
    level_record_field = {
        'tips': fields.String(default=''),
        'level': fields.Integer(default=0),
        'score': fields.Integer(default=0),
        'is_break': fields.Integer(default=0),
        'error_count': fields.Integer(default=0),
    }

    data_field = {
        'level': fields.Integer(default=0),
        'score': fields.Integer(default=0),
        'level_record': fields.List(fields.Nested(level_record_field))
    }

    data_fields = {
        'user_name': fields.String(default=''),
        'user_mobile': fields.String(default=''),
        'highest_score': fields.Integer(default=0),
        'break_record_count': fields.Integer(default=0),
        'break_level_record': fields.List(fields.Nested(data_field))
    }
    return common_fields(data_fields)


def sign_fields():
    data_fields = {
        'username': fields.String(default=''),
        'auth_token': fields.String(default=''),
        'user_id': fields.Integer(default=0),
        'b_id': fields.Integer(default=0),
    }
    return common_fields(data_fields)


def user_game_fields():
    data_fields = {
        'data': fields.List(fields.String),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def games_fields():
    data_field = {
        'game_name': fields.String(default=''),
        'id': fields.String(default=''),
        'user_count': fields.Integer(default=0),
    }
    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def game_users_fields():
    data_field = {
        'user_name': fields.String(default=''),
        'user_mobile': fields.String(default=''),
        'game_name': fields.String(default=''),
        'highest_score': fields.Integer(default=0),
        'user_id': fields.Integer(default=0),
        'break_count': fields.Integer(default=0),
        'start_time': fields.String(default=''),
        'end_time': fields.String(default=''),
        'c_time': fields.String(default=''),
        'game_id': fields.String(default=''),
    }

    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def label_fields():
    data_field = {
        'name': fields.String(default=''),
        'id': fields.Integer(default=0),
    }

    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def article_fields():
    data_field = {
        'title': fields.String(default=''),
        'instruction': fields.String(default=''),
        'id': fields.Integer(default=0),
        'c_time': fields.String(default=''),
        'label_name': fields.String(default=''),
        'label_id': fields.Integer(default=0),
    }

    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def article_info_fields():
    data_field = {
        'title': fields.String(default=''),
        'content': fields.String(default=''),
        'label_name': fields.String(default=''),
        'label_id': fields.Integer(default=0),
        'id': fields.Integer(default=0),
        'c_time': fields.String(default=''),
    }
    data_fields = {
        'data': fields.Nested(data_field),
    }
    return common_fields(data_fields)


def answer_record_user_fields():
    data_field = {
        'questionnaire_name': fields.String(default=''),
        'id': fields.Integer(default=0),
        'score': fields.Integer(default=0),
        'c_time': fields.String(default=''),
        'feedback_content': fields.String(default=''),
        'user_name': fields.String(default=''),
    }

    data_fields = {
        'data': fields.List(fields.Nested(data_field)),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def user_basic_information_fields():
    data_field = {
        "name": fields.String(default=''),
        "gender": fields.String(default=''),
        "nation": fields.String(default=''),
        "birthday": fields.String(default=''),
        "culture": fields.String(default=''),
        "marriage": fields.String(default=''),
        "live": fields.String(default=''),
        "work_status": fields.String(default=''),
        "position": fields.String(default=''),
        "economy": fields.String(default=''),
        "address": fields.String(default=''),
        "internet_equipment": fields.String(default=''),
        "internet_time": fields.String(default=''),
        "social_media": fields.String(default=''),
        "height": fields.String(default=''),
        "weight": fields.String(default=''),
        "id_card": fields.String(default=''),
        "group_id": fields.String(default=''),
        "age": fields.Integer(default=0),
        "nickname": fields.String(default=''),
        "avatar_url": fields.String(default=''),
        "province": fields.String(default=''),
        "city": fields.String(default=''),
        "district": fields.String(default=''),
        "basic_diseases": fields.String(default=''),
        "serious_illness": fields.String(default=''),
            "RDAs_diary": fields.String(default='')


    }

    data_fields = {
        'data': fields.Nested(data_field),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def sport_evaluation_fields():
    data_field = {
        'user_name': fields.String(default=''),
        'c_time': fields.String(default=''),
        'height': fields.Float(default=0.0),
        'weight': fields.Float(default=0.0),
        'sit_and_reach_l': fields.Float(default=0.0),
        'sit_and_reach_r': fields.Float(default=0.0),
        'claw_l': fields.Float(default=0.0),
        'claw_r': fields.Float(default=0.0),
        'sitting_count': fields.Integer(default=0),
        'arm_count_l': fields.Integer(default=0),
        'arm_count_r': fields.Integer(default=0),
        'mark_time_count': fields.Integer(default=0),
        'walk244': fields.Integer(default=0),
        'id': fields.Integer(default=0),
        'user_id': fields.Integer(default=0),
        'mark_time_score': fields.Float(default=0),
        'mark_time_level': fields.String(default=''),
        'sitting_level': fields.String(default=''),
        'sitting_score': fields.Float(default=0),
        'arm_score': fields.Float(default=0),
        'arm_level': fields.String(default=''),
        'BMI_score': fields.Float(default=0),
        'BMI_level': fields.String(default=''),
        'walk244_score': fields.Float(default=0),
        'walk244_level': fields.String(default=''),
        'sit_and_reach_score': fields.Float(default=0),
        'sit_and_reach_level': fields.String(default=''),
        'claw_score': fields.Float(default=0),
        'claw_level': fields.String(default=''),
        'total_points': fields.Float(default=0)
    }

    data_fields = {
        'data': fields.Nested(data_field),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)


def user_diet_fields():
    data_field = {

        "time": fields.String(default=''),
        "water": fields.String(default=''),
        "cereal": fields.String(default=''),
        "tubers": fields.String(default=''),
        "vegetable": fields.String(default=''),
        "fruit": fields.String(default=''),
        "meat_egg": fields.String(default=''),
        "milk": fields.String(default=''),
        "soy_nut": fields.String(default=''),
        "salt": fields.String(default=''),
        "oil": fields.String(default='')

    }

    data_fields = {
        'data': fields.Nested(data_field),
        'total': fields.Integer(default=0)
    }
    return common_fields(data_fields)
