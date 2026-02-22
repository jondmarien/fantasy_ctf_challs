# Solution: The Cartographer's Lost Map

## Category: OSINT | Difficulty: Beginner | Points: 100

## Overview

Identify a castle from a photograph using reverse image search and geolocation clues from the challenge description.

## Given Files

- `challenge/lost_map.jpg` — A photo of a medieval castle on a small island. EXIF metadata has been stripped.

## Steps

1. **Examine the image** — The photo shows a stone castle on a small island where three bodies of water meet, with a highland backdrop. No EXIF GPS data is available.

2. **Reverse image search** — Upload `lost_map.jpg` to Google Images, TinEye, or Yandex. The castle's distinctive appearance (stone bridge, island location, highland setting) returns results identifying it as **Eilean Donan Castle**.

3. **Verify with description clues** — The challenge mentions *"where three great waters meet, on an isle in the highlands of the old world."* Eilean Donan Castle sits at the confluence of three sea lochs (Loch Duich, Loch Long, and Loch Alsh) in the Scottish Highlands. This matches perfectly.

4. **Submit the flag** — The answer is the castle name in snake_case.

## Flag

```text
FantasyCTF{eilean_donan_castle}
```
