"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronRight,
  Clock,
  Cloud,
  Database,
  Eye,
  Fingerprint,
  Fish,
  Flame,
  Ghost,
  GitBranch,
  KeyRound,
  Lock,
  Mail,
  Radio,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Skull,
  Sparkles,
  Terminal,
  Wand2,
  X,
  Zap,
} from "lucide-react";

// ---------------------------------------------------------------------------
// Types + mock data
// ---------------------------------------------------------------------------
type Severity = "specter" | "poltergeist" | "apparition";
type Status = "haunting" | "triaging" | "contained" | "sealing" | "resolved";
type Tone = "orange" | "purple" | "green";
type Icon = typeof Ghost;

type Alert = {
  id: string;
  title: string;
  kind: string;
  source: string;
  resource: string;
  severity: Severity;
  status: Status;
  risk: number;
  owner: string;
  lastSeen: string;
  detail: string;
  blastRadius: string[];
  evidence: string[];
  playbook: string[];
};

type AuditEvent = {
  id: string;
  time: string;
  label: string;
  detail: string;
  tone: Tone;
};

const SEVERITY: Record<
  Severity,
  {
    label: string;
    sub: string;
    Icon: Icon;
    text: string;
    bg: string;
    border: string;
    bar: string;
  }
> = {
  specter: {
    label: "SPECTER",
    sub: "Critical",
    Icon: Skull,
    text: "text-orange-300",
    bg: "bg-orange-500/10",
    border: "border-orange-500/35",
    bar: "bg-gradient-to-r from-orange-500 to-amber-300",
  },
  poltergeist: {
    label: "POLTERGEIST",
    sub: "High",
    Icon: Flame,
    text: "text-purple-300",
    bg: "bg-purple-500/10",
    border: "border-purple-500/35",
    bar: "bg-gradient-to-r from-purple-500 to-fuchsia-300",
  },
  apparition: {
    label: "APPARITION",
    sub: "Medium",
    Icon: Eye,
    text: "text-sky-300",
    bg: "bg-sky-500/10",
    border: "border-sky-500/35",
    bar: "bg-gradient-to-r from-sky-500 to-cyan-300",
  },
};

const STATUS: Record<
  Status,
  {
    label: string;
    text: string;
    bg: string;
    border: string;
    dot: string;
    progress: number;
  }
> = {
  haunting: {
    label: "HAUNTING",
    text: "text-orange-200",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    dot: "bg-orange-400",
    progress: 0,
  },
  triaging: {
    label: "TRIAGING",
    text: "text-purple-200",
    bg: "bg-purple-500/10",
    border: "border-purple-500/30",
    dot: "bg-purple-400 animate-pulse",
    progress: 2,
  },
  contained: {
    label: "CONTAINED",
    text: "text-emerald-200",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    dot: "bg-emerald-400",
    progress: 3,
  },
  sealing: {
    label: "SEALING",
    text: "text-purple-200",
    bg: "bg-purple-500/10",
    border: "border-purple-500/30",
    dot: "bg-purple-400 animate-pulse",
    progress: 4,
  },
  resolved: {
    label: "RESOLVED",
    text: "text-slate-300",
    bg: "bg-slate-500/10",
    border: "border-slate-500/30",
    dot: "bg-slate-400",
    progress: 4,
  },
};

const INITIAL_ALERTS: Alert[] = [
  {
    id: "GP-1042",
    title: "prod-deploy-key is still breathing",
    kind: "Exposed secret",
    source: "GitHub",
    resource: "AWS IAM · AKIA••••7Q2",
    severity: "specter",
    status: "haunting",
    risk: 96,
    owner: "Unassigned",
    lastSeen: "2m ago",
    detail:
      "A live access key was committed to a public repo. It can assume deploy-prod and read three S3 buckets.",
    blastRadius: ["3 repos", "1 prod role", "3 buckets"],
    evidence: ["commit a91f2c", "CloudTrail: 0 calls", "key age: 218d"],
    playbook: [
      "Scope the key + confirm exposure",
      "Check CloudTrail for recent use",
      "Rotate in Secrets Manager",
      "Disable old key + verify deny",
    ],
  },
  {
    id: "GP-1043",
    title: "MFA reset page is a doppelgänger",
    kind: "Phishing lure",
    source: "Email report",
    resource: "login-microsoft[.]secure-verify[.]io",
    severity: "poltergeist",
    status: "haunting",
    risk: 88,
    owner: "Unassigned",
    lastSeen: "6m ago",
    detail:
      "Lookalike domain + urgent “MFA reset” copy. Two lab users clicked; one submitted credentials.",
    blastRadius: ["2 users", "1 session", "0 MFA prompts"],
    evidence: ["2 clicks", "1 credential submit", "sender spoofed"],
    playbook: [
      "Quarantine sender + URL",
      "Revoke active sessions",
      "Force MFA re-enrollment",
      "Notify affected users",
    ],
  },
  {
    id: "GP-1044",
    title: "legacy-admin has no owner",
    kind: "Zombie credential",
    source: "AWS IAM",
    resource: "IAM user · last used 97d ago",
    severity: "poltergeist",
    status: "haunting",
    risk: 81,
    owner: "Unassigned",
    lastSeen: "11m ago",
    detail:
      "Console access + AdministratorAccess. The owner left the lab in June. No expiry, no MFA.",
    blastRadius: ["Admin policy", "1 console user", "All regions"],
    evidence: ["MFA disabled", "owner: departed", "age: 412d"],
    playbook: [
      "Disable console access",
      "Remove AdministratorAccess",
      "Check CloudTrail history",
      "Delete after 7-day hold",
    ],
  },
  {
    id: "GP-1045",
    title: "OAuth token outlived its app",
    kind: "Stale token",
    source: "GitHub",
    resource: "OAuth app · “lab-helper”",
    severity: "apparition",
    status: "haunting",
    risk: 64,
    owner: "Unassigned",
    lastSeen: "18m ago",
    detail:
      "Token has repo:write scope. The app was archived eight months ago and is no longer maintained.",
    blastRadius: ["2 repos", "write scope", "1 org"],
    evidence: ["app archived 8mo", "last write 41d", "2 repos"],
    playbook: [
      "Revoke the OAuth token",
      "Audit recent writes",
      "Rotate CI secrets",
      "Document the exception",
    ],
  },
];

const INITIAL_AUDIT: AuditEvent[] = [
  {
    id: "a1",
    time: "09:41",
    label: "Exposure detected",
    detail: "prod-deploy-key found in public commit",
    tone: "orange",
  },
  {
    id: "a2",
    time: "09:40",
    label: "Lure reported",
    detail: "MFA reset page reported by lab user",
    tone: "purple",
  },
  {
    id: "a3",
    time: "09:39",
    label: "Sweep complete",
    detail: "4 findings · 0 secret values shown",
    tone: "green",
  },
];

const CONNECTORS = [
  { name: "GitHub", detail: "12 repos", age: "3s", Icon: GitBranch },
  { name: "AWS IAM", detail: "us-east-1", age: "12s", Icon: Cloud },
  { name: "Phishing inbox", detail: "SES report", age: "41s", Icon: Mail },
];

const NAV_ITEMS: { label: string; Icon: Icon; badge?: string; active?: boolean }[] = [
  { label: "Threat Crypt", Icon: Ghost, badge: "4", active: true },
  { label: "NecroScan", Icon: KeyRound, badge: "1" },
  { label: "LureLens", Icon: Fish },
  { label: "Runbooks", Icon: BookOpen },
  { label: "Evidence", Icon: Database },
];

const TOAST_META: Record<
  Tone,
  { Icon: Icon; box: string; icon: string; bar: string }
> = {
  orange: {
    Icon: Radio,
    box: "border-orange-500/35 bg-[#1a1410]",
    icon: "bg-orange-500/15 text-orange-300",
    bar: "bg-orange-400",
  },
  purple: {
    Icon: Sparkles,
    box: "border-purple-500/35 bg-[#171220]",
    icon: "bg-purple-500/15 text-purple-300",
    bar: "bg-purple-400",
  },
  green: {
    Icon: CheckCircle2,
    box: "border-emerald-500/35 bg-[#101a15]",
    icon: "bg-emerald-500/15 text-emerald-300",
    bar: "bg-emerald-400",
  },
};

// ---------------------------------------------------------------------------
// Small UI primitives
// ---------------------------------------------------------------------------
function GhostMark({ className = "" }: { className?: string }) {
  return (
    <div
      className={`relative flex items-center justify-center rounded-2xl bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600 text-[#0d0f12] ghost-glow ${className}`}
    >
      <Ghost className="h-[58%] w-[58%]" strokeWidth={2.4} />
      <span className="absolute -right-1 -top-1 h-2 w-2 rounded-full bg-purple-400 shadow-[0_0_12px_rgba(168,85,247,0.9)]" />
    </div>
  );
}

function SeverityChip({ severity, compact = false }: { severity: Severity; compact?: boolean }) {
  const meta = SEVERITY[severity];
  const Icon = meta.Icon;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[9px] font-bold tracking-[0.13em] ${meta.bg} ${meta.border} ${meta.text} ${compact ? "" : "sm:text-[10px]"}`}
    >
      <Icon className={`h-3 w-3 ${severity === "specter" ? "animate-flicker" : ""}`} strokeWidth={2.2} />
      {meta.label}
    </span>
  );
}

function StatusChip({ status }: { status: Status }) {
  const meta = STATUS[status];
  const busy = status === "triaging" || status === "sealing";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[9px] font-bold tracking-[0.13em] ${meta.bg} ${meta.border} ${meta.text}`}
    >
      {busy ? (
        <RefreshCw className="h-2.5 w-2.5 animate-spin" strokeWidth={2.5} />
      ) : (
        <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
      )}
      {meta.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------
export default function GhostProtocolDashboard() {
  const [alerts, setAlerts] = useState<Alert[]>(INITIAL_ALERTS);
  const [selectedId, setSelectedId] = useState(INITIAL_ALERTS[0].id);
  const [filter, setFilter] = useState<"all" | "active" | "contained">("all");
  const [audit, setAudit] = useState<AuditEvent[]>(INITIAL_AUDIT);
  const [toast, setToast] = useState<{ title: string; body: string; tone: Tone } | null>(null);
  const [sweepAge, setSweepAge] = useState(3);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const interval = setInterval(() => setSweepAge((age) => age + 1), 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    return () => {
      timers.current.forEach((timer) => clearTimeout(timer));
      if (toastTimer.current) clearTimeout(toastTimer.current);
    };
  }, []);

  const selected = alerts.find((alert) => alert.id === selectedId) ?? alerts[0];
  const severity = SEVERITY[selected.severity];
  const status = STATUS[selected.status];

  const filteredAlerts = useMemo(() => {
    if (filter === "active") {
      return alerts.filter((alert) =>
        ["haunting", "triaging", "sealing"].includes(alert.status),
      );
    }
    if (filter === "contained") {
      return alerts.filter((alert) => ["contained", "resolved"].includes(alert.status));
    }
    return alerts;
  }, [alerts, filter]);

  const activeCount = alerts.filter((alert) =>
    ["haunting", "triaging", "sealing"].includes(alert.status),
  ).length;
  const containedCount = alerts.filter((alert) =>
    ["contained", "resolved"].includes(alert.status),
  ).length;
  const peakRisk = Math.max(...alerts.map((alert) => alert.risk));

  const stats = [
    {
      label: "Active haunts",
      value: String(activeCount).padStart(2, "0"),
      hint: "need a human",
      Icon: Flame,
      accent: "text-orange-300",
      line: "from-orange-500/70",
    },
    {
      label: "Contained",
      value: String(containedCount).padStart(2, "0"),
      hint: "verified fixes",
      Icon: ShieldCheck,
      accent: "text-emerald-300",
      line: "from-emerald-400/70",
    },
    {
      label: "Peak risk",
      value: String(peakRisk),
      hint: "of 100",
      Icon: Activity,
      accent: "text-purple-300",
      line: "from-purple-500/70",
    },
    {
      label: "Secrets shown",
      value: "00",
      hint: "metadata only",
      Icon: Lock,
      accent: "text-slate-300",
      line: "from-slate-500/70",
    },
  ];

  const filters = [
    { id: "all" as const, label: "All", count: alerts.length },
    { id: "active" as const, label: "Haunting", count: activeCount },
    { id: "contained" as const, label: "Contained", count: containedCount },
  ];

  function schedule(action: () => void, delay: number) {
    const timer = setTimeout(action, delay);
    timers.current.push(timer);
  }

  function stamp() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function flashToast(title: string, body: string, tone: Tone) {
    setToast({ title, body, tone });
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 4600);
  }

  function addAudit(label: string, detail: string, tone: Tone) {
    setAudit((events) => [
      {
        id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        time: stamp(),
        label,
        detail,
        tone,
      },
      ...events,
    ]);
  }

  function triageAlert(id: string) {
    const alert = alerts.find((item) => item.id === id);
    if (!alert || alert.status !== "haunting") return;

    setSelectedId(id);
    setAlerts((current) =>
      current.map((item) =>
        item.id === id ? { ...item, status: "triaging", owner: "You" } : item,
      ),
    );
    addAudit("Triage started", `${id} moved to TRIAGING`, "purple");
    flashToast(
      "Triage in progress",
      `Scoping ${id}. Secret values stay in the vault; only metadata is shown.`,
      "purple",
    );

    schedule(() => {
      setAlerts((current) =>
        current.map((item) => (item.id === id ? { ...item, status: "contained" } : item)),
      );
      addAudit("Contained", `Old credential denied · ${id}`, "green");
      flashToast(
        "Secret contained",
        `${id} is quarantined. Verify the old credential is denied, then seal the evidence.`,
        "green",
      );
    }, 1700);
  }

  function sealExorcism(id: string) {
    const alert = alerts.find((item) => item.id === id);
    if (!alert || alert.status !== "contained") return;

    setAlerts((current) =>
      current.map((item) => (item.id === id ? { ...item, status: "sealing" } : item)),
    );
    addAudit("Sealing evidence", `${id} · signed audit packet`, "purple");
    flashToast("Sealing evidence", "Writing the signed audit packet and verify receipt…", "purple");

    schedule(() => {
      setAlerts((current) =>
        current.map((item) => (item.id === id ? { ...item, status: "resolved" } : item)),
      );
      addAudit("Resolved", `${id} · old credential denied · evidence sealed`, "green");
      flashToast(
        "Exorcism complete",
        `${id} is resolved. The audit packet is sealed and ready for a judge to inspect.`,
        "green",
      );
    }, 1500);
  }

  function runSweep() {
    setSweepAge(0);
    addAudit("Sweep complete", "4 findings · demo tenant", "orange");
    flashToast(
      "Sweep complete",
      "4 findings, 0 secret values shown. The demo data is deterministic and judge-safe.",
      "orange",
    );
  }

  const canTriage = selected.status === "haunting";
  const canSeal = selected.status === "contained";

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0D0F12] text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-grid opacity-70" />
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_74%_8%,rgba(168,85,247,0.12),transparent_34rem),radial-gradient(circle_at_16%_92%,rgba(249,115,22,0.09),transparent_30rem)]" />
      <div className="scanlines pointer-events-none fixed inset-0 z-[1] opacity-40" />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-[1600px]">
        {/* Sidebar */}
        <aside className="hidden w-[238px] shrink-0 border-r border-white/[0.06] bg-[#0a0c10]/80 px-4 py-5 lg:flex lg:flex-col">
          <div className="flex items-center gap-3">
            <GhostMark className="h-10 w-10 animate-float" />
            <div>
              <p className="font-display text-[13px] font-bold tracking-[0.16em] text-white">
                GHOSTPROTOCOL
              </p>
              <p className="mt-0.5 font-mono text-[8px] uppercase tracking-[0.2em] text-slate-500">
                Threat exorcism unit
              </p>
            </div>
          </div>

          <div className="mt-9 font-mono text-[9px] font-bold uppercase tracking-[0.2em] text-slate-600">
            Workspace
          </div>
          <nav className="mt-2 space-y-1">
            {NAV_ITEMS.map(({ label, Icon, badge, active }) => (
              <button
                key={label}
                type="button"
                className={`group flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left text-[12px] transition ${
                  active
                    ? "border-orange-500/20 bg-orange-500/10 text-orange-200"
                    : "border-transparent text-slate-400 hover:border-white/[0.06] hover:bg-white/[0.03] hover:text-slate-200"
                }`}
              >
                <Icon
                  className={`h-4 w-4 ${active ? "text-orange-300" : "text-slate-500 group-hover:text-slate-300"}`}
                  strokeWidth={1.9}
                />
                <span className="flex-1 font-medium">{label}</span>
                {badge && (
                  <span className="rounded-md bg-white/[0.06] px-1.5 py-0.5 font-mono text-[9px] text-slate-400">
                    {badge}
                  </span>
                )}
              </button>
            ))}
          </nav>

          <div className="mt-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-3">
            <div className="flex items-center gap-2 font-mono text-[9px] uppercase tracking-[0.18em] text-slate-500">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              Demo tenant
            </div>
            <p className="mt-2 text-[11px] leading-relaxed text-slate-400">
              AWS <span className="font-mono text-slate-300">us-east-1</span>
              <br />
              No live secrets. No destructive actions.
            </p>
          </div>

          <div className="mt-auto flex items-center gap-2 border-t border-white/[0.06] pt-4 text-[10px] text-slate-500">
            <ShieldAlert className="h-3.5 w-3.5 text-purple-400" />
            <span>Human approval required</span>
          </div>
        </aside>

        {/* Main */}
        <main className="min-w-0 flex-1 px-4 py-5 sm:px-6 lg:px-8 lg:py-7">
          {/* Mobile brand */}
          <div className="mb-5 flex items-center gap-3 lg:hidden">
            <GhostMark className="h-9 w-9" />
            <div>
              <p className="font-display text-xs font-bold tracking-[0.16em]">GHOSTPROTOCOL</p>
              <p className="font-mono text-[8px] uppercase tracking-[0.18em] text-slate-500">
                Threat exorcism unit
              </p>
            </div>
          </div>

          {/* Header */}
          <header className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <div className="flex items-center gap-2 font-mono text-[9px] font-bold uppercase tracking-[0.2em] text-purple-300">
                <span className="h-px w-6 bg-purple-400/60" />
                Workspace / Threat Crypt
              </div>
              <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Threat <span className="text-glow-orange text-orange-400">Crypt</span>
              </h1>
              <p className="mt-1 max-w-xl text-sm text-slate-400">
                Every alert has a pulse. Every fix leaves a trail.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="inline-flex items-center gap-2 rounded-xl border border-emerald-500/25 bg-emerald-500/[0.07] px-3 py-2 font-mono text-[9px] font-bold uppercase tracking-[0.18em] text-emerald-300">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                Live demo
              </div>
              <button
                type="button"
                onClick={runSweep}
                className="group inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-xs font-semibold text-slate-300 transition hover:border-orange-500/30 hover:bg-orange-500/[0.06] hover:text-orange-200"
              >
                <RefreshCw className="h-3.5 w-3.5 text-orange-400 transition group-hover:rotate-180" />
                Sweep now
                <span className="font-mono text-[9px] text-slate-500">{sweepAge}s</span>
              </button>
              <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-purple-500/25 bg-purple-500/10 font-display text-xs font-bold text-purple-200">
                GP
              </div>
            </div>
          </header>

          {/* Stats */}
          <section className="mt-5 grid grid-cols-2 gap-3 xl:grid-cols-4">
            {stats.map(({ label, value, hint, Icon, accent, line }) => (
              <div
                key={label}
                className="group relative overflow-hidden rounded-2xl border border-white/[0.07] bg-[#11151a]/80 p-4"
              >
                <div
                  className={`absolute left-0 top-0 h-px w-full bg-gradient-to-r ${line} to-transparent opacity-70`}
                />
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-mono text-[9px] font-bold uppercase tracking-[0.18em] text-slate-500">
                      {label}
                    </p>
                    <p className={`mt-1 font-display text-3xl font-bold leading-none ${accent}`}>
                      {value}
                    </p>
                    <p className="mt-1.5 text-[10px] text-slate-500">{hint}</p>
                  </div>
                  <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] p-2">
                    <Icon className={`h-4 w-4 ${accent}`} strokeWidth={1.9} />
                  </div>
                </div>
              </div>
            ))}
          </section>

          {/* Main grid */}
          <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.15fr)_minmax(390px,0.85fr)]">
            {/* Alert queue */}
            <section className="flex flex-col overflow-hidden rounded-2xl border border-white/[0.07] bg-[#11151a]/80">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.06] px-4 py-3.5">
                <div>
                  <h2 className="flex items-center gap-2 font-display text-sm font-bold tracking-wide text-white">
                    <Radio className="h-4 w-4 text-orange-400" />
                    Active alerts
                  </h2>
                  <p className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.16em] text-slate-500">
                    Ranked by blast radius · {filteredAlerts.length} visible
                  </p>
                </div>
                <div className="flex rounded-lg border border-white/[0.07] bg-black/20 p-0.5">
                  {filters.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setFilter(item.id)}
                      aria-pressed={filter === item.id}
                      className={`rounded-md px-2.5 py-1.5 font-mono text-[9px] font-bold uppercase tracking-[0.12em] transition ${
                        filter === item.id
                          ? "bg-white/[0.08] text-white"
                          : "text-slate-500 hover:text-slate-300"
                      }`}
                    >
                      {item.label}
                      <span className="ml-1.5 text-slate-600">{item.count}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="relative h-px overflow-hidden bg-white/[0.04]">
                <div className="animate-scan-sweep absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-orange-400/80 to-transparent" />
              </div>

              <div className="divide-y divide-white/[0.05]">
                {filteredAlerts.map((alert) => {
                  const isSelected = alert.id === selected.id;
                  const sev = SEVERITY[alert.severity];
                  const stat = STATUS[alert.status];
                  const SevIcon = sev.Icon;
                  return (
                    <button
                      key={alert.id}
                      type="button"
                      onClick={() => setSelectedId(alert.id)}
                      aria-pressed={isSelected}
                      className={`group relative flex w-full items-start gap-3 px-4 py-3.5 text-left transition ${
                        isSelected
                          ? "bg-orange-500/[0.055]"
                          : "hover:bg-white/[0.025]"
                      }`}
                    >
                      {isSelected && (
                        <span className="absolute inset-y-2 left-0 w-0.5 rounded-full bg-orange-400" />
                      )}
                      <div
                        className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border ${sev.bg} ${sev.border}`}
                      >
                        <SevIcon
                          className={`h-4 w-4 ${sev.text} ${alert.severity === "specter" ? "animate-flicker" : ""}`}
                          strokeWidth={2}
                        />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-1.5">
                          <SeverityChip severity={alert.severity} compact />
                          <StatusChip status={alert.status} />
                          <span className="ml-auto font-display text-sm font-bold text-white">
                            {alert.risk}
                          </span>
                        </div>
                        <h3 className="mt-1.5 truncate text-[13px] font-semibold text-slate-100">
                          {alert.title}
                        </h3>
                        <p className="mt-0.5 truncate font-mono text-[9px] text-slate-500">
                          {alert.id} · {alert.source} · {alert.resource} · {alert.lastSeen}
                        </p>
                      </div>

                      <ChevronRight
                        className={`mt-2 h-4 w-4 shrink-0 transition ${
                          isSelected
                            ? "text-orange-400"
                            : "text-slate-600 group-hover:translate-x-0.5 group-hover:text-slate-400"
                        }`}
                      />
                    </button>
                  );
                })}
              </div>

              <div className="mt-auto border-t border-white/[0.06] p-4">
                <div className="flex items-start gap-3 rounded-xl border border-dashed border-orange-500/25 bg-orange-500/[0.045] p-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-orange-500/10 text-orange-300">
                    <Ghost className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-mono text-[8px] font-bold uppercase tracking-[0.18em] text-orange-300">
                      Highest leverage
                    </p>
                    <p className="mt-1 text-[11px] leading-relaxed text-slate-400">
                      Rotate <span className="font-mono text-slate-200">prod-deploy-key</span> first — 96 risk
                      and a production blast radius. 11 low-confidence signals were suppressed.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setFilter("all");
                      setSelectedId("GP-1042");
                    }}
                    className="shrink-0 rounded-lg border border-orange-500/25 bg-orange-500/10 px-2.5 py-1.5 font-mono text-[9px] font-bold uppercase tracking-[0.12em] text-orange-200 transition hover:bg-orange-500/20"
                  >
                    Focus
                  </button>
                </div>
              </div>
            </section>

            {/* Detail */}
            <section className="flex flex-col rounded-2xl border border-white/[0.07] bg-[#11151a]/80">
              <div className="flex items-start justify-between gap-3 border-b border-white/[0.06] px-4 py-3.5">
                <div>
                  <p className="font-mono text-[9px] font-bold uppercase tracking-[0.18em] text-slate-500">
                    Selected signal
                  </p>
                  <p className="mt-1 font-mono text-[10px] text-slate-400">{selected.id}</p>
                </div>
                <div className="text-right">
                  <p className="font-mono text-[8px] font-bold uppercase tracking-[0.18em] text-slate-500">
                    Risk
                  </p>
                  <p className={`font-display text-2xl font-bold leading-none ${severity.text}`}>
                    {selected.risk}
                    <span className="text-xs text-slate-600">/100</span>
                  </p>
                </div>
              </div>

              <div className="flex-1 px-4 py-4">
                <div className="flex flex-wrap items-center gap-2">
                  <SeverityChip severity={selected.severity} />
                  <StatusChip status={selected.status} />
                  <span className="rounded-full border border-white/[0.08] bg-white/[0.03] px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.12em] text-slate-400">
                    {selected.kind}
                  </span>
                </div>

                <h2 className="mt-3 text-balance font-display text-xl font-bold leading-tight text-white">
                  {selected.title}
                </h2>
                <p className="mt-1 break-all font-mono text-[10px] text-slate-500">{selected.resource}</p>

                <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${severity.bar}`}
                    style={{ width: `${selected.risk}%` }}
                  />
                </div>

                <p className="mt-4 text-[12px] leading-relaxed text-slate-400">{selected.detail}</p>

                <div className="mt-4">
                  <p className="font-mono text-[9px] font-bold uppercase tracking-[0.18em] text-slate-500">
                    Blast radius
                  </p>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {selected.blastRadius.map((item) => (
                      <span
                        key={item}
                        className="rounded-lg border border-white/[0.07] bg-white/[0.03] px-2 py-1 font-mono text-[9px] text-slate-300"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4">
                  <div className="flex items-center justify-between">
                    <p className="font-mono text-[9px] font-bold uppercase tracking-[0.18em] text-slate-500">
                      Exorcism playbook
                    </p>
                    <p className="font-mono text-[9px] text-slate-600">
                      {status.progress}/{selected.playbook.length}
                    </p>
                  </div>
                  <div className="mt-2 space-y-1.5">
                    {selected.playbook.map((step, index) => {
                      const done = index < status.progress;
                      return (
                        <div key={step} className="flex items-center gap-2.5 text-[11px]">
                          <span
                            className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full border font-mono text-[8px] ${
                              done
                                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                                : "border-white/10 bg-white/[0.02] text-slate-600"
                            }`}
                          >
                            {done ? <Check className="h-2.5 w-2.5" strokeWidth={3} /> : index + 1}
                          </span>
                          <span className={done ? "text-slate-300" : "text-slate-500"}>{step}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="mt-4 rounded-xl border border-white/[0.06] bg-black/20 p-3">
                  <div className="flex items-center gap-2">
                    <Terminal className="h-3.5 w-3.5 text-purple-400" />
                    <p className="font-mono text-[9px] font-bold uppercase tracking-[0.16em] text-slate-500">
                      Evidence trail
                    </p>
                    <span className="ml-auto rounded bg-emerald-500/10 px-1.5 py-0.5 font-mono text-[8px] text-emerald-300">
                      signed
                    </span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {selected.evidence.map((item) => (
                      <span
                        key={item}
                        className="rounded border border-white/[0.06] bg-white/[0.02] px-1.5 py-0.5 font-mono text-[8px] text-slate-500"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      if (canTriage) triageAlert(selected.id);
                      else if (canSeal) sealExorcism(selected.id);
                    }}
                    disabled={!canTriage && !canSeal}
                    className={`group inline-flex flex-1 items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-xs font-bold transition ${
                      canTriage
                        ? "bg-orange-500 text-[#160d06] shadow-[0_0_28px_-8px_rgba(249,115,22,0.8)] hover:bg-orange-400"
                        : canSeal
                          ? "bg-emerald-500 text-[#06140c] shadow-[0_0_28px_-8px_rgba(34,197,94,0.7)] hover:bg-emerald-400"
                          : "cursor-not-allowed border border-white/[0.06] bg-white/[0.03] text-slate-500"
                    }`}
                  >
                    {selected.status === "haunting" && (
                      <>
                        <Zap className="h-3.5 w-3.5 transition group-hover:scale-110" />
                        Triage secret
                      </>
                    )}
                    {selected.status === "triaging" && (
                      <>
                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        Triaging…
                      </>
                    )}
                    {selected.status === "contained" && (
                      <>
                        <Wand2 className="h-3.5 w-3.5 transition group-hover:rotate-12" />
                        Seal exorcism
                      </>
                    )}
                    {selected.status === "sealing" && (
                      <>
                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        Sealing evidence…
                      </>
                    )}
                    {selected.status === "resolved" && (
                      <>
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Resolved
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() =>
                      flashToast(
                        "Evidence packet",
                        `${selected.id} · signed JSON + CSV preview (demo mode).`,
                        "purple",
                      )
                    }
                    className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-white/[0.08] bg-white/[0.02] px-3 py-2.5 text-xs font-semibold text-slate-400 transition hover:border-purple-500/30 hover:text-purple-200"
                  >
                    <ArrowUpRight className="h-3.5 w-3.5" />
                    Open
                  </button>
                </div>

                <p className="mt-2.5 text-center font-mono text-[8px] uppercase tracking-[0.12em] text-slate-600">
                  No secret values are rendered in this view.
                </p>
              </div>
            </section>
          </div>

          {/* Audit + connectors */}
          <section className="mt-5 grid gap-4 lg:grid-cols-2">
            <div className="rounded-2xl border border-white/[0.07] bg-[#11151a]/80 p-4">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 font-display text-xs font-bold uppercase tracking-[0.16em] text-white">
                  <Clock className="h-3.5 w-3.5 text-purple-400" />
                  Audit séance
                </h2>
                <span className="rounded-full border border-emerald-500/20 bg-emerald-500/[0.06] px-2 py-0.5 font-mono text-[8px] uppercase tracking-[0.12em] text-emerald-300">
                  Append-only
                </span>
              </div>
              <div className="mt-3 space-y-2">
                {audit.slice(0, 3).map((event) => (
                  <div key={event.id} className="flex items-start gap-2.5">
                    <span
                      className={`mt-1 h-1.5 w-1.5 shrink-0 rounded-full ${
                        event.tone === "orange"
                          ? "bg-orange-400"
                          : event.tone === "purple"
                            ? "bg-purple-400"
                            : "bg-emerald-400"
                      }`}
                    />
                    <p className="min-w-0 flex-1 truncate text-[10px] text-slate-400">
                      <span className="font-mono text-[9px] text-slate-600">{event.time}</span>{" "}
                      <span className="font-semibold text-slate-300">{event.label}</span> · {event.detail}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-white/[0.07] bg-[#11151a]/80 p-4">
              <div className="flex items-center justify-between">
                <h2 className="flex items-center gap-2 font-display text-xs font-bold uppercase tracking-[0.16em] text-white">
                  <Fingerprint className="h-3.5 w-3.5 text-orange-400" />
                  Connector coverage
                </h2>
                <span className="font-mono text-[8px] uppercase tracking-[0.12em] text-slate-600">
                  3 / 3 online
                </span>
              </div>
              <div className="mt-3 grid gap-2 sm:grid-cols-3">
                {CONNECTORS.map(({ name, detail, age, Icon }) => (
                  <div
                    key={name}
                    className="rounded-lg border border-white/[0.06] bg-white/[0.02] px-2.5 py-2"
                  >
                    <div className="flex items-center gap-1.5">
                      <Icon className="h-3 w-3 text-slate-400" />
                      <span className="truncate text-[10px] font-semibold text-slate-300">{name}</span>
                      <span className="ml-auto h-1.5 w-1.5 rounded-full bg-emerald-400" />
                    </div>
                    <p className="mt-1 truncate font-mono text-[8px] text-slate-600">
                      {detail} · {age} ago
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <footer className="mt-5 flex flex-wrap items-center justify-between gap-2 border-t border-white/[0.05] pt-3 font-mono text-[8px] uppercase tracking-[0.14em] text-slate-600">
            <span>GhostProtocol · Demo workspace · No live secrets</span>
            <span className="flex items-center gap-1.5">
              <ShieldAlert className="h-3 w-3 text-purple-500" />
              Human approval required for destructive actions
            </span>
          </footer>
        </main>
      </div>

      {/* Toast */}
      {toast && (
        <div
          role="status"
          aria-live="polite"
          className={`animate-toast-in fixed bottom-5 right-5 z-50 w-[min(390px,calc(100vw-2.5rem))] overflow-hidden rounded-2xl border p-4 shadow-2xl backdrop-blur-xl ${TOAST_META[toast.tone].box}`}
        >
          <div className={`absolute inset-y-0 left-0 w-0.5 ${TOAST_META[toast.tone].bar}`} />
          <div className="flex items-start gap-3">
            <div
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl ${TOAST_META[toast.tone].icon}`}
            >
              {(() => {
                const ToastIcon = TOAST_META[toast.tone].Icon;
                return <ToastIcon className="h-4 w-4" />;
              })()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-white">{toast.title}</p>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-400">{toast.body}</p>
            </div>
            <button
              type="button"
              onClick={() => setToast(null)}
              aria-label="Dismiss notification"
              className="rounded-lg p-1 text-slate-500 transition hover:bg-white/[0.06] hover:text-slate-300"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
