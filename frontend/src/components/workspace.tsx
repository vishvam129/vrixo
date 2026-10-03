"use client";

/* eslint-disable @next/next/no-img-element -- images are authenticated blobs, not static assets */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { FilmStrip, STATUS_LABEL } from "@/components/film-strip";
import { ACCEPTED, Compare, DropZone } from "@/components/light-table";
import { DEFAULT_TOOL, paramsFor, ToolTray, type ToolState } from "@/components/tool-tray";
import { api, describeError, token, type Job, type Upload, type User } from "@/lib/api";
import { DEMO, DEMO_UPLOAD, REPO_URL } from "@/lib/demo";
import { operationById } from "@/lib/operations";
import { clearImageCache, useImage } from "@/lib/use-image";

const MAX_BYTES = 10 * 1024 * 1024;
const isActive = (job: Job) => job.status === "queued" || job.status === "running";

export function Workspace({ user, onSignedOut }: { user: User; onSignedOut: () => void }) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  // uploaded, nothing run on it yet (the demo starts with its sample photo on the table)
  const [draft, setDraft] = useState<Upload | null>(DEMO ? DEMO_UPLOAD : null);
  const [tool, setTool] = useState<ToolState>(DEFAULT_TOOL);
  const [uploading, setUploading] = useState(false);
  const [sending, setSending] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const known = useRef(new Map<string, Job["status"]>());

  const selected = useMemo(
    () => jobs.find((job) => job.id === selectedId) ?? null,
    [jobs, selectedId],
  );
  const photo = selected?.upload ?? draft;
  const anyActive = jobs.some(isActive);

  /** Store the latest jobs and announce any that just finished. */
  const absorb = useCallback((next: Job[]) => {
    for (const job of next) {
      const before = known.current.get(job.id);
      if (before && before !== job.status) {
        if (job.status === "succeeded") toast(operationById(job.operation).done);
        if (job.status === "failed") toast.error(`${operationById(job.operation).name} failed`);
      }
      known.current.set(job.id, job.status);
    }
    setJobs(next);
  }, []);

  useEffect(() => {
    api
      .listJobs()
      .then((loaded) => {
        absorb(loaded);
        if (loaded.length > 0) setSelectedId(loaded[0].id);
      })
      .catch((error) => toast.error(describeError(error)));
  }, [absorb]);

  // while something is waiting or working, ask the server once a second
  useEffect(() => {
    if (!anyActive) return;
    const timer = window.setInterval(() => {
      setNow(Date.now());
      api.listJobs().then(absorb).catch(() => {});
    }, 1000);
    return () => window.clearInterval(timer);
  }, [anyActive, absorb]);

  async function addPhoto(file: File) {
    if (!ACCEPTED.includes(file.type)) {
      toast.error("That file isn't a JPEG, PNG or WebP image.");
      return;
    }
    if (file.size > MAX_BYTES) {
      toast.error("That photo is larger than 10 MB. Choose a smaller one.");
      return;
    }
    setUploading(true);
    try {
      setDraft(await api.upload(file));
      setSelectedId(null);
    } catch (error) {
      toast.error(describeError(error));
    } finally {
      setUploading(false);
    }
  }

  async function run() {
    if (!photo) return;
    setSending(true);
    try {
      const job = await api.createJob(photo.id, tool.operation, paramsFor(tool));
      known.current.set(job.id, job.status);
      setJobs((current) => [job, ...current]);
      setSelectedId(job.id);
      setDraft(null);
      setNow(Date.now());
      if (job.status === "succeeded") toast(operationById(job.operation).done); // already finished
    } catch (error) {
      toast.error(describeError(error));
    } finally {
      setSending(false);
    }
  }

  function signOut() {
    token.clear();
    clearImageCache();
    onSignedOut();
  }

  const original = useImage(photo ? `/uploads/${photo.id}/file` : null);
  const result = useImage(
    selected?.status === "succeeded" ? `/jobs/${selected.id}/result` : null,
  );
  const operation = selected ? operationById(selected.operation) : null;
  const elapsed = selected
    ? Math.max(0, Math.round((now - new Date(selected.queued_at).getTime()) / 1000))
    : 0;

  return (
    <div className="mx-auto grid min-h-screen max-w-[1500px] grid-rows-[auto_1fr]">
      <header className="flex items-center gap-4 border-b border-border px-5 py-3">
        <p className="font-display text-2xl leading-none font-semibold tracking-wide">Vrixo</p>
        <p className="ml-auto hidden truncate text-sm text-graphite sm:block">{user.email}</p>
        {DEMO ? (
          <a href={REPO_URL} className="text-sm font-medium underline underline-offset-4">
            Source on GitHub
          </a>
        ) : (
          <button
            type="button"
            onClick={signOut}
            className="text-sm font-medium underline underline-offset-4"
          >
            Sign out
          </button>
        )}
      </header>

      <div className="grid grid-cols-1 gap-x-6 gap-y-5 px-5 py-5 lg:grid-cols-[176px_minmax(0,1fr)_300px]">
        <div className="order-3 -mx-5 min-w-0 lg:order-1 lg:mx-0">
          <FilmStrip jobs={jobs} selectedId={selectedId} onSelect={setSelectedId} />
        </div>

        <main className="order-1 min-w-0 lg:order-2">
          <h1 className="sr-only">Your photo</h1>
          {DEMO && (
            <p className="mb-4 border-l-4 border-signal bg-surface px-4 py-3 text-sm">
              This is a demo with one sample photo. Each result was made by Vrixo&apos;s models and
              saved; nothing is processed here.{" "}
              <a href={`${REPO_URL}#getting-started`} className="font-medium underline underline-offset-4">
                Run it on your machine
              </a>{" "}
              to use your own photos.
            </p>
          )}
          <div className="relative h-[min(62vh,640px)] min-h-72 border border-border bg-surface">
            {!photo && <DropZone onFile={addPhoto} busy={uploading} />}

            {photo && result && original && (
              <Compare before={original} after={result} transparent={operation?.transparent} />
            )}

            {photo && !result && (
              <>
                {original && (
                  <img
                    src={original}
                    alt={photo.filename}
                    className={`absolute inset-0 h-full w-full object-contain ${selected && isActive(selected) ? "developing" : ""}`}
                  />
                )}
                {selected && isActive(selected) && (
                  <p
                    role="status"
                    className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-ink px-4 py-2 text-sm whitespace-nowrap text-surface"
                  >
                    {selected.status === "queued"
                      ? "Waiting for its turn"
                      : `${STATUS_LABEL.running} on it, ${elapsed} s so far`}
                  </p>
                )}
                {selected?.status === "failed" && (
                  <div
                    role="alert"
                    className="absolute inset-x-4 bottom-4 border-l-4 border-destructive bg-surface p-4"
                  >
                    <p className="font-medium">{operation?.name} didn&apos;t finish.</p>
                    <p className="mt-1 text-sm text-graphite">
                      {selected.error ?? "The server didn't say why."} Pick a tool and run it
                      again, or try a different photo.
                    </p>
                  </div>
                )}
              </>
            )}
          </div>

          {DEMO && (
            <p className="mt-2 text-xs text-graphite">Sample photo: NASA, public domain.</p>
          )}
          {photo && (
            <div className="mt-4 flex flex-wrap items-start gap-x-10 gap-y-4">
              <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
                <dt className="text-graphite">File</dt>
                <dd className="truncate font-medium">{photo.filename}</dd>
                <dt className="text-graphite">Size</dt>
                <dd>
                  {photo.width} × {photo.height} px
                </dd>
                {selected?.status === "succeeded" && operation && (
                  <>
                    <dt className="text-graphite">Result</dt>
                    <dd>
                      {operation.done} in {((selected.duration_ms ?? 0) / 1000).toFixed(1)} s
                      {DEMO && " when it was recorded, on a laptop CPU"}
                    </dd>
                  </>
                )}
              </dl>

              <div className="ml-auto flex flex-wrap gap-3">
                {result && selected && (
                  <a
                    href={result}
                    download={`vrixo-${selected.operation}.${result.endsWith(".jpg") ? "jpg" : "png"}`}
                    className="grid h-11 place-items-center bg-ink px-5 font-medium text-surface hover:bg-ink/85"
                  >
                    Download result
                  </a>
                )}
                {!DEMO && (
                <label className="grid h-11 cursor-pointer place-items-center border border-ink px-5 font-medium hover:bg-surface has-focus-visible:outline-2">
                  {uploading ? "Uploading…" : "Use another photo"}
                  <input
                    type="file"
                    accept={ACCEPTED.join(",")}
                    className="sr-only"
                    disabled={uploading}
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (file) addPhoto(file);
                      event.target.value = "";
                    }}
                  />
                </label>
                )}
              </div>
            </div>
          )}
        </main>

        <aside className="order-2 lg:order-3">
          <ToolTray
            tool={tool}
            onChange={setTool}
            onRun={run}
            running={sending}
            disabledReason={photo ? null : "Add a photo first."}
            fixedOptions={DEMO}
          />
        </aside>
      </div>
    </div>
  );
}
