import os
import subprocess

# Define directories
image_dir = "assets/images"
audio_dir = "assets/audio"
output_dir = "output_videos"

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get list of image and audio files
images = sorted([f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
audios = sorted([f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav'))])

# Generate video for each image/audio pair using ffmpeg
for idx, (image, audio) in enumerate(zip(images, audios)):
    image_path = os.path.join(image_dir, image)
    audio_path = os.path.join(audio_dir, audio)
    output_video = os.path.join(output_dir, f"output_{idx+1:03d}.mp4")

    # ffmpeg command to generate video for each image/audio pair
    ffmpeg_command = [
        'ffmpeg', '-loop', '1', '-i', image_path, '-i', audio_path,
        '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k',
        '-pix_fmt', 'yuv420p', '-shortest', output_video
    ]

    print(f"Creating video: {output_video}")
    subprocess.run(ffmpeg_command)

# Create file list for concatenation
filelist_path = os.path.join(output_dir, 'filelist.txt')
with open(filelist_path, 'w') as f:
    for idx in range(len(images)):
        f.write(f"file 'output_{idx+1:03d}.mp4'\n")

# ffmpeg command to concatenate the videos
final_output = "final_output.mp4"
concat_command = [
    'ffmpeg', '-f', 'concat', '-safe', '0', '-i', filelist_path, '-c', 'copy', final_output
]

print(f"Concatenating videos into: {final_output}")
subprocess.run(concat_command)

print("Final video created successfully.")
