---
name: video-editing
description: Video editing workflow for clipping, trimming, cutting, merging, extracting audio, adding subtitles, resizing, and transcoding with ffmpeg. Use when a user asks to edit or process video/audio files (e.g., "剪掉前10秒", "合并两个视频", "加字幕", "转成竖屏短视频", "导出无损/小体积版本").
---

# Video Editing Skill

Follow this workflow to complete video editing tasks reliably with `ffmpeg`/`ffprobe`.

## 1) Confirm intent and constraints

Gather:
- Input file paths
- Exact edit operations (trim/cut/merge/subtitle/resize/speed)
- Target format and quality constraints (MP4/H.264, social media limits, max size)
- Whether re-encoding is allowed or stream copy is preferred

If any parameter is missing, infer sensible defaults and state them clearly before running commands.

## 2) Inspect media first

Always inspect source media:

```bash
ffprobe -hide_banner -i INPUT
```

Record:
- Duration
- Video codec, resolution, fps
- Audio codec, sample rate, channels
- Time base and keyframe sensitivity if frame-accurate cuts are needed

## 3) Use operation-specific recipes

Read `references/ffmpeg-recipes.md` and pick the smallest correct recipe.

Priority:
1. Stream copy (`-c copy`) when no re-encode is needed
2. Re-encode only when filter/compatibility requires it
3. Keep commands reproducible and explicit

## 4) Verify output

After each edit:
- Probe output with `ffprobe`
- Check duration delta matches expected result
- Spot-check playback start/end
- Confirm audio is present and synced

## 5) Deliverables

Provide:
- Final output path(s)
- Exact command(s) used
- Brief quality/compression notes
- Optional alternate export command (higher quality or smaller size)

## Notes

- Prefer MP4 (`libx264` + `aac`) for broad compatibility.
- For social short videos, prefer even dimensions and `yuv420p` pixel format.
- Avoid unnecessary generation loss by minimizing repeated re-encodes.
