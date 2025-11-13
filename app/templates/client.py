# client.py
import asyncio
import base64
import json
import queue
import threading

import pyaudio
import websockets

# Configuración de audio
audio_format = pyaudio.paInt16  # Resolución de 16 bits
channels = 1  # Audio mono
rate = 24000  # Frecuencia de muestreo de 24kHz
chunk = 1024  # Número de muestras por frame

# Inicializar PyAudio
p = pyaudio.PyAudio()
stream_in = p.open(
    format=audio_format,
    channels=channels,
    rate=rate,
    input=True,
    frames_per_buffer=chunk,
    start=True,
)  # start=True para comenzar la grabación inmediatamente

stream_out = p.open(
    format=audio_format, channels=channels, rate=rate, output=True, start=False
)  # start=False para controlar cuándo comienza la reproducción

# Reemplaza esta URL con la URL del servidor
SERVER_URL = "wss://api.voicebot.parrot.es.int.emea.aws.mapfre.com/local"

# Eventos para controlar el habla del usuario
input_queue = queue.Queue()
output_queue = queue.Queue()
recording = True  # Iniciar grabación inmediatamente
playing = False
user_speaking = False


async def main():
    print("Conectando al servidor...")
    async with websockets.connect(SERVER_URL) as websocket:
        print("Conectado al servidor.")

        # Hilos para capturar y reproducir audio
        def read_audio_input():
            try:
                while True:
                    audio_data = stream_in.read(chunk, exception_on_overflow=False)
                    input_queue.put(audio_data)
            except Exception as e:
                print(f"Error en read_audio_input: {e}")

        def write_audio_output():
            try:
                while True:
                    audio_data = output_queue.get()
                    if audio_data:
                        stream_out.write(audio_data)
                    else:
                        print("Audio_data está vacío")
            except Exception as e:
                print(f"Error en write_audio_output: {e}")

        input_thread = threading.Thread(target=read_audio_input, daemon=True)
        output_thread = threading.Thread(target=write_audio_output, daemon=True)
        input_thread.start()
        output_thread.start()

        # Corrutina para enviar audio al servidor
        async def send_audio_to_server():
            try:
                while True:
                    audio_data = await asyncio.get_event_loop().run_in_executor(
                        None, input_queue.get
                    )
                    audio_base64 = base64.b64encode(audio_data).decode("utf-8")
                    message = json.dumps(
                        {"type": "client_audio", "audio": audio_base64}
                    )
                    await websocket.send(message)
            except Exception as e:
                print(f"Error en send_audio_to_server: {e}")

        # Corrutina para detectar si el usuario está hablando
        async def detect_user_speaking():
            global user_speaking
            silence_threshold = (
                500  # Umbral de silencio en bytes (ajusta según sea necesario)
            )
            try:
                while True:
                    audio_data = await asyncio.get_event_loop().run_in_executor(
                        None, input_queue.get
                    )
                    if max(audio_data) > silence_threshold:
                        if not user_speaking:
                            user_speaking = True
                            await websocket.send(
                                json.dumps({"type": "user_speaking", "value": True})
                            )
                    else:
                        if user_speaking:
                            user_speaking = False
                            await websocket.send(
                                json.dumps({"type": "user_speaking", "value": False})
                            )
                    # Regresar el audio al input_queue para que también se envíe al servidor
                    input_queue.put(audio_data)
            except Exception as e:
                print(f"Error en detect_user_speaking: {e}")

        # Corrutina para recibir datos del servidor
        async def receive_from_server():
            global recording, playing
            try:
                while True:
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    msg_type = response_data.get("type")

                    if msg_type == "speech_started":
                        # El usuario ha comenzado a hablar
                        if playing:
                            stream_out.stop_stream()
                            playing = False
                            # Limpiar cola de salida
                            with output_queue.mutex:
                                output_queue.queue.clear()
                        # print("Asistente detectó que el usuario está hablando.")

                    elif msg_type == "speech_stopped":
                        # El usuario ha terminado de hablar
                        print("Asistente detectó que el usuario dejó de hablar.")

                    elif msg_type == "assistant_audio":
                        # Audio del asistente
                        if not playing:
                            stream_out.start_stream()
                            playing = True
                        audio_data = base64.b64decode(response_data["audio"])
                        output_queue.put(audio_data)

                    elif msg_type == "assistant_text":
                        print("Asistente:", response_data["text"])

            except Exception as e:
                print(f"Error en receive_from_server: {e}")

        await asyncio.gather(
            send_audio_to_server(), receive_from_server(), detect_user_speaking()
        )


if __name__ == "__main__":
    asyncio.run(main())
