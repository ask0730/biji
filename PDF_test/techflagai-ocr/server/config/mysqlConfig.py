class MysqlConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://your_username:your_ip:3306/ocr_recovery'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'init_command': "SET time_zone='+08:00';"}}


