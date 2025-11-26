class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///vehicle_parking.sqlite3"
    JWT_SECRET_KEY = "2f8b51a28371090fb2d7b1377489814c"