# Solution: The Spy's Cipher Journal

## Category: OSINT | Difficulty: Medium | Points: 400

## Overview

Extract a hidden URL from image EXIF metadata, visit it to find an encrypted message, then ROT13-decode it to get the flag.

## Given Files

- `challenge/journal_page.jpg` — An image with hidden data in its EXIF metadata.

## Steps

1. **Extract EXIF metadata** — Run `exiftool journal_page.jpg` or use any EXIF viewer. The `ImageDescription` field contains a Base64-encoded string.

2. **Decode the Base64 string**:

   ```bash
   echo "aHR0cHM6Ly9wYXN0ZWJpbi5jb20vcmF3L1p1UHRrN1R2" | base64 -d
   ```

   This reveals: `https://pastebin.com/raw/ZuPtk7Tv`

3. **Visit the Pastebin URL** — The paste contains a Shadow Council dispatch with an encrypted message:

   ```text
   SnagnflPGS{fu4q0j_p0hap1y_3kc0f3q}
   ```

   The paste also hints: *"The Shadow Council encrypts with the simplest of ancient ciphers. Shift by 13."*

4. **Apply ROT13 decoding**:

   ```bash
   echo "SnagnflPGS{fu4q0j_p0hap1y_3kc0f3q}" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
   ```

## Tools Used

- `exiftool` — EXIF metadata extraction
- `base64` — Base64 decoding
- `tr` or CyberChef — ROT13 decoding
- Web browser — visiting the Pastebin URL

## Flag

```text
FantasyCTF{sh4d0w_c0unc1l_3xp0s3d}
```
