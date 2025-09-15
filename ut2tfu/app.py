from fastapi import FastAPI, Request, HTTPException
import random
import time
import os

app = FastAPI()

# 1. Táctica de Replicación

# Simulamos múltiples "réplicas" de la app que pueden responder.
replica_name = os.getenv("REPLICA_NAME", "Replica-desconocida")

@app.get("/replica")
def get_replica():
    return {"message": f"Respuesta dada por {replica_name}"}


# 2. Táctica de Reintentos

# Simula un endpoint que a veces falla, y reintentamos hasta 3 veces.
@app.get("/unstable")
def unstable_endpoint():
    for attempt in range(1, 4):  # hasta 3 intentos
        if random.random() < 0.5:  # 50% de probabilidad de éxito
            return {"message": f"Éxito en el intento {attempt}"}
        time.sleep(0.5)  # esperar un poco antes de reintentar
    raise HTTPException(status_code=500, detail="Falló después de 3 intentos")



# 3. Seguridad - Rate Limiting

# Evita que un cliente haga demasiadas requests en poco tiempo.
from collections import defaultdict
from time import time as now

request_counts = defaultdict(list)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host
    current_time = now()
    window = 10  # segundos
    limit = 5    # máximo de requests por ventana

    # limpiar requests viejas
    request_counts[ip] = [t for t in request_counts[ip] if current_time - t < window]

    if len(request_counts[ip]) >= limit:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    request_counts[ip].append(current_time)
    return await call_next(request)



# 4. Seguridad - Validación API Key

API_KEY = "secreta123"

@app.get("/secure-data")
def secure_data(request: Request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"secure": "Esta es información protegida con una Key"}



# Rutas básicas

@app.get("/")
def root():
    return {"message": "Funcoinaaa!"}

@app.get("/ping")
def ping():
    return {"pong": "ok"}
