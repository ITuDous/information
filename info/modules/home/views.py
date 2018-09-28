from info.constants import CLICK_RANK_MAX_NEWS, HOME_PAGE_MAX_NEWS
from info.models import User, News, Category
from info.utils.response_code import RET, error_map
from . import home_blu
from flask import current_app, render_template, session, request, jsonify


@home_blu.route('/')
def index():
    # 判断用户是否登陆,看session中是否保存了user_id
    user_id = session.get("user_id")
    user = None
    if user_id:
        # 根据user_id获取用户信息
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)

    user = user.to_dict() if user else None

    # 查询点击量排行前十的新闻
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.lgger.error(e)

    news_list = [news.to_dict() for news in news_list]

    # 查询所有的分类信息
    categories = []
    try:
        categories = Category.query.all()
    except BaseException as e:
        current_app.logger.error(e)

    # 将用户信息传入模板,进行模板渲染
    return render_template("index.html", user=user, news_list=news_list, categories=categories)


@home_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")


@home_blu.route('/get_news_list')
def get_news_list():
    # 获取参数
    cid = request.args.get("cid")  # 分类id
    cur_page = request.args.get("cur_page")  # 当前页码
    per_count = request.args.get("per_count", HOME_PAGE_MAX_NEWS)  # 每页条数
    # 校验参数
    if not all([cid, cur_page]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 格式转换
    try:
        cid = int(cid)
        cur_page = int(cur_page)
        per_count = int(per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 判断分类id是否等于1
    filter_list = []
    if cid != 1:
        filter_list.append(News.category_id == cid)

    # 根据参数查询目标新闻
    try:
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page, per_count)
    except BaseException as e:
        return jsonify(error=RET.DBERR, errmsg=error_map[RET.DBERR])

    data = {
        "news_list": [news.to_basic_dict() for news in pn.items],
        "total_page": pn.pages
    }

    # 将新闻包装为json并返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=data)
