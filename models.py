"""FastAPI API for Text to SQL"""

from fastapi import FastAPI
from pydantic import BaseModel

from bsql.sql.sqlcoder import SQLCoder
from bsql.viz.llama2 import Data2Viz
from bsql.viz.vegalite import VegaLite

app = FastAPI()


sqlcoder = SQLCoder()
llama = Data2Viz()
vegalite = VegaLite()


class InferenceRequest(BaseModel):
    """Inference request"""

    question: str = ""
    query: str = ""
    prompt: str = ""
    schema: str = ""
    query_result: str = ""
    model_name: str = "sqlcoder"


@app.get("/test")
def test_server():
    """Test server"""
    return "Hello from Text to SQL Server"


@app.post("/inference")
def inference(request: InferenceRequest):
    """Inference"""
    if request.model_name == "sqlcoder":
        return sqlcoder.inference(request.question, request.schema)

    if request.model_name == "data2viz":
        return vegalite.inference(request.question, request.query_result)

    if request.model_name == "followup":
        return llama.generate_followup_questions(request.question)

    return "Model not found"
