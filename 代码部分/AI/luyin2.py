import requests



headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Referer': 'https://robot.ownthink.com/',
}        #  出于习惯加上的请求头，可无


def get_data(text):
  # 请求思知机器人API所需要的一些信息  
    data = {
        "appid": "df012e7077cfc348d0991bf44122645f",
        "userid": "Pluto",
        "spoken": text,
    }
    return data


def get_answer(text):
    # 获取思知机器人的回复信息
    data = get_data(text)
    url = 'https://api.ownthink.com/bot'  # API接口
    response = requests.post(url=url, data=data, headers=headers) 
    response.encoding = 'utf-8'
    result = response.json()
    answer = result['data']['info']['text']
    return answer

