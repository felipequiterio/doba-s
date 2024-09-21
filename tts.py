import os
import time
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

print("Loading model...")
config = XttsConfig()
config.load_json("models/xtts2/config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="models/xtts2/", use_deepspeed=True)
model.cuda()

print("Computing speaker latents...")
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["data/tts/reference.wav"])

print("Inference...")
out = model.inference(
    """E aos que pensam que me derrotaram respondo com a minha vitória. Era escravo do povo e hoje me
        liberto para a vida eterna. Mas esse povo de quem fui escravo não mais será escravo de ninguém. Meu
        sacrifício ficará para sempre em sua alma e meu sangue será o preço do seu resgate. Lutei contra a
        espoliação do Brasil. Lutei contra a espoliação do povo. Tenho lutado de peito aberto. O ódio, as
        infâmias, a calúnia não abateram meu ânimo. Eu vos dei a minha vida. Agora vos ofereço a minha morte.
        Nada receio. Serenamente dou o primeiro passo no caminho da eternidade e saio da vida para entrar na
        História""",
    "pt",
    gpt_cond_latent,
    speaker_embedding,
    temperature=0.1, # Add custom parameters here
)
torchaudio.save("xtts.wav", torch.tensor(out["wav"]).unsqueeze(0), 24000)