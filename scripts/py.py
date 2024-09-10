from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

# Create the root element
mlt = Element('mlt', {'LC_NUMERIC': 'C', 'version': '7.27.0'})

# Create profile
profile = SubElement(mlt, 'profile', {
    'description': 'automatic', 'width': '1920', 'height': '1080', 'progressive': '1',
    'sample_aspect_num': '1', 'sample_aspect_den': '1', 'display_aspect_num': '16',
    'display_aspect_den': '9', 'frame_rate_num': '24', 'frame_rate_den': '1', 'colorspace': '709'
})

# Create bumper video chain
chain_bumper = SubElement(mlt, 'chain', {'id': 'chain_bumper', 'out': '00:00:06.458'})
SubElement(chain_bumper, 'property', {'name': 'length'}).text = '00:00:06.500'
SubElement(chain_bumper, 'property', {'name': 'eof'}).text = 'pause'
SubElement(chain_bumper, 'property', {'name': 'resource'}).text = 'assets/bumpers/bumper.mp4'
SubElement(chain_bumper, 'property', {'name': 'mlt_service'}).text = 'avformat'
SubElement(chain_bumper, 'property', {'name': 'meta.media.nb_streams'}).text = '2'

# Create music chain with fade out
chain_music = SubElement(mlt, 'chain', {'id': 'chain_music', 'out': '00:00:10.000'})
SubElement(chain_music, 'property', {'name': 'length'}).text = '00:00:10.000'
SubElement(chain_music, 'property', {'name': 'eof'}).text = 'pause'
SubElement(chain_music, 'property', {'name': 'resource'}).text = 'assets/bumpers/bumper.mp3'
SubElement(chain_music, 'property', {'name': 'mlt_service'}).text = 'avformat'
SubElement(chain_music, 'property', {'name': 'meta.media.nb_streams'}).text = '1'

# Add fade out effect to the music
filter_fadeout = SubElement(chain_music, 'filter', {'id': 'fadeout'})
SubElement(filter_fadeout, 'property', {'name': 'mlt_service'}).text = 'volume'
SubElement(filter_fadeout, 'property', {'name': 'shotcut:filter'}).text = 'fadeOutVolume'
SubElement(filter_fadeout, 'property', {'name': 'level'}).text = '00:00:07.000=0;00:00:10.000=-60'
SubElement(filter_fadeout, 'property', {'name': 'fadeOut'}).text = '1'

# Create playlist for video
playlist_video = SubElement(mlt, 'playlist', {'id': 'playlist_video'})
SubElement(playlist_video, 'entry', {'producer': 'chain_bumper', 'in': '00:00:00.000', 'out': '00:00:06.458'})

# Create playlist for audio
playlist_audio = SubElement(mlt, 'playlist', {'id': 'playlist_audio'})
SubElement(playlist_audio, 'entry', {'producer': 'chain_music', 'in': '00:00:00.000', 'out': '00:00:10.000'})

# Create the tractor
tractor = SubElement(mlt, 'tractor', {'id': 'tractor0', 'title': 'Bumper + Music'})
SubElement(tractor, 'track', {'producer': 'playlist_video'})
SubElement(tractor, 'track', {'producer': 'playlist_audio', 'hide': 'video'})

# Create transitions (optional)
transition = SubElement(tractor, 'transition', {'id': 'transition0'})
SubElement(transition, 'property', {'name': 'a_track'}).text = '0'
SubElement(transition, 'property', {'name': 'b_track'}).text = '1'
SubElement(transition, 'property', {'name': 'mlt_service'}).text = 'mix'
SubElement(transition, 'property', {'name': 'always_active'}).text = '1'
SubElement(transition, 'property', {'name': 'sum'}).text = '1'

# Format the XML
xml_str = xml.dom.minidom.parseString(tostring(mlt)).toprettyxml(indent="  ")

# Save to file
with open("bumper_music_with_fadeout.mlt", "w") as f:
    f.write(xml_str)

print("MLT file created: bumper_music_with_fadeout.mlt")
