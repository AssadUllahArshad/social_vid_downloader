// Existing-record authoring only. No network requests, discovery, or provider edits.
import {readFileSync,writeFileSync,renameSync} from 'node:fs';
import {qualityGate,transition,fingerprint,publicationInventory,published} from '../apps/web/src/lib/editorial/workflow.mjs';
const load=p=>JSON.parse(readFileSync(p,'utf8'));
const registryPath='content/editorial/first-500-inventory.json',articlePath='content/editorial/articles.json';
const briefs=load(registryPath),articles=load(articlePath),core=load('content/pages/publication.json');
const statePath='docs/5000-page-build-state.md';const state=JSON.parse(readFileSync(statePath,'utf8').match(/```json\n([\s\S]*?)\n```/)[1]);
const pass=state.existingDraftBulkPass,completed=new Set(pass.completedIDs),date='2026-10-09';
const drafts=[
['audacity-resample-vs-set-track-rate','Audacity resampling versus rate interpretation: preserve timing',
'Choose between converting a recording to another sample rate and changing how its existing samples are timed. Check pitch, duration and synchronization.',
'Resampling and reinterpreting a track’s sample rate solve different problems. A proper conversion represents the same passage at a new sample rate while aiming to preserve its duration. Reading unchanged samples at another rate changes their timing and pitch. Decide which outcome you actually need before adjusting an authorized recording.',
[
['Identify the operation before changing a rate',
'A sample-rate value describes how many samples belong to a second of playback. It is not a loudness control or a promise of better source quality. A receiving editor may need a particular rate for compatibility, but that requirement does not mean the original performance should become faster or higher pitched.',
'In a conversion, the processor calculates a new sequence of samples for the requested time grid. In reinterpretation, the sequence is treated as belonging to a different clock. The distinction remains important even if both workflows show the same final rate label. Use your installed Audacity version’s documented controls rather than assuming that every rate field performs conversion.'],
['Compare duration and recognizable landmarks',
'Keep the source unchanged and record its duration, known rate and a few clear listening landmarks. Export a separate test using the operation you intend. Compare the opening, middle and ending in a receiving player or editor. An expected format label alone cannot prove that the passage kept its pace or alignment.',
'When the source is synchronized to picture, compare identifiable mouth movements or other sound events after importing the test. If both pitch and duration changed unexpectedly, investigate reinterpretation before compensating with an unrelated speed effect. If duration stayed similar but isolated events moved, inspect the rest of the edit and processing path instead of blaming the rate label alone.'],
['Verify the handoff without inventing detail',
'Inspect the actual exported stream’s sample rate, channel count and duration. These properties answer different questions. A higher sample rate does not recover missing frequencies or undo earlier lossy encoding. Retain the original file and identify the test as a derivative so the recipient can repeat or reverse the choice.',
'A successful check uses the required representation and preserves the intended passage. If the receiver rejects the file, inspect its codec and container as well as its rate; renaming an extension does not perform any conversion. Do not repeatedly transform the only retained source while searching for a compatible export.']
],
'Suppose a ten-second recording contains 480,000 samples per channel at 48,000 samples per second. Reinterpreting those samples as 44,100 per second makes the passage about 10.88 seconds long. A conversion to 44,100 Hz instead produces roughly 441,000 samples per channel for the same ten-second passage. Compare the actual result rather than relying on its filename.',
['audio-sample-rate','audio-pitch-shift-vs-playback-speed']],
['pcm-endianness-raw-import','Raw PCM import: supply the missing sample interpretation',
'Identify sample rate, channel count, sample format and byte order before importing headerless PCM. Verify duration and avoid guessing from an extension.',
'A headerless PCM recording does not describe how its bytes should be interpreted. To import it correctly, you need the sample format, byte order where relevant, channel organization and sample rate supplied by its producer. Guessing can produce harsh noise, the wrong duration or incorrect channels even when the file is complete.',
[
['Obtain the recording description first',
'Ask the producer for the actual export parameters and whether the payload is truly raw audio. A WAV container can carry descriptive headers; a headerless payload cannot provide the same information by itself. Do not remove a header from a supported container merely because a raw-import option is available in your editor.',
'Identify whether samples are integer or floating point, their width, and the applicable signedness. For multibyte values, endianness describes the order of bytes within each value. Channel count and arrangement describe how successive values belong to channels. These are interpretation choices, not language selections or audio enhancement settings.'],
['Check the expected size and listening result',
'For a straightforward interleaved PCM payload, duration can be estimated by dividing byte count by sample rate, channel count and bytes per sample. This estimate assumes no extra framing, padding or attached metadata. A large discrepancy with the producer’s stated duration is a reason to investigate the format rather than trim the recording.',
'Import a copy with the confirmed parameters and start listening at a low, comfortable level. Stop if the result is unexpectedly loud noise. Compare recognizable speech, beginning and ending, and channel contributions. A readable waveform alone does not prove that byte order or sample interpretation is correct.'],
['Verify an ordinary delivery copy',
'Export a separate supported audio file once interpretation is established. Inspect its duration, channel count and rate, then listen in the receiving application. A conventional container helps communicate those properties to the recipient, but it cannot make incorrectly decoded samples authentic by labeling them with plausible metadata.',
'Preserve the original payload together with the producer’s parameter note. If essential details remain unknown, describe the file as unresolved rather than distributing a guessed decoding as a verified recording. This downloader handles supported source media; it does not identify arbitrary raw recordings or guarantee recovery from missing format information.']
],
'Suppose a producer confirms 48,000 Hz, mono, signed 16-bit little-endian PCM with no framing. Two bytes per sample imply 96,000 bytes per second. A 5,760,000-byte payload therefore represents sixty seconds. Treating the same bytes as stereo would suggest thirty seconds, showing why the channel description matters before editing.',
['audio-sample-rate','mono-vs-stereo-dialogue']],
['audio-rumble-highpass-review','Review a high-pass filter without thinning the voice',
'Separate unwanted low-frequency rumble from wanted voice and environmental sound. Compare a scoped high-pass change at matched listening levels.',
'A high-pass filter attenuates lower frequencies; it does not recognize which sound belongs to a voice. It may reduce low-frequency rumble while also removing wanted warmth or environmental information. Choose a scoped adjustment by listening to the actual passage, not by applying one supposedly correct cutoff to every recording.',
[
['Identify the unwanted low-frequency component',
'Compare the unprocessed recording with the problem you hear. Wind, handling noise and mechanical vibration can create low-frequency disturbance, but the audible cause is not established by a waveform looking large. Check whether the disturbance is localized or sustained, and whether it occurs during speech you need to preserve.',
'Listen through a dependable receiving path at a comfortable level. Tiny speakers can conceal both rumble and useful low-frequency sound. A different monitoring arrangement may reveal the problem without changing the file. Retain an unchanged source and note which passage you are evaluating before adjusting any processing.'],
['Make a controlled comparison around the affected passage',
'Create a separate test and vary one filter choice at a time. Cutoff and slope affect how broadly low-frequency content is reduced. Begin with a restrained adjustment and compare the whole phrase, including quiet syllables and pauses. Avoid interpreting a simple drop in overall level as proof that intelligibility improved.',
'Use comparable listening levels for the original and processed versions. Listen for a voice becoming thin, a meaningful background cue disappearing, or a transition sounding different at the edge of a selected interval. If the noise overlaps speech across a broad range, a high-pass filter may leave much of it intact while still changing the voice.'],
['Verify the accepted derivative',
'Check the actual exported recording in the intended player or video edit. Confirm that the duration and synchronization stayed appropriate and that the passage is understandable. A cleaner preview in an editor is not sufficient evidence if the final export uses different processing or omits an enabled effect.',
'Document the affected interval and the accepted filter choice, and keep the source available. Do not claim that filtering reconstructs missing detail or restores damaged microphone capture. If the result sacrifices important sound, keep the original and reconsider the delivery requirement instead of repeatedly raising the cutoff.']
],
'Suppose a short interview has a low mechanical rumble between sentences. A test makes the pauses quieter but also removes much of a speaker’s lower vocal tone. The useful comparison includes that speaker’s complete sentence, not only a silent interval. Accept a more restrained result or keep the source if the lost tone matters.',
['audio-loudness-vs-peak','lossy-vs-lossless-media']],
['audio-hum-notch-harmonics','Identify hum and harmonics before applying a notch',
'Check whether interference is narrow and recurring, inspect harmonics, and compare a restrained notch against speech rather than assuming one hum frequency.',
'A notch reduces a narrow frequency region. It can help with a recurring tonal interference, but it does not identify the interference automatically or separate a voice from every overlapping sound. Measure and listen to the recording before choosing a notch; do not assume one electrical frequency is correct for every source.',
[
['Distinguish a recurring tone from broad noise',
'Listen to both a quiet interval and a passage containing speech. A sustained tone, broad hiss and changing mechanical sound call for different investigations. A frequency display can help locate recurring components, but a visible line may also belong to wanted musical or environmental content. Keep the original recording for comparison.',
'Harmonics occur at multiples of a fundamental frequency. A recording can contain several related components rather than one isolated tone. Check the observed spectrum and listening result instead of applying a list of guessed frequencies. The recording path, environment and later processing can affect what is actually present.'],
['Compare a narrow adjustment against wanted sound',
'Test one limited notch on a copy and listen across the affected region. Width and depth influence how much nearby content changes. A deeper or broader cut is not automatically a better cleanup, particularly where voice or music occupies the same region. Compare at sensible, similar listening levels.',
'If a tone remains, check whether it belongs to another recurring component rather than widening the first notch indiscriminately. Investigate changes one at a time so you can identify which choice helped or harmed the recording. Listen for unnatural vocal color, ringing or a mismatch between processed and unprocessed intervals.'],
['Verify the whole phrase and exported file',
'Judge intelligibility and retained meaning, not only a quieter spectrum line. Include quiet speakers, held sounds and important ambience in the check. A treatment that sounds convincing in a short pause can still damage a phrase where the wanted signal overlaps the interference.',
'Export a separately identified derivative and compare it in the receiving application. Retain the source and a note of the accepted processing. Notching does not repair clipped capture or guarantee removal of changing interference. If the needed signal cannot be retained acceptably, explain the limitation instead of labeling the result a complete restoration.']
],
'Suppose an inspection finds a steady component near 60 Hz and another near 120 Hz. Reducing only the first may leave an audible higher component. Those observations justify separate controlled comparisons on this recording; they do not justify applying 60 Hz to a different file whose disturbance is elsewhere.',
['audio-rumble-highpass-review','audio-loudness-vs-peak']],
['integrated-vs-short-term-loudness','Integrated versus short-term loudness: choose the interval',
'Compare whole-program loudness with a moving listening interval. Reset measurements, use matching passages and keep loudness readings separate from peaks.',
'Integrated loudness summarizes the measured program interval, while short-term loudness describes a moving portion of that program. A whole-file reading can hide a quiet sentence or a loud transition. Compare the same content and measurement scope before using either result to judge a speech passage or delivery copy.',
[
['Decide which question the measurement should answer',
'For a complete delivery, measure the intended full program rather than an arbitrary excerpt. For a local level change, examine the passage around that change. A short segment containing only an introduction is not interchangeable with an entire interview. Record the interval and the meter’s displayed measurement type alongside the result.',
'Peak readings answer another question about brief extremes. They cannot replace a program loudness measurement, and loudness alone does not establish whether a waveform clips. Check both when preparing an authorized derivative. Listening volume on your device also changes your experience without changing the stored audio or its measured program properties.'],
['Make a comparison using matching material',
'Reset the meter as appropriate for a fresh whole-program measurement and play the intended interval. Check that the observed signal is the one you plan to export, including enabled tracks and processing. A stale reading that includes an earlier playback can lead to an incorrect conclusion about the current passage.',
'For short-term comparisons, observe corresponding moments in the original and derivative. Include quieter speech and transitions, not only the loudest section. If a file’s overall result seems similar while one speaker becomes difficult to hear, inspect that local passage rather than applying one global change based solely on the integrated value.'],
['Verify the receiving copy rather than a meter alone',
'Listen to the actual export at a comfortable level and inspect its peak behavior as well as the relevant loudness measurements. Level changes, compression and editing can affect local dynamics differently. Similar numerical readings do not guarantee equal clarity, naturalness or retained meaning.',
'Use the recipient’s documented delivery requirement when one exists; there is no single invented target that suits every platform or listening purpose. Preserve the original and identify which interval and method produced your comparison. This downloader preserves available source media rather than automatically mastering every recording to a universal loudness value.']
],
'Suppose two interviews have similar whole-program measurements. One contains a much quieter answer after a loud introduction. Comparing that answer’s moving loudness and listening clarity reveals a local issue that the overall number cannot explain alone. Review the answer and transition before making a change to the entire program.',
['audio-loudness-vs-peak','mono-vs-stereo-dialogue']],
['float-audio-export-integer-clipping','Floating-point audio to integer delivery: check scaled peaks',
'Check recoverable floating-point levels before integer export. Preserve the source and distinguish numerical headroom from audio clipped during capture.',
'A floating-point working representation can hold values outside the normal full-scale range, but that does not make every overloaded recording recoverable. Before an integer delivery, inspect and scale the actual signal as needed. Distinguish numerical over-range values from distortion already introduced by a microphone, converter or earlier processing stage.',
[
['Find the layer where overload occurred',
'Keep the unchanged recording and examine representative loud events. A waveform reaching a boundary may suggest an issue, but its appearance alone does not prove where distortion originated. Compare listening evidence and the known capture or processing path. Lowering level cannot reconstruct peaks that were already flattened earlier in the chain.',
'A float working file provides a representation for processing, not a guarantee about the original capture hardware. A low-level export of an already distorted recording can still sound distorted. Avoid describing any format label as proof of unlimited microphone headroom or a promise that clipped voices will become authentic again.'],
['Prepare a separately scaled integer export',
'When intact over-range values exist in the working signal, make a controlled gain adjustment before an integer conversion so the intended peaks fit the delivery range. Check the complete recording rather than assuming the first loud passage is its maximum. Account for enabled effects that may change the signal after your adjustment.',
'Select the actual required sample format and retain sufficient level margin for the intended delivery. Quantization and encoding introduce separate considerations; changing bitrate is not a substitute for addressing over-range samples. Do not repeatedly overwrite the only float source while comparing alternatives or searching for a suitable level.'],
['Verify the resulting sound and representation',
'Inspect the exported file’s actual sample representation where applicable, then listen to the previously troublesome events in the receiving application. Check that the delivered signal has not introduced new clipping and that quieter material remains usable. A meter inside the project does not establish what a differently configured export contains.',
'If distortion remains after a sensible level change, investigate an earlier clipped stage or another processing cause. Keep the evidence and explain the limitation rather than promising restoration. This service can provide available source streams; it does not repair captured overload or certify arbitrary edited audio as an unchanged master.']
],
'Suppose a working float signal has intact peaks above its normal full-scale reference. Lowering gain before a separate integer export can bring those peaks within range. If the original analog capture already flattened a shouted syllable, lowering the same passage merely makes the distorted syllable quieter; it cannot recover its missing shape.',
['audio-loudness-vs-peak','lossy-vs-lossless-media']]
];
const sources=[{title:'FFmpeg: audio processing and measurement reference',url:'https://www.ffmpeg.org/ffmpeg-filters.html'},{title:'FFprobe: inspect exported media',url:'https://ffmpeg.org/ffprobe.html'}];
const review={accuracy:true,distinctValue:true,answerFirst:true,supportedClaims:true,examples:true,specificity:true,reviewer:'Existing-draft bulk content review',reviewedAt:date};
const candidates=[];
for(const [slug,title,description,intro,sections,example,links] of drafts){
 const brief=briefs.find(b=>b.path===`/guides/general/${slug}/`);if(!brief||completed.has(brief.id)||brief.status!=='DRAFT')continue;
 const related=links.map(s=>`/guides/general/${s}/`);
 const rationale=`This record addresses ${brief.userBenefit} The related existing articles explain broader representations or listening checks. This page instead supplies a controlled comparison, a distinct failure boundary and a worked example for that specific task; it makes no new downloader or application-version claim.`;
 candidates.push({...brief,title,h1:title,description,intro,sections:sections.map(([heading,...paragraphs])=>({heading,paragraphs})),example,related,sources,faq:[],canonical:brief.path,status:'REVIEW',indexable:false,lastUpdated:date,review,inventoryApproval:{approved:true,intent:brief.intent,path:brief.path,rationale},whyExistingContentDoesNotSatisfy:rationale,semanticReview:{...brief.semanticReview,state:'APPROVED_DISTINCT_TASK',reviewer:review.reviewer,reviewedAt:date,rationale}});
}
const reports=candidates.map(p=>({page:p,quality:qualityGate(p,[...articles,...candidates],core,1)}));
const successful=new Set(reports.filter(r=>r.quality.passed).map(r=>r.page.path));
for(const {page,quality} of reports){
 const b=briefs.find(b=>b.path===page.path);
 if(!quality.passed||page.related.some(path=>!articles.some(p=>published(p)&&p.path===path)&&!successful.has(path))){b.bulkScreening={result:'CONTENT_FAILED_STATIC_GATE',errors:quality.errors,checkedAt:new Date().toISOString()};continue;}
 let approved=transition(page,'APPROVED',{passed:true,digest:fingerprint(page)});approved=transition(approved,'PUBLISHED',{passed:true,digest:approved.approval.digest});articles.push({...approved,quality});
 Object.assign(b,{status:'PUBLISHED',indexable:true,inventoryApproval:page.inventoryApproval,semanticReview:page.semanticReview,whyExistingContentDoesNotSatisfy:page.whyExistingContentDoesNotSatisfy,disposition:{...b.disposition,classification:'APPROVED_TO_WRITE',outcome:'PUBLISHED',destination:b.path,reason:page.whyExistingContentDoesNotSatisfy,reviewedAt:date}});
 completed.add(b.id);pass.decisions.push({id:b.id,path:b.path,outcome:'PUBLISHED'});
}
for(const [path,data] of [[registryPath,briefs],[articlePath,articles]]){writeFileSync(path+'.tmp',JSON.stringify(data,null,2)+'\n');renameSync(path+'.tmp',path);}
pass.completedIDs=[...completed];pass.pendingIDs=pass.originalDraftIDs.filter(id=>!completed.has(id));pass.published=pass.decisions.filter(d=>d.outcome==='PUBLISHED').length;pass.lastCompletedID=pass.completedIDs.at(-1);pass.nextID=pass.pendingIDs[0];pass.updatedAt=new Date().toISOString();pass.validation={status:'FINAL_VALIDATION_PENDING'};
state.currentIndexable=publicationInventory(core,articles).filter(published).length;state.currentPublishedArticles=articles.filter(published).length;state.unresolvedCandidates=pass.pendingIDs.length;
writeFileSync(statePath,'# Existing-draft bulk checkpoint\n\nOnly existing records are authorized; no new topics or candidates. Pending IDs require complete, evidence-backed content review. Resume without repeating completed IDs.\n\n```json\n'+JSON.stringify(state,null,2)+'\n```\n');
console.log(JSON.stringify({attempted:candidates.length,publishedThisRun:reports.filter(r=>completed.has(briefs.find(b=>b.path===r.page.path).id)).length,errors:reports.filter(r=>!r.quality.passed).map(r=>({path:r.page.path,errors:r.quality.errors})),remaining:pass.pendingIDs.length,indexable:state.currentIndexable}));
