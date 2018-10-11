from flask import current_app, abort, render_template, g, request, jsonify

from info import db
from info.common import user_login_data
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, Comment, User
from info.modules.news import news_blu
from info.utils.response_code import RET, error_map


# 详情页面
@news_blu.route('/<int:news_id>')
@user_login_data  # news_detail = user_login_data(news_detail)
def news_detail(news_id):
    # 根据新闻id查询该新闻所有的数据
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(404)

    # 点击量+1
    news.clicks += 1

    # 查询`点击量排行前10的新闻`
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.logger.error(e)

    news_list = [news.to_basic_dict() for news in news_list]

    user = g.user
    is_collect = False
    if user:
        # 查询`当前用户是否收藏了该新闻`, 将情况传入模板, 模板渲染
        if news in user.collection_news:
            is_collect = True

    # `查询该新闻的所有评论`(生成日期倒序), 再进行`模板渲染`
    try:
        comments = news.comments.order_by(Comment.create_time.desc()).all()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    comment_list = []

    for comment in comments:
        comment_dict = comment.to_dict()
        is_like = False
        # 判断哪些评论被”我”点过赞
        if user:  # 如果该用户已登录
            if comment in user.like_comments:
                is_like = True

        comment_dict["is_like"] = is_like
        comment_list.append(comment_dict)

    # 判断用户是否登陆,并且判断是否有作者
    is_followed = False
    if user and news.user_id:

        if news.user in user.followed:
            is_followed = True

    user = user.to_dict() if user else None

    # 将数据传入模板, 进行模板渲染
    return render_template("news/detail.html", news=news.to_dict(), news_list=news_list, user=user,
                           is_collect=is_collect,
                           comments=comment_list, is_followed=is_followed)


# 新闻收藏
@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 校验参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 判断该新闻是否存在
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action执行收藏/取消收藏(user和news建立/删除关系)
    if action == "collect":  # 收藏
        # 让user和news建立关系
        user.collection_news.append(news)
    else:  # 取消收藏
        user.collection_news.remove(news)

    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 评论/回复
@news_blu.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_content = request.json.get("comment")
    news_id = request.json.get("news_id")
    parent_id = request.json.get("parent_id")
    # 校验参数
    if not all([comment_content, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 生成一个评论数据, 添加到数据库中
    comment = Comment()
    comment.content = comment_content
    comment.news_id = news_id
    comment.user_id = user.id
    if parent_id:  # 子评论
        try:
            parent_id = int(parent_id)
            comment.parent_id = parent_id
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        db.session.add(comment)
        db.session.commit()  # 此处必须手动提交, 否则不生成评论id, 前端就获取不到评论id
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=comment.to_dict())


# 评论点赞
@news_blu.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    # 校验参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        comment_id = int(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 判断该评论是否存在
    try:
        comment = Comment.query.get(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action执行点赞/取消点赞(user和comment建立/删除关系)
    if action == "add":  # 点赞
        # 让user和news建立关系
        user.like_comments.append(comment)
        comment.like_count += 1
    else:  # 取消点赞
        user.like_comments.remove(comment)
        comment.like_count -= 1

    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@news_blu.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    # 判断用户是否登录
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    user_id = request.json.get("user_id")
    action = request.json.get("action")
    # 校验参数
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        user_id = int(user_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 判断该作者是否存在
    try:
        author = User.query.get(user_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not author:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["follow", "unfollow"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据action执行关注/取消关注(user和author建立/删除关系)
    if action == "follow":  # 关注
        # 让user和author建立关系
        user.followed.append(author)
    else:  # 取消关注
        user.followed.remove(author)

    # json返回结果
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
