from fastapi import FastAPI
from sqladmin import Admin
from app.db import engine
from app.admin_import import TrafficImportView

app = FastAPI()
admin = Admin(app, engine)
admin.add_view(TrafficImportView)
