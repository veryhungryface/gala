import paramiko
import requests
from concurrent.futures import ThreadPoolExecutor

#노드 상태 검사 커맨드
comm = "sudo gala-node status"

err_detect = []
err_detect_ip = []

def count_label(label):
    if label[:3] == "FMT":
        n = 3
    elif label[:3] == "FM_":
        n = 2    
    else:
        n = 1
    return n    
        
def ssh_command(ip, label):
    key = paramiko.RSAKey.from_private_key_file("./authenticate/sk8bty.pem")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, port=22, username='root', pkey=key)
        
    except Exception as e:
        err_detect.append(f'{label}:::  {e}')
        err_detect_ip.append(f"{ip}")
    
    stdin, stdout, sdterr = ssh.exec_command(comm)
    result = stdout.readlines()
    
    c = count_label(label)
    for sentence in result[-count_label(label):]:
        #print(sentence)
        if sentence.strip() == "Gala Node is not running":
            err_detect.append(f"{label}::: Gala Node is not running")
            err_detect_ip.append(f"{ip}")      
    
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
    
    ############################
    #   SSH 접속 & 커맨드입력    #
    ############################
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(ssh_command, ip_label['ip'], ip_label['label']) for ip_label in IPs_LABELs]
    
    err_detect.sort()
       
    
    print("\n\n######### 비정상 노드 검사 결과 #########\n")
    
    if len(err_detect) == 0:
        print("모든 노드 정상 작동 중!")
    
    if len(err_detect) != 0:
        for err in err_detect:
            print(err)
        print("\n비정상 노드 ",len(err_detect),"개 발견")
        
    print(f"\n\n{len(IPs_LABELs)}개 인스턴스 검사 완료!\n")

command()
