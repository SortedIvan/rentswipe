from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME = "rentswipeservice",
    MAIL_PASSWORD = "pqxlqnaydtkffofy",
    MAIL_FROM = "rentswipeservice@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME= "Rentswipe",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS= False
)

