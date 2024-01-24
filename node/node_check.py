import paramiko
import json
from multiprocessing import Pool, Manager

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

if __name__ == "__main__":
    # SSH 접속 정보 설정
    ssh_username = "root"  # 항상 root로 설정

    # 파일에서 JSON 데이터 읽기
    with open('servers.json', 'r') as json_file:
        data = json.load(json_file)

    # 문제가 있는 서버를 저장할 리스트
    failed_servers = []

    # head 변수 설정
    head = 'FRR'
    comm = 'gala-node status'
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

    # 결과 출력
    for result in results:
        print(f"Server Label: {result['label']}")
        print("Result:")
        print(result['result'])
        print("="*20 + "\n")

    # 문제가 있는 서버 출력
    for result in results:
        if 'error' in result:
            failed_servers.append(result['error'])
    
    failed_cnt = len(failed_servers)
    server_cnt = len(args_list)
    success_cnt = server_cnt - failed_cnt

    if failed_servers:
        print(f"({success_cnt}) servers were successfully processed.\nBut failed to connect to the following ({failed_cnt}) servers:")
        for failed_server in failed_servers:
            print(f" - {failed_server}")
    else:
        print(f"[Head name : {head}] \nAll ({success_cnt}) servers were successfully processed.")