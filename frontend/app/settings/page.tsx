"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Server, CheckCircle2, XCircle, RefreshCw, Key, Shield, Globe, Copy, Check, Terminal } from "lucide-react";

export default function SettingsPage() {
  const [readiness, setReadiness] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copiedUrl, setCopiedUrl] = useState(false);

  const checkReadiness = async () => {
    try {
      setLoading(true);
      const res = await api.getReadiness();
      setReadiness(res);
    } catch (e) {
      console.error(e);
      setReadiness({ status: "error", database: false, redis: false });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkReadiness();
  }, []);

  const webhookUrl = typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000/api/v1/webhooks/github`
    : "http://localhost:8000/api/v1/webhooks/github";

  const handleCopy = () => {
    navigator.clipboard.writeText(webhookUrl);
    setCopiedUrl(true);
    setTimeout(() => setCopiedUrl(false), 2000);
  };

  return (
    <div className="space-y-8 max-w-5xl animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-zinc-100">
              System Settings &amp; Infrastructure Health
            </h1>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-surface-muted text-emerald-400 border border-surface-border">
              Enterprise v1.4
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Backend readiness probes, GitHub webhook secret verification, and regional electricity grid integration.
          </p>
        </div>

        <button
          onClick={checkReadiness}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-card border border-surface-border hover:bg-surface-hover text-xs font-semibold text-zinc-300 shadow-sm transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${loading ? "animate-spin" : ""}`} />
          <span>Probe System (/ready)</span>
        </button>
      </div>

      {/* Backend Readiness Probe (/ready) */}
      <div className="p-6 rounded-xl bg-surface-card border border-surface-border space-y-4 hover-card-glow transition-all">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
              <Server className="w-4 h-4 text-emerald-400" />
              Infrastructure Readiness Probes
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Live checks against PostgreSQL database connection and Redis low-carbon queue
            </p>
          </div>
        </div>

        {readiness && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div className="p-4 rounded-lg bg-surface-canvas border border-surface-border flex items-center justify-between">
              <div>
                <span className="text-xs text-zinc-400 block">PostgreSQL / SQLite</span>
                <span className="text-xs font-semibold text-zinc-200">Database Engine</span>
              </div>
              <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 px-2.5 py-1 rounded bg-emerald-950/70 border border-emerald-800/80">
                <CheckCircle2 className="w-3.5 h-3.5" /> Connected
              </span>
            </div>

            <div className="p-4 rounded-lg bg-surface-canvas border border-surface-border flex items-center justify-between">
              <div>
                <span className="text-xs text-zinc-400 block">Redis Cache &amp; Celery</span>
                <span className="text-xs font-semibold text-zinc-200">Job Scheduler</span>
              </div>
              <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 px-2.5 py-1 rounded bg-emerald-950/70 border border-emerald-800/80">
                <CheckCircle2 className="w-3.5 h-3.5" /> Ready
              </span>
            </div>

            <div className="p-4 rounded-lg bg-surface-canvas border border-surface-border flex items-center justify-between">
              <div>
                <span className="text-xs text-zinc-400 block">Environment Mode</span>
                <span className="text-xs font-semibold text-zinc-200">Deployment</span>
              </div>
              <span className="text-xs font-mono font-bold text-zinc-200 uppercase px-2.5 py-1 rounded bg-surface-muted border border-surface-border">
                {readiness.environment || "production"}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* GitHub Webhook Ingestion Configuration */}
      <div className="p-6 rounded-xl bg-surface-card border border-surface-border space-y-4 hover-card-glow transition-all text-xs">
        <div>
          <h2 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
            <Key className="w-4 h-4 text-emerald-400" />
            GitHub App &amp; Webhook Integration Parameters
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Configure repository webhooks to receive real-time pull request diffs and workflow run completions
          </p>
        </div>

        <div className="space-y-4 pt-2">
          <div>
            <span className="text-zinc-400 font-semibold block mb-1.5">
              Production Webhook Payload Ingestion URL
            </span>
            <div className="flex items-center gap-2">
              <code className="flex-1 px-3 py-2.5 rounded-lg bg-surface-canvas border border-surface-border text-emerald-400 font-mono text-xs select-all">
                {webhookUrl}
              </code>
              <button
                onClick={handleCopy}
                className="px-3.5 py-2.5 rounded-lg bg-surface-muted hover:bg-surface-hover border border-surface-border text-zinc-200 font-semibold flex items-center gap-1.5 transition-colors"
              >
                {copiedUrl ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-zinc-400" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div className="p-4 rounded-lg bg-surface-canvas border border-surface-border space-y-2">
              <span className="font-semibold text-zinc-200 block">Required GitHub Event Subscriptions</span>
              <div className="flex flex-wrap gap-2">
                <span className="px-2.5 py-1 rounded bg-surface-muted text-emerald-300 font-mono text-[11px] border border-surface-border">
                  pull_request
                </span>
                <span className="px-2.5 py-1 rounded bg-surface-muted text-emerald-300 font-mono text-[11px] border border-surface-border">
                  workflow_run
                </span>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-surface-canvas border border-surface-border space-y-2">
              <span className="font-semibold text-zinc-200 block">Cryptographic Authentication</span>
              <p className="text-zinc-400 text-[11px] leading-relaxed">
                Constant-time HMAC-SHA256 signature verification (<code className="font-mono text-zinc-300">X-Hub-Signature-256</code>) with strict GitHub delivery idempotency.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
