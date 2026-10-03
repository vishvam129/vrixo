"use client";

/* eslint-disable @next/next/no-img-element -- images are authenticated blobs, not static assets */

import type { Job } from "@/lib/api";
import { operationById } from "@/lib/operations";
import { cn } from "@/lib/utils";
import { useImage } from "@/lib/use-image";

export const STATUS_LABEL: Record<Job["status"], string> = {
  queued: "Waiting",
  running: "Working",
  succeeded: "Done",
  failed: "Failed",
};

function Frame({
  job,
  number,
  selected,
  onSelect,
}: {
  job: Job;
  number: number;
  selected: boolean;
  onSelect: () => void;
}) {
  const done = job.status === "succeeded";
  const active = job.status === "queued" || job.status === "running";
  const image = useImage(done ? `/jobs/${job.id}/result` : `/uploads/${job.upload_id}/file`);
  const operation = operationById(job.operation);

  return (
    <li>
      <button
        type="button"
        onClick={onSelect}
        aria-current={selected}
        aria-label={`Photo ${number}: ${operation.name}, ${STATUS_LABEL[job.status].toLowerCase()}`}
        className={cn(
          "block w-32 shrink-0 bg-surface p-1.5 text-left outline-offset-2 lg:w-full",
          selected && "bg-signal",
        )}
      >
        <span
          className={cn(
            "block aspect-[3/2] overflow-hidden bg-film",
            operation.transparent && done && "checker",
          )}
        >
          {image && (
            <img
              src={image}
              alt=""
              className={cn("h-full w-full object-cover", active && "developing", job.status === "failed" && "opacity-30 grayscale")}
            />
          )}
        </span>
        <span className="mt-1.5 flex items-baseline justify-between gap-2">
          <span className="font-display text-base leading-none font-semibold">{number}</span>
          <span className={cn("truncate text-xs", job.status === "failed" ? "text-destructive" : "text-graphite", selected && "text-ink")}>
            {done ? operation.name : STATUS_LABEL[job.status]}
          </span>
        </span>
      </button>
    </li>
  );
}

/** The user's photos as a strip of film, newest first. Frame numbers are their order. */
export function FilmStrip({
  jobs,
  selectedId,
  onSelect,
}: {
  jobs: Job[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  if (jobs.length === 0) {
    return (
      <div className="film-strip film-strip-vertical flex min-h-28 items-center px-6 py-5 lg:h-full lg:px-5 lg:py-6">
        <p className="bg-surface px-3 py-2 text-sm text-graphite">Your finished photos will line up here.</p>
      </div>
    );
  }
  return (
    <nav aria-label="Your photos" className="film-strip film-strip-vertical lg:h-full">
      <ol className="flex gap-1.5 overflow-x-auto px-1.5 py-5 lg:max-h-[calc(100vh-6rem)] lg:flex-col lg:overflow-x-visible lg:overflow-y-auto lg:px-5 lg:py-2">
        {jobs.map((job, index) => (
          <Frame
            key={job.id}
            job={job}
            number={jobs.length - index}
            selected={job.id === selectedId}
            onSelect={() => onSelect(job.id)}
          />
        ))}
      </ol>
    </nav>
  );
}
