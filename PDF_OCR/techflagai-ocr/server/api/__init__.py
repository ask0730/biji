# -*- coding: utf-8 -*-
import importlib
import logging
import os
from pathlib import Path
from flask import Flask, current_app # Ensure current_app is imported if used elsewhere, though not strictly needed for _config fix
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask import send_from_directory, abort
from urllib.parse import unquote
import os
import traceback
from werkzeug.exceptions import HTTPException # <--- 添加导入
from config.mysqlConfig import MysqlConfig
from config.jwtConfig import JwtConfig
from config.otherConfig import OtherConfig
_config = None # <--- 修改: 初始化为 None

# 初始化数据库
db = SQLAlchemy()

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
BLUEPRINTS_DIR = os.path.join('api')

def register_blueprints(app):
    """注册所有蓝图"""
    blueprints_files = [
        f[:-3] for f in os.listdir(BLUEPRINTS_DIR) 
        if f.endswith('Api.py') and not f.startswith('__')
    ]

    package = __name__.split('.')[0]
    for blueprint_file in blueprints_files:
        module_name = '.{}'.format(blueprint_file)
        module = importlib.import_module(module_name, package=package)
        api_blueprint = getattr(module, 'api_blueprint', None)
        if api_blueprint:
            url_prefix = '/api' + (api_blueprint.url_prefix or '')
            app.register_blueprint(api_blueprint, url_prefix=url_prefix)

def setup_logging(app):
    """配置日志"""
    app.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

def create_app():
    """创建并配置 Flask 应用"""
    global _config # <--- 添加: 声明我们将修改模块级的 _config

    # 此时，run.py 中的 load_dotenv() 应该已经执行完毕
    _config = OtherConfig() # <--- 修改: 在此处实例化 _config

    # 创建 Flask 应用
    app = Flask(__name__)
    
    # 添加静态文件路由
    @app.route('/api/file/<path:filename>')
    def serve_static(filename):
        try:
            # 解码URL编码的路径
            decoded_filename = unquote(filename)
            app.logger.debug(f"serve_static: Original filename from URL: {filename}")
            app.logger.debug(f"serve_static: Decoded filename: {decoded_filename!r}")
            # 现在 _config.FILE_PATH 会使用上面新实例化的 _config 对象
            app.logger.debug(f"serve_static: Configured FILE_PATH: {_config.FILE_PATH!r}")

            # 拼接完整路径 (用户提到的 L67 附近)
            # _config.FILE_PATH 现在是正确的
            full_path = os.path.join(_config.FILE_PATH, decoded_filename)
            app.logger.debug(f"serve_static: Constructed full_path: {full_path!r}")
            
            # 验证文件是否存在
            file_exists = os.path.exists(full_path)
            app.logger.debug(f"serve_static: Result of os.path.exists(full_path): {file_exists}")

            if not file_exists:
                app.logger.error(f"serve_static: File not found based on os.path.exists: {full_path}")
                # 尝试列出父目录内容进行调试
                parent_dir = os.path.dirname(full_path)
                app.logger.debug(f"serve_static: Checking parent directory: {parent_dir!r}")
                if os.path.exists(parent_dir) and os.path.isdir(parent_dir):
                    app.logger.debug(f"serve_static: Parent directory {parent_dir} exists and is a directory.")
                    try:
                        app.logger.debug(f"serve_static: Contents of parent directory {parent_dir}: {os.listdir(parent_dir)}")
                    except Exception as list_e:
                        app.logger.debug(f"serve_static: Could not list contents of {parent_dir}: {list_e}")
                else:
                    app.logger.debug(f"serve_static: Parent directory {parent_dir} does not exist or is not a directory.")
                abort(404) # 文件未找到，抛出404
                
            return send_from_directory(_config.FILE_PATH, decoded_filename)
        except HTTPException as e: # 捕获由 abort() 抛出的HTTP异常 (如 404)
            # 这些是预期的HTTP错误，例如 abort(404)
            app.logger.info(f"serve_static: HTTP exception occurred: {str(e)}") # 使用 info 或 debug 级别
            # traceback.print_exc() # 对于HTTPException，堆栈跟踪可能不是必需的，除非用于调试
            raise e # 重新抛出原始的HTTP异常，以便Flask正确处理它
        except Exception as e: # 捕获其他所有非HTTP的意外错误
            app.logger.error(f"serve_static: Unexpected error serving file: {str(e)}")
            traceback.print_exc() # 打印详细的堆栈跟踪
            abort(500) # 对于其他未知错误，返回500

    @app.route('/api/static/<path:filename>')
    def serve_ocr_static(filename):
        try:
            # 解码URL编码的路径
            decoded_filename = unquote(filename)
            app.logger.debug(f"serve_static: Original filename from URL: {filename}")
            app.logger.debug(f"serve_static: Decoded filename: {decoded_filename!r}")
            # 现在 _config.FILE_PATH 会使用上面新实例化的 _config 对象
            app.logger.debug(f"serve_static: Configured FILE_PATH: {_config.OCR_OPEN_FILE_PATH!r}")

            # 拼接完整路径 (用户提到的 L67 附近)
            # _config.FILE_PATH 现在是正确的
            full_path = os.path.join(_config.OCR_OPEN_FILE_PATH, decoded_filename)
            app.logger.debug(f"serve_static: Constructed full_path: {full_path!r}")
            
            # 验证文件是否存在
            file_exists = os.path.exists(full_path)
            app.logger.debug(f"serve_static: Result of os.path.exists(full_path): {file_exists}")

            if not file_exists:
                app.logger.error(f"serve_static: File not found based on os.path.exists: {full_path}")
                # 尝试列出父目录内容进行调试
                parent_dir = os.path.dirname(full_path)
                app.logger.debug(f"serve_static: Checking parent directory: {parent_dir!r}")
                if os.path.exists(parent_dir) and os.path.isdir(parent_dir):
                    app.logger.debug(f"serve_static: Parent directory {parent_dir} exists and is a directory.")
                    try:
                        app.logger.debug(f"serve_static: Contents of parent directory {parent_dir}: {os.listdir(parent_dir)}")
                    except Exception as list_e:
                        app.logger.debug(f"serve_static: Could not list contents of {parent_dir}: {list_e}")
                else:
                    app.logger.debug(f"serve_static: Parent directory {parent_dir} does not exist or is not a directory.")
                abort(404) # 文件未找到，抛出404
                
            return send_from_directory(_config.OCR_OPEN_FILE_PATH, decoded_filename)
        except HTTPException as e: # 捕获由 abort() 抛出的HTTP异常 (如 404)
            # 这些是预期的HTTP错误，例如 abort(404)
            app.logger.info(f"serve_static: HTTP exception occurred: {str(e)}") # 使用 info 或 debug 级别
            # traceback.print_exc() # 对于HTTPException，堆栈跟踪可能不是必需的，除非用于调试
            raise e # 重新抛出原始的HTTP异常，以便Flask正确处理它
        except Exception as e: # 捕获其他所有非HTTP的意外错误
            app.logger.error(f"serve_static: Unexpected error serving file: {str(e)}")
            traceback.print_exc() # 打印详细的堆栈跟踪
            abort(500) # 对于其他未知错误，返回500
    
    # 加载配置
    app.config.from_object(MysqlConfig)
    app.config.from_object(JwtConfig)
    # app.config.from_object(OtherConfig) # <--- 旧代码
    app.config.from_object(_config) # <--- 修改: 从已正确初始化的 _config 实例加载

    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # 设置日志
    setup_logging(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 配置 JWT
    jwt = JWTManager(app)
    jwt.JWT_DEBUG = True
    app.jwt = jwt
    
    return app