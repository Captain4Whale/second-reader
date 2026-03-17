import { ArrowRight, LoaderCircle, Upload } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router";
import { fetchJobStatus, JobStatusResponse, toWebSocketUrl, uploadEpub } from "../lib/api";
import { canonicalBookAnalysisPath, canonicalBookPath } from "../lib/contract";
import { uiTypography } from "../lib/visual-system";

const jobStageLabels: Record<JobStatusResponse["status"], string> = {
  queued: "Preparing your book",
  parsing_structure: "Reading the structure",
  ready: "Structure is ready",
  deep_reading: "Reading and annotating",
  chapter_note_generation: "Finishing chapter reactions",
  paused: "Paused, ready to continue",
  completed: "Ready to open",
  error: "Needs attention",
};

function AnalysisTarget({ job }: { job: JobStatusResponse }) {
  if (!job.book_id) {
    return null;
  }

  const target = job.status === "completed" ? canonicalBookPath(job.book_id) : canonicalBookAnalysisPath(job.book_id);

  return (
    <Link
      to={target}
      data-testid="upload-open-current-result"
      className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--amber-accent)] text-white no-underline hover:bg-[var(--warm-700)] transition-colors"
      style={uiTypography.control}
    >
      Open current result
      <ArrowRight className="w-4 h-4" />
    </Link>
  );
}

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState<JobStatusResponse | null>(null);

  useEffect(() => {
    if (!job?.job_id || !job.ws_url || job.status === "completed" || job.status === "error") {
      return;
    }

    const socket = new WebSocket(toWebSocketUrl(job.ws_url));
    socket.onmessage = () => {
      void fetchJobStatus(job.job_id).then(setJob).catch(() => undefined);
    };

    return () => {
      socket.close();
    };
  }, [job?.job_id, job?.status, job?.ws_url]);

  useEffect(() => {
    if (!job?.job_id || job.status === "completed" || job.status === "error") {
      return;
    }

    const timer = window.setInterval(() => {
      void fetchJobStatus(job.job_id).then(setJob).catch(() => undefined);
    }, 3000);

    return () => {
      window.clearInterval(timer);
    };
  }, [job?.job_id, job?.status]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Please select an EPUB file.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const accepted = await uploadEpub(file);
      const nextJob = await fetchJobStatus(accepted.job_id);
      setJob(nextJob);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Upload failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_0.8fr] gap-6">
        <form onSubmit={handleSubmit} className="bg-white rounded-3xl border border-[var(--warm-300)]/30 p-8 shadow-sm">
          <p className="text-[var(--amber-accent)] uppercase tracking-[0.18em] mb-2" style={uiTypography.eyebrow}>
            Upload EPUB
          </p>
          <h1 className="text-[var(--warm-900)] mb-3" style={uiTypography.pageTitle}>
            Start a new deep-reading run
          </h1>
          <p className="text-[var(--warm-600)] mb-8" style={uiTypography.body}>
            Upload an EPUB to begin a guided reading run. This page will keep up with the book as it moves from structure to chapter results.
          </p>

          <label className="block mb-4">
            <span className="block text-[var(--warm-700)] mb-2" style={uiTypography.metaMedium}>
              EPUB file
            </span>
            <input
              type="file"
              accept=".epub,application/epub+zip"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              data-testid="upload-input"
              className="block w-full rounded-xl border border-[var(--warm-300)]/50 bg-[var(--warm-50)] px-4 py-3 text-[var(--warm-700)]"
            />
          </label>

          {file ? (
            <p className="text-[var(--warm-500)] mb-4" style={uiTypography.caption}>
              Selected file: {file.name}
            </p>
          ) : null}

          {error ? (
            <p className="text-[var(--destructive)] mb-4" style={uiTypography.caption}>
              {error}
            </p>
          ) : null}

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={submitting}
              data-testid="upload-submit"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-[var(--amber-accent)] text-white hover:bg-[var(--warm-700)] transition-colors disabled:opacity-60 cursor-pointer"
              style={uiTypography.control}
            >
              {submitting ? <LoaderCircle className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              {submitting ? "Uploading..." : "Upload and analyze"}
            </button>
            <Link
              to="/books"
              className="text-[var(--warm-600)] no-underline hover:text-[var(--warm-800)]"
              style={uiTypography.control}
            >
              Back to books
            </Link>
          </div>
        </form>

        <div className="bg-white rounded-3xl border border-[var(--warm-300)]/30 p-8 shadow-sm">
          <p className="text-[var(--amber-accent)] uppercase tracking-[0.18em] mb-2" style={uiTypography.eyebrow}>
            Job Status
          </p>
          {!job ? (
            <p className="text-[var(--warm-600)]" style={uiTypography.body}>
              No upload is in progress in this tab yet. Once you submit an EPUB, this panel will follow the run until it is ready to open.
            </p>
          ) : (
            <div className="space-y-4">
              <div>
                <p className="text-[var(--warm-500)] mb-1" style={uiTypography.chip}>
                  Stage
                </p>
                <p className="text-[var(--warm-900)]" style={uiTypography.bodyStrong}>
                  {jobStageLabels[job.status]}
                </p>
              </div>

              {job.book_title ? (
                <div>
                  <p className="text-[var(--warm-500)] mb-1" style={uiTypography.chip}>
                    Book
                  </p>
                  <p className="text-[var(--warm-900)]" style={uiTypography.bodyStrong}>
                    {job.book_title}
                  </p>
                </div>
              ) : null}

              {job.progress_percent != null ? (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[var(--warm-500)]" style={uiTypography.chip}>
                      Progress
                    </span>
                    <span className="text-[var(--warm-700)]" style={uiTypography.chip}>
                      {Math.round(job.progress_percent)}%
                    </span>
                  </div>
                  <div className="h-2 bg-[var(--warm-200)] rounded-full overflow-hidden">
                    <div className="h-full bg-[var(--amber-accent)]" style={{ width: `${job.progress_percent}%` }} />
                  </div>
                </div>
              ) : null}

              {job.last_error ? (
                <p className="text-[var(--destructive)]" style={uiTypography.caption}>
                  {job.last_error.message}
                </p>
              ) : null}

              <AnalysisTarget job={job} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
