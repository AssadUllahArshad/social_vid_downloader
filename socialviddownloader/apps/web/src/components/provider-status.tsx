"use client";
import { useState } from "react";
import { platformName } from "@/lib/content";
type Provider = {
  provider: string; supportedContentTypes: string[]; status: string;
  extraction: string; download: string; lastTestStatus: string;
  lastFailureCategory: string | null; lastSuccessfulLiveTest: string | null;
  supports_multiple_audio_tracks?: boolean | null;
  supports_language_metadata?: boolean | null;
  supports_dual_audio_mux?: boolean | null;
};
export function ProviderStatus() {
  const [token, setToken] = useState("");
  const [providers, setProviders] = useState<Provider[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function load(event: React.FormEvent) {
    event.preventDefault(); setLoading(true); setError(""); setProviders([]);
    try {
      const response = await fetch("/api/admin/providers/", { headers: { Authorization: `Bearer ${token}` }, cache: "no-store" });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error?.message || result.error || "Provider status could not be loaded.");
      setProviders(result.providers); setToken("");
    } catch (problem) { setError(problem instanceof Error ? problem.message : "Provider status is unavailable."); }
    finally { setLoading(false); }
  }
  function evidence(value?: boolean | null) { return value == null ? "Not observed" : value ? "Observed" : "Not present"; }
  return <section aria-labelledby="provider-status-title">
    <h2 id="provider-status-title">Provider status</h2>
    <p>Read-only operational status. Administrator access is required; the token is never stored in the browser.</p>
    <p>Audio capability observations describe tested source videos, not every video on a platform.</p>
    <form onSubmit={load} className="provider-login">
      <label htmlFor="provider-token">Administrator access token</label>
      <input id="provider-token" type="password" autoComplete="off" value={token} onChange={event => setToken(event.target.value)} required maxLength={256} />
      <button className="download-button" disabled={loading}>{loading ? "Loading…" : "Load provider status"}</button>
    </form>
    {error && <p role="alert">{error}</p>}
    <div className="provider-health-grid">{providers.map(provider => <article className="notice" key={provider.provider}>
      <h3>{platformName(provider.provider)}</h3>
      <dl>
        <dt>Supported content</dt><dd>{provider.supportedContentTypes.join(", ") || "None"}</dd>
        <dt>Status</dt><dd>{provider.status}</dd>
        <dt>Analysis / download</dt><dd>{provider.extraction} / {provider.download}</dd>
        <dt>Multiple audio tracks in the last source</dt><dd>{evidence(provider.supports_multiple_audio_tracks)}</dd>
        <dt>Language metadata in the last source</dt><dd>{evidence(provider.supports_language_metadata)}</dd>
        <dt>Verified multiple-audio output</dt><dd>{evidence(provider.supports_dual_audio_mux)}</dd>
        <dt>Last test</dt><dd>{provider.lastTestStatus}</dd>
        <dt>Last failure category</dt><dd>{provider.lastFailureCategory || "None recorded"}</dd>
        <dt>Last successful live download test</dt><dd>{provider.lastSuccessfulLiveTest || "Not recorded"}</dd>
      </dl>
    </article>)}</div>
  </section>;
}
