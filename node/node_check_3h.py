import paramiko
import os
import json
from multiprocessing import Pool, Manager
from discord_webhook import DiscordWebhook

# head = os.environ.get('COMMAND_INPUT1', '')  # 환경 변수에서 명령어를 가져옵니다.
# comm = os.environ.get('COMMAND_INPUT2', '')

head = ''
comm = 'sudo gala-node status'

def process_server(args, result_queue, comm, shared_failed_servers):
    server, ssh_username = args
    try:
        # SSH 세션 생성
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 비밀번호가 없는 경우에만 키 기반 인증 사용
        ssh.connect(server['ip'], username=ssh_username, password=server['password'])

        # 명령 실행
        stdin, stdout, stderr = ssh.exec_command(comm)

        # 결과 추가
        result_queue.put({
            'label': server['label'],
            'result': stdout.read().decode('utf-8')
        })

        # 접속 종료
        ssh.close()

        return None

    except paramiko.AuthenticationException:
        print(f"Failed to authenticate on server {server['label']}")
        shared_failed_servers.append(server['label'])

    except paramiko.SSHException:
        print(f"Unable to establish SSH connection to server {server['label']}")
        shared_failed_servers.append(server['label'])

    except Exception as e:
        print(f"An error occurred on server {server['label']}: {str(e)}")
        shared_failed_servers.append(server['label'])

def send_discord_notification(failed_servers):
    if failed_servers:
        webhook_url = 'https://discord.com/api/webhooks/960069009540259860/2UkmDlsEg-ymQ2L0X2GbifywiJwyWOWPJWf409ojtBMUi6VJ6RhptTCuFaIK5gsqVF94'
        message = f"이상 노드 발견!\n\n {', '.join(failed_servers)}"
        webhook = DiscordWebhook(url=webhook_url, content=message)
        webhook.execute()
        print('discord webhook sended')


if __name__ == "__main__":
     # SSH 접속 정보 설정
    ssh_username = "root"  # 항상 root로 설정

    # Specify the absolute path to the 'servers.json' file
    json_file_path = '/root/my_project/server/servers.json'

    # Open the JSON file
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        
    # 문제가 있는 서버를 저장할 리스트
    failed_servers = []
    # 문제가 있는 서버를 저장할 리스트 (Manager의 리스트 proxy 사용)
    with Manager() as manager:
        shared_failed_servers = manager.list()
        result_queue = manager.Queue()

        # 병렬 작업을 위한 Pool과 Manager 생성
        with Pool() as pool:
            # 각 서버에 대해 병렬로 작업 수행
            args_list = [(server, ssh_username) for server in data if server['label'].startswith(head)]
            pool.starmap(process_server, [(arg, result_queue, comm, shared_failed_servers) for arg in args_list])

        # 결과를 label 오름차순으로 정렬
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())

        failed_servers = list(shared_failed_servers)
        failed_cnt = len(failed_servers)
        server_cnt = len(args_list)
        success_cnt = server_cnt - failed_cnt

        if failed_servers:
            send_discord_notification(failed_servers)