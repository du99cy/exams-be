from re import TEMPLATE
from fastapi_mail import ConnectionConfig

MONGO_DETAILS = "mongodb://127.0.0.1:27017"
API_URL = "http://118.70.48.144:9920"
DATABASE_NAME = 'online_exam'
TIMEOUT_CONNECTIONS_TO_DATABASE = 5000

EMAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME="du321999cy@gmail.com",
    MAIL_PASSWORD="NguyenQuangDu1999cY",
    MAIL_FROM="du321999cy@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

TEMPLATE_EMAIL = """
     <html>
        <body>
         
 
        <h1>Chào {user_name} !!!</h1>
        <br>
        <h3>Cảm ơn đã đăng ký là thành viên đến hệ thống của Công ty AI Academy</h3>
        <img src="https://aiacademy.edu.vn/assets/images/logo.jpg">
        <div style="margin:20px 0;font-size:14px;">
            <a href="{activate_link}">Hãy nhân vào đây để kích hoạt tài khoản</a>
        </div>
        </body>
        </html>
"""

FORGOT_PASSWORD_EMAIL_TEMP = """
    <html>
        <body>
         
 
        
        <br>
        <h3>Cảm ơn đã đăng ký là thành viên đến hệ thống của Công ty AI Academy</h3>
        <img src="https://aiacademy.edu.vn/assets/images/logo.jpg">
        <div style="margin:20px 0;font-size:14px;">
            Mật khẩu mới của bạn là : <strong>{new_password}</strong>
        </div>
        </body>
        </html>
"""
# for auth
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

AVATAR_PIC_DEFAULT = 'static-files/avatar_pic_default.jpg'

CONFIRM_TOKEN_URL = "http://localhost:4200/confirm-token/{token}"

FACEBOOK_GRAPH_API_URL = 'https://graph.facebook.com/v8.0/me?fields=first_name,last_name,picture&access_token={access_token}'