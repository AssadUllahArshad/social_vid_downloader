"""Explicit inventory-stage answer ownership; no writing approval or publishing.

Scores surface candidates; the mappings below record task-scope decisions.
Draft canonical owners remain nonpublic. Such consolidations are held with
RESEARCH_REQUIRED until the owner is published; they create no public aliases.
"""
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
REVIEW_DATE=datetime.now(ZoneInfo('Asia/Karachi')).date().isoformat()
p=Path('content/editorial/first-500-inventory.json');rows=json.loads(p.read_text());articles=json.loads(Path('content/editorial/articles.json').read_text());known={r['path']:r for r in rows};public={r['path'] for r in articles if r['status']=='PUBLISHED' and r['indexable']}
merges={
 'analysis-ok-preparation-expired':'temporary-analysis-session',
 'download-preparation-vs-browser-transfer':'verified-file-readiness',
 'filename-extension-html-error-response':'downloaded-file-is-html',
 'browser-save-link-vs-page':'downloaded-file-is-html',
 'download-progress-size-unknown':'verified-file-readiness',
 'video-export-invalid-temp-extension':'incomplete-video-file',
 'video-player-hardware-decoding-artifacts':'hardware-vs-software-decoding',
 'video-player-audio-track-switch-offset':'audio-out-of-sync',
 'video-player-default-track-persistence':'multiple-audio-track-player',
 'video-player-subtitle-switch-resume':'caption-sidecar-not-showing',
 'video-file-random-seek-crash':'incomplete-video-file',
 'video-save-destination-disconnected':'incomplete-video-file',
 'video-archive-partial-cloud-download':'incomplete-video-file',
 'media-player-unsupported-subtitle-codec':'caption-sidecar-not-showing',
 'av1-hardware-bit-depth-profile':'codec-profile-and-level',
 'h264-10bit-decoder-path':'codec-profile-and-level',
 'vp9-profile-alpha-color-depth':'codec-profile-and-level',
 'hevc-tier-level-bitrate-constraints':'codec-profile-and-level',
 'video-pixel-format-vs-codec-name':'video-container-vs-codec',
 'image-sequence-missing-frame-gap':'premiere-numbered-image-sequence-handoff',
 'image-sequence-alpha-associated-resources':'premiere-numbered-image-sequence-handoff',
 'video-alpha-straight-vs-premultiplied':'video-alpha-channel-handoff',
 'video-alpha-luma-matte-vs-channel':'video-alpha-channel-handoff',
 'video-green-screen-vs-alpha-export':'video-alpha-channel-handoff',
 'stereo-video-layout-metadata-mismatch':'stereoscopic-video-vs-spherical-projection',
 'vr180-vs-360-viewing-scope':'spherical-video-vs-flat-playback',
 'video-lens-distortion-vs-aspect-stretch':'video-aspect-ratio',
 'video-rolling-shutter-vs-stabilization-warp':'stabilized-video-crop-and-warp-review',
 'video-banding-vs-block-compression':'video-color-depth',
 'video-grain-vs-digital-noise':'video-bitrate',
 'video-deblocking-vs-detail-recovery':'does-4k-upscale-improve-detail',
 'video-dither-vs-added-source-detail':'video-color-depth',
 'video-letterbox-pixels-vs-player-bars':'video-aspect-ratio',
 'video-pan-scan-vs-letterbox':'video-aspect-ratio',
 'video-poster-frame-vs-first-presented-frame':'thumbnail-vs-video-frame',
 'video-thumbnail-contact-sheet':'thumbnail-vs-video-frame',
 'vfr-average-rate-vs-packet-timing':'variable-frame-rate-editor-drift',
 'interlace-field-order-reversal':'interlaced-vs-progressive',
 'subtitle-ocr-review-image-text':'image-subtitles-vs-editable-text',
 'subtitle-default-vs-forced-track-flags':'forced-subtitles-vs-full-captions',
 'caption-export-after-retiming':'caption-timing-offset',
 'subtitle-edit-frame-rate-conversion':'caption-timing-offset',
 'caption-reading-order-two-speakers':'overlapping-caption-cues',
 'caption-line-length-vs-reading-speed':'caption-line-breaks-and-meaning',
 'audio-time-stretch-vs-pitch-shift':'audio-pitch-shift-vs-playback-speed',
 'audio-phase-delay-vs-polarity':'audio-channel-downmix',
 'audio-crossfade-repeated-word':'audio-click-at-edit-boundary',
 'audio-lossy-generation-cascade':'lossy-vs-lossless-media',
 'audio-mono-sum-vs-single-channel':'audio-channel-downmix',
 'audio-stereo-width-vs-channel-language':'dual-audio-vs-stereo',
 'audacity-stereo-split-vs-mono-mix':'audio-channel-downmix',
 'media-hash-vs-perceptual-match':'archive-checksums',
 'two-pass-encode-vs-two-audio-tracks':'dual-audio-vs-stereo',
 'video-export-two-pass-first-pass-only':'verified-file-readiness',
 'video-buffer-vs-file-cache':'browser-preview-vs-save',
 'browser-download-open-automatically':'browser-preview-vs-save',
 'chrome-download-resume-validity':'incomplete-video-file',
 'windows-hibernate-transfer-interruption':'incomplete-video-file',
 'windows-file-extension-hidden-video':'video-container-vs-codec',
 'network-share-video-copy-verification':'copy-video-to-usb',
 'external-drive-fat32-video-size':'copy-video-to-usb',
 'external-drive-apfs-exfat-video-handoff':'copy-video-to-usb',
 'onedrive-files-on-demand-pin-scope':'windows-cloud-vs-local-file',
 'dropbox-online-only-video-copy':'windows-cloud-vs-local-file',
 'mac-spotlight-video-search-index':'mac-downloads-folder',
 'mac-quarantine-video-open-warning':'safe-browser-download-warning',
 'android-media-scan-gallery-delay':'android-downloads-folder',
 'iphone-low-data-mode-video-transfer':'incomplete-video-file',
 'editing-project-offline-proxy-only':'video-editing-proxy',
 'editing-project-render-preview-vs-master':'archive-source-vs-edit',
 'editing-project-source-audio-split-channels':'dual-audio-vs-stereo',
 'editing-project-caption-companion-version':'caption-timing-offset',
 'editing-project-review-audio-bus-muted':'editor-import-no-audio',
 'editing-project-thumbnail-cache-only':'video-shortcut-vs-retained-file',
 'editing-project-save-before-media-move':'archive-source-vs-edit',
 'editing-project-export-receiving-reimport':'archive-source-vs-edit',
 'editing-project-multiple-sequences-name-collision':'archive-source-vs-edit',
 'video-review-comments-time-reference':'source-timecode-vs-sequence-position',
 'video-archive-case-collision':'archive-manifest',
 'video-archive-unicode-filenames':'archive-manifest',
 'video-archive-checksum-manifest-move':'archive-checksums',
 'video-archive-readonly-verification':'inspect-local-video-with-ffprobe',
 'video-archive-duplicate-content-different-cuts':'archive-source-vs-edit',
 'premiere-safe-margin-guide-vs-export':'video-aspect-ratio',
 'premiere-motion-position-vs-crop':'video-aspect-ratio',
 'final-cut-multicam-active-audio-angle':'final-cut-multicam-angle-sync-review',
 'final-cut-spatial-conform-fit-fill':'video-aspect-ratio',
 'final-cut-rate-conform-vs-retime':'playback-speed-vs-retimed-video',
 'clipchamp-local-project-assets-reconnect':'clipchamp-project-vs-media-backup',
 'clipchamp-export-range-duration':'archive-source-vs-edit',
 'clipchamp-aspect-ratio-crop-review':'video-aspect-ratio',
 'clipchamp-auto-caption-review-export':'automatic-caption-review',
 'obs-remux-recording-vs-transcode':'muxing-vs-transcoding',
 'obs-multiple-audio-recording-tracks':'dual-audio-vs-stereo',
 'ffmpeg-no-overwrite-existing-output':'local-h264-aac-review-transcode',
 'ffmpeg-progress-complete-vs-partial-output':'verified-file-readiness',
 'ffprobe-selected-packet-inspection':'inspect-local-video-with-ffprobe',
 'mediainfo-general-vs-stream-fields':'inspect-local-video-with-ffprobe',
 'handbrake-crop-auto-source-edges':'video-aspect-ratio',
 'handbrake-subtitle-burn-vs-passthrough':'open-vs-closed-captions',
 'vlc-record-button-vs-original-copy':'screen-recording-vs-retained-media',
 'vlc-snapshot-saved-destination':'export-still-frame-vs-video-screenshot',
 'quicktime-save-vs-export-encoding':'muxing-vs-transcoding',
 'resolve-timeline-resolution-export':'does-4k-upscale-improve-detail',
 'resolve-proxy-generator-relink':'video-editing-proxy',
}

merges.update({
 'final-cut-library-storage-location-change':'final-cut-library-media-handoff',
 'final-cut-event-copy-media-choice':'final-cut-library-media-handoff',
 'final-cut-clip-name-vs-source-filename':'archive-manifest',
 'final-cut-custom-metadata-view-handoff':'archive-manifest',
 'final-cut-find-unused-media-scope':'archive-source-vs-edit',
 'final-cut-relink-original-vs-proxy':'video-editing-proxy',
 'final-cut-import-canceled-media-state':'final-cut-incomplete-camera-import',
 'final-cut-photos-import-library-version':'photos-video-export-original-vs-edited',
 'final-cut-detached-audio-source-retention':'copy-selected-local-audio-stream',
 'final-cut-reference-role-export-names':'final-cut-role-stems-vs-mixed-soundtrack',
 'final-cut-voice-isolation-noise-overlap':'final-cut-voice-isolation-component-review',
 'final-cut-stabilization-tripod-choice':'stabilized-video-crop-and-warp-review',
 'final-cut-optical-flow-retime-review':'retimed-video-interpolation-artifacts',
 'final-cut-share-frame-size-vs-project':'video-aspect-ratio',
 'final-cut-roles-subroles-owner-map':'final-cut-role-stems-vs-mixed-soundtrack',
 'final-cut-share-export-xml-vs-movie':'archive-source-vs-edit',
 'final-cut-luma-key-vs-alpha-channel':'video-alpha-channel-handoff',
 'final-cut-mask-effect-tracking-loss':'tracked-video-blur-handoff-review',
 'final-cut-title-safe-area-review':'video-aspect-ratio',
 'premiere-lut-file-move-dependency':'final-cut-camera-lut-vs-creative-look',
 'premiere-optical-flow-render-preview':'retimed-video-interpolation-artifacts',
 'premiere-exposure-clipped-highlight':'hdr-video-washed-out',
 'premiere-export-transcript-vs-captions':'descriptive-transcript-from-captions',
 'premiere-source-timecode-manual-change':'source-timecode-vs-sequence-position',
 'premiere-marker-copy-sequence-context':'source-timecode-vs-sequence-position',
 'premiere-detach-proxy-original-state':'video-editing-proxy',
 'premiere-export-proxy-vs-final-master':'video-editing-proxy',
})


specific_extra = {
 'youtube-source-audio-recording-role':'/guides/general/original-vs-default-audio/',
 'youtube-caption-search-vs-audio-track':'/guides/general/subtitle-language-vs-audio-language/',
 'youtube-thumbnail-auto-selected-vs-custom':'/guides/general/thumbnail-vs-video-frame/',
 'youtube-upload-quality-label-source-encode':'/guides/general/source-provided-format-inventory/',
 'youtube-private-upload-window-close':'/guides/youtube/youtube-scheduled-publication-access/',
 'youtube-offline-premium-device-expiry':'/guides/youtube/youtube-offline-download-vs-media-file/',
 'youtube-recording-date-vs-publish-date':'/guides/youtube/youtube-scheduled-publication-access/',
 'youtube-description-source-permission-note':'/guides/general/video-permission-request/',
 'youtube-short-remix-attribution-handoff':'/guides/youtube/youtube-shorts-remix-source-removal/',
 'youtube-chapter-timestamps-after-owner-trim':'/guides/youtube/youtube-automatic-chapter-review/',
 'tiktok-browser-login-view-boundary':'/guides/tiktok/tiktok-video-temporary-provider-failure/',
 'tiktok-post-photo-alt-text':'/guides/tiktok/tiktok-photo-post-vs-video/',
 'tiktok-sound-volume-original-mix':'/guides/general/dual-audio-vs-stereo/',
 'spotlight-removal-shared-recipient-copy':'/guides/snapchat/spotlight-owner-retention-before-delete/',
 'spotlight-caption-overlay-vs-source-text':'/guides/general/downloaded-video-without-captions/',
 'spotlight-audio-attribution-vs-separated-stem':'/guides/general/dual-audio-vs-stereo/',
}

# Unlike generic software-name permutations, codec framing, particular project
# recovery artifacts and native publication controls remain hypotheses requiring
# primary-source verification. These scoped operations are not auto-approved.
specific={
 'youtube-custom-thumbnail-version':'/guides/general/thumbnail-vs-video-frame/',
 'youtube-shorts-thumbnail-frame-owner':'/guides/general/thumbnail-vs-video-frame/',
 'youtube-shorts-cover-edit-vs-retime':'/guides/general/thumbnail-vs-video-frame/',
 'instagram-grid-preview-crop-vs-reel':'/guides/general/thumbnail-vs-video-frame/',
 'instagram-reel-cover-image-vs-media':'/guides/general/thumbnail-vs-video-frame/',
 'youtube-channel-handle-vs-video-id':'/guides/youtube/youtube-video-copy-direct-link/',
 'tiktok-profile-link-vs-single-video':'/guides/tiktok/tiktok-video-copy-direct-link/',
 'spotlight-public-profile-clip-selection':'/guides/snapchat/snapchat-spotlight-copy-direct-link/',
 'spotlight-short-share-expansion':'/guides/snapchat/snapchat-spotlight-copy-direct-link/',
 'instagram-reel-comment-link-vs-source':'/guides/instagram/instagram-reels-copy-direct-link/',
 'instagram-post-share-to-dm-vs-copy-link':'/guides/instagram/instagram-video-copy-direct-link/',
 'facebook-share-dialog-url-vs-copy':'/guides/facebook/facebook-video-copy-direct-link/',
 'tiktok-share-qr-vs-direct-video-url':'/guides/tiktok/tiktok-video-copy-direct-link/',
 'youtube-comment-pinned-link-source':'/guides/youtube/youtube-video-copy-direct-link/',
 'youtube-processing-abandoned-upload':'/guides/youtube/youtube-upload-quality-processing/',
 'youtube-upload-checks-pending':'/guides/youtube/youtube-upload-quality-processing/',
 'youtube-scheduled-live-vs-upload-premiere':'/guides/youtube/youtube-live-premiere-availability/',
 'youtube-premiere-replay-vs-event':'/guides/youtube/youtube-live-premiere-availability/',
 'youtube-source-removal-retained-copy':'/guides/general/local-file-vs-expired-link/',
 'youtube-title-description-translation-vs-audio':'/guides/general/source-audio-language-selection/',
 'facebook-video-translation-vs-sound':'/guides/general/source-audio-language-selection/',
 'instagram-post-translation-vs-caption-text':'/guides/general/subtitle-language-vs-audio-language/',
 'youtube-language-caption-dub-controls':'/guides/general/subtitle-language-vs-audio-language/',
 'youtube-audio-track-language-notice':'/guides/general/missing-source-language/',
 'youtube-subscription-membership-access':'/guides/general/drm-access-boundary/',
 'youtube-location-restriction-not-codec':'/guides/youtube/youtube-video-temporary-provider-failure/',
 'youtube-caption-edit-new-video-version':'/guides/general/caption-timing-offset/',
 'youtube-clip-source-trim-change':'/guides/youtube/youtube-clip-vs-source-video/',
 'instagram-post-audience-change-existing-share':'/guides/instagram/instagram-video-temporary-provider-failure/',
 'instagram-video-close-friends-boundary':'/guides/instagram/instagram-video-temporary-provider-failure/',
 'facebook-video-group-member-access':'/guides/facebook/facebook-video-temporary-provider-failure/',
 'facebook-video-age-country-audience':'/guides/facebook/facebook-video-temporary-provider-failure/',
 'facebook-page-unpublish-source-access':'/guides/facebook/facebook-video-temporary-provider-failure/',
 'facebook-video-source-removed-shared-post':'/guides/facebook/facebook-video-temporary-provider-failure/',
 'tiktok-video-privacy-after-sharing':'/guides/tiktok/tiktok-video-temporary-provider-failure/',
 'tiktok-private-account-public-link':'/guides/tiktok/tiktok-video-temporary-provider-failure/',
 'tiktok-creator-download-disabled':'/guides/tiktok/tiktok-save-video-controls/',
 'tiktok-series-paywall-boundary':'/guides/general/drm-access-boundary/',
 'whatsapp-linked-device-video-retention':'/guides/whatsapp/whatsapp-exported-video-vs-chat-link/',
 'whatsapp-desktop-video-preview-save':'/guides/whatsapp/whatsapp-exported-video-vs-chat-link/',
 'whatsapp-web-download-destination':'/guides/whatsapp/whatsapp-exported-video-vs-chat-link/',
 'whatsapp-status-audience-change':'/guides/whatsapp/whatsapp-status-visibility-and-expiry/',
}
specific.update(specific_extra)
specific.update({'video-license-version-evidence': '/guides/general/creative-commons-video-license-check/', 'video-third-party-elements-in-permission': '/guides/general/video-permission-request/', 'video-permission-scope-internal-review': '/guides/general/video-permission-request/', 'video-permission-scope-commercial-context': '/guides/general/video-permission-request/', 'video-creative-commons-adaptation-license': '/guides/general/creative-commons-video-license-check/', 'video-creative-commons-music-exception': '/guides/general/creative-commons-video-license-check/', 'video-attribution-link-offline-delivery': '/guides/general/archive-manifest/', 'video-error-report-screenshot-redaction': '/guides/general/safe-error-report/', 'video-source-url-signed-token-report': '/guides/general/safe-error-report/', 'video-filename-person-name-public-share': '/guides/general/video-file-location-privacy/', 'video-location-background-review': '/guides/general/inspect-video-metadata-before-sharing/', 'video-source-id-versus-filename': '/guides/general/archive-manifest/', 'video-source-language-versus-viewer-locale': '/guides/general/source-audio-language-selection/', 'video-proxy-versus-mezzanine': '/guides/general/video-editing-proxy/', 'video-master-versus-distribution-copy': '/guides/general/archive-source-vs-edit/', 'video-restoration-versus-preservation': '/guides/general/archive-source-vs-edit/', 'video-render-cache-versus-delivery': '/guides/general/archive-source-vs-edit/', 'video-muxer-versus-encoder': '/guides/general/muxing-vs-transcoding/', 'source-camera-archive-versus-edit-project': '/guides/general/archive-source-vs-edit/', 'lossless-audio-copy-versus-lossy-stream-copy': '/guides/general/lossy-vs-lossless-media/', 'audio-track-selection-versus-source-separation': '/guides/general/dual-audio-vs-stereo/', 'youtube-studio-editor-save-processing': '/guides/youtube/youtube-studio-edit-version-retention/', 'youtube-studio-revert-original-scope': '/guides/youtube/youtube-studio-edit-version-retention/', 'youtube-audio-library-license-record': '/guides/youtube/youtube-audio-library-handoff/', 'instagram-owner-account-data-export-media': '/guides/general/meta-account-export-vs-public-video-link/', 'facebook-group-audience-video-access': '/guides/facebook/facebook-video-temporary-provider-failure/', 'tiktok-owner-account-data-export-media': '/guides/tiktok/tiktok-data-export-vs-video-backup/', 'video-platform-native-reuse-external-export': '/guides/general/public-url-vs-permission/', 'download-error-stage-support-report': '/guides/general/safe-error-report/', 'download-request-rate-limit-retry': '/guides/general/http-429-rate-limits/', 'ready-file-filename-disposition': '/guides/general/content-disposition-filename/', 'browser-range-request-video-seeking': '/guides/general/byte-range-playback/'})

specific.update({'premiere-native-consolidate-and-archive-projects': '/guides/general/archive-source-vs-edit/', 'premiere-native-move-project-to-another-computer': '/guides/general/archive-source-vs-edit/', 'premiere-native-transfer-projects-from-one-computer-to-another': '/guides/general/archive-source-vs-edit/', 'premiere-native-copy-transcode-or-archive-project': '/guides/general/archive-source-vs-edit/', 'premiere-native-import-images-as-image-sequence': '/guides/general/premiere-numbered-image-sequence-handoff/', 'premiere-native-view-sequence-timecode': '/guides/general/source-timecode-vs-sequence-position/', 'premiere-native-view-source-timecode-in-the-program-monitor': '/guides/general/source-timecode-vs-sequence-position/', 'premiere-native-change-timecode-display-format': '/guides/general/source-timecode-vs-sequence-position/', 'premiere-native-set-clip-timecode-manually': '/guides/general/source-timecode-vs-sequence-position/', 'premiere-native-attach-proxies-to-full-resolution-media': '/guides/general/video-editing-proxy/', 'premiere-native-reconnect-full-resolution-media-to-proxies': '/guides/general/video-editing-proxy/', 'premiere-native-create-low-resolution-clips-for-offline-editing': '/guides/general/video-editing-proxy/', 'premiere-native-set-the-aspect-ratio-of-a-sequence': '/guides/general/video-aspect-ratio/', 'premiere-native-change-clip-speed-using-the-speedduration-option': '/guides/general/playback-speed-vs-retimed-video/', 'premiere-native-change-clip-speed-and-duration-using-time-remapping': '/guides/general/playback-speed-vs-retimed-video/', 'premiere-native-apply-time-interpolation-methods-to-adjust-clip-speed': '/guides/general/retimed-video-interpolation-artifacts/', 'premiere-native-remove-time-remapping-from-a-clip': '/guides/general/playback-speed-vs-retimed-video/', 'premiere-native-change-the-frame-rate-of-a-clip': '/guides/general/frame-rate-vs-resolution/', 'premiere-native-change-the-field-order-of-a-clip': '/guides/general/interlaced-vs-progressive/', 'premiere-native-create-interlaced-or-non-interlaced-clips': '/guides/general/interlaced-vs-progressive/', 'premiere-native-import-caption-file-from-third-party-service': '/guides/general/premiere-import-authorized-srt/', 'premiere-native-extract-audio-from-clips': '/guides/general/copy-selected-local-audio-stream/', 'premiere-native-change-source-audio-channel-mapping': '/guides/general/audio-channel-downmix/', 'premiere-native-use-mono-clips-as-stereo-clips': '/guides/general/mono-vs-stereo-dialogue/', 'premiere-native-automatically-duck-audio': '/guides/general/premiere-music-ducking-dialogue-review/', 'premiere-native-export-a-still-frame': '/guides/general/export-still-frame-vs-video-screenshot/', 'premiere-native-export-a-still-image': '/guides/general/export-still-frame-vs-video-screenshot/', 'final-cut-native-copy-a-project-to-another-mac': '/guides/general/final-cut-library-media-handoff/', 'final-cut-native-view-source-and-project-timecode': '/guides/general/source-timecode-vs-sequence-position/', 'final-cut-native-trim-the-edges-of-the-video-frame': '/guides/general/video-aspect-ratio/', 'final-cut-native-view-and-reassign-roles': '/guides/general/final-cut-role-stems-vs-mixed-soundtrack/', 'final-cut-native-create-custom-roles': '/guides/general/final-cut-role-stems-vs-mixed-soundtrack/', 'final-cut-native-organize-clips-by-roles': '/guides/general/final-cut-role-stems-vs-mixed-soundtrack/', 'final-cut-native-show-audio-components-in-audio-lanes': '/guides/general/final-cut-role-stems-vs-mixed-soundtrack/', 'final-cut-native-organize-the-timeline-with-audio-lanes': '/guides/general/final-cut-role-stems-vs-mixed-soundtrack/', 'final-cut-native-show-video-role-colors': '/guides/general/final-cut-role-stems-vs-mixed-soundtrack/', 'final-cut-native-export-still-images': '/guides/general/export-still-frame-vs-video-screenshot/', 'final-cut-native-send-a-video-frame-to-pixelmator-pro': '/guides/general/export-still-frame-vs-video-screenshot/', 'final-cut-native-locate-source-media-files': '/guides/general/final-cut-library-media-handoff/', 'final-cut-native-consolidate-projects-and-libraries': '/guides/general/final-cut-library-media-handoff/', 'final-cut-native-copy-or-move-items-between-libraries': '/guides/general/final-cut-library-media-handoff/', 'final-cut-native-copy-or-move-a-library': '/guides/general/final-cut-library-media-handoff/', 'final-cut-native-view-and-change-clip-metadata': '/guides/general/archive-manifest/', 'final-cut-native-modify-metadata-views': '/guides/general/archive-manifest/', 'final-cut-native-batch-rename-clips': '/guides/general/archive-manifest/', 'final-cut-native-use-the-luma-keyer-effect': '/guides/general/video-alpha-channel-handoff/', 'final-cut-native-change-a-clips-opacity': '/guides/general/video-alpha-channel-handoff/'})

specific.update({'container-track-title-vs-language': '/guides/general/missing-source-language/', 'container-default-forced-disposition': '/guides/general/forced-subtitles-vs-full-captions/', 'container-attached-picture-vs-video': '/guides/general/thumbnail-vs-video-frame/', 'mp4-audio-only-m4a-extension': '/guides/general/m4a-vs-aac/', 'mp4-moov-box-missing-finalization': '/guides/general/incomplete-video-file/', 'mp4-brand-vs-enclosed-codec': '/guides/general/video-container-vs-codec/', 'wav-riff-size-vs-rf64': '/guides/general/long-wav-export-size-limit/', 'codec-chroma-subsampling-text-edges': '/guides/general/chroma-subsampling/', 'codec-bit-depth-dither-conversion': '/guides/general/video-color-depth/', 'codec-lossless-mode-source-identity': '/guides/general/lossy-vs-lossless-media/', 'audio-channel-language-role-manifest': '/guides/general/dual-audio-vs-stereo/', 'audio-pcm-signed-float-format': '/guides/general/pcm-bit-depth-vs-compressed-audio/', 'video-progressive-faststart-vs-complete': '/guides/general/mp4-faststart-index-placement/', 'video-range-limited-full-washed': '/guides/general/video-color-range/', 'video-audio-downmix-phase-cancel': '/guides/general/audio-channel-downmix/', 'video-captions-audio-description-confusion': '/guides/general/descriptive-audio/', 'caption-audio-description-transcript-role': '/guides/general/descriptive-audio/', 'video-color-tags-missing-source-context': '/guides/general/hdr-vs-sdr-video/', 'movie-checksum-read-error-vs-mismatch': '/guides/general/archive-checksums/', 'movie-copy-name-normalization-collision': '/guides/general/archive-manifest/'})

specific.update({'ready-file-zero-byte-check': '/guides/general/zero-byte-download/', 'video-audio-start-offset-vs-drift': '/guides/general/audio-out-of-sync/', 'video-subtitle-after-cut-overlap': '/guides/general/caption-timing-offset/', 'video-caption-direction-numbers': '/guides/general/caption-bidirectional-text-order/', 'movie-file-locked-during-copy': '/guides/general/windows-video-file-in-use/', 'caption-speaker-label-vs-voice-metadata': '/guides/general/webvtt-voice-annotation-vs-speaker-label/', 'caption-readability-background-contrast': '/guides/general/caption-text-contrast-changing-scenes/', 'caption-rtl-ltr-mixed-script-review': '/guides/general/caption-bidirectional-text-order/', 'caption-download-no-source-resource': '/guides/general/downloaded-video-without-captions/', 'caption-transcript-search-match-timestamp': '/guides/general/descriptive-transcript-from-captions/', 'caption-singular-plural-transcription-error': '/guides/general/automatic-caption-review/', 'caption-code-snippet-transcription': '/guides/general/automatic-caption-review/', 'caption-numeric-unit-review': '/guides/general/automatic-caption-review/', 'caption-translation-proper-name-review': '/guides/general/automatic-caption-review/', 'caption-unintelligible-speech-label': '/guides/general/automatic-caption-review/', 'caption-ellipses-continuation-meaning': '/guides/general/caption-line-breaks-and-meaning/', 'caption-pause-preserving-clean-transcript': '/guides/general/descriptive-transcript-from-captions/', 'caption-sdh-vs-dialogue-translation': '/guides/general/captions-vs-subtitles/', 'caption-duplicate-language-different-purpose': '/guides/general/captions-vs-subtitles/'})

specific.update({
 'chrome-download-dangerous-vs-uncommon':'/guides/general/safe-browser-download-warning/',
 'chrome-automatic-multiple-downloads':'/guides/general/multiple-downloads-browser-permission/',
 'chrome-guest-download-lifetime':'/guides/general/private-browsing-saved-video-files/',
 'safari-private-window-download-location':'/guides/general/private-browsing-saved-video-files/',
 'firefox-private-download-history':'/guides/general/private-browsing-saved-video-files/',
 'samsung-internet-secret-mode-download-scope':'/guides/general/private-browsing-saved-video-files/',
 'safari-download-list-removal-vs-file':'/guides/general/safari-download-history/',
 'firefox-download-panel-open-folder':'/guides/general/firefox-download-history/',
 'edge-smart-screen-warning-review':'/guides/general/safe-browser-download-warning/',
 'brave-shields-site-request-diagnostic':'/guides/general/browser-customization-download-page-failure/',
 'samsung-internet-download-manager-location':'/guides/general/samsung-internet-download-location/',
 'embedded-inapp-browser-external-open':'/guides/general/in-app-browser-vs-external-browser/',
 'iphone-files-downloads-provider-location':'/guides/general/icloud-drive-vs-local-storage/',
 'iphone-save-video-photos-incompatible':'/guides/general/iphone-files-vs-photos/',
 'iphone-photos-limited-library-app-selection':'/guides/general/photo-library-selected-video-access/',
 'android-usb-mtp-transfer-mode':'/guides/general/android-usb-file-transfer/',
 'android-usb-mtp-large-copy-interruption':'/guides/general/android-usb-file-transfer/',
 'android-recent-files-vs-download-directory':'/guides/general/android-downloads-folder/',
 'samsung-secure-folder-video-export':'/guides/general/samsung-secure-folder-video-handoff/',
 'pixel-photos-locked-folder-export':'/guides/general/google-photos-locked-folder-retention/',
 'windows-controlled-folder-access-export':'/guides/general/windows-protected-folder-video-save/',
 'windows-known-folder-redirect-downloads':'/guides/general/windows-cloud-vs-local-file/',
 'mac-files-full-disk-vs-folder-access':'/guides/general/mac-video-files-folders-access/',
 'mac-quick-look-vs-player-codec':'/guides/general/quicktime-file-compatibility/',
 'mac-tcc-permission-after-app-update':'/guides/general/mac-video-files-folders-access/',
 'casting-mirroring-vs-remote-media-playback':'/guides/general/cast-retained-video-vs-screen-mirroring/',
 'linux-xdg-download-folder-localization':'/guides/general/linux-video-download-location/',
 'linux-snap-removable-media-interface':'/guides/general/linux-video-file-access-permissions/',
 'linux-portal-file-picker-media-access':'/guides/general/linux-video-file-access-permissions/',
})

# Collapse equivalent raw task scopes to one draft owner before authoring.
draft_merges={
 'resolve-fusion-title-font-dependency':'editing-project-missing-font-title',
 'final-cut-motion-template-dependency':'editing-project-archive-custom-plugin-dependency',
 'resolve-fusion-composition-media-dependencies':'editing-project-archive-custom-plugin-dependency',
 'resolve-powergrade-external-lut-dependency':'editing-project-archive-custom-plugin-dependency',
 'audacity-plugin-missing-project':'editing-project-archive-custom-plugin-dependency',
 'youtube-end-screen-vs-video-pixels':'platform-overlay-vs-encoded-picture',
 'youtube-cards-vs-source-video':'platform-overlay-vs-encoded-picture',
 'youtube-playlist-order-vs-single-source':'platform-overlay-vs-encoded-picture',
 'spotlight-comments-vs-media-content':'platform-overlay-vs-encoded-picture',
 'facebook-live-replay-comment-context':'platform-overlay-vs-encoded-picture',
 'tiktok-reply-video-vs-comment':'platform-overlay-vs-encoded-picture',
 'facebook-reel-native-save-vs-bookmark':'account-video-bookmark-vs-retained-file',
 'tiktok-favorites-vs-downloads':'account-video-bookmark-vs-retained-file',
 'tiktok-collection-favorites-scope':'account-video-bookmark-vs-retained-file',
 'tiktok-repost-vs-local-retention':'account-video-bookmark-vs-retained-file',
 'youtube-watch-history-vs-retained-movie':'account-video-bookmark-vs-retained-file',
 'instagram-reel-pin-vs-backup':'account-video-bookmark-vs-retained-file',
 'instagram-reel-saved-audio-vs-recording':'account-video-bookmark-vs-retained-file',
 'instagram-remix-original-context':'published-remix-vs-editable-source',
 'facebook-reel-remix-source-identity':'published-remix-vs-editable-source',
 'spotlight-remix-vs-source-clip':'published-remix-vs-editable-source',
 'tiktok-stitch-vs-complete-source':'published-remix-vs-editable-source',
 'tiktok-duet-picture-audio-scope':'published-remix-vs-editable-source',
 'instagram-reel-template-vs-source-assets':'published-remix-vs-editable-source',
 'snapchat-memories-export-format-choice':'snapchat-memories-export-owner-video',
 'resolve-timeline-xml-roundtrip-limits':'editing-project-roundtrip-transition-loss',
 'audio-export-mute-solo-state':'audacity-track-mute-export-scope',
 'video-output-audio-longer-than-picture':'duration-stream-vs-container',
 'final-cut-library-consolidate-motion-content':'editing-project-archive-custom-plugin-dependency',
 'premiere-backup-autosave-vs-creative-cloud':'premiere-autosave-project-recovery',
 'video-timestamp-wraparound':'mpeg-ts-discontinuity-timestamps',
 'video-playback-colored-blocks':'video-decoder-error-concealment',
}

draft_merges.update({'final-cut-native-convert-text-to-3d-text': 'final-cut-native-add-3d-titles', 'final-cut-native-move-titles-in-3d-space': 'final-cut-native-add-3d-titles', 'final-cut-native-adjust-basic-3d-text-settings': 'final-cut-native-add-3d-titles', 'final-cut-native-add-materials-to-3d-text-facets': 'final-cut-native-add-3d-titles', 'final-cut-native-adjust-3d-text-lighting': 'final-cut-native-add-3d-titles', 'final-cut-native-add-the-default-audio-effect': 'final-cut-native-add-audio-effects', 'final-cut-native-remove-audio-effects': 'final-cut-native-add-audio-effects', 'final-cut-native-adjust-audio-effects': 'final-cut-native-add-audio-effects', 'final-cut-native-save-audio-effects-presets': 'final-cut-native-add-audio-effects', 'final-cut-native-add-the-default-video-effect': 'final-cut-native-add-video-effects', 'final-cut-native-remove-built-in-effects': 'final-cut-native-add-video-effects', 'final-cut-native-remove-or-turn-off-effects': 'final-cut-native-add-video-effects', 'final-cut-native-copy-effects-between-clips': 'final-cut-native-add-video-effects', 'final-cut-native-save-video-effects-presets': 'final-cut-native-add-video-effects', 'final-cut-native-add-video-effect-keyframes': 'final-cut-keyframe-interpolation-motion', 'final-cut-native-modify-groups-of-keyframes': 'final-cut-keyframe-interpolation-motion', 'final-cut-native-adjust-effect-curves': 'final-cut-keyframe-interpolation-motion', 'final-cut-native-copy-and-paste-keyframes': 'final-cut-keyframe-interpolation-motion', 'final-cut-native-add-magnetic-masks': 'final-cut-native-edit-magnetic-masks', 'final-cut-native-add-a-magnetic-mask-to-a-video-effect': 'final-cut-native-edit-magnetic-masks', 'final-cut-native-add-an-auto-mask-to-a-video-effect': 'final-cut-native-use-the-auto-mask', 'final-cut-native-add-a-shape-mask-to-a-video-effect': 'final-cut-color-mask-vs-shape-mask', 'final-cut-native-add-a-color-mask-to-a-video-effect': 'final-cut-color-mask-vs-shape-mask', 'final-cut-native-create-simple-shape-masks': 'final-cut-color-mask-vs-shape-mask', 'final-cut-native-remove-color-correction-effects': 'final-cut-native-add-color-correction-effects', 'final-cut-native-use-color-presets': 'final-cut-native-add-color-correction-effects', 'final-cut-native-save-color-correction-presets': 'final-cut-native-add-color-correction-effects', 'final-cut-native-compare-color-corrections': 'final-cut-native-add-color-correction-effects', 'premiere-native-create-a-subclip-from-the-project-panel': 'premiere-native-adjust-media-start-and-end-times-of-subclip', 'premiere-native-create-a-subclip-from-the-timeline': 'premiere-native-adjust-media-start-and-end-times-of-subclip', 'premiere-native-convert-subclip-to-master-clip': 'premiere-native-adjust-media-start-and-end-times-of-subclip', 'premiere-native-add-motion-graphic-templates-to-a-sequence': 'premiere-native-customize-motion-graphics-templates', 'premiere-native-organize-motion-graphics-templates': 'premiere-native-customize-motion-graphics-templates', 'premiere-native-copy-and-paste-audio-effects-in-the-timeline': 'premiere-native-apply-effects-using-audio-track-mixer', 'premiere-native-adjust-audio-track-effects-in-timeline': 'premiere-native-apply-effects-using-audio-track-mixer', 'premiere-native-copy-and-move-effects-in-audio-track-mixer': 'premiere-native-apply-effects-using-audio-track-mixer', 'premiere-native-archive-team-projects': 'premiere-native-restore-archived-team-projects', 'premiere-native-delete-archived-team-projects': 'premiere-native-restore-archived-team-projects', 'premiere-native-find-and-replace-text-using-the-graphics-tab': 'premiere-native-edit-text-in-graphics-tab', 'kdenlive-custom-effect-stack-dependency': 'editing-project-archive-custom-plugin-dependency', 'kdenlive-render-complete-open-output': 'verified-file-readiness', 'youtube-source-language-update-role': 'youtube-upload-original-language-field', 'youtube-auto-caption-native-delete': 'youtube-captions-draft-vs-published'})

draft_merges.update({'premiere-native-import-selected-premiere-sequences': 'premiere-import-selected-sequences', 'premiere-native-import-photoshop-and-illustrator-files': 'premiere-photoshop-layered-image-import', 'premiere-native-import-photoshop-files-into-premiere': 'premiere-photoshop-layered-image-import', 'premiere-native-record-a-voice-over-on-an-audio-track-from-the-timeline': 'premiere-record-voiceover-track-scope', 'premiere-native-record-audio-using-the-audio-track-mixer': 'premiere-record-voiceover-track-scope', 'premiere-native-mute-input-during-recording': 'premiere-mute-input-monitoring-record', 'premiere-native-import-and-export-presets': 'premiere-custom-export-preset-dependency', 'premiere-native-import-avid-media-composer-project-files': 'premiere-avid-interchange-source-references', 'premiere-native-export-from-avid-media-composer-to-premiere': 'premiere-avid-interchange-source-references', 'premiere-native-search-for-media-using-ai-powered-media-intelligence': 'premiere-media-intelligence-result-vs-source', 'premiere-native-search-for-audio-using-media-intelligence': 'premiere-audio-search-uncertain-word', 'premiere-native-search-for-similar-visuals-using-media-intelligence': 'premiere-media-intelligence-result-vs-source', 'premiere-native-manage-media-intelligence-metadata': 'premiere-media-intelligence-result-vs-source', 'premiere-native-add-a-marker-to-a-clip': 'premiere-markers-comment-handoff', 'premiere-native-copy-and-paste-sequence-markers': 'premiere-markers-comment-handoff', 'premiere-native-share-markers-with-after-effects': 'premiere-markers-comment-handoff', 'premiere-native-create-offline-clips': 'premiere-offline-clips-placeholder', 'premiere-native-edit-offline-clips': 'premiere-offline-clips-placeholder', 'premiere-native-relink-offline-clips': 'premiere-offline-clips-placeholder', 'premiere-native-convert-online-clips-to-offline-clips': 'premiere-offline-clips-placeholder', 'premiere-native-display-metadata-as-overlays': 'premiere-source-metadata-overlay-export', 'premiere-native-import-export-or-delete-overlay-settings': 'premiere-source-metadata-overlay-export', 'premiere-native-edit-transcripts-using-text-based-editing': 'premiere-transcript-cut-vs-word-correction', 'premiere-native-add-clips-to-the-timeline-using-text-based-editing': 'premiere-transcript-cut-vs-word-correction', 'premiere-native-edit-sequences-using-text-based-editing': 'premiere-transcript-cut-vs-word-correction', 'premiere-native-create-a-sequence-with-paper-edit': 'premiere-transcript-cut-vs-word-correction', 'premiere-native-change-clip-speed-and-duration-using-the-rate-stretch-tool': 'premiere-rate-stretch-duration-boundary', 'premiere-native-enable-or-disable-a-clip': 'premiere-video-track-enable-export', 'premiere-native-create-a-multi-camera-source-sequence': 'premiere-merge-clips-vs-multicam', 'premiere-native-create-and-edit-a-multi-camera-target-sequence': 'premiere-merge-clips-vs-multicam', 'premiere-native-create-linked-and-track-styles': 'premiere-caption-style-track-scope', 'premiere-native-apply-linked-and-track-styles': 'premiere-caption-style-track-scope', 'premiere-native-create-styles-for-captions': 'premiere-caption-style-track-scope', 'premiere-native-link-audio-and-video-clips': 'premiere-linked-selection-edit-scope', 'premiere-native-synchronize-audio-and-video': 'premiere-merge-clips-vs-multicam', 'premiere-native-synchronize-clips-in-the-timeline-panel': 'premiere-merge-clips-vs-multicam', 'premiere-native-use-the-timecode-from-an-audio-primary-clip-to-create-a-merged-clip': 'premiere-merge-clips-vs-multicam', 'premiere-native-edit-merged-clips': 'premiere-merge-clips-vs-multicam', 'premiere-native-render-and-replace-media-in-a-sequence': 'premiere-render-replace-recovery', 'premiere-native-replace-rendered-clips-with-original-media': 'premiere-render-replace-recovery', 'premiere-native-use-preview-files-when-rendering': 'premiere-preview-files-final-render', 'premiere-native-export-caption-tracks': 'premiere-export-caption-track-vs-burn', 'premiere-native-export-text-from-motion-graphics': 'premiere-motion-graphics-text-export', 'premiere-native-export-a-project-as-an-edl-file': 'premiere-edl-limited-timeline-handoff', 'premiere-native-export-a-project-as-a-final-cut-pro-xml-file': 'editing-project-roundtrip-transition-loss', 'premiere-native-export-videos-with-content-credentials': 'premiere-content-credentials-export', 'premiere-native-export-omf-files-for-pro-tools': 'premiere-omf-media-embedding-scope', 'premiere-native-export-aaf-files': 'premiere-aaf-audio-handoff', 'premiere-native-create-and-export-hdr-videos-for-youtube-on-mac': 'premiere-export-hdr-youtube-representation', 'premiere-native-view-versions-of-a-team-project': 'premiere-team-project-conflict-version', 'premiere-native-create-a-new-team-project-from-a-version': 'premiere-team-project-conflict-version', 'premiere-native-share-for-review-with-frame-io': 'premiere-frameio-upload-vs-original-storage', 'premiere-native-add-comments-on-shared-projects': 'premiere-review-frameio-time-reference', 'premiere-native-add-projects-to-a-production': 'premiere-productions-project-dependency', 'premiere-native-move-clips-and-sequences-between-projects-in-a-production': 'premiere-productions-project-dependency', 'premiere-native-copy-clips-across-projects-in-a-production': 'premiere-productions-project-dependency', 'premiere-native-find-and-edit-source-clips-in-a-production': 'premiere-productions-project-dependency', 'premiere-native-change-project-lock-status-in-production': 'premiere-project-locking-conflict', 'premiere-native-automatically-manage-your-media-cache-files': 'premiere-cache-cleanup-vs-source-delete', 'premiere-native-delete-media-cache-files-manually': 'premiere-cache-cleanup-vs-source-delete', 'premiere-native-manage-media-cache': 'premiere-cache-cleanup-vs-source-delete', 'premiere-native-recover-projects-after-a-crash': 'premiere-autosave-project-recovery', 'premiere-native-edit-premiere-sequences-in-audition': 'premiere-audition-edit-original-vs-copy', 'premiere-native-edit-premiere-audio-clips-in-audition': 'premiere-audition-edit-original-vs-copy', 'premiere-native-import-after-effects-compositions': 'premiere-dynamic-link-media-dependencies', 'premiere-native-replace-clips-with-a-dynamically-linked-after-effects-composition': 'premiere-dynamic-link-media-dependencies', 'premiere-native-delete-dynamically-linked-compositions-or-clips': 'premiere-dynamic-link-media-dependencies', 'premiere-native-make-a-dynamically-linked-composition-offline': 'premiere-dynamic-link-media-dependencies', 'premiere-native-relink-a-dynamically-linked-composition': 'premiere-dynamic-link-media-dependencies', 'premiere-native-share-assets-between-after-effects-and-premiere-using-dynamic-link': 'premiere-dynamic-link-media-dependencies', 'premiere-native-create-a-dynamically-linked-composition': 'premiere-dynamic-link-media-dependencies', 'premiere-native-import-an-after-effects-composition': 'premiere-dynamic-link-media-dependencies', 'premiere-native-delete-a-dynamicaly-linked-composition-or-clip': 'premiere-dynamic-link-media-dependencies', 'premiere-native-modify-a-dynamically-linked-composition-in-after-effects': 'premiere-dynamic-link-media-dependencies', 'premiere-native-copy-clips-from-premiere-to-after-effects': 'premiere-after-effects-roundtrip-identity', 'premiere-native-copy-from-after-effects-to-premiere': 'premiere-after-effects-roundtrip-identity', 'premiere-native-edit-still-images-in-premiere-using-photoshop': 'premiere-photoshop-graphic-update-scope', 'final-cut-native-import-spanned-clips': 'final-cut-spanned-camera-clip-import', 'final-cut-native-import-from-an-archive-or-disk-image': 'final-cut-camera-archive-vs-library', 'final-cut-native-duplicate-projects-and-clips': 'final-cut-snapshot-vs-project-duplicate', 'final-cut-native-delete-items-from-libraries': 'final-cut-delete-event-source-scope', 'final-cut-native-save-and-back-up-projects': 'final-cut-library-backup-media-scope', 'final-cut-native-create-freeze-frames': 'final-cut-freeze-frame-duration-insert', 'final-cut-native-configure-audio-channels': 'final-cut-audio-component-channel-config', 'final-cut-native-sync-audio-and-video': 'final-cut-synchronized-clip-source-scope', 'final-cut-native-modify-titles-in-motion': 'final-cut-title-template-edit-in-motion', 'final-cut-native-keyframe-audio-effects': 'final-cut-audio-keyframe-level-transition', 'final-cut-native-create-compound-clips': 'final-cut-compound-clip-vs-export', 'final-cut-native-edit-compound-clips': 'final-cut-compound-reference-parent-change', 'final-cut-native-import-media-for-multicam-edits': 'final-cut-multicam-angle-order', 'final-cut-native-create-multicam-clips': 'final-cut-multicam-angle-order', 'final-cut-native-edit-multicam-clips': 'final-cut-multicam-cut-vs-angle-editor', 'final-cut-native-add-clips-to-auditions': 'final-cut-audition-choice-export', 'final-cut-native-use-xml-to-transfer-projects': 'final-cut-fcpxml-media-references', 'final-cut-native-export-or-share-stereo-and-spatial-video': 'final-cut-stereoscopic-metadata-handoff', 'final-cut-native-import-stereo-and-spatial-video': 'final-cut-stereoscopic-metadata-handoff', 'final-cut-native-adjust-stereo-video-properties': 'final-cut-stereoscopic-metadata-handoff', 'final-cut-native-use-the-green-screen-keyer-effect': 'final-cut-chroma-key-spill-edge-review', 'final-cut-native-add-a-color-mask': 'final-cut-color-mask-vs-shape-mask', 'final-cut-native-edit-a-color-mask': 'final-cut-color-mask-vs-shape-mask', 'final-cut-native-add-a-shape-mask': 'final-cut-color-mask-vs-shape-mask', 'final-cut-native-add-shape-masks-to-a-color-mask': 'final-cut-color-mask-vs-shape-mask', 'final-cut-native-remove-a-color-or-shape-mask': 'final-cut-color-mask-vs-shape-mask', 'final-cut-native-use-the-color-wheels-effect': 'final-cut-color-wheels-vs-curves', 'final-cut-native-use-the-color-curves-effect': 'final-cut-color-wheels-vs-curves', 'final-cut-native-use-wide-gamut-hdr-color-processing': 'final-cut-wide-gamut-library-output', 'final-cut-native-view-hdr-video': 'final-cut-wide-gamut-library-output', 'final-cut-native-share-roles-as-files': 'final-cut-export-audio-role-container', 'final-cut-native-export-closed-captions': 'final-cut-share-captions-format', 'final-cut-native-relink-clips-to-media-files': 'final-cut-media-representation-change', 'final-cut-native-create-optimized-and-proxy-files': 'final-cut-optimized-media-vs-original', 'final-cut-native-manage-render-files': 'final-cut-delete-generated-media-scope', 'final-cut-native-restore-a-library': 'final-cut-project-recovery-backup-version'})

draft_merges.update({
 'tiktok-photosensitive-content-notice':'platform-overlay-vs-encoded-picture',
 'youtube-corrections-card-vs-movie-edit':'platform-overlay-vs-encoded-picture',
 'tiktok-music-add-external-library':'account-video-bookmark-vs-retained-file',
 'spotlight-save-favorite-vs-movie':'account-video-bookmark-vs-retained-file',
 'tiktok-playlist-view-vs-video-file':'account-video-bookmark-vs-retained-file',
 'tiktok-auto-captions-vs-creator-captions':'tiktok-auto-captions-owner-edit',
 'tiktok-post-preview-vs-final-published':'tiktok-post-processing-pending',
 'tiktok-effect-resource-vs-rendered-video':'published-remix-vs-editable-source',
 'tiktok-cover-text-vs-caption-file':'platform-overlay-vs-encoded-picture',
})

merges.update({
 'picture-in-picture-window-vs-retained-file':'browser-preview-vs-save',
 'browser-hardware-decoder-local-preview':'hardware-vs-software-decoding',
 'icloud-browser-video-export-representation':'photos-video-export-original-vs-edited',
 'video-copy-completed-size-check-mismatch':'archive-checksums',
 'video-archive-checksum-algorithm-migration':'archive-checksums',
 'video-player-end-time-vs-file-completion':'incomplete-video-file',
 'video-archive-manifest-path-renaming':'archive-manifest',
})
draft_merges.update({
 'video-filesystem-sparse-file-accounting':'movie-file-zero-disk-allocation',
})

draft_merges.update({'mp4-fragmented-vs-flat-file': 'fragmented-mp4-vs-flat-mp4', 'mp4-timescale-versus-frame-rate': 'mov-timescale-vs-frame-rate', 'mp4-hevc-tag-hvc1-hev1': 'hevc-hvc1-vs-hev1', 'mov-reference-movie-external-resources': 'mov-reference-movie-media-dependencies', 'mkv-track-uid-vs-number': 'matroska-track-uid-vs-index', 'mkv-ordered-chapters-playback-scope': 'matroska-ordered-chapters-editions', 'h264-avcc-annexb-packaging': 'h264-avcc-vs-annex-b', 'codec-bframe-reorder-delay': 'video-b-frames-decode-order', 'codec-open-closed-gop-cut-boundary': 'closed-vs-open-gop-trim', 'codec-dnxhr-profile-handoff': 'dnxhr-profile-handoff', 'codec-av1-film-grain-metadata': 'av1-film-grain-synthesis', 'codec-hevc-dolby-vision-profile': 'hevc-dolby-vision-base-layer', 'video-demux-versus-decode': 'demuxer-vs-decoder', 'video-packet-versus-frame': 'packet-vs-frame-media-inspection', 'mp4-edit-list-empty-leading-time': 'mp4-edit-list-trim-interpretation'})

draft_merges.update({'facebook-reel-saved-collection-source-gone': 'account-video-bookmark-vs-retained-file', 'facebook-video-caption-language-file-name': 'facebook-video-accessibility-caption-owner', 'facebook-reel-remix-side-by-side-output': 'published-remix-vs-editable-source', 'instagram-reel-remix-layout-derivative': 'published-remix-vs-editable-source', 'instagram-reel-save-owner-music-version': 'instagram-reel-added-music-owner-save', 'tiktok-native-video-cover-text-post': 'platform-overlay-vs-encoded-picture'})
merges.update({'spotlight-upload-camera-roll-orientation':'video-rotation-metadata'})

merges.update({'handbrake-native-upscale-source-detail': 'does-4k-upscale-improve-detail', 'handbrake-burned-and-soft-caption-output': 'open-vs-closed-captions', 'handbrake-import-srt-native-encoding': 'caption-character-encoding', 'handbrake-native-audio-gain-headroom': 'audio-clipping', 'vlc-native-subtitle-selection-encoding': 'caption-character-encoding', 'vlc-native-subtitle-delay-session': 'caption-timing-offset', 'vlc-native-audio-delay-session': 'audio-out-of-sync', 'vlc-native-snapshot-vs-cover-art': 'thumbnail-vs-video-frame', 'vlc-native-volume-above-reference': 'audio-clipping', 'vlc-native-spherical-projection-selection': 'spherical-video-vs-flat-playback', 'vlc-native-stereo-display-handoff': 'stereoscopic-video-vs-spherical-projection'})
draft_merges.update({'handbrake-native-surround-passthrough-fallback': 'handbrake-passthrough-vs-audio-encode', 'vlc-native-audio-extraction-selected-stream': 'vlc-convert-selected-audio-output', 'vlc-ios-native-playlist-scope': 'vlc-native-playlist-external-media', 'vlc-native-recording-folder-discovery': 'vlc-native-record-playback-range'})

draft_merges.update({'kdenlive-sequence-duplicate-version-scope':'kdenlive-archive-package-scope'})

draft_merges.update({'final-cut-native-use-auto-mask-or-magnetic-mask':'final-cut-native-use-the-auto-mask'})

draft_merges.update({'audio-pcm-endianness-raw-import': 'pcm-endianness-raw-import', 'audio-true-peak-versus-sample-peak': 'true-peak-vs-sample-peak', 'audio-resampling-antialiasing-context': 'audio-resampling-aliasing-review', 'caption-nonspeech-sound-description': 'caption-non-speech-sound-scope', 'caption-safe-area-cropped-delivery': 'caption-safe-placement-vs-video-crop', 'caption-ruby-annotations-retention': 'webvtt-ruby-pronunciation-handoff', 'wav-channel-mask-layout': 'wav-extensible-channel-mask', 'opus-pre-skip-end-trim': 'opus-pre-skip-output-rate', 'opus-input-rate-versus-coded-clock': 'opus-pre-skip-output-rate'})

merges.update({'clipchamp-locate-files-cache-versus-source': 'clipchamp-project-vs-media-backup', 'clipchamp-content-backup-completion': 'clipchamp-project-vs-media-backup', 'clipchamp-project-second-computer-assets': 'clipchamp-project-vs-media-backup', 'clipchamp-native-recovery-export-versus-source': 'clipchamp-project-vs-media-backup', 'clipchamp-onedrive-project-asset-folder': 'clipchamp-project-vs-media-backup', 'clipchamp-native-export-download-destination': 'clipchamp-project-vs-media-backup', 'clipchamp-native-template-source-dependency': 'clipchamp-project-vs-media-backup', 'clipchamp-native-resolution-source-limit': 'does-4k-upscale-improve-detail', 'clipchamp-native-aspect-ratio-crop-review': 'video-aspect-ratio', 'm365-player-custom-thumbnail-vs-file': 'thumbnail-vs-video-frame', 'm365-player-chapters-vs-embedded-markers': 'video-chapters-vs-separate-files'})
draft_merges.update({'m365-player-transcript-delete-retained-copy': 'm365-player-transcript-owner-edit', 'm365-native-meeting-chapters-transcript-review': 'm365-player-chapters-vs-embedded-markers', 'm365-native-playlist-source-availability': 'account-video-bookmark-vs-retained-file', 'm365-native-video-share-copy-scope': 'shared-drive-link-revocation-copies'})

# Full existing TTML/image answers already own these receiving checks.
merges.update({
 'ttml-clock-frame-tick-expression':'ttml-caption-handoff',
 'ttml-profile-required-feature-reception':'ttml-caption-handoff',
 'ttml-namespace-validation-versus-caption-support':'ttml-caption-handoff',
 'ttml-region-coordinate-viewport':'ttml-caption-handoff',
 'ttml-image-caption-versus-editable-text':'image-subtitles-vs-editable-text',
})
# Identity, validity and discovery belong to one credential-validation owner.
draft_merges.update({
 'video-content-credentials-signer-vs-creator':'video-content-credentials-validation-scope',
 'video-content-credentials-missing-versus-invalid':'video-content-credentials-validation-scope',
 'webvtt-cue-settings-unsupported-receiver':'webvtt-region-layout-handoff',
})

merges.update({'shotcut-speech-text-transcript-review':'automatic-caption-review'})

merges.update({'blender-sequencer-fit-fill-stretch':'video-aspect-ratio'})
draft_merges.update({'blender-strip-slip-source-boundary':'blender-movie-strip-source-start'})

merges.update({'matroska-forced-flag-versus-caption-content':'forced-subtitles-vs-full-captions'})
draft_merges.update({'matroska-track-language-precedence':'mkvtoolnix-track-order-language','matroska-default-flags-player-preferences':'mkvtoolnix-track-order-language'})

changed=0
for r in rows:
 if r.get('batch')!='expansion-stage-a-2026-10-08' or r['status']!='DRAFT':continue
 slug=r['path'].split('/')[-2]
 if slug in specific:dest=specific[slug]
 elif slug in merges:dest='/guides/general/'+merges[slug]+'/'
 elif slug in draft_merges:
  target=draft_merges[slug];dest=next(x['path'] for x in rows if x['path'].split('/')[-2]==target)
 else:continue
 assert dest in known or dest in public,dest
 reason=('Inventory-stage task-scope consolidation: the stated outcome is already owned by '+dest+'. Software/platform naming or a narrower symptom does not justify a second dominant URL. If source-specific details merit improvement, review and enrich the canonical answer; no alternative public route is created.')
 r.update(status='ARCHIVED',indexable=False,inventoryApproval=None)
 r['semanticReview'].update(state='MERGED_EXISTING_TASK' if dest in public else 'MERGED_DRAFT_TASK',comparisons=[dest],rationale=reason,reviewer='Bulk task-scope inventory consolidation; not content approval',reviewedAt=REVIEW_DATE)
 r['disposition'].update(classification='MERGE_WITH_EXISTING',destination=dest,internalLinkDestination=dest,reason=reason,outcome='CONSOLIDATED' if dest in public else 'RESEARCH_REQUIRED',reviewedAt=REVIEW_DATE);changed+=1
rejected_low_value={
 'premiere-native-edit-video-in-premiere',
 'premiere-native-export-video-and-audio-files',
 'premiere-native-export-options-in-premiere',
 'premiere-native-incorporate-branded-graphics-and-audio-elements',
 'premiere-native-export-for-viewing-platforms',
 'premiere-native-add-or-remove-clips',
 'premiere-native-edit-video-using-the-properties-panel',
 'final-cut-native-use-expanded-color-controls',
 'final-cut-native-adjust-timeline-clip-appearance',
 'final-cut-native-create-a-new-library',
 'final-cut-native-view-a-clips-information',
 'final-cut-native-modify-a-projects-settings',
 'final-cut-native-export-file-and-apple-devices-destinations',
}
rejected=0
for r in rows:
 if r.get('batch')!='expansion-stage-a-2026-10-08' or r['status']!='DRAFT' or r['path'].split('/')[-2] not in rejected_low_value:continue
 reason='Rejected low-value raw navigation topic: the current proposal describes a broad interface, settings panel or collection of operations rather than one specific unresolved media task. An official navigation entry alone does not justify a separate public SEO page. Retain the source lead for research supporting actual task owners.'
 r.update(status='ARCHIVED',indexable=False,inventoryApproval=None)
 r['semanticReview'].update(state='REJECTED_LOW_VALUE',rationale=reason,reviewer='Inventory task-specificity rejection; no writing approval',reviewedAt=REVIEW_DATE)
 r['disposition'].update(classification='REJECTED_LOW_VALUE',destination=None,internalLinkDestination=r['related'][0],reason=reason,outcome='REJECTED',reviewedAt=REVIEW_DATE)
 rejected+=1
# Resolve historical aliases to a single active owner. Never leave ownership
# dependent on another archived candidate, and reject cycles before writing.
flattened=0;synchronized=0
for r in rows:
 if r.get('batch')!='expansion-stage-a-2026-10-08' or r['disposition']['classification']!='MERGE_WITH_EXISTING':continue
 dest=r['disposition']['destination'];seen={r['path']}
 while dest in known and known[dest]['status']=='ARCHIVED':
  assert dest not in seen,('Cyclic task ownership',r['path'],dest)
  seen.add(dest)
  owner=known[dest]
  assert owner['disposition']['classification']=='MERGE_WITH_EXISTING',('Archived owner has no replacement',dest)
  dest=owner['disposition']['destination']
 assert dest in public or (dest in known and known[dest]['status']=='DRAFT'),('Inactive task owner',dest)
 expected_state='MERGED_EXISTING_TASK' if dest in public else 'MERGED_DRAFT_TASK'
 expected_outcome='CONSOLIDATED' if dest in public else 'RESEARCH_REQUIRED'
 if dest!=r['disposition']['destination']:
  r['semanticReview']['comparisons']=[dest]
  r['semanticReview']['state']='MERGED_EXISTING_TASK' if dest in public else 'MERGED_DRAFT_TASK'
  r['semanticReview']['rationale']+=' Final active answer owner: '+dest+'.'
  r['disposition'].update(destination=dest,internalLinkDestination=dest,outcome='CONSOLIDATED' if dest in public else 'RESEARCH_REQUIRED')
  r['disposition']['reason']+=' Final active answer owner: '+dest+'.'
  flattened+=1
 elif r['semanticReview']['state']!=expected_state or r['disposition']['outcome']!=expected_outcome:
  # A later approved owner can become public without changing its URL. Keep
  # alias bookkeeping current while leaving the alias itself nonpublic.
  r['semanticReview'].update(state=expected_state,comparisons=[dest])
  r['disposition'].update(outcome=expected_outcome,internalLinkDestination=dest)
  synchronized+=1
p.write_text(json.dumps(rows,indent=2)+'\n');print('Task scopes consolidated:',changed,'Ownership chains flattened:',flattened,'Owner lifecycle records synchronized:',synchronized,'Low-value proposals rejected:',rejected)
