from collections import defaultdict
import json
import os
import subprocess
from unidecode import unidecode


def normalizar(nome: str):
  if not nome:  # Evita o erro caso o título venha como None
    return ""
  nome = nome.lower()
  nome = unidecode(nome)
  nome = nome.replace("-", " ")
  nome = nome.replace("_", " ")
  nome = "".join(c for c in nome if c.isalnum() or c == " ")
  return nome.strip()


def musicas_locais(pasta):
  musicas = set()
  for arquivo in os.listdir(pasta):
    if arquivo.lower().endswith(
        (".mp3", ".m4a", ".wav", ".flac", ".opus", ".aac")
    ):
      nome = os.path.splitext(arquivo)[0]
      normalizado = normalizar(nome)
      if normalizado:
        musicas.add(normalizado)
  return musicas


def obter_dados_playlist(url):
  """Obtém os dados da playlist uma única vez para evitar chamadas duplas ao yt-dlp."""
  comando = [
      "yt-dlp",
      "--flat-playlist",
      "-J",
      "--cookies",
      "cookies.txt",
      url,
  ]
  resultado = subprocess.run(comando, capture_output=True, text=True)
  try:
    return json.loads(resultado.stdout)
  except json.JSONDecodeError:
    print("Erro ao decodificar o JSON do yt-dlp. Verifique o link ou os cookies.")
    return {"entries": []}


def musicas_playlist(dados):
  titulos = set()
  for video in dados.get("entries", []):
    if video and video.get("title"):  # Garante que o vídeo e o título existem
      titulo_norm = normalizar(video["title"])
      if titulo_norm:
        titulos.add(titulo_norm)
  return titulos


def playlist_titulos_links(dados):
  mapa = defaultdict(list)
  for video in dados.get("entries", []):
    if video and video.get("title") and video.get("id"):
      titulo = normalizar(video["title"])
      link = f"https://www.youtube.com/watch?v={video['id']}"
      if titulo:
        mapa[titulo].append(link)
  return mapa


def garantir_pasta_novas(pasta_base):
  pasta_novas = os.path.join(pasta_base, "novas")
  os.makedirs(pasta_novas, exist_ok=True)
  return pasta_novas


def baixar_links(links, pasta_destino, novas=True):
  if not links:
    return
  if novas:
    pasta_novas = garantir_pasta_novas(pasta_destino)
    saida = f"{pasta_novas}/%(title)s.%(ext)s"
  else:
    saida = f"{pasta_destino}/%(title)s.%(ext)s"

  comando = [
      "yt-dlp",
      "-x",
      "--audio-format",
      "mp3",
      "--audio-quality",
      "0",
      "--ffmpeg-location",
      r"C:\ffmpeg\bin",
      "-o",
      saida,
      "-f",
      "ba/b",
      "--cookies",
      "cookies.txt",
      *links,
  ]
  subprocess.run(comando)


# --- Fluxo Principal ---
if input("Você quer baixar músicas novas para uma playlist? (s/n) ").lower() == (
    "s"
):
  pasta_musicas = input("Informe o caminho da pasta de músicas: ")

  if input("Você quer baixar uma playlist? (s/n) ").lower() == "s":
    playlist_url = input("Insira a URL da playlist: ")

    print("Analisando playlist...")
    dados_playlist = obter_dados_playlist(playlist_url)

    locais = musicas_locais(pasta_musicas)
    musicas = musicas_playlist(dados_playlist)
    mapa_playlist = playlist_titulos_links(dados_playlist)

    faltando = musicas - locais

    links_para_baixar = {}

    print(f"Total de {len(faltando)} músicas novas:")
    for m in sorted(faltando):
      print(m)

    for musica in faltando:
      if musica in mapa_playlist:
        links_para_baixar[musica] = mapa_playlist[musica]
      else:
        print("Não encontrado:", musica)

    links = []
    for musica in links_para_baixar:
      links.append(links_para_baixar[musica][0])

    if links:
      input("Pressione Enter para iniciar o download...")
      baixar_links(links, pasta_musicas, novas=True)
    else:
      print("Nenhuma música nova para baixar.")

  else:
    print("Cole os links das músicas (um por linha).")
    print("Pressione Enter em uma linha vazia para finalizar.")

    links = []
    while True:
      link = input("> ").strip()
      if not link:
        break
      links.append(link)

    if links:
      input("Pressione Enter para iniciar o download...")
      baixar_links(links, pasta_musicas, novas=True)
    else:
      print("Nenhum link informado.")

else:
  destino = input("Informe o caminho da pasta destino: ")

  if input("Você quer baixar uma playlist? (s/n) ").lower() == "s":
    playlist_url = input("Informe o link da playlist: ")

    print("Analisando playlist...")
    dados_playlist = obter_dados_playlist(playlist_url)

    mapa_playlist = playlist_titulos_links(dados_playlist)

    links = []
    for musica in mapa_playlist:
      links.append(mapa_playlist[musica][0])

    if links:
      input("Pressione Enter para iniciar o download...")
      baixar_links(links, destino, novas=False)
    else:
      print("Nenhum link válido encontrado na playlist.")

  else:
    print("Cole os links das músicas (uma por linha).")
    print("Pressione Enter em uma linha vazia para finalizar.")

    links = []
    while True:
      link = input("> ").strip()
      if not link:
        break
      links.append(link)

    if links:
      input("Pressione Enter para iniciar o download...")
      baixar_links(links, destino, novas=False)
    else:
      print("Nenhum link informado.")

input("Downloads concluídos. Pressione Enter para sair.")