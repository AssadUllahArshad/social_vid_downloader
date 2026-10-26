// Explicit body-reviewed ownership decisions only; no similarity auto-approval.
import fs from 'node:fs';import {published,fingerprint} from '../apps/web/src/lib/editorial/workflow.mjs';
const load=p=>JSON.parse(fs.readFileSync(p));const state=load('docs/video-tools-execution-state.json'),registry=load('content/editorial/first-500-inventory.json'),articles=load('content/editorial/articles.json');
const groups=[
  [
    "h264-avcc-vs-annex-b",
    [
      "h265-hvcc-annexb-packaging"
    ],
    "The complete owner explicitly contrasts both H.264 and HEVC configuration/framing, identifies their codec-specific bitstream filters and verifies the elementary output resource/timing limits. These are one receiving-packaging decision."
  ],
  [
    "codec-tag-vs-real-bitstream",
    [
      "hevc-hvc1-vs-hev1"
    ],
    "The complete owner explicitly explains hvc1/hev1 sample-entry conventions, limited justified tag/remux use and actual receiver verification. It does not falsely treat changing a tag as transcoding."
  ],
  [
    "aac-adts-vs-container-config",
    [
      "aac-adts-vs-latm-transport"
    ],
    "The approved article separates ADTS and LATM framing from AAC profiles, requires the actual transport identification and limits ADTS-to-container conversion instead of claiming the ADTS filter accepts LATM."
  ],
  [
    "webvtt-header-missing",
    [
      "webvtt-cue-identifier-versus-visible-text",
      "webvtt-note-style-region-payload"
    ],
    "The approved owner gives specific header, identifier and NOTE/STYLE/REGION structural checks, distinguishes metadata from visible cue payload and verifies converted text against original cue scope."
  ],
  [
    "source-changes-after-analysis",
    [
      "format-selection-stale-analysis",
      "merge-failed-stream-parameter-change"
    ],
    "The reviewed existing canonical compares fresh metadata and source stream properties, rejects reuse of stale format/session identifiers and requires choosing a real current compatible inventory without invented fallback qualities."
  ],
  [
    "archive-checksums",
    [
      "download-hash-changes-between-preparations",
      "movie-network-copy-source-changing"
    ],
    "The reviewed owner freezes a completed source/destination comparison, excludes still-writing artifacts and explicitly distinguishes legitimate remux/tag/encoding byte changes from faithful copy requirements."
  ],
  [
    "audio-out-of-sync",
    [
      "bluetooth-delay-vs-file-sync"
    ],
    "The reviewed owner directly compares wireless versus direct speakers and different players, distinguishes playback-path delay from a stored stream offset and tests beginning/middle/end landmarks before editing."
  ],
  [
    "audio-channel-downmix",
    [
      "video-one-channel-silent-speaker-map",
      "video-audio-channel-order-wrong",
      "obs-audio-polarity-route-review"
    ],
    "The complete canonical verifies stream selection, known channel positions and actual output routing; it also explicitly compares relative-polarity cancellation on independent contributions before changing a recoverable mix. These candidates repeat that channel-path diagnosis rather than a new OBS routing-control tutorial."
  ],
  [
    "caption-sidecar-not-showing",
    [
      "video-subtitle-track-selected-blank",
      "video-subtitle-position-offscreen",
      "linux-case-sensitive-video-sidecar"
    ],
    "The complete owner checks explicit selection/enabling, full file names and version matching, known cue intervals and supported off-screen presentation settings. Explicit loading tests avoid assuming filename auto-association across filesystems."
  ],
  [
    "edge-download-history",
    [
      "edge-download-location-per-file"
    ],
    "The existing Edge guide explicitly identifies Settings Downloads Location and the ask-where-to-save option, distinguishes earlier chosen paths and explains that defaults only affect future saves."
  ],
  [
    "firefox-handler-system-default-video",
    [
      "firefox-pdf-like-inline-media-save"
    ],
    "The reviewed canonical directly separates inline browser response handling, file saving and filesystem default-app selection, with scoped controls and actual file verification. The candidate is that same handling distinction."
  ],
  [
    "playback-speed-vs-retimed-video",
    [
      "browser-video-rate-setting-vs-file-speed",
      "video-pitch-after-frame-rate-conform"
    ],
    "The canonical explicitly covers playbackRate versus a saved derivative and Premiere Interpret Footage duration/audio effects versus per-instance retiming, with normal-speed export checks."
  ],
  [
    "audio-click-at-edit-boundary",
    [
      "video-file-audio-sample-discontinuity"
    ],
    "The complete owner compares source and edited joins, addresses sample discontinuities, stereo boundary differences, fades and synchronization rather than claiming a cleaner waveform restores lost original samples."
  ],
  [
    "interlaced-vs-progressive",
    [
      "vlc-native-deinterlace-playback-review"
    ],
    "The canonical already separates receiver deinterlacing from a saved scan conversion, tests moving/paused detail and field order, and directs documented receiver support before modifying a source. No separate universal VLC preset is appropriate."
  ],
  [
    "matroska-codec-delay-versus-added-silence",
    [
      "matroska-discard-padding-trim-context",
      "matroska-seek-preroll-versus-timeline-offset"
    ],
    "The complete owner gives each of CodecDelay, block-level signed DiscardPadding and SeekPreRoll its own scope, compares sequential and seeked boundaries, and prevents adding guessed silence or applying decoder compensation twice."
  ],
  [
    "mp3-gapless-delay-handoff",
    [
      "mp3-xing-vbri-duration-seeking"
    ],
    "The complete owner explicitly addresses Xing/VBRI duration and seeking information, variable-rate filesize estimates and differences between actual continuous playback and seek behavior."
  ],
  [
    "wav-extensible-channel-mask",
    [
      "audio-channel-mask-ambisonic-role"
    ],
    "The complete owner explicitly distinguishes speaker-mask assignments from ambisonic component order/normalization, unspecified layouts and labels versus sample reordering; it does not invent an ambisonic renderer."
  ],
  [
    "youtube-clip-vs-source-video",
    [
      "youtube-clips-feature-source-scope"
    ],
    "The complete existing YouTube Clip guide explicitly identifies the referenced source and interval, public-source access dependency, unsupported Clip input and a separately verified authorized excerpt workflow."
  ],
  [
    "youtube-playback-enhancement-vs-source",
    [
      "youtube-video-audio-enhancement-source-role"
    ],
    "The existing complete owner covers actual platform playback enhancements separately from source-delivered file properties, retained-source verification and the absence of enhancement reversal."
  ],
  [
    "youtube-viewer-transcript-navigation",
    [
      "youtube-transcript-panel-resource-version"
    ],
    "The existing canonical explicitly checks the matching recording and caption resource, warns about later edits and old timestamps, and separates viewing a transcript from exporting captions or retaining media."
  ],
  [
    "instagram-trial-reel-sharing-state",
    [
      "instagram-trial-reel-publication-state"
    ],
    "These two Instagram records have the same Trial Reel publication-state intent. The complete canonical already covers trial versus draft, profile-grid differences and broader sharing without private-access claims."
  ],
  [
    "whatsapp-view-once-vs-retained-file",
    [
      "whatsapp-view-once-video-retention-boundary"
    ],
    "The existing complete WhatsApp canonical gives the native View Once retention boundary, distinguishes ordinary files and Status, forbids bypass/recovery claims and provides the authorized replacement-file workflow."
  ],
  [
    "tiktok-save-video-controls",
    [
      "tiktok-post-download-vs-creator-studio"
    ],
    "The existing owner explicitly distinguishes viewer Share/Save Video, creator download settings and owner offline retention from management or public extraction, with actual output verification and preserved Beta status."
  ],
  [
    "source-audio-language-selection",
    [
      "youtube-preferred-language-versus-source-track"
    ],
    "The reviewed owner explicitly distinguishes a platform/browser language preference from genuine retrievable audio inventory, requires listening to the actual track and verifies saved local streams without generating missing languages."
  ],
  [
    "final-cut-library-media-handoff",
    [
      "final-cut-library-backup-media-scope",
      "final-cut-optimized-media-vs-original"
    ],
    "The complete Final Cut canonical explicitly states that automatic library backups contain the database rather than media and distinguishes original, optimized and proxy media choices, source preservation and receiver verification."
  ],
  [
    "premiere-collect-project-media",
    [
      "premiere-search-bin-vs-retained-media"
    ],
    "The complete Premiere canonical collects actual used recordings with Project Manager and distinguishes sequence/project item organization from a verified copied resource package. A search/bin listing is not another archive procedure or finished artifact."
  ],
  [
    "video-color-primaries-vs-transfer",
    [
      "video-matrix-coefficients-handoff",
      "codec-color-metadata-bitstream-container"
    ],
    "The approved owner individually explains matrix coefficients, transfer and primaries, inspects color_space with FFprobe and explicitly compares container/bitstream interpretation versus a real pixel conversion."
  ],
  [
    "hdr-static-vs-dynamic-metadata",
    [
      "video-metadata-mastering-display-vs-output",
      "codec-hdr10-static-metadata-scope",
      "codec-hdr10plus-dynamic-metadata-handoff",
      "hevc-dolby-vision-base-layer"
    ],
    "The approved owner explicitly separates mastering-display context from the receiving screen, static versus dynamic payloads, HDR10+/Dolby Vision-specific retention and a decoded base layer versus the complete intended presentation. It requires metadata-aware and receiving checks without claiming universal restoration."
  ],
  [
    "video-tone-map-highlight-review",
    [
      "video-gamut-map-saturated-colors",
      "video-sdr-white-level-vs-hdr"
    ],
    "The complete owner separately handles luminance and gamut mapping, SDR reference-white interpretation in an HDR project, contrasting test scenes and the actual saved receiving copy. These records are aspects of the same reviewed conversion decision."
  ],
  [
    "hls-vs-dash",
    [
      "playlist-manifest-vs-media-segments"
    ],
    "The complete existing canonical explicitly distinguishes HLS/DASH instruction documents from referenced media, live and on-demand resource scope, access boundaries and a verified saved output."
  ],
  [
    "hls-master-playlist-vs-variant",
    [
      "hls-discontinuity-segment-timing"
    ],
    "The new complete owner explicitly separates variant/rendition roles and media segment order, explains discontinuity timestamp/parameter boundaries and requires actual assembled output verification instead of naive byte concatenation."
  ],
  [
    "hls-webvtt-timestamp-map-local-handoff",
    [
      "hls-webvtt-segment-crossing-cues",
      "hls-webvtt-empty-segment-versus-missing-captions"
    ],
    "The complete owner has dedicated crossing-cue and empty-segment sections, the local/media anchor calculation and distinction between valid quiet text intervals and missing/HTML responses."
  ],
  [
    "ttml-external-font-image-resource-retention",
    [
      "ttml-whitespace-preservation-dialogue",
      "caption-style-inheritance-export"
    ],
    "The approved owner explicitly covers effective inherited style, XML whitespace/preservation context, permitted font/image assets and receiving presentation checks. These candidates are aspects of the same TTML presentation-resource handoff."
  ],
  [
    "video-player-network-share-stall",
    [
      "linux-fuse-network-mount-video-seek"
    ],
    "The complete owner explicitly discusses a FUSE-backed mount as a remote read/seek path, compares a checksum-matching local copy and requires separate continuous-versus-seek observations without weakening permissions."
  ],
  [
    "video-usb-exfat-repair-first-copy",
    [
      "movie-external-drive-health-read-errors"
    ],
    "The approved owner distinguishes repair prompts, unstable/disconnecting hardware and persistent read errors, avoids repeated destructive experiments, preserves readable copies and requires independent verification rather than promising repair of missing movie content."
  ],
  [
    "vlc-native-transcode-save-destination",
    [
      "vlc-native-stream-versus-save-output",
      "vlc-native-batch-output-overwrite"
    ],
    "The complete owner gives independent codec/mux/access/destination stages, explicitly distinguishes file and network output, verifies completed artifacts and requires distinct output names for multiple operations without claiming a special website batch function."
  ],
  [
    "copy-video-to-usb",
    [
      "windows-removable-drive-eject-video",
      "windows-usb-device-removal-queued-write"
    ],
    "The complete owner explicitly covers Windows Quick removal versus Better performance/cached writes, finishing and verifying transfers before safe eject, and comparing source versus failed destination without format assumptions."
  ],
  [
    "android-usb-file-transfer",
    [
      "android-usb-locked-screen-file-list"
    ],
    "The complete Android owner begins with unlocking the device, uses the supported File transfer mode and distinguishes absent device recognition from an inaccessible or missing actual source."
  ],
  [
    "linux-video-file-access-permissions",
    [
      "linux-flatpak-player-folder-access"
    ],
    "The existing complete Linux owner has a dedicated Flatpak sandbox/portal section, explicit supported Open chooser comparison, least-scope permissions and separate decoding checks."
  ],
  [
    "cloud-sync-vs-backup",
    [
      "samsung-gallery-onedrive-sync-scope"
    ],
    "The canonical explicitly distinguishes synchronized additions/edits/deletions and online/offline availability from independently recoverable versions, using OneDrive behavior and a separate non-destructive restore test. A Gallery view is not a separate archive procedure."
  ],
  [
    "storage-space-check",
    [
      "nas-video-user-quota-vs-free-capacity"
    ],
    "The complete owner explicitly checks the actual destination volume and provider/user quota separately from total machine capacity and server processing budgets, preserving errors before scoped writable-location comparisons."
  ],
  [
    "recover-recently-deleted-video",
    [
      "google-photos-account-switch-video"
    ],
    "The complete recovery canonical verifies the correct device/account/collection before diagnosing deletion, separates Google Photos Archive and Trash, and distinguishes unavailable local bytes from permanent deletion. The candidate does not introduce another recovery mechanism."
  ],
  [
    "kdenlive-render-zone-vs-project",
    [
      "kdenlive-render-selected-zone-versus-full",
      "kdenlive-render-marker-multi-export"
    ],
    "The approved native Kdenlive owner covers Full project, Selected zone, Marker Zone and Markers Multi-Export with actual controls, expected output mappings and per-file endpoint verification."
  ],
  [
    "editing-project-roundtrip-transition-loss",
    [
      "editing-project-roundtrip-speed-loss",
      "premiere-edl-limited-timeline-handoff",
      "shotcut-export-edl-resource-loss"
    ],
    "The complete interchange canonical explicitly covers EDL/exchange capability scope, source references and handles, transition versus cut losses, speed ramps/reverse/freeze differences and a receiving render compared with a reference. It does not claim to provide native EDL export controls for either editor."
  ],
  [
    "video-shortcut-vs-retained-file",
    [
      "premiere-project-shortcut-reference",
      "google-drive-shortcut-vs-original-download"
    ],
    "The complete canonical distinguishes the shortcut reference from target bytes, requires locating and copying the actual authorized target and verifies destination independence. A project or cloud shortcut does not introduce a separate preservation mechanism."
  ],
  [
    "editing-project-relative-vs-absolute-paths",
    [
      "premiere-removable-network-media-reference",
      "mac-network-volume-sleep-video-relink"
    ],
    "The complete canonical inspects expected locations and unavailable volumes, verifies the intended source before supported relinking, preserves folder/base relationships and checks actual receiving references rather than swapping a similarly named take."
  ],
  [
    "caption-text-contrast-changing-scenes",
    [
      "caption-placement-obscured-interface"
    ],
    "The complete canonical explicitly reviews text against changing scenes and controls, preserves critical interface/picture information, compares supported receiver styling and verifies the accepted caption/video pair. Its burn-in capability statement was corrected and freshly quality-approved."
  ],
  [
    "premiere-relink-moved-video",
    [
      "premiere-offline-clips-placeholder",
      "premiere-offline-export-slates"
    ],
    "The complete native Premiere owner identifies offline references, checks previous path and actual source identity, uses Link Media with matching properties and verifies the timeline rather than treating a placeholder or disappeared warning as restored media."
  ],
  [
    "browser-download-disk-quota-vs-web-storage",
    [
      "clipchamp-temp-storage-clear-relink"
    ],
    "The approved storage canonical explicitly protects local-only editor projects before clearing site data, separates browser origin allocation from saved sources and requires refreshed project/media reference verification instead of pretending that clearing state recovers unsaved edits."
  ],
  [
    "caption-character-encoding",
    [
      "video-subtitle-font-missing-glyphs"
    ],
    "The complete canonical has explicit missing-glyph-versus-byte-decoding diagnosis, suitable-font/receiver tests, multiple scripts/punctuation review and a separately verified revised sidecar."
  ],
  [
    "automatic-caption-review",
    [
      "caption-non-speech-sound-scope",
      "caption-foreign-dialogue-review",
      "caption-profanity-edited-version-match",
      "caption-source-text-revision-ledger"
    ],
    "The complete canonical checks semantic wording against the exact recording, meaningful non-speech sounds and speaker changes, target-language verification as a separate task, retained generated versus corrected versions and unresolved passages rather than invented words."
  ],
  [
    "caption-line-breaks-and-meaning",
    [
      "caption-reading-speed-lower-third"
    ],
    "The reviewed owner separately checks authored versus receiver wrapping, information density versus available duration and important visuals obscured by text. It requires ordinary-speed receiving review rather than deleting meaningful words to fit a layout."
  ],
  [
    "ass-override-tags-visible-text",
    [
      "ass-drawing-subtitles-vs-dialogue",
      "video-subtitle-tag-rendered-literal"
    ],
    "The complete owner distinguishes rendered ASS overrides, literal source commands and non-dialogue vector drawings, preserves event timing and checks format-aware conversion rather than indiscriminate markup deletion. Generic other-format parsing remains in linked WebVTT and format guides."
  ],
  [
    "caption-language-script-transliteration",
    [
      "caption-translated-track-quality-verification",
      "caption-automatic-translation-source-chain"
    ],
    "The complete owner independently verifies source transcription and qualified target-language meaning, handles inherited recognition errors, labels review scope and checks timing/display after translation instead of mistaking fluency for correctness."
  ],
  [
    "captions-separate-language-files",
    [
      "caption-language-switch-cue-label"
    ],
    "The complete owner explicitly records actual language and caption role, distinguishes separately selectable tracks from mixed unlabeled dialogue, verifies every resource and refuses to relabel another language as a missing translation."
  ],
  [
    "matroska-cues-seek-index",
    [
      "video-index-seek-table-damage"
    ],
    "The complete owner separately compares sequential and seeked playback, inspects indexing/track context, limits remux claims and verifies a saved output without confusing navigation repair with restored encoded pictures."
  ],
  [
    "matroska-ordered-chapters-editions",
    [
      "mkv-linked-segments-archive-scope"
    ],
    "The complete owner gives linked segment identity and resource inventory its own sections, distinguishes a UUID/reference from bytes and verifies the selected edition across external transitions."
  ],
  [
    "matroska-reader-version-versus-document",
    [
      "matroska-virtual-track-subresource-support",
      "matroska-accessibility-track-flags"
    ],
    "The approved owner explicitly separates minimum reader support, virtual/combined track dependencies and default/accessibility purpose flags, requiring actual content and receiver verification rather than inventing an accessibility resource."
  ],
  [
    "closed-vs-open-gop-trim",
    [
      "codec-idr-cra-random-access",
      "codec-intra-refresh-vs-keyframe"
    ],
    "The complete owner explicitly differentiates codec-specific IDR/CRA random-access context, inter-picture dependencies and gradual intra refresh, then verifies actual copied-cut startup instead of treating a generic keyframe flag as universal independence."
  ],
  [
    "codec-parameter-change-midstream",
    [
      "mp4-sample-description-change",
      "mpeg-ts-pid-change-recording"
    ],
    "The complete owner explicitly locates later configuration/raster and program-component changes, identifies MP4 sample-description versus transport signaling context and compares continuous/seeked receiver behavior before a stable derivative."
  ],
  [
    "codec-two-pass-scene-allocation",
    [
      "codec-vbv-receiver-buffer-constraint"
    ],
    "The complete owner separates average-rate targets from decoder buffer/peak constraints, requires the receiving specification and actual encoder/output compatibility checks, and does not equate two-pass success with universal scene quality or exact size."
  ],
  [
    "ffmpeg-astats-channel-evidence",
    [
      "ffmpeg-volumedetect-measurement-scope",
      "ffmpeg-audio-spectral-statistics",
      "ffmpeg-loudnorm-analysis-vs-apply"
    ],
    "The complete owner supplies an explicit bounded stream-mapped analysis, distinguishes cumulative/reset channel statistics from spectral and loudness methods, and clearly separates null-sink reporting from an applied normalization artifact."
  ],
  [
    "ffmpeg-amerge-vs-amix",
    [
      "ffmpeg-pan-channel-routing",
      "ffmpeg-channelsplit-rejoin-layout",
      "ffmpeg-join-audio-common-timing"
    ],
    "The complete canonical explicitly separates amerge channel assembly, amix audible mixing and documented pan/join/split mapping, requires known roles and common timing and verifies speaker layout/headroom/endpoints without inventing isolated stems."
  ],
  [
    "ffmpeg-sidechain-dialogue-reference",
    [
      "ffmpeg-sidechain-gate-trigger"
    ],
    "The new complete owner gives actual main/reference routing and independently discusses gating trigger behavior versus compression, verifies wanted events and prevents the reference being mistaken for final audible dialogue."
  ],
  [
    "google-drive-video-download-permission",
    [
      "shared-drive-link-revocation-copies"
    ],
    "The complete native Drive canonical directly separates owner-controlled future access/download actions from independently retained recipient copies and explicitly rejects universal recall or private delivery-address bypass."
  ],
  [
    "video-file-location-privacy",
    [
      "video-personal-data-export-sharing",
      "video-accessibility-reviewer-sharing-scope"
    ],
    "The complete privacy canonical reviews the actual supplied files, folders and manifests, excludes unrelated personal context and tokens, requires intended authorized audience/channel and inspects the final receiving artifact rather than exposing a whole production archive."
  ],
  [
    "inspect-video-metadata-before-sharing",
    [
      "mov-metadata-location-track-scope",
      "handbrake-native-metadata-passthrough-review",
      "video-content-credentials-sharing-privacy"
    ],
    "The complete canonical performs group-aware actual-file metadata inspection, compares camera/source/exported copies, distinguishes filesystem and embedded information, bounds absence claims and rechecks a revised delivery. It does not promise that a transcode strips private fields or that provenance metadata certifies privacy."
  ],
  [
    "video-permission-revocation-archive-plan",
    [
      "video-retention-expiry-manifest",
      "video-license-audit-expired-source",
      "video-retained-copy-account-deletion"
    ],
    "The approved owner preserves dated terms and source evidence, inventories local/shared copies and ongoing uses, distinguishes expiry/deletion from permission changes and rejects both invented historical terms and universal remote-erasure claims."
  ],
  [
    "video-shared-folder-inherited-access",
    [
      "video-review-link-access-expiry",
      "video-accessibility-reviewer-sharing-scope"
    ],
    "The complete owner checks actual account/link controls, qualified expiry availability, parent/file audience and a limited reviewer package while distinguishing governed access from already retained recipient copies."
  ],
  [
    "video-caption-personal-data-review",
    [
      "video-child-participant-sharing-review"
    ],
    "The complete privacy review identifies audience/purpose and sensitive participant context, requires responsible qualified authorization review without universal legal rules, and examines picture, speech, text and metadata together before a revised handoff."
  ],
  [
    "audio-delay-filter-vs-timestamp-offset",
    [
      "ffmpeg-audio-padding-end-scope",
      "ffmpeg-audio-delay-channel-scope"
    ],
    "The approved owner explicitly distinguishes inserted samples and timestamp movement, shows same-delay stereo scope, requires finite apad requirements and verifies audible beginning/tail against the intended picture instead of guessing a universal sync fix."
  ],
  [
    "ffmpeg-audio-format-negotiation",
    [
      "shotcut-project-audio-channel-layout"
    ],
    "The complete owner separates input, filter negotiation and saved encoder representation; explicitly requires known channel roles rather than relabelling count, verifies real output and distinguishes intended downmixes from metadata assertions. This record is the same project/output layout handoff concept, not a separate native Shotcut settings tutorial."
  ],
  [
    "audio-clipping",
    [
      "ffmpeg-audio-clip-restoration-limits"
    ],
    "The complete canonical explicitly distinguishes lowered clipped samples from recovered source information, calls restoration an estimate, preserves original and derivative roles and verifies affected and unaffected passages."
  ],
  [
    "steady-audio-noise-profile-review",
    [
      "audacity-equalization-vs-noise-removal"
    ],
    "The complete native Audacity canonical identifies steady noise versus other problems, obtains an actual noise-only profile, reviews removed residue and preserves wanted speech. Its procedure is a noise-reduction operation, not changing tone with an equalizer."
  ],
  [
    "speech-noise-gate-quiet-word-review",
    [
      "obs-expander-quiet-speech-review"
    ],
    "The complete pause-attenuation owner reviews quiet wanted words against noise, source-dependent threshold and moderate reduction, timing boundaries and actual export. The candidate is the same attenuation review rather than an OBS-specific setup tutorial."
  ],
  [
    "automatic-caption-review",
    [
      "ffmpeg-audio-subtitle-asr-boundary",
      "clipchamp-native-autocaption-source-review"
    ],
    "The complete review canonical checks actual source speech, names/numbers/negation, selected language and timeline, preserves generated versus corrected text and states reviewed scope rather than promising automatic recognition accuracy."
  ],
  [
    "final-cut-role-stems-vs-mixed-soundtrack",
    [
      "final-cut-range-export-selected",
      "final-cut-export-audio-role-container",
      "final-cut-compound-clip-audio-role-scope"
    ],
    "The complete native Final Cut canonical gives actual Share Export File Settings/Roles controls, range versus clip selection, mono/stereo/surround contribution grouping and separate/multitrack outputs. It verifies contributions against the actual editable project rather than assuming labels isolate stems."
  ],
  [
    "final-cut-multicam-angle-sync-review",
    [
      "final-cut-multicam-angle-order",
      "final-cut-multicam-sync-drift-later",
      "final-cut-sync-audio-reference-choice"
    ],
    "The complete native owner explicitly distinguishes angle assembly/order/synchronization, selects a supported reference, compares beginning and later common events and keeps missing coverage visible."
  ],
  [
    "prores-vs-prores-raw-handoff",
    [
      "prores-proxy-vs-hq-delivery"
    ],
    "The complete ProRes owner explicitly distinguishes conventional Proxy/LT/422/HQ/4444 roles from acquisition RAW, checks the receiver and actual source role and refuses to treat a proxy or larger export as recovered master data."
  ],
  [
    "premiere-import-authorized-srt",
    [
      "premiere-export-caption-track-vs-burn",
      "premiere-captions-visible-track-selection",
      "premiere-caption-track-format-limit"
    ],
    "The native SRT owner gives actual import/Text-panel and intended sequence checks, distinguishes visible/burned picture from separately supplied selectable resources and verifies the actual export rather than inferring delivery from timeline display."
  ],
  [
    "automatic-caption-review",
    [
      "tiktok-auto-captions-owner-edit"
    ],
    "The complete caption review owner checks source speech, meaning, speaker/non-speech cues and matching version, preserves corrected versus generated text and requires actual received timing and review scope rather than claiming recognition success from platform fluency."
  ],
  [
    "ffmpeg-picture-comparison-alignment",
    [
      "ffmpeg-psnr-ssim-limits",
      "ffmpeg-vmaf-reference-scope"
    ],
    "The complete owner includes actual aligned-input SSIM structure, distinguishes timestamp reset from matching content, defines PSNR/SSIM and model-dependent VMAF scope and requires local-detail review rather than universal aggregate quality certification."
  ],
  [
    "ffmpeg-black-frame-detection-review",
    [
      "ffmpeg-freeze-detect-content-review"
    ],
    "The complete owner explicitly contrasts black and freeze candidate detectors, records bounded thresholds/intervals, reviews intentional stillness and sound, and verifies any edited derivative instead of calling every flag source corruption."
  ],
  [
    "video-fingerprint-vs-watermark",
    [
      "ffmpeg-video-signature-similarity"
    ],
    "The existing canonical explicitly distinguishes computed content signatures/fingerprints, visible watermarks and actual byte identity, bounds matching/ownership inferences and requires actual source context rather than treating similarity as permission or original authenticity."
  ],
  [
    "ffmpeg-filtergraph-labelled-output-map",
    [
      "ffmpeg-filtergraph-split-copy-scope"
    ],
    "The complete owner explicitly explains split/asplit processing branches versus independent source copies, labelled connections versus selected output and actual stream/content verification."
  ],
  [
    "ffmpeg-crop-coordinate-frame-bounds",
    [
      "ffmpeg-crop-detection-review",
      "ffmpeg-pad-output-background"
    ],
    "The complete owner supplies bounded crop geometry, separately explains added canvas versus removed content and reviews detector false positives against moving scenes and critical labels."
  ],
  [
    "ffmpeg-transpose-rotation-metadata",
    [
      "ffmpeg-rotate-expanded-canvas",
      "ffmpeg-flip-mirrored-text"
    ],
    "The complete owner distinguishes automatic metadata interpretation, physical transpose, free-angle rotation/canvas and horizontal flip, checking corners and meaningful text before accepting the saved receiving orientation."
  ],
  [
    "ffmpeg-audio-waveform-picture",
    [
      "ffmpeg-waveform-vectorscope-companion",
      "ffmpeg-signalstats-clipping-context"
    ],
    "The complete owner explicitly separates diagnostic waveform/vector/signal views from source media, identifies selected interval and color interpretation and rejects source recovery or whole-program proof from a graphic or clipped-looking signal representation."
  ],
  [
    "video-alpha-channel-handoff",
    [
      "codec-prores-profile-alpha"
    ],
    "The existing complete owner explicitly identifies ProRes 4444/4444 XQ alpha support, distinguishes profile labels from useful transparency, tests a contrasting composite and verifies straight versus premultiplied edge handling in the receiver."
  ],
  [
    "blender-scene-frame-range-sequencer",
    [
      "blender-audio-echo-tail-export"
    ],
    "The complete native owner explicitly reviews scene range, supported sequencer participation and sound-strip/effect tails at the saved endpoint. It does not fabricate a Blender-native echo control and distinguishes completed rendering from retaining the wanted tail."
  ],
  [
    "audacity-selection-vs-entire-project-export",
    [
      "audacity-track-mute-export-scope"
    ],
    "The complete native export-range owner explicitly explains the documented difference between Entire Project excluding mute/solo-inaudible tracks and Current Selection including selected tracks under its own scope, with receiving-mix checks."
  ],
  [
    "audacity-label-track-export-alignment",
    [
      "audacity-export-multiple-label-naming"
    ],
    "The native label-export owner has explicit point/region and uppermost-label-track rules, track-versus-label split choices, unique destination/overwrite and label-number-prefix naming review, followed by per-artifact spoken-boundary verification."
  ],
  [
    "handbrake-default-track-selection-native",
    [
      "handbrake-passthrough-vs-audio-encode",
      "handbrake-native-subtitle-default-selection",
      "handbrake-native-container-track-selection"
    ],
    "The complete native owner gives source/title and Selection Behaviour/Reload checks, supported auto-passthrough masks and fallback encoding, actual subtitle/container versus burn representation and per-resource receiving verification without creating absent languages."
  ],
  [
    "handbrake-queue-item-setting-snapshot",
    [
      "handbrake-queue-import-missing-source",
      "handbrake-queue-retry-single-item",
      "handbrake-native-auto-file-naming-collision"
    ],
    "The complete native queue owner explicitly distinguishes saved job settings from main-window state, uses Edit/re-add, preserves referenced media, checks resolved automatic names and isolates failed/partial artifacts from already verified outputs."
  ],
  [
    "obs-application-audio-capture-source",
    [
      "obs-macos-desktop-audio-native-scope"
    ],
    "The complete owner includes separate documented Windows and macOS source routes, installed-version scope, source identity/visibility and duplicate-capture checks, followed by a real retained sample rather than monitoring-only proof."
  ],
  [
    "obs-monitor-output-routing-distinction",
    [
      "obs-advanced-recording-track-selection",
      "obs-surround-recording-channel-map"
    ],
    "The complete native owner uses Advanced Audio Properties assignments plus Settings Output enabling, distinguishes monitor/track/channel layers and checks actual saved contributions and spatial layout."
  ],
  [
    "obs-recording-encoder-overload",
    [
      "obs-encoding-overload-versus-source-damage"
    ],
    "The complete owner distinguishes capture/render/encode performance from receiver-only decode stalls, preserves logs and actual gaps and tests a controlled lighter recording without pretending to restore uncaptured events."
  ],
  [
    "ffmpeg-reverse-video-memory-scope",
    [
      "ffmpeg-reverse-audio-separate-output"
    ],
    "The canonical reversal guide explicitly explains areverse alongside reverse, trims before buffering, selects and resets both resources, retains a new output and verifies reversed sound and chronology. A separate audio-only guide would repeat the same bounded reversal and saved-output decision; a silent or single-resource graph is addressed as a scope adaptation, not an invented site control."
  ],
  [
    "caption-karaoke-timing-vs-simple-cues",
    [
      "webvtt-inline-timestamp-karaoke",
      "ass-karaoke-timing-vs-subtitle-cues"
    ],
    "The canonical guide explicitly distinguishes WebVTT inline timestamp tags and ASS karaoke override timing from a simple cue interval. It supplies receiver testing, retained-source handoff, intentional simplification and separate wording/progression verification, satisfying both representation-specific candidates without competing pages for the same timing-preservation decision."
  ],
  [
    "ffmpeg-frame-rate-filter-vs-interpolation",
    [
      "ffmpeg-video-sync-frame-dup-drop",
      "ffmpeg-motion-interpolation-edge-review"
    ],
    "The published temporal-conversion guide explicitly covers output synchronization duplication and dropping, fps versus minterpolate, moving edges, scene cuts and occlusions, timestamp/duration verification and complete audio/caption delivery. Both candidates ask for the same cadence-operation identification and derivative acceptance; the canonical supplies their full practical checks rather than inferring captured frames from a rate label."
  ],
  [
    "final-cut-library-media-handoff",
    [
      "final-cut-media-representation-change"
    ],
    "The existing complete native Final Cut library guide specifies original, optimized and proxy copy scope, Library Properties and Consolidate media types, external-source inclusion and receiving-location source checks. It explicitly separates generated representations from source masters and requires source-reference verification, satisfying this representation-availability task without a competing library handoff page."
  ],
  [
    "ass-subtitle-font-attachment-handoff",
    [
      "ffmpeg-ass-render-font-resources",
      "caption-burn-font-license"
    ],
    "The enriched canonical font handoff now supplies a bounded native FFmpeg ass/fontsdir rendering command, installed-filter check, internal font-name and glyph verification, plus separate rendering-versus-font-file-distribution permission review. It explicitly requires the exact font terms and reports unresolved permission without universal legal conclusions. Both dependency and permitted-font-use candidates are fully addressed within this actual styled-caption delivery workflow."
  ],
  [
    "blender-video-sequencer-project-media",
    [
      "blender-sequencer-scene-resource-scope",
      "blender-video-editing-directory-handoff"
    ],
    "The native Blender handoff explicitly inventories the selected sequencer scene, external movies and sound, nested scene and compositor resources, generated previews and original media. It gives supported missing-file and relative-path controls, explains packing limits, preserves the receiving directory structure and verifies an actual destination render. These records repeat that same complete editable-resource delivery intent; a review movie remains separate."
  ],
  [
    "caption-sidecar-not-showing",
    [
      "vlc-android-native-subtitle-file-picker"
    ],
    "The complete sidecar owner already identifies the actual local movie and permitted caption file, documents explicit VLC for Android subtitle-file selection with a primary VideoLAN source, verifies supported format and accessible files, and checks enablement, known cue positions and moved receiving paths. This candidate repeats that file-picker association and access diagnosis; it does not require changing caption content before correct native selection."
  ],
  [
    "ffmpeg-read-embedded-caption-data",
    [
      "codec-captions-sei-retention"
    ],
    "The complete native caption-data guide explicitly addresses applicable SEI/video-carried information, why an ordinary subtitle inventory can omit it, packet-copy versus text-resource claims, an experimental bounded FFmpeg subcc/RCWT path and actual post-remux/transcode service verification. This candidate repeats the same retained-caption representation and receiving-path acceptance decision; the canonical does not promise universal text extraction."
  ],
  [
    "final-cut-delete-generated-media-scope",
    [
      "final-cut-optimized-proxy-delete-recreate",
      "final-cut-library-cache-vs-backup-location"
    ],
    "The native cleanup canonical distinguishes Library Properties source/cache/backups, render versus optimized/proxy categories, external generated storage and supported Delete Generated commands. It requires actual original availability before regeneration and separately preserves database state, satisfying these closely overlapping generated-storage and recoverability decisions without treating previews as masters."
  ],
  [
    "final-cut-snapshot-vs-project-duplicate",
    [
      "final-cut-compound-reference-parent-change",
      "final-cut-compound-clip-vs-export"
    ],
    "The complete snapshot guide explains shared compound and multicam parents, native Duplicate versus Snapshot Project, preserved parent relationships and actual nested-content/output verification. It explicitly distinguishes a compound edit reference from an independent rendered movie and separately requires source/media packaging, fully covering these parent-change and nested-edit retention intents."
  ],
  [
    "final-cut-project-recovery-backup-version",
    [
      "final-cut-library-repair-recoverable-state"
    ],
    "The native recovery canonical preserves the current library and sources, opens a dated backup through From Backup, checks recovered sequence identity and missing external media, and directs an unopenable state to maintained Apple recovery guidance rather than blind database edits. It does not promise missing-file reconstruction or automatic repair; this fulfills the candidate\u2019s safe recoverable-state task."
  ],
  [
    "final-cut-share-destination-vs-render-file",
    [
      "final-cut-browser-range-vs-project-export",
      "final-cut-share-batch-destination",
      "final-cut-share-background-process-completion"
    ],
    "The full native share canonical gives browser project/clip versus timeline range selection, I/O bounds and clip-selection limits, supported batch scope and mixed settings, Export File destination review, Window Background Tasks and per-output receiving verification. These candidates overlap that same selected-source-to-completed-file workflow; the article explicitly checks every batch result and never treats a queue as a delivery."
  ],
  [
    "handbrake-source-scan-versus-encode",
    [
      "handbrake-source-title-selection",
      "handbrake-live-preview-versus-final-output",
      "handbrake-source-supported-but-encode-fails",
      "handbrake-activity-log-source-versus-encode"
    ],
    "The complete native scan-to-encode canonical supplies Open Source, actual Title selection and recognizable-content checks, Preview Position/Duration/Live Preview, separate Start Encode and destination verification, plus Activity Log stages and private-path sanitization. It explicitly rejects scan recognition or a bounded preview as full-file success, completing these overlapping source-selection and encoding-evidence tasks."
  ],
  [
    "vlc-native-transcode-save-destination",
    [
      "vlc-native-remux-versus-convert-profile"
    ],
    "The complete native VLC output guide explicitly distinguishes transcode codecs from std access/file/mux/dst packaging, requires source and saved codec inspection and native profile review, and states that an extension or smaller file is not proof of stream copying. It verifies the actual saved receiving file and retained resources, fully answering this remux-versus-convert intent without a competing output-profile page."
  ],
  [
    "ffmpeg-alpha-extract-companion",
    [
      "ffmpeg-alpha-merge-channel-interpretation"
    ],
    "The complete alpha-companion canonical explicitly explains alphamerge second-input luma, a native mapped reconstruction command, matched geometry/time origin and deliberate frame-sync ending, and actual matte/edge tests over receiving backgrounds. It separates precision and straight/premultiplied interpretation and does not invent missing source transparency, completing this same companion reconstruction intent."
  ],
  [
    "final-cut-smart-collection-vs-folder-copy",
    [
      "final-cut-keyword-range-vs-cut-file",
      "final-cut-favorites-rejected-source-ranges",
      "final-cut-source-analysis-generated-keywords"
    ],
    "The complete native organization guide gives keyword range controls and separate excerpt exports, Favorite/Reject and Hide Rejected/All Clips semantics, and actual analysis-keyword inspection through Skimmer Info or list view. It explains rule-based references versus retained bytes and checks the physical handoff, completing these overlapping organized-source identification tasks without duplicate pages for each metadata label."
  ],
  [
    "final-cut-camera-archive-vs-library",
    [
      "final-cut-spanned-camera-clip-import"
    ],
    "The native camera archive canonical explicitly retains each required card archive, supplies Create Archive and retained-archive import controls, checks Final Cut completeness indicators and tests span boundaries, audio and ending. It distinguishes missing separately imported portions from a complete logical shot, fully answering this spanned-source package and import task."
  ],
  [
    "ffmpeg-interlace-detection-evidence",
    [
      "ffmpeg-field-order-correction"
    ],
    "The complete native interlace guide inspects field flags and moving sections, compares top-versus-bottom-first evidence, distinguishes setfield metadata from pixel transformation and supplies an explicit known-TFF bwdif test with cadence and saved-motion checks. It rejects archive-wide blind correction and verifies audio/caption mapping separately, fully covering this field-order acceptance task."
  ],
  [
    "video-alpha-channel-handoff",
    [
      "ffmpeg-premultiply-alpha-edges"
    ],
    "The enriched canonical alpha guide gives native FFmpeg premultiply/unpremultiply inspection and inplace existing-alpha scope alongside actual straight/premultiplied representation and receiver edge checks. It preserves precision, rejects double premultiplication and tests fades over contrasting backgrounds, fully answering the candidate\u2019s alpha-association diagnosis without promising missing-source recovery."
  ],
  [
    "ffmpeg-stack-input-time-alignment",
    [
      "ffmpeg-stack-resolution-cadence"
    ],
    "The native stack canonical explicitly sets common height and supported pixel representation, records square-pixel SDR assumptions, applies a deliberate fps conversion and verifies output dimensions, aspect and moving events. It identifies duplicate/drop behavior, shortest-input scope and lack of new captured detail, completing this same compatible raster/cadence preparation task for a verified composite."
  ],
  [
    "ffmpeg-overlay-time-origin",
    [
      "ffmpeg-filtergraph-format-before-overlay"
    ],
    "The native overlay canonical explicitly inspects input color/pixel precision, real alpha and negotiated format, sets justified origins and an explicit straight-alpha graph, then checks semitransparent edges and saved ending behavior. It warns that normalization is not unchanged precision or HDR preservation, completing this same compatible-overlay preparation task rather than relying on successful filter negotiation alone."
  ],
  [
    "spotlight-owner-retention-before-delete",
    [
      "snapchat-memories-export-owner-video",
      "spotlight-owner-download-original-vs-published"
    ],
    "The existing complete Snapchat owner-retention guide explicitly gives official Memories swipe-up/hold/Export destination controls and web owner Download, checks actual independent output and compares production parent versus posted edit, duration and sound. It explains that an exported rendition is not necessarily a camera master or editable package and preserves Beta/public-only downloader limits. These candidates repeat that supported owner-export and source-version acceptance workflow."
  ],
  [
    "spotlight-owner-retention-before-delete",
    [
      "snapchat-memories-export-multiple-items"
    ],
    "The enriched native owner-retention guide gives the actual Memories selector, selected-item export controls and a per-recording output inventory and picture/sound/ending check. It distinguishes an exported set from a merged movie, editable originals and published Spotlight renditions, fully completing this quantity variant of the same permitted native export handoff."
  ],
  [
    "instagram-post-caption-edit-vs-video-version",
    [
      "facebook-video-edit-description-version",
      "tiktok-post-edit-vs-movie-version",
      "tiktok-studio-post-management-version"
    ],
    "The complete post-text/version canonical explicitly covers Instagram descriptive captions, Facebook descriptions and TikTok post or creator-management text as publication metadata separate from actual movie versions. It supplies source-ID/change records, prior-artifact preservation, real stream/content/checksum comparison and completed-file verification without inventing universal replacement controls. These candidates ask that same manifest decision, not distinct native menu tutorials."
  ],
  [
    "linux-video-file-access-permissions",
    [
      "linux-mount-option-video-access"
    ],
    "The enriched native access canonical now supplies readonly findmnt target/options inspection, distinguishes disconnected mounts, ro writing scope and noexec binary execution from movie data reading, and keeps network authorization and application portals separate. It requires the narrow authorized remedy and rejects unrelated recursive chmod or protection changes, fully answering this mount-layer access subtask."
  ],
  [
    "premiere-transcript-cut-vs-word-correction",
    [
      "premiere-speaker-filter-removal-scope",
      "premiere-pause-removal-action-review",
      "premiere-caption-speaker-label-correction"
    ],
    "The complete native transcript guide explicitly supplies Edit speaker name, recording-based label verification and the Transcript filter\u2019s speakers/pauses/text bulk controls. It checks necessary questions, overlapping context and silent visual actions before cuts, separates label correction from mixed-voice isolation and verifies the actual revised sequence and output. These candidates are overlapping safeguards within that same transcript-driven edit workflow."
  ],
  [
    "premiere-cache-cleanup-vs-source-delete",
    [
      "premiere-audio-conform-every-open"
    ],
    "The native cache canonical explicitly investigates repeated conforming through configured cache persistence, automatic cleanup policies, normal authorized access and changing source identity. It preserves original audio, distinguishes generated waveform/conform resources from recordings and verifies actual playback, fully completing this cache-lifecycle diagnosis without claiming a universal cause or deleting the source."
  ],
  [
    "ffmpeg-filter-color-conversion-explicit",
    [
      "ffmpeg-colorspace-conversion-metadata",
      "ffmpeg-color-matrix-vs-gamut"
    ],
    "The native conversion canonical explicitly distinguishes matrix, primaries, transfer and range, supplies a source-qualified colorspace transformation and separate output metadata flags, and checks actual receiving pictures and declarations. It rejects tag-only pixel conversion, unknown-input assumptions and restored-detail claims, fully completing these overlapping transformation-versus-interpretation decisions."
  ],
  [
    "premiere-export-in-out-scope",
    [
      "premiere-background-export-project-version"
    ],
    "The native export canonical explicitly records the active sequence, submitted range, queue settings and destination, distinguishes direct export from Media Encoder work and compares the actual output against the submitted version rather than later edits. It preserves accepted project and external dependencies without promising an immutable job snapshot, fully completing this queued-version identity task."
  ],
  [
    "video-tone-map-highlight-review",
    [
      "ffmpeg-tone-map-sdr-delivery"
    ],
    "The full canonical gives actual input/output color interpretation, bounded conversion-sample selection and receiving SDR highlight/gamut checks, explicitly explaining that an isolated native tonemap filter is not a complete or universally valid conversion graph. This candidate asks for that same receiving-SDR acceptance decision."
  ],
  [
    "ffmpeg-temporal-denoise-trailing-edges",
    [
      "video-denoise-temporal-smear"
    ],
    "The approved canonical directly diagnoses motion trails from temporal denoising, compares saved matched passages and separates temporal from spatial native hqdn3d settings. The generic smear candidate is the same artifact and acceptance workflow."
  ],
  [
    "video-player-network-share-stall",
    [
      "movie-network-share-credential-expiry"
    ],
    "The complete owner separates network opening/read/seek failures, explicitly checks expired authorized storage sessions and unavailable mounts, and compares a permitted unchanged local copy. This candidate repeats that network-session boundary rather than asking for credential bypass."
  ],
  [
    "safe-browser-download-warning",
    [
      "movie-download-antivirus-quarantine"
    ],
    "The full canonical identifies malware protection versus transfer failure, checks the expected artifact and warning details, preserves antivirus controls and refers specific evidence for a suspected false positive. The candidate is that same protection-stage diagnosis; it does not require unsafe quarantine-release instructions."
  ],
  [
    "browser-os-open-file-picker-permission",
    [
      "video-open-dialog-extension-filter-hidden"
    ],
    "The reviewed canonical identifies an absent picker listing separately from local availability, selection permission and decoding, uses the supported narrow picker workflow and verifies the selected artifact. An extension-filtered listing is that same selection-stage distinction, not a new media conversion."
  ],
  [
    "archive-checksums",
    [
      "video-archive-dedup-before-delete"
    ],
    "The complete owner compares frozen completed files with the same algorithm, separates byte identity from visual similarity and completeness, preserves independent recoverable copies and warns against choosing a correct copy by size. The candidate repeats this verified duplicate-copy decision, not perceptual deduplication."
  ],
  [
    "closed-vs-open-gop-trim",
    [
      "intra-only-vs-long-gop-editing",
      "all-keyframe-output-file-size"
    ],
    "The canonical explicitly compares inter-picture dependencies with intra-only editing media, requires receiver/configuration/timing compatibility, explains that a larger all-intra derivative does not add camera detail, and verifies the actual cut. Both candidates ask for the same access-versus-representation tradeoff."
  ],
  [
    "ffmpeg-detelecine-source-cadence",
    [
      "ffmpeg-decimate-static-scenes",
      "pulldown-cadence-vs-frame-duplication"
    ],
    "The complete approved owner identifies actual field cadence, native detelecine pattern alignment, fieldmatch versus decimate responsibilities and cycle-based loss of intentional static intervals. It verifies motion and full delivery timing instead of treating every similar frame as expendable. Both candidates repeat that recovery-versus-redundancy decision."
  ],
  [
    "video-backup-restore-test",
    [
      "video-archive-restore-drill-scope"
    ],
    "The actual canonical gives a separate-folder non-destructive restore drill, chooses the failure/version/reference, verifies local bytes, sound and project dependencies, and records observed versus unverified scope. This candidate repeats that exact recoverability test."
  ],
  [
    "duration-stream-vs-container",
    [
      "video-output-picture-longer-than-audio"
    ],
    "The canonical explicitly compares overall and per-stream endpoints, final still holds, shortest-input omission and receiver presentation. It requires checking the actual last visual event and sound instead of padding to match duration numbers. This is the candidate\u2019s same picture/audio endpoint diagnosis."
  ],
  [
    "browser-session-history-back-job-state",
    [
      "preparation-retry-vs-parallel-jobs"
    ],
    "The owner gives current session/job-status verification before resubmission, identifies accidental multiple jobs by actual inputs/settings, rejects unnecessary retries and verifies the one intended ready artifact. The candidate repeats that lifecycle and retry decision, not a new scheduling feature."
  ],
  [
    "video-caption-personal-data-review",
    [
      "caption-speaker-name-consent"
    ],
    "The full canonical explicitly includes caption names, speech and manifests in an audience-specific participant-information review, requires applicable authorization and updates affected resources together. A caption speaker-name review is that same cross-resource disclosure decision, not a standalone legal determination."
  ],
  [
    "archive-manifest",
    [
      "video-archive-offline-index-vs-media"
    ],
    "The full owner distinguishes descriptive inventory and actual retained file identity, records unknowns and separate required media locations, and connects future restore checks to the bytes. A filename/index record is not the media archive itself; the candidate repeats this inventory-versus-retained-artifact distinction."
  ],
  [
    "video-player-network-share-stall",
    [
      "nas-video-transcoding-vs-original"
    ],
    "The owner explicitly distinguishes an actual stored-file copy from a media-server transcoded rendition and uses a controlled same-file local/network comparison. The candidate asks for that same receiving representation comparison, not instructions for proprietary server settings."
  ],
  [
    "thumbnail-vs-video-frame",
    [
      "media-server-metadata-poster-vs-source",
      "windows-explorer-thumbnail-cache-file-identity"
    ],
    "The complete canonical distinguishes representative/custom cover images from actual decoded content and verifies source identity, beginning/middle/end, sound and real stream properties. Neither a server poster nor an Explorer thumbnail establishes the movie bytes or current version. These candidates repeat that recognition-versus-media-evidence intent, not cache-management controls."
  ],
  [
    "video-inside-zip-archive",
    [
      "iphone-files-uncompress-video-package"
    ],
    "The actual owner already gives the specific Apple Files tap-ZIP extraction into a folder, Files-versus-Photos distinction, space and package retention, associated companions and independent movie verification. This is the candidate\u2019s same native package-opening workflow."
  ],
  [
    "local-file-review-versus-hosted-review",
    [
      "google-drive-video-processing-preview",
      "editing-project-remote-review-vs-source-upload",
      "video-cloud-preview-stale-after-replacement"
    ],
    "The approved canonical separates hosted playback preparation from authorized original-file availability, requires the actual receiving account/version and distinguishes reused links/comments from earlier local artifacts. Each candidate repeats this preview/version-versus-retained-source handoff decision rather than a new private-platform extraction feature."
  ],
  [
    "handbrake-native-custom-preset-version",
    [
      "handbrake-cli-preset-import-native"
    ],
    "The enriched complete preset owner now documents installed CLI version/help, actual JSON import and case-sensitive selection, bounded start/duration semantics and independent GUI/CLI artifact comparisons. It explicitly rejects bit-identity and unrelated queued-job assumptions. This is the same portable preset intent with a native CLI path."
  ],
  [
    "handbrake-native-hardware-encoder-unavailable",
    [
      "handbrake-native-hardware-versus-software-encode",
      "codec-hardware-encoder-vs-decoder"
    ],
    "The approved owner explicitly separates runtime encoding from source decoding, identifies CPU contributions during hardware work and gives source/settings-matched hardware/software receiving-output comparisons without equating numeric quality scales. These candidates repeat that processing-path decision and verification."
  ],
  [
    "caption-text-contrast-changing-scenes",
    [
      "caption-safe-placement-vs-video-crop",
      "video-captions-mobile-desktop-different"
    ],
    "The completed canonical now explicitly verifies burned versus selectable text after actual crop/aspect changes, protects meaningful action and checks receiver size/wrapping. It already covers cross-device styling, changing backgrounds and saved-file review. These candidates repeat that caption presentation acceptance, not wording translation or a new crop feature."
  ],
  [
    "ass-subtitle-font-attachment-handoff",
    [
      "video-font-license-package-handoff"
    ],
    "The actual full owner explicitly separates local rendering, font redistribution, attachments and editable project delivery, requires the exact supplied terms and an authorized alternative when resources cannot travel. The generic font-package candidate repeats this resource/use-permission distinction without needing a competing licensing page."
  ],
  [
    "video-will-not-open",
    [
      "video-playback-black-picture-audible"
    ],
    "The complete owner now gives actual stream inspection for audible sound with black or missing picture, separates audio-only content from unsupported or disabled video and compares known scenes across receivers without diagnosing deliberate darkness as loss. This candidate is that same completion/compatibility investigation."
  ],
  [
    "video-decoder-error-concealment",
    [
      "video-first-frame-green-decoder-state",
      "video-intermittent-chroma-flash"
    ],
    "The enriched full canonical explicitly compares startup/seek-only green or color disturbances against recurring same-frame defects, uses unchanged artifacts and decoder evidence, and does not overstate a second receiver or re-encode as original-detail recovery. Both candidates repeat that stored-versus-receiving-decoder decision."
  ],
  [
    "frame-rate-vs-resolution",
    [
      "video-fps-label-vs-motion-duplicates"
    ],
    "The actual owner explicitly distinguishes captured temporal samples from repeated or interpolated pictures, treats advertised averages separately from actual timing and verifies meaningful motion instead of upgrading a label into captured detail. The candidate repeats that motion-evidence distinction."
  ],
  [
    "webvtt-region-layout-handoff",
    [
      "caption-region-rollup-vs-popon"
    ],
    "The enriched owner now explains native scroll:up, region line capacity and text leaving display before cue end, compares normal-speed rolling history with fixed-cue output and requires deliberate wording/timing regrouping. The candidate is that same receiving presentation adaptation."
  ],
  [
    "video-content-credentials-validation-scope",
    [
      "video-content-credentials-external-manifest-handoff",
      "video-content-credentials-remux-derivative"
    ],
    "The actual full canonical preserves embedded or separately supplied manifest resources, validates the exact actual asset with a supported installed validator, separates binding/trust from truth and explicitly revalidates remuxed or edited receiving artifacts instead of copying a parent badge. These candidates repeat that credential-resource and derivative-validation scope, not a new signing capability."
  ],
  [
    "youtube-live-premiere-availability",
    [
      "youtube-premiere-countdown-vs-upload"
    ],
    "The actual complete owner explicitly identifies scheduled/countdown pages, ordinary prerecorded Premieres versus live camera events and the need for a completed actually playable source. It verifies resulting duration rather than manufacturing media from event metadata. This is the same availability-state intent."
  ],
  [
    "video-chapters-vs-separate-files",
    [
      "container-chapter-timebase-rounding",
      "container-chapter-language-labels"
    ],
    "The full owner inspects actual chapter timebase versus raw integers and reported start_time/end_time, verifies receiver navigation against actual scene boundaries, and now explicitly separates language-specific navigation labels from real soundtrack and subtitle languages. Both candidates repeat chapter-metadata interpretation and receiver verification."
  ],
  [
    "ffmpeg-copy-metadata-scope",
    [
      "matroska-segment-title-versus-filename"
    ],
    "The complete metadata owner now includes a specific native format_tags=title inspection, stored global title versus filename/catalog distinction and scoped permitted rewriting with preserved parent/receiver checks. This is the candidate\u2019s same embedded-title handoff intent."
  ],
  [
    "obs-hybrid-recording-finalization",
    [
      "fragmented-mp4-vs-flat-mp4"
    ],
    "The complete owner explicitly distinguishes fragmented media/metadata writing from a conventional finalized presentation, separates layout from codec and completeness, tests the actual receiver and preserves interrupted media without claiming missing samples can be recovered. The generic fragmented/flat candidate is that same layout and receiver decision, with a concrete native example."
  ],
  [
    "ffmpeg-read-embedded-caption-data",
    [
      "cea-608-vs-708-caption-reception"
    ],
    "The actual canonical explicitly covers EIA-608/CEA-708 packet carriage, source/decoder and required service identification, bounded native packet inspection versus editable text and receiving wording/timing verification. This candidate is that same representation/service acceptance boundary, not a promise that a text sidecar supplies broadcast services."
  ],
  [
    "caption-time-reference-wall-clock",
    [
      "caption-live-delay-vs-archived-sync"
    ],
    "The full canonical explicitly separates reading/live-presentation delay from actual event time, establishes recording origin/version and maps only documented intervals with landmark checks. The candidate repeats the live cue-time versus archived recording reference distinction."
  ],
  [
    "editing-project-roundtrip-transition-loss",
    [
      "editing-project-archive-custom-plugin-dependency",
      "editing-project-missing-font-title",
      "editing-project-consolidate-trim-handles"
    ],
    "The approved owner explicitly inventories external fonts/plugins, verifies a receiving render against an accepted reference, preserves originals and labels flattened substitutes as a different deliverable. It also requires actual retained source ranges beyond cuts for transition handles. These candidates repeat that portable editable-dependency/handle acceptance rather than new application-specific installation or licensing controls."
  ],
  [
    "editing-project-relative-vs-absolute-paths",
    [
      "movie-export-missing-linked-still"
    ],
    "The full canonical explicitly inventories graphics/linked visual assets, reconnects only the known retained resource through the supported missing-media workflow and verifies receiving render paths. A movie cannot reconstruct an absent editable still; this candidate repeats that source-dependency recovery boundary."
  ],
  [
    "youtube-screen-reader-video-navigation",
    [
      "caption-keyboard-toggle-state",
      "caption-screen-reader-player-control"
    ],
    "The complete native owner gives real player focus/mode, seek/volume and available caption controls, verifies enabled state against a known cue and keeps text resources distinct from spoken audio or offline files. It uses YouTube as a concrete documented receiver and explicitly refers other implementations to their own accessible controls. These generic candidates repeat the same focus/control and actual caption-state acceptance."
  ],
  [
    "tiktok-reuse-history-before-removal",
    [
      "tiktok-duet-stitch-owner-permission",
      "tiktok-reuse-source-permission-change"
    ],
    "The complete owner already gives actual future-reuse versus existing-history removal scope, explains shared Duet/Stitch controls, verifies retained original before destructive removal and separates platform reuse from independently saved copies. These candidates repeat that same owner-control and affected-source relationship."
  ],
  [
    "public-url-vs-permission",
    [
      "tiktok-credit-video-source-vs-permission"
    ],
    "The reviewed canonical explicitly separates credit and public source accessibility from documented authorization, checks exact included components and intended use, and refuses blanket clearance from uploader or extraction success. This generic attribution-versus-permission question has no separate native TikTok control task."
  ],
  [
    "published-remix-vs-editable-source",
    [
      "facebook-reel-music-mix-vs-stem",
      "spotlight-sound-vs-original-recording",
      "instagram-reel-effects-export-version"
    ],
    "The complete owner checks the actual published movie/version and native stream inventory, explicitly separates a mixed soundtrack from production stems and baked visual effects from interactive settings, and requests authorized parents rather than claiming reconstruction. These candidates ask for that same published-versus-editable representation and owner-retained resource distinction, not separate native creation controls."
  ],
  [
    "premiere-video-track-enable-export",
    [
      "movie-export-no-graphics-preview"
    ],
    "The completed owner gives actual native output inclusion versus targeting/locks, verifies clip interval and obscuring layers, inspects required graphic/font dependencies and compares an actual saved sequence export rather than a source preview. The generic graphics-output candidate repeats this render-scope diagnosis without a separate application-specific task."
  ],
  [
    "premiere-nested-sequence-audio-handoff",
    [
      "movie-export-missing-nested-sequence"
    ],
    "The completed owner gives native child opening, actual parent/child interval and processing scope, media/sound dependency inspection and saved parent rendering comparison. The generic missing nested-output candidate repeats this reference-versus-render investigation."
  ],
  [
    "premiere-music-ducking-dialogue-review",
    [
      "premiere-essential-sound-tag-vs-effect"
    ],
    "The actual full canonical identifies independently adjustable sources, documents Essential Sound role tagging separately from generated Amplify/gain keyframes and explicitly rejects isolating voice or music from a supplied mixed stream. This candidate repeats that classification-versus-processing boundary."
  ],
  [
    "premiere-cache-cleanup-vs-source-delete",
    [
      "editing-project-audio-conform-cache"
    ],
    "The approved native cache owner directly distinguishes generated CFA/PEK waveform/conform resources from actual recorded source sound, uses scoped native cleanup and verifies the receiving artifact without deleting source media. The generic conform-cache candidate repeats that same resource distinction."
  ],
  [
    "http-403-vs-404",
    [
      "analysis-network-timeout-vs-source-gone"
    ],
    "The complete owner now explicitly separates a request deadline from confirmed source absence, compares ordinary permitted page availability with backend stages and gives bounded next steps without credential or network bypass. This candidate repeats that actual-response versus inferred deletion intent."
  ],
  [
    "storage-space-check",
    [
      "merge-failed-disk-space-temporary"
    ],
    "The actual full owner already separates client destination space from server budgets and explicitly bounds aggregate source inputs plus temporary output. It chooses only smaller real source inventory when appropriate, never invents a storage multiplier and does not tell users that freeing phone space expands server capacity. This is the same capacity-stage diagnosis."
  ],
  [
    "ffmpeg-audio-impulse-click-review",
    [
      "video-playback-audio-pops-receiver"
    ],
    "The completed owner now gives controlled same-file, compatible-receiver and ordinary-output comparisons before native repair, distinguishes repeated stored impulses from receiver-only pops and rejects applying de-click to conceal an unestablished cause. The candidate repeats that sound-path versus source artifact diagnosis."
  ],
  [
    "audacity-resample-vs-set-track-rate",
    [
      "video-audio-sample-rate-header-mismatch"
    ],
    "The full canonical directly distinguishes reading unchanged samples under another rate from actual resampling and intentional speed changes, compares pitch/duration/landmarks and requires producer evidence before converting. This candidate repeats the incorrect interpretation-versus-deliberate retiming decision."
  ],
  [
    "iphone-external-drive-files-video-copy",
    [
      "iphone-external-drive-power-availability"
    ],
    "The complete approved owner explicitly diagnoses drive disappearance during copying, gives Apple\u2019s native USB-C/Lightning external-power scope, separates capacity/write/per-file limits and verifies an actual completed receiving movie. The power candidate repeats that copy-access failure boundary, not another tool or formatting task."
  ],
  [
    "browser-os-open-file-picker-permission",
    [
      "android-scoped-storage-picker-access",
      "android-photo-picker-cloud-item"
    ],
    "The completed canonical explicitly distinguishes narrow selected-file/provider access from app gallery or all-storage permission and now verifies cloud/provider retrieval completion separately from thumbnail and authorization. It uses actual supported picking/import and receiving content checks, without inventing Android-version-wide behavior. These candidates repeat that selected scope and real-byte availability decision."
  ],
  [
    "spherical-video-vs-flat-playback",
    [
      "spherical-projection-reframe-derivative"
    ],
    "The full canonical already chooses navigable versus fixed-direction delivery, inspects actual source projection context, verifies important action outside the selected viewpoint and captions in the saved final view, and labels the fixed derivative separately. The candidate is that same receiving-view and preservation-scope decision."
  ],
  [
    "frame-rate-vs-resolution",
    [
      "video-player-wrong-display-refresh"
    ],
    "The enriched complete owner explicitly distinguishes screen refresh from actual encoded/captured cadence, compares the same moving passage under supported display settings and rejects a universal refresh value or fabricated new frames. The candidate repeats that receiving presentation versus source timing diagnosis."
  ],
  [
    "final-cut-multichannel-component-mute",
    [
      "final-cut-audio-component-channel-config"
    ],
    "The complete owner identifies actual channels by content, gives native component selection and configuration review, distinguishes configuration from muting and verifies saved role/channel mixes without inventing participants or another language. The second candidate repeats that same component/configuration acceptance workflow."
  ],
  [
    "final-cut-three-point-edit-range",
    [
      "final-cut-backtimed-edit-source-end"
    ],
    "The newly approved native guide explicitly explains source and destination duration control, Shift-D/Shift-Q backtiming, the fixed ending and overwritten earlier interval. The ending-focused candidate is the same source/destination placement task."
  ],
  [
    "audio-loudness-vs-peak",
    [
      "final-cut-loudness-meter-vs-normalize"
    ],
    "The candidate asks for measurement-versus-processing interpretation rather than an application-specific normalizer. The reviewed owner distinguishes meter evidence, measured interval, playback volume, peak normalization and actual stored processing, with source and output checks."
  ],
  [
    "final-cut-synchronized-clip-source-scope",
    [
      "final-cut-break-apart-synchronized-clip"
    ],
    "The approved synchronized-source guide directly resolves independent source adjustment through Open Clip, active sound and timing checks. It contrasts decomposition and command scope without falsely promising Break Apart for every synchronized container. The candidate is consolidated into that complete relationship-preservation answer."
  ],
  [
    "spotlight-owner-publication-state",
    [
      "spotlight-public-profile-association"
    ],
    "The reviewed owner explicitly distinguishes a profile association from an independent media copy, identifies the native owner submission and requires an actual item link. It fully covers the candidate source-identity and publication-context question."
  ],
  [
    "snapchat-spotlight-temporary-provider-failure",
    [
      "spotlight-age-content-warning-public-access"
    ],
    "The candidate asks for supported public access and content-type boundaries, not an age-setting tutorial. The complete owner diagnoses restricted versus available item access, preserves Beta evidence and forbids credential/private-content workarounds. A second restriction page would repeat that same public extraction boundary."
  ],
  [
    "final-cut-native-convert-closed-captions-to-another-format",
    [
      "final-cut-native-convert-closed-captions-to-subtitles"
    ],
    "The existing canonical was substantively expanded with the complete individually authored caption-to-connected-title workflow, exact selection and duplicate command, preserved originals and visible-versus-selectable delivery checks. The gate detected overlapping URL and intent; consolidation retains the complete useful instructions without weakening that gate."
  ],
  [
    "final-cut-fcpxml-media-references",
    [
      "final-cut-fcpxml-version-compatibility"
    ],
    "The newly approved canonical includes actual File Export XML version selection, current/two-previous compatibility choices, FCPXML 1.10 feature requirements, bundle representation, separate dependencies and receiving import verification. Version and reference candidates are consolidated into one complete interchange acceptance workflow."
  ]
];
const startingRemaining=state.seoCompletion.remainingIDs.length;let count=0;for(const[target,slugs,reason]of groups){const owner=articles.find(x=>x.path.endsWith(`/${target}/`));if(!owner||!published(owner)||owner.approval?.digest!==fingerprint(owner))throw Error(`Unapproved owner ${target}`);for(const slug of slugs){const row=registry.find(x=>x.path.endsWith(`/${slug}/`));if(!row)throw Error(`Missing existing ID ${slug}`);if(!state.seoCompletion.remainingIDs.includes(row.id))continue;row.dispositionHistory=[...(row.dispositionHistory||[]),row.disposition];Object.assign(row,{status:'ARCHIVED',indexable:false,inventoryApproval:null,semanticReview:{state:'MERGED_EXISTING_TASK',reviewer:'938-queue full-body canonical ownership review',reviewedAt:'2026-10-13',comparisons:[owner.path],rationale:reason},disposition:{classification:'MERGE_WITH_EXISTING',outcome:'CONSOLIDATED',destination:owner.path,internalLinkDestination:owner.path,reason,reviewedAt:'2026-10-13'},candidateCompletion:{completedAt:'2026-10-13',result:'MERGED',publicationEligible:false,missingRequirements:[]}});state.seoCompletion.decisions.push({id:row.id,path:row.path,outcome:'MERGED',destination:owner.path,reason});state.seoCompletion.completedIDs.push(row.id);state.seoCompletion.remainingIDs=state.seoCompletion.remainingIDs.filter(id=>id!==row.id);count++;}}
const m=state.seoCompletion;m.processed=m.completedIDs.length;m.merged=m.decisions.filter(d=>d.outcome==='MERGED').length;m.stillDeferred=m.remainingIDs.length;m.unprocessed=m.remainingIDs.length;m.lastCompletedID=m.decisions.at(-1)?.id;state.phases.E.remainingAuthoringIDs=m.remainingIDs;state.phases.E.remainingIDs=m.remainingIDs;state.phases.E.remainingDrafts=m.remainingIDs.length;state.remainingAuthoringRecords=m.remainingIDs.length;state.seoCompletion.batches??=[];if(count)state.seoCompletion.batches.push({date:'2026-10-13',startingRemaining,published:0,merged:count,rejected:0,completedThisBatch:count,remaining:m.remainingIDs.length});
fs.writeFileSync('content/editorial/first-500-inventory.json.tmp',JSON.stringify(registry,null,2)+'\n');fs.renameSync('content/editorial/first-500-inventory.json.tmp','content/editorial/first-500-inventory.json');fs.writeFileSync('docs/video-tools-execution-state.json',JSON.stringify(state,null,2)+'\n');console.log({newMerges:count,lifetimeProcessed:m.processed,published:m.published,remaining:m.remainingIDs.length});
