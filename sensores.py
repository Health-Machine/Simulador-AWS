import json
import random
import datetime as dt
import requests
from datetime import timedelta

# Endpoint de destino
url = "https://g5xyw5okt6.execute-api.us-east-1.amazonaws.com/hml/raw-bucket-891377383993/sensor/captura_de_dados.json"

# Corrente
tensao_padrao = 2.5
sensibilidade = 0.066
corrente_nominal = 10.0
tensao_teorica = tensao_padrao + corrente_nominal * sensibilidade

# Tensão
vmax_in = 400
variacao_minima = 300
tensao_normal_base = 350
variacao_normal = 2.0
probabilidade_pico = 0.01

# Temperatura
temperatura_nominal = 25.0
variacao_maxima_temp = 0.8

# Vibração
velocidade_nominal = 6.0
variacao_permitida = 5.0
horario_parada_inicio = 12  # início da parada (12h)
horario_parada_fim = 16     # fim da parada (16h)

# Frequência
frequencia_nominal = 60.0
frequencia_minima = 38.0
frequencia_maxima = 72.0
osc_normal_amp = 4.0
osc_phase_amp = 1.0
velocidade_variacao = 0.02  # variação linear (~1,2 por hora)
ultima_freq = frequencia_nominal
fase = "normal"
fora_limite_desde = None  # controla tempo fora dos limites

# Pressão
pressao_nominal = 35.0
variacao_maxima_pressao = 2.5


def simular_dados(meses, intervalo_minutos):
    agora = dt.datetime.now()
    current_time = agora - dt.timedelta(days=30 * meses)
    dados = []

    while current_time <= agora:
        record = {
            'data_captura': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'sensor_1': calcular_corrente(),
            'sensor_2': calcular_tensao(),
            'sensor_3': calcular_temperatura(),
            'sensor_4': calcular_vibracao(current_time),
            'sensor_5': calcular_pressao(),
            'sensor_6': calcular_frequencia(current_time, agora)
        }

        dados.append(record)
        current_time += dt.timedelta(minutes=intervalo_minutos)

    print(f"📊 Total de registros gerados: {len(dados)}")

    # --- Envio ao endpoint ---
    try:
        r = requests.put(
            url,
            data=json.dumps(dados),
            headers={'Content-Type': 'application/json'}
        )
        print(f"🌐 Envio concluído! Status: {r.status_code}")
        print(f"📨 Resposta do servidor: {r.text[:200]}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar dados: {e}")


def calcular_corrente():
    """
    Simula o comportamento da corrente em quatro estados operacionais:
    - Desligada (< 0.5 A)
    - Ociosa (0.5 A - 9.9 A)
    - Em Carga (10 A - 50 A)
    - Sobrecarga (> 50 A)

    Comportamento esperado:
    - 90% das leituras são normais (Em Carga)
    - 10% das leituras simulam anomalias (Desligada, Ociosa ou Sobrecarga)
    """
    comportamento_normal = random.random() > 0.10  # 90% normal

    if comportamento_normal:
        # Corrente normal entre 10 e 50 A (faixa de trabalho)
        corrente = random.uniform(10, 50)
    else:
        # 10% de chance — escolhe um estado anômalo
        estado_anomalo = random.choice(["Desligada", "Ociosa", "Sobrecarga"])
        if estado_anomalo == "Desligada":
            corrente = random.uniform(0.0, 0.3)
        elif estado_anomalo == "Ociosa":
            corrente = random.uniform(0.4, 9.9)
        else:  # Sobrecarga
            corrente = random.uniform(51, 80)

    # Converte para tensão simulando o sensor (saída do ACS712, por exemplo)
    tensao_saida = tensao_padrao + corrente * sensibilidade + random.uniform(-0.05, 0.05)
    corrente_real = (tensao_saida - tensao_padrao) / sensibilidade
    return round(corrente_real, 3)



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


def calcular_vibracao(current_time):
    hora = current_time.hour
    # 4h de parada diária
    if horario_parada_inicio <= hora < horario_parada_fim:
        return 0.0
    variacao = random.uniform(-variacao_permitida, variacao_permitida)
    return round(velocidade_nominal + variacao, 3)


def calcular_pressao():
    variacao = random.uniform(-variacao_maxima_pressao, variacao_maxima_pressao)
    return round(pressao_nominal + variacao, 2)


def calcular_frequencia(current_time, inicio_simulacao):
    global ultima_freq, fase, fora_limite_desde

    # tempo desde o início (em dias)
    dias_passados = (current_time - inicio_simulacao).days
    minutos_passados = (current_time - inicio_simulacao).total_seconds() / 60

    # define a fase do ciclo
    if dias_passados % 4 == 0:
        fase = "normal"
        alvo = frequencia_nominal
        osc = random.uniform(-osc_normal_amp, osc_normal_amp)
    elif dias_passados % 4 == 1:
        fase = "descendo"
        alvo = frequencia_minima
        osc = random.uniform(-osc_phase_amp, osc_phase_amp)
    elif dias_passados % 4 == 2:
        fase = "subindo"
        alvo = frequencia_nominal
        osc = random.uniform(-osc_phase_amp, osc_phase_amp)
    else:
        fase = "subindo_alta"
        alvo = frequencia_maxima
        osc = random.uniform(-osc_phase_amp, osc_phase_amp)

    # aproxima linearmente até o alvo
    if ultima_freq < alvo:
        ultima_freq = min(ultima_freq + velocidade_variacao, alvo)
    elif ultima_freq > alvo:
        ultima_freq = max(ultima_freq - velocidade_variacao, alvo)

    valor = ultima_freq + osc

    # --- controle de tempo fora da faixa ---
    limite_min, limite_max = 40.0, 70.0
    if valor < limite_min or valor > limite_max:
        if fora_limite_desde is None:
            fora_limite_desde = current_time
        else:
            tempo_fora = current_time - fora_limite_desde
            if tempo_fora > timedelta(minutes=30):
                # força retorno gradual à faixa segura
                if valor < limite_min:
                    ultima_freq += 0.2  # sobe mais rápido
                elif valor > limite_max:
                    ultima_freq -= 0.2
                valor = ultima_freq
    else:
        fora_limite_desde = None  # reset do contador

    # segurança
    valor = max(frequencia_minima, min(valor, frequencia_maxima))
    ultima_freq = valor

    return round(valor, 2)

# Exemplo de uso:
simular_dados(meses=1, intervalo_minutos=1)
