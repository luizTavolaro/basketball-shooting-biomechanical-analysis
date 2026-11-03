import requests
import pandas as pd

url = "http://127.0.0.1:5000/"

tests = [
    ["tests/test11.mp4", " mao_dir"]
    # ["tests/test1.mp4", "mao_dir"]
    # , ["tests/test2.mp4", "mao_dir"]
    # , ["tests/test3.mp4", "mao_dir"]
    # , ["tests/test4.mp4", "mao_dir"]
    # , ["tests/test5.mp4", "mao_dir"]
    # , ["tests/test6.mp4", "mao_dir"]
    # , ["tests/test7.mp4", "mao_dir"]
    # , ["tests/test8.mp4", "mao_dir"]
    # , ["tests/test9.mp4", "mao_dir"]
    # , ["tests/test10.mp4", "mao_dir"]
    # , ["tests/test11.mp4", "mao_dir"]
    # , ["tests/test12.mp4", "mao_dir"]
    # , ["tests/test13.mp4", "mao_esq"]
    # , ["tests/test14.mp4", "mao_dir"]
    # , ["tests/test15.mp4", "mao_dir"]
]


for t in tests:
    caminho_video = t[0]
    mao_arremesso = t[1] 

    payload = {"caminho_video": caminho_video, "mao_arremesso": mao_arremesso}

    response = requests.post(url, json=payload)
    response_j = response.json()

    ang = response_j['angulo']
    code = response_j['resultado']['resultado_code']

    t.append(ang)
    t.append(code)


df = pd.DataFrame(tests, columns=['video', 'mao_arremesso', 'ang', 'code'])

df.to_csv('tests/tests_tmp.csv')
