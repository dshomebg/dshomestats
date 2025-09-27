from sqladmin import BaseView, expose
from fastapi import Request, UploadFile
from starlette.responses import HTMLResponse
import pandas as pd
from app.db import SessionLocal
from app.models import Traffic
import os
import tempfile

class TrafficImportView(BaseView):
    name = "Импорт на трафик"
    icon = "fa fa-upload"

    @expose("/", methods=["GET", "POST"])
    async def import_traffic(self, request: Request):
        if request.method == "POST":
            form = await request.form()
            file: UploadFile = form["file"]
            file_ext = os.path.splitext(file.filename)[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name

            try:
                if file_ext in [".xlsx", ".xls"]:
                    df = pd.read_excel(tmp_path)
                elif file_ext == ".csv":
                    df = pd.read_csv(tmp_path)
                else:
                    os.remove(tmp_path)
                    return HTMLResponse("<b>Невалиден формат!</b>")
            finally:
                os.remove(tmp_path)

            # Показваме колоните и първия ред за преглед
            columns = df.columns.tolist()
            preview = df.head(1).to_html(index=False)
            mapping_fields = [
                "year", "month", "organic", "brand", "facebook",
                "facebook_paid", "google_paid", "other"
            ]
            mapping_form = "".join(
                f'<label>{field}: <select name="map_{field}" required>' +
                "".join(f'<option value="{col}">{col}</option>' for col in columns) +
                "</select></label><br>"
                for field in mapping_fields
            )

            # Запази файла временно за втория POST
            df.to_csv(f"/tmp/traffic_import.csv", index=False)

            html = f"""
                <h3>Преглед на първия ред:</h3>
                {preview}
                <form action="/admin/traffic-import/process" method="post">
                {mapping_form}
                <button type="submit">Импорт</button>
                </form>
            """
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
        df = pd.read_csv("/tmp/traffic_import.csv")
        mapping_fields = [
            "year", "month", "organic", "brand", "facebook",
            "facebook_paid", "google_paid", "other"
        ]
        mapping = {field: form[f"map_{field}"] for field in mapping_fields}
        db = SessionLocal()
        imported = 0
        for _, row in df.iterrows():
            traffic = Traffic(**{field: row[mapping[field]] for field in mapping_fields})
            db.add(traffic)
            imported += 1
        db.commit()
        db.close()
        os.remove("/tmp/traffic_import.csv")
        return HTMLResponse(f"<b>Импорт завършен! Импортирани редове: {imported}</b>")
