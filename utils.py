import cv2
import math
import logging
import mediapipe as mp


def encontrar_objetos(caminho_video, indices):
    logging.info("encontrar_objetos")

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path='pose_landmarker_heavy.task'),
        running_mode=VisionRunningMode.VIDEO,
        num_poses=1
    )

    cap = cv2.VideoCapture(caminho_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    objetos = {}
    frame_atual = 0

    with PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            timestamp_ms = int((frame_atual / fps) * 1000)
            
            altura, largura, _ = frame.shape
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            resultado = landmarker.detect_for_video(mp_image, timestamp_ms)
            
            if resultado.pose_landmarks:
                landmarks = resultado.pose_landmarks[0]
                
                lm_mao = landmarks[indices["mao"]]
                mao_y  = int(lm_mao.y * altura)
                mao_x  = int(lm_mao.x * largura)

                lm_cotovelo = landmarks[indices["cotovelo"]]
                cotovelo_y  = int(lm_cotovelo.y * altura)
                cotovelo_x  = int(lm_cotovelo.x * largura)

                lm_quadril = landmarks[indices["quadril"]]
                quadril_y = int(lm_quadril.y * altura)
                quadril_x  = int(lm_quadril.x * largura)
                
                objetos[f"{frame_atual}"] = {
                    "mao_y": mao_y,
                    "cotovelo_y": cotovelo_y,
                    "quadril_y": quadril_y,
                    "mao_x": mao_x,
                    "cotovelo_x": cotovelo_x,
                    "quadril_x": quadril_x
                }
                
            frame_atual += 1

    cap.release()

    return objetos

def encontrar_frames_arremesso(objetos):
    frame_soltura_str = min(objetos, key=lambda f: objetos[f]["mao_y"])
    frame_soltura = int(frame_soltura_str)

    frames_ordenados = sorted(
        [int(f) for f in objetos.keys() if int(f) <= frame_soltura], reverse=True
    )

    frame_preparo = frame_soltura
    maior_y_cintura = 0

    for f in frames_ordenados:
        cintura_atual = objetos[str(f)]["quadril_y"]

        if cintura_atual > maior_y_cintura:
            maior_y_cintura = cintura_atual
            frame_preparo = f

    return frame_preparo, frame_soltura

def calc_ang(caminho_video, objetos, frame_preparo, mao_arremesso):
    logging.info("calc_ang")

    cap = cv2.VideoCapture(caminho_video)

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_preparo)
    ret_preparo, img_preparo = cap.read()

    cap.release()

    f_key = str(frame_preparo)

    mao_y = objetos[f_key]["mao_y"]
    cotovelo_y = objetos[f_key]["cotovelo_y"]
    quadril_y = objetos[f_key]["quadril_y"]

    mao_x = objetos[f_key]["mao_x"]
    cotovelo_x = objetos[f_key]["cotovelo_x"]
    quadril_x = objetos[f_key]["quadril_x"]

    cv2.circle(img_preparo, (mao_x, mao_y), 2, (0, 255, 0), -1)
    cv2.circle(img_preparo, (cotovelo_x, cotovelo_y), 2, (0, 255, 0), -1)
    cv2.circle(img_preparo, (quadril_x, quadril_y), 2, (0, 255, 0), -1)

    d_x = abs(mao_x - cotovelo_x)
    d_y = abs(mao_y - cotovelo_y)
    
    ang_rad = math.atan(d_x / d_y)
    ang = math.degrees(ang_rad)

    rounded = round(ang, 2)
    
    cv2.line(img_preparo, (cotovelo_x, cotovelo_y), (mao_x, mao_y), (0, 255, 0), 3)
    cv2.line(img_preparo, (mao_x, mao_y), (mao_x, cotovelo_y), (0, 255, 0), 3)
    cv2.line(img_preparo, (cotovelo_x, cotovelo_y), (mao_x, cotovelo_y), (0, 255, 0), 3)
    
    if mao_arremesso == 'mao_esq':
        cv2.putText(img_preparo, f"{rounded}°", (mao_x - 10, cotovelo_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 3)
    else:
        cv2.putText(img_preparo, f"{rounded}°", (mao_x + 10, cotovelo_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 3)

    cv2.imwrite(f"{caminho_video}_result.png", img_preparo)

    return f"{caminho_video}_result.png", rounded

def avalia_resultado(ang): 
    limites = {
        'p_superior': 15.11,
        'p_inferior': 0.7
    }

    if ang > limites["p_superior"]:
        resultado_abs = ang - limites["p_superior"]
        resultado_var = (ang / limites["p_superior"]) - 1
        resultado_txt = f"Seu arremesso está {resultado_abs} graus do esperado, oque represeta {resultado_var} de desvio"
        return {
            "resultado_abs": resultado_abs, 
            "resultado_var": resultado_var, 
            "resultado_txt": resultado_txt,
            "resultado_code": "NP" 
        }

    elif ang < limites["p_superior"]:
            resultado_abs = limites["p_inferior"] - ang
            resultado_var = (ang / limites["p_inferior"]) - 1
            resultado_txt = f"Seu arremesso está {resultado_abs} graus do esperado, oque represeta {resultado_var} de desvio"
            return {
                "resultado_abs": resultado_abs, 
                "resultado_var": resultado_var, 
                "resultado_txt": resultado_txt,
                "resultado_code": "NP"
            }

    else: 
        return {
            "resultado_txt": f"Seu arremesso ({ang}) está dentro da faixa esperada {limites['p_inferior']} e {limites['p_superior']}",
            "resultado_code": "P"
        }