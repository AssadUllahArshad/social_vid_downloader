// Explicit body-reviewed ownership decisions only; no similarity auto-approval.
import fs from 'node:fs';import {published,fingerprint} from '../apps/web/src/lib/editorial/workflow.mjs';
const load=p=>JSON.parse(fs.readFileSync(p));const state=load('docs/video-tools-execution-state.json'),registry=load('content/editorial/first-500-inventory.json'),articles=load('content/editorial/articles.json');
const groups=[
  [
    "container-track-id-vs-stream-index",
    [
      "matroska-track-uid-vs-index",
      "mpeg-ts-program-vs-stream-selection",
      "container-multiple-video-streams-role",
      "mp4-cover-art-vs-video-track"
    ],
    "The owner explicitly covers native IDs versus numeric order, program/component selection and attached-image versus motion roles, with local program/stream inspection and actual-content verification."
  ],
  [
    "mkv-attachments-vs-subtitle-streams",
    [
      "mkv-attachment-mime-filename-identity",
      "mkvtoolnix-font-attachments-retention",
      "container-data-stream-preservation"
    ],
    "The owner distinguishes timed streams and other data roles from attached fonts/covers, verifies export scope and font/name identity, and retains required companions without promising unknown-stream preservation."
  ],
  [
    "duration-stream-vs-container",
    [
      "mp4-edit-list-trim-interpretation",
      "ffmpeg-shortest-termination-scope",
      "video-edited-file-container-duration",
      "video-last-frame-hang-vs-duration"
    ],
    "The owner explicitly compares container/stream/presentation endpoints, stored versus selected intervals, final holds and shortest-input termination, then verifies wanted ending picture and sound."
  ],
  [
    "video-decoder-error-concealment",
    [
      "codec-reference-frame-loss"
    ],
    "The owner explains reference-dependent damage propagation and concealed reconstruction, compares decoder evidence and refuses original-recovery claims."
  ],
  [
    "video-motion-blur-vs-low-frame-rate",
    [
      "video-shutter-angle-vs-playback-rate"
    ],
    "The owner separates within-frame exposure context from cadence and playback retiming, explicitly stating that viewing-rate changes cannot reconstruct sharper captured samples."
  ],
  [
    "video-row-stride-vs-raster-size",
    [
      "raw-video-no-container-timing"
    ],
    "The owner requires producer-known pixel representation, dimensions, row stride and separate timing/audio context before a raw-frame import."
  ],
  [
    "video-cloud-name-collision-case-folding",
    [
      "video-cloud-reserved-filename-rejection",
      "video-file-names-unicode-normalization",
      "windows-long-path-video-copy",
      "mac-finder-tag-vs-filename",
      "video-zip-extraction-name-collision"
    ],
    "The owner covers case/Unicode identity, destination rules and path constraints, labels versus actual filenames, archive-entry overwrite scope and preserving a mapping to both original recordings."
  ],
  [
    "linux-video-hardlinks-storage-accounting",
    [
      "mac-finder-alias-broken-media-target",
      "mac-video-folder-symlink-backup-scope",
      "windows-video-folder-junction-copy-scope",
      "video-reflink-copy-vs-independent-backup"
    ],
    "The owner distinguishes hard-link shared identity, symlink/alias/junction targets and copy traversal, and logical copy-on-write sharing versus a separately recoverable off-device copy. GNU and Microsoft primary documentation were reviewed."
  ],
  [
    "pts-vs-dts-video-timestamps",
    [
      "mov-timescale-vs-frame-rate",
      "video-b-frames-decode-order",
      "vp9-superframe-packet-count",
      "matroska-laced-block-versus-frame",
      "matroska-timestamp-scale-clock-inspection",
      "matroska-negative-timestamp-decode-context",
      "video-duration-first-frame-negative-pts",
      "ffprobe-count-frames-vs-nb-frames"
    ],
    "The owner now explicitly covers native timescale interpretation, reordered/negative decode timing, grouped packets/blocks versus decoded pictures and missing metadata counts versus counted intervals. It directs the same receiving inspection rather than asserting universal raw units."
  ],
  [
    "video-raster-versus-active-picture",
    [
      "display-aspect-ratio-clean-aperture"
    ],
    "The owner explicitly covers coded grid, clean-aperture presentation and destructive cropping as distinct observations before the receiving check."
  ],
  [
    "encoder-preset-vs-quality-control",
    [
      "codec-encoder-quality-preset-scope"
    ],
    "The existing owner explains encoder-specific preset effort and explicitly rejects matching preset labels as evidence of equal codec quality or speed."
  ],
  [
    "constant-quality-vs-target-bitrate",
    [
      "codec-crf-qp-bitrate-decision"
    ],
    "The existing owner chooses actual delivery constraints, explains mode/codec-specific numerical settings and measures output rather than promising universal quality-to-size conversion."
  ],
  [
    "ffmpeg-sharpen-halo-review",
    [
      "video-ringing-vs-sharpening-halos"
    ],
    "The existing owner compares original and derivative edges, distinguishes newly exaggerated fringes and rejects sharpening as a universal source-detail restoration."
  ],
  [
    "demuxer-vs-decoder",
    [
      "codec-extradata-missing-remux",
      "codec-extradata-versus-packet-payload"
    ],
    "The owner now has explicit decoder-initialization/parameter-resource versus packet-payload coverage, inspecting receiver/container requirements after remux instead of inferring configuration from a label."
  ]
];
let count=0;for(const[target,slugs,reason]of groups){const owner=articles.find(x=>x.path===`/guides/general/${target}/`);if(!owner||!published(owner)||owner.approval?.digest!==fingerprint(owner))throw Error(`Unapproved owner ${target}`);for(const slug of slugs){const row=registry.find(x=>x.path===`/guides/general/${slug}/`);if(!row)throw Error(`Missing existing ID ${slug}`);if(!state.seoCompletion.remainingIDs.includes(row.id))continue;row.dispositionHistory=[...(row.dispositionHistory||[]),row.disposition];Object.assign(row,{status:'ARCHIVED',indexable:false,inventoryApproval:null,semanticReview:{state:'MERGED_EXISTING_TASK',reviewer:'Consolidated full-body intent review',reviewedAt:'2026-10-12',comparisons:[owner.path],rationale:reason},disposition:{classification:'MERGE_WITH_EXISTING',outcome:'CONSOLIDATED',destination:owner.path,internalLinkDestination:owner.path,reason,reviewedAt:'2026-10-12'},candidateCompletion:{completedAt:'2026-10-12',result:'MERGED',publicationEligible:false,missingRequirements:[]}});state.seoCompletion.decisions.push({id:row.id,path:row.path,outcome:'MERGED',destination:owner.path,reason});state.seoCompletion.completedIDs.push(row.id);state.seoCompletion.remainingIDs=state.seoCompletion.remainingIDs.filter(id=>id!==row.id);count++;}}
const m=state.seoCompletion;m.processed=m.completedIDs.length;m.merged=m.decisions.filter(d=>d.outcome==='MERGED').length;m.stillDeferred=m.remainingIDs.length;m.unprocessed=m.remainingIDs.length;m.lastCompletedID=m.decisions.at(-1)?.id;state.phases.E.remainingAuthoringIDs=m.remainingIDs;state.phases.E.remainingIDs=m.remainingIDs;state.phases.E.remainingDrafts=m.remainingIDs.length;state.remainingAuthoringRecords=m.remainingIDs.length;state.seoCompletion.batches??=[];if(count)state.seoCompletion.batches.push({date:'2026-10-12',startingRemaining:997,published:8,merged:count,rejected:0,completedThisBatch:8+count,remaining:m.remainingIDs.length});
fs.writeFileSync('content/editorial/first-500-inventory.json',JSON.stringify(registry,null,2)+'\n');fs.writeFileSync('docs/video-tools-execution-state.json',JSON.stringify(state,null,2)+'\n');console.log({newMerges:count,lifetimeProcessed:m.processed,published:m.published,remaining:m.remainingIDs.length});
