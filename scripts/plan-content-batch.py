"""Create the nonpublic first-batch intent inventory; never publish content."""
import json
from pathlib import Path

# These are briefs, not generated prose or automatically approved SEO pages.

from pathlib import Path as _GenerationPath
import json as _generation_json
_control = _GenerationPath(__file__).resolve().parents[1] / "content/editorial/generation-control.json"
if _control.exists() and _generation_json.loads(_control.read_text()).get("status") == "PAUSED_FOR_LAUNCH":
    raise SystemExit("Content generation is PAUSED_FOR_LAUNCH. Resume only after an explicit user instruction.")

contexts = [
    ('youtube', 'youtube-shorts', 'YouTube Shorts', '/youtube-shorts-downloader/', '/youtube/'),
    ('youtube', 'youtube-video', 'YouTube video', '/youtube-video-downloader/', '/youtube/'),
    ('instagram', 'instagram-video', 'Instagram video post', '/instagram-video-downloader/', '/instagram/'),
    ('instagram', 'instagram-reels', 'Instagram Reel', '/instagram-reels-downloader/', '/instagram/'),
    ('facebook', 'facebook-video', 'Facebook video', '/facebook-video-downloader/', '/facebook/'),
    ('facebook', 'facebook-reels', 'Facebook Reel', '/facebook-reels-downloader/', '/facebook/'),
    ('tiktok', 'tiktok-video', 'TikTok video', '/tiktok-video-downloader/', '/tiktok/'),
    ('snapchat', 'snapchat-spotlight', 'Snapchat Spotlight clip', '/snapchat-spotlight-downloader/', '/snapchat-downloader/'),
]
# Scope-specific briefs require their own evidence and examples before approval.
briefs = [
('device','save-on-iphone','Save an authorized {name} on iPhone','Complete the source-link-to-Files workflow on iPhone for this content type.'),
('device','save-on-ipad','Save an authorized {name} on iPad','Use the iPad browser and file workflow without treating an app cache as an export.'),
('device','save-on-android','Save an authorized {name} on Android','Locate the actual Android file after processing a link for this content type.'),
('device','save-on-windows','Save an authorized {name} on Windows','Choose the right source link and verify the saved desktop file.'),
('device','save-on-mac','Save an authorized {name} on Mac','Move from the source share link to a verified local Mac file.'),
('device','save-on-chromebook','Save an authorized {name} on Chromebook','Distinguish browser completion from the resulting local Chromebook media file.'),
('browser','safari-link-workflow','Use Safari to save an authorized {name}','Explain Safari-specific source sharing and file-save decisions for this content type.'),
('browser','chrome-link-workflow','Use Chrome to save an authorized {name}','Resolve this source link and follow the Chrome download workflow.'),
('browser','firefox-link-workflow','Use Firefox to save an authorized {name}','Describe the source link and Firefox save workflow with a tested example.'),
('browser','edge-link-workflow','Use Edge to save an authorized {name}','Choose and verify the actual media file in the Edge workflow.'),
('how-to','copy-direct-link','Copy a direct link to one {name}','Identify which share-link form refers to one clip instead of a feed or profile.'),
('how-to','recognize-link-types','Recognize supported {name} URL forms','Separate accepted source URL forms from unrelated pages and unsupported collections.'),
('how-to','check-link-ownership','Check permission before saving a {name}','Choose an owner-approved file workflow instead of assuming visibility grants a license.'),
('how-to','choose-quality','Choose a source quality for a {name}','Use actual extracted dimensions and size evidence instead of fixed quality promises.'),
('how-to','verify-saved-file','Verify the saved {name} file','Check duration and playback against the selected public source.'),
('platform-help','profile-vs-clip','Why a profile link cannot select a {name}','Find the individual media link when a shared page points to a profile.'),
('platform-help','collection-vs-single','Why a collection link cannot select one {name}','Extract a single authorized clip link without implying batch collection downloads.'),
('platform-help','access-restrictions','Access restrictions on public {name} links','Diagnose when visible source content still cannot be fetched without account access.'),
('platform-help','deleted-source','What happens when a {name} is deleted','Recognize unavailable source content and choose a legitimate original-file alternative.'),
('platform-help','short-link-resolution','Resolve a short share link for a {name}','Recognize the final supported content type after an official share redirect.'),
('troubleshooting','invalid-url','Fix an invalid {name} URL','Locate the missing media identifier or wrong URL form instead of repeatedly retrying.'),
('troubleshooting','login-required','Why a {name} link requires login','Explain an access-required failure without collecting credentials or bypassing permissions.'),
('troubleshooting','not-found','Why a {name} link returns not found','Distinguish a bad media identifier from removed or no-longer-public source content.'),
('troubleshooting','no-formats','Why no formats appear for a {name}','Interpret missing usable source formats without inventing a downloadable version.'),
('troubleshooting','temporary-provider-failure','Temporary processing failures for a {name}','Distinguish temporary extractor availability from permanent access restrictions.'),
('troubleshooting','timeout','Why preparation of a {name} times out','Reduce selected source workload within actual limits instead of claiming fake completion.'),
('troubleshooting','size-limit','Why a {name} exceeds the file-size limit','Choose a genuinely available smaller format when a source exceeds the configured budget.'),
('troubleshooting','duration-limit','Why a {name} exceeds the duration limit','Interpret a duration rejection and seek an original authorized file instead of a workaround.'),
('troubleshooting','expired-analysis','Why a {name} analysis session expires','Recheck the source to get valid current format identifiers.'),
('troubleshooting','expired-file','Why a saved-file link for a {name} expires','Separate temporary service links from a durable file already saved on the device.'),
('troubleshooting','missing-preview','Why a {name} preview is unavailable','Distinguish thumbnail or browser playback limits from verified output availability.'),
('troubleshooting','wrong-content-type','Why a {name} link opens the wrong tool','Match the resolved media route to the actual content type.'),
('troubleshooting','empty-source','Why a {name} yields no video streams','Recognize a source that contains no supported video instead of fabricating a file.'),
('troubleshooting','source-changed','Why a {name} changes between analysis and download','Refresh source inventory after expired or changed upstream formats.'),
('faq','private-content','Can private {name} content be downloaded here?','Give a clear source-specific access boundary and a legitimate owner-file alternative.'),
('faq','download-permission','Does a public {name} link grant download permission?','Separate access to a clip from the permission needed to retain or reuse it.'),
('faq','watermark','Does saving a {name} remove its watermark?','Explain preservation of source video rather than promising watermark removal.'),
('faq','original-file','Is a downloaded {name} the original upload?','Distinguish delivered platform encodes from an owner’s original source file.'),
('formats','portrait-dimensions','Read portrait dimensions for a {name}','Interpret width and height without treating a portrait short side as a universal quality label.'),
('formats','highest-available','Find the highest available quality for a {name}','Use actual returned source formats and explain absent higher resolutions.'),
('formats','mp4-output','Understand MP4 output for a {name}','Separate the output container from codec compatibility and quality.'),
('formats','webm-output','Understand WebM output for a {name}','Explain why codec combinations may produce WebM and what playback support means.'),
('formats','mkv-output','Understand MKV fallback for a {name}','Explain a compatible fallback file without claiming universal browser playback.'),
('formats','file-size-estimate','Read file-size estimates for a {name}','Distinguish measured output bytes from estimated source transfer sizes.'),
('comparison','app-offline-vs-file','App offline access versus a local {name} file','Separate an official offline experience from an exportable local media file.'),
('comparison','preview-vs-download','Previewing versus downloading a {name}','Explain why a playing preview does not mean a permanent file has been saved.'),
('comparison','platform-save-vs-export','Saving a {name} in its app versus exporting a file','Distinguish an in-app bookmark from media bytes stored on a device.'),
('use-case','owner-backup','Back up an authorized {name}','Plan an owner-file backup without substituting a platform encode for the original master.'),
('use-case','permissioned-review','Save a {name} for an authorized review','Preserve source context and permission while preparing a review copy.'),
('use-case','source-evidence','Keep source context with a saved {name}','Record the source link and ownership context separately from temporary download tokens.'),
]
assert len(briefs) == 50
rows=[]
for priority,(platform,key,name,tool,hub) in enumerate(contexts,1):
 for family,slug,title,benefit in briefs:
  rows.append({'path':f'/guides/{platform}/{key}-{slug}/','platform':platform,'family':family,'title':title.format(name=name),'h1':title.format(name=name),'primaryKeyword':title.format(name=name).lower(),'secondaryKeywords':[f'{name.lower()} {family}',f'{name.lower()} link help'],'intent':f'{key}:{slug}','userBenefit':benefit,'priority':priority,'targetDownloader':tool,'hub':hub,'status':'PLANNED','indexable':False,'inventoryApproval':None,'reviewRequirements':['Distinct value beyond the cross-platform guide','Source-specific worked example','Current source/access evidence','Duplicate and intent ownership review']})
# Cross-platform briefs avoid multiplying general file/device problems across platforms.
general = {
'device': 'iphone-downloads-folder|ipad-downloads-folder|android-downloads-folder|windows-downloads-folder|mac-downloads-folder|chromebook-local-files|iphone-files-vs-photos|ipad-files-vs-photos|android-downloads-vs-gallery|icloud-drive-vs-local-storage|windows-cloud-vs-local-file|mac-cloud-vs-local-file|copy-video-to-usb|external-drive-playback|storage-space-check',
'browser': 'chrome-download-history|firefox-download-history|edge-download-history|safari-download-history|in-app-browser-vs-external-browser|browser-preview-vs-save|download-prompt-vs-inline-video|browser-download-location|safe-browser-download-warning|private-browsing-file-storage',
'troubleshooting': 'downloaded-file-has-no-sound|video-will-not-open|zero-byte-download|incomplete-video-file|video-freezes-during-playback|audio-out-of-sync|unsupported-video-codec|unsupported-audio-codec|browser-cannot-preview-mkv|video-opens-as-text|downloaded-file-is-html|wrong-file-extension|multiple-audio-track-player|local-file-vs-expired-link|permissions-vs-storage-failure',
'formats': 'mp4-container|webm-container|mkv-container|h264-video-codec|hevc-video-codec|av1-video-codec|vp9-video-codec|aac-audio-codec|opus-audio-codec|vorbis-audio-codec|video-bitrate|audio-bitrate|variable-bitrate|resolution-vs-bitrate|frame-rate-vs-resolution',
'glossary': 'video-container-vs-codec|muxing-vs-transcoding|remuxing-vs-reencoding|lossless-stream-copy|progressive-vs-separate-streams|pixel-dimensions|portrait-aspect-ratio|landscape-aspect-ratio|frame-rate|audio-sample-rate|audio-channel-count|audio-track-vs-channel|language-tag|default-audio-disposition|drm-access-boundary',
'audio': 'source-audio-language-selection|single-vs-dual-audio|dual-audio-vs-stereo|missing-source-language|original-vs-default-audio|descriptive-audio|dubbed-source-audio|mkv-for-mixed-audio-codecs|verify-audio-stream-count|subtitle-language-vs-audio-language',
'faq': 'does-public-mean-permission|does-4k-upscale-improve-detail|does-renaming-extension-convert-video|does-preview-save-a-file|does-browser-language-create-audio',
'comparison': 'mp4-vs-webm|mp4-vs-mkv|h264-vs-hevc|aac-vs-opus|resolution-vs-file-size',
'use-case': 'permissioned-video-archive|retain-source-attribution|keep-original-master|document-authorized-review|organize-language-track-copies',
'platform-help': 'source-provided-format-inventory|temporary-analysis-session|opaque-format-identifiers|verified-file-readiness|source-changes-after-analysis',
}
for family,topics in general.items():
 for topic in topics.split('|'):
  name=topic.replace('-',' ')
  rows.append({'path':f'/guides/general/{topic}/','platform':'general','family':family,'title':name[0].upper()+name[1:],'h1':name[0].upper()+name[1:],'primaryKeyword':name,'secondaryKeywords':[name+' video help'],'intent':'general:'+topic,'userBenefit':f'Explain {name} with a concrete file or workflow example and a verification step that resolves this specific video problem.','priority':9,'targetDownloader':'/youtube-video-downloader/','hub':'/youtube/','status':'PLANNED','indexable':False,'inventoryApproval':None,'reviewRequirements':['Concrete diagnostic or educational outcome','Verified example','Ownership of cross-platform intent','Duplicate and claim review']})
assert len(rows)==500, len(rows)
Path('content/editorial/first-500-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
lines=['# First 500 intent briefs','', 'These are nonpublic PLANNED briefs. A distinct-value sentence is not proof of editorial approval. Context variants must justify separate publication or be consolidated into the general guide. No inferred search-volume figures are recorded.','', '| URL | Platform | Family | Primary keyword | Secondary keywords | Intent | User benefit | Priority | Target downloader | Status |','|---|---|---|---|---|---|---|---|---|---|']
for r in rows:
 lines.append('| '+' | '.join(str(r[k]) if k!='secondaryKeywords' else ', '.join(r[k]) for k in ['path','platform','family','primaryKeyword','secondaryKeywords','intent','userBenefit','priority','targetDownloader','status'])+' |')
Path('docs/first-500-inventory.md').write_text('\n'.join(lines)+'\n')
