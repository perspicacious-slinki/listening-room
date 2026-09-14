import json
import os

from pydub.utils import mediainfo

fn = "tracks.json"

files = os.listdir("conv_songs")
tracks = list()
albums = dict()

for fname in files:
    trackname = fname.split("-")[-1].split(".")[0][1:]
    albumname = mediainfo("conv_songs/"+fname)['TAG']['album']
    print(trackname + " - " + albumname)
    albums.setdefault(albumname,[]).append({"title":trackname, "file": fname, "note": albumname})


for album in albums.keys():
    trackdata = albums[album]
    sortedtrackdata = sorted(trackdata,key = lambda d: d['file'])
    for track in sortedtrackdata:
        tracks.append(track)


print(tracks)
with open(fn,"w") as fd:
    fd.write(json.dumps(tracks,indent=2))
