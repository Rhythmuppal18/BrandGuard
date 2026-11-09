import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import confetti from "canvas-confetti";
import {
  ShieldCheck, AlertTriangle, CheckCircle2, FileText, Upload, RefreshCw,
  Check, X, Award, BookOpen, Activity, Sparkles, Layers, Wand2, Download,
  Sliders, SplitSquareVertical, FileCheck, ArrowRight, UserCheck, Eye,
  Edit3, HelpCircle, Plus, RotateCcw, Info
} from "lucide-react";
import "./styles.css";

const API_BASE = "http://127.0.0.1:8000/api";

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
              <div className="brand-icon-shield">
                <ShieldCheck size={26} className="shield-svg" />
              </div>
            </div>
            <div className="brand-heading">
              <div className="brand-title-row">
                <h1 className="brand-title-text">
                  Brand<span className="brand-accent-text">Guard</span>
                </h1>
                <span className="cyber-beacon-pill">
                  <span className="beacon-core"></span>
                  ROUND 2 BUILD
                </span>
              </div>
              <div className="brand-subline">
                <span className="brand-subline-main">Autonomous Brand Governance Platform</span>
                <span className="brand-subline-dot">·</span>
                <span className="brand-subline-team">Team WHO CARES?</span>
              </div>
            </div>
          </div>

          {/* Floating Navigation Dock */}
          <nav className="floating-tabs">
            <button
              className={`tab-pill ${activeTab === "studio" ? "active" : ""}`}
              onClick={() => setActiveTab("studio")}
            >
              <Layers size={14} /> Review Studio
            </button>
            <button
              className={`tab-pill ${activeTab === "knowledge" ? "active" : ""}`}
              onClick={() => setActiveTab("knowledge")}
            >
              <BookOpen size={14} /> Brand Hub
            </button>
            <button
              className={`tab-pill ${activeTab === "audit" ? "active" : ""}`}
              onClick={() => setActiveTab("audit")}
            >
              <Activity size={14} /> Audit Trail
            </button>
            <button
              className={`tab-pill ${activeTab === "benchmark" ? "active" : ""}`}
              onClick={() => { setActiveTab("benchmark"); if (!benchmarkData) runBenchmark(); }}
            >
              <Award size={14} /> Benchmark (30 Cases)
            </button>
            <button
              className={`tab-pill ${activeTab === "roadmap" ? "active" : ""}`}
              onClick={() => setActiveTab("roadmap")}
            >
              <Sparkles size={14} /> Round 3 Plan
            </button>
          </nav>

          {/* Role Pill with Pulsing LED */}
          <div className="role-floating-capsule">
            <div className="pulse-led"></div>
            <select
              className="role-select-native"
              value={currentRole}
              onChange={(e) => setCurrentRole(e.target.value)}
            >
              <option value="Creator">Content Creator</option>
              <option value="Brand Manager">Brand Manager</option>
              <option value="Legal & Compliance Reviewer">Legal Reviewer</option>
              <option value="Brand Admin">Brand Admin</option>
            </select>
          </div>
        </header>

        {/* 4-Step Sleek Stepper */}
        <div className="stepper-dock">
          <div className={`step-node ${activeStep >= 1 ? (activeStep > 1 ? "completed" : "active") : ""}`}>
            <div className="step-circle">{activeStep > 1 ? "✓" : "1"}</div>
            <span>01. Content Input</span>
          </div>
          <div className="step-divider-line"></div>
          <div className={`step-node ${activeStep >= 2 ? (activeStep > 2 ? "completed" : "active") : ""}`}>
            <div className="step-circle">{activeStep > 2 ? "✓" : "2"}</div>
            <span>02. Multi-Layer Scan</span>
          </div>
          <div className="step-divider-line"></div>
          <div className={`step-node ${activeStep >= 3 ? (activeStep > 3 ? "completed" : "active") : ""}`}>
            <div className="step-circle">{activeStep > 3 ? "✓" : "3"}</div>
            <span>03. Tracked Changes & Fix</span>
          </div>
          <div className="step-divider-line"></div>
          <div className={`step-node ${activeStep === 4 ? "completed active" : ""}`}>
            <div className="step-circle">{activeStep === 4 ? "★" : "4"}</div>
            <span>04. Human Sign-Off & Stamped Clearance</span>
          </div>
        </div>

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
                    <label className="meta-label">Document Title</label>
                    <input
                      type="text"
                      className="glass-field-input"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Title or Campaign Name"
                    />
                  </div>
                  <div>
                    <label className="meta-label">Target Channel</label>
                    <select
                      className="glass-field-select"
                      value={contentType}
                      onChange={(e) => setContentType(e.target.value)}
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
                    <label className="meta-label" style={{ margin: 0 }}>
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
                      className="glass-field-textarea"
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      placeholder="Enter or paste copy to verify against brand rules, tone guidelines, and verified facts..."
                      rows={8}
                    />
                  ) : (
                    renderInteractiveInspector()
                  )}
                </div>

                {/* Hologram File Upload Dropzone */}
                <label className="hologram-file-dropzone">
                  <input
                    type="file"
                    style={{ display: "none" }}
                    accept=".pdf,.docx,.txt,.md"
                    onChange={handleFileUpload}
                  />
                  <Upload size={18} color="var(--cyan)" />
                  <span>Drop Word (.docx) or PDF document to auto-extract and review</span>
                </label>

                <button
                  className="btn-vfx-scan"
                  onClick={runReview}
                  disabled={busy || !content.trim()}
                >
                  {busy ? <RefreshCw className="spin" size={17} /> : <Wand2 size={17} />}
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

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
              {/* Facts Register */}
              <div className="floating-glass-panel">
                <div className="panel-header-clean">
                  <h2><BookOpen size={16} color="var(--cyan)" /> Approved Facts Register</h2>
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
                  <h2><AlertTriangle size={16} color="var(--rose)" /> Prohibited Vocabulary</h2>
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
              <h2><Activity size={16} color="var(--purple)" /> Immutable Governance Audit Trail</h2>
              <span className="badge-neon approved">Cryptographically Logged</span>
            </div>

            {!reviewResult?.audit_trail || reviewResult.audit_trail.length === 0 ? (
              <p style={{ color: "var(--text-muted)", padding: "3rem", textAlign: "center" }}>
                Run an inspection in the Review Studio to view real-time audit trail logs.
              </p>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table className="vfx-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Actor & Role</th>
                      <th>Event Action</th>
                      <th>Details</th>
                      <th>SHA-256 Hash</th>
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
                <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "0.75rem", marginBottom: "1rem" }}>
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
                  <div style={{ overflowX: "auto" }}>
                    <table className="vfx-table">
                      <thead>
                        <tr>
                          <th>Test ID</th>
                          <th>Scenario Name</th>
                          <th>Text Under Test</th>
                          <th>Expected</th>
                          <th>Detected</th>
                          <th>Latency</th>
                          <th>Status</th>
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
      </div>

      {/* Modal: Add Banned Term */}
      {newTermModal && (
        <div className="modal-overlay-custom">
          <div className="modal-dialog-custom">
            <h3 style={{ color: "#fff", fontSize: "1.1rem", fontWeight: 700 }}>Add Prohibited Term to Brand Rules</h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              The rule engine will automatically enforce this term with case-adaptive replacement.
            </p>
            <div>
              <label className="meta-label">Prohibited Term or Phrase</label>
              <input
                type="text"
                className="glass-field-input"
                placeholder="e.g. cheap, free money, crypto"
                value={newTermForm.term}
                onChange={(e) => setNewTermForm({ ...newTermForm, term: e.target.value })}
              />
            </div>
            <div>
              <label className="meta-label">Approved Replacement</label>
              <input
                type="text"
                className="glass-field-input"
                placeholder="e.g. cost-effective, digital asset"
                value={newTermForm.suggested_replacement}
                onChange={(e) => setNewTermForm({ ...newTermForm, suggested_replacement: e.target.value })}
              />
            </div>
            <div>
              <label className="meta-label">Policy Rationale</label>
              <input
                type="text"
                className="glass-field-input"
                placeholder="e.g. Diminishes brand enterprise positioning."
                value={newTermForm.reason}
                onChange={(e) => setNewTermForm({ ...newTermForm, reason: e.target.value })}
              />
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
              <button className="btn-subtle-trans" onClick={() => setNewTermModal(false)}>Cancel</button>
              <button className="btn-stamped-approve" onClick={handleAddTerm}>Save Prohibited Term</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Add Approved Fact */}
      {newFactModal && (
        <div className="modal-overlay-custom">
          <div className="modal-dialog-custom">
            <h3 style={{ color: "#fff", fontSize: "1.1rem", fontWeight: 700 }}>Add Verified Brand Fact</h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              Add a factual proposition to the approved knowledge base for claim corroboration.
            </p>
            <div>
              <label className="meta-label">Claim Identifier / Topic</label>
              <input
                type="text"
                className="glass-field-input"
                placeholder="e.g. market_rank_2026, uptime_sla"
                value={newFactForm.claim_key}
                onChange={(e) => setNewFactForm({ ...newFactForm, claim_key: e.target.value })}
              />
            </div>
            <div>
              <label className="meta-label">Approved Factual Statement</label>
              <textarea
                className="glass-field-textarea"
                style={{ minHeight: 70 }}
                placeholder="e.g. ApexPay guarantees 99.99% multi-region uptime."
                value={newFactForm.statement}
                onChange={(e) => setNewFactForm({ ...newFactForm, statement: e.target.value })}
              />
            </div>
            <div>
              <label className="meta-label">Verification Source Document</label>
              <input
                type="text"
                className="glass-field-input"
                placeholder="e.g. SOC2 Type II Report 2026, Section 4.2"
                value={newFactForm.source_document}
                onChange={(e) => setNewFactForm({ ...newFactForm, source_document: e.target.value })}
              />
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
              <button className="btn-subtle-trans" onClick={() => setNewFactModal(false)}>Cancel</button>
              <button className="btn-stamped-approve" onClick={handleAddFact}>Register Approved Fact</button>
            </div>
          </div>
        </div>
      )}

      {/* Dismissal Modal */}
      {rejectionModal && (
        <div className="modal-overlay-custom">
          <div className="modal-dialog-custom">
            <h3 style={{ marginBottom: "0.35rem", color: "#fff", fontSize: "1rem" }}>Dismiss Suggestion</h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "0.85rem" }}>
              Dismissing a rule flag for “{rejectionModal.originalText}” requires a brief reason. This helps BrandGuard detect ambiguous or outdated guidelines.
            </p>
            <textarea
              className="glass-field-textarea"
              style={{ minHeight: 80, marginBottom: "0.85rem" }}
              placeholder="E.g., Legal exception granted for this partner announcement..."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
            />
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
              <button
                className="btn-subtle-trans"
                style={{ padding: "0.35rem 0.85rem", fontSize: "0.78rem" }}
                onClick={() => setRejectionModal(null)}
              >
                Cancel
              </button>
              <button
                className="btn-vfx-reject"
                onClick={() => {
                  handleSuggestion(rejectionModal.changeId, "reject", rejectionReason || "Creator dismissed");
                  setRejectionModal(null);
                }}
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
