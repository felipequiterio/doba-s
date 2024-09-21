from pytube import YouTube
from pydub import AudioSegment
import os
import asyncio
from utils.log import get_custom_logger

# Inicializando o logger
logger = get_custom_logger('CONVERTER')

async def download_youtube_video_to_wav(video_url, output_file_path):
    loop = asyncio.get_event_loop()

    try:
        # Fazer download do vídeo do YouTube (executar bloqueante no executor)
        logger.info("Iniciando download do vídeo do YouTube: %s", video_url)
        yt = await loop.run_in_executor(None, YouTube, video_url)
        stream = yt.streams.filter(only_audio=True).first()

        if stream is None:
            logger.error("Erro: Não foi encontrado stream de áudio para o vídeo: %s", video_url)
            return

        # Baixar o stream de áudio em formato MP4 de forma assíncrona
        logger.info("Baixando o stream de áudio para o arquivo temporário.")
        audio_file = await loop.run_in_executor(None, stream.download, "temp_audio.mp4")
        logger.info("Download concluído.")

        # Converter o arquivo MP4 para WAV de forma assíncrona
        logger.info("Convertendo o arquivo MP4 para WAV.")
        audio = await loop.run_in_executor(None, AudioSegment.from_file, audio_file, "mp4")
        await loop.run_in_executor(None, audio.export, output_file_path, "wav")
        logger.info("Arquivo convertido para WAV: %s", output_file_path)

        # Remover o arquivo temporário MP4
        os.remove(audio_file)
        logger.info("Arquivo temporário removido.")

    except Exception as e:
        logger.error("Erro durante o processo de conversão: %s", e)

# Exemplo de uso:
async def main():
    await download_youtube_video_to_wav("https://www.youtube.com/watch?v=KUxTstoFd1Q", "output_file.wav")

# Executar a função principal
if __name__ == "__main__":
    asyncio.run(main())
