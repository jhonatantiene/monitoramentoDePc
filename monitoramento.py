import psutil
import platform
import requests
import time
import socket
import wmi
import subprocess

API_URL = "http://127.0.0.1:80/status"

uso_disco = None 
    
def formatar_tempo_ligado():
    segundos_ligado = int(time.time() - psutil.boot_time())

    dias = segundos_ligado // (24 * 3600)
    segundos_ligado = segundos_ligado % (24 * 3600)
    horas = segundos_ligado // 3600
    segundos_ligado %= 3600
    minutos = segundos_ligado // 60
    segundos = segundos_ligado % 60

    return f"{dias}d {horas}h {minutos}m {segundos}s"

def verificar_servicos():
    servicos = []
    sistema = platform.system()
    
    if sistema == "Linux":
        try:
            resultado = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--no-pager'],
                capture_output=True, text=True, check=True
            )
            return resultado.stdout
        except subprocess.CalledProcessError as e:
            return f"Erro ao listar serviços: {e}"
    
    elif sistema == "Windows":
        try:
            c = wmi.WMI()
            for servico in c.Win32_Service():
                if servico:
                    servicos.append({
                        "nome": servico.Name,
                        "status": servico.State,
                        "inicializacao": servico.StartMode
                    })
            return servicos
        except Exception as e:
            return f"Erro ao acessar serviços WMI: {e}"
    else:
        return "Sistema não suportado"

def coletar_dados():
    sistema = platform.system()
    uso_disco = None
    
    if sistema == "Windows":
        try:
            c = wmi.WMI()
            for disk in c.Win32_PerfFormattedData_PerfDisk_PhysicalDisk():
                if disk.Name == "_Total":
                    uso_disco = min(float(disk.PercentDiskTime), 100.0)
                    break
        except Exception as e:
            uso_disco = f"Erro ao coletar: {e}"
    else:
        uso_disco = "Não disponível"


    caminho_disco = 'C://'
    if sistema != "Windows":
        caminho_disco = '/'

    disco = psutil.disk_usage(caminho_disco)

    return {
        "hostname": socket.gethostname(),
        "sistema": sistema,
        "cpu": psutil.cpu_percent(),
        "memoria": psutil.virtual_memory().percent,
        "espaco em disco total": f"{round(disco.total / (1024 ** 3), 2)} GB",
        "espaco em disco usado": f"{round(disco.used / (1024 ** 3), 2)} GB",
        "espaco em disco usado (%)": f"{disco.percent}%",
        "espaco em disco livre": f"{round(disco.free / (1024 ** 3), 2)} GB",
        "uso do disco": f"{uso_disco}%",
        "Tempo ligado": formatar_tempo_ligado(),
        "servicos": verificar_servicos()
    }

while True:
    dados = coletar_dados()
    try:
        response = requests.post(API_URL, json=dados, timeout=5)
        print(f"Enviado com sucesso! | Status: {response.status_code}")
    except Exception as e:
        print(f"Erro:{e}")
    time.sleep(5)