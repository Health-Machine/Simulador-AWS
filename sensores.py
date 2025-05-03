import sys
import random
import pandas as pd
import datetime as dt
import time
import database
import io
import boto3


inicio = 1000
fim = 6000
passo = 100

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
engine = database.get_engine()

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
variacao_maxima_pressao = 0.5  # Pa



def measure_memory():
    return sys.getsizeof([]) / (1024 * 1024)


def simular_dados(sensor_id, calcular_valor):
    valores = []
    start_time = time.time()
    start_memory = measure_memory()

    current_time = dt.datetime.now()

    for repeticoes in range(inicio, fim + 1, passo):
        for _ in range(repeticoes):
            valor_calculado = calcular_valor()
            insert = {
                'fk_sensor': sensor_id,
                'valor': valor_calculado,
                'data_captura': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            valores.append(insert)
            current_time += dt.timedelta(seconds=1)

    end_time = time.time()
    end_memory = measure_memory()

    df = pd.DataFrame(valores)
    # df.to_sql('captura', con=engine, if_exists='append', index=False)
    #df.to_csv('captura.csv', mode='a', header=False, index=False)

    # Salvar em um buffer de memória
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # # Enviar para o S3
    s3 = boto3.client('s3')
    bucket_name = 'raw-bucket-health-machine'
    arquivo_s3 = f'dados/sensor_{sensor_id}.csv'

    s3.put_object(Bucket=bucket_name, Key=arquivo_s3, Body=csv_buffer.getvalue())

    print(f"Arquivo enviado ao S3: s3://{bucket_name}/{arquivo_s3}")
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