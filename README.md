# Image-to-Video Pipeline POC with TTS

POC to turn still images and narration text into a final, narrated video using [CoQui TTS](https://github.com/coqui-ai/TTS).

---

Prereqs:

* Python 3.8+ and the following libraries:

```bash
pip install TTS pyyaml
```

Depending on the model you use, you may need to download certain packages. For the default, you'll need espeak and espeak-ng:

```bash
sudo apt install espeak espeak-ng
```

## Using the tool

First, add the images you'd like to use to the **assets/images** folder.

Then update **assets/script_mapping.yaml** to define each image and it's narration text.

```bash
python scripts/create_video.py
```

By default, this will:

* Generate audio for each text entry using Coqui TTS
* Create a short video for each image/audio pair
* Optionally prepend/append bumber videos stored in assets/bumpers
* Concatenate everything into a final video stored at outputs/final_output.mp4

### Optional flag

If you've previously generated audio/image clips that you don't want to overwrite, add the **-k** flag when you run the script and the .wav files stored in **assets/audio** will not be overwritten. They will be concatenated into the final video.

```bash
python scripts/create_video.py -k
```

## Choosing a TTS Model and Speaker

By default, the script uses **tts_models/en/vctk/vits**, which is a multi-speaker model. You can select a voice using the **speaker** parameter:

```python
tts.tts_to_file(text="Hello world", speaker="p225", file_path="out.wav")
```

To list al available speakers, at the Python command line run:
```python
print(tts.speakers)
```
