from TTS.api import TTS

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
text = "Welcome to your automated video project. In this workshop, you will learn to deploy FortiGates to your AWS Cloud environment."
tts.tts_to_file(text=text, file_path="intro.mp3")
