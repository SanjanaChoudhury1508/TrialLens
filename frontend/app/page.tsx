"use client";

import { FormEvent, useState } from "react";

interface Source {
  document_id: string;
  trial_id: string | null;
  source_type: string;
  section?: string;
  content?: string;
  relevance_score?: number;
}

interface AskResponse {
  question: string;
  answer: string;
  sources: Source[];
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data: AskResponse = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(
        "Unable to connect to TrialLens. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f7f8fa] text-slate-900">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              TrialLens
            </h1>
            <p className="text-sm text-slate-500">
              Citation-grounded clinical trial research assistant
            </p>
          </div>

          <div className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-xs font-medium text-slate-600">
            Clinical Research AI
          </div>
        </div>
      </header>

      {/* Main */}
      <section className="mx-auto max-w-4xl px-6 py-16">
        {/* Hero */}
        <div className="mb-10 text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-blue-600">
            Evidence-based research
          </p>

          <h2 className="text-4xl font-bold tracking-tight text-slate-900">
            Ask questions about clinical trials.
          </h2>

          <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-slate-500">
            Search across indexed clinical trial documents and receive
            answers grounded in retrieved evidence.
          </p>
        </div>

        {/* Search box */}
        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm"
        >
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask something like: What were the coprimary endpoints of the A-BRAVE trial?"
            rows={4}
            className="w-full resize-none rounded-xl border-0 bg-transparent px-4 py-3 text-base outline-none placeholder:text-slate-400"
          />

          <div className="flex items-center justify-between border-t border-slate-100 px-2 pt-3">
            <span className="text-xs text-slate-400">
              Answers are generated from indexed evidence.
            </span>

            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {loading ? "Researching..." : "Ask TrialLens"}
            </button>
          </div>
        </form>

        {/* Error */}
        {error && (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-8 text-center">
            <div className="mx-auto mb-4 h-7 w-7 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600" />
            <p className="text-sm font-medium text-slate-700">
              Searching clinical evidence...
            </p>
            <p className="mt-1 text-xs text-slate-400">
              Retrieving, reranking and generating an evidence-grounded answer
            </p>
          </div>
        )}

        {/* Answer */}
        {result && !loading && (
          <div className="mt-10 space-y-6">
            <section className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
              <div className="mb-5 flex items-center justify-between">
                <h3 className="text-lg font-bold text-slate-900">
                  Answer
                </h3>

                <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700">
                  Evidence grounded
                </span>
              </div>

              <div className="whitespace-pre-wrap text-[15px] leading-7 text-slate-700">
                {result.answer}
              </div>
            </section>

            {/* Sources */}
            <section>
              <div className="mb-4">
                <h3 className="text-lg font-bold text-slate-900">
                  Sources
                </h3>
                <p className="mt-1 text-sm text-slate-500">
                  Evidence retrieved from the TrialLens knowledge base.
                </p>
              </div>

              <div className="space-y-4">
                {result.sources.map((source, index) => (
                  <details
                    key={`${source.document_id}-${source.section}-${index}`}
                    className="group rounded-2xl border border-slate-200 bg-white shadow-sm"
                  >
                    <summary className="cursor-pointer list-none px-6 py-5">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-sm font-semibold text-slate-900">
                            {source.document_id}
                          </p>

                          <div className="mt-2 flex flex-wrap gap-2">
                            {source.trial_id && (
                              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                                {source.trial_id}
                              </span>
                            )}

                            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
                              {source.source_type}
                            </span>
                          </div>
                        </div>

                        <span className="text-xs text-slate-400">
                          Evidence {index + 1}
                        </span>
                      </div>

                      {source.section && (
                        <p className="mt-4 text-sm font-medium text-slate-600">
                          {source.section}
                        </p>
                      )}
                    </summary>

                    {source.content && (
                      <div className="border-t border-slate-100 px-6 py-5">
                        <p className="text-sm leading-6 text-slate-600">
                          {source.content}
                        </p>
                      </div>
                    )}
                  </details>
                ))}
              </div>
            </section>
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-6 text-center text-xs text-slate-400">
          TrialLens · Citation-grounded clinical trial research
        </div>
      </footer>
    </main>
  );
}