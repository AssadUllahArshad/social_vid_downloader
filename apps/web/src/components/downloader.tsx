"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import { useLocale } from "./locale-context";
import Image from "next/image";
import { platformName } from "@/lib/content";
import snapchatErrors from "@/locales/snapchat-errors.json";
import {
  Clipboard,
  Download,
  Link2,
  X,
  LoaderCircle,
  ShieldCheck,
  Play,
} from "lucide-react";
type AudioTrack = {
  id: string;
  language_code: string | null;
  language_name: string;
  label: string;
  is_default: boolean;
  is_original: boolean;
  is_descriptive?: boolean;
  is_dubbed?: boolean;
  codec: string;
  bitrate: number | null;
};
type VideoFormat = {
  id: string;
  quality: string;
  height: number;
  extension: string;
  filesize: number | null;
  estimatedFilesize: number | null;
  requiresMerge: boolean;
  hasAudio: boolean;
  videoCodec?: string;
  audioCodec?: string;
  audio_track_ids?: string[];
  default_audio_track_id?: string | null;
  audio_containers?: Record<string, string>;
  supports_dual_audio?: boolean;
};
type VideoResult = {
  sessionId: string;
  platform: string;
  title: string;
  thumbnail: string | null;
  creator: string | null;
  duration: number | null;
  formats: VideoFormat[];
  audio_tracks?: AudioTrack[];
  supports_dual_audio?: boolean;
};
type ReadyFile = {
  downloadUrl: string;
  previewUrl: string;
  filename: string;
  filesize: number;
  extension?: string;
  audio_mode?: string;
  audio_tracks?: AudioTrack[];
};
function audioFor(video: VideoResult, format?: VideoFormat) {
  return (video.audio_tracks || []).filter((track) => format?.audio_track_ids?.includes(track.id));
}
function differentAudio(first: AudioTrack, second: AudioTrack) {
  return first.id !== second.id && (!first.language_code || !second.language_code || first.language_code.split("-")[0] !== second.language_code.split("-")[0]);
}
function containerFor(format: VideoFormat, primary: string, secondary: string, dual: boolean) {
  const first = format.audio_containers?.[primary] || format.extension;
  const second = format.audio_containers?.[secondary] || first;
  return dual && first !== second ? "mkv" : first;
}
function bytes(value: number) {
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}
export function Downloader({
  platform,
  contentType,
  enabled = true,
  capabilityState = "AVAILABLE",
}: {
  example?: string;
  platform?: string;
  contentType?: string;
  enabled?: boolean;
  capabilityState?: "AVAILABLE" | "BETA" | "TEMPORARILY_UNAVAILABLE" | "UNSUPPORTED";
}) {
  const localeContext = useLocale();
  const localized = !!localeContext && localeContext.locale !== "en";
  const t = useCallback((english: string, key: keyof NonNullable<typeof localeContext>["messages"]) => {
    return localized ? localeContext!.messages[key] : english;
  }, [localized, localeContext]);
  function sourceError(message: string | undefined, code?: string) {
    if (code && (code.startsWith("snapchat_") || (platform?.toLowerCase() === "snapchat" && code === "content_unsupported"))) {
      const messages = snapchatErrors[localeContext?.locale || "en"];
      if (Object.hasOwn(messages, code)) return messages[code as keyof typeof messages];
    }
    if (!localized) return message;
    return localeContext!.messages[code && /expir/.test(code) ? "expired" : code && /invalid/.test(code) ? "invalid" : code && /unavailable|rate|restrict|authentication/.test(code) ? "sourceError" : "error"];
  }
  const [state, setState] = useState(capabilityState);
  const [availabilityNotice, setAvailabilityNotice] = useState<string | null>(null);
  useEffect(() => {
    if (!platform) return;
    const controller = new AbortController();
    fetch("/api/v1/capabilities/", { signal: controller.signal }).then(r => r.json()).then(data => {
      const provider = data.providers?.find((p: { platform: string }) => p.platform.toLowerCase() === platform.toLowerCase());
      const next = provider?.contentTypes?.[contentType || "video"];
      setAvailabilityNotice(typeof provider?.availabilityNotice === "string" ? t(provider.availabilityNotice, "sourceError") : null);
      if (["AVAILABLE", "BETA", "TEMPORARILY_UNAVAILABLE", "UNSUPPORTED"].includes(next)) setState(next);
    }).catch(() => {});
    return () => controller.abort();
  }, [platform, contentType, t]);
  const usable = enabled && (state === "AVAILABLE" || state === "BETA");
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [video, setVideo] = useState<VideoResult | null>(null);
  const [selected, setSelected] = useState("");
  const [audioMode, setAudioMode] = useState<"single" | "dual">("single");
  const [primaryAudio, setPrimaryAudio] = useState("");
  const [secondaryAudio, setSecondaryAudio] = useState("");
  const chosenFormat = video?.formats.find((format) => format.id === selected);
  const availableAudio = video ? audioFor(video, chosenFormat) : [];
  const primaryTrack = availableAudio.find((track) => track.id === primaryAudio);
  const secondaryTracks = availableAudio.filter((track) => !primaryTrack || differentAudio(primaryTrack, track));
  const dualAudio = audioMode === "dual";
  const audioValid = !availableAudio.length || Boolean(primaryTrack && (!dualAudio || secondaryTracks.some((track) => track.id === secondaryAudio)));
  const outputContainer = chosenFormat ? containerFor(chosenFormat, primaryAudio, secondaryAudio, dualAudio) : "";
  function clearPrepared() {
    setReady(null); setStatus(""); setError("");
  }
  function chooseAudio(result: VideoResult, format: VideoFormat, preferred = "") {
    const tracks = audioFor(result, format);
    const primary = tracks.find((track) => track.id === preferred) || tracks.find((track) => track.id === format.default_audio_track_id) || tracks[0];
    setPrimaryAudio(primary?.id || "");
    setSecondaryAudio(primary ? tracks.find((track) => differentAudio(primary, track))?.id || "" : "");
    if (!format.supports_dual_audio || tracks.length < 2) setAudioMode("single");
  }
  const [preparing, setPreparing] = useState(false);
  const [ready, setReady] = useState<ReadyFile | null>(null);
  const [thumbnailFailed, setThumbnailFailed] = useState(false);
  const [status, setStatus] = useState("");
  const requestVersion = useRef(0);
  useEffect(
    () => () => {
      requestVersion.current += 1;
    },
    [],
  );
  function reset() {
    requestVersion.current += 1;
    setVideo(null);
    setAudioMode("single"); setPrimaryAudio(""); setSecondaryAudio("");
    setReady(null);
    setPreparing(false);
    setThumbnailFailed(false);
    setLoading(false);
    setStatus("");
  }
  async function prepare() {
    if (!video || !selected || !audioValid) return;
    const version = ++requestVersion.current;
    setPreparing(true);
    setReady(null);
    setError("");
    setStatus(t("Preparing your download…", "preparing"));
    try {
      const response = await fetch("/api/v1/download/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: video.sessionId,
          formatId: selected,
          ...(availableAudio.length ? {audio_mode: audioMode, audio_track_ids: dualAudio ? [primaryAudio, secondaryAudio] : [primaryAudio]} : {}),
        }),
      });
      const created = await response.json();
      if (!response.ok || !created.success)
        throw new Error(
          sourceError(created.error?.message, created.error?.code) || t("The file could not be prepared.", "error"),
        );
      for (let attempt = 0; attempt < 180; attempt++) {
        if (version !== requestVersion.current) return;
        await new Promise((resolve) => setTimeout(resolve, 2000));
        if (version !== requestVersion.current) return;
        const poll = await fetch(created.statusUrl, { cache: "no-store" });
        const job = await poll.json();
        if (!poll.ok || job.status === "error")
          throw new Error(
            sourceError(job.error?.message, job.error?.code) || t("This download is no longer available.", "expired"),
          );
        if (job.status === "ready") {
          if (version === requestVersion.current) {
            setReady(job);
            setStatus(t("Your download is ready. Select Save file to save it to your device.", "ready"));
          }
          return;
        }
        if (version === requestVersion.current)
          setStatus(
            job.status === "queued"
              ? t("Your download is queued…", "queued")
              : t("Preparing your video and audio…", "preparing"),
          );
      }
      throw new Error(t("Preparing your download took too long. Please submit the link again.", "error"));
    } catch (problem) {
      if (version === requestVersion.current)
        setError(
          problem instanceof Error
            ? problem.message
            : t("Download preparation failed.", "error"),
        );
    } finally {
      if (version === requestVersion.current) setPreparing(false);
    }
  }
  function validate(value: string) {
    if (!value.trim()) return "";
    try {
      const parsed = new URL(value);
      if (
        !["https:", "http:"].includes(parsed.protocol) ||
        parsed.username ||
        parsed.password
      )
        return t("Please enter a public video link starting with http:// or https://.", "invalid");
      const hosts = [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "instagram.com",
        "www.instagram.com",
        "facebook.com",
        "www.facebook.com",
        "m.facebook.com",
        "fb.watch",
        "tiktok.com",
        "www.tiktok.com",
        "vm.tiktok.com",
        "vt.tiktok.com",
        "snapchat.com",
        "www.snapchat.com",
      ];
      if (!hosts.includes(parsed.hostname))
        return t("This website is not supported. Choose a listed platform.", "unsupported");
      return "";
    } catch {
      return t("Please enter a complete video link starting with https://.", "invalid");
    }
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const issue =
      validate(url) || (!url.trim() ? t("Paste a video link first.", "paste") : "");
    if (issue) {
      setError(issue);
      return;
    }
    reset();
    const version = ++requestVersion.current;
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/v1/extract/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: url.trim(),
          platform: platform?.toLowerCase(),
          contentType,
        }),
      });
      const result = await response.json();
      if (version !== requestVersion.current) return;
      if (!response.ok || !result.success)
        setError(
          sourceError(result.error?.message, result.error?.code) || t("The source video could not be analyzed.", "error"),
        );
      else {
        setVideo(result);
        setSelected(result.formats[0]?.id || "");
        setAudioMode("single");
        if (result.formats[0]) chooseAudio(result, result.formats[0]);
      }
    } catch {
      if (version !== requestVersion.current) return;
      setError(
        t("The video service is currently unavailable. Please try again later.", "sourceError"),
      );
    } finally {
      if (version === requestVersion.current) setLoading(false);
    }
  }
  return (
    <div className="download-card">
      <div className="card-label">
        <Link2 size={16} /> {t("YOUR VIDEO LINK", "paste")}
      </div>
      {state === "BETA" && <p className="notice" role="status">{t("Beta: public-link availability can vary. Only verified files are offered.", "limitations")}</p>}
      {state === "TEMPORARILY_UNAVAILABLE" && <p className="notice" role="status">{t("This tool is temporarily unavailable. Please try again later.", "sourceError")}</p>}
      <form onSubmit={submit}>
        <div className="url-row">
          <Link2 size={20} className="input-icon" />
          <input
            aria-label={t("Video URL", "paste")} 
            type="url"
            placeholder={localized ? localeContext!.messages.paste : platform ? `Paste a ${platformName(platform)} ${contentType === "shorts" ? "Shorts" : contentType === "reels" ? "Reel" : contentType === "spotlight" ? "Spotlight" : contentType === "story" ? "Story" : contentType === "status" ? "Status" : "video"} link` : "Paste a video link here"}
            value={url}
            onChange={(e) => {
              reset();
              setUrl(e.target.value);
              setError(validate(e.target.value));
            }}
            aria-invalid={Boolean(error)}
            aria-describedby="download-message"
            maxLength={2048}
          />
          {url ? (
            <button
              type="button"
              className="paste"
              aria-label={t("Clear URL", "clear")} 
              onClick={() => {
                reset();
                setUrl("");
                setError("");
              }}
            >
              <X size={16} />
            </button>
          ) : (
            <button
              type="button"
              className="paste"
              onClick={async () => {
                try {
                  const value = await navigator.clipboard.readText();
                  setUrl(value);
                  setError(validate(value));
                } catch {
                  setError(
                    t("Clipboard access is unavailable. Paste your link into the field.", "clipboard"),
                  );
                }
              }}
            >
              <Clipboard size={15} /> {t("Paste Link", "paste")}
            </button>
          )}
          <button
            className="download-button"
            disabled={loading || preparing || !usable}
            type="submit"
          >
            {loading ? (
              <LoaderCircle size={18} className="spin" />
            ) : (
              <Download size={18} />
            )}{" "}
            {loading ? t("Analyzing your video…", "analyze") : t("Download", "download")}
          </button>
        </div>
        <p
          id="download-message"
          role={error ? "alert" : undefined}
          className={error ? "error" : "input-help"}
        >
          {error ||
            t("Paste a link to content you own or have permission to save.", "notice")}
        </p>
      </form>
      {availabilityNotice && usable && <p className="input-help" role="status">{availabilityNotice}</p>}
      {video && (
        <section
          className="video-result"
          aria-label={t("Video preview and available qualities", "preview")} 
        >
          <div className="video-result-heading">
            {video.thumbnail && !thumbnailFailed ? (
              <Image
                width={180}
                height={105}
                unoptimized
                src={video.thumbnail}
                alt={t("Video thumbnail", "thumbnail")} 
                onError={() => setThumbnailFailed(true)}
                className="source-thumbnail"
              />
            ) : (
              <span className="no-thumbnail">
                <Play size={28} />
                {t("No thumbnail available", "thumbnail")}
              </span>
            )}
            <div>
              <span className="result-platform">{platformName(video.platform)}</span>
              <h3>{video.title}</h3>
              {video.creator && <p>{video.creator}</p>}
              {video.duration != null && (
                <p>
                  {Math.floor(video.duration / 60)}:
                  {Math.floor(video.duration % 60)
                    .toString()
                    .padStart(2, "0")}
                </p>
              )}
            </div>
          </div>
          <fieldset className="format-selector" disabled={preparing}>
            <legend>{t("Choose an available quality", "quality")}</legend>
            {video.formats.map((format) => (
              <label
                className={
                  selected === format.id
                    ? "format-option selected"
                    : "format-option"
                }
                key={format.id}
              >
                <input
                  type="radio"
                  name="quality"
                  value={format.id}
                  checked={selected === format.id}
                  onChange={() => {
                    setSelected(format.id);
                    chooseAudio(video, format, primaryAudio);
                    clearPrepared();
                  }}
                />
                <span>
                  <strong>{format.quality}</strong>
                  <span>
                    {containerFor(format, primaryAudio, secondaryAudio, dualAudio).toUpperCase()}
                    {dualAudio || (primaryAudio && format.default_audio_track_id !== primaryAudio)
                      ? t(" · size varies with audio selection", "unknownSize")
                      : format.filesize
                      ? ` · ${bytes(format.filesize)}`
                      : format.estimatedFilesize
                        ? ` · ${localized ? "≈" : "about"} ${bytes(format.estimatedFilesize)}`
                        : t(" · size unknown", "unknownSize")}
                  </span>
                  <small>
                    {format.requiresMerge
                      ? t("Audio and video will be combined", "merge")
                      : format.hasAudio
                        ? t("Video with audio", "withAudio")
                        : t("Silent video", "silent")}
                  </small>
                </span>
              </label>
            ))}
          </fieldset>
          {availableAudio.length > 1 ? (
            <div className="audio-controls">
              {chosenFormat?.supports_dual_audio && (
                <fieldset className="audio-mode" disabled={preparing}>
                  <legend>{t("Audio Mode", "audio")}</legend>
                  {(["single", "dual"] as const).map((mode) => <label key={mode}>
                    <input type="radio" name="audio-mode" checked={audioMode === mode} onChange={() => {setAudioMode(mode); clearPrepared();}} />
                    {mode === "single" ? t("Single Audio", "single") : t("Dual Audio", "dual")}
                  </label>)}
                </fieldset>
              )}
              <div className="audio-language-grid">
                <label htmlFor="primary-audio">{dualAudio ? t("Primary Audio", "primary") : t("Audio", "audio")}
                  <select id="primary-audio" aria-label={dualAudio ? t("Primary Audio", "primary") : t("Audio", "audio")} value={primaryAudio} disabled={preparing} onChange={(event) => {
                    const track = availableAudio.find((item) => item.id === event.target.value)!;
                    setPrimaryAudio(track.id);
                    if (!availableAudio.some((item) => item.id === secondaryAudio && differentAudio(track, item)))
                      setSecondaryAudio(availableAudio.find((item) => differentAudio(track, item))?.id || "");
                    clearPrepared();
                  }}>
                    {availableAudio.map((track) => <option key={track.id} value={track.id}>{localized && track.label === "Original" ? localeContext!.messages.original : track.label}</option>)}
                  </select>
                </label>
                {dualAudio && <label htmlFor="secondary-audio">{t("Secondary Audio", "secondary")}
                  <select id="secondary-audio" aria-label={t("Secondary Audio", "secondary")} value={secondaryAudio} disabled={preparing} onChange={(event) => {setSecondaryAudio(event.target.value); clearPrepared();}}>
                    {!secondaryTracks.length && <option value="">{t("No different audio language is available", "noAudio")}</option>}
                    {secondaryTracks.map((track) => <option key={track.id} value={track.id}>{localized && track.label === "Original" ? localeContext!.messages.original : track.label}</option>)}
                  </select>
                </label>}
              </div>
            </div>
          ) : <p className="audio-summary">{t("Audio", "audio")}: {(localized && availableAudio[0]?.label === "Original" ? localeContext!.messages.original : availableAudio[0]?.label) || (chosenFormat?.hasAudio ? t("Original", "original") : t("No audio available", "noAudio"))}</p>}
          {availableAudio.length > 0 && <p className="audio-output" role="status">
            {t("Output", "output")}: {chosenFormat?.quality} {outputContainer.toUpperCase()} · {dualAudio ? t("Dual Audio", "dual") : primaryTrack?.label}
            {outputContainer === "mkv" && t(" — MKV is required to preserve these tracks without re-encoding. Download the file and use a player that supports MKV.", "mkv")}
            {dualAudio && t(" Both audio tracks remain separate. Browser previews may play only the primary track; use a compatible player to switch tracks.", "dualHelp")}
          </p>}
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          {status && (
            <p className="processing-status" aria-live="polite">
              {status}
            </p>
          )}
          {ready ? (
            <div className="ready-file">
              {ready.extension !== "mkv" ? <video
                controls
                preload="metadata"
                src={ready.previewUrl}
                aria-label={t("Prepared video preview", "preview")} 
              /> : <p>{t("MKV preview is unavailable in most browsers. Save the file to play it in a compatible media player.", "mkv")}</p>}
              {ready.audio_tracks && ready.audio_tracks.length > 0 && <p>
                {t("Saved audio", "audio")}: {ready.audio_tracks.map((track) => track.label).join("; ")}
              </p>}
              <a className="download-button" href={ready.downloadUrl}>
                <Download size={18} />
                {t("Save file", "save")} · {bytes(ready.filesize)}
              </a>
              <p>{t("This file is temporary. Save it before the download link expires.", "temporary")}</p>
            </div>
          ) : (
            <button
              type="button"
              className="download-button prepare-button"
              disabled={preparing || !selected || !audioValid}
              onClick={prepare}
            >
              {preparing ? (
                <LoaderCircle size={18} className="spin" />
              ) : (
                <Download size={18} />
              )}{" "}
              {preparing
                ? t("Preparing your download…", "preparing")
                : availableAudio.length > 1
                  ? `${t("Download", "download")} ${chosenFormat?.quality || "video"}${dualAudio ? t(" Dual Audio", "dual") : `${localized ? " " : " with "}${primaryTrack?.label || t("selected audio", "audio")}`}`
                  : `${t("Prepare", "download")} ${chosenFormat?.quality || ""}`}
            </button>
          )}
        </section>
      )}
      <div className="card-footer">
        <span>
          <ShieldCheck size={15} /> {t("No account password required", "noPassword")}
        </span>
        <span>
          {enabled
            ? t("Public, authorized videos only", "notice")
            : t("This tool is unavailable", "unsupported")}
        </span>
      </div>
    </div>
  );
}
