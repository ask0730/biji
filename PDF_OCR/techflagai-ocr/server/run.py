# -*- coding: utf-8 -*-
# run.py
from api import create_app
from dotenv import load_dotenv
import os
from pathlib import Path

# 使用绝对路径加载环境文件
base_dir = Path(__file__).parent
env = os.getenv('FLASK_ENV', 'production')
env_file = os.path.join(str(base_dir), '.env.{}'.format(env))
load_dotenv(str(env_file))
print(os.environ)
app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true',
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', '8090'))
    )
