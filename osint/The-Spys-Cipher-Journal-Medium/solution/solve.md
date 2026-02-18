# Solution: The Spy's Cipher Journal

## Difficulty: Medium (400 pts)

## Technique: EXIF Metadata → Base64 Decode → Web Lookup → ROT13

### Steps

1. **Examine the image metadata** — Run `exiftool journal_page.jpg` (or use any EXIF viewer). Look for unusual fields. The `ImageDescription` field contains a Base64-encoded string.

2. **Decode the Base64 string:**

   ```bash
   echo "aHR0cHM6Ly9wYXN0ZWJpbi5jb20vcmF3L1p1UHRrN1R2" | base64 -d
   ```

   This reveals: `https://pastebin.com/raw/ZuPtk7Tv`

3. **Visit the Pastebin URL** — The paste contains a Shadow Council dispatch with an encrypted message:

   ```
   SnagnflPGS{fu4q0j_p0hap1y_3kc0f3q}
   ```
   
   The paste also hints: *"The Shadow Council encrypts with the simplest of ancient ciphers. Shift by 13."*

4. **Apply ROT13 decoding:**

   ```bash
   echo "SnagnflPGS{fu4q0j_p0hap1y_3kc0f3q}" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
   ```

5. **Submit the flag:**

```
FantasyCTF{sh4d0w_c0unc1l_3xp0s3d}
```

### Tools Used

- `exiftool` — EXIF metadata extraction
- `base64` — Base64 decoding
- `tr` or CyberChef — ROT13 decoding
- Web browser — visiting the Pastebin URL
