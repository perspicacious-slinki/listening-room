cd raw_songs
for fn in *.mp3; do
    ffmpeg -i "$fn" -c:a libmp3lame -b:a 192k "../conv_songs/$fn" &
done;