# Image-to-Video Pipeline POC with TTS

POC to turn still images and narration text into a final, narrated video using [Piper](https://github.com/rhasspy/piper/tree/master) and [CoQui](https://github.com/coqui-ai/TTS) TTS frameworks.

---

## Prereqs:

* Python 3.8+ and the following libraries:

### CoQui

If using Coqui AI:

```bash
pip3 install TTS pyyaml
```

Depending on the model you use, you may need to download certain packages. For the default, you'll need espeak and espeak-ng:

```bash
sudo apt install espeak espeak-ng
```
### Piper

If using Piper AI, you can install using pip:

```bash
pip3 install piper-tts
```

Then, download the .onnx and .onnx.json [files](https://github.com/rhasspy/piper/blob/master/VOICES.md) associated with the desired voice to the **voices** directory and run:

```bash
mkdir voices

echo 'Hello world!' | piper \
  --model voices/en_US-lessac-medium \
  --output_file hello_world.wav
```

There is also the option to utilize a GPU via the onnxruntime-gpu package, so if opting for that you'll need to download it:
```bash
.venv/bin/pip3 install onnxruntime-gpu
```

## Using the tool

First, add the images you'd like to use to the **assets/images** folder.

Then update **assets/script_mapping.yaml** to define each image and it's narration text. See the existing file for an example.

Then, run the script and specify which framework you want to use (CoQui or Piper):

```bash
python3 scripts/create_video.py --coqui

python3 scripts/create_video.py --piper
```

By default, this will:

* Generate audio for each text entry using specified TTS framework
* Create a short video for each image/audio pair
* Optionally prepend/append bumber videos stored in assets/bumpers
* Concatenate everything into a final video stored at outputs/final_output.mp4

### Optional flag

If you've previously generated audio/image clips that you don't want to overwrite, add the **-k** flag when you run the script and the .wav files stored in **assets/audio** will not be overwritten. They will be concatenated into the final video.

```bash
python scripts/create_video.py -k
```

## Choosing a TTS Model and Speaker

### CoQui

By default, the script uses **tts_models/en/vctk/vits**, which is a multi-speaker model. You can select a voice using the **speaker** parameter:

```python
tts.tts_to_file(text="Hello world", speaker="p225", file_path="out.wav")
```

To list al available speakers, at the Python command line run:
```python
print(tts.speakers)
```

### Piper

To test out different voices, there are samples located [here](https://rhasspy.github.io/piper-samples/)

The associated .onnx and .onnx.json files associated with the voice you want to use can then be downloaded from [here](https://github.com/rhasspy/piper/blob/master/VOICES.md). By default, the script will look for these files in the **voices** folder. 

However, you can specify alternate preferred download locations and voice model files in the script:

```python
...
# === Piper configuration ===
piper_bin = "piper"   #path to Piper binary
model_path = "voices/en_GB-aru-medium.onnx"
model_config_path = "voices/en_GB-aru-medium.onnx.json"
output_wav = "final_output.wav"
...
```

