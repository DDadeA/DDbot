import os
os.system('pip install -r ./requirement.txt')

import discord
from os.path import exists
from os import listdir, mkdir
import time
import PySimpleGUI as sg
from threading import Thread

from tempfile import NamedTemporaryFile
import audio_effects
from pydub import AudioSegment
import configparser

## Utils
from .makevoice import *

_version = 'V5.1'


config = configparser.ConfigParser()
dirlist = listdir()
if not 'effect' in dirlist: mkdir('effect')
if not 'tts_model' in dirlist: mkdir('tts_model')
if not 'config.ini' in dirlist:
    config['INITIAL'] = {
        'BOT_TOKEN': 'YOUR_TOKEN',
        'Whitelist': '너의 이름은,연호'
    }
    config['TTS'] = {'rate':1.0, 'volume':0.0, 'pitch':0.0}
    config['nouse'] = {
        'speed': '1',
    }
    with open('config.ini', 'w', encoding='utf8') as configfile:
        config.write(configfile)
else: config.read('config.ini', encoding='utf8')

TOKEN = config['INITIAL']['BOT_TOKEN']
whitelist = config['INITIAL']['Whitelist'].split(',')
speed = float(config['nouse']['speed'])
audioeffect = {}
audioeffect['rate']   = float(config['TTS']['rate']  )
audioeffect['volume'] = float(config['TTS']['volume'])
audioeffect['pitch']  = float(config['TTS']['pitch'] )

out_path = NamedTemporaryFile().name + '.wav'
effected_path = NamedTemporaryFile().name + '.wav'
VCdict = dict()

banTTSWord = [':', '<', '>']

async def effect_audio(_path, _ae):
    # import audio file
    try:
        audio = AudioSegment.from_file(_path, 'wav')
        
        if not _ae['rate']   == '1.0': audio = audio_effects.speed_change(audio, speed_changes=_ae['rate'])
        if not _ae['pitch']  == '1.0': audio = audio_effects.pitch_change(audio, _ae['pitch'])
        if not _ae['volume'] == '1.0': audio = audio + _ae['volume']
        
        audio.export(effected_path, format="wav")
    except Exception as e:
        print("effect_audio > Error : ", e)
        audio = AudioSegment.from_file(_path, 'mp3')
        
        if not _ae['rate']   == '1.0': audio = audio_effects.speed_change(audio, speed_changes=_ae['rate'])
        if not _ae['pitch']  == '1.0': audio = audio_effects.pitch_change(audio, _ae['pitch'])
        if not _ae['volume'] == '1.0': audio = audio + _ae['volume']
        
        audio.export(effected_path, format="mp3")


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

import struct
bitness = struct.calcsize('P') * 8
target = 'x64' if bitness > 32 else 'x86'
filename = f'./bin/libopus-0.{target}.dll'  
# filename = os.path.join(os.path.dirname(os.path.abspath(discord.__file__)), 'bin', f'libopus-0.{target}.dll')
discord.opus.load_opus(filename)
print(filename)

@client.event
async def on_ready():
    print('Event > on_ready')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,large_image_url='https://imgur.com/df9iPHM', name='ONLINE'))

@client.event
async def on_message(message):
    print('Event > on_message')
    
    global name, tone, rate, whitelist, VCdict
    
    
    # DDbot?
    try: 
        if not 'DDbot' in message.channel.topic: return
    except: return
    
    # is it own message
    if message.author == client.user: return
    
    
    # message refine
    msg = message.system_content
    
    if not len(message.stickers) == 0:
        msg = str(message.stickers[0]) # Returns the name ofthe sticker item.
        
    for word in banTTSWord:
        msg = msg.replace(word, '')
    
    print(f'final text > \'{msg}\'')
    
    
    # is command
    try:
        if msg[:1] in ['e', 'ㄷ']:
            await commander(message)
            return
    except: pass
    
    
    # Whitelist?
    if message.author.name in whitelist:   pass
    elif message.author.nick in whitelist: pass
    elif whitelist[0] == '':               pass  # 화리가 없는가?
    else: return
    
    
    # connect to the voice channel
    if not str(message.author.voice.channel.id) in VCdict:
        VCdict[str(message.author.voice.channel.id)] = await message.author.voice.channel.connect(reconnect=True)
        msg = 'start'


    # special voice?
    if exists(f'./effect/{msg}.mp3'):
        audio_path = f'./effect/{msg}.mp3'
    elif exists(f'./effect/{msg}.wav'):
        audio_path = f'./effect/{msg}.wav'
    else:
        ## message filter
        if message.system_content.startswith('<:'): # removed at BanTTSWord
            msg = '이모티콘'
        if msg.startswith('http'):
            msg = '링크'
            
        ## message to mp3
        await makevoice(msg, voice, out_path) 
        audio_path = out_path
    
    # get voice client
    try: vc = VCdict[str(message.author.voice.channel.id)]
    except: 
        await message.channel.send(f'> {message.author.name}, 당신이 참여한 음성채팅의 존재를 확인할 수 없습니다.')
        return
    
    # Effect
    await effect_audio(audio_path, audioeffect)
    
    # wait until
    while vc.is_playing(): time.sleep(0.5)
    
    # plays
    audio_source = discord.FFmpegPCMAudio(effected_path)
    vc.play(audio_source, after=None)


@lambda _: Thread(target=_, daemon=True).start()
def rundiscord():
    client.run(TOKEN)



sg.theme("DarkGrey1")
layout_r = [[sg.Text('목소리ㅡㅡㅡㅡㅡㅡㅡㅡ', font='default 16'), sg.OptionMenu(values=voicelist, default_value = voicelist[0], size=(30,10), key = 'voice')],
            [sg.Text('말하기속도ㅡㅡㅡㅡㅡㅡ', font='default 16'), sg.Slider(range=(0.5, 2.0), enable_events= True, default_value=1.0, resolution=0.1, orientation='h', key = 'speed', font = 'default 8')],
            [sg.Text('화이트리스트ㅡㅡㅡㅡㅡ', font='default 16'), sg.Input(default_text = ','.join(whitelist), enable_events= True, key = 'user_list', font = 'default 16', size=(25,10))]
            ]

layout_l = [[sg.Col([[sg.Slider(range=(0.1, 4.0), enable_events= True, default_value=1.0, resolution=0.1, orientation='v', key = 'rate', font = 'default 8')],      [sg.Text('배속', font='default 16')]], expand_x = 8),
             sg.Col([[sg.Slider(range=(-20.0, 20.0), enable_events= True, default_value=0.0, resolution=1.0, orientation='v', key = 'volume', font = 'default 8')], [sg.Text('볼륨', font='default 16')]], expand_x = 8),
             sg.Col([[sg.Slider(range=(-5.0, 5.0), enable_events= True, default_value=0.0, resolution=1.0, orientation='v', key = 'pitch', font = 'default 8')],    [sg.Text('피치', font='default 16')]], expand_x = 8)
            ]]

layout = [  [sg.Text(f'{_version} 디디 봇', font='default 40'), sg.Text('/ \'effect\'폴더에 효과음을 넣어주세요☆ (mp3, wav 지원)', font='default 10')],
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

