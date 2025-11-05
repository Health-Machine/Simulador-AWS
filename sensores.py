import json
import random
import datetime as dt
import requests  # única adição

url = "https://suotc0e1d7.execute-api.us-east-1.amazonaws.com/hml/raw-bucket-891377383993/sensor/captura_de_dados.json"

# Corrente
tensao_padrao = 2.5
sensibilidade = 0.066
corrente_nominal = 10.0
tensao_teorica = tensao_padrao + corrente_nominal * sensibilidade

# Tensão
vmax_in = 400
variacao_minima = 0
tensao_normal_base = 350  # O centro da faixa normal
variacao_normal = 2.0
probabilidade_pico = 0.05 # 5% de chance de pico

# Temperatura
temperatura_nominal = 25.0
variacao_maxima_temp = 0.8

# Vibração
velocidade_nominal = 6.0
variacao_permitida = 5.0

# Frequência
frequencia_nominal = 60.0
variacao_maxima_freq = 1.5

# Pressão
pressao_nominal = 35.0
variacao_maxima_pressao = 2.5


def simular_dados(url, meses, intervalo_minutos):
    agora = dt.datetime.now()
    current_time = agora - dt.timedelta(days=30 * meses)
    dados = []

    while current_time <= agora:

        record = {
            'data_captura': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'sensor_1': calcular_corrente(),
            'sensor_2': calcular_tensao(),
            'sensor_3': calcular_temperatura(),
            'sensor_4': calcular_vibracao(),
            'sensor_5': calcular_pressao(),
            'sensor_6': calcular_frequencia()
        }

        dados.append(record)
        current_time += dt.timedelta(minutes=intervalo_minutos)

    # envia o JSON direto via HTTP PUT
    r = requests.put(url, data=json.dumps(dados), headers={'Content-Type': 'application/json'})

    print(f"Status: {r.status_code}")
    print(f"Resposta: {r.text}")
    # print(json.dumps(dados, indent=2))
    print(f"Enviado para: {url} ({len(dados)} registros)")


def calcular_corrente():
    variacao = random.uniform(-0.5, 0.5)
    tensao_saida = tensao_teorica + variacao
    return round((tensao_saida - tensao_padrao) / sensibilidade, 3)

def calcular_tensao():
    limite_normal_inferior = tensao_normal_base - variacao_normal
    limite_normal_superior = tensao_normal_base + variacao_normal

    if random.random() < probabilidade_pico:
        if random.choice([True, False]):
            variacao = random.uniform(limite_normal_superior, vmax_in)
        else:
            variacao = random.uniform(variacao_minima, limite_normal_inferior)
    
    else:
        variacao = random.uniform(limite_normal_inferior, limite_normal_superior)

    return round(variacao, 2)

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


# Exemplo de uso:
simular_dados(url, meses=1, intervalo_minutos=1)
