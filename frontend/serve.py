#!/usr/bin/env python3
"""
Script simple para servir el frontend del procesador de volantes médicos
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuración
PORT = 8080
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Añadir headers para CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print("=" * 60)
        print("🏥 MAPFRE - Frontend de Volantes Médicos")
        print("=" * 60)
        print(f"\n✅ Servidor iniciado en: {url}")
        print(f"📁 Sirviendo archivos desde: {DIRECTORY}")
        print(f"\n🌐 Abriendo navegador...")
        print(f"\n⚠️  Asegúrate de que el API esté ejecutándose en:")
        print(f"   http://localhost:8000/v1/image/process-image")
        print(f"\n💡 Para detener el servidor, presiona Ctrl+C")
        print("=" * 60)
        
        # Abrir navegador automáticamente
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Servidor detenido. ¡Hasta luego!")

if __name__ == "__main__":
    main()
