from fastapi import FastAPI
from sqladmin import Admin, ModelView

from app.db import engine
from app.models import User, Traffic
from app.admin_import import TrafficImportView
app = FastAPI(
    title="Traffic API",
    description="Модул за трафик с пера по месеци и години",
    version="0.2.0"
)

# SQLAdmin setup:
admin = Admin(app, engine)

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.is_admin]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

class TrafficAdmin(ModelView, model=Traffic):
    column_list = [
        Traffic.id, Traffic.year, Traffic.month, Traffic.organic, Traffic.brand,
        Traffic.facebook, Traffic.facebook_paid, Traffic.google_paid, Traffic.other
    ]
    name = "Traffic"
    name_plural = "Traffic"
    icon = "fa-solid fa-chart-line"

admin.add_view(UserAdmin)
admin.add_view(TrafficAdmin)
admin.add_view(TrafficImportView)
# Останалите твои endpoint-и могат да си стоят както са били
