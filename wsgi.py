from xb2 import create_app
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

config_name = os.getenv("FLASK_CONFIG", 'development')
app = create_app(config_name)