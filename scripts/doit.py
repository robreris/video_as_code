#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET

def update_mlt(mlt_file, audio_dir, video_dir, image_dir, text_dir=None):
    tree = ET.parse(mlt_file)
    root = tree.getroot()
    
    # Get lists of available media files
    audio_files = sorted([os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".mp3") or f.endswith(".wav")])
    video_files = sorted([os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")])
    image_files = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(".png") or f.endswith(".jpg")])
    
    if text_dir:
        text_files = sorted([os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.endswith(".txt")])

    # Update audio resources
    for chain in root.findall(".//chain"):
        resource = chain.find("property[@name='resource']")
        if resource is not None:
            if resource.text.endswith(".mp3") or resource.text.endswith(".wav"):
                resource.text = audio_files.pop(0) if audio_files else resource.text
            elif resource.text.endswith(".mp4"):
                resource.text = video_files.pop(0) if video_files else resource.text

    # Update image producers
    for producer in root.findall(".//producer"):
        resource = producer.find("property[@name='resource']")
        if resource is not None and resource.text.endswith(".png"):
            resource.text = image_files.pop(0) if image_files else resource.text

    # Optionally, update text resources (if needed in the .mlt file)
    if text_dir:
        for producer in root.findall(".//producer"):
            resource = producer.find("property[@name='resource']")
            if resource is not None and resource.text.endswith(".txt"):
                resource.text = text_files.pop(0) if text_files else resource.text

    # Save the updated XML to a new file
    tree.write("assets/mlt/updated_video_as_code.mlt", encoding='utf-8', xml_declaration=True)

# Paths to your assets directories
mlt_file = "/workspaces/video_as_code/assets/mlt/video_as_code.mlt"
audio_dir = "/workspaces/video_as_code/assets/audio"
video_dir = "/workspaces/video_as_code/assets/video"
image_dir = "/workspaces/video_as_code/assets/images"
text_dir = "/workspaces/video_as_code/assets/text"  # Optional, if you're dealing with text files

# Update the MLT file
update_mlt(mlt_file, audio_dir, video_dir, image_dir, text_dir)
