import { FormEvent, useMemo, useState } from "react";

type ApiResponse = {
  report: string;
};

type ReportSection = {
  title: string;
  body: string;
};

const sampleIdea =
  "I want to build an app that helps remote software teams reduce unnecessary meetings by identifying repeated status calls and suggesting async updates.";

const reportHighlights = [
  "10-section validation brief",
  "MVP and landing page copy",
  "Practical 7-day action plan"
];

function normalizeSectionTitle(title: string) {
  return title
    .replace(/#+\s*$/g, "")
    .replace(/^\d+\.\s*/, "")
    .trim()
    .replace(/^[*_]+|[*_]+$/g, "")
    .replace(/[^a-z0-9]+/gi, " ")
    .trim()
    .toLowerCase();
}

const expectedSectionTitles = new Set(
  [
    "Idea Summary",
    "Target Customer",
    "Pain Point",
    "Value Proposition",
    "MVP Scope",
    "Landing Page Copy",
    "Validation Experiments",
    "Risks",
    "7-Day Action Plan",
    "Short Pitch"
  ].map(normalizeSectionTitle)
);

function splitReport(markdown: string): ReportSection[] {
  const normalized = markdown.trim();
  if (!normalized) {
    return [];
  }

  const matches = [...normalized.matchAll(/^#{1,6}\s+(.+)$/gm)].filter((match) =>
    expectedSectionTitles.has(normalizeSectionTitle(match[1]))
  );

  if (matches.length !== expectedSectionTitles.size) {
    return [{ title: "StartupSpark Report", body: normalized }];
  }

  return matches.map((match, index) => {
    const start = (match.index ?? 0) + match[0].length;
    const end =
      index + 1 < matches.length ? matches[index + 1].index ?? normalized.length : normalized.length;

    return {
      title: match[1].trim(),
      body: normalized.slice(start, end).trim()
    };
  });
}

function renderMarkdownBlock(markdown: string) {
  const lines = markdown.split(/\r?\n/);

  return lines.map((line, index) => {
    const key = `${index}-${line}`;
    const trimmed = line.trim();

    if (!trimmed) {
      return <div className="line-break" key={key} />;
    }

    if (trimmed.startsWith("### ")) {
      return (
        <h4 className="subheading" key={key}>
          {trimmed.replace(/^###\s+/, "")}
        </h4>
      );
    }

    if (/^[-*]\s+/.test(trimmed)) {
      return (
        <li className="bullet" key={key}>
          {trimmed.replace(/^[-*]\s+/, "")}
        </li>
      );
    }

    if (/^\d+\.\s+/.test(trimmed)) {
      return (
        <p className="numbered" key={key}>
          {trimmed}
        </p>
      );
    }

    return (
      <p className="paragraph" key={key}>
        {trimmed}
      </p>
    );
  });
}

function downloadMarkdown(report: string) {
  const blob = new Blob([report], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "startup-spark-report.md";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export default function App() {
  const [idea, setIdea] = useState(sampleIdea);
  const [saveAs, setSaveAs] = useState("");
  const [report, setReport] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copyLabel, setCopyLabel] = useState("Copy report");

  const reportSections = useMemo(() => splitReport(report), [report]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setReport("");
    setCopyLabel("Copy report");

    if (idea.trim().length < 10) {
      setError("Enter a startup idea with at least 10 characters.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/generate-report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          idea: idea.trim(),
          save_as: saveAs.trim() || null
        })
      });

      const data = (await response.json()) as ApiResponse | { detail?: string };

      if (!response.ok) {
        throw new Error("detail" in data ? data.detail : "The backend returned an error.");
      }

      setReport((data as ApiResponse).report);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "StartupSpark could not generate a report."
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function copyReport() {
    if (!report) {
      return;
    }

    await navigator.clipboard.writeText(report);
    setCopyLabel("Copied");
    window.setTimeout(() => setCopyLabel("Copy report"), 1600);
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">StartupSpark</p>
          <h1>Turn a rough idea into a founder-ready validation brief.</h1>
          <p className="hero-text">
            Use your local Google ADK agent to pressure-test a startup concept, scope a
            lean MVP, draft landing page copy, and plan the first week of validation.
          </p>
          <div className="hero-metrics" aria-label="StartupSpark output highlights">
            {reportHighlights.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </div>
        <div className="hero-panel" aria-label="Workflow">
          <p className="panel-label">Workflow</p>
          <div>
            <strong>1. Describe</strong>
            <span>Paste the raw idea, even if it is messy.</span>
          </div>
          <div>
            <strong>2. Generate</strong>
            <span>The backend calls your ADK agent, not the browser.</span>
          </div>
          <div>
            <strong>3. Review</strong>
            <span>Read, copy, download, or save the Markdown report.</span>
          </div>
        </div>
      </section>

      <section className="workspace">
        <form className="input-card" onSubmit={handleSubmit}>
          <div className="section-heading">
            <p className="eyebrow">Input</p>
            <h2>Founder brief</h2>
            <p>Describe who it helps, what hurts, and what outcome you want to create.</p>
          </div>

          <label htmlFor="idea">Startup idea</label>
          <textarea
            id="idea"
            value={idea}
            onChange={(event) => setIdea(event.target.value)}
            placeholder="Example: A tool that helps solo founders interview customers and summarize validation insights into clear next steps."
            rows={9}
          />

          <label htmlFor="saveAs">Save as Markdown (optional)</label>
          <input
            id="saveAs"
            value={saveAs}
            onChange={(event) => setSaveAs(event.target.value)}
            placeholder="remote-team-meeting-reducer"
          />

          <button className="primary-button" disabled={isLoading} type="submit">
            {isLoading ? "Generating report..." : "Generate validation report"}
          </button>

          {error && <div className="error-box">{error}</div>}
        </form>

        <section className="preview-card" aria-live="polite">
          <div className="preview-header">
            <div>
              <p className="eyebrow">Output</p>
              <h2>Validation report</h2>
            </div>
            <div className="actions">
              <button disabled={!report} onClick={copyReport} type="button">
                {copyLabel}
              </button>
              <button disabled={!report} onClick={() => downloadMarkdown(report)} type="button">
                Download .md
              </button>
            </div>
          </div>

          {isLoading && (
            <div className="loading-state">
              <div className="spinner" />
              <p>StartupSpark is drafting the founder brief...</p>
            </div>
          )}

          {!isLoading && !report && !error && (
            <div className="empty-state">
              <p className="empty-kicker">Ready when you are</p>
              <h3>Your validation brief will appear here</h3>
              <p>
                Expect practical sections for customer, pain, MVP, landing page copy,
                validation experiments, risks, action plan, and pitch.
              </p>
              <div className="empty-checklist" aria-label="Expected report sections">
                <span>Customer</span>
                <span>MVP</span>
                <span>Experiments</span>
                <span>Risks</span>
                <span>Pitch</span>
              </div>
            </div>
          )}

          {!isLoading && report && (
            <div className="report-grid">
              {reportSections.map((section) => (
                <article className="report-section" key={section.title}>
                  <h3>{section.title}</h3>
                  <div>{renderMarkdownBlock(section.body)}</div>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
