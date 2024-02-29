import json

# 파일에서 데이터 읽기
with open('servers.txt', 'r') as file:
    data = []
    lines = file.readlines()
    for line in lines[1:]:  # 첫 번째 줄은 레이블, IP, 패스워드 정보를 설명하므로 무시
        label, ip, password = line.strip().split('\t')
        record = {"label": label, "ip": ip, "password": password}
        data.append(record)

# 데이터를 JSON 형식으로 변환
json_data = json.dumps(data, indent=2)

# JSON 데이터를 파일에 저장
with open('servers.json', 'w') as json_file:
    json_file.write(json_data)

print("JSON 파일이 생성되었습니다: servers.json")
