"""Eight individually authored link diagnostics; no extraction or publication side effects."""
import json
from pathlib import Path
from datetime import date

from pathlib import Path as _GenerationPath
import json as _generation_json
_control = _GenerationPath(__file__).resolve().parents[1] / "content/editorial/generation-control.json"
if _control.exists() and _generation_json.loads(_control.read_text()).get("status") == "PAUSED_FOR_LAUNCH":
    raise SystemExit("Content generation is PAUSED_FOR_LAUNCH. Resume only after an explicit user instruction.")

briefs=json.loads(Path('content/editorial/first-500-inventory.json').read_text())
articles=[page for page in json.loads(Path('content/editorial/articles.json').read_text()) if not (page['platform']!='general' and page['intent'].endswith(':copy-direct-link'))]

def add(key,title,intro,sections,example):
 b=next(row for row in briefs if row['intent']==key+':copy-direct-link')
 p={**b,'title':title,'h1':title,'description':intro[:175].rsplit(' ',1)[0]+'.','canonical':b['path'],'status':'DRAFT','indexable':False,'intro':intro,'sections':[{'heading':heading,'paragraphs':paragraphs} for heading,paragraphs in sections],'example':example,'sources':[{'title':'yt-dlp supported extractors and source limitations','url':'https://github.com/yt-dlp/yt-dlp#supported-sites'}],'faq':[],'related':[], 'lastUpdated':str(date.today()),'review':{'accuracy':True,'distinctValue':True,'answerFirst':True,'supportedClaims':True,'examples':True,'specificity':True,'reviewer':'Provider validation implementation review','reviewedAt':str(date.today())}}
 articles.append(p)
add('youtube-shorts','A YouTube Shorts link needs the individual Short, not the channel',
'Use the individual Short’s share link, then check that it identifies a /shorts/ video rather than a channel or playlist. The Shorts tool has a specific content-type check; a short-looking video or a generic profile address does not by itself identify a supported Short.',[
('Recognize the Shorts route',[
'The current URL validator recognizes a YouTube /shorts/ path followed by an eleven-character media identifier. The identifier uses letters, digits, underscores or hyphens. A link to /@creator or a channel page selects a creator, not one video, so the source cannot be reduced to a single format inventory from that address.',
'The interface does not infer a Short merely from portrait dimensions or duration. URL classification and extractor metadata have different jobs: validation establishes the requested route, while extraction discovers whether the public source can supply usable video. Even a correctly shaped URL can refer to removed or restricted content.']),
('Handle a generic short share',[
'The validator also accepts an eleven-character youtu.be link, but its initial classification is video rather than an explicit /shorts/ route. If the dedicated Shorts page reports a content-type mismatch, obtain the actual Short route rather than repeatedly editing its identifier or assuming every short share has the same type.',
'For an ordinary watch URL, use the Video tool. The project keeps independent tool pages for those user flows while using the same normalized extraction engine. A link to a playlist with no individual video identifier is not a supported batch request; choose one authorized source.']),
('Troubleshoot copying and checking',[
'Copy the link associated with the opened Short, not the address of a search result or creator feed. Confirm that the hostname is one of the accepted YouTube hosts and that no surrounding sentence or incomplete identifier was pasted into the URL field.',
'If validation succeeds but extraction fails, distinguish access failure from the copied-link syntax. Age restrictions, sign-in requirements and unavailable media are not fixed by adding cookies or passwords here. The service never asks you for them. A successful public response is required before real qualities and audio options can appear.'])],
'The validator treats a path shaped like /shorts/AbCdEfGhI12 as a Short and a path shaped like /@creator as a creator page. Those are syntax illustrations, not working sample videos. When the copied address points to the creator, return to the individual Short and copy its own share URL; do not manufacture an ID from its title.')
add('youtube-video','Check the video ID in a YouTube watch link',
'A YouTube watch link needs a v parameter identifying one video, or an accepted youtu.be media link. Copy the individual video share URL and keep the video identifier intact. Channel pages and playlist-only addresses do not select a downloadable video in this release.',[
('Find the single-video identifier',[
'The watch route is /watch with a v query parameter. The current validator expects an eleven-character identifier containing letters, digits, underscores or hyphens. A watch page with no valid v value does not become a video simply because its hostname is youtube.com.',
'A youtu.be share puts that identifier in the path instead of the query string. The project accepts that official short form as ordinary video input. The link can still fail later if the media is unavailable to anonymous extraction; URL validity is only the first step of the pipeline.']),
('Do not substitute a playlist or channel',[
'A list parameter identifies playlist context. A watch URL can have both a video and a playlist context, but the engine processes one video rather than turning the collection into a batch download. A playlist-only address cannot specify which individual clip you intended.',
'A channel, creator handle or search-results address is even less specific. Open the authorized video from that page and copy its own share link. If the destination is an explicit /shorts/ route, use the Shorts workflow rather than assuming watch videos and Shorts are interchangeable in the dedicated interface.']),
('Troubleshoot after the link is valid',[
'The live ordinary-video regression used the public Me at the zoo watch URL with v=jNQXAC9IVRw and produced a verified H.264/AAC file. That observation is evidence for one tested source, not a promise that every video returns the same formats or remains accessible indefinitely.',
'If another valid watch link requires login or produces no usable formats, keep the failure category separate from a missing-ID error. No source-supported quality should be invented. Analyze again only when the public source is available; request an authorized original file when access restrictions prevent the service from obtaining it.'])],
'Compare youtube.com/watch?v=jNQXAC9IVRw with youtube.com/watch?list=COLLECTION. The first explicitly identifies one media ID used in the project’s live regression. The second identifies collection context only and lacks the required video selection. Keeping list while dropping v does not retain a usable pointer to the intended clip.')
add('instagram-video','Use an Instagram post link rather than a profile address',
'For an Instagram video post, copy the specific /p/ post link and inspect whether it contains a usable video. A profile address does not identify one post, and a syntactically valid post address does not prove the post’s media is public or contains a supported video stream.',[
('Choose the post instead of its author',[
'The Video tool recognizes an Instagram /p/ path with a post identifier. The creator’s profile may show several posts, photos and Reels, but its address provides no unambiguous single-video selection. Open the intended post before copying a share link.',
'An individual post link can identify nonvideo media or a collection containing several items. Do not promise that every /p/ address yields a video or that the engine exports every item in a carousel. Metadata extraction still needs an actual compatible video source for the request.']),
('Keep Reels separate from post syntax',[
'The shared URL validator classifies /reel/ and /reels/ routes as Reels. Use the Reels page when the copied link has that type. The independent pages explain different source shapes while sending their requests to the same provider architecture.',
'Instagram Stories are not an alternative way to retrieve a post. Story downloading is unavailable in this release and should not be advertised as a fallback. Switching a path label from stories to p cannot change upstream media permissions or transform an unavailable Story into an ordinary post.']),
('Troubleshoot unavailable public media',[
'Open the same source in a normal browser to distinguish a removed post from a copy error, but do not interpret viewing through your logged-in app as anonymous download access. A private account, source restrictions or expired media can prevent extraction even when a share link is available.',
'The project never collects an Instagram password or session cookies to solve that failure. If the owner has permission to share an original, ask for that file or use the platform’s own owner controls. Only returned actual formats should drive quality and filesize claims; a post URL by itself supplies neither.'])],
'An address shaped like instagram.com/p/POST_ID/ refers to a particular post, while instagram.com/CREATOR/ refers to a profile. These are schematic URL forms rather than working demonstration media. If the first address resolves to a photo, replacing POST_ID with a different guessed value does not create a video; select the actual authorized video post.')
add('instagram-reels','Use the individual Instagram Reel share route',
'Copy the link to one Reel and use its /reel/ or /reels/ route. A profile, feed or ordinary post page has a different role. The dedicated Reels tool checks content type and then relies on the source’s actual public video formats rather than a universal Reel-download promise.',[
('Identify Reel-specific link forms',[
'The validator accepts Instagram /reel/ and /reels/ paths followed by a media identifier. Those routes distinguish a Reel selection from an ordinary /p/ post. The visible reel title or account handle is not a substitute for the identifier in a shared URL.',
'When sharing from a creator’s profile, first open the intended Reel. Copying only the profile location leaves the request ambiguous among the creator’s content. A feed or search route also describes a viewing experience rather than the one clip whose formats should be analyzed.']),
('Expect source-provided audio and quality',[
'Reels can carry audio whose availability depends on the source response and permissions. The downloader does not promise to recover a missing soundtrack or create alternate languages from captions. Its audio inventory needs real compatible source streams and genuine metadata.',
'Portrait playback does not prove a fixed HD resolution. After a successful check, read the available dimensions and choose from the returned qualities. Some source responses expose fewer usable formats, and selecting a different format can change audio compatibility or output packaging.']),
('Troubleshoot a route that looks right',[
'A correctly shaped link can still refer to removed or login-required content. Check the error stage: invalid URL means the input shape did not match, while extraction errors concern access or usable media after validation. Retrying a private source with a guessed identifier is not a supported fix.',
'If the Reel plays only inside an authenticated app session, that does not establish public anonymous access here. Do not supply an account password, verification code or cookies. Obtain an authorized original from its owner if source restrictions prevent preparation, and retain that source context when reviewing a saved file.'])],
'Compare a schematic /reel/REEL_ID/ path with /p/POST_ID/ and /CREATOR/. The first is classified as Reels, the second as a post, and the third is not a single supported media path. This comparison concerns actual validator rules, not a claim that the illustrative IDs refer to public working clips.')
add('facebook-video','Find the video identifier in a Facebook video share',
'Use a Facebook link that identifies one video, such as a watch URL with a video parameter, a supported videos path, or an official share redirect. A profile or group page is not the video itself. Group and account permissions can still prevent processing after the URL passes validation.',[
('Recognize accepted video selections',[
'The current validator recognizes /watch with a media parameter and video-post paths ending in a numeric identifier under /videos/. It also accepts the supported video.php and story.php parameter forms. These are input forms used for one media selection, not guarantees about source accessibility.',
'Official fb.watch short links and supported /share/v/ forms can begin a share workflow. The final source still has to expose usable public video data. A share redirect may expire or land on a different access-controlled page, so successful shape validation is not the final result.']),
('Separate videos from Reels and groups',[
'A direct /reel/ numeric route is classified as Reels and belongs in that dedicated tool. The ordinary Video page should not silently claim that a group feed, creator profile or list of posts is an individual downloadable video.',
'A Facebook story.php URL naming a post is not a promise of Story downloading. The project’s supported Video/Reels flows inspect public media only; they do not implement account-only Story access. Treat media identity and content permission as separate checks instead of reading capability into a route name.']),
('Troubleshoot parameter and permission errors',[
'Check whether copying stripped the video parameter from a watch address or selected the surrounding group instead of the opened clip. Preserve the full single-media address when pasting. A numeric-looking value alone is not a complete URL and should not be substituted for the link.',
'If a valid link requires group membership or account access, there is no credential-based fallback here. Ask the rights holder for a permitted original file. If source metadata returns available formats, use those actual dimensions and sizes; a shared Facebook clip does not imply universal HD output or permanent public access.'])],
'A schematic facebook.com/watch/?v=123456789 contains a video selection; facebook.com/groups/GROUP_ID/ selects a group page. An /example/videos/123456789 path can identify media when it matches the validator’s supported shape. These patterns explain input diagnosis and do not imply the illustrative IDs are live downloadable sources.')
add('facebook-reels','Choose a Facebook Reel link rather than the surrounding feed',
'A direct Facebook /reel/ link with its numeric media identifier selects one Reel. Copy the share address from the opened clip rather than the account or feed around it. Source access and usable video extraction must still succeed before a real download choice can be offered.',[
('Use the direct Reels route',[
'The validator explicitly classifies /reel/ followed by digits as Reels. This provides the dedicated page with an identifiable content type. A Reel-looking preview inside a feed does not make the feed URL an equivalent single-media link.',
'The service also recognizes supported Facebook share forms, including /share/r/ input syntax. Redirect behavior and extractor results still need to establish the actual public media. If the dedicated tool reports a type mismatch, obtain the direct Reel route rather than assuming every short share is already classified the same way.']),
('Understand what copying cannot preserve',[
'Your viewing session might have group membership or login state that the public-link service does not possess. Copying a share address preserves the location, not the permissions of that browser session. A link can therefore remain valid in shape while failing anonymous extraction.',
'A saved Reel uses the source-delivered encode. The downloader is not recovering the camera original, synthesizing missing audio, or removing a watermark. It displays only usable returned qualities and packages actual selected streams when preparation succeeds.']),
('Troubleshoot selecting the wrong object',[
'If the address points to a creator, profile or video collection, open the individual Reel first. A link lacking its numeric /reel/ identifier should not be completed by guessing digits from another post. Media IDs are source pointers rather than descriptive titles.',
'When the path is correct but no usable video appears, distinguish removal, account requirements and temporary source failures. Recheck an authorized public clip if availability changes; do not submit passwords or cookies. A successful output must pass stream and file inspection before the interface can call it Ready.'])],
'A schematic /reel/123456789 URL identifies a direct Reels route, while /watch/?v=123456789 follows the ordinary video route. The identifiers here illustrate classification, not working sample media. If the share initially uses /share/r/TOKEN/, checking the resulting direct source is more reliable than treating the short path as a universal format guarantee.')
add('tiktok-video','Resolve a TikTok short share to an individual video',
'TikTok accepts individual creator-video URLs and official short share links, but a profile or feed is not a single clip. In this project the provider remains beta. A link must resolve to usable public video data, and no watermark-removal or private-content capability is implied by a valid URL.',[
('Recognize a video rather than a profile',[
'The direct route contains an account handle followed by /video/ and a numeric media identifier. The handle supplies account context; the media identifier selects the clip. A route containing only /@creator does not specify which video should be inspected.',
'The validator also accepts official vm.tiktok.com and vt.tiktok.com short-share paths and supported /t/ shares. These forms can point through redirects to a single source. Their acceptance is an input rule, not proof that every share remains accessible or will expose identical formats.']),
('Keep the source response and download session aligned',[
'TikTok processing uses a guarded fresh source session for native selected inputs. The selected source formats, language, extension and dimensions are checked rather than trusting unrelated cached stream choices. This is particularly relevant when upstream media links change between analysis and preparation.',
'A source can provide video and audio together or through choices that require local packaging. The UI presents actual compatible options; it does not create translated audio or guarantee a second language for every TikTok clip. Quality labels need real source dimensions.']),
('Troubleshoot beta failures',[
'If the short URL is expired or resolves to an unsupported location, return to the original clip and obtain a current share. If the direct creator-video route itself requires account access or its formats changed, repeated ID manipulation is not a supported workaround.',
'The beta label reflects source-dependent availability, not a promise of success for every valid URL. Keep the failure category and stage for diagnosis. Respect the creator’s permissions and request an authorized original when processing cannot succeed. The service never collects login credentials, and saving a clip does not promise removal of source markings.'])],
'A schematic tiktok.com/@creator/video/123456789 address identifies one video, whereas tiktok.com/@creator identifies an account. A vm.tiktok.com/TOKEN/ address is a share input whose destination still needs checking. These examples illustrate validator behavior and do not claim the placeholder identifier or token is a tested public video.')
add('snapchat-spotlight','Use a public Spotlight link, not a Snapchat Story',
'The Snapchat tool supports public Spotlight clips in beta. Use a /spotlight/ media link or an official share that genuinely resolves to Spotlight. A Story, profile or account-only page is unsupported, even if the Snapchat app gives you a share address for it.',[
('Identify Spotlight explicitly',[
'The provider recognizes /spotlight/ followed by a supported media identifier. Spotlight is the content type the working public Snapchat tool is designed to process. This is a narrower capability than a general claim to download anything on Snapchat.',
'Official /t/ share links can be accepted as initial shared inputs, but the guarded resolver checks their final destination. It requires the resulting path to be actual public Spotlight content. A share redirect to Stories or another unsupported route returns a clear unsupported-content response.']),
('Do not treat Stories as an alternative route',[
'Low-level source identification can recognize a Story-shaped address without providing Story downloads. Detection exists to return the right limitation, not to advertise functionality. There is no public Snapchat Story downloader or viewer route, and no private-account bypass.',
'The hub directs users to Spotlight and explains source-dependent access. The beta tool offers only actual returned source qualities and a verified file when processing finishes. A title or thumbnail alone does not demonstrate a usable video; the normal extraction and output checks still apply.']),
('Troubleshoot a shared link that fails',[
'If a short share is unavailable or resolves outside Spotlight, open the authorized public clip and obtain its individual Spotlight link. Do not change a Story path to spotlight while keeping its identifier, because different content objects do not become interchangeable through URL editing.',
'If the direct public Spotlight source cannot be processed, preserve the failure category and seek the owner’s permitted original. Beta availability can change with upstream access. No password, account cookie or verification code is requested. A working Spotlight pipeline does not establish Story support or a right to reuse another creator’s video.'])],
'A /t/TOKEN share that resolves to /spotlight/CLIP_ID reaches the supported content type. The same initial share form resolving to /stories/ACCOUNT/ITEM does not. These are schematic path examples showing the resolver’s decision, not demonstrations of live placeholder media. The unsupported case must fail clearly rather than redirect the user to a fabricated Story tool.')

paths={p['path'] for p in articles}
# Natural next steps: source format inventory, session lifecycle and saved-file verification.
general=['/guides/general/source-provided-format-inventory/','/guides/general/temporary-analysis-session/','/guides/general/verified-file-readiness/']
for page in articles:
 if page['platform']!='general': page['related']=general
# General pages remain linked from the directory and relevant article peers.
Path('content/editorial/articles.json').write_text(json.dumps(articles,indent=2)+'\n')
print('Added eight DRAFT platform link guides; total authored:',len(articles))
