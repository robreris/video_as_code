#!/bin/bash

# Create necessary directories
mkdir -p outputs

# Define your intro/outro video and audio files
intro_video="assets/bumpers/bumper.mp4"
outro_video="assets/bumpers/bumper.mp4"
bumper_audio="assets/bumpers/bumper.wav"

# Define the input images and audio files
images=(assets/images/*.png)
audios=(assets/audio/*.mp3)

# Ensure the number of images matches the number of audio files
if [ ${#images[@]} -ne ${#audios[@]} ]; then
    echo "Error: The number of images and audio files do not match."
    exit 1
fi

# Step 1: Combine the intro video and bumper audio into one video
ffmpeg -i "$intro_video" -i "$bumper_audio" -c:v copy -c:a aac -strict experimental \
    -shortest outputs/intro_with_audio.mp4

# Step 2: Loop over each image/audio pair and create individual video segments
counter=1
for i in "${!images[@]}"; do
    image="${images[$i]}"
    audio="${audios[$i]}"
    output="outputs/segment${counter}.mp4"

    # Get the duration of the audio file
    duration=$(ffmpeg -i "$audio" 2>&1 | grep "Duration" | awk '{print $2}' | tr -d ,)

    # Create a video from the image and audio
    ffmpeg -loop 1 -i "$image" -i "$audio" -c:v libx264 -c:a aac -strict experimental \
        -b:a 192k -pix_fmt yuv420p -shortest -t "$duration" "$output"

    counter=$((counter + 1))
done

# Step 3: Combine the outro video and bumper audio into one video
ffmpeg -i "$outro_video" -i "$bumper_audio" -c:v copy -c:a aac -strict experimental \
    -shortest outputs/outro_with_audio.mp4

# Step 4: Create absolute paths for the intro, segments, and outro
echo "file '$(pwd)/outputs/intro_with_audio.mp4'" > outputs/files.txt  # Add intro
for f in outputs/segment*.mp4; do
    echo "file '$(pwd)/$f'" >> outputs/files.txt  # Add segments
done
echo "file '$(pwd)/outputs/outro_with_audio.mp4'" >> outputs/files.txt  # Add outro

# Step 5: Concatenate all the segments (with intro and outro) into one video
ffmpeg -f concat -safe 0 -i outputs/files.txt -c copy outputs/final_video.mp4

# Clean up individual segments
rm outputs/segment*.mp4
rm outputs/files.txt
rm outputs/intro_with_audio.mp4
rm outputs/outro_with_audio.mp4
