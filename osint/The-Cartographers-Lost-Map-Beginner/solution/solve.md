# Solution: The Cartographer's Lost Map

## Difficulty: Beginner (100 pts)

## Technique: Reverse Image Search + Geolocation

### Steps

1. **Examine the image** — `lost_map.jpg` shows a medieval castle on a small island where three bodies of water meet. EXIF metadata has been stripped, so no GPS coordinates are available.

2. **Reverse image search** — Upload the image to Google Images, TinEye, or Yandex. The castle's distinctive appearance (stone bridge, island location, highland backdrop) will return results identifying it as **Eilean Donan Castle**.

3. **Verify** — The description mentions *"where three great waters meet, on an isle in the highlands of the old world."* Eilean Donan Castle sits at the confluence of three sea lochs (Loch Duich, Loch Long, and Loch Alsh) in the Scottish Highlands.

4. **Submit the flag:**

```
FantasyCTF{eilean_donan_castle}
```
