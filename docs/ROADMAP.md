[![English](https://img.shields.io/badge/English-Roadmap-blue)](ROADMAP.md)
[![简体中文](https://img.shields.io/badge/简体中文-路线图-green)](ROADMAP.zh-CN.md)

# Roadmap

> Per-release details in [CHANGELOG.md](../CHANGELOG.md). Configuration reference in [`.env.example`](../.env.example) and [`job.example.yaml`](../examples/job.example.yaml).

## Completed

| Version | Key Themes |
|---------|-------------|
| v0.1.x | Core Pipeline / CLI / LLM script / Edge-TTS / SRT / MoviePy rendering / TTS cache / CI |
| v0.2.x | Scene & Media / research agent / WhisperX alignment / scene detection / clip matching / BGM / graceful degradation |
| v0.3.x | Platform & Workflow / YAML job config / multi-language subtitles / Gradio WebUI (superseded) |
| v0.4.x | TTS Abstraction & Infrastructure / TTS provider abstraction / config overhaul / FastAPI + React WebUI / render quality / match intelligence / effect portfolio / contract layer |
| v0.5.x | Ecosystem / Plugin API / SDK freeze / plugin discovery / VLM vision / narrative presets / scene filtering / WebUI split / QA dashboard |
| v0.6.x | Task Queue & Remote Inference / async jobs / persistence / cancel / progress / retry / REST API server / worker daemon / artifact mgmt / remote proxies |
| v0.7.x | Output Experience / GPU encoding / cost tracking / preview mode / scene transitions / text animation / multi-track audio / security hardening |
| v0.8.x | Service Deployment Basics / API key auth / video_format rename / render templates / exception narrowing / lint toolchain / queue deadlock fix |
| v0.9.x | Reliability / Batch / Docs / circuit breaker / checkpoints / graceful shutdown / retry policy / batch jobs / cron / DLQ / distributed rendering / sanitization / SAST / coverage gate / integration tests / i18n / voice map / tutorial / ADR / migration guide |
| v1.0.x | **Stable Release** / API freeze / stability guarantees / release checklist / final documentation pass / long-term support policy |
| v1.1.x | FunASR Chinese ASR / `mn doctor` / QA slideshow & black-frame detection / EmotionTrack / SQLite task store / visual-embedding match skeleton / timeline_export plugin / compliance (edge-tts + TMDB) / 90% coverage gate |

`CONTRACT_VERSION` (current): `(1, 0, 0)` (unchanged in v1.1 — no new contract exports)

---

## Current & Planned

> **Planning principle**: Alternate user-visible improvements with infrastructure work. v1.0 target users: local CLI creators + optional single-tenant service deployment. Engine positioning for the 1.x series: a reliable single-node / lightweight-service video engine — linear pipeline + resumable checkpoints + explicit artifact contract + resource-bounded rendering. Distributed workflow engines (Temporal / Celery) stay deferred until measured queue latency, render duration, recovery success rate, and duplicate provider calls justify the migration cost.

### v1.2 — Engine Reliability & Observability (next)

> Theme: close the loop on render reliability, crash recovery, and per-step observability before any DAG or distributed-workflow work. All work lands under the existing quality gates (90% coverage, mypy, ruff, SAST). No contract surface change expected — `CONTRACT_VERSION` stays `(1, 0, 0)`.

#### Rendering & queue stability

- Terminable subprocesses — deadline + process-group terminate/kill for the MoviePy main encode and sidechain BGM mix (mux is already bounded); PID and timeout reason logged; partial artifacts cleaned up.
- Atomic artifact publication — render and clip outputs written to a task temp path first, atomically replaced into the final path after QA passes; failure removes partials.
- Codec config unification — `render_video_codec` / `render_encoder` honored consistently across final render and clip export (fixes a dead config path).
- Portrait QA fix — `1080x1920` output no longer misjudged by width/height assumptions in deliverable QA.
- Crash-recovery closure — startup scan reclaims orphaned `RUNNING` tasks (marked recoverable or failed) instead of requiring manual cleanup; checkpoint restore loop verified end-to-end.

#### Service hardening

- Non-loopback auth by default — anonymous task submission and artifact download rejected on externally bound deployments.
- Task admission limits — caps on submission size, concurrency, per-task duration, and estimated artifact size.

#### Observability & recovery trust

- Structured step logs — task ID, step, attempt, duration, provider, cache hit, PID, artifact size, and error class for every step.
- Execution manifest — inputs, config, providers, per-step timing, cache hits, checksums, and QA results recorded per deliverable.
- Checkpoint fingerprints — input/config/provider fingerprint + artifact manifest + schema version; stale checkpoints invalidated on restore.
- OpenTelemetry tracing (or equivalent structured trace) — task as trace, step/provider/subprocess as span, with latency, retry, cache, and cost attribution.
- Generation dry-run — research / script / scene planning only, no TTS or FFmpeg calls (separate from the existing cleanup dry-run).
- Provider call hygiene — unified retry/backoff adoption across LLM / VLM / TTS / TMDB with per-provider budgets and idempotency keys against duplicate billing.

#### Efficiency & cost

- Hardware encoding productization — unified FFmpeg binary + device detection, capability cache, fallback-reason reporting, and benchmark.
- Prompt/script cache — keyed by normalized topic / style / language / prompt-template version / model, with hit-source attribution.
- TTS cache accounting — cross-task hit rate, reference counting, and auditable origin.
- Resource-aware admission — temp-disk / CPU / GPU / duration / resolution checks before render starts; GPU and CPU queues separated.

### v1.3 — Workflow Semantics & Product Foundation

> Theme: prepare selective rerun and product-grade service semantics while keeping linear execution. Expected `CONTRACT_VERSION` MINOR bump (new contract exports).

- Selective rerun — rerun only `generate_voice` or `render_video`; downstream steps invalidated automatically, no re-research.
- Linear-compatible DAG contract — explicit step inputs / outputs / artifact keys / dependency declarations with a linear adapter (no parallelism yet).
- Versioned deliverable manifest — `deliverable_manifest.json` declaring MP4 / audio / SRT / script / clips / timeline / checksums / compatibility version.
- Dashboard contract — stable manifest / API surface for the external `movie-narrator-web` UI.
- Principal & tenant foundation — tenant/principal propagated through task, artifact, cache reference, audit, and lifecycle; every route authorized.
- Plans & entitlements — max duration / resolution / watermark / GPU & provider access / output format / TTL modeling.
- Webhook MVP — signed events, delivery retry, idempotent event IDs, delivery records (replaces pure polling).
- Timeline export hardening — `timeline_export_backend` accepted by the core whitelist with integration tests.
- Reference media input contract — `reference_media[]` entries with video/image kind, usage, license source, and style features; image-reference style hints via the VLM provider.

### Long-term — Architecture Outgrowths (demand-driven)

Commitments are made only against real metrics (queue latency, render duration, recovery success rate, duplicate provider calls, cache hit rate, disk/GPU utilization):

- Temporal pilot (Celery as fallback) — only when multi-node workers, durable timers, heartbeats, manual approval steps, or replayable execution history become actual requirements.
- HDR / 4K pipeline — 10-bit pix_fmt, profile, color primaries/transfer/mastering metadata, VRAM budgeting, and a 4K QA baseline (not just a `video_sizes` bump).
- Optional soft subtitles — `subtitle_delivery=burned|sidecar|muxed` with `mov_text` compatibility testing.
- Extended timeline adapters — Premiere XML beyond the current OTIO + Jianying support.
- Media cache pool — content-hash + TTL + license-metadata cache for future external stock-footage integration.

### Community & SaaS Ecosystem (demand-driven)

The following remain out of the v1.2/v1.3 scope and will be prioritized only when community feedback and enterprise demand materialize:

- Community preset sharing — `mn presets install <url>` mechanism (depends on stable API after contract freeze)
- Helm chart / K8s deployment templates — for teams actually running on Kubernetes
- Full multi-tenant isolation — tenant-scoped task storage and artifacts (foundation laid in v1.3)
- OAuth2 authentication — full auth flow for web clients (only if SaaS demand materializes)
- Token bucket rate limiting — per-tenant request throttling (only if multi-user deployment demand materializes)
