from flask import Flask

app = Flask(__name__)

from app import home_page
from app import user_views
from app import staff_views
from app import admin_views
