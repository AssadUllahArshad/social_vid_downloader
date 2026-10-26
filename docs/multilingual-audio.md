# Source-driven multilingual audio

The shared provider pipeline now separates video quality from source audio selection. YouTube Video/Shorts, Facebook Video/Reels, Instagram Video/Reels, TikTok and Snapchat Spotlight use the same inventory, session validation, mux planning and final verification. Provider availability and indexing rules are unchanged. No language landing pages, AI translation, password collection or Snapchat Story tool were added.

## Audio inventory

Extraction returns `audio_tracks` and `supports_dual_audio`. Each track has an opaque ID, normalized `language_code`, `language_name`, source-derived original/default/descriptive/dubbed flags, codec, bitrate when supplied, a readable label, and `origin: "source"`. URLs, native selectors, cookies and request headers remain private.

Only audio-bearing, non-DRM, supported direct HTTP formats are considered. Alternate languages can come from audio-only formats, separate combined video/audio formats, or FFprobe-measured streams inside one source file. Codec/bitrate variants are grouped rather than advertised as additional languages. Subtitles and top-level video-language hints do not create audio options. Untagged progressive variants do not prove an extra language when identified audio already exists. Missing audio language remains unknown; a sole unknown source audio stream may be labeled Original without falsely setting its `is_original` metadata flag.

YouTube's installed yt-dlp extractor exposes original/default preferences, language codes and format notes. Those are retained. Embedded stream metadata is isolated: an unidentified second stream never inherits the first stream's language, codec, role or bitrate. One bounded combined-source header inspection is performed when the extractor has not already exposed alternatives; unavailable metadata is never inferred.

Each quality lists its compatible `audio_track_ids`, `default_audio_track_id`, `audio_containers` and `supports_dual_audio`. The UI uses these values, with no fixed language menu. Single-track videos show a compact audio summary; multiple-track videos expose audio selection and, where compatible, Single Audio / Dual Audio controls. Original/default source audio is initially selected. Changing quality or audio clears the prepared file and reconciles selections.

## Download API

The existing endpoint and identifiers remain compatible:

```json
{
  "sessionId": "<32-character extraction session ID>",
  "formatId": "<20-character returned quality ID>",
  "audio_mode": "dual",
  "audio_track_ids": ["<returned primary audio ID>", "<returned secondary audio ID>"]
}
```

Omitting the new fields uses the quality's default source audio. `single` selects one track; `dual` requires two; `multi` accepts two to eight tracks for future advanced clients. The production UI exposes single and dual modes. Duplicate IDs and repeated known base languages are rejected. Unknown-language tracks require genuine distinct source evidence; no language is guessed. All selections are validated against the short-lived extraction session before a job is created. Existing short-lived sessions and silent videos retain their supported path. Extraction caches use an audio-aware version namespace.

The queued response identifies the planned container and selected audio. Ready responses describe verified output audio, including its actual default flag and its separate `source_is_default` flag. The selected primary audio is written as the default output stream; a source-default secondary track is not mislabeled as the output default.

Error codes include `audio_track_unavailable`, `second_audio_track_unavailable`, `dual_audio_not_supported`, `duplicate_audio_track`, `duplicate_audio_language`, `invalid_audio_selection`, `audio_mux_failed`, and `unsupported_container`. Unknown language is valid metadata, not a reason to fabricate a language or reject a usable stream. Raw FFmpeg errors are not exposed.

## Files and containers

FFmpeg explicitly maps one video stream and each selected audio stream separately with stream copy. Language tags use ISO 639 codes where available; unknown language stays undefined. Track labels, original/descriptive/dubbed dispositions where supported, and the primary default disposition are written. Two languages are never mixed into one stereo track. Identical source inputs are downloaded once, including files with several embedded audio streams. Alternate audio inside combined videos prefers a smaller source video rather than downloading an HD copy solely for its audio.

MP4 is preferred for supported combinations; WebM is retained for compatible WebM codecs. MKV handles otherwise supported combinations such as H.264 video with AAC and Opus audio. The UI shows the resulting container before preparation, explains MKV when necessary, and offers the verified MKV file with its correct MIME type. Browser previews may play only the primary audio stream; users can switch tracks in a compatible downloaded-file player. Browser MKV previews are not promised. Exact default-source file sizes are withheld when remuxing changes the file; alternative audio selections do not reuse a misleading default size.

Filenames contain sanitized language names and a dual/multi-audio suffix as appropriate, with bounded length. Stream copy avoids unnecessary re-encoding. Aggregate input size, final file size, duration, processing time and temporary-file/session expiration remain bounded by the existing settings. Failed preparation removes its directory. Native TikTok inputs remain in one guarded fresh yt-dlp session, with per-input native selector, language, extension and dimension checks; FFmpeg only reads local files.

Before muxing, FFprobe checks the selected local source streams and rejects conflicting language tags before writing output metadata. Before ready, FFprobe checks actual video dimensions, duration and file validity, one video stream, the exact selected audio-stream count, language tags where known, unchanged audio codecs, and primary/secondary default disposition for multiple tracks. Automated tests also compare compressed AAC output packets to their selected source packets.

## Internal observations

Authenticated provider administration contains `supports_multiple_audio_tracks`, `supports_language_metadata`, and `supports_dual_audio_mux`. Unobserved values remain unknown. The first two describe the last extracted source; dual-audio mux is marked verified only after an actual multiple-track output passes FFprobe. These observations are not universal claims about every video on a provider and are not added to public provider capability advertising.

## Validation and live limits

- 166 API tests pass, including all existing provider regressions and 67 new audio cases. Tests cover single/two/three-or-more tracks, language normalization and missing metadata, roles/defaults, filtering and deduplication, session injection rejection, primary/secondary ordering, real single/dual/multi muxing, embedded streams, container fallback, filenames, cleanup, size/duration limits, native TikTok inputs, conflicting source language tags, and truthful capability observations.
- 30 desktop/mobile browser tests pass, including source-only language options, compact unknown-audio fallback, actual selected audio request IDs, saved fixture stream counts/languages, selection resets, MKV messaging, all existing downloader tests, and removed Snapchat Story routes.
- Three content inventory tests, TypeScript, ESLint, Ruff and the production build pass.

A live public YouTube extraction of `$456,000 Squid Game In Real Life!` returned 24 source audio tracks, including English and Hindi, with actual original/default metadata. Two full dual-audio download attempts exceeded the unchanged 180-second budget. The second attempt used the smaller combined-source selection policy. Both failed without returning a ready file, and failed output directories were removed. **No live dual-audio file success is claimed.** Other providers' alternate-audio behavior is verified with extractor fixtures and real local FFmpeg media, not claimed as live multilingual success.

A separate live ordinary-video regression succeeded for [Me at the zoo](https://www.youtube.com/watch?v=jNQXAC9IVRw): a real 506,033-byte MP4 with one H.264 video stream and one AAC audio stream. Its source language metadata was unknown and stayed unknown (`und`); no English-language option was invented.

See [live evidence](multilingual-audio-live-test.json). Implementation follows the installed yt-dlp extractor and [official yt-dlp format documentation](https://github.com/yt-dlp/yt-dlp#format-selection), with explicit mappings, metadata and dispositions as documented by [FFmpeg](https://www.ffmpeg.org/ffmpeg.html).
