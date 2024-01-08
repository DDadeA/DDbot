from gtts import gTTS
from navertts import NaverTTS

from os import listdir

async def makevoice(_text, _voice, out_path, _args=[]):
    print(f"Currently Selected voice = {_voice}")
    
    if _voice == voicelist[0]: await googleTTS(_text, out_path, _args)
    elif _voice == voicelist[1]: await naverTTS(_text, out_path, _args)
    else: 
        name, p = _voice.split('-')
        voice_id = model[p].speakers.index(name)
        
        print(f"Special Voice: {name}, {p}, {voice_id}")
        await VITSTTS(_text, p, voice_id, out_path)

async def googleTTS(_text, out_path, _args):
    print('> googleTTS')
    tts = gTTS(text =_text, lang='ko')
    tts.save(out_path)
    
async def naverTTS(_text, out_path, _args):
    print('> naverTTS')
    tts = NaverTTS(str(_text), speed=int((_args[0]-1)*2.5))
    tts.save(out_path)

model = {}
def LoadVoice(voice):
    files = listdir(f'tts_model/{voice}')
    
    # Get model path
    model_path = ""
    for file in files:
        if '.pth' in file: model_path = f'tts_model/{voice}/{file}'
        
    # Model file doesn't exist
    if model_path == "": raise Exception(f"Can't find model file from tts_model/{voice}")
    
    config_path = f'tts_model/{voice}/{file}'
    
    try:
        global model
        print(model_path, config_path)
        model[voice] = (MoeGoeTTS(model_path, config_path))
        print(model[voice])
        
        return [i+'-'+str(voice) for i in model[voice].speakers]
    except Exception as e:
        print('|안내| - 모델을 불러오는 중 문제가 발생하였습니다.', e)

async def VITSTTS(_text, voice, speaker_id, out_path):
    global model
    
    model[voice].wav(text=_text, speaker_id = speaker_id, filepath=out_path)


voicelist = ['Google_man', 'Naver_woman']
global voice
voice = voicelist[0]

if len(listdir('tts_model'))>0:
    print('|안내| - VITS 모델이 발견되었습니다. 해당 모델 사용을 위한 모듈을 불러옵니다.')
    from moegoe_tts import MoeGoeTTS
    
    
    for model_name in listdir('tts_model'):
        speakers = LoadVoice(model_name)
        for speaker in speakers:
            voicelist.append(speaker)
    print('|안내| - 모듈을 성공적으로 불러왔습니다!')

print(f'|안내| - 음성 모델 발견: {voicelist}\
      \n|안내| - 기본 음성 모델: {voice}')