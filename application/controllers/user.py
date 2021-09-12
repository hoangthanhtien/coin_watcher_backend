from gatco.response import json
from application.server import app
from application.database import db
from application.extensions import auth
from application.models.model import User
from application.controllers import generate_random_string
from application.config import Config
from application.controllers.helpers import send_email
from sqlalchemy import or_
import ujson
from application.database import redis_db


async def create_user(data=None):
    """Tạo user khi user đăng ký
    :param dict data: Thông tin user 
    """

    user_name = data.get("user_name")
    full_name = data.get("full_name") 
    email = data.get("email")
    password = data.get("password")

    user_existed = db.session.query(User).filter(User.email == email).first()
    if not user_existed:
        user_salt = generate_random_string(length=64, type="lowercase")
        user_password = auth.encrypt_password(password, user_salt)
        new_user = User()
        new_user.email = email
        new_user.user_name = user_name
        new_user.full_name = full_name
        new_user.salt = user_salt
        new_user.password = user_password 
        db.session.add(new_user)
        db.session.commit()
        return new_user 
    else:
        return json(Config.DUPLICATE_EMAIL_ERR, 409)


@app.route("/test_welcome_email", methods=["GET"])
async def test_mail(request):
    email_sent = await send_email(['hoangthanhtien0604@gmail.com'],'welcome') 
    if email_sent:
        return json({'messsage':"Gửi email thành công"},200)

@app.route("/user/register", methods=["POST"])
async def user_register(request):
    if request.method == "POST":
        """
        request body example:
        {
            "user_name":"tienvjppro",
            "email":"hoangthanhtien0604@gmail.com",
            "password":"thisissomedumbpassword",
            "full_name":"Hoàng Thành Tiến"
        }
        """
        data = request.json
        user_name = data.get("user_name")
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name")
        if not data or not email or not full_name or not password:
            return json(Config.BAD_REQUEST_ERR, 400)
        else:
            data = {
                "user_name":user_name,
                "email":email,
                "password":password,
                "full_name":full_name
            }
            new_user = await create_user(data)
            if new_user:
                sent_welcome_email = await send_email([email],'welcome') 
                if sent_welcome_email: 
                    return json({"message":"Đăng ký user thành công, kiểm tra email của bạn để kích hoạt tài khoản"}, 200)
                else:
                    return json({})
    else:
        return json(Config.METHOD_NOT_ALLOW_ERR, 405)

async def create_access_token(user_data):
    access_token = generate_random_string(length=64, type='letters') 
    redis_db.set(access_token, ujson.dumps(user_data),ex=43200)
    return access_token


@app.route("/user/login", methods=["POST", "GET"])
async def user_login(request):
    param = request.json
    user_name = param.get("user_name")
    password = param.get("password")
    email = param.get("email")
    if (email and password) or (user_name and password):
        user = db.session.query(User).filter(or_(User.user_name == user_name, User.email == email)).first()
        if (user is not None) and auth.verify_password(password, user.password, user.salt):
            auth.login_user(request, user)
            user_info = {"id": user.id, "user_name": user.user_name, "full_name": user.full_name}
            access_token = await create_access_token(user_data=user_info)
            user_info['access_token'] = access_token
            return json(user_info,200)
        return json(Config.LOGIN_ERR, status=520)

    else:
        return json(Config.BAD_REQUEST_ERR, status=400)

@app.route("/user/logout", methods=["GET"])
async def user_logout(request):
    access_token = request.headers.get("access_token") 
    redis_db.delete(access_token)
    auth.logout_user(request)
    return json({})

@app.route("/user/current_user", methods=["GET"])
async def user_current_user(request):
    user_id = auth.current_user(request)
    print(user_id)

    user = User.query.filter(User.id == user_id).first()
    if user is not None:
        print(user.full_name)
        return json({"id": user.id, "user_name": user.user_name, "full_name": user.full_name})
    else:
        return json({"error_code": "NOT_FOUND", "error_message": "User not found"}, status=520)

