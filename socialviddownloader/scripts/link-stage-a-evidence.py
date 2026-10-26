"""Connect draft hypotheses to bulk-discovered official source leads.

A navigation lead is not a reviewed primary article or factual approval.
This script never changes article content, eligibility, or candidate decisions.
"""
import json,re
from pathlib import Path
p=Path('content/editorial/first-500-inventory.json');r=json.loads(p.read_text());sources=json.loads(Path('content/editorial/stage-a-source-opportunities.json').read_text())
def words(t):return set(re.findall(r'[a-z0-9]{3,}',t.lower()))-{'premiere','video','actual','retained','the','and','for','with','from','into'}
def score(a,b):return len(a&b)/len(a|b) if a|b else 0
for s in sources:s['_words']=words(s['topicKey'])
linked=0
youtube_topics={
 'youtube-preferred-language-versus-source-track':'13339776',
 'youtube-video-audio-enhancement-source-role':'16619284',
 'youtube-transcript-panel-resource-version':'15930243',
 'youtube-tv-captions-receiver-setting':'15921047',
 'youtube-screen-reader-video-navigation':'189278',
 'youtube-create-project-media-retention':'13521789',
 'youtube-create-save-versus-upload':'13521602',
 'youtube-create-upload-failure-stage':'13521687',
 'youtube-create-caption-export-role':'13818789',
 'youtube-create-animation-timing-export':'13522106',
 'youtube-create-template-asset-dependencies':'16399142',
 'youtube-create-generated-content-provenance':'16631240',
 'youtube-create-audio-track-review':'13521394',
 'youtube-short-template-vs-source-project':'16738000',
 'youtube-short-generated-soundtrack-label':'14151606',
 'youtube-shorts-generated-picture-source':'15260303',
 'youtube-shorts-source-video-owner-excerpt':'12836917',
 'youtube-owner-add-audio-description':'16166822',
 'youtube-subtitle-editor-authorized-access':'11983512',
 'youtube-caption-file-receiver-supported-format':'2734698',
 'youtube-translated-title-versus-caption':'6289575',
 'youtube-source-language-update-role':'6304325',
 'youtube-auto-caption-native-delete':'2734705',
 'youtube-copyright-music-panel-resource':'7680188',
}
open_source_topics={
 'blender-sequencer-scene-resource-scope':'sequencer_scene',
 'blender-video-editing-directory-handoff':'setup/directory_structure',
 'blender-movie-strip-source-start':'edit/montage/strips/movie',
 'blender-sound-strip-movie-association':'edit/montage/strips/sound',
 'blender-image-sequence-strip-timing':'edit/montage/strips/image',
 'blender-scene-strip-nested-output':'edit/montage/strips/scene',
 'blender-clip-strip-versus-movie-strip':'edit/montage/strips/clip',
 'blender-mask-strip-source-dependency':'edit/montage/strips/mask',
 'blender-adjustment-strip-coverage':'edit/montage/strips/adjustment',
 'blender-compositor-strip-render-dependency':'edit/montage/strips/compositor',
 'blender-multicam-selector-source-alignment':'edit/montage/strips/effects/multicam',
 'blender-speed-control-audio-handoff':'edit/montage/strips/effects/speed_control',
 'blender-alpha-over-under-layer-order':'edit/montage/strips/effects/alpha_over_under',
 'blender-cross-versus-gamma-cross':'edit/montage/strips/transitions/gamma_cross',
 'blender-wipe-transition-source-boundaries':'edit/montage/strips/transitions/wipe',
 'blender-sound-crossfade-overlap':'edit/montage/strips/transitions/sound_crossfade',
 'blender-strip-color-balance-source-context':'edit/montage/modifiers/color_balance',
 'blender-tone-map-view-versus-output':'edit/montage/modifiers/tone_map',
 'blender-strip-white-balance-reference':'edit/montage/modifiers/white_balance',
 'blender-strip-mask-modifier-scope':'edit/montage/modifiers/mask',
 'blender-audio-pitch-modifier-context':'edit/montage/modifiers/pitch',
 'blender-audio-echo-tail-export':'edit/montage/modifiers/echo',
 'blender-sound-equalizer-receiver-review':'edit/montage/modifiers/sound_equalizer',
 'blender-meta-strip-nested-edit-scope':'edit/montage/meta',
 'blender-storyboard-versus-sequencer-delivery':'storyboarding/app_template',
 'obs-hybrid-recording-finalization':'hybrid-mp4',
 'obs-advanced-recording-track-selection':'advanced-recording-settings-guide',
 'obs-recording-encoder-preset-receiver':'recording-encoder-presets-guide',
 'obs-media-source-close-reopen-state':'media-sources',
 'obs-image-source-file-update':'image-sources',
 'obs-video-capture-resolution-source':'video-capture-sources',
 'obs-application-audio-capture-source':'application-audio-capture-guide',
 'obs-macos-desktop-audio-native-scope':'macos-desktop-audio-capture-guide',
 'obs-monitor-output-routing-distinction':'audio-mixer-guide',
 'obs-expander-quiet-speech-review':'expander-filter',
 'obs-audio-polarity-route-review':'invert-polarity-filter',
 'obs-surround-recording-channel-map':'surround-sound-guide',
 'obs-encoding-overload-versus-source-damage':'encoding-performance-troubleshooting',
 'obs-wrong-gpu-native-capture':'gpu-selection-guide',
 'obs-game-capture-blank-source':'game-capture-troubleshooting',
 'kdenlive-archive-package-scope':'project_and_asset_management/file_management/archiving',
 'kdenlive-autosave-backup-version':'project_and_asset_management/file_management/auto_save',
 'kdenlive-project-bin-versus-library':'project_and_asset_management/project_bin',
 'kdenlive-effect-clip-track-master-scope':'effects_and_filters',
 'kdenlive-effect-zone-keyframe-scope':'effects_and_filters',
 'kdenlive-custom-effect-stack-dependency':'effects_and_filters',
 'kdenlive-render-preset-receiver':'exporting/render',
 'kdenlive-render-complete-open-output':'exporting/render',
}
open_source_topics.update({
 'kdenlive-ripple-delete-aligned-tracks':'cutting_and_assembling/editing',
 'kdenlive-slip-edit-source-window':'cutting_and_assembling/editing',
 'kdenlive-spacer-selected-track-scope':'cutting_and_assembling/editing',
 'kdenlive-edit-insert-versus-overwrite':'cutting_and_assembling/editing',
 'kdenlive-three-point-source-target':'cutting_and_assembling/editing',
 'kdenlive-linked-audio-video-split':'cutting_and_assembling/editing',
 'kdenlive-multiple-item-resize-scope':'cutting_and_assembling/editing',
 'kdenlive-nested-sequence-source-change':'cutting_and_assembling/sequence',
 'kdenlive-sequence-copy-project-dependencies':'cutting_and_assembling/sequence',
 'kdenlive-sequence-duplicate-version-scope':'cutting_and_assembling/sequence',
 'kdenlive-sequence-specific-output-settings':'cutting_and_assembling/sequence',
 'kdenlive-sequence-timecode-offset':'cutting_and_assembling/sequence',
 'kdenlive-nested-waveform-update':'cutting_and_assembling/sequence',
 'kdenlive-native-subtitle-style-scope':'effects_and_filters/subtitles',
 'kdenlive-native-subtitle-layer-order':'effects_and_filters/subtitles',
 'kdenlive-native-subtitle-import-export-scope':'effects_and_filters/subtitles',
 'kdenlive-native-subtitle-mkv-selection':'effects_and_filters/subtitles',
 'kdenlive-native-subtitle-line-split-timing':'effects_and_filters/subtitles',
 'kdenlive-native-speech-recognition-model':'effects_and_filters/speech_to_text',
 'kdenlive-native-transcript-created-clips':'effects_and_filters/speech_to_text',
 'kdenlive-native-silence-detection-selection':'effects_and_filters/speech_to_text',
 'kdenlive-render-selected-zone-versus-full':'exporting/render',
 'kdenlive-render-marker-multi-export':'exporting/render',
 'kdenlive-render-script-source-dependencies':'exporting/render',
 'kdenlive-render-parallel-resource-limits':'exporting/render',
})
native_retention_topics={
 'firefox-picture-in-picture-caption-handoff':'firefox-picture-in-picture',
 'picture-in-picture-window-vs-retained-file':'firefox-picture-in-picture',
 'icloud-windows-video-hydration-progress':'icloud-photos-windows',
 'icloud-video-edit-windows-sync-direction':'icloud-photos-windows',
 'icloud-browser-video-export-representation':'icloud-export-representation',
 'windows-photos-remove-library-vs-delete-file':'photos-library-file-actions',
 'facebook-video-reels-unified-creation':'facebook-unified-reel-creation',
 'facebook-reel-desktop-vs-mobile-editing':'facebook-create-reel',
 'facebook-reel-owner-remix-controls':'facebook-create-reel',
 'facebook-video-caption-language-file-name':'facebook-caption-upload',
 'spotlight-remix-source-versus-composite':'native-snap-remix',
 'spotlight-snap-comment-vs-original-video':'spotlight-snap-comment',
 'spotlight-owner-comment-moderation-scope':'spotlight-disable-comments',
 'spotlight-timed-text-versus-transcript':'spotlight-creator-timed-caption',
}
playback_encoder_topics={'handbrake-source-scan-versus-encode': ('HandBrake official documentation',
                                         'workflow/open-video-source'),
 'handbrake-source-title-selection': ('HandBrake official documentation', 'workflow/open-video-source'),
 'handbrake-point-range-native-selection': ('HandBrake official documentation',
                                            'advanced/point-to-point'),
 'handbrake-live-preview-versus-final-output': ('HandBrake official documentation',
                                                'workflow/preview-settings'),
 'handbrake-queue-item-setting-snapshot': ('HandBrake official documentation', 'advanced/queue'),
 'handbrake-queue-import-missing-source': ('HandBrake official documentation', 'advanced/queue'),
 'handbrake-queue-retry-single-item': ('HandBrake official documentation', 'advanced/queue'),
 'handbrake-native-custom-preset-version': ('HandBrake official documentation',
                                            'advanced/custom-presets'),
 'handbrake-default-track-selection-native': ('HandBrake official documentation',
                                              'advanced/audio-subtitle-defaults'),
 'handbrake-native-subtitle-default-selection': ('HandBrake official documentation',
                                                 'advanced/audio-subtitle-defaults'),
 'handbrake-foreign-audio-search-review': ('HandBrake official documentation', 'advanced/subtitles'),
 'handbrake-burned-and-soft-caption-output': ('HandBrake official documentation', 'advanced/subtitles'),
 'handbrake-import-srt-native-encoding': ('HandBrake official documentation', 'advanced/subtitles'),
 'handbrake-native-crop-auto-review': ('HandBrake official documentation', 'advanced/resizing-video'),
 'handbrake-native-rotation-dimension-order': ('HandBrake official documentation',
                                               'advanced/resizing-video'),
 'handbrake-native-upscale-source-detail': ('HandBrake official documentation',
                                            'advanced/resizing-video'),
 'handbrake-native-surround-passthrough-fallback': ('HandBrake official documentation',
                                                    'advanced/surround-sound'),
 'handbrake-native-drc-versus-loudness': ('HandBrake official documentation',
                                          'technical/dynamic-range-compression'),
 'handbrake-native-audio-gain-headroom': ('HandBrake official documentation', 'technical/audio-quality'),
 'handbrake-chapter-import-source-range': ('HandBrake official documentation',
                                           'advanced/chapter-markers'),
 'handbrake-native-metadata-passthrough-review': ('HandBrake official documentation',
                                                  'advanced/metadata-passthru'),
 'handbrake-activity-log-source-versus-encode': ('HandBrake official documentation',
                                                 'help/activity-log'),
 'handbrake-native-process-isolation-worker': ('HandBrake official documentation',
                                               'technical/process-isolation'),
 'handbrake-native-bit-depth-output-check': ('HandBrake official documentation',
                                             'technical/video-bit-depth'),
 'handbrake-native-hdr-metadata-handoff': ('HandBrake official documentation', 'technical/hdr'),
 'handbrake-native-filter-chain-review': ('HandBrake official documentation',
                                          'technical/filters-summary'),
 'handbrake-native-hardware-encoder-unavailable': ('HandBrake official documentation',
                                                   'technical/video-codecs'),
 'handbrake-native-hardware-versus-software-encode': ('HandBrake official documentation',
                                                      'technical/video-presets-tunes'),
 'handbrake-native-auto-file-naming-collision': ('HandBrake official documentation',
                                                 'technical/automatic-file-naming'),
 'handbrake-native-container-track-selection': ('HandBrake official documentation',
                                                'technical/containers'),
 'handbrake-source-supported-but-encode-fails': ('HandBrake official documentation',
                                                 'technical/source-formats'),
 'handbrake-cli-preset-import-native': ('HandBrake official documentation', 'advanced/custom-presets'),
 'vlc-native-external-audio-playback': ('VideoLAN official VLC user documentation',
                                        'desktop/3.0/en/advanced/player/external_audio_track'),
 'vlc-native-multiple-instances-review': ('VideoLAN official VLC user documentation',
                                          'desktop/3.0/en/advanced/player/play_multiple_instances'),
 'vlc-native-transcode-save-destination': ('VideoLAN official VLC user documentation',
                                           'desktop/3.0/en/advanced/transcode/transcode_and_save'),
 'vlc-native-stream-versus-save-output': ('VideoLAN official VLC user documentation',
                                          'desktop/3.0/en/advanced/transcode/transcode_and_stream'),
 'vlc-native-batch-output-overwrite': ('VideoLAN official VLC user documentation',
                                       'desktop/3.0/en/advanced/transcode/batch_encode'),
 'vlc-native-audio-extraction-selected-stream': ('VideoLAN official VLC user documentation',
                                                 'desktop/3.0/en/advanced/transcode/extract_audio'),
 'vlc-native-merge-order-output-review': ('VideoLAN official VLC user documentation',
                                          'desktop/3.0/en/advanced/transcode/merge_videos'),
 'vlc-native-remux-versus-convert-profile': ('VideoLAN official VLC user documentation',
                                             'desktop/3.0/en/advanced/streaming/remuxing'),
 'vlc-native-record-playback-range': ('VideoLAN official VLC user documentation',
                                      'desktop/3.0/en/basic/recording/playing'),
 'vlc-native-recording-folder-discovery': ('VideoLAN official VLC user documentation',
                                           'desktop/3.0/en/basic/recording/playing'),
 'vlc-native-snapshot-vs-cover-art': ('VideoLAN official VLC user documentation',
                                      'desktop/3.0/en/basic/video'),
 'vlc-native-subtitle-selection-encoding': ('VideoLAN official VLC user documentation',
                                            'desktop/3.0/en/basic/subtitles'),
 'vlc-native-subtitle-delay-session': ('VideoLAN official VLC user documentation',
                                       'desktop/3.0/en/basic/settings/adjustmentsandeffects'),
 'vlc-native-audio-delay-session': ('VideoLAN official VLC user documentation',
                                    'desktop/3.0/en/basic/settings/adjustmentsandeffects'),
 'vlc-native-video-crop-session': ('VideoLAN official VLC user documentation',
                                   'desktop/3.0/en/basic/video'),
 'vlc-native-deinterlace-playback-review': ('VideoLAN official VLC user documentation',
                                            'desktop/3.0/en/basic/video'),
 'vlc-native-volume-above-reference': ('VideoLAN official VLC user documentation',
                                       'desktop/3.0/en/basic/audio'),
 'vlc-native-playlist-external-media': ('VideoLAN official VLC user documentation',
                                        'desktop/3.0/en/basic/media'),
 'vlc-android-native-video-grouping': ('VideoLAN official VLC user documentation',
                                       'android/3.X/en/video/video_explorer'),
 'vlc-android-native-library-rescan': ('VideoLAN official VLC user documentation',
                                       'android/3.X/en/video/video_explorer'),
 'vlc-android-native-subtitle-file-picker': ('VideoLAN official VLC user documentation',
                                             'android/3.X/en/video/video_player'),
 'vlc-android-native-audio-track-name': ('VideoLAN official VLC user documentation',
                                         'android/3.X/en/video/video_player'),
 'vlc-ios-native-video-app-storage': ('VideoLAN official VLC user documentation',
                                      'ios/3.X/en/basic/mediagroups'),
 'vlc-ios-native-delete-media-scope': ('VideoLAN official VLC user documentation',
                                       'ios/3.X/en/basic/audio'),
 'vlc-ios-native-group-movie-identity': ('VideoLAN official VLC user documentation',
                                         'ios/3.X/en/basic/mediagroups'),
 'vlc-ios-native-playlist-scope': ('VideoLAN official VLC user documentation',
                                   'ios/3.X/en/basic/playlist'),
 'vlc-native-spherical-projection-selection': ('VideoLAN official VLC user documentation',
                                               'desktop/3.0/en/advanced/player/360_video'),
 'vlc-native-stereo-display-handoff': ('VideoLAN official VLC user documentation',
                                       'desktop/3.0/en/advanced/player/3d_display')}
open_source_topics.update({'blender-strip-slip-source-boundary': 'edit/montage/editing',
 'blender-strip-overlap-edit-mode': 'edit/montage/editing',
 'blender-gap-removal-selection-scope': 'edit/montage/editing',
 'blender-retiming-transition-source-audio': 'edit/montage/editing',
 'blender-freeze-retiming-slide-duration': 'edit/montage/editing',
 'blender-hold-split-source-offset': 'edit/montage/editing',
 'blender-linked-strip-duplicate-data-scope': 'edit/montage/editing',
 'blender-scene-frame-range-sequencer': 'edit/montage/editing',
 'blender-image-strip-separate-sequence': 'edit/montage/editing',
 'blender-effect-input-reassignment': 'edit/montage/editing',
 'blender-strip-mute-render-scope': 'edit/montage/editing',
 'blender-movie-set-render-size-project': 'edit/montage/editing',
 'blender-sequencer-fit-fill-stretch': 'edit/montage/editing',
 'blender-sequencer-crop-vs-transform': 'edit/montage/strips/strip_properties',
 'blender-strip-color-space-source': 'edit/montage/strips/strip_properties',
 'blender-sound-strip-mono-representation': 'edit/montage/strips/strip_properties',
 'blender-sound-waveform-cache-vs-resource': 'edit/montage/strips/strip_properties',
 'blender-sequencer-cache-stale-preview': 'sequencer/sidebar/cache',
 'blender-proxy-timecode-source-seek': 'sequencer/sidebar/proxy',
 'blender-custom-proxy-directory-handoff': 'sequencer/sidebar/proxy'})
microsoft_native_topics={'clipchamp-locate-files-cache-versus-source': 'why-do-i-need-to-locate-my-files',
 'clipchamp-content-backup-completion': 'using-content-backup',
 'clipchamp-temp-storage-clear-relink': 'why-does-clipchamp-store-temporary-files-on-my-computer',
 'clipchamp-project-second-computer-assets': 'can-i-work-on-my-clipchamp-editing-project-on-a-different-computer',
 'clipchamp-native-recovery-export-versus-source': 'can-i-recover-videos-and-recordings-in-clipchamp',
 'clipchamp-native-unsaved-change-state': 'why-have-i-lost-changes-to-my-video-editing-project',
 'clipchamp-onedrive-project-asset-folder': 'troubleshooting-onedrive-backed-clipchamp-editing-projects',
 'clipchamp-missing-stock-asset-derivative': 'how-to-update-and-fix-your-video-if-a-stock-asset-has-been-deleted',
 'clipchamp-unsupported-input-representation': 'why-am-i-seeing-an-unsupported-file-type-error',
 'clipchamp-unsupported-hardware-browser': 'why-is-my-hardware-unsupported',
 'clipchamp-iphone-import-preparation': 'what-to-do-if-your-iphone-videos-are-slow-to-import-into-clipchamp',
 'clipchamp-export-output-size-change': 'why-your-output-video-file-may-be-larger-than-the-original',
 'clipchamp-exported-file-vs-youtube-upload': 'why-does-my-upload-from-clipchamp-to-youtube-fail',
 'clipchamp-native-export-download-destination': 'exporting-from-clipchamp-troubleshooting',
 'clipchamp-native-source-import-vs-timeline': 'how-to-add-media-to-a-video-in-clipchamp',
 'clipchamp-native-remove-asset-versus-instance': 'how-to-delete-media-from-a-video',
 'clipchamp-google-drive-source-import-context': 'how-to-add-files-from-google-drive-to-clipchamp',
 'clipchamp-native-gif-timeline-duration': 'how-to-add-gifs-to-videos',
 'clipchamp-native-still-duration-output': 'how-to-change-the-duration-of-an-image-on-the-timeline',
 'clipchamp-native-voice-recorder-source-retention': 'how-to-use-the-voice-recorder',
 'clipchamp-native-ai-voice-source-label': 'how-to-use-the-text-to-speech-feature',
 'clipchamp-native-webcam-mirrored-preview': 'why-does-my-text-show-up-mirrored-when-i-record-a-webcam-video',
 'clipchamp-native-screen-recording-two-resources': 'how-to-make-a-screen-recording',
 'clipchamp-native-group-edit-resource-scope': 'how-to-group-assets-on-the-timeline',
 'clipchamp-native-multi-item-trim-scope': 'how-to-use-multi-item-editing',
 'clipchamp-native-picture-in-picture-layer': 'how-to-use-picture-in-picture',
 'clipchamp-native-green-screen-edge-review': 'how-to-use-the-green-screen-effect-in-clipchamp',
 'clipchamp-native-separated-audio-timeline': 'how-to-mute-separate-and-delete-audio-from-video',
 'clipchamp-native-noise-suppression-review': 'how-to-use-noise-suppression',
 'clipchamp-native-silence-removal-sync': 'how-to-use-silence-removal',
 'clipchamp-native-autocaption-source-review': 'how-to-use-autocaptions-in-clipchamp',
 'clipchamp-native-caption-sidecar-vs-render': 'how-to-use-autocaptions-in-clipchamp',
 'clipchamp-native-template-source-dependency': 'what-to-do-if-your-clipchamp-project-or-assets-aren-t-loading',
 'clipchamp-native-transition-source-boundary': 'how-to-add-transitions-and-fades-to-videos',
 'clipchamp-native-aspect-ratio-crop-review': 'how-to-change-the-aspect-ratio-of-a-video',
 'clipchamp-native-generated-background-layer': 'how-to-add-color-and-gradient-backgrounds-to-videos',
 'clipchamp-native-auto-composition-source-review': 'how-to-use-video-auto-composition',
 'clipchamp-native-watermark-stock-context': 'does-clipchamp-add-a-watermark-to-videos',
 'clipchamp-native-resolution-source-limit': '4k-video-support-in-clipchamp',
 'm365-player-alternate-audio-resource': 'using-alternative-audio-tracks-in-a-video',
 'm365-player-transcript-owner-edit': 'view-edit-and-manage-video-transcripts-and-captions',
 'm365-player-transcript-delete-retained-copy': 'delete-a-video-s-transcript-and-captions-file',
 'm365-player-trim-versus-retained-file': 'how-to-trim-videos-in-microsoft-clipchamp-s-video-player',
 'm365-player-chapters-vs-embedded-markers': 'creating-and-managing-chapters-for-videos-in-the-clipchamp-player',
 'm365-player-custom-thumbnail-vs-file': 'include-a-custom-thumbnail-for-your-video-or-audio-file-in-the-clipchamp-video-player',
 'm365-player-noise-suppression-session': 'using-noise-suppression-in-the-clipchamp-video-player',
 'm365-player-embed-recipient-access': 'embedding-a-clipchamp-video-or-audio-file-in-third-party-sites',
 'm365-native-playlist-source-availability': 'video-playlists-in-onedrive-and-sharepoint',
 'm365-native-video-share-copy-scope': 'share-a-video-or-audio-file-across-microsoft-365',
 'm365-native-screen-recording-permission-scope': 'troubleshoot-camera-microphone-and-screen-recording-permissions-in-clipchamp',
 'm365-native-meeting-chapters-transcript-review': 'auto-generated-chapters-on-teams-meeting-videos'}
shotcut_task_topics={'shotcut-export-source-playlist-timeline': 'export-basics',
 'shotcut-mlt-nested-clip-resource-scope': 'open-mlt-xml-as-clip',
 'shotcut-backup-save-recovery-version': 'file-backup-and-save',
 'shotcut-resource-dialog-missing-handoff': 'resources-dialog',
 'shotcut-export-edl-resource-loss': 'export-edl',
 'shotcut-filter-trim-duration-context': 'trimming-filters',
 'shotcut-export-failure-timeline-region': 'export-failed-find-solutions',
 'shotcut-edit-friendly-conversion-resource': 'convert-to-edit-friendly-dialog',
 'shotcut-vfr-source-edit-sync': 'editing-variable-frame-rate-source-clips',
 'shotcut-hdr-processing-receiving-output': 'editing-hdr-source-clips',
 'shotcut-project-audio-channel-layout': 'audio-channels',
 'shotcut-video-mode-change-layout': 'video-mode',
 'shotcut-nearest-neighbor-seeking-accuracy': 'interpolation',
 'shotcut-realtime-preview-drops-vs-export': 'realtime-frame-dropping',
 'shotcut-source-player-versus-project': 'source-vs-project-player',
 'shotcut-ripple-all-tracks-sync-scope': 'timeline-ripple-all-tracks',
 'shotcut-adjustment-clip-filter-coverage': 'timeline-adjustment-clip',
 'shotcut-auto-duck-reference-track': 'automatic-audio-ducking',
 'shotcut-align-reference-track-offset': 'align-to-reference-track',
 'shotcut-voiceover-take-resource-retention': 'record-audio-voice-over',
 'shotcut-replace-clip-filter-time-scope': 'replace-command',
 'shotcut-filter-copy-scope-keyframes': 'apply-copied-filters',
 'shotcut-transition-overlap-source-handles': 'creating-a-transition',
 'shotcut-custom-wipe-resource-handoff': 'creating-a-custom-video-wipe',
 'shotcut-subtitles-panel-track-export': 'subtitles-panel',
 'shotcut-speech-text-transcript-review': 'speech-to-text-subtitles',
 'shotcut-caption-tts-generated-narration': 'subtitles-text-to-speech',
 'shotcut-export-preset-versus-project-mode': 'creating-export-presets',
 'shotcut-hardware-encode-failed-fallback': 'hardware-encoding',
 'shotcut-export-metadata-versus-project-notes': 'embedding-metadata-into-exports',
 'shotcut-command-line-export-source-context': 'export-at-the-command-line',
 'shotcut-filter-set-external-plugin-handoff': 'external-plugin-support-openfx-vst2-and-lv2',
 'shotcut-time-remap-audio-boundary': 'time-remap-filter',
 'shotcut-project-mlt-vs-movie': 'project-management',
 'shotcut-proxy-vs-export-original': 'proxy-editing'}
normative_task_topics={'video-content-credentials-validation-scope': 'content-credentials-specification',
 'video-content-credentials-external-manifest-handoff': 'content-credentials-specification',
 'video-content-credentials-remux-derivative': 'content-credentials-specification',
 'video-content-credentials-ingredient-resources': 'content-credentials-specification',
 'video-content-credentials-sharing-privacy': 'content-credentials-security',
 'video-content-credentials-signer-vs-creator': 'content-credentials-specification',
 'video-content-credentials-missing-versus-invalid': 'content-credentials-specification',
 'hls-webvtt-timestamp-map-local-handoff': 'hls-webvtt-segments',
 'hls-webvtt-segment-crossing-cues': 'hls-webvtt-segments',
 'hls-webvtt-empty-segment-versus-missing-captions': 'hls-webvtt-segments',
 'ttml-relative-container-timing-handoff': 'ttml2',
 'ttml-clock-frame-tick-expression': 'ttml2',
 'ttml-profile-required-feature-reception': 'ttml2',
 'ttml-external-font-image-resource-retention': 'ttml2',
 'ttml-region-coordinate-viewport': 'ttml2',
 'ttml-namespace-validation-versus-caption-support': 'ttml2',
 'ttml-whitespace-preservation-dialogue': 'ttml2',
 'ttml-image-caption-versus-editable-text': 'ttml2',
 'webvtt-cue-identifier-versus-visible-text': 'webvtt1',
 'webvtt-note-style-region-payload': 'webvtt1',
 'webvtt-cue-settings-unsupported-receiver': 'webvtt1'}
normative_task_topics.update({'matroska-accessibility-track-flags': 'matroska-specification-notes',
 'matroska-codec-delay-versus-added-silence': 'matroska-specification-notes',
 'matroska-default-flags-player-preferences': 'matroska-specification-notes',
 'matroska-discard-padding-trim-context': 'matroska-specification-notes',
 'matroska-forced-flag-versus-caption-content': 'matroska-specification-notes',
 'matroska-laced-block-versus-frame': 'matroska-specification-notes',
 'matroska-negative-timestamp-decode-context': 'matroska-specification-notes',
 'matroska-reader-version-versus-document': 'matroska-specification-notes',
 'matroska-seek-preroll-versus-timeline-offset': 'matroska-specification-notes',
 'matroska-segment-title-versus-filename': 'matroska-specification-notes',
 'matroska-stream-copy-element-retention': 'matroska-specification-notes',
 'matroska-timestamp-scale-clock-inspection': 'matroska-specification-notes',
 'matroska-track-language-precedence': 'matroska-specification-notes',
 'matroska-virtual-track-subresource-support': 'matroska-specification-notes'})
for b in r:
 if b.get('batch')!='expansion-stage-a-2026-10-08':continue
 slug=b['path'].split('/')[-2]
 if slug in shotcut_task_topics:
  exact=[s for s in sources if s['provider']=='Shotcut official user guide' and s['topicKey']==shotcut_task_topics[slug]]
  assert len(exact)==1,('Missing Shotcut research lead',b['path'])
  b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'association':'CURATED_NATIVE_TASK_LEAD_NOT_FACTUAL_APPROVAL'} for s in exact]
  linked+=1
  continue
 if slug in normative_task_topics:
  exact=[s for s in sources if s['topicKey']==normative_task_topics[slug]]
  assert len(exact)==1,('Missing normative research lead',b['path'])
  b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'association':'CURATED_SPECIFICATION_LEAD_NOT_FACTUAL_APPROVAL'} for s in exact]
  linked+=1
  continue
 slug=b['path'].split('/')[-2]
 if slug in microsoft_native_topics:
  exact=[s for s in sources if s['provider']=='Microsoft Clipchamp official support' and s['topicKey']==microsoft_native_topics[slug]]
  assert len(exact)==1,('Ambiguous or missing Microsoft native research lead',b['path'])
  b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'association':'CURATED_RESEARCH_LEAD_NOT_FACTUAL_APPROVAL'} for s in exact]
  linked+=1
  continue
 if slug in playback_encoder_topics:
  provider,topic=playback_encoder_topics[slug]
  exact=[s for s in sources if s['provider']==provider and s['topicKey']==topic]
  assert len(exact)==1,('Ambiguous or missing playback/encoder lead',b['path'])
  b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'association':'CURATED_NATIVE_TASK_LEAD_NOT_FACTUAL_APPROVAL'} for s in exact]
  linked+=1
  continue
 if slug in native_retention_topics:
  exact=[s for s in sources if s['topicKey']==native_retention_topics[slug]]
  assert len(exact)==1,('Ambiguous or missing native retention lead',b['path'])
  b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'association':'CURATED_NATIVE_TASK_LEAD_NOT_FACTUAL_APPROVAL'} for s in exact]
  linked+=1
  continue
 if slug in open_source_topics:
  provider={'blender':'Blender official video editing manual','obs':'OBS official knowledge base','kdenlive':'Kdenlive official manual'}[slug.split('-')[0]]
  exact=[s for s in sources if s['provider']==provider and s['topicKey']==open_source_topics[slug]]
  assert exact,('Missing open-source discovery lead',b['path'])
  b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'association':'CURATED_NATIVE_TASK_LEAD_NOT_FACTUAL_APPROVAL'} for s in exact]
  linked+=1
  continue
 if b['platform']=='youtube':
  identifier=youtube_topics.get(b['path'].split('/')[-2])
  if identifier:
   exact=[s for s in sources if s['sourceURL']=='https://support.google.com/youtube/answer/'+identifier+'?hl=en']
   assert exact,('Missing YouTube discovery lead',b['path'])
   b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'association':'CURATED_NATIVE_TASK_LEAD_NOT_FACTUAL_APPROVAL'} for s in exact]
   linked+=1
  # "YouTube Premiere" is a platform event, not Adobe's editing application.
  continue
 if 'premiere' in b['path']:provider='Adobe Premiere documentation navigation'
 elif 'final-cut' in b['path']:provider='Apple Final Cut guide'
 elif 'audacity' in b['path']:provider='Audacity official manual'
 elif 'ffmpeg' in b['path'] or 'ffprobe' in b['path']:provider='FFmpeg official filters reference'
 else:continue
 native=re.search(r'/(?:premiere|final-cut)-native-([^/]+)/',b['path'])
 if native:
  exact=[s for s in sources if s['provider']==provider and re.sub(r'0$','',s['topicKey'])==native.group(1)]
  assert exact,('Missing native source lead',b['path'])
  b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'association':'EXACT_DISCOVERY_TOPIC_NOT_FACTUAL_APPROVAL'} for s in exact]
  linked+=1
  continue
 w=words(b['path']+' '+b['title']+' '+b['userBenefit'])
 shortlist=sorted(((score(w,s['_words']),s) for s in sources if s['provider']==provider),key=lambda x:x[0],reverse=True)[:3]
 b['primarySourceLeads']=[{'sourceID':s['sourceID'],'url':s['sourceURL'],'topicKey':s['topicKey'],'bodyReviewed':False,'matchIsHypothesis':True,'lexicalSimilarity':round(v,4)} for v,s in shortlist if v>=(0.02 if provider=='FFmpeg official filters reference' else 0.08)]
 if b['primarySourceLeads']:linked+=1
p.write_text(json.dumps(r,indent=2)+'\n');print('Draft/source shortlist associations:',linked)
