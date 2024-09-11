import os
import subprocess
import shutil
from datetime import datetime

# Define directories
image_dir = "assets/images"
audio_dir = "assets/audio"
output_dir = "assets/temp"
output_final_dir = "assets/outputs"

# Add a timestamp to ensure uniqueness of the final output filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
final_output = os.path.join(output_final_dir, f"final_output_{timestamp}.mp4")

# Create output and temp directories if they don't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

if not os.path.exists(output_final_dir):
    os.makedirs(output_final_dir)

# Function to get the duration of an audio file using ffprobe
def get_audio_duration(audio_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    return float(result.stdout)

# Get list of image and audio files
images = sorted([f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
audios = sorted([f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav'))])

# Generate video for each image/audio pair using ffmpeg
for idx, (image, audio) in enumerate(zip(images, audios)):
    image_path = os.path.join(image_dir, image)
    audio_path = os.path.join(audio_dir, audio)
    output_video = os.path.join(output_dir, f"output_{idx+1:03d}.mp4")

    # Get the duration of the audio file
    audio_duration = get_audio_duration(audio_path)

    # ffmpeg command to generate video for each image/audio pair
    ffmpeg_command = [
        'ffmpeg', '-y', '-i', image_path,  # No loop, just show image once
        '-i', audio_path,  # Audio plays only once
        '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k',
        '-pix_fmt', 'yuv420p', '-shortest', output_video  # Use -shortest to match video length to audio length
    ]

    print(f"Creating video: {output_video}")
    subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# Create file list for concatenation
filelist_path = os.path.join(output_dir, 'filelist.txt')
with open(filelist_path, 'w') as f:
    for idx in range(len(images)):
        video_file = f"output_{idx+1:03d}.mp4"  # Only the filename is needed
        f.write(f"file '{video_file}'\n")  # Ensure the correct format is used

# ffmpeg command to concatenate the videos with the overwrite flag (-y)
concat_command = [
    'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', filelist_path, '-c', 'copy', final_output
]

print(f"Concatenating videos into: {final_output}")
concat_process = subprocess.run(concat_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Debugging: Print the output and error from ffmpeg
print(concat_process.stdout.decode('utf-8'))
print(concat_process.stderr.decode('utf-8'))

# Check if the final output was successfully created
if os.path.exists(final_output):
    print(f"{final_output} created successfully.")
    
    # Remove the output_dir (assets/temp) directory after final_output.mp4 is created
    try:
        shutil.rmtree(output_dir)
        print(f"Deleted the directory: {output_dir}")
    except Exception as e:
        print(f"Error deleting {output_dir}: {e}")
else:
    print(f"Failed to create {final_output}, skipping deletion of {output_dir}.")
