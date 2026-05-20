# FFmpeg Recipes for Video Editing

## 1. Trim by time range (fast, no re-encode when keyframes permit)

```bash
ffmpeg -ss START -to END -i input.mp4 -c copy output_trim.mp4
```

## 2. Trim with frame accuracy (re-encode)

```bash
ffmpeg -i input.mp4 -ss START -to END -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k output_trim_precise.mp4
```

## 3. Remove first/last N seconds

```bash
# remove first 10s
ffmpeg -ss 10 -i input.mp4 -c copy output_no_head.mp4

# remove last 8s (needs duration D, output ends at D-8)
ffmpeg -i input.mp4 -to END_TIME -c copy output_no_tail.mp4
```

## 4. Concatenate clips (same codec/params)

Create `list.txt`:

```text
file 'part1.mp4'
file 'part2.mp4'
file 'part3.mp4'
```

Run:

```bash
ffmpeg -f concat -safe 0 -i list.txt -c copy merged.mp4
```

## 5. Add hard subtitles (burn-in)

```bash
ffmpeg -i input.mp4 -vf "subtitles=sub.srt" -c:v libx264 -crf 20 -preset medium -c:a copy output_hardsub.mp4
```

## 6. Add soft subtitles (mov_text in MP4)

```bash
ffmpeg -i input.mp4 -i sub.srt -c:v copy -c:a copy -c:s mov_text output_softsub.mp4
```

## 7. Convert horizontal to vertical short video (center crop)

```bash
ffmpeg -i input.mp4 -vf "scale=1920:-2,crop=1080:1920" -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 128k -pix_fmt yuv420p output_vertical.mp4
```

## 8. Compress while preserving quality

```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset slow -c:a aac -b:a 128k -movflags +faststart output_small.mp4
```

## 9. Extract audio

```bash
ffmpeg -i input.mp4 -vn -c:a mp3 -b:a 192k output.mp3
```

## 10. Mute video

```bash
ffmpeg -i input.mp4 -an -c:v copy output_muted.mp4
```
