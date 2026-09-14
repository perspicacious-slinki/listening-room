#!/usr/bin/env python3
"""
Encrypts mp3 files (and the track manifest) for the Listening Room page.

Usage:
    python3 encrypt.py --password "your password" --input raw_songs --manifest tracks.json --out songs

  --input     folder containing your plain, unencrypted mp3 files
  --manifest  a small JSON file describing the tracks (see tracks.example.json)
  --out       where to write the encrypted output (normally the songs/ folder
              that you commit to the repo — the plain mp3s and tracks.json
              should NOT be committed)

The SALT below must match the SALT_HEX constant in index.html. A default is
already provided and matches out of the box. Only change it if you want a
different salt (then update both places).
"""

import argparse
import json
import os
import sys

try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    sys.exit("Missing dependency. Run: pip install cryptography --break-system-packages")

SALT_HEX = "7fe777fe532640d970260de6faa0f670"  # must match SALT_HEX in index.html
ITERATIONS = 300000


def derive_key(password: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes.fromhex(SALT_HEX),
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(key: bytes, plaintext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    iv = os.urandom(12)
    ciphertext = aesgcm.encrypt(iv, plaintext, None)
    return iv + ciphertext  # index.html expects [12-byte iv][ciphertext+tag]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--password", required=True)
    ap.add_argument("--input", required=True, help="folder of plain mp3 files")
    ap.add_argument("--manifest", required=True, help="tracks.json describing the tracks")
    ap.add_argument("--out", required=True, help="output folder (e.g. songs/)")
    args = ap.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        tracks = json.load(f)

    key = derive_key(args.password)
    os.makedirs(args.out, exist_ok=True)

    out_manifest = []
    for t in tracks:
        src_path = os.path.join(args.input, t["file"])
        if not os.path.isfile(src_path):
            sys.exit(f"Missing file: {src_path}")

        with open(src_path, "rb") as f:
            plain = f.read()

        enc_name = t["file"] + ".enc"
        enc_bytes = encrypt_bytes(key, plain)
        with open(os.path.join(args.out, enc_name), "wb") as f:
            f.write(enc_bytes)

        out_manifest.append({
            "title": t["title"],
            "file": enc_name,
            **({"note": t["note"]} if t.get("note") else {}),
        })
        print(f"encrypted {t['file']} -> {enc_name}  ({len(plain)/1024/1024:.1f} MB)")

    manifest_bytes = json.dumps(out_manifest).encode("utf-8")
    enc_manifest = encrypt_bytes(key, manifest_bytes)
    with open(os.path.join(args.out, "manifest.json.enc"), "wb") as f:
        f.write(enc_manifest)

    print(f"\nWrote {len(out_manifest)} track(s) + manifest.json.enc to {args.out}/")
    print("Commit the contents of that folder. Do NOT commit your plain mp3s or tracks.json.")


if __name__ == "__main__":
    main()
