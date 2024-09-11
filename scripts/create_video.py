import os
import subprocess

# Define directories
image_dir = "assets/images"
audio_dir = "assets/audio"
output_dir = "assets/temp"
output_final_dir = "outputs"
bumper_path = os.path.abspath("assets/bumpers/bumper.mp4")  # Absolute path to bumper video

# Create output and temp directories if they don't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

if not os.path.exists(output_final_dir):
    os.makedirs(output_final_dir)

# Get list of image and audio files
images = sorted([f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
audios = sorted([f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav'))])

# Check if images and audio files are found
if not images:
    print("No images found in assets/images")
if not audios:
    print("No audio files found in assets/audio")

# Create file list for concatenation
filelist_path = os.path.join(output_dir, 'filelist.txt')
with open(filelist_path, 'w') as f:
    # Check if bumper exists and write it at the beginning
    if os.path.exists(bumper_path):
        print(f"Bumper found at {bumper_path}, adding to the beginning and end.")
        f.write(f"file '{bumper_path}'\n")  # Include the bumper at the beginning
    
    # Add the generated videos
    for idx, (image, audio) in enumerate(zip(images, audios)):
        image_path = os.path.join(image_dir, image)
        audio_path = os.path.join(audio_dir, audio)
        
        # Debug: Print paths to check if files are being processed
        print(f"Processing image: {image_path}")
        print(f"Processing audio: {audio_path}")

        output_video = os.path.join(output_dir, f"output_{idx+1:03d}.mp4")

        # ffmpeg command to generate video for each image/audio pair
        ffmpeg_command = [
            'ffmpeg', '-y', '-i', image_path,  # No loop, just show image once
            '-i', audio_path,  # Audio plays only once
            '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k',
            '-pix_fmt', 'yuv420p', '-shortest', output_video  # Ensure the video length matches the audio length
        ]

        print(f"Creating video: {output_video}")
        ffmpeg_process = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(ffmpeg_process.stdout.decode('utf-8'))
        print(ffmpeg_process.stderr.decode('utf-8'))

        # Write the output video path to the filelist
        if os.path.exists(output_video):
            f.write(f"file '{os.path.abspath(output_video)}'\n")

    # Add bumper.mp4 at the end
    if os.path.exists(bumper_path):
        f.write(f"file '{bumper_path}'\n")  # Include the bumper at the end
    else:
        print(f"Bumper not found at {bumper_path}, skipping.")