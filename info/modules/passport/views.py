import re

from info.utils.response_code import RET, error_map
from . import passport_blu
from info import redis_store
from flask import request, abort, current_app, make_response, Response, jsonify

#  获取图片验证码
from info.utils.captcha.pic_captcha import captcha


@passport_blu.route('/get_img_code')
def get_img_code():
    #  获取参数
    img_code_id = request.args.get("img_code_id")
    #  校验参数
    if not img_code_id:
        return abort(403)

    #  生成图片验证码
    img_name, img_text, img_bytes = captcha.generate_captcha()

    #  保存图片key和验证文字
    try:
        redis_store.set("img_code_id" + img_code_id, img_text, ex=180)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(500)

    #  设置自定义的响应头
    response = make_response(img_bytes)
    response.content_type = "image/jpeg"
    #  返回验证码图片
    return response


@passport_blu.route('/get_sms_code', methods=['POST'])
def get_sms_code():
    #  获取参数
    mobile = request.json.get("mobile")
    img_code = request.json.get("img_code")
    img_code_id = request.json.get("img_code_id")
    #  校验参数
    if not all([mobile, img_code, img_code_id]):
        #  返回自定义的错误信息
        return jsonify(error=RET.PARAMERR)

    #  校验手机号格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(error=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    #  根据手机号取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_id"+mobile)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
