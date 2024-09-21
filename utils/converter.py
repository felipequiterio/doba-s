from pydub import AudioSegment
import asyncio
import os
from utils.log import get_custom_logger

logger = get_custom_logger('CONVERTER')

async def convert_mp3_to_wav(mp3_file_path, output_file_path):
    loop = asyncio.get_event_loop()

    if not os.path.exists(mp3_file_path):
        logger.error("Arquivo MP3 não encontrado: %s", mp3_file_path)
        return

    try:
        logger.info("Carregando arquivo MP3: %s", mp3_file_path)
        audio = await loop.run_in_executor(None, AudioSegment.from_mp3, mp3_file_path)

        logger.info("Convertendo MP3 para WAV: %s", output_file_path)
        await loop.run_in_executor(None, audio.export, output_file_path, 'wav')
        
        logger.info("Conversão concluída com sucesso: %s", output_file_path)
        
    except Exception as e:
        logger.error("Erro durante a conversão: %s", e)


async def convert_aif_to_wav(aif_file_path, wav_file_path):
    try:
        audio = AudioSegment.from_file(aif_file_path, format="aiff")
        
        audio.export(wav_file_path, format="wav")
        logger.info(f"Arquivo convertido com sucesso: {wav_file_path}")
    except Exception as e:
        logger.error(f"Erro ao converter o arquivo: {e}")

# Exemplo de uso
async def main():
    await convert_mp3_to_wav("data/tts/vitin.mp3", "data/tts/reference.wav")

# Executar a função principal
if __name__ == "__main__":
    asyncio.run(main())