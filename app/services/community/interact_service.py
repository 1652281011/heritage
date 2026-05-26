import time
from app.models import db
from app.models.community import Post, Like, Comment
from app.models.users import User

class InteractService:
    @staticmethod
    def toggle_like(post_id, user_id):
        post = Post.query.get(post_id)
        if not post:
            return False, "POST_NOT_FOUND"

        # 2. 检查该用户是否已经点过赞
        like_record = Like.query.filter_by(post_id=post_id, user_id=user_id).first()

        if like_record:
            # --- 场景：取消点赞 ---
            db.session.delete(like_record)
            post.like_count = max(0, post.like_count - 1)
            action_status = "UNLIKE"
        else:
            # --- 场景：点赞成功 ---
            new_like = Like(
                post_id=post_id, 
                user_id=user_id, 
                c_time=int(time.time())
            )
            db.session.add(new_like)
            post.like_count += 1
            action_status = "LIKE"

        # 3. 提交数据库
        try:
            db.session.commit()
            # 返回当前点赞总数和动作类型
            return True, {"count": post.like_count, "action": action_status}
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def add_comment(post_id, user_id, content):
        post = Post.query.get(post_id)
        if not post: return False, "帖子不存在"
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        post.comment_count += 1
        db.session.add(comment)
        db.session.commit()
        return True, comment.to_dict()