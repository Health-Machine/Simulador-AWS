import sys
import random
import pandas as pd
import datetime as dt
import time
import database
import io
import boto3
import requests

inicio = 1000
fim = 6000
passo = 100

url = "https://bzz8yo29s7.execute-api.us-east-1.amazonaws.com/hml/raw-bucket-199917718936/teste.json"

# ID_SENSOR_CORRENTE = database.get_sensor('ACS712 30A')
# ID_SENSOR_TENSAO = database.get_sensor('ZMPT101B')
# ID_SENSOR_TEMPERATURA = database.get_sensor('LM35CZ')
# ID_SENSOR_VIBRACAO = database.get_sensor('QM30VT1')
# ID_SENSOR_PRESSAO = database.get_sensor('MPX5700DP')
# ID_SENSOR_FREQUENCIA = database.get_sensor('IFM DI6001')

ID_SENSOR_CORRENTE = 1
ID_SENSOR_TENSAO = 2
ID_SENSOR_TEMPERATURA = 3
ID_SENSOR_VIBRACAO = 4
ID_SENSOR_PRESSAO = 5
ID_SENSOR_FREQUENCIA = 6

# Configuração do banco de dados
# engine = database.get_engine()

# Corrente
tensao_padrao = 2.5
sensibilidade = 0.066
corrente_nominal = 10.0
tensao_teorica = tensao_padrao + corrente_nominal * sensibilidade

# Tensão
vmax_out = 3.53
vmax_in = 400
variacao_minima = 220

# Parâmetros do sensor de temperatura
temperatura_nominal = 25.0  # graus Celsius
variacao_maxima_temp = 0.8  # variação máxima simulada

# Parâmetros do sensor QM30VT1
velocidade_nominal = 10.0  # Velocidade de vibração nominal em mm/s
variacao_permitida = 2.0  # Variação aleatória permitida

# Parâmetros do sensor de frequência
frequencia_nominal = 60.0
variacao_maxima_freq = 1.5

# Parâmetros do sensor de pressão
pressao_nominal = 35.0  # Pa
variacao_maxima_pressao = 2.5  # Pa

def measure_memory():
    return sys.getsizeof([]) / (1024 * 1024)

def _sensor_name(sensor_id):
    mapping = {
        1: 'corrente',
        2: 'tensao',
        3: 'temperatura',
        4: 'vibracao',
        5: 'pressao',
        6: 'frequencia'
    }
    return mapping.get(sensor_id, 'sensor')

def simular_dados(sensor_id, calcular_valor):
    valores = []
    start_time = time.time()
    start_memory = measure_memory()

    agora = dt.datetime.now()
    seis_meses_atras = agora - dt.timedelta(days=30)  # Aproximadamente 6 meses

    current_time = seis_meses_atras
    # Simular dados a cada minuto durante 6 meses (aproximadamente 262,800 registros)
    while current_time <= agora:
        valor_calculado = calcular_valor()
        insert = {
            'fk_sensor': sensor_id,
            'valor': valor_calculado,
            'data_captura': current_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        valores.append(insert)
        current_time += dt.timedelta(minutes=1)  # 1 dado por minuto

    end_time = time.time()
    end_memory = measure_memory()

    df = pd.DataFrame(valores)

    # Preparar arquivo JSON com o padrão de nome solicitado:
    # Ex: 20250909211500-frequencia.json (YYYYMMDDhhmmss-nome_sensor.json)
    ts = dt.datetime.now().strftime('%Y%m%d%H%M%S')
    nome_sensor = _sensor_name(sensor_id)
    filename = f"{ts}-{nome_sensor}.json"
    # Construir a URL de PUT pegando a base da url original e substituindo o arquivo final
    base_url = url.rsplit('/', 1)[0]
    put_url = f"{base_url}/{filename}"

    # Gerar JSON como bytes (orient='records' = array de objetos)
    json_bytes = df.to_json(orient='records').encode('utf-8')

    # Fazer PUT com conteúdo binário (equivalente a --data-binary @file e header Content-Type)
    headers = {'Content-Type': 'application/json'}
    response = requests.put(put_url, data=json_bytes, headers=headers)
    print(f"PUT URL: {put_url}")
    print(f"Status Code: {response.status_code}, Response: {response.text}")

    # Salvar CSV em buffer
    # csv_buffer = io.StringIO()
    # df.to_csv(csv_buffer, index=False)

    # Enviar para "S3" local (simulado)
    # bucket_name = 'raw-bucket-health-machine'
    # arquivo_s3 = f'sensor_{sensor_id}.csv'

    # with open(arquivo_s3, 'w', newline='', encoding='utf-8') as f:
    #     f.write(csv_buffer.getvalue())

    # print(f"Arquivo enviado ao S3: s3://{bucket_name}/{arquivo_s3}")
    print("""
    Tempo de execução: {:.2f} segundos
    Memória usada: {:.2f} MB
    """.format(end_time - start_time, end_memory - start_memory))

def calcular_corrente():
    variacao = random.uniform(-0.01, 0.02)
    tensao_saida = tensao_teorica + variacao
    return round((tensao_saida - tensao_padrao) / sensibilidade, 3)

def calcular_tensao():
    variacao = random.uniform(variacao_minima, vmax_in)
    return (variacao / vmax_in) * vmax_out

def calcular_temperatura():
    variacao = random.uniform(-variacao_maxima_temp, variacao_maxima_temp)
    return round(temperatura_nominal + variacao, 2)

def calcular_vibracao():
    variacao = random.uniform(-variacao_permitida, variacao_permitida)
    return round(velocidade_nominal + variacao, 3)

def calcular_pressao():
    variacao = random.uniform(-variacao_maxima_pressao, variacao_maxima_pressao)
    return round(pressao_nominal + variacao, 2)

def calcular_frequencia():
    variacao = random.uniform(-variacao_maxima_freq, variacao_maxima_freq)
    return round(frequencia_nominal + variacao, 2)

def sim_corrente():
    simular_dados(ID_SENSOR_CORRENTE, calcular_corrente)

def sim_tensao():
    simular_dados(ID_SENSOR_TENSAO, calcular_tensao)

def sim_temperatura():
    simular_dados(ID_SENSOR_TEMPERATURA, calcular_temperatura)

def sim_vibracao():
    simular_dados(ID_SENSOR_VIBRACAO, calcular_vibracao)

def sim_pressao():
    simular_dados(ID_SENSOR_PRESSAO, calcular_pressao)

def sim_frequencia():
    simular_dados(ID_SENSOR_FREQUENCIA, calcular_frequencia)
