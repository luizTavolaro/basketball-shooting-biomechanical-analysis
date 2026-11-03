import requests

url = "http://127.0.0.1:5000/"
caminho_video = "test3.mp4"
mao_arremesso = "mao_dir"

payload = {"caminho_video": caminho_video, "mao_arremesso": mao_arremesso}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())