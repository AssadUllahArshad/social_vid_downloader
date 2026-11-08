import Link from "next/link";

export function ConverterGuide() {
  return (
    <section aria-labelledby="converter-help">
      <h2 id="converter-help">How to convert a video</h2>
      <ol>
        <li>Choose one video file from your device that you own or have permission to edit.</li>
        <li>Select an output format. Start with MP4 for a general viewing copy.</li>
        <li>Leave compression quality at 28 for a first attempt, or adjust it using the guidance below.</li>
        <li>Click Process files and keep this page open while the upload and conversion finish.</li>
        <li>Download the finished file before it expires. Open the saved copy and check the picture and sound.</li>
      </ol>
      <h2>Which output format should I choose?</h2>
      <ul>
        <li><strong>MP4:</strong> H.264 video with AAC audio, when audio is present. A practical starting point for sharing and playback; compatibility still depends on the receiving device or app.</li>
        <li><strong>WebM:</strong> VP9 video with Opus audio, when present. Choose it when your destination supports WebM. Encoding can take longer, and a smaller file is not guaranteed.</li>
        <li><strong>MOV:</strong> H.264 video with AAC audio, when present. Use it when your destination asks for a MOV file. This does not create a ProRes master or an editable project.</li>
      </ul>
      <p>Changing the format re-encodes the video. It cannot restore missing detail or guarantee a smaller file. See our <Link href="/guides/general/video-container-vs-codec/">guide to containers and codecs</Link> for the difference between a file format and its encoded streams.</p>
      <h2>What does compression quality mean?</h2>
      <p>The number controls compression, rather than resolution: lower values generally preserve more detail and produce larger files; higher values generally produce smaller files with more visible loss. The allowed range is 18–40, with 28 selected initially. Results vary with the source and output format, so compare a short clip before converting an important recording.</p>
      <h2>Files, audio and limits</h2>
      <p>Choose a local video file, not a social media URL. The service inspects the upload and rejects files it cannot read or process. A video filename alone does not guarantee that its codecs are supported.</p>
      <p>Conversion uses the first video stream and, if present, the first audio stream. Additional audio tracks, selectable subtitles, chapters and source metadata are not retained. Keep the original if those features matter.</p>
      <p>The current service limits are 200 MiB for the input and output, and 30 minutes of media duration. The upload form displays the active size limit. Processing also has a time limit, so a complex file can fail even when its size and duration fit. Prepared files expire after 10 minutes; download promptly and keep your own copy.</p>
      <h2>Why did my conversion fail?</h2>
      <p>Check the error message first. The input may be unreadable, exceed a limit, or require more processing time than available. Try a shorter source clip or a different output format. If the output is too large, a higher compression number may help at the cost of detail. Changing the filename extension does not repair or convert a file.</p>
    </section>
  );
}
