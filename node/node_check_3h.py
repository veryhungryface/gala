import paramiko
import os
import json
from multiprocessing import Pool, Manager
from discord_webhook import DiscordWebhook

head = ''
comm = 'sudo gala-node status'

def process_server(args, result_queue, comm):
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
        return server['label']
    except paramiko.SSHException:
        print(f"Unable to establish SSH connection to server {server['label']}")
        return server['label']
    except Exception as e:
        print(f"An error occurred on server {server['label']}: {str(e)}")
        return server['label']

def send_discord_notification(failed_servers):
    if failed_servers:
        webhook_url = 'https://discord.com/api/webhooks/960069009540259860/2UkmDlsEg-ymQ2L0X2GbifywiJwyWOWPJWf409ojtBMUi6VJ6RhptTCuFaIK5gsqVF94'
        message = f"이상 노드 발견!\n\n {', '.join(failed_servers)}"
        webhook = DiscordWebhook(url=webhook_url, content=message)
        webhook.execute()

if __name__ == "__main__":
    # SSH 접속 정보 설정
    ssh_username = "root"  # 항상 root로 설정

    # 파일에서 JSON 데이터 읽기
    with open('servers.json', 'r') as json_file:
        data = json.load(json_file)

    # 문제가 있는 서버를 저장할 리스트
    failed_servers = []

    # 병렬 작업을 위한 Pool과 Manager 생성
    with Pool() as pool, Manager() as manager:
        # 공유 큐 생성
        result_queue = manager.Queue()
        # 각 서버에 대해 병렬로 작업 수행
        args_list = [(server, ssh_username) for server in data if server['label'].startswith(head)]
        pool.starmap(process_server, [(arg, result_queue, comm) for arg in args_list])

        # 수행 결과 가져오기
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())

    # 결과를 label 오름차순으로 정렬
    results.sort(key=lambda x: x['label'])

    if failed_servers:
        send_discord_notification(failed_servers)

