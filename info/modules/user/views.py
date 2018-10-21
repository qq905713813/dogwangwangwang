from flask import current_app
from flask import g,redirect,render_template, jsonify
from flask import request

from info import constants, db
from info.models import Category, News
from info.utils.commons import user_login_data
from info.utils.image_storage import image_storage
from info.utils.response_code import RET
from . import user_blue


# 功能描述：新闻发布
# 请求路径：/user/news_release
# 请求方式：GET,POST
# 请求参数：GET无，POST， title,category_id,digest,index_image,content
# 返回值：GET请求，user_news_release.html，data分类列表字段数据,POST,errno,errmsg
@user_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    """
    1.判断是否是GET请求，携带分类数据展示
    2.如果是POST，获取参数
    3.校验参数，为空校验
    4.判断图片是否上传成功
    5.创建新闻镀锡，设置新闻属性
    6.保存到数据库
    7.返回响应
    :return:
    """
    # 1.判断是否是GET请求，携带分类数据展示
    if request.method == "GET":
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            current_app.logger(e)
            return jsonify(errno=RET.DBERR,errmsg="获取分类失败")

        # 分类对象列表，转字典列表
        category_list = []
        for category in categories:
            category_list.append(category)

        return render_template("news/user_news_release.html",categories=category_list)

    # 2.如果是POST，获取参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    # 3.校验参数，为空校验
    if not all([title,category_id,digest,content]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")
    # # 上传图片
        pass

    # 4.判断图片是否上传成功
        pass
    # 5.创建新闻属性，设置新闻属性
    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.digest = digest
    # news.index_image_url = constants.QINIU_DOMIN_PREFIX + index_image
    news.index_image_url = "没有图片"
    news.content = content
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1 # 表示正审核中

    # 6.保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="新闻发布失败")
    # 7.返回响应
    return jsonify(errno=RET.OK,errmsg="发布成功")








# 功能描述：上传图片
# 请求路径：/user/pic_info
# 请求方式：POST,GET
# 请求参数：无，POST有参数，avatar
# 返回值：GET请求，user_pci_info.html页面,data字典数据，POST请求：errno,errmsg,avatar_url
@user_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    """
    1.判断请求方式，如果是GET，渲染页面，携带用户数据
    2.如果是POST请求，获取参数
    3.校验参数，为空校验
    4.上传图片
    5.判断是否上传成功
    6.设置图片到用户对象
    7.返回响应，携带图片

    :return:
    """
    # 1.判断请求方式，如果是GET,渲染界面，携带用户数据
    if request.method == "GET":
        return render_template("news/user_pic_info.html",user=g.user.to_dict())

    # 2.如果是POST请求，获取参数
    avatar = request.files.get("avatar")

    # 3.校验参数，为空校验
    if not avatar:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 4.上传图片
    try:
        image_name = image_storage(avatar.read())
    except Exception as e:
        # current_app.logger(e)
        return jsonify(errno=RET.THIRDERR,errmsg="七牛云异常")

    # 5.判断是否上传成功
    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg="上传失败")

    # 6.设置图片到用户对象
    g.user.avatar_url = image_name

    # 7.返回响应，携带图片
    data = {
        "avatar":constants.QINIU_DOMIN_PREFIX + image_name
    }
    return jsonify(errno=RET.OK,errmsg="上传成功",data=data)





# 功能描述：密码修改
# 请求路径：/user/pass_info
# 请求方式：GET,POST
# 请求参数：GET无，POST有参数,old_password,new_password
# 返回值：GET请求：user_pass_info.html页面，data字典数据；POST请求：errno,errmsg

@user_blue.route('/pass_info', methods=['GET','POST'])
@user_login_data
def pass_info():
    """
    1.判断请求方式
    2.如果式POST请求，获取参数
    3.为空校验
    4.判断旧密码是否正确
    5.修改新密码
    6.返回响应
    :return:
    """
    # 1.判断请求方式，如果是GET，渲染页面
    if request.method == "GET":
        return render_template("news/user_pass_info.html")
    # 2.如果是POST请求，获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    # 3.为空校验
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 4.判断旧密码是否正确
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR,errmsg="旧密码错误")
    # 5.修改新密码
    g.user.password = new_password

    # 6.返回响应
    return jsonify(errno=RET.OK,errmsg="修改成功")



# 功能描述：展示基本资料信息
# 请求描述：/user/base_info
# 请求方式：GER,POST
# 请求参数：POST请求参数，nick_name.signature,gender
# 返回值：errno,errmsg
@user_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    # 1.判断如果是GET,携带用户数据，渲染页面
    if request.method == "GET":
        return render_template("news/user_base_info.html",user=g.user.to_dict())
    # 2.如果是POST请求，获取参数
    # 2.1 获取参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 2.2 校验参数，为空校验
    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 2.3 性别类型校验
    if gender not in ["MAN","WOMAN"]:
        return jsonify(errno=RET.DATAERR,errmsg="性别异常")

    # 2.4 修改用户信息
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    # 2.5 返回响应
    return jsonify(errno=RET.OK,errmsg="修改成功")






# 功能: 获取用户个人中心页面
# 请求路径: /user/info
# 请求方式:GET
# 请求参数:无
# 返回值: user.html页面,用户字典data数据
@user_blue.route('/info')
@user_login_data
def user_info():
    # 判断用户是否有登陆
    if not g.user:
        return redirect("/")

    # 拼接数据，渲染页面
    data = {
        "user_info":g.user.to_dict()

    }
    return render_template("news/user.html",data=data)