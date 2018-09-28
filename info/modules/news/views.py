from flask import current_app, abort, render_template

from info.models import News
from info.modules.news import news_blu

@news_blu.route('/<int:news_id>')
def news_datail(news_id):

    # 根据新闻id查询该新闻的所有数据
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(404)

    return render_template("detail.html", news=news.to_dict())