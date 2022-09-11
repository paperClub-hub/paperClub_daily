import os
from tqdm import tqdm
import json
import glob,time
import numpy as np
import datetime
import psutil
import pandas as pd


####  服务器gpu + cpu + 内存 + 显存监控
####  2021-4-28, qunosen



def linux_cmd_process(cmd):

    return os.popen(cmd).read()


def get_gpu_cost_info():
    "gpu信息"
    gpu_info_cmd = "nvidia-smi -L"
    gpu_info_log = linux_cmd_process(gpu_info_cmd)


    "gpu在用Process ID 和消耗显存"
    # gpu_process_id_cmd = "nvidia-smi -q | grep -E 'Process ID|Used GPU Memory' | awk -v FS=':' '{print $2}' | xargs echo"
    gpu_process_id_cmd = "nvidia-smi -q | grep -E 'Process ID|Used GPU Memory' | awk -v FS=':' '{print $2}' | awk '{print $1}'| xargs echo"
    gpu_process_id_log = linux_cmd_process(gpu_process_id_cmd)
    # process_ids = np.array(gpu_process_id_log.split())[np.array([1,3,5])] #### 在用gpu 进程id
    # id_memory_cost = np.array(gpu_process_id_log.split())[np.array([0,2,4])] ### gpu开销
    # gpu_process_id_log = [(f"process_id: {id}, gpu_cost(MB): {m}") for id,m in zip(process_ids,id_memory_cost)]


    "gpu使用率"
    gpu_use_cmd = "nvidia-smi -q -d UTILIZATION | grep -A 5 'GPU Utilization' | tail -1 | awk '{print $3}'"
    gpu_use_log = int(linux_cmd_process(gpu_use_cmd))/100.0 ### gpu使用百分比, 0.32


    "内存占用百分比"
    memory_use_cmd = "nvidia-smi -q -d MEMORY | grep -E 'Total|Used'|head -2|awk '{print $3}'|xargs|awk '{print $2/$1}'"
    memory_use_log = float(linux_cmd_process(memory_use_cmd)) ##内存使用百分比, 0.637535

    "#获取内存详细信息"
    memory_info_cmd = "nvidia-smi -q -d MEMORY |grep -E 'Total|Used|Free'|head -3|awk '{print $3}'|xargs echo"
    memory_info_log = list(map(int, linux_cmd_process(memory_info_cmd).split())) ### 总显存，已用显存，剩余显存

    "#获取GPU Current 温度:"
    temperature_cmd = "nvidia-smi -q -d Temperature |grep 'GPU Current'|awk '{print $5}'"
    current_temp_log = int(linux_cmd_process(temperature_cmd))


    data = {
        "gpu_info_log" : gpu_info_log,
        "gpu_process_id_log" : gpu_process_id_log,
        "gpu_use_log" : gpu_use_log,
        "memory_use_log" : memory_use_log,
        "memory_info_log" : memory_info_log,
        "current_temp_log" : current_temp_log,

    }

    return data


def get_systerm_cost():
    ##### cpu使用率
    cpuper = psutil.cpu_percent()/100.0
    ##### 系统内存：
    system_memory_use_cmd = "cat /proc/meminfo | grep -E 'MemTotal|MemAvailable|Active' |head -3|awk '{print $2}' | xargs echo"
    system_memory_use_log = linux_cmd_process(system_memory_use_cmd).split()

    # mem = psutil.virtual_memory()
    # memper = mem.percent ### 内存使用率

    data = {
        "CPUPER": cpuper,
        "MemTotal(MB)": system_memory_use_log[0],
        "MemAvailable(MB)": system_memory_use_log[1],
        "MemUsed(MB)": system_memory_use_log[2],
    }

    return data


def MonitorSystem(saveFile=None):
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')

    system_info_dict = get_systerm_cost()
    gpu_info_dict = get_gpu_cost_info()
    
    sys_cpu_used_rate = system_info_dict.get('CPUPER') #### CPU使用率
    sys_total_m = system_info_dict.get('MemTotal(MB)') #### 系统总内存
    sys_used_m = system_info_dict.get('MemUsed(MB)') ### 已用内存
    gpu_used_rate = gpu_info_dict.get('gpu_use_log') ### gpu使用率
    gpu_memory_used_rate = gpu_info_dict.get('memory_use_log') ### 显存使用率
    gpu_total_m = gpu_info_dict.get('memory_info_log')[0] ## gpu总显存MB
    # gpu_used_m =  gpu_info_dict.get('memory_info_log')[1] ## gpu已用显存
    gpu_free_m =  gpu_info_dict.get('memory_info_log')[2] ## gpu可用显存
    gpu_temp = gpu_info_dict.get('current_temp_log') ### gpu温度

    sys_memory_rate = int(sys_used_m)/int(sys_total_m) * 1.0 ### 系统内存使用率
    gpu_template_rate = int(gpu_temp)/100.0 ### gpu温度比率
    gpu_memory_avaible_rate = int(gpu_free_m)/int(gpu_total_m) * 1.0 ### gpu可用显存占比
    
    
    log_line = f'{ts} sys_cpu_used_rate: {sys_cpu_used_rate:.4f}%, sys_memory_rate: {sys_memory_rate:.4f}%, ' \
               f'gpu_used_rate: {gpu_used_rate:.4f}%, gpu_memory_used_rate: {gpu_memory_used_rate:.4f}%, ' \
               f'gpu_memory_avaible_rate: {gpu_memory_avaible_rate:.4f}%, gpu_template_rate: {gpu_template_rate:.4f}%'
    
    #print(log_line)
    
    if saveFile:
        data = {
            "ts":ts,
            "info":[system_info_dict,gpu_info_dict]
        }
        
        # js_data = json.dumps(data, ensure_ascii=False, indent=2)
        print(data,file=open(saveFile,"a"))
    

def loopMonitor(logFile):
    while True:
        MonitorSystem(logFile)
        time.sleep(0.5)
    

    
def logFile2CSV(logFile):
    
    dict = {}
    dict["ts"] = []
    dict["sys_cpu_used_rate"] = []
    dict["sys_memory_rate"] = []
    dict["gpu_used_rate"] = []
    dict["gpu_memory_used_rate"] = []
    dict["gpu_memory_avaible_rate"] = []
    dict["gpu_template_rate"] = []
    CSVFile = os.path.splitext(logFile)[0] + ".csv"
    
    with open(logFile, 'r') as f:
        for line in f.readlines():
            line = eval(line)
            
            ts = line.get('ts')
            sys_cpu_used_rate = line.get('info')[0].get('CPUPER') #### CPU使用率
            sys_total_m = line.get('info')[0].get('MemTotal(MB)') #### 系统总内存
            sys_used_m = line.get('info')[0].get('MemUsed(MB)') ### 已用内存
            gpu_used_rate = line.get('info')[1].get('gpu_use_log') ### gpu使用率
            gpu_memory_used_rate = line.get('info')[1].get('memory_use_log') ### 显存使用率
            gpu_total_m = line.get('info')[1].get('memory_info_log')[0] ## gpu总显存MB
            gpu_free_m =  line.get('info')[1].get('memory_info_log')[2] ## gpu可用显存
            gpu_temp = line.get('info')[1].get('current_temp_log') ### gpu温度
            
            sys_memory_rate = int(sys_used_m)/int(sys_total_m) * 1.0 ### 系统内存使用率
            gpu_template_rate = int(gpu_temp)/100.0 ### gpu温度比率
            gpu_memory_avaible_rate = int(gpu_free_m)/int(gpu_total_m) * 1.0 ### gpu可用显存占比
            
            dict["ts"].append(ts)
            dict["sys_cpu_used_rate"].append(sys_cpu_used_rate)
            dict["sys_memory_rate"].append(sys_memory_rate)
            dict["gpu_used_rate"].append(gpu_used_rate)
            dict["gpu_memory_used_rate"].append(gpu_memory_used_rate)
            dict["gpu_memory_avaible_rate"].append(gpu_memory_avaible_rate)
            dict["gpu_template_rate"].append(gpu_template_rate)
        
        DF = pd.DataFrame.from_dict(dict)
        DF.to_csv(CSVFile)
        

        

if __name__=="__main__":

    logFile = "log.txt"
    print("程序运行 ....")    
    
    #loopMonitor(logFile)
    
    if not os.path.exists(logFile):
        print( "loopMonitor ...")
        loopMonitor(logFile)
    
    else:
        print("logFile transform ...")
        logFile2CSV(logFile)

