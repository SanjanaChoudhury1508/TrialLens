"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";

interface Source {
  document_id: string;
  trial_id: string;
  source_type: string;
  section: string;
  content: string;
  relevance_score: number;
}

interface AskResponse {
  question: string;
  answer: string;
  sources: Source[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const EXAMPLE_QUESTIONS = [
  "What were the coprimary endpoints of the A-BRAVE trial?",
  "What treatment was evaluated in the A-BRAVE trial?",
  "Did avelumab significantly improve disease-free survival?",
  "What was the overall survival hazard ratio?",
];

const LOADING_STEPS = [
  "Searching clinical evidence…",
  "Reranking relevant sources…",
  "Generating evidence-grounded answer…",
];

function formatSourceType(sourceType: string): string {
  return sourceType.replace(/[_-]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatDocumentName(documentId: string): string {
  return documentId.replace(/[_-]/g, " ");
}

/** Grows the textarea to fit its content (capped), instead of always reserving a
 *  fixed number of rows — keeps the box compact for short questions. */
function autoResizeTextarea(el: HTMLTextAreaElement) {
  el.style.height = "auto";
  el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
}

/** Renders answer text, turning numbered/bulleted plain-text lines into real lists. */
function AnswerBody({ text }: { text: string }) {
  const blocks = text.trim().split(/\n\s*\n/);

  return (
    <div className="space-y-4 text-[1.05rem] leading-[1.75] text-ink">
      {blocks.map((block, i) => {
        const lines = block
          .split("\n")
          .map((l) => l.trim())
          .filter(Boolean);
        const isNumbered = lines.length > 1 && lines.every((l) => /^\d+[.)]\s+/.test(l));
        const isBulleted = lines.length > 1 && lines.every((l) => /^[-*•]\s+/.test(l));

        if (isNumbered) {
          return (
            <ol key={i} className="list-decimal space-y-2 pl-5 marker:font-medium marker:text-accent">
              {lines.map((l, j) => (
                <li key={j}>{l.replace(/^\d+[.)]\s+/, "")}</li>
              ))}
            </ol>
          );
        }
        if (isBulleted) {
          return (
            <ul key={i} className="list-disc space-y-2 pl-5 marker:text-accent">
              {lines.map((l, j) => (
                <li key={j}>{l.replace(/^[-*•]\s+/, "")}</li>
              ))}
            </ul>
          );
        }
        return <p key={i}>{block}</p>;
      })}
    </div>
  );
}

/**
 * Displays the raw cross-encoder reranker score (cross-encoder/ms-marco-MiniLM-L-6-v2).
 * This is NOT a probability or percentage — it's an unbounded relevance score — so it
 * is shown as-is, never normalized into a percentage or a progress bar.
 */
function ScoreBadge({ score }: { score: number }) {
  return (
    <span
      className="shrink-0 font-mono text-sm font-semibold text-ink-soft"
      title="Reranker score (cross-encoder/ms-marco-MiniLM-L-6-v2)"
    >
      {score.toFixed(2)}
    </span>
  );
}

function EvidenceCard({
  source,
  index,
  isExpanded,
  onToggle,
}: {
  source: Source;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const preview = source.content.length > 160 ? `${source.content.slice(0, 160).trim()}…` : source.content;
  const panelId = `evidence-panel-${index}`;
  const hasScore = typeof source.relevance_score === "number" && !Number.isNaN(source.relevance_score);

  return (
    <li className="relative pl-9">
      <span
        className="absolute left-0 top-1 flex h-7 w-7 items-center justify-center rounded-full border border-border-strong bg-surface font-mono text-xs font-medium text-ink-soft"
        aria-hidden="true"
      >
        {index + 1}
      </span>
      <div className="rounded-xl border border-border bg-surface p-4 transition-shadow hover:shadow-md">
        {/* Document name is repeated across many chunks from the same source, so it
            stays visually secondary to the trial ID — but readable, not near-invisible. */}
        <p className="mb-1.5 truncate text-xs text-ink-soft" title={formatDocumentName(source.document_id)}>
          {formatDocumentName(source.document_id)}
        </p>

        {/* Trial ID + source type are the differentiating identifiers, so they carry
            the most visual weight in the card header. */}
        <div className="mb-2 flex flex-wrap items-baseline gap-x-1.5 font-mono text-sm">
          <span className="font-semibold text-ink">{source.trial_id}</span>
          <span aria-hidden="true" className="text-ink-faint">·</span>
          <span className="text-ink-soft">{formatSourceType(source.source_type)}</span>
        </div>

        {source.section && (
          <p className="mb-3 inline-block rounded bg-accent-soft px-2 py-0.5 text-[0.7rem] font-semibold uppercase tracking-wide text-accent-strong">
            {source.section}
          </p>
        )}

        <div id={panelId} className="whitespace-pre-line text-sm leading-relaxed text-ink-soft">
          {isExpanded ? source.content : preview}
        </div>

        <div className="mt-3 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={onToggle}
            aria-expanded={isExpanded}
            aria-controls={panelId}
            className="focus-ring inline-flex items-center gap-1 rounded text-sm font-medium text-accent hover:text-accent-strong"
          >
            {isExpanded ? "Hide evidence" : "View evidence"}
            <span aria-hidden="true" className={`inline-block transition-transform ${isExpanded ? "rotate-90" : ""}`}>
              →
            </span>
          </button>
          {hasScore && <ScoreBadge score={source.relevance_score} />}
        </div>
      </div>
    </li>
  );
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingStep, setLoadingStep] = useState(0);
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isLoading) return;
    setLoadingStep(0);
    const id = setInterval(() => {
      setLoadingStep((s) => (s + 1) % LOADING_STEPS.length);
    }, 1500);
    return () => clearInterval(id);
  }, [isLoading]);

  useEffect(() => {
    if (textareaRef.current) autoResizeTextarea(textareaRef.current);
  }, [question]);

  async function askQuestion(rawQuestion: string) {
    const trimmed = rawQuestion.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      const data: AskResponse = await res.json();
      setResult(data);
      setSubmittedQuestion(trimmed);
      setExpanded({});
    } catch {
      setError("TrialLens couldn't retrieve an answer right now. Check that the backend is running and try again.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    askQuestion(question);
  }

  function handleExampleClick(example: string) {
    setQuestion(example);
    textareaRef.current?.focus();
  }

  const hasResult = !!result && !isLoading;

  return (
    <div className="min-h-screen bg-bg font-sans text-ink antialiased">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <header className="sticky top-0 z-30 border-b border-border bg-surface/95 backdrop-blur supports-[backdrop-filter]:bg-surface/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <span className="font-display text-xl font-semibold tracking-tight text-ink">TrialLens</span>
            <span className="hidden text-sm text-ink-faint sm:inline">
              Citation-grounded clinical trial research assistant
            </span>
          </div>
          <span className="inline-flex shrink-0 items-center rounded-full border border-accent/20 bg-accent-soft px-3 py-1 font-mono text-[0.7rem] font-medium uppercase tracking-wide text-accent-strong">
            Clinical Research AI
          </span>
        </div>
      </header>

      <main id="main-content" className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <section className="mb-6 max-w-2xl lg:mb-8">
          <p className="mb-3 font-mono text-xs font-semibold uppercase tracking-widest text-accent">
            Evidence-based research
          </p>
          <h1 className="font-display text-3xl font-semibold leading-tight text-ink sm:text-4xl">
            Ask questions about clinical trials.
          </h1>
          <p className="mt-3 text-base leading-relaxed text-ink-soft">
            Search across indexed clinical trial documents and receive answers grounded in retrieved evidence, with
            every claim traceable to its source.
          </p>
        </section>

        <section aria-label="Ask TrialLens a question" className="mb-12">
          <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-border bg-surface p-3 shadow-sm sm:p-4"
          >
            <label htmlFor="question" className="sr-only">
              Your clinical research question
            </label>
            <textarea
              id="question"
              ref={textareaRef}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  askQuestion(question);
                }
              }}
              placeholder="e.g. What were the coprimary endpoints of the A-BRAVE trial?"
              rows={2}
              disabled={isLoading}
              className="focus-ring w-full resize-none overflow-y-auto rounded-lg bg-transparent p-2 text-base leading-relaxed text-ink placeholder:text-ink-faint disabled:opacity-60"
            />
            <div className="flex flex-col-reverse items-start justify-between gap-3 border-t border-border px-2 pt-3 sm:flex-row sm:items-center">
              <p className="text-xs text-ink-faint">Answers are generated from indexed evidence, not general knowledge.</p>
              <button
                type="submit"
                disabled={isLoading || !question.trim()}
                className="focus-ring inline-flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-accent-strong disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
              >
                {isLoading ? (
                  <>
                    <span
                      className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/40 border-t-white"
                      aria-hidden="true"
                    />
                    Searching…
                  </>
                ) : (
                  "Ask TrialLens"
                )}
              </button>
            </div>
          </form>

          {isLoading && (
            <p role="status" aria-live="polite" className="mt-3 text-sm text-ink-faint">
              {LOADING_STEPS[loadingStep]}
            </p>
          )}

          {error && (
            <div role="alert" className="mt-4 rounded-xl border border-danger/20 bg-danger-soft px-4 py-3 text-sm">
              <p className="font-medium text-danger">Something went wrong</p>
              <p className="mt-1 text-danger/90">{error}</p>
              <button
                type="button"
                onClick={() => askQuestion(question)}
                className="focus-ring mt-2 inline-flex items-center rounded text-sm font-medium text-danger underline underline-offset-2"
              >
                Try again
              </button>
            </div>
          )}
        </section>

        {hasResult && result && (
          <section className="grid gap-8 lg:grid-cols-[minmax(0,1.7fr)_minmax(300px,1fr)] lg:items-start">
            <div className="animate-fade-up rounded-2xl border border-border bg-surface p-5 shadow-sm sm:p-6">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-border pb-3">
                <h2 className="font-display text-xl font-semibold text-ink">Answer</h2>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-trust-soft px-3 py-1 text-xs font-medium text-trust">
                  <span className="h-1.5 w-1.5 rounded-full bg-trust" aria-hidden="true" />
                  Evidence grounded
                </span>
              </div>
              <p className="mb-3 text-sm text-ink-faint">{submittedQuestion}</p>
              <AnswerBody text={result.answer} />
            </div>

            {/* Heading/description stay put; only the card list beneath scrolls, so a
                long source list never stretches the page and leaves a tall blank gap
                next to a shorter answer. On mobile/tablet (below lg) this is just a
                normal block flowing beneath the answer, full width, no scroll container. */}
            <div className="lg:sticky lg:top-24">
              <div className="mb-4">
                <h2 className="mb-1 font-display text-lg font-semibold text-ink">Sources</h2>
                <p className="text-sm text-ink-faint">Evidence retrieved from the TrialLens knowledge base.</p>
              </div>

              {result.sources.length > 0 ? (
                <div className="sources-rail lg:max-h-[calc(100vh-14rem)] lg:overflow-y-auto lg:pr-1">
                  <ul className="evidence-rail space-y-3">
                    {result.sources.map((source, i) => (
                      <EvidenceCard
                        key={`${source.document_id}-${i}`}
                        source={source}
                        index={i}
                        isExpanded={!!expanded[i]}
                        onToggle={() => setExpanded((prev) => ({ ...prev, [i]: !prev[i] }))}
                      />
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="rounded-xl border border-border bg-surface-muted p-4 text-sm text-ink-faint">
                  No supporting evidence was returned for this answer.
                </p>
              )}
            </div>
          </section>
        )}

        {!hasResult && !isLoading && !error && (
          <section aria-label="Example questions" className="max-w-2xl">
            <p className="mb-3 text-sm font-medium text-ink-soft">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_QUESTIONS.map((example) => (
                <button
                  key={example}
                  type="button"
                  onClick={() => handleExampleClick(example)}
                  className="focus-ring rounded-full border border-border bg-surface px-4 py-2 text-left text-sm text-ink-soft transition-colors hover:border-accent/40 hover:bg-accent-soft hover:text-accent-strong"
                >
                  {example}
                </button>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="border-t border-border py-8">
        <p className="text-center text-sm text-ink-faint">TrialLens · Citation-grounded clinical trial research</p>
      </footer>
    </div>
  );
}