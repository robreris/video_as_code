import subprocess

# Text to speak
text = "Hello from Piper!"

# Path to Piper binary and voice files
piper_bin = "piper"
model_path = "voices/en_GB-aru-medium.onnx"
config_path = "voices/en_GB-aru-medium.onnx.json"
output_wav = "output.wav"

# Call Piper from the shell
result = subprocess.run(
    [piper_bin, "--model", model_path, "--config", config_path, "--output_file", output_wav],
    input=text.encode('utf-8'),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

if result.returncode == 0:
    print("Audio saved to", output_wav)
else:
    print("Error:", result.stderr.decode())
