from flask import Flask, request, jsonify
from utils import *

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    data = request.get_json()

    mao_arremesso = data.get("mao_arremesso")
    caminho_video = data.get("caminho_video")

    if mao_arremesso == 'mao_dir':
        indices =  {
            "cotovelo": 14
            , "mao": 16
            , "quadril": 24
        }

    else:
        indices =  {
            "cotovelo": 13
            , "mao": 15
            , "quadril": 23
        }
    
    conexoes = ("cotovelo", "mao")
    calc = ("cotovelo", "mao")

    objetos = encontrar_objetos(caminho_video=caminho_video, indices=indices)

    frame_preparo, frame_soltura = encontrar_frames_arremesso(objetos=objetos)

    caminho_video_resultado, angulo = calc_ang(caminho_video=caminho_video, objetos=objetos, frame_preparo=frame_preparo, mao_arremesso=mao_arremesso)

    resultado = avalia_resultado(ang=angulo)

    return (
        jsonify({
            "caminho_video_resultado": caminho_video_resultado,
            "angulo": angulo,
            "resultado": resultado
        }),
        200,
    )

if __name__ == "__main__":
    app.run(debug=True)