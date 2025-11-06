import json
import random
import datetime as dt
import requests

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
freq_normal_min = 55.0
freq_normal_max = 65.0
frequencia_minima = 38.0
frequencia_maxima = 72.0
osc_normal_amp = 5.0
osc_phase_amp = 1.5
recovery_hours = 6
ultima_freq = frequencia_nominal
inicio_zona_critica = None
tipo_zona = None  # 'alta' ou 'baixa'  

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
    global ultima_freq, inicio_zona_critica, tipo_zona

    total_days = (current_time - inicio_simulacao).days
    phase = total_days % 4
    seconds_into_day = (current_time - current_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    frac_day = seconds_into_day / 86400.0

    # --- cálculo original de baseline ---
    if phase == 0:
        baseline = frequencia_nominal
        osc = random.uniform(-osc_normal_amp, osc_normal_amp)
        valor = baseline + osc

    elif phase == 1:
        baseline = frequencia_nominal + (frequencia_minima - frequencia_nominal) * frac_day
        osc = random.uniform(-osc_phase_amp, osc_phase_amp)
        valor = min(baseline + osc, frequencia_nominal - 0.1)

    elif phase == 2:
        hour_of_day = seconds_into_day / 3600.0
        if hour_of_day <= recovery_hours:
            progresso = hour_of_day / recovery_hours
            baseline = frequencia_minima + (frequencia_nominal - frequencia_minima) * progresso
            osc = random.uniform(-osc_phase_amp, osc_phase_amp)
            valor = baseline + osc
        else:
            baseline = frequencia_nominal
            osc = random.uniform(-osc_normal_amp, osc_normal_amp)
            valor = baseline + osc

    else:  # phase == 3
        baseline = frequencia_nominal + (frequencia_maxima - frequencia_nominal) * frac_day
        osc = random.uniform(-osc_phase_amp, osc_phase_amp)
        valor = max(baseline + osc, frequencia_nominal + 0.1)

    # --- segurança de limites absolutos ---
    valor = max(min(round(valor, 2), 78.0), 28.0)

    # --- controle de tempo em zona crítica ---
    zona_critica = None
    if valor > 70:
        zona_critica = 'alta'
    elif valor < 40:
        zona_critica = 'baixa'

    if zona_critica:
        if tipo_zona != zona_critica:
            # entrou em nova zona
            tipo_zona = zona_critica
            inicio_zona_critica = current_time
        else:
            # já estava nessa zona
            tempo_na_zona = current_time - inicio_zona_critica
            if tempo_na_zona > timedelta(minutes=30):
                # força retorno gradual à faixa segura
                if zona_critica == 'alta':
                    valor = random.uniform(68, 70)
                else:
                    valor = random.uniform(40, 42)
                tipo_zona = None
                inicio_zona_critica = None
    else:
        tipo_zona = None
        inicio_zona_critica = None

    ultima_freq = valor
    return valor


# Exemplo de uso:
simular_dados(meses=1, intervalo_minutos=1)
