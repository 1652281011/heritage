#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 下午11:03
# @Software：PyCharm
# @Author  : scott

from app.api.v1.apps.achievement.achievements import AchievementAtlasResource
from app.api.v1.apps.achievement.my_achievement import UserEarnedAchievementResource
from app.api.v1.apps.collecct.collect import HeritageCollectResource
from app.api.v1.apps.collecct.list import HeritageCollectListResource
from app.api.v1.apps.community.mylikepost import MyLikedPostResource
from app.api.v1.apps.community.mypostlist import MyPostListResource
from app.api.v1.apps.community.post_comment import CommentResource
from app.api.v1.apps.community.post_delete import PostDeleteResource
from app.api.v1.apps.community.post_detail import PostDetailResource
from app.api.v1.apps.community.post_like import LikeResource
from app.api.v1.apps.community.post_list import PostListResource
from app.api.v1.apps.community.post_publish import PostPublish
from app.api.v1.apps.community.post_update import PostUpdateResource
from app.api.v1.apps.datetime.datetime import DateTime
# from app.api.v1.apps.break_record.break_record import BreakRecord, GameUserRanking, UsersHistoryRecord, \
#     UsersHistoryRecordInfo


from app.api.v1.apps.game.game_record import InteractionFileResultResource
from app.api.v1.apps.game.interactive_history import UserRecentGamesResource
from app.api.v1.apps.heritage.admin_manage import AdminHeritageDirectResource
from app.api.v1.apps.heritage.audit import HeritageRequestAuditResource
from app.api.v1.apps.heritage.audit_detail import HeritageRequestDetailResource
from app.api.v1.apps.heritage.audit_list import AdminHeritageRequestListResource
from app.api.v1.apps.heritage.brow_history import UserBrowsingHistoryResource
from app.api.v1.apps.heritage.cancle import HeritageRequestCancelResource
from app.api.v1.apps.heritage.delete import HeritageDeleteResource
from app.api.v1.apps.heritage.heritage_detail import HeritageDetailResource
from app.api.v1.apps.heritage.heritage_list import HeritageListResource
from app.api.v1.apps.heritage.heritage_submit import HeritageRequestSubmitResource
from app.api.v1.apps.heritage.user_audit_list import UserMyHeritageRequestResource
from app.api.v1.apps.interaction.audit_list import AdminInteractionAuditListResource
from app.api.v1.apps.interaction.cancle import InteractionCancelResource
from app.api.v1.apps.interaction.check_list import ExpertMyInteractionListResource
from app.api.v1.apps.interaction.interaction_contribute import InteractionContributeResource
from app.api.v1.apps.interaction.interaction_review import InteractionReviewResource
from app.api.v1.apps.interaction.launch_list import HeritageInteractionListResource
from app.api.v1.apps.interaction.manage_interaction import ManageInteractionDetailResource
from app.api.v1.apps.interaction.update import ExpertInteractionUpdateResource
from app.api.v1.apps.interaction.user_interaction import InteractionDetailResource
from app.api.v1.apps.log.admin_log import AdminLogListResource
from app.api.v1.apps.map.add_element import ElementAddResource
from app.api.v1.apps.map.complete import HeritageAllCompletionResource
from app.api.v1.apps.map.element import ElementListResource
from app.api.v1.apps.map.unbond_list import UnboundHeritageResource
from app.api.v1.apps.map.update import ElementUpdateResource
from app.api.v1.apps.question.admin_submit import AdminQuestionDirectResource
from app.api.v1.apps.question.answer_verify import AnswerVerifyResource
from app.api.v1.apps.question.audit import QuestionRequestAuditResource
from app.api.v1.apps.question.audit_list import QuestionRequestListResource
from app.api.v1.apps.question.cancle import QuestionRequestCancelResource
from app.api.v1.apps.question.delete_question import AdminQuestionDeleteResource
from app.api.v1.apps.question.detail import QuestionDetailResource
from app.api.v1.apps.question.req_detail import QuestionRequestDetailResource
from app.api.v1.apps.question.finished_list import UserFinishedHeritageResource
from app.api.v1.apps.question.question_list import AdminQuestionListResource
from app.api.v1.apps.question.question_submit import QuestionRequestSubmitResource
from app.api.v1.apps.question.quiz_record import QuizCompleteResource
from app.api.v1.apps.question.random_question import QuestionRandomResource
from app.api.v1.apps.user.account_manage import AdminUserManageResource
from app.api.v1.apps.user.apply import CreatorApplyResource
from app.api.v1.apps.user.apply_detail import AdminCreatorDetailResource
from app.api.v1.apps.user.apply_progress import CreatorProgressResource
from app.api.v1.apps.user.audit_apply import CreatorAuditResource
from app.api.v1.apps.user.checkin import CheckInResource
from app.api.v1.apps.user.detail_info import UserDetailResource
from app.api.v1.apps.user.register import Register
from app.api.v1.apps.user.sign_in import SignIn
from app.api.v1.apps.user.update_info import UserInfoResource
from app.api.v1.apps.user.update_password import UserPasswordResource
from app.api.v1.apps.user.user_list import AdminUserListResource
from app.api.v1.apps.work.change_name import UserWorkNameUpdateResource
from app.api.v1.apps.work.delete import UserWorkDeleteResource
from app.api.v1.apps.work.download import UserWorkDownloadResource
from app.api.v1.apps.work.work_list import UserWorkSearchResource

RESOURCES = [

    (DateTime, '/v1/date-time'),#获取服务器的时间

    (Register, '/v1/user/register'),
    (SignIn, '/v1/user/sign-in'),
    (UserDetailResource, '/v1/user/detail'),

    (CheckInResource, '/v1/user/checkin'),

    (UserInfoResource, '/v1/user/updinfo'),
    (UserPasswordResource, '/v1/user/updpwd'),

    (AdminUserListResource, '/v1/admin/users'),

    (CreatorApplyResource, '/v1/user/apply'),
    (CreatorProgressResource, '/v1/user/applyprogress'),
    (AdminCreatorDetailResource, '/v1/admin/applydetail'),
    (CreatorAuditResource, '/v1/admin/auditapply'),
    (AdminUserManageResource, '/v1/admin/manage'),

    (AdminLogListResource, '/v1/admin/log'),
    
    (HeritageListResource, '/v1/heritage/list'),
    (HeritageDetailResource, '/v1/heritage/detail'),

    (HeritageRequestSubmitResource, '/v1/heritage/submit'),
    (UserMyHeritageRequestResource, '/v1/heritage/auditlist'),
    (AdminHeritageRequestListResource, '/v1/heritage/adminlist'),
    (HeritageRequestDetailResource, '/v1/heritage/auditdetail'),
    (HeritageRequestAuditResource, '/v1/heritage/audit'),
    (HeritageRequestCancelResource, '/v1/heritage/cancle'),
    (AdminHeritageDirectResource, '/v1/heritage/adminsubmit'),
    (HeritageDeleteResource, '/v1/heritage/delete'),

    (HeritageCollectResource, '/v1/heritage/collect'),
    (HeritageCollectListResource, '/v1/heritage/collectlist'),

    (UserBrowsingHistoryResource, '/v1/user/heritage/history'),

    (QuestionRandomResource, '/v1/question/problem'),
    (AnswerVerifyResource, '/v1/question/check'),

    (QuizCompleteResource, '/v1/question/record'),

    (UserFinishedHeritageResource, '/v1/question/finishedlist'),

    (QuestionRequestSubmitResource, '/v1/question/submit'),
    (QuestionRequestListResource, '/v1/question/auditlist'),
    (QuestionRequestAuditResource, '/v1/question/audit'),
    (QuestionRequestDetailResource, '/v1/question/auditdetail'),
    (AdminQuestionDirectResource, '/v1/question/adminsubmit'),
    (QuestionRequestCancelResource, '/v1/question/cancle'),
    (AdminQuestionListResource, '/v1/question/allquestion'),
    (AdminQuestionDeleteResource, '/v1/question/delete'),
    (QuestionDetailResource, '/v1/question/detail'),

    (PostListResource, '/v1/community/postlist'),
    (PostPublish, '/v1/community/postpublish'),
    (PostDeleteResource,'/v1/community/postdelete'),
    (PostUpdateResource, '/v1/community/postupdate'),
    (PostDetailResource, '/v1/community/postdetail'),
    (MyPostListResource, '/v1/community/myposts'),
    (MyLikedPostResource, '/v1/community/myliked'),
    (LikeResource, '/v1/community/like'),
    (CommentResource, '/v1/community/comment'),

    (InteractionContributeResource, '/v1/interact/submit'),
    (ExpertInteractionUpdateResource, '/v1/interact/update'),
    (AdminInteractionAuditListResource, '/v1/interact/auditlist'),
    (InteractionReviewResource, '/v1/interact/audit'),
    (ExpertMyInteractionListResource, '/v1/interact/mysubmit'),
    (ManageInteractionDetailResource, '/v1/interact/managedetail'),
    (HeritageInteractionListResource, '/v1/interact/launch'),
    (InteractionCancelResource, '/v1/interact/cancle'),
    (InteractionDetailResource, '/v1/interact/userdetail'),

    (InteractionFileResultResource, '/v1/game/finish'),

    (UserRecentGamesResource, '/v1/user/game/history'),

    (UserWorkSearchResource, '/v1/work/list'),
    (UserWorkNameUpdateResource, '/v1/work/updname'),
    (UserWorkDeleteResource, '/v1/work/delete'),
    (UserWorkDownloadResource, '/v1/work/download'),

    (AchievementAtlasResource, '/v1/achievement/list'),
    (UserEarnedAchievementResource, '/v1/user/achiecement'),

    (HeritageAllCompletionResource, '/v1/map/list'),
    (ElementListResource, '/v1/map/element'),
    (ElementAddResource, '/v1/map/addelement'),
    (UnboundHeritageResource, '/v1/map/unbond'),
    (ElementUpdateResource, '/v1/map/update')
]
