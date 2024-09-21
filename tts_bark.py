import os
os.environ["XDG_CACHE_HOME"] = os.path.expanduser("~/.cache")

import torch
import torchaudio
from TTS.api import TTS

print("Carregando o modelo BARK TTS...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/bark", progress_bar=False, gpu=True)

print("Carregando a embedding do locutor...")
speaker_embedding = tts.get_speaker_embedding("data/tts/reference.wav")

print("Realizando a síntese de fala...")
texto = """E aos que pensam que me derrotaram respondo com a minha vitória. Era escravo do povo e hoje me
liberto para a vida eterna. Mas esse povo de quem fui escravo não mais será escravo de ninguém. Meu
sacrifício ficará para sempre em sua alma e meu sangue será o preço do seu resgate. Lutei contra a
espoliação do Brasil. Lutei contra a espoliação do povo. Tenho lutado de peito aberto. O ódio, as
infâmias, a calúnia não abateram meu ânimo. Eu vos dei a minha vida. Agora vos ofereço a minha morte.
Nada receio. Serenamente dou o primeiro passo no caminho da eternidade e saio da vida para entrar na
História"""

wav = tts.tts(
    texto,
    speaker_embedding=speaker_embedding,
    language="pt",
    emotion="neutral",
)

print("Salvando o áudio...")
torchaudio.save("bark_tts.wav", torch.tensor(wav).unsqueeze(0), sample_rate=tts.synthesizer.output_sample_rate)
