from hmac import digest_size

from flask import g, redirect, render_template, request, jsonify, abort, current_app

from info import db
from info.common import user_login_data, img_upload
from info.constants import USER_COLLECTION_MAX_NEWS, QINIU_DOMIN_PREFIX
from info.models import tb_user_collection, Category, News
from info.utils.response_code import RET, error_map
from . import user_blu


@user_blu.route('/user_info')
@user_login_data
def user_info():
    """个人中心"""
    user = g.user
    if not user:
        return redirect('/')

    return render_template("user/user.html", user=user.to_dict())


@user_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    """显示基本信息"""

    user = g.user
    if not user:
        return abort(403)
    if request.method == "GET":
        return render_template("user/user_base_info.html", user=user.to_dict())

    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 修改用户模型
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@user_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    """头像设置"""
    user = g.user
    if not user:
        return abort(403)
    if request.method == "GET":
        return render_template("user/user_pic_info.html", user=user.to_dict())

    try:
        img_bytes = request.files.get("avatar").read()

        # 将文件上传到文件服务器
        try:
            file_name = img_upload(img_bytes)
            user.avatar_url = file_name
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_dict())


@user_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    """修改密码"""

    user = g.user
    if not user:
        return abort(403)
    if request.method == "GET":
        return render_template("user/user_pass_info.html", user=user.to_dict())

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    user.password = new_password

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@user_blu.route('/collection')
@user_login_data
def collection():
    user = g.user
    if not user:
        return abort(403)

    # 获取当前页码
    p = request.args.get("p", 1)

    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)

    # 查询当前用户收藏的所有页码,指定页码
    news_list = []
    cur_page = 1
    total_page = 1
    try:
        pn = user.collection_news.order_by(tb_user_collection.c.create_time.desc()).paginate(p, USER_COLLECTION_MAX_NEWS)
        news_list = [news.to_dict() for news in pn.items]
        cur_page = pn.page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    data = {
        "news_list": news_list,
        "cur_page": cur_page,
        "total_page": total_page
    }
    return render_template("user/user_collection.html", data=data)


@user_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():
    """发布文章"""

    user = g.user
    if not user:
        return abort(403)
    if request.method == "GET":
        # 查询所有的分类信息
        categories = []
        try:
            categories = Category.query.all()
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

        if len(categories):
            categories.pop(0)

        return render_template("user/user_news_release.html", categories=categories)

    # 获取参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    contnet = request.form.get("content")
    if not all([title, category_id, digest, contnet]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        category_id = int(category_id)
    except BaseException as e:
        current_app.logger.error(e)

    # 生成新闻模型
    news = News()
    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.content = contnet
    news.source = "个人发布"
    news.user_id = user.id
    news.status = 1

    try:
        img_bytes = request.files.get("index_image").read()
        file_name = img_upload(img_bytes)
        news.index_image_url = QINIU_DOMIN_PREFIX + file_name
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    db.session.add(news)

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@user_blu.route('/news_list')
@user_login_data
def news_list():
    user = g.user
    if not user:
        return abort(403)

    # 获取当前页码
    p = request.args.get("p", 1)

    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)

    # 查询当前用户收藏的所有页码,指定页码
    news_list = []
    cur_page = 1
    total_page = 1
    try:
        pn = user.news_list.order_by(News.create_time.desc()).paginate(p, USER_COLLECTION_MAX_NEWS)
        news_list = [news.to_review_dict() for news in pn.items]
        cur_page = pn.page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)

    data = {
        "news_list": news_list,
        "cur_page": cur_page,
        "total_page": total_page
    }
    return render_template("user/user_news_list.html", data=data)


@user_blu.route('/user_follow')
@user_login_data
def user_follow():

    user = g.user
    if not user:
        return abort(403)

    # 获取当前页码
    p = request.args.get("p", 1)

    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)

    # 查询当前用户关注的所有作者,指定页码
    author_list = []
    cur_page = 1
    total_page = 1
    try:
        pn = user.followed.paginate(p, USER_COLLECTION_MAX_NEWS)
        author_list = [author.to_dict() for author in pn.items]
        cur_page = pn.page
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)

    data = {
        "author_list": author_list,
        "cur_page": cur_page,
        "total_page": total_page
    }
    return render_template("user/user_follow.html", data=data)

















