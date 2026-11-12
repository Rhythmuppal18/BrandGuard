import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import confetti from "canvas-confetti";
import {
  ShieldCheck, AlertTriangle, CheckCircle2, FileText, Upload, RefreshCw,
  Check, X, Award, BookOpen, Activity, Sparkles, Layers, Wand2, Download,
  Sliders, SplitSquareVertical, FileCheck, ArrowRight, UserCheck, Eye, EyeOff,
  Edit3, HelpCircle, Plus, RotateCcw, Info, Lock, Unlock, Zap, ShieldAlert,
  Scale, Key, History, AlertOctagon, CheckSquare
} from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || (window.location.port === "5173" ? "http://127.0.0.1:8000/api" : "/api");

function App() {
  const [activeTab, setActiveTab] = useState("studio");
  const [currentRole, setCurrentRole] = useState("Creator");

  // Studio state
  const [title, setTitle] = useState("Q4 Product Launch Announcement");
  const [content, setContent] = useState("");
  const [contentType, setContentType] = useState("social_post");
  const [scenarios, setScenarios] = useState([]);
  const [reviewResult, setReviewResult] = useState(null);
  const [viewMode, setViewMode] = useState("split"); // "split", "diff", "rules"
  const [editorMode, setEditorMode] = useState("editor"); // "editor", "inspector"
  const [selectedFindingId, setSelectedFindingId] = useState(null);
  const [showGuide, setShowGuide] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [reviewerComment, setReviewerComment] = useState("");
  const [rejectionModal, setRejectionModal] = useState(null);
  const [rejectionReason, setRejectionReason] = useState("");

  // Pillar 1: Multimodal Visual Engine state
  const [visualSamples, setVisualSamples] = useState([]);
  const [selectedVisualSample, setSelectedVisualSample] = useState(null);
  const [visualAssetType, setVisualAssetType] = useState("banner");
  const [visualAnalysis, setVisualAnalysis] = useState(null);
  const [visualBusy, setVisualBusy] = useState(false);
  const [visualActiveSubtab, setVisualActiveSubtab] = useState("palette");

  // Pillar 2: Enterprise Privacy Shield state
  const [privacyText, setPrivacyText] = useState(
    "Internal Board Memo: Contact CFO Dr. Sarah Jenkins at s.jenkins@apexpay.com or direct line +1 (555) 234-8901.\n" +
    "DO NOT leak private production token sk_test_99887766554433221100aabbcc on internal Slack channels.\n" +
    "Preliminary Q3 audit: ApexPay achieved $48.5M ARR with high-value merchant escrow account 4111-2222-3333-4444.\n" +
    "Internal deployment cluster gateway resides at 10.0.4.12:8443."
  );
  const [privacyAirGapped, setPrivacyAirGapped] = useState(true);
  const [privacyResult, setPrivacyResult] = useState(null);
  const [privacyRestored, setPrivacyRestored] = useState(false);
  const [privacyBusy, setPrivacyBusy] = useState(false);
  const [disclosureLedger, setDisclosureLedger] = useState([]);

  // Pillar 3: Continuous Guideline Health & Self-Healing state
  const [governanceMetrics, setGovernanceMetrics] = useState(null);
  const [disputeStats, setDisputeStats] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [governanceBusy, setGovernanceBusy] = useState(false);
  const [governanceTab, setGovernanceTab] = useState("conflicts");
  const [disputeModal, setDisputeModal] = useState(null);
  const [disputeReasonInput, setDisputeReasonInput] = useState("");

  // Brand Hub & Custom Management state
  const [brandKit, setBrandKit] = useState(null);
  const [newTermModal, setNewTermModal] = useState(false);
  const [newTermForm, setNewTermForm] = useState({ term: "", suggested_replacement: "", reason: "" });
  const [newFactModal, setNewFactModal] = useState(false);
  const [newFactForm, setNewFactForm] = useState({ claim_key: "", statement: "", source_document: "", expires_at: "" });

  // Benchmark state
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [benchmarkBusy, setBenchmarkBusy] = useState(false);
  const [commitments, setCommitments] = useState(null);

  useEffect(() => {
    fetchScenarios();
    fetchBrandKit();
    fetchCommitments();
    fetchVisualSamples();
    fetchPrivacyLedger();
    fetchGovernanceData();
  }, []);

  async function fetchScenarios() {
    try {
      const res = await fetch(`${API_BASE}/scenarios`);
      if (res.ok) {
        const data = await res.json();
        setScenarios(data);
        if (data.length > 0 && !content) {
          loadScenario(data[0]);
        }
      }
    } catch (e) {
      console.warn("API connecting...", e);
    }
  }

  async function fetchBrandKit() {
    try {
      const res = await fetch(`${API_BASE}/brand`);
      if (res.ok) setBrandKit(await res.json());
    } catch (e) {
      console.warn(e);
    }
  }

  async function fetchCommitments() {
    try {
      const res = await fetch(`${API_BASE}/round3-commitments`);
      if (res.ok) setCommitments(await res.json());
    } catch (e) {
      console.warn(e);
    }
  }

  // --- PILLAR 1: VISUAL ENGINE HANDLERS ---
  async function fetchVisualSamples() {
    try {
      const res = await fetch(`${API_BASE}/visual/samples`);
      if (res.ok) {
        const data = await res.json();
        setVisualSamples(data.samples || []);
        if (data.samples && data.samples.length > 0 && !visualAnalysis) {
          inspectVisualAsset(data.samples[0].image_data, data.samples[0].title, "banner");
          setSelectedVisualSample(data.samples[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function inspectVisualAsset(imageBase64, filename, assetType) {
    setVisualBusy(true);
    try {
      const res = await fetch(`${API_BASE}/visual/inspect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_base64: imageBase64,
          filename: filename || "asset.png",
          asset_type: assetType || visualAssetType
        })
      });
      if (res.ok) {
        const data = await res.json();
        setVisualAnalysis(data);
        if (data.overall_visual_score >= 85) triggerConfetti();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setVisualBusy(false);
    }
  }

  function handleCustomImageUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const b64 = reader.result;
      setSelectedVisualSample("custom");
      inspectVisualAsset(b64, file.name, visualAssetType);
    };
    reader.readAsDataURL(file);
  }

  // --- PILLAR 2: PRIVACY SHIELD HANDLERS ---
  async function runPrivacyScan(textToScan, airGapped) {
    if (!textToScan) return;
    setPrivacyBusy(true);
    setPrivacyRestored(false);
    try {
      const res = await fetch(`${API_BASE}/privacy/scan-redact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textToScan,
          air_gapped_mode: airGapped !== undefined ? airGapped : privacyAirGapped
        })
      });
      if (res.ok) {
        const data = await res.json();
        setPrivacyResult(data.scan_result);
        fetchPrivacyLedger();
        if (data.scan_result.total_redactions > 0) triggerConfetti();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setPrivacyBusy(false);
    }
  }

  async function restorePrivacyText() {
    if (!privacyResult) return;
    if (privacyRestored) {
      setPrivacyRestored(false);
      return;
    }
    setPrivacyBusy(true);
    try {
      const res = await fetch(`${API_BASE}/privacy/restore`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scan_id: privacyResult.scan_id,
          redacted_text: privacyResult.redacted_text
        })
      });
      if (res.ok) {
        setPrivacyRestored(true);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setPrivacyBusy(false);
    }
  }

  async function fetchPrivacyLedger() {
    try {
      const res = await fetch(`${API_BASE}/privacy/ledger?limit=25`);
      if (res.ok) {
        const data = await res.json();
        setDisclosureLedger(data.ledger || []);
      }
    } catch (e) {
      console.error(e);
    }
  }

  // --- PILLAR 3: GUIDELINE HEALTH & GOVERNANCE HANDLERS ---
  async function fetchGovernanceData() {
    setGovernanceBusy(true);
    try {
      const [mRes, dRes, cRes, pRes] = await Promise.all([
        fetch(`${API_BASE}/governance/health-metrics`),
        fetch(`${API_BASE}/governance/disputes`),
        fetch(`${API_BASE}/governance/conflicts`),
        fetch(`${API_BASE}/governance/proposals`)
      ]);
      if (mRes.ok) setGovernanceMetrics(await mRes.json());
      if (dRes.ok) setDisputeStats((await dRes.json()).dispute_analytics || []);
      if (cRes.ok) setConflicts((await cRes.json()).conflicts || []);
      if (pRes.ok) setProposals((await pRes.json()).proposals || []);
    } catch (e) {
      console.error(e);
    } finally {
      setGovernanceBusy(false);
    }
  }

  async function handleApplyClarification(proposalId) {
    try {
      const res = await fetch(`${API_BASE}/governance/proposals/${proposalId}/apply?admin_user=${encodeURIComponent(currentRole)}`, {
        method: "POST"
      });
      if (res.ok) {
        fetchGovernanceData();
        triggerConfetti();
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function handleRollbackClarification(proposalId) {
    try {
      const res = await fetch(`${API_BASE}/governance/proposals/${proposalId}/rollback?admin_user=${encodeURIComponent(currentRole)}`, {
        method: "POST"
      });
      if (res.ok) {
        fetchGovernanceData();
        triggerConfetti();
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function handleSubmitDispute() {
    if (!disputeModal || !disputeReasonInput.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/governance/dispute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rule_id: disputeModal.rule_id,
          rule_name: disputeModal.rule_name,
          category: disputeModal.category || "General",
          reason: disputeReasonInput.trim(),
          user_role: currentRole
        })
      });
      if (res.ok) {
        setDisputeModal(null);
        setDisputeReasonInput("");
        fetchGovernanceData();
        triggerConfetti();
      }
    } catch (e) {
      console.error(e);
    }
  }

  function loadScenario(sc) {
    setTitle(sc.title);
    setContent(sc.text);
    setContentType(sc.content_type);
    setReviewResult(null);
    setSelectedFindingId(null);
    setEditorMode("editor");
    setError("");
  }

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setBusy(true);
    setError("");
    try {
      const reader = new FileReader();
      reader.onload = async () => {
        const base64Data = reader.result;
        const res = await fetch(`${API_BASE}/upload`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            filename: file.name,
            file_base64: base64Data,
            title: file.name.replace(/\.[^/.]+$/, ""),
            content_type: contentType
          })
        });
        if (!res.ok) throw new Error("File extraction failed. Ensure file is a valid .docx, .pdf, or text file.");
        const data = await res.json();
        setTitle(data.item.title);
        setContent(data.item.current_content);
        setReviewResult(data.item);
        if (data.item.brand_score >= 85) triggerConfetti();
      };
      reader.readAsDataURL(file);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function runReview() {
    if (!content.trim()) return;
    setBusy(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          content,
          content_type: contentType
        })
      });
      if (!res.ok) throw new Error("Inspection failed.");
      const data = await res.json();
      setReviewResult(data);
      if (data.findings && data.findings.length > 0) {
        setSelectedFindingId(data.findings[0].id);
      }
      if (data.brand_score >= 85) triggerConfetti();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleSuggestion(suggestionId, action, reason = null) {
    if (!reviewResult) return;
    try {
      const res = await fetch(`${API_BASE}/items/${reviewResult.content_id}/suggestions/${suggestionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action,
          actor: currentRole === "Creator" ? "Content Creator" : "Brand Manager",
          role: currentRole,
          rejection_reason: reason
        })
      });
      if (!res.ok) throw new Error("Action failed.");
      const updated = await res.json();
      setReviewResult(updated);
      setContent(updated.current_content);
      if (updated.brand_score >= 85) triggerConfetti();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleMagicFixAll() {
    if (!reviewResult) return;
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/items/${reviewResult.content_id}/accept-all?actor=${encodeURIComponent(currentRole)}&role=${encodeURIComponent(currentRole)}`, {
        method: "POST"
      });
      if (!res.ok) throw new Error("Magic fix failed.");
      const updated = await res.json();
      setReviewResult(updated);
      setContent(updated.current_content);
      triggerConfetti();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleStatusTransition(targetStatus) {
    if (!reviewResult) return;
    setError("");
    try {
      const effectiveRole = targetStatus === "Approved" ? "Brand Manager" : currentRole;
      const effectiveActor = targetStatus === "Approved" ? "Brand Manager" : (currentRole === "Creator" ? "Content Creator" : "Brand Manager");
      const res = await fetch(`${API_BASE}/items/${reviewResult.content_id}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_status: targetStatus,
          actor: effectiveActor,
          role: effectiveRole,
          comment: reviewerComment
        })
      });
      if (!res.ok) {
        const errJson = await res.json();
        throw new Error(errJson.detail || "Action could not be completed.");
      }
      const updated = await res.json();
      setReviewResult(updated);
      setReviewerComment("");
      if (targetStatus === "Approved") {
        setCurrentRole("Brand Manager");
        triggerConfetti();
      }
    } catch (err) {
      setError(err.message);
    }
  }

  function downloadCertificate() {
    if (!reviewResult) return;
    window.open(`${API_BASE}/items/${reviewResult.content_id}/certificate`, "_blank");
  }

  function downloadDocx() {
    if (!reviewResult) return;
    window.open(`${API_BASE}/items/${reviewResult.content_id}/export-docx`, "_blank");
  }

  async function handleAddTerm() {
    if (!newTermForm.term || !newTermForm.suggested_replacement) return;
    try {
      const res = await fetch(`${API_BASE}/brand/banned-term`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: `BT-${Date.now().toString().slice(-4)}`,
          term: newTermForm.term,
          suggested_replacement: newTermForm.suggested_replacement,
          reason: newTermForm.reason || "Prohibited corporate vocabulary",
          rule_id: "RULE-TERM-01"
        })
      });
      if (res.ok) {
        setNewTermModal(false);
        setNewTermForm({ term: "", suggested_replacement: "", reason: "" });
        fetchBrandKit();
        triggerConfetti();
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function handleAddFact() {
    if (!newFactForm.statement) return;
    try {
      const res = await fetch(`${API_BASE}/brand/fact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: `FACT-${Date.now().toString().slice(-4)}`,
          claim_key: newFactForm.claim_key || "custom_claim",
          statement: newFactForm.statement,
          source_document: newFactForm.source_document || "Brand Guidelines Addendum 2026",
          verified_by: "Brand Manager",
          valid_from: "2026-01-01",
          expires_at: newFactForm.expires_at || null,
          is_active: true
        })
      });
      if (res.ok) {
        setNewFactModal(false);
        setNewFactForm({ claim_key: "", statement: "", source_document: "", expires_at: "" });
        fetchBrandKit();
        triggerConfetti();
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function handleResetBrandKit() {
    if (!window.confirm("Reset brand rules and knowledge base to baseline defaults?")) return;
    try {
      const res = await fetch(`${API_BASE}/brand/reset`, { method: "POST" });
      if (res.ok) {
        fetchBrandKit();
        triggerConfetti();
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function runBenchmark() {
    setBenchmarkBusy(true);
    try {
      const res = await fetch(`${API_BASE}/benchmark`);
      if (res.ok) {
        setBenchmarkData(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setBenchmarkBusy(false);
    }
  }

  function triggerConfetti() {
    confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 } });
  }

  function getStepIndex() {
    if (!reviewResult) return 1;
    if (reviewResult.status === "Approved") return 4;
    if (reviewResult.status === "In Review" || reviewResult.status === "Changes Requested") return 3;
    return 2;
  }

  const activeStep = getStepIndex();

  // Word metrics calculation
  const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
  const readTimeMin = Math.max(1, Math.ceil(wordCount / 180));

  function renderInteractiveInspector() {
    if (!reviewResult || !reviewResult.findings || reviewResult.findings.length === 0) {
      return (
        <div className="inspector-view-container">
          <p style={{ color: "var(--emerald)", fontWeight: 600 }}>
            ✓ No active policy infractions detected in this text.
          </p>
          <div style={{ marginTop: "0.5rem", color: "#cbd5e1", whiteSpace: "pre-wrap" }}>
            {content}
          </div>
        </div>
      );
    }

    const text = reviewResult.original_content;
    const sortedFindings = [...reviewResult.findings]
      .filter(f => f.start_char >= 0 && f.end_char <= text.length)
      .sort((a, b) => a.start_char - b.start_char);

    const spans = [];
    let cur = 0;

    sortedFindings.forEach((f, idx) => {
      if (f.start_char > cur) {
        spans.push(text.slice(cur, f.start_char));
      }
      spans.push(
        <span
          key={`find-${f.id}-${idx}`}
          className={`inspector-highlight ${f.severity.toLowerCase()} ${selectedFindingId === f.id ? "selected-ring" : ""}`}
          onClick={() => {
            setSelectedFindingId(f.id);
            setViewMode("rules");
          }}
          title={`Click to inspect rule: ${f.rule_name} (${f.severity})`}
        >
          {f.matched_text}
        </span>
      );
      cur = Math.max(cur, f.end_char);
    });

    if (cur < text.length) {
      spans.push(text.slice(cur));
    }

    return (
      <div className="inspector-view-container">
        <div style={{ marginBottom: "0.5rem", fontSize: "0.75rem", color: "var(--cyan)", display: "flex", alignItems: "center", gap: 5 }}>
          <Sparkles size={13} /> Click any highlighted term to view the cited regulation and 1-click fix.
        </div>
        <div style={{ whiteSpace: "pre-wrap" }}>{spans}</div>
      </div>
    );
  }

  function renderDiff() {
    if (!reviewResult || !reviewResult.tracked_changes || reviewResult.tracked_changes.length === 0) {
      return <div>{reviewResult?.current_content || content}</div>;
    }

    let text = reviewResult.original_content;
    const changes = [...reviewResult.tracked_changes].sort((a, b) => b.start_char - a.start_char);
    const parts = [];
    let lastIndex = text.length;

    changes.forEach((tc) => {
      if (tc.start_char < lastIndex) {
        parts.unshift(text.slice(tc.end_char, lastIndex));
        parts.unshift(
          <span key={`tc-${tc.id}`}>
            <span className="del-glow">{tc.original_text}</span>
            <span className="ins-glow">{tc.replacement_text}</span>
          </span>
        );
        lastIndex = tc.start_char;
      }
    });
    if (lastIndex > 0) {
      parts.unshift(text.slice(0, lastIndex));
    }

    return <div className="diff-glow-container">{parts}</div>;
  }

  return (
    <div>
      {/* Ambient Cosmic VFX Glowing Orbs */}
      <div className="ambient-scene">
        <div className="ambient-orb orb-cyan"></div>
        <div className="ambient-orb orb-purple"></div>
        <div className="ambient-orb orb-blue"></div>
      </div>

      <div className="ultra-app">
        {/* Floating Dock Header */}
        <header className="floating-dock-header">
          <div className="brand-aura-box">
            <div className="brand-emblem-wrap">
              <div className="brand-emblem-halo"></div>
              <div className="brand-icon-shield" title="BrandGuard Autonomous Multi-Modal Governance">
                <ShieldCheck size={28} className="shield-svg" />
              </div>
            </div>
            <div className="brand-heading">
              <div className="brand-title-row">
                <h1 className="brand-title-text">
                  Brand<span className="brand-accent-text">Guard</span>
                </h1>
                <span className="cyber-beacon-pill round3-badge">
                  <span className="beacon-core pulse-beacon"></span>
                  ROUND 3 FINAL · ENTERPRISE
                </span>
              </div>
              <div className="brand-subline">
                <span className="brand-subline-main">Pre-Publication Multi-Modal Brand Governance</span>
                <span className="brand-subline-dot">·</span>
                <span className="brand-subline-team">Team WHO CARES?</span>
              </div>
            </div>
          </div>

          {/* Floating Navigation Dock */}
          <nav className="floating-tabs" aria-label="Main Application Navigation">
            <button
              className={`tab-pill ${activeTab === "studio" ? "active" : ""}`}
              onClick={() => setActiveTab("studio")}
              aria-current={activeTab === "studio" ? "page" : undefined}
            >
              <Layers size={14} aria-hidden="true" /> Review Studio
            </button>
            <button
              className={`tab-pill ${activeTab === "visual" ? "active" : ""}`}
              onClick={() => { setActiveTab("visual"); if (visualSamples.length === 0) fetchVisualSamples(); }}
              aria-current={activeTab === "visual" ? "page" : undefined}
            >
              <Sliders size={14} aria-hidden="true" /> Multimodal Visual
            </button>
            <button
              className={`tab-pill ${activeTab === "privacy" ? "active" : ""}`}
              onClick={() => { setActiveTab("privacy"); if (!privacyResult) runPrivacyScan(privacyText, privacyAirGapped); }}
              aria-current={activeTab === "privacy" ? "page" : undefined}
            >
              <Lock size={14} aria-hidden="true" /> Privacy Shield
            </button>
            <button
              className={`tab-pill ${activeTab === "governance" ? "active" : ""}`}
              onClick={() => { setActiveTab("governance"); fetchGovernanceData(); }}
              aria-current={activeTab === "governance" ? "page" : undefined}
            >
              <Zap size={14} aria-hidden="true" /> Guideline Health
            </button>
            <button
              className={`tab-pill ${activeTab === "knowledge" ? "active" : ""}`}
              onClick={() => setActiveTab("knowledge")}
              aria-current={activeTab === "knowledge" ? "page" : undefined}
            >
              <BookOpen size={14} aria-hidden="true" /> Brand Hub
            </button>
            <button
              className={`tab-pill ${activeTab === "audit" ? "active" : ""}`}
              onClick={() => { setActiveTab("audit"); fetchPrivacyLedger(); }}
              aria-current={activeTab === "audit" ? "page" : undefined}
            >
              <Activity size={14} aria-hidden="true" /> Audit & Ledger
            </button>
            <button
              className={`tab-pill ${activeTab === "benchmark" ? "active" : ""}`}
              onClick={() => { setActiveTab("benchmark"); if (!benchmarkData) runBenchmark(); }}
              aria-current={activeTab === "benchmark" ? "page" : undefined}
            >
              <Award size={14} aria-hidden="true" /> Benchmark (30 Cases)
            </button>
          </nav>

          {/* Role Pill with Pulsing LED */}
          <div className="role-floating-capsule">
            <div className="pulse-led" aria-hidden="true"></div>
            <select
              className="role-select-native"
              value={currentRole}
              onChange={(e) => setCurrentRole(e.target.value)}
              aria-label="Active User Role Switcher"
            >
              <option value="Creator">Content Creator</option>
              <option value="Brand Manager">Brand Manager</option>
              <option value="Legal & Compliance Reviewer">Legal Reviewer</option>
              <option value="Brand Admin">Brand Admin</option>
            </select>
          </div>
        </header>

        {/* 4-Step Sleek Stepper */}
        <nav className="stepper-dock" aria-label="Governance Workflow Progress">
          <div className={`step-node ${activeStep >= 1 ? (activeStep > 1 ? "completed" : "active") : ""}`}>
            <div className="step-circle">{activeStep > 1 ? "✓" : "1"}</div>
            <span>01. Content Input</span>
          </div>
          <div className="step-divider-line" aria-hidden="true"></div>
          <div className={`step-node ${activeStep >= 2 ? (activeStep > 2 ? "completed" : "active") : ""}`}>
            <div className="step-circle">{activeStep > 2 ? "✓" : "2"}</div>
            <span>02. Multi-Layer Scan</span>
          </div>
          <div className="step-divider-line" aria-hidden="true"></div>
          <div className={`step-node ${activeStep >= 3 ? (activeStep > 3 ? "completed" : "active") : ""}`}>
            <div className="step-circle">{activeStep > 3 ? "✓" : "3"}</div>
            <span>03. Tracked Changes & Fix</span>
          </div>
          <div className="step-divider-line" aria-hidden="true"></div>
          <div className={`step-node ${activeStep === 4 ? "completed active" : ""}`}>
            <div className="step-circle">{activeStep === 4 ? "★" : "4"}</div>
            <span>04. Human Sign-Off & Stamped Clearance</span>
          </div>
        </nav>

        <main role="main" id="main-content">

        {/* TAB 1: REVIEW STUDIO */}
        {activeTab === "studio" && (
          <>
            {/* Beginner-Friendly Quick Start Walkthrough Ribbon */}
            {showGuide && (
              <div className="beginner-guide-card">
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <HelpCircle size={22} color="var(--cyan)" />
                  <div>
                    <h4 style={{ fontSize: "0.88rem", fontWeight: 700, color: "#fff", marginBottom: 2 }}>
                      Beginner & Evaluator Interactive Walkthrough
                    </h4>
                    <div className="beginner-guide-steps">
                      <div className="beginner-step-badge">
                        <span className="beginner-step-num">1</span>
                        <span>Click any scenario chip below (or upload .docx/.pdf)</span>
                      </div>
                      <div className="beginner-step-badge">
                        <span className="beginner-step-num">2</span>
                        <span>Click "Scan & Protect Content" to see line citations</span>
                      </div>
                      <div className="beginner-step-badge">
                        <span className="beginner-step-num">3</span>
                        <span>Use "Magic Fix All" to apply verified rewrites</span>
                      </div>
                      <div className="beginner-step-badge">
                        <span className="beginner-step-num">4</span>
                        <span>Click "Approve" to download PDF Certificate & Word file</span>
                      </div>
                    </div>
                  </div>
                </div>
                <button
                  style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "0.75rem" }}
                  onClick={() => setShowGuide(false)}
                  title="Dismiss guide banner"
                >
                  ✕ Dismiss
                </button>
              </div>
            )}

            {/* Interactive Scenario Glow Chips */}
            <div className="scenario-strip">
              <span className="strip-label"><Sparkles size={13} color="var(--cyan)" /> 1-Click Samples:</span>
              {scenarios.map((sc, i) => {
                const icons = ["🚀", "⚠️", "☁️", "✉️", "✨"];
                return (
                  <button
                    key={sc.id}
                    className="scenario-glow-chip"
                    onClick={() => loadScenario(sc)}
                    title={sc.summary}
                  >
                    <span>{icons[i % icons.length]}</span>
                    <span>{sc.title}</span>
                  </button>
                );
              })}
            </div>

            {error && (
              <div style={{
                background: "rgba(244,63,94,0.12)",
                border: "1px solid rgba(244,63,94,0.4)",
                padding: "0.75rem 1rem",
                borderRadius: 10,
                color: "#fda4af",
                fontSize: "0.85rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "0.5rem"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <AlertTriangle size={16} color="#f43f5e" />
                  <span>{error}</span>
                </div>
                <button
                  onClick={() => setError("")}
                  style={{ background: "transparent", border: "none", color: "#fda4af", cursor: "pointer", fontSize: "0.95rem", padding: "0 4px" }}
                  title="Dismiss alert"
                >
                  ✕
                </button>
              </div>
            )}

            {/* 2-Column Balanced Floating Studio */}
            <div className="studio-grid-balanced">
              {/* Left Column: Content Editor & Interactive Highlight Inspector */}
              <div className="floating-glass-panel">
                <div className="panel-header-clean">
                  <h2><FileText size={16} color="var(--blue)" /> Content Submission</h2>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                      {wordCount} words · {content.length} chars · ~{readTimeMin}m read
                    </span>
                    {reviewResult && (
                      <div style={{ display: "flex", gap: 4, background: "rgba(8,12,26,0.6)", padding: "2px", borderRadius: 6, border: "1px solid var(--border-glass)" }}>
                        <button
                          style={{
                            background: editorMode === "editor" ? "rgba(59,130,246,0.3)" : "transparent",
                            border: "none",
                            color: editorMode === "editor" ? "#fff" : "var(--text-muted)",
                            padding: "3px 8px",
                            borderRadius: 4,
                            cursor: "pointer",
                            fontSize: "0.72rem",
                            display: "flex",
                            alignItems: "center",
                            gap: 3
                          }}
                          onClick={() => setEditorMode("editor")}
                        >
                          <Edit3 size={11} /> Edit Text
                        </button>
                        <button
                          style={{
                            background: editorMode === "inspector" ? "rgba(6,182,212,0.3)" : "transparent",
                            border: "none",
                            color: editorMode === "inspector" ? "#38bdf8" : "var(--text-muted)",
                            padding: "3px 8px",
                            borderRadius: 4,
                            cursor: "pointer",
                            fontSize: "0.72rem",
                            display: "flex",
                            alignItems: "center",
                            gap: 3
                          }}
                          onClick={() => setEditorMode("inspector")}
                        >
                          <Eye size={11} /> Visual Inspector
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                <div className="grid-meta-inputs">
                  <div>
                    <label className="meta-label" htmlFor="doc-title-input">Document Title</label>
                    <input
                      id="doc-title-input"
                      type="text"
                      className="glass-field-input"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Title or Campaign Name"
                      aria-label="Document Title"
                    />
                  </div>
                  <div>
                    <label className="meta-label" htmlFor="doc-channel-select">Target Channel</label>
                    <select
                      id="doc-channel-select"
                      className="glass-field-select"
                      value={contentType}
                      onChange={(e) => setContentType(e.target.value)}
                      aria-label="Target Channel"
                    >
                      <option value="social_post">Social Media</option>
                      <option value="press_release">Press Release</option>
                      <option value="support_notice">Support Policy</option>
                      <option value="marketing_email">Newsletter</option>
                      <option value="blog">Corporate Blog</option>
                    </select>
                  </div>
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                    <label className="meta-label" htmlFor="doc-content-textarea" style={{ margin: 0 }}>
                      {editorMode === "editor" ? "Content Draft (Type or Paste)" : "Interactive Policy Inspector View"}
                    </label>
                    {reviewResult?.findings?.length > 0 && editorMode === "editor" && (
                      <span
                        style={{ fontSize: "0.72rem", color: "var(--cyan)", cursor: "pointer", textDecoration: "underline" }}
                        onClick={() => setEditorMode("inspector")}
                      >
                        Switch to Visual Highlight Inspector →
                      </span>
                    )}
                  </div>

                  {editorMode === "editor" ? (
                    <textarea
                      id="doc-content-textarea"
                      className="glass-field-textarea"
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      placeholder="Enter or paste copy to verify against brand rules, tone guidelines, and verified facts..."
                      rows={8}
                      aria-label="Content Draft Editor"
                    />
                  ) : (
                    renderInteractiveInspector()
                  )}
                </div>

                {/* Hologram File Upload Dropzone */}
                <label className="hologram-file-dropzone" aria-label="Upload document file (.docx, .pdf, .txt, .md)">
                  <input
                    type="file"
                    style={{ display: "none" }}
                    accept=".pdf,.docx,.txt,.md"
                    onChange={handleFileUpload}
                    aria-label="File input for document upload"
                  />
                  <Upload size={18} color="var(--cyan)" aria-hidden="true" />
                  <span>Drop Word (.docx) or PDF document to auto-extract and review</span>
                </label>

                <button
                  className="btn-vfx-scan"
                  onClick={runReview}
                  disabled={busy || !content.trim()}
                  aria-label="Scan and Protect Content against brand rules"
                >
                  {busy ? <RefreshCw className="spin" size={17} aria-hidden="true" /> : <Wand2 size={17} aria-hidden="true" />}
                  {busy ? "Running 4-Layer Guideline Verification..." : "✨ Scan & Protect Content →"}
                </button>
              </div>

              {/* Right Column: Intelligence & Findings Deck */}
              <div className="floating-glass-panel">
                <div className="panel-header-clean">
                  <h2><ShieldCheck size={16} color="var(--emerald)" /> BrandGuard Intelligence Deck</h2>
                  {reviewResult && (
                    <span className={`badge-neon ${reviewResult.status.toLowerCase().replace(" ", "-")}`}>
                      {reviewResult.status}
                    </span>
                  )}
                </div>

                {!reviewResult ? (
                  <div style={{ textAlign: "center", padding: "4rem 1.5rem", color: "var(--text-muted)" }}>
                    <ShieldCheck size={48} color="var(--cyan)" style={{ opacity: 0.35, marginBottom: "0.85rem" }} />
                    <h3 style={{ color: "#fff", marginBottom: "0.4rem", fontSize: "1.05rem" }}>Ready to Protect Your Brand</h3>
                    <p style={{ fontSize: "0.84rem", maxWidth: 360, margin: "0 auto", lineHeight: 1.55 }}>
                      Click any scenario above or paste copy to see line-by-line proof citations, tracked-change rewrites, and instant brand scoring.
                    </p>
                  </div>
                ) : (
                  <>
                    {/* Holographic Scorecard Row */}
                    <div className="score-holographic-row">
                      <div className="score-holographic-main">
                        <div className={`hologram-score-ring ${reviewResult.brand_score >= 85 ? "green" : reviewResult.brand_score >= 60 ? "amber" : "red"}`}>
                          {reviewResult.brand_score}
                        </div>
                        <div className="score-holographic-text">
                          <h3>Brand Consistency Index</h3>
                          <p>
                            {reviewResult.findings.length === 0
                              ? "✓ 100% compliant with approved guidelines"
                              : `${reviewResult.findings.length} issue(s) flagged across guidelines`}
                          </p>
                        </div>
                      </div>

                      {/* 1-Click Magic Fix Button */}
                      {reviewResult.tracked_changes?.some(tc => tc.status === "pending") && (
                        <button
                          className="btn-magic-pulsing"
                          onClick={handleMagicFixAll}
                          title="Instantly accept all verified fixes and boost consistency score"
                        >
                          <Sparkles size={14} /> Magic Fix All
                        </button>
                      )}
                    </div>

                    {/* Subscore Pills Row with Progress Gauges */}
                    {reviewResult.category_scores && (
                      <div className="subscore-pills-row">
                        <div className="subscore-mini-pill">
                          <div className="subscore-mini-title">Terminology</div>
                          <div className="subscore-mini-val" style={{ color: reviewResult.category_scores.Terminology >= 80 ? "var(--emerald)" : "var(--rose)" }}>
                            {reviewResult.category_scores.Terminology}%
                          </div>
                          <div style={{ width: "100%", height: 3, background: "rgba(255,255,255,0.08)", borderRadius: 2, marginTop: 4, overflow: "hidden" }}>
                            <div style={{ width: `${reviewResult.category_scores.Terminology}%`, height: "100%", background: reviewResult.category_scores.Terminology >= 80 ? "var(--emerald)" : "var(--rose)" }} />
                          </div>
                        </div>
                        <div className="subscore-mini-pill">
                          <div className="subscore-mini-title">Claims & Facts</div>
                          <div className="subscore-mini-val" style={{ color: reviewResult.category_scores["Claims & Facts"] >= 80 ? "var(--emerald)" : "var(--rose)" }}>
                            {reviewResult.category_scores["Claims & Facts"]}%
                          </div>
                          <div style={{ width: "100%", height: 3, background: "rgba(255,255,255,0.08)", borderRadius: 2, marginTop: 4, overflow: "hidden" }}>
                            <div style={{ width: `${reviewResult.category_scores["Claims & Facts"]}%`, height: "100%", background: reviewResult.category_scores["Claims & Facts"] >= 80 ? "var(--emerald)" : "var(--rose)" }} />
                          </div>
                        </div>
                        <div className="subscore-mini-pill">
                          <div className="subscore-mini-title">Tone & Voice</div>
                          <div className="subscore-mini-val" style={{ color: reviewResult.category_scores["Tone & Voice"] >= 80 ? "var(--emerald)" : "var(--rose)" }}>
                            {reviewResult.category_scores["Tone & Voice"]}%
                          </div>
                          <div style={{ width: "100%", height: 3, background: "rgba(255,255,255,0.08)", borderRadius: 2, marginTop: 4, overflow: "hidden" }}>
                            <div style={{ width: `${reviewResult.category_scores["Tone & Voice"]}%`, height: "100%", background: reviewResult.category_scores["Tone & Voice"] >= 80 ? "var(--emerald)" : "var(--rose)" }} />
                          </div>
                        </div>
                        <div className="subscore-mini-pill">
                          <div className="subscore-mini-title">Guidelines</div>
                          <div className="subscore-mini-val" style={{ color: reviewResult.category_scores.Guidelines >= 80 ? "var(--emerald)" : "var(--rose)" }}>
                            {reviewResult.category_scores.Guidelines}%
                          </div>
                          <div style={{ width: "100%", height: 3, background: "rgba(255,255,255,0.08)", borderRadius: 2, marginTop: 4, overflow: "hidden" }}>
                            <div style={{ width: `${reviewResult.category_scores.Guidelines}%`, height: "100%", background: reviewResult.category_scores.Guidelines >= 80 ? "var(--emerald)" : "var(--rose)" }} />
                          </div>
                        </div>
                      </div>
                    )}

                    {/* View Mode Bar */}
                    <div className="view-mode-bar-clean">
                      <div className="view-mode-tabs-clean">
                        <button
                          className={`view-mode-btn-clean ${viewMode === "split" ? "active" : ""}`}
                          onClick={() => setViewMode("split")}
                        >
                          <SplitSquareVertical size={13} style={{ display: "inline", marginRight: 4 }} />
                          Side-by-Side
                        </button>
                        <button
                          className={`view-mode-btn-clean ${viewMode === "diff" ? "active" : ""}`}
                          onClick={() => setViewMode("diff")}
                        >
                          <Sliders size={13} style={{ display: "inline", marginRight: 4 }} />
                          Tracked Diff ({reviewResult.tracked_changes?.length || 0})
                        </button>
                        <button
                          className={`view-mode-btn-clean ${viewMode === "rules" ? "active" : ""}`}
                          onClick={() => setViewMode("rules")}
                        >
                          <FileCheck size={13} style={{ display: "inline", marginRight: 4 }} />
                          Rule Proofs ({reviewResult.findings?.length || 0})
                        </button>
                      </div>
                    </div>

                    {/* VIEW 1: SIDE-BY-SIDE SPLIT COMPARE */}
                    {viewMode === "split" && (
                      <div className="split-view-cards">
                        <div className="split-card-item original">
                          <div className="split-card-head">
                            <span>Original Submitted Draft</span>
                            <span style={{ color: "var(--rose)" }}>Policy Breaches</span>
                          </div>
                          <div className="split-card-body-text">{reviewResult.original_content}</div>
                        </div>
                        <div className="split-card-item cleaned">
                          <div className="split-card-head">
                            <span>Protected Compliant Output</span>
                            <span style={{ color: "var(--emerald)" }}>Approved</span>
                          </div>
                          <div className="split-card-body-text">{reviewResult.current_content}</div>
                        </div>
                      </div>
                    )}

                    {/* VIEW 2: TRACKED DIFF */}
                    {viewMode === "diff" && (
                      <div>
                        {renderDiff()}

                        <div style={{ marginTop: "0.85rem", maxHeight: 220, overflowY: "auto" }}>
                          {reviewResult.tracked_changes?.length === 0 ? (
                            <p style={{ color: "var(--emerald)", fontSize: "0.82rem" }}>
                              ✓ All suggested corrections have been applied.
                            </p>
                          ) : (
                            reviewResult.tracked_changes?.map((tc) => (
                              <div key={tc.id} className="suggestion-card-vfx">
                                <div className="suggestion-card-top">
                                  <span className="rule-pill-tag">VERIFIED FIX</span>
                                  <span className={`badge-neon ${tc.status}`}>
                                    {tc.status.toUpperCase()}
                                  </span>
                                </div>

                                <div className="suggestion-inline-preview">
                                  <span className="del">“{tc.original_text}”</span>
                                  <span style={{ margin: "0 0.35rem", color: "var(--text-muted)" }}>→</span>
                                  <span className="ins">“{tc.replacement_text}”</span>
                                </div>

                                {tc.status === "pending" && (
                                  <div className="suggestion-vfx-actions">
                                    <button
                                      className="btn-vfx-accept"
                                      onClick={() => handleSuggestion(tc.id, "accept")}
                                    >
                                      <Check size={13} /> Accept Fix
                                    </button>
                                    <button
                                      className="btn-vfx-reject"
                                      onClick={() => {
                                        setRejectionModal({ changeId: tc.id, originalText: tc.original_text });
                                        setRejectionReason("");
                                      }}
                                    >
                                      <X size={13} /> Dismiss
                                    </button>
                                  </div>
                                )}

                                {tc.status === "rejected" && tc.rejection_reason && (
                                  <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginTop: "0.35rem" }}>
                                    <strong>Dismissal justification:</strong> {tc.rejection_reason}
                                  </div>
                                )}
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                    )}

                    {/* VIEW 3: RULE CITATIONS */}
                    {viewMode === "rules" && (
                      <div style={{ maxHeight: 300, overflowY: "auto" }}>
                        {reviewResult.findings?.map((f) => (
                          <div
                            key={f.id}
                            className={`rule-proof-card ${f.severity.toLowerCase()} ${selectedFindingId === f.id ? "selected-proof-ring" : ""}`}
                            onClick={() => setSelectedFindingId(f.id)}
                          >
                            <div className="proof-meta-top">
                              <span style={{ fontWeight: 800, fontSize: "0.75rem", color: f.severity === "Critical" ? "var(--rose)" : "var(--amber)" }}>
                                [{f.severity.toUpperCase()}] {f.category}
                              </span>
                              <span style={{ fontSize: "0.72rem", fontFamily: "var(--font-mono)", color: "var(--cyan)" }}>
                                {f.rule_id} · {f.confidence_score}% Confidence
                              </span>
                            </div>

                            <p style={{ fontSize: "0.88rem", color: "#fff", marginBottom: "0.25rem", fontWeight: 600 }}>
                              “{f.matched_text}”
                            </p>
                            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.45 }}>
                              {f.explanation}
                            </p>

                            <div className="proof-citation-pill">
                              <strong style={{ color: "var(--cyan)" }}>Verified Citation Source:</strong> {f.citation_source}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Stamped Clearance & Governance Deck */}
                    <div className="clearance-action-deck">
                      <div className="clearance-deck-top">
                        <div style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 700, fontSize: "0.88rem", color: "#fff" }}>
                          <UserCheck size={16} color="var(--emerald)" /> Human Sign-Off & Governance
                        </div>
                        <span style={{ fontSize: "0.74rem", color: "var(--text-muted)" }}>
                          Acting as: <strong style={{ color: "var(--cyan)" }}>{currentRole}</strong>
                        </span>
                      </div>

                      <input
                        type="text"
                        className="glass-field-input"
                        style={{ fontSize: "0.8rem", padding: "0.45rem 0.75rem" }}
                        value={reviewerComment}
                        onChange={(e) => setReviewerComment(e.target.value)}
                        placeholder="Add review feedback or sign-off notes (logged in immutable audit trail)..."
                      />

                      <div className="clearance-deck-btns">
                        {reviewResult.status !== "Approved" ? (
                          <>
                            <button
                              className="btn-subtle-trans"
                              onClick={() => handleStatusTransition("In Review")}
                            >
                              Submit for Review
                            </button>
                            <button
                              className="btn-subtle-trans"
                              onClick={() => handleStatusTransition("Changes Requested")}
                            >
                              Request Changes
                            </button>
                            <button
                              className="btn-stamped-approve"
                              onClick={() => handleStatusTransition("Approved")}
                            >
                              <Award size={15} /> Approve Brand Clearance
                            </button>
                          </>
                        ) : (
                          <>
                            <div style={{ display: "flex", alignItems: "center", gap: 5, color: "var(--emerald)", fontSize: "0.84rem", fontWeight: 700 }}>
                              <CheckCircle2 size={16} /> Fully Cleared & Approved
                            </div>
                            <button
                              className="btn-gold-cert"
                              onClick={downloadCertificate}
                            >
                              <Download size={15} /> Certificate (PDF)
                            </button>
                            <button
                              className="btn-docx-export"
                              onClick={downloadDocx}
                            >
                              <FileText size={15} /> Approved Word (.docx)
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </>
        )}

        {/* ================================================================= */}
        {/* PILLAR 1: MULTIMODAL VISUAL & ACCESSIBILITY COMPLIANCE ENGINE    */}
        {/* ================================================================= */}
        {activeTab === "visual" && (
          <div className="visual-container">
            <div className="r3-hero-ribbon">
              <div className="r3-hero-left">
                <h2><Sliders size={20} color="var(--cyan)" /> Multimodal Visual & Accessibility Compliance Engine</h2>
                <p>
                  Mathematical CIEDE2000 (ΔE₀₀) color deviation against official brand palette,
                  WCAG 2.1 AA/AAA contrast matrix, and logo aspect-ratio & margin clearance verification.
                </p>
              </div>
              <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                <label className="btn-vfx-scan" style={{ cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 6, margin: 0, padding: "0.55rem 1rem", fontSize: "0.82rem" }}>
                  <Upload size={14} /> Upload Custom Asset
                  <input type="file" accept="image/*" onChange={handleCustomImageUpload} style={{ display: "none" }} />
                </label>
              </div>
            </div>

            {/* 1-Click Preset Visual Assets */}
            <div className="r3-preset-strip">
              <span className="strip-label"><Sparkles size={13} color="var(--cyan)" /> 1-Click Evaluator Assets:</span>
              {visualSamples.map((sample) => (
                <button
                  key={sample.id}
                  className={`r3-preset-btn ${selectedVisualSample === sample.id ? "active" : ""}`}
                  onClick={() => {
                    setSelectedVisualSample(sample.id);
                    inspectVisualAsset(sample.image_data, sample.title, sample.id.includes("logo") ? "logo" : "banner");
                  }}
                >
                  <span>{sample.id.includes("compliant") ? "✨" : sample.id.includes("contrast") ? "⚠️" : "🚨"}</span>
                  <span>{sample.title}</span>
                  <small style={{ opacity: 0.7, fontSize: "0.7rem" }}>({sample.expected_score})</small>
                </button>
              ))}
            </div>

            {/* Main Visual Workspace Grid */}
            {visualAnalysis ? (
              <div className="visual-workspace-grid">
                {/* Left Column: Asset Preview & Score Pod */}
                <div className="visual-preview-card">
                  <div className="panel-header-clean" style={{ padding: 0 }}>
                    <div>
                      <h3 style={{ fontSize: "1rem", color: "#fff", fontWeight: 700 }}>Asset Rendering & Inspection</h3>
                      <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                        {visualAnalysis.filename} · {visualAnalysis.dimensions.width} × {visualAnalysis.dimensions.height} px ({visualAnalysis.format})
                      </p>
                    </div>
                    <span className={`badge-neon ${visualAnalysis.clearance_status === "APPROVED_VISUAL" ? "approved" : visualAnalysis.clearance_status === "WARNING_REMEDIATION_RECOMMENDED" ? "in-review" : "changes-requested"}`}>
                      {visualAnalysis.clearance_status}
                    </span>
                  </div>

                  <div className="visual-asset-stage">
                    {visualSamples.find(s => s.id === selectedVisualSample)?.image_data ? (
                      <img
                        src={visualSamples.find(s => s.id === selectedVisualSample).image_data}
                        alt="Analyzed Asset Preview"
                        className="visual-asset-img"
                      />
                    ) : (
                      <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Custom Asset Loaded</div>
                    )}
                  </div>

                  <div className="visual-score-pod">
                    <div>
                      <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Overall Visual Score</div>
                      <div className="visual-score-big" style={{ color: visualAnalysis.overall_visual_score >= 85 ? "var(--emerald)" : visualAnalysis.overall_visual_score >= 60 ? "var(--amber)" : "var(--rose)" }}>
                        {visualAnalysis.overall_visual_score}<span style={{ fontSize: "1rem", color: "var(--text-muted)", fontWeight: 500 }}>/100</span>
                      </div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "0.78rem", fontWeight: 700, color: "#fff" }}>
                        {visualAnalysis.overall_visual_score >= 85 ? "Brand Certified" : "Remediation Advised"}
                      </div>
                      <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>
                        Weighted: 45% Palette, 30% WCAG, 25% Geometry
                      </div>
                    </div>
                  </div>

                  <div className="visual-subscores-grid">
                    <div className="visual-subscore-item">
                      <div className="label">Palette ΔE₀₀</div>
                      <div className="val" style={{ color: "var(--cyan)" }}>{visualAnalysis.component_scores.palette_compliance}/100</div>
                    </div>
                    <div className="visual-subscore-item">
                      <div className="label">WCAG Contrast</div>
                      <div className="val" style={{ color: "var(--emerald)" }}>{visualAnalysis.component_scores.accessibility_contrast}/100</div>
                    </div>
                    <div className="visual-subscore-item">
                      <div className="label">Logo Geometry</div>
                      <div className="val" style={{ color: "var(--purple)" }}>{visualAnalysis.component_scores.logo_geometry}/100</div>
                    </div>
                  </div>
                </div>

                {/* Right Column: Detailed Scientific Breakdown */}
                <div className="floating-glass-panel">
                  <div style={{ display: "flex", gap: "0.5rem", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.75rem", marginBottom: "1rem" }}>
                    <button
                      className={`tab-pill ${visualActiveSubtab === "palette" ? "active" : ""}`}
                      onClick={() => setVisualActiveSubtab("palette")}
                      style={{ fontSize: "0.78rem" }}
                    >
                      🎨 CIEDE2000 Palette ({visualAnalysis.extracted_dominant_colors.length})
                    </button>
                    <button
                      className={`tab-pill ${visualActiveSubtab === "wcag" ? "active" : ""}`}
                      onClick={() => setVisualActiveSubtab("wcag")}
                      style={{ fontSize: "0.78rem" }}
                    >
                      👁️ WCAG 2.1 Accessibility ({visualAnalysis.wcag_accessibility.evaluated_pairs} pairs)
                    </button>
                    <button
                      className={`tab-pill ${visualActiveSubtab === "geometry" ? "active" : ""}`}
                      onClick={() => setVisualActiveSubtab("geometry")}
                      style={{ fontSize: "0.78rem" }}
                    >
                      📐 Geometry & Safe-Space
                    </button>
                  </div>

                  {/* Subtab 1: CIEDE2000 Palette Findings */}
                  {visualActiveSubtab === "palette" && (
                    <div>
                      <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
                        Dominant color clusters extracted via histogram analysis and evaluated against official brand palette using ISO/CIE CIEDE2000 color distance formula (ΔE ≤ 2.0 considered imperceptible drift).
                      </p>
                      <div className="swatch-grid">
                        {visualAnalysis.color_compliance_findings.map((cf, idx) => (
                          <div key={idx} className="swatch-box">
                            <div className="swatch-color-pill" style={{ background: cf.extracted_hex }}></div>
                            <div className="swatch-meta-hex">{cf.extracted_hex}</div>
                            <div style={{ fontSize: "0.72rem", color: "var(--text-secondary)" }}>{cf.coverage_percent}% coverage</div>
                            <div className="swatch-meta-delta">
                              <span style={{ color: "var(--text-muted)" }}>ΔE₀₀: <strong>{cf.delta_e_2000}</strong></span>
                              <span className={`badge-neon ${cf.severity === "Pass" ? "approved" : cf.severity === "Warning" ? "in-review" : "changes-requested"}`} style={{ fontSize: "0.65rem", padding: "0.1rem 0.35rem" }}>
                                {cf.severity}
                              </span>
                            </div>
                            <div style={{ fontSize: "0.7rem", color: "var(--cyan)", borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "0.3rem" }}>
                              Matched: {cf.closest_brand_color} ({cf.closest_brand_hex})
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Subtab 2: WCAG 2.1 Matrix */}
                  {visualActiveSubtab === "wcag" && (
                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                        <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                          Relative luminance contrast measured across foreground/background asset layers.
                        </p>
                        <span className={`badge-neon ${visualAnalysis.wcag_accessibility.status === "PASS" ? "approved" : "changes-requested"}`}>
                          WCAG Status: {visualAnalysis.wcag_accessibility.status}
                        </span>
                      </div>
                      <div className="wcag-table-wrap">
                        <table className="wcag-table">
                          <thead>
                            <tr>
                              <th>Background</th>
                              <th>Foreground</th>
                              <th>Ratio</th>
                              <th>AA Normal (≥4.5:1)</th>
                              <th>AAA (≥7:1)</th>
                              <th>Remediation Suggestion</th>
                            </tr>
                          </thead>
                          <tbody>
                            {visualAnalysis.wcag_accessibility.pairs.map((p, i) => (
                              <tr key={i}>
                                <td>
                                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                                    <div style={{ width: 16, height: 16, borderRadius: 4, background: p.background_hex, border: "1px solid rgba(255,255,255,0.2)" }}></div>
                                    <code>{p.background_hex}</code>
                                  </div>
                                </td>
                                <td>
                                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                                    <div style={{ width: 16, height: 16, borderRadius: 4, background: p.foreground_hex, border: "1px solid rgba(255,255,255,0.2)" }}></div>
                                    <code>{p.foreground_hex}</code>
                                  </div>
                                </td>
                                <td><strong>{p.contrast_ratio}</strong></td>
                                <td>
                                  <span className={`badge-neon ${p.wcag_21_aa_normal ? "approved" : "changes-requested"}`}>
                                    {p.wcag_21_aa_normal ? "PASS" : "FAIL"}
                                  </span>
                                </td>
                                <td>
                                  <span className={`badge-neon ${p.wcag_21_aaa_normal ? "approved" : "in-review"}`}>
                                    {p.wcag_21_aaa_normal ? "PASS" : "FAIL"}
                                  </span>
                                </td>
                                <td style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{p.suggestion}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Subtab 3: Logo Geometry & Safe Space */}
                  {visualActiveSubtab === "geometry" && (
                    <div>
                      <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
                        Verifies that brand emblem aspect ratio has not been warped/stretched and that clear-space safety perimeter (minimum 10% isolation boundary) has no edge encroachment.
                      </p>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "1rem" }}>
                        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "1rem" }}>
                          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Aspect Ratio Lock</div>
                          <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "#fff", marginTop: "0.25rem" }}>
                            {visualAnalysis.logo_geometry.actual_aspect_ratio}:1
                          </div>
                          <div style={{ fontSize: "0.75rem", color: visualAnalysis.logo_geometry.aspect_ratio_compliant ? "var(--emerald)" : "var(--rose)", marginTop: "0.25rem" }}>
                            {visualAnalysis.logo_geometry.aspect_ratio_compliant ? "✓ Aspect Ratio Locked (Within 5% Tolerance)" : `⚠️ Distorted (${visualAnalysis.logo_geometry.aspect_deviation_percent}% Deviation from target ${visualAnalysis.logo_geometry.target_aspect_ratio}:1)`}
                          </div>
                        </div>

                        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "1rem" }}>
                          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Safe Space Margin Buffer</div>
                          <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "#fff", marginTop: "0.25rem" }}>
                            {visualAnalysis.logo_geometry.clear_space_compliant ? "Protected" : "Encroached"}
                          </div>
                          <div style={{ fontSize: "0.75rem", color: visualAnalysis.logo_geometry.clear_space_compliant ? "var(--emerald)" : "var(--rose)", marginTop: "0.25rem" }}>
                            {visualAnalysis.logo_geometry.clear_space_compliant ? "✓ 10% perimeter clear space is uncompromised" : "⚠️ Graphic or boundary clipping detected in isolation perimeter"}
                          </div>
                        </div>
                      </div>

                      <div style={{ marginTop: "1rem", background: "rgba(15,23,42,0.6)", padding: "0.85rem", borderRadius: 8, fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                        <strong>Geometric Assessment:</strong> {visualAnalysis.logo_geometry.explanation}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="floating-glass-panel" style={{ textAlign: "center", padding: "3rem" }}>
                <RefreshCw size={28} className="spin" color="var(--cyan)" style={{ margin: "0 auto 1rem" }} />
                <p style={{ color: "#fff", fontWeight: 600 }}>Running Multimodal Inspection Pipeline...</p>
              </div>
            )}
          </div>
        )}

        {/* ================================================================= */}
        {/* PILLAR 2: ENTERPRISE PRIVACY SHIELD & AIR-GAPPED INFERENCE        */}
        {/* ================================================================= */}
        {activeTab === "privacy" && (
          <div className="privacy-container">
            <div className="r3-hero-ribbon">
              <div className="r3-hero-left">
                <h2><Lock size={20} color="var(--cyan)" /> Enterprise Privacy Shield & Air-Gapped Pipeline</h2>
                <p>
                  Pattern & heuristic redaction radar for API credentials, credit accounts, and confidential ARR metrics.
                  Features reversible context-preserving vault mapping, zero-data-retention kill-switch, and cryptographic SHA-256 AI disclosure ledger.
                </p>
              </div>
              <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                <button
                  className={`btn-vfx-scan ${privacyAirGapped ? "round3-badge" : ""}`}
                  onClick={() => {
                    const nextMode = !privacyAirGapped;
                    setPrivacyAirGapped(nextMode);
                    runPrivacyScan(privacyText, nextMode);
                  }}
                  style={{ padding: "0.55rem 1rem", fontSize: "0.82rem", display: "flex", alignItems: "center", gap: 6 }}
                >
                  {privacyAirGapped ? <CheckCircle2 size={15} color="var(--emerald)" /> : <AlertTriangle size={15} color="var(--amber)" />}
                  {privacyAirGapped ? "Air-Gapped: 100% Offline" : "External AI Gateway"}
                </button>
              </div>
            </div>

            {/* 1-Click Sensitive Presets */}
            <div className="r3-preset-strip">
              <span className="strip-label"><Sparkles size={13} color="var(--cyan)" /> 1-Click Sensitive Copy Presets:</span>
              <button
                className="r3-preset-btn"
                onClick={() => {
                  const txt = "Confidential Board Memo: Contact CFO Dr. Sarah Jenkins at s.jenkins@apexpay.com or call +1 (555) 234-8901. Do not share live token sk_test_99887766554433221100aabbcc on Slack. Q3 enterprise ARR reached $48.5M ARR with customer vault 4111-2222-3333-4444 on gateway 10.0.4.12.";
                  setPrivacyText(txt);
                  runPrivacyScan(txt, privacyAirGapped);
                }}
              >
                <span>🔒</span> CFO Q3 Financial & API Credentials
              </button>
              <button
                className="r3-preset-btn"
                onClick={() => {
                  const txt = "Infrastructure Incident Report: Server outage traced to cluster 10.12.84.1. Incident Commander Alex reached at a.turner@cloudrails.io (+44 20 7946 0991). Auth token Bearer ghp_99887766554433221100aabbcc expired. Estimated payout SLA damages: $120,000 profit loss.";
                  setPrivacyText(txt);
                  runPrivacyScan(txt, privacyAirGapped);
                }}
              >
                <span>🔑</span> DevOps Incident & Secret Token
              </button>
            </div>

            {/* Privacy Radar Split Screen */}
            <div className="privacy-grid">
              {/* Raw Input Column */}
              <div className="privacy-pane">
                <div className="panel-header-clean" style={{ padding: 0 }}>
                  <h3 style={{ fontSize: "0.95rem", color: "#fff", fontWeight: 700 }}>Pre-Publication Draft (Raw)</h3>
                  <span className="badge-neon in-review">Unmasked Input</span>
                </div>
                <textarea
                  className="privacy-textarea"
                  value={privacyText}
                  onChange={(e) => setPrivacyText(e.target.value)}
                  placeholder="Paste memo, PR release, or executive comms containing sensitive figures or secrets..."
                />
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    Air-gapped scan runs 100% locally with zero external network egress.
                  </span>
                  <button
                    className="btn-vfx-scan"
                    onClick={() => runPrivacyScan(privacyText, privacyAirGapped)}
                    disabled={privacyBusy}
                    style={{ padding: "0.45rem 1rem", fontSize: "0.82rem" }}
                  >
                    {privacyBusy ? "Scanning..." : "Scan & Redact Secrets"}
                  </button>
                </div>
              </div>

              {/* Redacted & Masked Column */}
              <div className="privacy-pane">
                <div className="panel-header-clean" style={{ padding: 0 }}>
                  <h3 style={{ fontSize: "0.95rem", color: "#fff", fontWeight: 700 }}>Privacy Shield Masked Output</h3>
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    {privacyResult && (
                      <span className="badge-neon approved" style={{ fontSize: "0.72rem" }}>
                        {privacyResult.total_redactions} Secrets Isolated
                      </span>
                    )}
                    <button
                      className="btn-subtle-trans"
                      onClick={restorePrivacyText}
                      disabled={!privacyResult}
                      title="Authorized Brand Manager & Legal Reviewer Reversible Unmasking"
                      style={{ fontSize: "0.72rem", padding: "0.2rem 0.55rem", display: "inline-flex", alignItems: "center", gap: 4 }}
                    >
                      {privacyRestored ? <EyeOff size={12} /> : <Eye size={12} />}
                      {privacyRestored ? "Hide Original" : "Reveal Vault"}
                    </button>
                  </div>
                </div>

                <div className="masked-display-box">
                  {privacyRestored ? (
                    <div style={{ color: "#34d399", whiteSpace: "pre-wrap" }}>{privacyText}</div>
                  ) : privacyResult ? (
                    <div>{privacyResult.redacted_text}</div>
                  ) : (
                    <div style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
                      Click "Scan & Redact Secrets" or select a preset to view contextual masking...
                    </div>
                  )}
                </div>

                {privacyResult && (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.25rem" }}>
                    {Object.entries(privacyResult.categories_found).map(([cat, count]) => (
                      <span key={cat} className="badge-neon in-review" style={{ fontSize: "0.7rem", padding: "0.15rem 0.5rem" }}>
                        {cat}: <strong>{count}</strong>
                      </span>
                    ))}
                    <span style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginLeft: "auto", fontFamily: "var(--font-mono)" }}>
                      SHA-256: {privacyResult.sha256_hash.slice(0, 16)}...
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Tamper-Evident SHA-256 AI Disclosure Ledger */}
            <div className="floating-glass-panel" style={{ marginTop: "1.5rem" }}>
              <div className="panel-header-clean">
                <div>
                  <h2><ShieldCheck size={18} color="var(--cyan)" /> Cryptographic AI Disclosure & Audit Ledger</h2>
                  <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                    Immutable SHA-256 cryptographic audit trail recording model parameters, execution mode, prompt/response digests, and latency.
                  </p>
                </div>
                <button className="btn-subtle-trans" onClick={fetchPrivacyLedger} style={{ fontSize: "0.75rem", padding: "0.3rem 0.7rem" }}>
                  <RefreshCw size={12} /> Refresh Ledger
                </button>
              </div>

              <div className="table-responsive">
                <table className="disclosure-table">
                  <thead>
                    <tr>
                      <th>Ledger ID</th>
                      <th>Execution Mode</th>
                      <th>Model Identifier</th>
                      <th>Prompt SHA-256</th>
                      <th>Response SHA-256</th>
                      <th>Redactions</th>
                      <th>Latency</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {disclosureLedger.slice(0, 8).map((entry) => (
                      <tr key={entry.id}>
                        <td><code>{entry.id}</code></td>
                        <td>
                          <span className={`badge-neon ${entry.execution_mode === "AIR_GAPPED_OFFLINE" ? "approved" : "in-review"}`}>
                            {entry.execution_mode}
                          </span>
                        </td>
                        <td style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{entry.model_identifier}</td>
                        <td><code style={{ fontSize: "0.7rem" }}>{entry.prompt_hash.slice(0, 14)}...</code></td>
                        <td><code style={{ fontSize: "0.7rem" }}>{entry.response_hash.slice(0, 14)}...</code></td>
                        <td><strong>{entry.redaction_count}</strong></td>
                        <td style={{ fontSize: "0.75rem", color: "var(--purple)" }}>{entry.latency_ms} ms</td>
                        <td>
                          <span className="badge-neon approved" style={{ fontSize: "0.68rem" }}>
                            ✓ TAMPER_EVIDENT
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* PILLAR 3: CONTINUOUS GUIDELINE HEALTH & SELF-HEALING GOVERNANCE   */}
        {/* ================================================================= */}
        {activeTab === "governance" && (
          <div className="governance-container">
            <div className="r3-hero-ribbon">
              <div className="r3-hero-left">
                <h2><Zap size={20} color="var(--cyan)" /> Continuous Guideline Health & Self-Healing Governance</h2>
                <p>
                  Adaptive brand intelligence: Analyzes creator disputes, detects policy collisions and contradictory rules,
                  and generates AI-assisted guideline clarifications with 1-click apply and rollback workflows.
                </p>
              </div>
              <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
                <button className="btn-subtle-trans" onClick={fetchGovernanceData} style={{ fontSize: "0.8rem", padding: "0.5rem 0.9rem" }}>
                  <RefreshCw size={13} /> Sync Health Metrics
                </button>
              </div>
            </div>

            {/* Executive Health KPI Cards */}
            {governanceMetrics && (
              <div className="health-metrics-row">
                <div className="health-metric-card">
                  <div className="title">Guideline Health Score</div>
                  <div className="val" style={{ color: governanceMetrics.overall_health_score >= 80 ? "var(--emerald)" : "var(--amber)" }}>
                    {governanceMetrics.overall_health_score}<span style={{ fontSize: "1rem", color: "var(--text-muted)" }}>/100</span>
                  </div>
                  <div className="delta">✓ Evaluated against 18 Active Rules</div>
                </div>

                <div className="health-metric-card">
                  <div className="title">Mean Time to Approval (MTTA)</div>
                  <div className="val" style={{ color: "var(--cyan)" }}>
                    {governanceMetrics.mean_time_to_approval_hours} <span style={{ fontSize: "1rem", fontWeight: 600 }}>hrs</span>
                  </div>
                  <div className="delta">↓ {governanceMetrics.mtta_reduction_pct}% Velocity Improvement</div>
                </div>

                <div className="health-metric-card">
                  <div className="title">Active Policy Collisions</div>
                  <div className="val" style={{ color: governanceMetrics.active_conflicts_count > 0 ? "var(--rose)" : "var(--emerald)" }}>
                    {governanceMetrics.active_conflicts_count}
                  </div>
                  <div className="delta" style={{ color: "var(--text-secondary)" }}>
                    {governanceMetrics.resolved_conflicts_count} Resolved by Self-Healing
                  </div>
                </div>

                <div className="health-metric-card">
                  <div className="title">High-Friction Rules</div>
                  <div className="val" style={{ color: "var(--amber)" }}>
                    {governanceMetrics.high_friction_rules_count}
                  </div>
                  <div className="delta" style={{ color: "var(--text-secondary)" }}>
                    {governanceMetrics.healthy_rules_count} Healthy Rules
                  </div>
                </div>
              </div>
            )}

            {/* Governance Subtabs */}
            <div style={{ display: "flex", gap: "0.5rem", borderBottom: "1px solid var(--border-glass)", paddingBottom: "0.75rem", marginBottom: "1.25rem" }}>
              <button
                className={`tab-pill ${governanceTab === "conflicts" ? "active" : ""}`}
                onClick={() => setGovernanceTab("conflicts")}
              >
                <AlertTriangle size={14} /> Conflicting Guidelines ({conflicts.filter(c => c.status === "ACTIVE_COLLISION").length})
              </button>
              <button
                className={`tab-pill ${governanceTab === "proposals" ? "active" : ""}`}
                onClick={() => setGovernanceTab("proposals")}
              >
                <Sparkles size={14} /> AI Self-Healing Proposals ({proposals.length})
              </button>
              <button
                className={`tab-pill ${governanceTab === "disputes" ? "active" : ""}`}
                onClick={() => setGovernanceTab("disputes")}
              >
                <Activity size={14} /> Rule Dispute Leaderboard ({disputeStats.length})
              </button>
            </div>

            {/* Subtab 1: Conflicting Guidelines & Collisions */}
            {governanceTab === "conflicts" && (
              <div>
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
                  Algorithmic contradiction detection identifies policy collision points where following one brand rule inevitably breaches another.
                </p>

                {conflicts.map((conf) => (
                  <div key={conf.id} className="collision-card">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span className={`badge-neon ${conf.severity === "CRITICAL" ? "changes-requested" : "in-review"}`}>
                          {conf.severity} COLLISION
                        </span>
                        <strong style={{ color: "#fff", fontSize: "0.95rem" }}>{conf.title}</strong>
                      </div>
                      <span className={`badge-neon ${conf.status === "ACTIVE_COLLISION" ? "changes-requested" : "approved"}`}>
                        {conf.status}
                      </span>
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", margin: "0.75rem 0" }}>
                      <div style={{ background: "rgba(15,23,42,0.8)", padding: "0.75rem", borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}>
                        <div style={{ fontSize: "0.7rem", color: "var(--cyan)", fontWeight: 700, textTransform: "uppercase" }}>Rule A: {conf.rule_a_id} ({conf.rule_a_name})</div>
                        <div style={{ fontSize: "0.8rem", color: "#fff", marginTop: "0.25rem", fontStyle: "italic" }}>“{conf.rule_a_excerpt}”</div>
                      </div>
                      <div style={{ background: "rgba(15,23,42,0.8)", padding: "0.75rem", borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}>
                        <div style={{ fontSize: "0.7rem", color: "var(--purple)", fontWeight: 700, textTransform: "uppercase" }}>Rule B: {conf.rule_b_id} ({conf.rule_b_name})</div>
                        <div style={{ fontSize: "0.8rem", color: "#fff", marginTop: "0.25rem", fontStyle: "italic" }}>“{conf.rule_b_excerpt}”</div>
                      </div>
                    </div>

                    <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "0.5rem" }}>
                      <strong>Operational Impact:</strong> {conf.impact_description}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Subtab 2: AI Clarification Proposals & 1-Click Auto-Healing */}
            {governanceTab === "proposals" && (
              <div>
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
                  AI-assisted self-healing proposals synthesize conflicting guidelines into clear, scoped directives. Administrators can approve in 1 click or safely rollback.
                </p>

                {proposals.map((prop) => (
                  <div key={prop.id} className="floating-glass-panel" style={{ marginBottom: "1.25rem" }}>
                    <div className="panel-header-clean">
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <Sparkles size={18} color="var(--cyan)" />
                        <h3 style={{ fontSize: "1rem", color: "#fff", fontWeight: 700 }}>{prop.title}</h3>
                        <span className={`badge-neon ${prop.status === "APPLIED" ? "approved" : prop.status === "ROLLED_BACK" ? "changes-requested" : "in-review"}`}>
                          {prop.status}
                        </span>
                      </div>
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        {prop.status !== "APPLIED" ? (
                          <button
                            className="btn-stamped-approve"
                            onClick={() => handleApplyClarification(prop.id)}
                            style={{ fontSize: "0.78rem", padding: "0.35rem 0.85rem" }}
                          >
                            ⚡ Accept Clarification & Auto-Heal
                          </button>
                        ) : (
                          <button
                            className="btn-vfx-reject"
                            onClick={() => handleRollbackClarification(prop.id)}
                            style={{ fontSize: "0.78rem", padding: "0.35rem 0.85rem" }}
                          >
                            ↺ Rollback Proposal
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="proposal-diff-box">
                      <div className="proposal-diff-col" style={{ borderRight: "1px solid rgba(255,255,255,0.06)", paddingRight: "1rem" }}>
                        <span style={{ fontSize: "0.7rem", color: "var(--rose)", fontWeight: 700, textTransform: "uppercase" }}>Previous Ambiguous Directives:</span>
                        <p style={{ color: "var(--text-secondary)", marginTop: "0.35rem" }}>{prop.original_text}</p>
                      </div>
                      <div className="proposal-diff-col">
                        <span style={{ fontSize: "0.7rem", color: "var(--emerald)", fontWeight: 700, textTransform: "uppercase" }}>Proposed Harmonized Clarification:</span>
                        <p style={{ color: "#fff", fontWeight: 600, marginTop: "0.35rem" }}>{prop.proposed_clarification}</p>
                      </div>
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.75rem", fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                      <span><strong>Rationale:</strong> {prop.rationale}</span>
                      <div style={{ display: "flex", gap: "0.75rem" }}>
                        <span style={{ color: "var(--emerald)" }}>Dispute Reduction: ~{prop.estimated_dispute_reduction_pct}%</span>
                        <span style={{ color: "var(--cyan)" }}>Confidence: {prop.confidence_score}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Subtab 3: Statistical Dispute Leaderboard */}
            {governanceTab === "disputes" && (
              <div>
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
                  Aggregated dispute analytics: Measures rule friction indices based on creator dismissal frequency, false-positive dispute volume, and rejection reasons.
                </p>

                <div className="table-responsive">
                  <table className="vfx-table">
                    <thead>
                      <tr>
                        <th>Rule ID</th>
                        <th>Guideline Title</th>
                        <th>Category</th>
                        <th>Evaluations</th>
                        <th>Disputes</th>
                        <th>Dispute Rate</th>
                        <th>Friction Index</th>
                        <th>Health Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {disputeStats.map((ds) => (
                        <tr key={ds.rule_id}>
                          <td><code>{ds.rule_id}</code></td>
                          <td>
                            <div style={{ fontWeight: 600, color: "#fff" }}>{ds.rule_name}</div>
                            <small style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                              Top reason: “{ds.top_dispute_reasons[0] || 'N/A'}”
                            </small>
                          </td>
                          <td><span className="badge-neon in-review">{ds.category}</span></td>
                          <td>{ds.total_evaluations}</td>
                          <td><strong style={{ color: ds.dispute_count > 10 ? "var(--rose)" : "#fff" }}>{ds.dispute_count}</strong></td>
                          <td>{ds.dispute_rate_pct}%</td>
                          <td>
                            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                              <strong>{ds.friction_index}/10</strong>
                              <div className="friction-bar-track" style={{ width: 60 }}>
                                <div
                                  className="friction-bar-fill"
                                  style={{
                                    width: `${Math.min(100, ds.friction_index * 10)}%`,
                                    background: ds.friction_index >= 3.0 ? "var(--rose)" : ds.friction_index >= 1.5 ? "var(--amber)" : "var(--emerald)"
                                  }}
                                ></div>
                              </div>
                            </div>
                          </td>
                          <td>
                            <span className={`badge-neon ${ds.status === "HEALTHY" ? "approved" : ds.status === "ATTENTION" ? "in-review" : "changes-requested"}`}>
                              {ds.status}
                            </span>
                          </td>
                          <td>
                            <button
                              className="btn-subtle-trans"
                              onClick={() => {
                                setDisputeModal(ds);
                                setDisputeReasonInput("");
                              }}
                              style={{ fontSize: "0.7rem", padding: "0.2rem 0.5rem" }}
                            >
                              File Dispute
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Live Dispute Modal */}
            {disputeModal && (
              <div className="modal-overlay-custom" role="dialog" aria-modal="true" aria-labelledby="modal-disp-title">
                <div className="modal-dialog-custom">
                  <h3 id="modal-disp-title" style={{ color: "#fff", fontSize: "1.05rem", fontWeight: 700 }}>
                    File Dispute on {disputeModal.rule_id}
                  </h3>
                  <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                    Logging disputes feeds the self-healing governance engine to adapt or clarify overly restrictive rules.
                  </p>
                  <div style={{ marginTop: "0.75rem" }}>
                    <label className="meta-label">Dispute Reason & Scenario Context</label>
                    <textarea
                      className="glass-field-textarea"
                      style={{ minHeight: 80 }}
                      placeholder="E.g., Rule conflicts with marketing promotion brief; phrasing was approved by director..."
                      value={disputeReasonInput}
                      onChange={(e) => setDisputeReasonInput(e.target.value)}
                    />
                  </div>
                  <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "1rem" }}>
                    <button className="btn-subtle-trans" onClick={() => setDisputeModal(null)}>Cancel</button>
                    <button className="btn-stamped-approve" onClick={handleSubmitDispute}>Log Dispute Event</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}


        {/* TAB 2: BRAND KNOWLEDGE HUB */}
        {activeTab === "knowledge" && brandKit && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <div>
                <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fff" }}>Brand Knowledge Hub ({brandKit.brand_name})</h2>
                <p style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>
                  Active facts register, numbered brand rules, and prohibited terminology used to substantiate every finding.
                </p>
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button
                  className="btn-subtle-trans"
                  style={{ fontSize: "0.78rem", padding: "0.4rem 0.85rem", display: "flex", alignItems: "center", gap: 4 }}
                  onClick={() => setNewTermModal(true)}
                >
                  <Plus size={13} /> Add Banned Term
                </button>
                <button
                  className="btn-subtle-trans"
                  style={{ fontSize: "0.78rem", padding: "0.4rem 0.85rem", display: "flex", alignItems: "center", gap: 4 }}
                  onClick={() => setNewFactModal(true)}
                >
                  <Plus size={13} /> Add Brand Fact
                </button>
                <button
                  className="btn-subtle-trans"
                  style={{ fontSize: "0.78rem", padding: "0.4rem 0.85rem", display: "flex", alignItems: "center", gap: 4 }}
                  onClick={handleResetBrandKit}
                  title="Reset to defaults"
                >
                  <RotateCcw size={13} /> Reset Baseline
                </button>
              </div>
            </div>

            <div className="responsive-grid-2col">
              {/* Facts Register */}
              <div className="floating-glass-panel">
                <div className="panel-header-clean">
                  <h2><BookOpen size={16} color="var(--cyan)" aria-hidden="true" /> Approved Facts Register</h2>
                  <span className="badge-neon approved">{brandKit.approved_facts.length} Verified</span>
                </div>
                <div style={{ maxHeight: 480, overflowY: "auto" }}>
                  {brandKit.approved_facts.map((fact) => (
                    <div key={fact.id} style={{ background: "rgba(8,12,26,0.7)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "0.8rem", marginBottom: "0.55rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                        <span style={{ fontSize: "0.72rem", fontFamily: "var(--font-mono)", color: "var(--cyan)", fontWeight: 700 }}>{fact.id} · {fact.claim_key}</span>
                        <span className={`badge-neon ${fact.is_active ? "approved" : "changes-requested"}`}>
                          {fact.is_active ? "ACTIVE" : "EXPIRED"}
                        </span>
                      </div>
                      <p style={{ fontSize: "0.86rem", fontWeight: 600, color: "#fff", marginBottom: "0.25rem" }}>“{fact.statement}”</p>
                      <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                        <strong>Source:</strong> {fact.source_document} | <strong>Validity:</strong> {fact.expires_at || "Permanent"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Banned Vocabulary */}
              <div className="floating-glass-panel">
                <div className="panel-header-clean">
                  <h2><AlertTriangle size={16} color="var(--rose)" aria-hidden="true" /> Prohibited Vocabulary</h2>
                  <span className="badge-neon changes-requested">{brandKit.banned_terms.length} Terms</span>
                </div>
                <div style={{ maxHeight: 480, overflowY: "auto" }}>
                  {brandKit.banned_terms.map((term) => (
                    <div key={term.id} style={{ background: "rgba(8,12,26,0.7)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "0.8rem", marginBottom: "0.55rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                        <span style={{ fontSize: "0.84rem", fontWeight: 700, color: "#fda4af", textDecoration: "line-through" }}>{term.term}</span>
                        <span style={{ fontSize: "0.84rem", fontWeight: 700, color: "#6ee7b7" }}>→ {term.suggested_replacement}</span>
                      </div>
                      <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{term.reason}</p>
                      <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>Governed by: {term.rule_id}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: AUDIT TRAIL */}
        {activeTab === "audit" && (
          <div className="floating-glass-panel">
            <div className="panel-header-clean">
              <h2><Activity size={16} color="var(--purple)" aria-hidden="true" /> Immutable Governance Audit Trail</h2>
              <span className="badge-neon approved">Cryptographically Logged</span>
            </div>

            {!reviewResult?.audit_trail || reviewResult.audit_trail.length === 0 ? (
              <p style={{ color: "var(--text-muted)", padding: "3rem", textAlign: "center" }}>
                Run an inspection in the Review Studio to view real-time audit trail logs.
              </p>
            ) : (
              <div className="table-responsive" role="region" aria-label="Governance Audit Trail">
                <table className="vfx-table">
                  <thead>
                    <tr>
                      <th scope="col">Timestamp</th>
                      <th scope="col">Actor & Role</th>
                      <th scope="col">Event Action</th>
                      <th scope="col">Details</th>
                      <th scope="col">SHA-256 Hash</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reviewResult.audit_trail.map((entry) => (
                      <tr key={entry.id}>
                        <td style={{ fontSize: "0.75rem", color: "var(--text-muted)", whiteSpace: "nowrap" }}>{entry.timestamp}</td>
                        <td>
                          <div style={{ fontWeight: 700, color: "#fff" }}>{entry.actor}</div>
                          <div style={{ fontSize: "0.7rem", color: "var(--cyan)" }}>{entry.role}</div>
                        </td>
                        <td>
                          <span className="rule-pill-tag" style={{ fontSize: "0.68rem" }}>{entry.action}</span>
                        </td>
                        <td style={{ fontSize: "0.8rem", maxWidth: 450 }}>{entry.details}</td>
                        <td><code style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{entry.content_hash}</code></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: ACCURACY BENCHMARK */}
        {activeTab === "benchmark" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <div>
                <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fff" }}>Validation Benchmark Suite</h2>
                <p style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>
                  Empirical results across 30 hidden-mistake cases (Terminology, Claims, Expired Facts, Tone).
                </p>
              </div>
              <button
                className="btn-vfx-scan"
                style={{ width: "auto" }}
                onClick={runBenchmark}
                disabled={benchmarkBusy}
              >
                {benchmarkBusy ? <RefreshCw className="spin" size={14} /> : <Award size={14} />}
                {benchmarkBusy ? "Testing 30 Cases..." : "Run Test Suite Now"}
              </button>
            </div>

            {benchmarkData && (
              <>
                <div className="benchmark-stats-strip">
                  <div style={{ background: "rgba(13,20,38,0.7)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "0.75rem", textAlign: "center" }}>
                    <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Total Tests</div>
                    <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "#fff" }}>{benchmarkData.summary.total_tests}</div>
                  </div>
                  <div style={{ background: "rgba(13,20,38,0.7)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "0.75rem", textAlign: "center" }}>
                    <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Passed Tests</div>
                    <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--emerald)" }}>{benchmarkData.summary.passed_tests}</div>
                  </div>
                  <div style={{ background: "rgba(13,20,38,0.7)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "0.75rem", textAlign: "center" }}>
                    <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Accuracy</div>
                    <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--emerald)" }}>{benchmarkData.summary.accuracy_rate_percent}%</div>
                    <small style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>Target: {benchmarkData.summary.target_from_round1}</small>
                  </div>
                  <div style={{ background: "rgba(13,20,38,0.7)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "0.75rem", textAlign: "center" }}>
                    <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Citation Rate</div>
                    <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--cyan)" }}>{benchmarkData.summary.citation_rate_percent}%</div>
                    <small style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>Target: 100%</small>
                  </div>
                  <div style={{ background: "rgba(13,20,38,0.7)", border: "1px solid var(--border-glass)", borderRadius: 10, padding: "0.75rem", textAlign: "center" }}>
                    <div style={{ fontSize: "0.68rem", color: "var(--text-muted)", textTransform: "uppercase" }}>Avg Latency</div>
                    <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--purple)" }}>{benchmarkData.summary.avg_latency_ms} ms</div>
                    <small style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>Near-instant</small>
                  </div>
                </div>

                <div className="floating-glass-panel">
                  <div className="table-responsive" role="region" aria-label="Benchmark Test Cases">
                    <table className="vfx-table">
                      <thead>
                        <tr>
                          <th scope="col">Test ID</th>
                          <th scope="col">Scenario Name</th>
                          <th scope="col">Text Under Test</th>
                          <th scope="col">Expected</th>
                          <th scope="col">Detected</th>
                          <th scope="col">Latency</th>
                          <th scope="col">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {benchmarkData.cases.map((c) => (
                          <tr key={c.id}>
                            <td><strong>{c.id}</strong></td>
                            <td style={{ fontWeight: 600 }}>{c.title}</td>
                            <td style={{ maxWidth: 300, fontSize: "0.78rem", color: "var(--text-secondary)" }}>“{c.sample_text}”</td>
                            <td><span className="badge-neon auto-checked">{c.expected_count} issues</span></td>
                            <td><span className="badge-neon in-review">{c.detected_count} found</span></td>
                            <td style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{c.latency_ms} ms</td>
                            <td>
                              <span className={`badge-neon ${c.passed ? "approved" : "changes-requested"}`}>
                                {c.passed ? "PASSED" : "FAILED"}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB 5: ROUND 3 ROADMAP */}
        {activeTab === "roadmap" && commitments && (
          <div>
            <div style={{ marginBottom: "1rem" }}>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fff" }}>Three Major Improvements Committed for Round 3</h2>
              <p style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>
                Mandatory CodeTitans commitment: Meaningful functional expansions beyond cosmetic changes.
              </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1rem" }}>
              {commitments.improvements.map((imp) => (
                <div key={imp.id} className="floating-glass-panel">
                  <div className="panel-header-clean">
                    <h2>
                      <span style={{ background: "var(--blue)", color: "#fff", width: 24, height: 24, borderRadius: "50%", display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", marginRight: 8 }}>
                        {imp.id}
                      </span>
                      {imp.title}
                    </h2>
                    <span className="badge-neon auto-checked">Round 3 Deliverable</span>
                  </div>

                  <p style={{ fontSize: "0.88rem", color: "#fff" }}>
                    {imp.scope}
                  </p>

                  <h5 style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "var(--text-muted)" }}>
                    Planned Technical Capabilities:
                  </h5>
                  <ul style={{ paddingLeft: "1.25rem", fontSize: "0.82rem", color: "var(--text-secondary)" }}>
                    {imp.capabilities.map((cap, i) => (
                      <li key={i} style={{ marginBottom: "0.25rem" }}>{cap}</li>
                    ))}
                  </ul>

                  <div style={{ background: "rgba(6,182,212,0.1)", border: "1px solid rgba(6,182,212,0.25)", padding: "0.75rem", borderRadius: 8, fontSize: "0.8rem", color: "#38bdf8" }}>
                    <strong>User-Facing Deliverable:</strong> {imp.deliverables}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        </main>

        {/* Semantic Accessible Footer */}
        <footer role="contentinfo" className="brandguard-footer">
          <div>
            <strong>BrandGuard</strong> · Pre-Publication Autonomous Brand Governance · Team <strong>WHO CARES?</strong>
          </div>
          <div className="footer-links">
            <a href="/docs" target="_blank" rel="noopener noreferrer">Interactive API Docs</a>
            <span aria-hidden="true">·</span>
            <a href="https://github.com/Rhythmuppal18/BrandGuard" target="_blank" rel="noopener noreferrer">GitHub Repository</a>
            <span aria-hidden="true">·</span>
            <span>CodeTitans India 2026</span>
          </div>
        </footer>
      </div>

      {/* Modal: Add Banned Term */}
      {newTermModal && (
        <div className="modal-overlay-custom" role="dialog" aria-modal="true" aria-labelledby="modal-term-title">
          <div className="modal-dialog-custom">
            <h3 id="modal-term-title" style={{ color: "#fff", fontSize: "1.1rem", fontWeight: 700 }}>Add Prohibited Term to Brand Rules</h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              The rule engine will automatically enforce this term with case-adaptive replacement.
            </p>
            <div>
              <label className="meta-label" htmlFor="modal-term-input">Prohibited Term or Phrase</label>
              <input
                id="modal-term-input"
                type="text"
                className="glass-field-input"
                placeholder="e.g. cheap, free money, crypto"
                value={newTermForm.term}
                onChange={(e) => setNewTermForm({ ...newTermForm, term: e.target.value })}
                aria-label="Prohibited Term or Phrase"
              />
            </div>
            <div>
              <label className="meta-label" htmlFor="modal-term-replace">Approved Replacement</label>
              <input
                id="modal-term-replace"
                type="text"
                className="glass-field-input"
                placeholder="e.g. cost-effective, digital asset"
                value={newTermForm.suggested_replacement}
                onChange={(e) => setNewTermForm({ ...newTermForm, suggested_replacement: e.target.value })}
                aria-label="Approved Replacement"
              />
            </div>
            <div>
              <label className="meta-label" htmlFor="modal-term-reason">Policy Rationale</label>
              <input
                id="modal-term-reason"
                type="text"
                className="glass-field-input"
                placeholder="e.g. Diminishes brand enterprise positioning."
                value={newTermForm.reason}
                onChange={(e) => setNewTermForm({ ...newTermForm, reason: e.target.value })}
                aria-label="Policy Rationale"
              />
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
              <button className="btn-subtle-trans" onClick={() => setNewTermModal(false)} aria-label="Cancel adding term">Cancel</button>
              <button className="btn-stamped-approve" onClick={handleAddTerm} aria-label="Save Prohibited Term">Save Prohibited Term</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Add Approved Fact */}
      {newFactModal && (
        <div className="modal-overlay-custom" role="dialog" aria-modal="true" aria-labelledby="modal-fact-title">
          <div className="modal-dialog-custom">
            <h3 id="modal-fact-title" style={{ color: "#fff", fontSize: "1.1rem", fontWeight: 700 }}>Add Verified Brand Fact</h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              Add a factual proposition to the approved knowledge base for claim corroboration.
            </p>
            <div>
              <label className="meta-label" htmlFor="modal-fact-key">Claim Identifier / Topic</label>
              <input
                id="modal-fact-key"
                type="text"
                className="glass-field-input"
                placeholder="e.g. market_rank_2026, uptime_sla"
                value={newFactForm.claim_key}
                onChange={(e) => setNewFactForm({ ...newFactForm, claim_key: e.target.value })}
                aria-label="Claim Identifier"
              />
            </div>
            <div>
              <label className="meta-label" htmlFor="modal-fact-statement">Approved Factual Statement</label>
              <textarea
                id="modal-fact-statement"
                className="glass-field-textarea"
                style={{ minHeight: 70 }}
                placeholder="e.g. ApexPay guarantees 99.99% multi-region uptime."
                value={newFactForm.statement}
                onChange={(e) => setNewFactForm({ ...newFactForm, statement: e.target.value })}
                aria-label="Approved Factual Statement"
              />
            </div>
            <div>
              <label className="meta-label" htmlFor="modal-fact-source">Verification Source Document</label>
              <input
                id="modal-fact-source"
                type="text"
                className="glass-field-input"
                placeholder="e.g. SOC2 Type II Report 2026, Section 4.2"
                value={newFactForm.source_document}
                onChange={(e) => setNewFactForm({ ...newFactForm, source_document: e.target.value })}
                aria-label="Verification Source Document"
              />
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
              <button className="btn-subtle-trans" onClick={() => setNewFactModal(false)} aria-label="Cancel adding fact">Cancel</button>
              <button className="btn-stamped-approve" onClick={handleAddFact} aria-label="Register Approved Fact">Register Approved Fact</button>
            </div>
          </div>
        </div>
      )}

      {/* Dismissal Modal */}
      {rejectionModal && (
        <div className="modal-overlay-custom" role="dialog" aria-modal="true" aria-labelledby="modal-dismiss-title">
          <div className="modal-dialog-custom">
            <h3 id="modal-dismiss-title" style={{ marginBottom: "0.35rem", color: "#fff", fontSize: "1rem" }}>Dismiss Suggestion</h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "0.85rem" }}>
              Dismissing a rule flag for “{rejectionModal.originalText}” requires a brief reason. This helps BrandGuard detect ambiguous or outdated guidelines.
            </p>
            <textarea
              className="glass-field-textarea"
              style={{ minHeight: 80, marginBottom: "0.85rem" }}
              placeholder="E.g., Legal exception granted for this partner announcement..."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              aria-label="Reason for dismissing rule suggestion"
            />
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
              <button
                className="btn-subtle-trans"
                style={{ padding: "0.35rem 0.85rem", fontSize: "0.78rem" }}
                onClick={() => setRejectionModal(null)}
                aria-label="Cancel dismissal"
              >
                Cancel
              </button>
              <button
                className="btn-vfx-reject"
                onClick={() => {
                  handleSuggestion(rejectionModal.changeId, "reject", rejectionReason || "Creator dismissed");
                  setRejectionModal(null);
                }}
                aria-label="Confirm dismissal"
              >
                Confirm Dismissal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
