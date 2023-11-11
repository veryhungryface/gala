import paramiko
import requests
from concurrent.futures import ThreadPoolExecutor
import os

servername_start = os.environ.get('COMMAND_INPUT1', '')  # 환경 변수에서 명령어를 가져옵니다.
comm = 'sudo gala-node status'

results =[]

        
def ssh_command(ip, label):

    key = paramiko.RSAKey.from_private_key_file("./authenticate/sk8bty.pem")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # print(f"인스턴스({label}) 작업 중.")
    ssh.connect(ip, port=22, username='root', pkey=key)

    stdin, stdout, sdterr = ssh.exec_command(comm)
    result = stdout.readlines()
    
    # "Workload Status:" 이후의 부분을 가져오기
    result_trans = []

    workload_status_index = None
    for i, element in enumerate(result):
        if element.startswith('Workload Status:'):
            workload_status_index = i
            break

    if workload_status_index is not None and workload_status_index + 1 < len(result):
        result_trans.append(result[workload_status_index + 2:])
    
    data = result_trans[0][0]
    space_str = ' '*len(f"-->{label} : ")
    r = space_str.join(result_trans[0])
    
    results.append(f"-->{label} : {r}")
    
    ssh.close()

def command():
    # VULTR API
    vultrapi= "M7ADD652O7BFJOKWKCBJZAB4INNPUDUYQVRQ"

    # 인스턴스 정보 가져오기
    url = "https://api.vultr.com/v2/instances"
    headers = {"Authorization": "Bearer {}".format(vultrapi),
            "Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    instances = response.json()['instances']

    IPs_LABELs = [{'ip': instance['main_ip'], 'label': instance['label']} for instance in instances]

    if len(servername_start)==0:
        IPs_LABELs_filter = IPs_LABELs    
    else:
        IPs_LABELs_filter = [entry for entry in IPs_LABELs if entry['label'].startswith(servername_start)]
    ############################
    #   SSH 접속 & 커맨드입력    #
    ############################

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(ssh_command, ip_label['ip'], ip_label['label']) for ip_label in IPs_LABELs_filter]

    results.sort()
        
    print("\n\n######### 커맨드 실행 결과 #########\n")
    for i in results:
        print(i)
    print(f"\n\n{len(IPs_LABELs_filter)}개 인스턴스 커맨드 실행 완료!")

command()
