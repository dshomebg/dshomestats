from sqladmin import BaseView, expose
from starlette.responses import HTMLResponse

class TrafficImportView(BaseView):
    name = "Импорт на трафик"
    icon = "fa fa-upload"
    slug = "trafficimport"  # slug-а определя URL-а: /admin/trafficimport/

    @expose("/", methods=["GET"])
    async def import_traffic(self, request):
        return HTMLResponse("<h1>Работи!</h1>")
