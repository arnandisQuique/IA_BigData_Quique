import json
import time
import websocket
from kafka import KafkaProducer
from prometheus_client import start_http_server, Gauge, Counter

# Métricas para Grafana
M_PRECIO_ACTUAL = Gauge('crypto_precio_actual', 'Precio actual', ['par'])
M_MENSAJES = Counter('pipeline_mensajes_total', 'Total mensajes enviados')

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def on_message(ws, message):
    data = json.loads(message)
    symbol = data.get('s')
    price = float(data.get('c'))
    
    M_PRECIO_ACTUAL.labels(par=symbol).set(price)
    M_MENSAJES.inc()
    
    producer.send('crypto_raw_data', value=data)
    print(f"Tick: {symbol} @ {price}")

def start_websocket():
    # BTCUSDT (Obligatorio) + ETHUSDT (Elegido)
    url = "wss://stream.binance.com:9443/ws/btcusdt@miniTicker/ethusdt@miniTicker"
    ws = websocket.WebSocketApp(url, on_message=on_message)
    ws.run_forever()

if __name__ == "__main__":
    start_http_server(8000)
    start_websocket()