from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from pydantic import BaseModel
from typing import Optional
import sys
import io
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from config.settings import APP_ROOT, DB_ETICARET

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass

from llm_manager import llm_sorgu_zinciri_kur


app = FastAPI(
    title="Text-to-SQL API",
    description="Doğal dilden SQL sorguları üreten ve çalıştıran API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class SQLResponse(BaseModel):
    question: str
    sql: str
    results: list
    error: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=SQLResponse)
def ask(request: QuestionRequest):
    chain, db, schema = llm_sorgu_zinciri_kur()

    if chain is None or db is None:
        return SQLResponse(
            question=request.question,
            sql="",
            results=[],
            error="Veritabanı bağlantısında veya model kurulumunda hata oluştu.",
        )

    try:
        uretilen_sql = chain.invoke({"schema": schema, "question": request.question})
        uretilen_sql = uretilen_sql.strip()

        import sqlite3

        db_path = str(DB_ETICARET)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(uretilen_sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = [dict(zip(columns, row)) for row in rows]

        return SQLResponse(question=request.question, sql=uretilen_sql, results=results)
    except Exception as e:
        return SQLResponse(
            question=request.question,
            sql=uretilen_sql if "uretilen_sql" in locals() else "",
            results=[],
            error=str(e),
        )


@app.get("/schema")
def get_schema():
    chain, db, schema = llm_sorgu_zinciri_kur()
    if db is None:
        return {"error": "Veritabanı bulunamadı."}
    return {"schema": schema}


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
        title="Text-to-SQL API",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
