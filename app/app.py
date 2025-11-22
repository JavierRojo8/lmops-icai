# app/app.py

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Importar routers
from app.routers.agent import router as image_processor
# TODO 8: Importar el router file_info
from app.routers import file_info


app = FastAPI(
    title="MAPFRE - Image Processing API",
    description="API for extracting information from images using Gemini",
    version="1.0.0",
)

# Añadimos CORS ya que se necesita para poder hacer peticiones
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos los routers
app.include_router(image_processor, prefix="/v1/image")
# Incluimos los routers de file_info
# TODO 9: Registrar el router en la aplicación y añade el  prefix="/v1/files"
app.include_router(file_info.router, prefix="/v1/files")
# Servir archivos estáticos del frontend
# Buscar el directorio frontend tanto en desarrollo como en Docker
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    print(f"✅ Frontend servido desde: {frontend_dir}")
else:
    print(f"⚠️  Directorio frontend no encontrado: {frontend_dir}")
@app.get("/healthcheck", response_class=JSONResponse)
async def healthcheck():
    """
    Endpoint para verificar el estado del servidor.

    Returns:
        JSONResponse: Estado del servidor.
    """
    return JSONResponse({"status": "ok", "message": "Service is running"})


# Descomentar si ejecutar en local se debe ejecutar desde la raiz del proyecto con python -m parrot.app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
