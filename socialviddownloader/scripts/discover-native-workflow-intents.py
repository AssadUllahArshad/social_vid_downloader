"""Bulk native-operation hypotheses from previously saved official indexes.

This produces discovery input, not articles, distinct-intent approvals or pages.
Action topics must describe a media operation, not a navigation/UI/version page.
Exact topic aliases share one proposal. Current answers and all drafts remain
the comparison pool; possible overlaps need recorded ownership before writing.
"""
import json
import re
from collections import Counter
from pathlib import Path


from pathlib import Path as _GenerationPath
import json as _generation_json
_control = _GenerationPath(__file__).resolve().parents[1] / "content/editorial/generation-control.json"
if _control.exists() and _generation_json.loads(_control.read_text()).get("status") == "PAUSED_FOR_LAUNCH":
    raise SystemExit("Content generation is PAUSED_FOR_LAUNCH. Resume only after an explicit user instruction.")

sources = json.loads(Path('content/editorial/stage-a-source-opportunities.json').read_text())
registry = json.loads(Path('content/editorial/first-500-inventory.json').read_text())
seed_path = Path('content/editorial/stage-a-intent-seeds.tsv')
seeds = seed_path.read_text()
existing_slugs = {line.split('|')[2] for line in seeds.splitlines() if line and not line.startswith('#')}
existing_titles = {re.sub(r'[^a-z0-9]', '', row['title'].lower()) for row in registry}
actions = {'add', 'adjust', 'apply', 'archive', 'attach', 'automatically', 'batch',
           'change', 'compare', 'configure', 'consolidate', 'convert', 'copy',
           'create', 'customize', 'delete', 'detect', 'display', 'duplicate',
           'edit', 'enable', 'export', 'extract', 'find', 'fix', 'import',
           'incorporate', 'insert', 'keyframe', 'link', 'locate', 'make',
           'manage', 'modify', 'move', 'mute', 'organize', 'override', 'record',
           'recover', 'reconnect', 'relink', 'remove', 'rename', 'render',
           'replace', 'restore', 'retime', 'save', 'search', 'select', 'send',
           'set', 'share', 'show', 'sort', 'split', 'stabilize', 'sync',
           'synchronize', 'transfer', 'trim', 'use', 'view'}
resources = {'audio', 'caption', 'captions', 'clip', 'clips', 'color', 'composition',
             'compositions', 'effect', 'effects', 'export', 'exports', 'file',
             'files', 'frame', 'frames', 'graphic', 'graphics', 'hdr', 'image',
             'images', 'keyframes', 'library', 'libraries', 'lut', 'luts', 'mask',
             'masks', 'media', 'metadata', 'multicam', 'music', 'project',
             'projects', 'proxies', 'proxy', 'raw', 'recording', 'roles',
             'sequence', 'sequences', 'sound', 'speech', 'subtitle', 'subtitles',
             'text', 'timecode', 'timeline', 'timelines', 'title', 'titles',
             'track', 'tracks', 'transition', 'transitions', 'video', 'voice'}
exclude = re.compile(r'keyboard|shortcut|touch-bar|demo-project|new-content|image-playground|'
                     r'color-palette|gradient|splash-screen|launch|window|preferences|'
                     r'creative-cloud-library|creative-cloud-libraries|adobe-stock|'
                     r'new-project|open-project|delete-project|new-event|column-sets|'
                     r'show-or-hide|display-options|column|filmstrip|browser-view|'
                     r'basic-color|plug-ins-and-extensions|motion-content|'
                     r'final-cut-pro-workflow|work-with-photoshop-and-premiere')

def normalized(topic):
    return re.sub(r'0$', '', topic)

def title_words(topic):
    special = {'hdr': 'HDR', 'xml': 'XML', 'xmp': 'XMP', 'mxf': 'MXF',
               'srt': 'SRT', 'lut': 'LUT', 'luts': 'LUTs', 'ai': 'AI',
               'h264': 'H.264', 'h265': 'H.265', 'iphone': 'iPhone',
               'ipad': 'iPad', 'imovie': 'iMovie', 'prores': 'ProRes'}
    return ' '.join(special.get(word, word) for word in topic.split('-'))

proposals = []
seen_operations = set()
for source in sources:
    if source['provider'] == 'Adobe Premiere documentation navigation':
        app, prefix = 'Premiere', 'premiere'
    elif source['provider'] == 'Apple Final Cut guide':
        app, prefix = 'Final Cut', 'final-cut'
    else:
        continue
    topic = normalized(source['topicKey'])
    words = set(topic.split('-'))
    if topic.split('-')[0] not in actions or not words.intersection(resources) or exclude.search(topic):
        continue
    if len(words) < 3:
        continue
    operation = (prefix, topic)
    if operation in seen_operations:
        continue
    seen_operations.add(operation)
    slug = prefix + '-native-' + topic
    title = app + ': ' + title_words(topic)
    if slug in existing_slugs or re.sub(r'[^a-z0-9]', '', title.lower()) in existing_titles:
        continue
    family = 'captions' if words.intersection({'caption','captions','subtitle','subtitles'}) else 'audio' if words.intersection({'audio','sound','music','speech','voice'}) else 'creator'
    if source['workflowGroup'] == 'troubleshooting':
        family = 'troubleshooting'
    task = ('Evaluate the native ' + title_words(topic) + ' operation in ' + app +
            ' for authorized retained media: identify the affected project or source resources, '
            'the intended output and a meaningful receiving check. Confirm the primary instructions '
            'and existing answer ownership before treating this as a separate guide.')
    proposals.append({'platform': 'general', 'family': family, 'slug': slug,
                      'title': title, 'task': task, 'source': source})

if proposals:
    with seed_path.open('a') as handle:
        handle.write('\n# Official native-operation discovery hypotheses; bodies and scope not yet approved.\n')
        for row in proposals:
            handle.write('|'.join(row[key] for key in ['platform','family','slug','title','task']) + '\n')
print(json.dumps({'rawOperationProposalsAdded': len(proposals),
                  'families': dict(Counter(row['family'] for row in proposals)),
                  'articlesWritten': 0, 'approved': 0, 'published': 0,
                  'requiresSemanticScopeReview': True}, indent=2))
