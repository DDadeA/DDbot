from gtts import gTTS
from navertts import NaverTTS

from os import listdir

async def makevoice(_text, _voice, out_path, _args=[]):
    if _voice == voicelist[0]: await googleTTS(_text, out_path, _args)
    elif _voice == voicelist[1]: await naverTTS(_text, out_path, _args)
    else: VITSTTS(_text, out_path)

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
    for file in files:
        if '.pth' in file:
            model_path = f'tts_model/{voice}/{file}'
        if '.json' in file:
            config_path = f'tts_model/{voice}/{file}'
    
    try:
        global model
        model[voice] = (MoeGoeTTS(model_path, config_path))
        
        return [i+'-'+str(voice) for i in model[-1].speakers]
    except:
        print('|안내| - 모델을 불러오는 중 문제가 발생하였습니다.')

async def VITSTTS(_text, voice, out_path):
    global model
    
    model.wav(text=_text, speaker_id = speaker_id, filepath=out_path)


voicelist = ['Google_man', 'Naver_woman']
voice = voicelist[0]

if len(listdir('tts_model'))>0:
    print('|안내| - VITS 모델이 발견되었습니다. 해당 모델 사용을 위한 모듈을 불러옵니다.')
    import git
    git.Git(".").clone('https://github.com/DDadeA/moegoe_tts')
    
    from moegoe_tts import MoeGoeTTS
    
    
    for model_name in listdir('tts_model'):
        speakers = LoadVoice(model_name)
        for speaker in speakers:
            voicelist.append(speaker)
    print('|안내| - 모듈을 성공적으로 불러왔습니다!')

print(f'|안내| - 음성 모델 발견: {voicelist}\
      \n|안내| - 기본 음성 모델: {voice}')