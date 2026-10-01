from fastapi import FastAPI
import sqlite3
from datetime import datetime

app = FastAPI()


def criar_banco():
    conexao = sqlite3.connect("estacao.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estacao_id TEXT,
            temperatura REAL,
            umidade REAL,
            pressao REAL,
            qualidade_ar REAL,
            luminosidade REAL,
            chuva REAL,                         
            data_hora TEXT
        )
    """)

    conexao.commit()
    conexao.close()


criar_banco()


@app.get("/")
def inicio():
    return {"mensagem": "API funcionando"}


@app.post("/leituras")
def receber_dados(dados: dict):

    campos_obrigatorios = [
        "estacao_id",
        "temperatura",
        "umidade",
        "pressao",
        "qualidade_ar",
        "luminosidade",
        "chuva"
    ]

    for campo in campos_obrigatorios:
        if campo not in dados:
            return {
                "erro": f"Campo obrigatório não informado: {campo}"
            }

    conexao = sqlite3.connect("estacao.db")
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO leituras (
            estacao_id,
            temperatura,
            umidade,
            pressao,
            qualidade_ar,
            luminosidade,
            chuva,
            data_hora
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados["estacao_id"],
        dados["temperatura"],
        dados["umidade"],
        dados["pressao"],
        dados["qualidade_ar"],
        dados["luminosidade"],
        dados["chuva"],
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ))

    conexao.commit()
    conexao.close()

    return {
        "mensagem": "Dados salvos com sucesso"
    }
    
@app.get("/leituras")
def listar_leituras():
    conexao = sqlite3.connect("estacao.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM leituras")
    dados = cursor.fetchall()

    conexao.close()

    leituras = []

    for dado in dados:
        leitura = {
            "id": dado[0],
            "estacao_id": dado[1],
            "temperatura": dado[2],
            "umidade": dado[3],
            "pressao": dado[4],
            "qualidade_ar": dado[5],
            "luminosidade": dado[6],
            "chuva": dado[7],
            "data_hora": dado[8]
        }

        leituras.append(leitura)

    return {
        "leituras": leituras
    }
    
    
@app.get("/leituras/ultima")
def ultima_leitura():
    conexao = sqlite3.connect("estacao.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT * FROM leituras
        ORDER BY id DESC
        LIMIT 1
    """)

    dado = cursor.fetchone()

    conexao.close()

    if dado is None:
        return {
            "mensagem": "Nenhuma leitura encontrada"
        }

    leitura = {
        "id": dado[0],
        "estacao_id": dado[1],
        "temperatura": dado[2],
        "umidade": dado[3],
        "pressao": dado[4],
        "qualidade_ar": dado[5],
        "luminosidade": dado[6],
        "chuva": dado[7],
        "data_hora": dado[8]
    }

    return {
        "ultima_leitura": leitura
    }
@app.get("/estatisticas")
def estatisticas():
    conexao = sqlite3.connect("estacao.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            AVG(temperatura),
            MIN(temperatura),
            MAX(temperatura),
            AVG(umidade)
        FROM leituras
    """)

    dados = cursor.fetchone()

    conexao.close()

    return {
    "temperatura_media": round(dados[0],2),
    "temperatura_minima": dados[1],
    "temperatura_maxima": dados[2],
    "umidade_media": round(dados[3], 2)
}