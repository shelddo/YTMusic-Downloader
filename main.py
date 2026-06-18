import os
from unidecode import unidecode
import subprocess
import json
from collections import defaultdict

def normalizar(nome):
    nome = nome.lower()
    nome = unidecode(nome)
    nome = nome.replace('-', ' ')
    nome = nome.replace('_', ' ')
    nome = ''.join(c for c in nome if c.isalnum() or c == ' ')
    return nome.strip()

def musicas_locais(pasta):
    musicas = set()
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(('.mp3', '.m4a', '.wav', '.flac', '.opus', '.aac')):
            nome = os.path.splitext(arquivo)[0]
            musicas.add(normalizar(nome))
    return musicas

def musicas_playlist(url):
    comando = [
        "yt-dlp",
        "--flat-playlist",
        "-J",
        "--cookies", "cookies.txt",
        url
    ]

    resultado = subprocess.run(comando, capture_output=True, text=True)
    dados = json.loads(resultado.stdout)

    titulos = set()
    for video in dados["entries"]:
        titulos.add(normalizar(video["title"]))
    return titulos

def playlist_titulos_links(url):
    comando = [
        "yt-dlp",
        "--flat-playlist",
        "-J",
        "--cookies", "cookies.txt",
        url
    ]

    resultado = subprocess.run(comando, capture_output=True, text=True)
    dados = json.loads(resultado.stdout)

    mapa = defaultdict(list)

    for video in dados["entries"]:
        titulo = normalizar(video["title"])
        link = f"https://www.youtube.com/watch?v={video['id']}"
        mapa[titulo].append(link)

    return mapa

def garantir_pasta_novas(pasta_base):
    pasta_novas = os.path.join(pasta_base, "novas")
    os.makedirs(pasta_novas, exist_ok=True)
    return pasta_novas

def baixar_links(links, pasta_destino, novas=True):
    if novas:
        pasta_novas = garantir_pasta_novas(pasta_destino)
        comando = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--ffmpeg-location", r"C:\ffmpeg\bin",
            "-o", f"{pasta_novas}/%(title)s.%(ext)s",
            #"--cookies", "cookies.txt",
            "-f", "ba/b",
            *links
        ]
    else:
        comando = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--ffmpeg-location", r"C:\ffmpeg\bin",
            "-o", f"{pasta_destino}/%(title)s.%(ext)s",
            #"--cookies", "cookies.txt",
            "-f", "ba/b",
            *links
        ]

    subprocess.run(comando)
    
def baixar_link(link, pasta_destino, novas=True):
    if novas:
        pasta_novas = garantir_pasta_novas(pasta_destino)
        comando = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--ffmpeg-location", r"C:\ffmpeg\bin",
            "-o", f"{pasta_novas}/%(title)s.%(ext)s",
            #"--cookies", "cookies.txt",
            "-f", "ba/b",
            link
        ]
    else:
        comando = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--ffmpeg-location", r"C:\ffmpeg\bin",
            "-o", f"{pasta_destino}/%(title)s.%(ext)s",
            #"--cookies", "cookies.txt",
            "-f", "ba/b",
            link
        ]

    subprocess.run(comando)

if input("Você quer baixar músicas novas para uma playlist? (s/n) ").lower() == 's':
    pasta_musicas = input("Informe o caminho da pasta de músicas: ")
    if input ("É playlist? (s/n) ").lower() == 's':
        playlist_url = input("Insira a URL da playlist: ")
        locais = musicas_locais(pasta_musicas)
        musicas = musicas_playlist(playlist_url)
        mapa_playlist = playlist_titulos_links(playlist_url)

        faltando = musicas - locais

        links_para_baixar = {}

        print(f"Total de {len(faltando)} músicas novas:")
        for m in faltando:
            print(m)
        for musica in faltando:
            if musica in mapa_playlist:
                links_para_baixar[musica] = mapa_playlist[musica]
            else:
                print("Não encontrado:", musica)
        links = []
        for musgas in links_para_baixar:
            links.append(links_para_baixar[musgas][0])
        input("Pressione Enter para iniciar o download...")        
        baixar_links(links, pasta_musicas) 
    else:
        musica = input("Insira a URL da música: ")
        locais = musicas_locais(pasta_musicas)
        input("Pressione Enter para iniciar o download...")        
        baixar_link(musica, pasta_musicas) 
else:
    destino = input("Informe o caminho da pasta destino: ")
    if input ("É playlist? (s/n) ").lower() == 's':
        playlist_url = input("Informe o link da playlist: ")
        musicas = musicas_playlist(playlist_url)
        mapa_playlist = playlist_titulos_links(playlist_url)
        links = []
        for link in mapa_playlist:
            links.append(mapa_playlist[link][0])
        input("Pressione Enter para iniciar o download...")        
        baixar_links(links, destino, False)
        
    else:
        link = input("Informe o link da música: ")
        input("Pressione Enter para iniciar o download...")
        baixar_link(link, destino, False)
        
input("Downloads concluídos. Pressione Enter para sair.")