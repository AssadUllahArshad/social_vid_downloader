"""Intent consolidation decisions for the original queue; does not publish."""
import json
from pathlib import Path
from datetime import date
store=Path('content/editorial/first-500-inventory.json')
briefs=json.loads(store.read_text());articles=json.loads(Path('content/editorial/articles.json').read_text())
selected='android-downloads-folder windows-downloads-folder mac-downloads-folder chromebook-local-files icloud-drive-vs-local-storage windows-cloud-vs-local-file copy-video-to-usb storage-space-check chrome-download-history firefox-download-history edge-download-history safari-download-history in-app-browser-vs-external-browser safe-browser-download-warning downloaded-file-has-no-sound video-will-not-open zero-byte-download incomplete-video-file video-freezes-during-playback audio-out-of-sync downloaded-file-is-html multiple-audio-track-player av1-video-codec vp9-video-codec video-bitrate audio-bitrate frame-rate-vs-resolution muxing-vs-transcoding audio-sample-rate drm-access-boundary source-audio-language-selection descriptive-audio dubbed-source-audio does-4k-upscale-improve-detail mp4-vs-webm mp4-vs-mkv h264-vs-hevc aac-vs-opus permissioned-video-archive organize-language-track-copies source-changes-after-analysis'.split()
provider_selected={'youtube-video','instagram-video','facebook-video','tiktok-video','snapchat-spotlight'}
old={p['path'] for p in articles if p['status']=='PUBLISHED'}
def g(slug):return '/guides/general/'+slug+'/'
# Canonical ownership decisions: these topics require the same answer, not a new URL.
general_merge={
'iphone-downloads-folder':'iphone-files-vs-photos','ipad-downloads-folder':'iphone-files-vs-photos','ipad-files-vs-photos':'iphone-files-vs-photos','android-downloads-vs-gallery':'android-downloads-folder','mac-cloud-vs-local-file':'icloud-drive-vs-local-storage','external-drive-playback':'copy-video-to-usb',
'download-prompt-vs-inline-video':'browser-preview-vs-save','browser-download-location':'chrome-download-history','private-browsing-file-storage':'browser-preview-vs-save',
'unsupported-video-codec':'video-will-not-open','unsupported-audio-codec':'downloaded-file-has-no-sound','browser-cannot-preview-mkv':'mp4-vs-mkv','video-opens-as-text':'downloaded-file-is-html','wrong-file-extension':'video-container-vs-codec','permissions-vs-storage-failure':'storage-space-check',
'mp4-container':'mp4-vs-mkv','webm-container':'mp4-vs-webm','mkv-container':'mp4-vs-mkv','h264-video-codec':'h264-vs-hevc','hevc-video-codec':'h264-vs-hevc','aac-audio-codec':'aac-vs-opus','opus-audio-codec':'aac-vs-opus','vorbis-audio-codec':'mp4-vs-webm','variable-bitrate':'video-bitrate','resolution-vs-bitrate':'video-bitrate',
'remuxing-vs-reencoding':'muxing-vs-transcoding','lossless-stream-copy':'muxing-vs-transcoding','progressive-vs-separate-streams':'muxing-vs-transcoding','pixel-dimensions':'frame-rate-vs-resolution','portrait-aspect-ratio':'source-provided-format-inventory','landscape-aspect-ratio':'source-provided-format-inventory','frame-rate':'frame-rate-vs-resolution','audio-channel-count':'dual-audio-vs-stereo','audio-track-vs-channel':'dual-audio-vs-stereo','language-tag':'missing-source-language','default-audio-disposition':'original-vs-default-audio',
'single-vs-dual-audio':'source-audio-language-selection','mkv-for-mixed-audio-codecs':'mp4-vs-mkv','verify-audio-stream-count':'verified-file-readiness',
'does-public-mean-permission':'permissioned-video-archive','does-renaming-extension-convert-video':'video-container-vs-codec','does-preview-save-a-file':'browser-preview-vs-save','does-browser-language-create-audio':'missing-source-language',
'resolution-vs-file-size':'video-bitrate','retain-source-attribution':'permissioned-video-archive','keep-original-master':'permissioned-video-archive','document-authorized-review':'permissioned-video-archive'}
# Platform variants retain their tool context but delegate common problems to one answer owner.
scoped_merge={
'save-on-iphone':'iphone-files-vs-photos','save-on-ipad':'iphone-files-vs-photos','save-on-android':'android-downloads-folder','save-on-windows':'windows-downloads-folder','save-on-mac':'mac-downloads-folder','save-on-chromebook':'chromebook-local-files',
'safari-link-workflow':'safari-download-history','chrome-link-workflow':'chrome-download-history','firefox-link-workflow':'firefox-download-history','edge-link-workflow':'edge-download-history',
'check-link-ownership':'permissioned-video-archive','choose-quality':'source-provided-format-inventory','verify-saved-file':'verified-file-readiness',
'no-formats':'source-provided-format-inventory','timeout':'verified-file-readiness','size-limit':'storage-space-check','duration-limit':'verified-file-readiness','expired-analysis':'temporary-analysis-session','expired-file':'local-file-vs-expired-link','missing-preview':'browser-preview-vs-save','empty-source':'source-provided-format-inventory','source-changed':'source-changes-after-analysis',
'download-permission':'permissioned-video-archive','original-file':'permissioned-video-archive','portrait-dimensions':'source-provided-format-inventory','highest-available':'source-provided-format-inventory','mp4-output':'mp4-vs-mkv','webm-output':'mp4-vs-webm','mkv-output':'mp4-vs-mkv','file-size-estimate':'video-bitrate','preview-vs-download':'browser-preview-vs-save','owner-backup':'permissioned-video-archive','permissioned-review':'permissioned-video-archive','source-evidence':'permissioned-video-archive'}
for b in briefs:
 slug=b['path'].split('/')[-2]
 key,topic=b['intent'].split(':',1)
 approved=b['path'] in old or (b['platform']=='general' and slug in selected) or (key in provider_selected and topic=='temporary-provider-failure')
 if approved:
  classification='APPROVED_TO_WRITE';destination=b['path']
  rationale='Owns a distinct diagnostic or decision outcome: '+b['userBenefit']+' A dedicated worked example and source evidence are required; keyword wording alone is not approval.'
  b['status']='PUBLISHED' if b['path'] in old else 'DRAFT';b['indexable']=b['path'] in old
  if b['path'] not in old: b['inventoryApproval']={'approved':True,'path':b['path'],'intent':b['intent'],'rationale':rationale,'reviewer':'First-batch intent consolidation review','reviewedAt':str(date.today())}
 else:
  classification='MERGE_WITH_EXISTING'
  if b['platform']=='general':
   assert slug in general_merge,slug
   destination=g(general_merge[slug]);reason='This is a narrower facet or synonymous question of the canonical guide; its specific check will be included in that answer rather than fragmenting it.'
  elif topic in scoped_merge:
   destination=g(scoped_merge[topic]);reason='Changing the source platform does not change this file/browser/format solution. Retain the platform link context in the tool guide and use this shared answer for the actual problem.'
  elif topic in {'recognize-link-types','profile-vs-clip','collection-vs-single','short-link-resolution','invalid-url','wrong-content-type'}:
   destination=b['path'].rsplit('/',1)[0] if False else '/guides/'+b['platform']+'/'+key+'-copy-direct-link/'
   reason='The already published content-type link guide answers these source-identification cases in one workflow, including accepted forms, wrong objects and invalid identifiers.'
  elif topic in {'access-restrictions','deleted-source','login-required','not-found','temporary-provider-failure','private-content'}:
   owner={'youtube':'youtube-video','instagram':'instagram-video','facebook':'facebook-video','tiktok':'tiktok-video','snapchat':'snapchat-spotlight'}[b['platform']]
   destination='/guides/'+b['platform']+'/'+owner+'-temporary-provider-failure/'
   reason='One provider-specific failure decision tree covers its supported content forms, source removal, public-access limits and temporary failures. A second page for the same diagnosis would divide the answer.'
  elif topic in {'watermark','app-offline-vs-file','platform-save-vs-export'}:
   destination=b['targetDownloader'];reason='The existing product page already states source preservation, source-dependent access and permission limits; the export-versus-preview distinction is also covered in the shared file-saving guide. No separate capability is being added.'
  else: raise AssertionError((slug,topic))
  rationale=reason+' Original benefit reviewed: '+b['userBenefit']
  b['status']='ARCHIVED';b['indexable']=False;b['inventoryApproval']=None
 b['disposition']={'classification':classification,'destination':destination,'reason':rationale,'reviewedAt':str(date.today()),'targetUser':('A viewer trying to resolve '+b['title'].lower()+'.'),'primaryQuestion':b['title'],'internalLinkDestination':destination,'outcome':'PUBLISHED' if b['path'] in old else 'WRITE_REQUIRED' if approved else 'CONSOLIDATED'}
store.write_text(json.dumps(briefs,indent=2)+'\n')
from collections import Counter
print(Counter(b['disposition']['classification'] for b in briefs))
print('New approved:',sum(b['disposition']['outcome']=='WRITE_REQUIRED' for b in briefs))
