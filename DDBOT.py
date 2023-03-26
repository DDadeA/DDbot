import discord
from os.path import exists
from os import listdir
import time
import PySimpleGUI as sg
from threading import Thread
import requests

from gtts import gTTS
from navertts import NaverTTS

import audio_effects
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio as play_sound


# 필요한 전역 변수 선언
_version = 'v3.2.4'

TOKEN = "{yourtoken}"

VCdict = dict()
whitelist = ['정연호','설로기']

voicelist = ['Google_man', 'Naver_woman']
voice = voicelist[0]
speed = 1.0

audioeffect = {'rate':1.0, 'volume':0.0, 'pitch':0.0}

banTTSWord = [':', '<', '>']


# AUTO UPDATE
# def req_check(req):
#    if not req.status_code == 200:
#        print('> 네트워크 연결을 확인해주세요. 엔터를 누르면 종료됩니다.')
#        input('')
#        exit()

#req = requests.get('{bot_version_path}', auth=('user','pass'))
#req_check(req)

# recent_version = req.text

# if not _version == recent_version:
#    print(f'> 새로운 버전 {recent_version}을 발견했습니다. 업데이트를 진행합니다.')
#    
#    req = requests.get('bot_code_path', auth=('user','pass'))
#    req_check(req)
#    
#    file = open('DDBOT.py', 'w', encoding='utf-8')
#    file.write(req.text.replace('\r', ''))
#    file.close()
#    print('> 업데이트가 완료되었습니다. 프로그램을 다시 시작해주세요. 엔터를 누르면 종료됩니다.')
#    input('')
#    exit()

async def makevoice(_text, _voice, _args):
    if _voice == voicelist[0]: await googleTTS(_text, _args)
    if _voice == voicelist[1]: await naverTTS(_text, _args)

async def googleTTS(_text, _args):
    print('> googleTTS')
    tts = gTTS(text =_text, lang='ko')
    tts.save("out.mp3")
    
async def naverTTS(_text, _args):
    print('> naverTTS')
    tts = NaverTTS(str(_text), speed=int((_args[0]-1)*2.5))
    tts.save('out.mp3')


async def effect_audio(_path, _ae):
    # import audio file
    audio = AudioSegment.from_file(_path, str(_path[-3:]))
    
    if not _ae['rate'] == 1.0: audio = audio_effects.speed_change(audio, speed_changes=_ae['rate'])
    if not _ae['pitch'] == 1.0: audio = audio_effects.pitch_change(audio, _ae['pitch'])
    if not _ae['volume'] == 1.0: audio = audio + _ae['volume']
    
    audio.export("effected.wav", format="wav")


async def commander(message):
    print('> commander')
    command = message.content.split(' ')
    if command[1] in ['목록', 'ahrfhr']:
        # send audio list
        audiolist = ", ".join(listdir('./effect/'))
        await message.channel.send(f'> 시그니쳐 사운드 목록입니다.\n```{audiolist}```')
    elif command[1] in ['play', 'p', 'ㅔ', '재생', 'wotod', '재', 'wo']:
        pass

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Event > on_ready')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,large_image_url='https://imgur.com/df9iPHM', name='ONLINE'))

@client.event
async def on_message(message):
    print('Event > on_message')
    
    global name, tone, rate, whitelist, VCdict
    
    #주제가 -DDbot 인가?
    if not 'DDbot' in message.channel.topic: return
    
    # 봇 본인의 메세지인가?
    if message.author == client.user: return
    
    
    # 메세지 가공
    msg = message.system_content
    
    if not len(message.stickers) == 0:
        msg = str(message.stickers[0]) # Returns the name ofthe sticker item.
        
    for word in banTTSWord:
        msg = msg.replace(word, '')
    
    print(f'final text > \'{msg}\'')
    
    # 명령어인지 체크
    try:
        if msg[:1] in ['e', 'ㄷ']:
            await commander(message)
            return
    except: pass
    
    
    # 화이트리스트인가?
    if message.author.name in whitelist:   pass
    elif message.author.nick in whitelist: pass
    elif whitelist[0] == '':               pass  # 화리가 없는가?
    else: return
    
    # VC 연결
    if not str(message.author.voice.channel.id) in VCdict:
        VCdict[str(message.author.voice.channel.id)] = await message.author.voice.channel.connect(reconnect=True)
        msg = 'start'


    # 특수 사운드 요청인가?
    if exists(f'./effect/{msg}.mp3'):
        audio_path = f'./effect/{msg}.mp3'
    elif exists(f'./effect/{msg}.wav'):
        audio_path = f'./effect/{msg}.wav'
    else:
        ## 일반 메세지 필터
        if message.system_content.startswith('<:'): # removed at BanTTSWord
            msg = '이모티콘'
        if msg.startswith('http'):
            msg = '링크'
            
        ## 메세지 내용을 mp3로 제작.
        await makevoice(msg, voice, [speed]) 
        audio_path = 'out.mp3'
    
    # dict 에서 vc 불러오기
    try: vc = VCdict[str(message.author.voice.channel.id)]
    except: 
        await message.channel.send(f'> {message.author.name}, 당신이 참여한 음성채팅의 존재를 확인할 수 없습니다.')
        return
    
    # 효과 넣기
    await effect_audio(audio_path, audioeffect)
    
    # 이전 소리가 끝날때까지 기다리기
    while vc.is_playing(): time.sleep(0.5)
    
    # 재생
    audio_source = discord.FFmpegPCMAudio('effected.wav')
    vc.play(audio_source, after=None)



def rundiscord():
    client.run(TOKEN)
# 스레드 생성. daemon 스레드는 백그라운드 스레드이며, 프로그램 종료 시 함께 종료됨
thread = Thread(target=rundiscord, args=(), daemon=True)
thread.start()


sg.theme("Darkblue")
layout_r = [[sg.Text('목소리ㅡㅡㅡㅡㅡㅡㅡㅡ', font='default 16'), sg.OptionMenu(values=voicelist, default_value = voicelist[0], size=(30,10), key = 'voice')], 
            [sg.Text('말하기속도ㅡㅡㅡㅡㅡㅡ', font='default 16'), sg.Slider(range=(0.5, 2.0), enable_events= True, default_value=1.0, resolution=0.1, orientation='h', key = 'speed', font = 'default 8')],
            [sg.Text('화이트리스트ㅡㅡㅡㅡㅡ', font='default 16'), sg.Input(default_text = ','.join(whitelist), enable_events= True, key = 'user_list', font = 'default 16', size=(25,10))]
            ]

layout_l = [[sg.Col([[sg.Slider(range=(0.1, 4.0), enable_events= True, default_value=1.0, resolution=0.1, orientation='v', key = 'rate', font = 'default 8')],      [sg.Text('배속', font='default 16')]], expand_x = 8),
             sg.Col([[sg.Slider(range=(-20.0, 20.0), enable_events= True, default_value=0.0, resolution=1.0, orientation='v', key = 'volume', font = 'default 8')], [sg.Text('볼륨', font='default 16')]], expand_x = 8),
             sg.Col([[sg.Slider(range=(-5.0, 5.0), enable_events= True, default_value=0.0, resolution=1.0, orientation='v', key = 'pitch', font = 'default 8')],    [sg.Text('피치', font='default 16')]], expand_x = 8)
            ]]

layout = [  [sg.Text(f'디디 봇 {_version}', font='default 40'), sg.Text('/ \'effect\'라는 폴더에 효과음을 넣어주세요. (mp3, wav)', font='default 10')],
            [sg.Text(' ', font='default 8')],
            [sg.Col(layout_r, p=0), sg.Column([], expand_x = 1), sg.Col(layout_l, p=0)],
            [sg.Text(' ', font='default 8')] ]

window = sg.Window(title = f"DD Bot {_version}", layout=layout, auto_size_text = True, resizable = True)

# GUI
while True:
    event, values = window.read()
    print('window Event > ')
    
    if event == sg.WIN_CLOSED: break
    
    
    # 변수 업데이트
    voice = values['voice']
    speed = float(values['speed'])
    whitelist = window.Element('user_list').get().split(',')
    
    audioeffect['rate'] = float(values['rate'])
    audioeffect['volume'] = float(values['volume'])
    audioeffect['pitch'] = float(values['pitch'])
    
    window.refresh()

for vc in VCdict.values():
    audio_source = discord.FFmpegPCMAudio('./effect/end.wav')
    vc.play(audio_source, after=None)
    time.sleep(6)
    
window.close()
exit()

