
from fastapi import FastAPI

app = FastAPI(titles="Voice API")


@app.get("/health")
def health():
	return("stauts: ok")
