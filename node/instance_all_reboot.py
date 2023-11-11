import requests

  
def reboot():
    # VULTR API
    vultrapi= "M7ADD652O7BFJOKWKCBJZAB4INNPUDUYQVRQ"
    
    # 인스턴스 정보 가져오기
    url = "https://api.vultr.com/v2/instances"
    headers = {"Authorization": "Bearer {}".format(vultrapi),
            "Content-Type": "application/json"}

    response = requests.get(url, headers=headers)
    instances = response.json()['instances']

    IDs = [instance['id'] for instance in instances]
    
    
    url = "https://api.vultr.com/v2/instances/reboot"
    headers = {"Authorization": "Bearer {}".format(vultrapi),
            "Content-Type": "application/json"}
    data = {
        "instance_ids": IDs[1:]
    }
    
    # requests.post(url=url, json=data, headers=headers)
    print(f"\n\n{len(IDs)}개 인스턴스 재부팅 요청 완료!")

        
reboot()
