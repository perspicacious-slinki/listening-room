# Listening Room

An encrypted page for private listening, designed for deployment to
github pages.

## How it works

GitHub Pages only serves static files, so there's no login auth
available. What this does instead: your audio files are encrypted (AES-256-GCM)
and committed to the repo, using a private key generated from your password.
The browser uses the same process to decrypt.

Files sitting on GitHub are encrypted. A direct link to `songs/track-one.mp3.enc` 
gets encrypted cyphertext. Without the password, there's no way to access
the audio data.


## 1. Prepare your tracks

Create:
- ```bash mkdir conv_songs raw_songs```
- Audio files (With metadata, and names starting with track number) in `raw_songs/`
- ```bash conv.sh``` to populate `conv_songs/`

`conv.sh`, is provided to convert audio to 192kbps mp3 using ffmpeg.

**File size:** GitHub blocks files over 100MB and warns above ~50MB.
Use [Git LFS](https://git-lfs.com) for very large files.


## 2. Create the track manifest

The page uses a json track manifest to determine display order and provide basic metadata.
By default, tracks are sorted in to albums by ID3 tag data. Ordering is done alphabetically,
hence the suggestion to begin track names with the track number - eg `03 - third track.mp3`

```bash
python3 trackbuilder.py
```

Do a quick manual check of the resulting `tracks.json` file - the order of this file is the display
order on the page.


## 3. Encrypt

```bash
pip install cryptography
python3 encrypt.py --password "your pass here" --input conv_songs --manifest tracks.json --out songs
```

This encrypts tracks to `.enc` files and encrypts the manifest to `manifest.json.enc`, placing the 
results in the `songs/` directory.


## 4. Deploy to GitHub Pages

```bash
git init
git add *
git commit -m "listening room"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Source → Deploy from branch →
main / (root)**. Site will go live in a minute or two at
`https://YOUR_USERNAME.github.io/YOUR_REPO/`.


## Changing the password or adding tracks later

Do steps 1-4 again. Note that in the event of a password change, all
audio tracks will be modified. There's no clean way to remove historical files
without deleting the repository and starting over.

## Notes

- The unlocked session is remembered for the current browser tab
  (`sessionStorage`) so you're not re-typing the password on every click.
- The `SALT_HEX` in `index.html` and `encrypt.py` must match.
  Only change it if you specifically want to; if you do,
  update both files together.
- Playback starts after the file is fetched and decrypted, so there's a
  brief pause before audio begins.
