"use client";

/* eslint-disable @next/next/no-img-element -- images are authenticated blobs, not static assets */

import { useRef, useState, type DragEvent } from "react";
import { cn } from "@/lib/utils";

/** Draggable before / after comparison. The range input makes it keyboard-operable. */
export function Compare({
  before,
  after,
  transparent,
}: {
  before: string;
  after: string;
  transparent?: boolean;
}) {
  const [position, setPosition] = useState(50);
  return (
    <div className={cn("relative h-full w-full select-none", transparent && "checker")}>
      <img src={after} alt="Result" className="absolute inset-0 h-full w-full object-contain" />
      <img
        src={before}
        alt="Original"
        className="absolute inset-0 h-full w-full bg-surface object-contain"
        style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}
      />
      <span className="pointer-events-none absolute top-3 left-3 bg-ink px-2 py-0.5 text-xs text-surface">
        Before
      </span>
      <span className="pointer-events-none absolute top-3 right-3 bg-signal px-2 py-0.5 text-xs text-ink">
        After
      </span>
      <div
        aria-hidden
        className="pointer-events-none absolute inset-y-0 w-0.5 bg-ink"
        style={{ left: `${position}%` }}
      >
        <span className="absolute top-1/2 left-1/2 grid size-8 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full bg-ink text-xs text-surface">
          ◂▸
        </span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={position}
        onChange={(event) => setPosition(Number(event.target.value))}
        aria-label="Compare before and after"
        className="absolute inset-0 h-full w-full cursor-ew-resize opacity-0"
      />
    </div>
  );
}

export const ACCEPTED = ["image/jpeg", "image/png", "image/webp"];

/** Empty table: the invitation to add a photo. */
export function DropZone({ onFile, busy }: { onFile: (file: File) => void; busy: boolean }) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);

  function drop(event: DragEvent) {
    event.preventDefault();
    setOver(false);
    const file = event.dataTransfer.files[0];
    if (file) onFile(file);
  }

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={drop}
      className={cn(
        "grid h-full w-full place-items-center border-2 border-dashed border-input p-6 text-center transition-colors",
        over && "border-ink bg-signal/15",
      )}
    >
      <div>
        <p className="font-display text-4xl font-semibold">
          {busy ? "Uploading…" : "Drop a photo here"}
        </p>
        <p className="mt-2 text-graphite">JPEG, PNG or WebP, up to 10 MB.</p>
        <button
          type="button"
          disabled={busy}
          onClick={() => input.current?.click()}
          className="mt-6 h-11 bg-ink px-5 font-medium text-surface hover:bg-ink/85 disabled:opacity-50"
        >
          Choose a photo
        </button>
        <input
          ref={input}
          type="file"
          accept={ACCEPTED.join(",")}
          className="sr-only"
          aria-label="Choose a photo"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) onFile(file);
            event.target.value = "";
          }}
        />
      </div>
    </div>
  );
}
