import paramiko
import os
import json
from multiprocessing import Pool, Manager

head = os.environ.get('COMMAND_INPUT1', '')  # 환경 변수에서 명령어를 가져옵니다.
comm = os.environ.get('COMMAND_INPUT2', '')

#head = 'FRR_2'
#comm = 'sudo gala-node status'

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



if __name__ == "__main__":
     # SSH 접속 정보 설정
    ssh_username = "root"  # 항상 root로 설정

    # 파일에서 JSON 데이터 읽기
    with open('servers.json', 'r') as json_file:
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

         # 결과에서 ": success"가 포함된 개수 확인
        success_cnt = sum(": success" in result['result'] for result in results)

        # 실패한 서버 수
        failed_cnt = len(failed_servers)
        server_cnt = len(args_list)

        if failed_servers:
            print(f"({success_cnt}) servers were successfully processed.\nBut failed to connect to the following ({failed_cnt}) servers:")
            for failed_server in failed_servers:
                print(f" - {failed_server}")
            print("="*30 + "\n")

        else:
            print(f"[Head name : {head}] \nAll ({success_cnt}) servers were successfully processed.")
            print("="*30 + "\n")

        # 결과 출력
        for result in results:
            print(f"<{result['label']}>")
            print(result['result'])
            print("="*30 + "\n")
