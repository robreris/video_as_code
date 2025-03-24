import os
import subprocess
import shutil
import yaml
import argparse
from TTS.api import TTS

parser = argparse.ArgumentParser()
parser.add_argument('-k', action='store_true')
parser.add_argument('--ls', type=str, help='Value for piper length_scale argument.', default='.85')
parser.add_argument('--ns', type=str, help='Value for piper noise_scale argument.', default='.5')
parser.add_argument('--nw', type=str, help='Value for piper length_scale argument.', default='.45')
parser.add_argument('--piper-voice', type=str, help='Piper voice model. e.g. en_US-kusal-medium', default='en_US-kusal-medium')
model_group = parser.add_mutually_exclusive_group(required=True)
model_group.add_argument('--piper', help="Use Piper model.", action="store_true")
model_group.add_argument('--coqui', help="Use Coqui model.", action="store_true")
args = parser.parse_args()

     
# === Piper configuration ===
piper_bin = "piper"   #path to Piper binary
voice_folder = "voices"  #voice model file location

model_path = voice_folder+"/"+args.piper_voice+".onnx"
model_config_path = voice_folder+"/"+args.piper_voice+".onnx.json"
output_wav = "final_output.wav"

# === Path Configuration ===
image_dir = "assets/images"
audio_dir = "assets/audio"
output_dir = "assets/temp"
output_dir_adj = "assets/temp_adj"
output_final_dir = "outputs"
mapping_file = "assets/script_mapping.yaml"

bumper_path_in = os.path.abspath("assets/bumpers/bumper_in.mp4")
bumper_path_out = os.path.abspath("assets/bumpers/bumper_out.mp4")
final_output = os.path.join(output_final_dir, "final_output.mp4")

# === Create output directories if not present ===
os.makedirs(audio_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_dir_adj, exist_ok=True)
os.makedirs(output_final_dir, exist_ok=True)

target_resolution = None

# === Load script mapping ===
with open(mapping_file, "r") as f:
    script_entries = yaml.safe_load(f)

# === Load Coqui TTS model ===
#tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
#tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)

# === Check if audio is CBR ===
def is_cbr(audio_file):
    ffprobe_command = [
        'ffprobe', '-v', 'error', '-select_streams', 'a:0',
        '-show_entries', 'format=bit_rate',
        '-of', 'default=noprint_wrappers=1:nokey=1', audio_file
    ]
    result = subprocess.run(ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    bitrate_info = result.stdout.decode('utf-8').strip()

    if bitrate_info:
        print(f"🔍 {audio_file} is CBR with bitrate {bitrate_info}")
        return True
    else:
        print(f"⚠️ {audio_file} may be VBR or bitrate info unavailable.")
        return False

# === Convert to CBR if necessary ===
def convert_to_cbr(input_audio, output_audio):
    if is_cbr(input_audio):
        print(f"✅ Skipping conversion for {input_audio}, already CBR.")
        shutil.copy(input_audio, output_audio)
    else:
        print(f"🔄 Converting {input_audio} to CBR → {output_audio}")
        cbr_command = [
            'ffmpeg', '-y',
            '-i', input_audio,
            '-ar', '48000',       # Set sample rate to match your video pipeline
            '-ac', '2',           # Stereo
            '-b:a', '192k',
            '-c:a', 'aac',
            '-fflags', '+bitexact',
            '-avoid_negative_ts', 'make_zero',
            output_audio
        ]
        subprocess.run(cbr_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# === Generate Audio ===
for entry in script_entries:
    image_filename = entry['image']
    text = entry['text']

    print(f"Entry: {entry}")
    print(f"Text: {text}")

    audio_basename = os.path.splitext(image_filename)[0]
    raw_path = os.path.join(audio_dir, f"{audio_basename}_raw.wav")
    final_path = os.path.join(audio_dir, f"{audio_basename}.wav")

    if os.path.exists(final_path) and args.k == True:
        print(f"✅ Audio already exists for {image_filename}, skipping.")
    else:
        if args.piper:
            print("Using Piper model...")
            print(f"🔊 Generating TTS via Piper for {image_filename}: {text}")
            result = subprocess.run(
              [
                     piper_bin, 
                     "--model", model_path, 
                     "--config", model_config_path, 
                     "--output_file", raw_path,
                     "--length_scale", args.ls,        # speed of speech; higher=slower
                     "--noise_scale", args.ns,       # speech pattern variation; lower=flatter
                     "--noise_w", args.nw            # duration/affects timing and rhythm 
              ],            
              input=text.encode('utf-8'),
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE
            )
        elif args.coqui:
            print("Using Coqui model...")
            print(f"🔊 Generating TTS via Coqui for {image_filename}: {text}")
            tts.tts_to_file(text=text, speaker="p225", file_path=raw_path)
        convert_to_cbr(raw_path, final_path)
        os.remove(raw_path)  # Clean up raw file


# === Helper: Get audio duration ===
def get_audio_duration(audio_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    return float(result.stdout)

def reencode_clip(input_path, output_path):
    print(f"🔄 Re-encoding: {input_path} → {output_path}")

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "192k"
    ]

    if target_resolution:
        cmd.extend(["-vf", f"scale={target_resolution}"])

    cmd.append(output_path)

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stderr.decode())

# === Create video clips for each image/audio pair ===
for idx, entry in enumerate(script_entries):
    image_path = os.path.join(image_dir, entry['image'])
    audio_path = os.path.join(audio_dir, os.path.splitext(entry['image'])[0] + ".wav")
    output_video = os.path.join(output_dir, f"output_{idx+1:03d}.mp4")

    if not os.path.exists(image_path) or not os.path.exists(audio_path):
        print(f"❌ Skipping {entry['image']} — image or audio file missing.")
        continue

    duration = get_audio_duration(audio_path)

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', image_path,
        '-i', audio_path,
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        '-c:v', 'libx264', '-tune', 'stillimage',
        '-c:a', 'aac', '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-t', str(duration),
        '-movflags', '+faststart',
        output_video
    ]

    print(f"🎥 Creating video: {output_video}")
    subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Re-encode all generated video clips
for filename in os.listdir(output_dir):
    if filename.endswith(".mp4"):
        input_path = os.path.join(output_dir, filename)
        output_path = os.path.join(output_dir_adj, filename)
        reencode_clip(input_path, output_path)

# === Create filelist for ffmpeg concat ===
filelist_path = os.path.join(output_dir_adj, 'filelist.txt')
with open(filelist_path, 'w') as f:
    if os.path.exists(bumper_path_in):
        f.write(f"file '{bumper_path_in}'\n")

    for idx in range(len(script_entries)):
        video_file = os.path.abspath(os.path.join(output_dir_adj, f"output_{idx+1:03d}.mp4"))
        if os.path.exists(video_file):
            f.write(f"file '{video_file}'\n")
        else:
            print(f"⚠️ Warning: {video_file} not found.")

    if os.path.exists(bumper_path_out):
        f.write(f"file '{bumper_path_out}'\n")

# === Concatenate videos ===
concat_command = [
    'ffmpeg', '-loglevel', 'verbose', '-y',
    '-f', 'concat', '-safe', '0',
    '-i', filelist_path,
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-c:a', 'aac',
    '-b:a', '192k',
    final_output
]

print(f"🧩 Concatenating final video: {final_output}")
concat_process = subprocess.run(concat_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if os.path.exists(final_output):
    print(f"✅ Final video created at: {final_output}")
    shutil.rmtree(output_dir)
    print(f"🧹 Cleaned up temp directory: {output_dir}")
    shutil.rmtree(output_dir_adj)
    print(f"🧹 Cleaned up temp directory: {output_dir_adj}")
else:
    print(f"❌ Final video creation failed.")
