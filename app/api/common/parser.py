# -*- coding: utf-8 -*-
import re
from flask_restful import reqparse
import werkzeug
from werkzeug.datastructures import FileStorage

# 工具函数
def is_mobile(mobile):
    if not mobile:
        return None
    # 确保正则支持11位
    import re
    if re.match(r'^1[3-9]\d{9}$', str(mobile)):
        return str(mobile)
    else:
        raise ValueError(u"手机号格式不正确")

def is_email(email_str):
    """验证邮箱格式"""
    email_str = str(email_str).strip()
    # 简单的邮箱正则
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email_str):
        raise ValueError(f"{email_str} 不是有效的邮箱格式")
    return email_str

def parse_bool(value):
    """自定义布尔类型解析函数"""
    if isinstance(value, str):
        return value.lower() == 'true' or value == '1'
    elif isinstance(value, int):
        return value == 1
    return bool(value)
  

def user_register_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, location='json', required=True, help='手机号/账号必填')
    parser.add_argument('password', type=str, location='json', required=True, help='密码必填')
    parser.add_argument('role_type', type=str, location='json', default='1', help='1:群众, 2:专家')

    return parser.parse_args()

def user_sign_in_parser():
    parser = reqparse.RequestParser()

    parser.add_argument('username', type=str, location='json', required=True, help=u'手机号')
    parser.add_argument('password', type=str, location='json', required=True, help=u'密码')
    parser.add_argument('app_type', type=str, location='json', default='web')
    
    return parser.parse_args()

def user_info_get_parser():
    """获取用户信息参数解析"""
    parser = reqparse.RequestParser()
    # 如果不传 user_id，默认查看当前登录用户自己
    parser.add_argument('user_id', type=int, location='args', required=False, help='用户ID')
    return parser.parse_args()

def user_update_parser():
    """更新用户信息参数解析"""
    parser = reqparse.RequestParser()
    parser.add_argument('nickname', type=str, location='form', help='昵称')
    parser.add_argument('bio', type=str, location='form', help='个性签名')
    parser.add_argument('avatar', type=werkzeug.datastructures.FileStorage, location='files', help='头像文件')
    
    # 隐私设置 (前端传 0 或 1)
    parser.add_argument('is_public_collect', type=int, location='form', help='公开收藏')
    parser.add_argument('is_public_like', type=int, location='form', help='公开点赞')
    parser.add_argument('is_public_work', type=int, location='form', help='公开作品')
    parser.add_argument('is_public_achievement', type=int, location='form', help='公开成就')
    
    return parser.parse_args()

def user_password_update_parser():
    """修改密码参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('old_password', type=str, location='json', required=True, help=u'旧密码必填')
    parser.add_argument('new_password', type=str, location='json', required=True, help=u'新密码必填')
    return parser.parse_args()

def heritage_list_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=20, location='args')
    parser.add_argument('keyword', type=str, default=None, location='args')
    parser.add_argument('heritage_class', type=str, default=None, location='args')
    parser.add_argument('origin', type=str, default=None, location='args')
    parser.add_argument('enroll_year', type=str, default=None, location='args')
    parser.add_argument('order_by', type=str, default='new', location='args', 
                        choices=['new', 'view', 'like', 'collect'], help="排序参数非法")
    return parser.parse_args()

# --- 新增：我的足迹（历史浏览）解析器 ---
def user_browsing_history_parser():
    """获取用户浏览历史列表参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    return parser.parse_args()

# --- 新增：最近游玩解析器 ---
def user_recent_games_parser():
    """获取用户最近互动游玩列表参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    return parser.parse_args()

def heritage_detail_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=True, location='args', help="非遗项目ID不能为空")
    return parser.parse_args()

# 1. 提交/修改申请解析器 (Form-Data)
def heritage_request_submit_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('req_type', type=int, required=True, location='form') # 1-新增, 2-修改
    parser.add_argument('heritage_id', type=int, location='form')
    parser.add_argument('request_id', type=int, location='form') 
    
    # 业务字段
    parser.add_argument('heritage_name', type=str, required=True, location='form')
    parser.add_argument('heritage_class', type=str, required=True, location='form')
    parser.add_argument('origin', type=str, location='form') # 发源地
    parser.add_argument('spread_region', type=str, required=True, location='form')
    parser.add_argument('brief_intro', type=str, location='form') # 简要介绍
    parser.add_argument('introduction', type=str, location='form')
    parser.add_argument('enroll_year', type=str, location='form') # 入选年份
    parser.add_argument('tags', type=str, location='form') # 标签（逗号隔开）
    
    # 文件
    parser.add_argument('cover_image', type=FileStorage, location='files')
    parser.add_argument('detail_images', type=FileStorage, location='files', action='append')
    return parser.parse_args()

# 2. 列表查询解析器
def heritage_request_list_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args') 
    parser.add_argument('status', type=int, location='args') # 0,1,2
    return parser.parse_args()

# 管理员列表搜索 (Args)
def heritage_request_search_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args') 
    parser.add_argument('status', type=int, location='args')
    parser.add_argument('user_keyword', type=str, location='args') # 搜申请人
    parser.add_argument('heritage_keyword', type=str, location='args') # 搜非遗名
    return parser.parse_args()


def heritage_request_id_parser():
    """解析撤销或查询ID (JSON格式)"""
    parser = reqparse.RequestParser()
    parser.add_argument('request_id', type=int, required=True, location='json')
    return parser.parse_args()

# 3. 管理员审核解析器
def heritage_audit_action_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('request_id', type=int, required=True, location='json')
    parser.add_argument('status', type=int, required=True, location='json') # 1-通过 2-拒绝
    parser.add_argument('review_comment', type=str, location='json')
    return parser.parse_args()

def heritage_request_id_parser():
    """解析撤销申请时传入的 ID"""
    parser = reqparse.RequestParser()
    # 接收 JSON 中的 request_id
    parser.add_argument('request_id', type=int, required=True, location='json', help="缺少申请单ID")
    return parser.parse_args()

def admin_heritage_direct_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('req_type', type=int, required=True, location='form')
    # 修改时需要传 heritage_id，新增时不需要
    parser.add_argument('heritage_id', type=int, location='form')
    
    parser.add_argument('heritage_name', type=str, location='form')
    parser.add_argument('heritage_class', type=str, location='form')
    parser.add_argument('origin', type=str, location='form')
    parser.add_argument('spread_region', type=str, location='form')
    parser.add_argument('brief_intro', type=str, location='form')
    parser.add_argument('introduction', type=str, location='form')
    parser.add_argument('enroll_year', type=str, location='form')
    parser.add_argument('tags', type=str, location='form')
    
    parser.add_argument('cover_image', type=FileStorage, location='files')
    parser.add_argument('detail_images', type=FileStorage, location='files', action='append')
    return parser.parse_args()

def heritage_delete_parser():
    """解析删除请求参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('heritage_id', type=int, required=True, location='json', help='非遗ID不能为空')
    return parser.parse_args()

def question_request_submit_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('req_type', type=int, required=True, location='json')
    parser.add_argument('question_id', type=int, location='json')
    parser.add_argument('request_id', type=int, location='json')
    parser.add_argument('heritage_id', type=int, required=True, location='json')
    # 题目字段
    parser.add_argument('q_type', type=int, required=True, location='json')
    parser.add_argument('stem', type=str, required=True, location='json')
    parser.add_argument('option_a', type=str, required=True, location='json')
    parser.add_argument('option_b', type=str, required=True, location='json')
    parser.add_argument('option_c', type=str, location='json')
    parser.add_argument('option_d', type=str, location='json')
    parser.add_argument('answer', type=str, required=True, location='json')
    parser.add_argument('analysis', type=str, location='json')
    return parser.parse_args()

def question_request_query_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('status', type=int, location='args')
    parser.add_argument('user_keyword', type=str, location='args')
    parser.add_argument('heritage_keyword', type=str, location='args')
    return parser.parse_args()

# 1. 管理员查询正式题库列表
def admin_question_query_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=20, location='args')
    parser.add_argument('heritage_id', type=int, location='args')
    parser.add_argument('q_type', type=int, location='args') # 1-3
    parser.add_argument('keyword', type=str, location='args') # 搜题干
    return parser.parse_args()

# 2. 管理员直接新增/修改题目
def admin_question_direct_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('req_type', type=int, required=True, location='json')
    # 存在 id 则为修改，不存在则为新增
    parser.add_argument('id', type=int, location='json') 
    parser.add_argument('heritage_id', type=int, required=True, location='json')
    parser.add_argument('q_type', type=int, required=True, choices=[1, 2, 3], location='json')
    parser.add_argument('stem', type=str, required=True, location='json')
    parser.add_argument('option_a', type=str, required=True, location='json')
    parser.add_argument('option_b', type=str, required=True, location='json')
    parser.add_argument('option_c', type=str, location='json')
    parser.add_argument('option_d', type=str, location='json')
    parser.add_argument('answer', type=str, required=True, location='json')
    parser.add_argument('analysis', type=str, location='json')
    return parser.parse_args()

# 3. 删除题目
def admin_question_delete_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('question_ids', type=list, required=True, location='json', help="请提供要删除的题目ID列表")
    return parser.parse_args()

def game_result_submit_parser():
    parser = reqparse.RequestParser()
    # 文本参数
    parser.add_argument('interaction_id', type=int, required=True, location='form')
    parser.add_argument('passed', type=str, required=True, location='form') # FormData中bool会转为字符串"true"
    parser.add_argument('work_name', type=str, location='form', help="作品名称")
    parser.add_argument('work_file', type=FileStorage, location='files', required=False, help="作品文件上传失败")
    return parser.parse_args()

def game_finish_parser():
    parser = reqparse.RequestParser()
    # 前端 Body 传参: {"heritage_id": 1}
    parser.add_argument('heritage_id', type=int, required=True, location='json', help="缺少非遗项目ID")
    return parser.parse_args()

def question_list_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('heritage_id', type=int, required=True, location='args', help="缺少非遗ID")
    return parser.parse_args()

def answer_verify_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('question_id', type=int, required=True, location='json')
    parser.add_argument('user_answer', type=str, required=True, location='json')
    return parser.parse_args()

def complete_quiz_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('heritage_id', type=int, required=True, location='json')
    parser.add_argument('answers', type=list, required=True, location='json')
    return parser.parse_args()

def user_finished_heritages_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    return parser.parse_args()

def collect_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('heritage_id', type=int, required=True, location='json', help="heritage_id不能为空")
    return parser.parse_args()

def collect_list_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    parser.add_argument('user_id', type=int, location='args')
    return parser.parse_args()

def all_completion_parser():
    """
    全量状态查询解析器
    """
    parser = reqparse.RequestParser()
    # 预留分页功能（如果未来非遗项目成千上万，建议加上）
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=100, location='args')
    return parser.parse_args()

def interaction_contribute_parser():
    """专家投稿解析器 (Multipart Form)"""
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, location='form', help="互动名称必填")
    parser.add_argument('heritage_id', type=int, required=True, location='form', help="非遗ID必填")
    parser.add_argument('description', type=str, location='form')
    parser.add_argument('entry_url', type=str, required=True, location='form', help="必须提供可访问的URL")
    parser.add_argument('cover_file', type=FileStorage, location='files', help="封面图片上传失败")
    return parser.parse_args()

def interaction_list_base_parser():
    """基础分页"""
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    return parser

# 投稿解析 (Form-Data)
def interaction_submit_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, location='form')
    parser.add_argument('heritage_id', type=int, required=True, location='form')
    parser.add_argument('description', type=str, location='form')
    parser.add_argument('entry_url', type=str, required=True, location='form')
    parser.add_argument('cover_file', type=FileStorage, location='files')
    return parser.parse_args()

def interaction_update_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('interaction_id', type=int, required=True, location='form')
    parser.add_argument('name', type=str, location='form')
    parser.add_argument('description', type=str, location='form')
    parser.add_argument('entry_url', type=str, location='form')
    parser.add_argument('cover_file', type=FileStorage, location='files')
    return parser.parse_args()

# 审核操作解析 (JSON)
def interaction_audit_action_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('interaction_id', type=int, required=True, location='json', help="缺少互动项目ID")
    # 允许 1:发布, 2:驳回, 3:下架
    parser.add_argument('status', type=int, required=True, choices=[1, 2, 3], location='json', help="审核状态非法")
    parser.add_argument('review_comment', type=str, location='json', help="审核备注")
    return parser.parse_args()

# 列表查询解析 (Args)
def interaction_query_list_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    parser.add_argument('status', type=int, location='args', choices=[0, 1, 2, 3])
    parser.add_argument('heritage_id', type=int, location='args')
    return parser.parse_args()

def interaction_by_heritage_parser():
    """根据非遗ID查询已上架互动列表的参数"""
    parser = reqparse.RequestParser()
    # 必须提供 heritage_id
    parser.add_argument('heritage_id', type=int, required=True, location='args', help="必须提供非遗项目ID")
    # 分页参数
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    return parser.parse_args()

# 详情查询解析 (Args)
def get_interaction_id_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=True, location='args')
    return parser.parse_args()

def interaction_id_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=True, location=['json', 'args'])
    return parser.parse_args()

def user_works_search_parser():
    parser = reqparse.RequestParser()
    # 目标用户的ID（从URL参数获取）
    parser.add_argument('user_id', type=int, required=True, location='args')
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    parser.add_argument('file_type', type=int, location='args')
    parser.add_argument('heritage_class', type=str, location='args')
    parser.add_argument('keyword', type=str, location='args')
    return parser.parse_args()

def work_name_update_parser():
    """修改作品名称参数解析器"""
    parser = reqparse.RequestParser()
    # 接收作品记录的唯一 ID
    parser.add_argument('record_id', type=int, required=True, location='json', help="缺少作品ID")
    # 接收新的作品名称
    parser.add_argument('work_name', type=str, required=True, location='json', help="作品名称不能为空")
    return parser.parse_args()

def work_delete_parser():
    """删除作品参数解析器"""
    parser = reqparse.RequestParser()
    # 接收需要删除的作品记录 ID
    parser.add_argument('record_id', type=int, required=True, location='json', help="缺少作品ID")
    return parser.parse_args()

def element_list_parser():
    """解析获取板块列表的参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('keyword', type=str, location='args') 
    return parser.parse_args()

def element_add_parser():
    """解析新增板块的参数"""
    parser = reqparse.RequestParser()
    # 必填项：板块标识符
    parser.add_argument('bind_element_id', type=str, required=True, location='json', help='板块标识符(bind_element_id)不能为空')
    # 可选项：是否激活，默认为0（未激活）
    parser.add_argument('is_active', type=int, default=0, location='json')
    return parser.parse_args()

def element_update_parser():
    """解析修改绑定关系的参数"""
    parser = reqparse.RequestParser()
    # 必填：确定要修改哪一个板块
    parser.add_argument('bind_element_id', type=str, required=True, location='json', help='板块标识不能为空')
    # 选填：要绑定的非遗ID（如果传空或0，可以视为解绑）
    parser.add_argument('heritage_id', type=int, location='json')
    # 选填：是否同时激活该板块
    parser.add_argument('is_active', type=int, location='json')
    return parser.parse_args()

def unbound_heritage_parser():
    """解析查询参数（如需搜索或分页可在此扩展）"""
    parser = reqparse.RequestParser()
    parser.add_argument('keyword', type=str, location='args')
    return parser.parse_args()

"""社区相关"""

def post_list_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('keyword', type=str, location='args', help=u'关键词')
    parser.add_argument('page', type=int, location='args', default=1)
    parser.add_argument('per_page', type=int, location='args', default=10)
    return parser.parse_args()

def post_detail_parser():
    """详情页参数解析"""
    parser = reqparse.RequestParser()
    parser.add_argument('post_id', type=int, location='args', required=True, help=u'帖子ID必传')
    return parser.parse_args()

def post_publish_parser():
    """发布帖子参数解析器"""
    parser = reqparse.RequestParser()

    parser.add_argument('title', type=str, location='form', required=True, help="标题不能为空")
    parser.add_argument('content', type=str, location='form', required=True, help="内容不能为空")

    parser.add_argument('is_public', type=int, location='form', default=1)
    parser.add_argument('images', type=werkzeug.datastructures.FileStorage, location='files', action='append', required=False, help="帖子图片")
    
    return parser.parse_args()

def post_delete_parser():
    parser = reqparse.RequestParser()
    # 删帖通常通过 URL 参数或 JSON 传参
    parser.add_argument('post_id', type=int, required=True, location=['json', 'args'], help="帖子ID不能为空")
    return parser.parse_args()

def post_update_parser(): 
    """修改帖子参数解析器 (仅限文本和状态)"""
    parser = reqparse.RequestParser()
    # 帖子ID必须传
    parser.add_argument('post_id', type=int, required=True, location='json', help="帖子ID不能为空")
    
    # 以下为可选修改字段
    parser.add_argument('title', type=str, location='json')
    parser.add_argument('content', type=str, location='json')
    parser.add_argument('is_public', type=int, location='json') # 1:公开, 0:私密
    
    return parser.parse_args()

def post_interact_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('post_id', type=int, location='json', required=True)
    parser.add_argument('content', type=str, location='json') # 仅评论需要
    return parser.parse_args()

def log_list_parser():
    """解析日志列表查询参数"""
    parser = reqparse.RequestParser()
    # 分页参数
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=15, location='args')
    # 筛选参数
    parser.add_argument('module', type=str, location='args')     # 按模块筛选
    parser.add_argument('admin_id', type=int, location='args')   # 按管理员ID筛选
    parser.add_argument('status', type=int, location='args')     # 1-成功, 0-失败

    parser.add_argument('keyword', type=str, location='args') 
    return parser.parse_args()

def creator_apply_parser():
    """用户提交申请参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('real_name', type=str, required=True, location='json', help='真实姓名不能为空')
    parser.add_argument('specialty', type=str, required=True, location='json', help='专业领域不能为空')
    parser.add_argument('reason', type=str, location='json')
    parser.add_argument('evidence_url', type=str, location='json')
    return parser.parse_args()

def creator_audit_parser():
    """管理员审核参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('application_id', type=int, required=True, location='json')
    parser.add_argument('status', type=int, required=True, location='json') # 1-通过, 2-驳回
    parser.add_argument('admin_comment', type=str, location='json')
    return parser.parse_args()

def creator_id_parser():
    """解析申请ID参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('application_id', type=int, required=True, location='args', help='申请ID不能为空')
    return parser.parse_args()

def admin_user_list_parser():
    """解析管理员查询用户列表的参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1, location='args')
    parser.add_argument('per_page', type=int, default=10, location='args')
    # 筛选参数
    parser.add_argument('role_type', type=str, location='args') # 1-群众, 2-专家, 3-管理
    parser.add_argument('status', type=int, location='args')    # 1-正常, 0-禁用
    parser.add_argument('keyword', type=str, location='args')   # 搜索账号或昵称
    return parser.parse_args()

def admin_user_query_parser():
    """解析查询特定用户详情的参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=True, location='args', help='用户ID不能为空')
    return parser.parse_args()

def admin_user_manage_parser():
    """解析管理员管理用户账号的参数"""
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=True, location='json')
    # 可选修改项
    parser.add_argument('status', type=int, location='json')    # 1-正常, 0-禁用
    parser.add_argument('role_type', type=str, location='json') # 1, 2, 3
    parser.add_argument('remark', type=str, location='json')    # 管理备注（用于日志）
    return parser.parse_args()

def achievement_query_parser():
    """解析成就列表查询参数"""
    parser = reqparse.RequestParser()
    # 想要查看的目标用户ID
    parser.add_argument('user_id', type=int, location='args')
    return parser.parse_args()

# 兼容性/通用 解析器 (防止旧的 import 报错)
def sign_up_parser():
    """普通用户注册(保留以防报错)"""
    parser = reqparse.RequestParser()
    parser.add_argument('mobile', type=is_mobile, location='json', required=True, help=u'手机号')
    parser.add_argument('name', type=str, location='json', required=False)
    parser.add_argument('password', type=str, location='json', required=False)
    return parser.parse_args()

def sign_in_wapplet_parser():
    """小程序登录(保留以防报错)"""
    parser = reqparse.RequestParser()
    parser.add_argument('code', type=str, location='json', required=True)
    parser.add_argument('encryptedData', type=str, location='json')
    parser.add_argument('iv', type=str, location='json')
    parser.add_argument('nickName', type=str, location='json')
    return parser.parse_args()

def login_parser():
    """通用登录(保留以防报错)"""
    parser = reqparse.RequestParser()
    parser.add_argument('mobile', type=str, required=True, location='json')
    parser.add_argument('password', type=str, required=True, location='json')
    return parser.parse_args()

def userBeginOnPage_parser():
    """埋点相关(保留以防报错)"""
    parser = reqparse.RequestParser()
    parser.add_argument('beginTime', type=str, location='json')
    return parser.parse_args()

def user_parser(method='post'):
    """通用用户查询(保留以防报错)"""
    parser = reqparse.RequestParser()
    if method == 'get':
        parser.add_argument('participant_id', type=str, location='args')
    return parser.parse_args()

def test_parser():
    """
    测试用参数解析器 (兼容旧代码)
    """
    # 确保文件顶部导入了 reqparse
    # from flask_restful import reqparse 
    
    parser = reqparse.RequestParser()
    parser.add_argument('foo', type=int, location=['json', 'args'], required=False, help=u'The foo')
    parser.add_argument('pw', type=str, location=['json', 'args'], required=False, help=u'The pw')
    return parser.parse_args()