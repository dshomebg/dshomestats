from fastapi import APIRouter, Request, UploadFile, Form
from sqladmin import BaseView, expose
from app.db import SessionLocal
from app.models import Traffic
import pandas as pd
from starlette.responses import HTMLResponse, RedirectResponse

router = APIRouter()

# Формата за импорт и преглед на първи ред
class TrafficImportView(BaseView):
    name = "Импорт на трафик"
    icon = "fa fa-upload"

    @expose("/", methods=["GET", "POST"])
    async def import_traffic(self, request: Request):
        if request.method == "POST":
            form = await request.form()
            file: UploadFile = form["file"]
            # Четем excel или csv
            if file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
                df = pd.read_excel(file.file)
            elif file.filename.endswith(".csv"):
                df = pd.read_csv(file.file)
            else:
                return HTMLResponse("<b>Невалиден формат!</b>")

            # Вземи колоните, покажи форма за мапинг
            columns = df.columns.tolist()
            preview = df.head(1).to_html(index=False)
            mapping_fields = ["year", "month", "organic", "brand", "facebook", "facebook_paid", "google_paid", "other"]
            mapping_form = "".join(
                f'<label>{field}: <select name="map_{field}">' +
                "".join(f'<option value="{col}">{col}</option>' for col in columns) +
                "</select></label><br>"
                for field in mapping_fields
            )

            # Покажи preview и mapping формата
            html = f"""
                <h3>Преглед на първия ред:</h3>
                {preview}
                <form action="/admin/traffic-import/process" method="post">
                {mapping_form}
                <input type="hidden" name="file_name" value="{file.filename}">
                <button type="submit">Импорт</button>
                </form>
            """
            # Съхрани df временно (можеш да ползваш session, файл, redis или temp файл)
            df.to_csv(f"/tmp/{file.filename}", index=False)
            return HTMLResponse(html)
        else:
            return HTMLResponse("""
                <form method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".xlsx,.xls,.csv" required>
                    <button type="submit">Качи</button>
                </form>
            """)

    @expose("/process", methods=["POST"])
    async def process_import(self, request: Request):
        form = await request.form()
        file_name = form["file_name"]
        df = pd.read_csv(f"/tmp/{file_name}")
        mapping_fields = ["year", "month", "organic", "brand", "facebook", "facebook_paid", "google_paid", "other"]
        mapping = {field: form[f"map_{field}"] for field in mapping_fields}
        db = SessionLocal()
        imported = 0
        for _, row in df.iterrows():
            traffic = Traffic(**{field: row[mapping[field]] for field in mapping_fields})
            db.add(traffic)
            imported += 1
        db.commit()
        db.close()
        return HTMLResponse(f"<b>Импорт завършен! Импортирани редове: {imported}</b>")

# В SQLAdmin main.py:
from app.admin_import import TrafficImportView
admin.add_view(TrafficImportView)
