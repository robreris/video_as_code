import subprocess
import os

# Input and output directories
input_dir = "assets/bumpers"
output_dir = "assets/bumpers-adjusted"

# Optional: target resolution to normalize (or None to keep original)
target_resolution = None  # e.g. "1280x720"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

def reencode_bumper(input_path, output_path):
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

# Process all .mp4 files in the input_dir
for filename in os.listdir(input_dir):
    if filename.endswith(".mp4"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        reencode_bumper(input_path, output_path)

print(f"✅ Done. Fixed bumpers saved in: {output_dir}")

