import os
import sys
import io
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import APP_ROOT, DB_ETICARET, ENV_FILE

# Windows terminal cikti uyumsuzlugunu onlemek icin UTF-8 zorlamasi
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass

# .env dosyasini yukle
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        load_dotenv(stream=f)

api_key = os.getenv("GEMINI_API_KEY")


def llm_sorgu_zinciri_kur():
    if not DB_ETICARET.exists():
        print("Hata: Veritabanı dosyası bulunamadı.", flush=True)
        return None, None, None

    db = SQLDatabase.from_uri(f"sqlite:///{DB_ETICARET}")

    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0,
        google_api_key=api_key
    )

    schema_info = db.get_table_info()

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Sen bir SQLite uzmanısın. Kullanıcının sorusuna karşılık gelen geçerli bir SQL sorgusu yaz.\n"
            "Sadece ve sadece SQL sorgusunun kendisini döndür. Açıklama yapma, ```sql gibi markdown etiketleri koyma.\n\n"
            "Veritabanı Şeması:\n{schema}"
        )),
        ("human", "{question}")
    ])

    chain = prompt | llm | StrOutputParser()
    return chain, db, schema_info


if __name__ == "__main__":
    print("Yapay Zeka Destekli SQL Asistanı Başlatılıyor...\n", flush=True)

    if not api_key:
        print("Hata: GEMINI_API_KEY bulunamadı! .env dosyasını kontrol edin.", flush=True)
        sys.exit(1)

    chain, db, schema = llm_sorgu_zinciri_kur()

    if chain and db:
        soru = "Toplam kaç tane sipariş var?"
        print(f"Prompt: {soru}", flush=True)

        try:
            uretilen_sql = chain.invoke({"schema": schema, "question": soru})
            uretilen_sql = uretilen_sql.strip()

            print(f"Generated SQL: {uretilen_sql}", flush=True)

            sonuc = db.run(uretilen_sql)
            print(f"DB Execution Result: {sonuc}", flush=True)

        except Exception as e:
            print(f"SQL Çalıştırılırken Hata Oluştu: {e}", flush=True)