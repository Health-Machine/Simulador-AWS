import threading
import sensores

# thread_sensor_corrente = threading.Thread(target=sensores.sim_corrente)
# thread_sensor_corrente.start()

# thread_sensor_tensao = threading.Thread(target=sensores.sim_tensao)
# thread_sensor_tensao.start()

# thread_sensor_temperatura = threading.Thread(target=sensores.sim_temperatura)
# thread_sensor_temperatura.start()

# thread_sensor_vibracao = threading.Thread(target=sensores.sim_vibracao)
# thread_sensor_vibracao.start()

thread_sensor_pressao = threading.Thread(target=sensores.sim_pressao)
thread_sensor_pressao.start()

# thread_sensor_frequencia = threading.Thread(target=sensores.sim_frequencia)
# thread_sensor_frequencia.start()

# thread_sensor_corrente.join()
# thread_sensor_tensao.join()
# thread_sensor_temperatura.join()
# thread_sensor_vibracao.join()
thread_sensor_pressao.join()
# thread_sensor_frequencia.join()

print("Execução do sensores concluída.")