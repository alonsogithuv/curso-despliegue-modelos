from fastapi import FastAPI

app = FastAPI(title="Mi primera API")

@app.get("/")
def root():
    return {"message":"Mi primera API esta funcionando"}


#Parametros
@app.get("/saludo/{nombre}")
def saludo (nombre):
    return {"saludo":f"Hola {nombre}, como estás?"}

