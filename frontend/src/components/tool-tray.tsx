"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { OPERATIONS } from "@/lib/operations";
import { cn } from "@/lib/utils";

export type ToolState = {
  operation: string;
  scale: 2 | 4 | 8;
  restoreFaces: boolean;
  colorize: boolean;
  repairScratches: boolean;
};

export const DEFAULT_TOOL: ToolState = {
  operation: "upscale",
  scale: 4,
  restoreFaces: false,
  colorize: true,
  repairScratches: true,
};

/** The API parameters for the chosen tool. */
export function paramsFor(tool: ToolState): Record<string, unknown> {
  if (tool.operation === "upscale") return { scale: tool.scale, face_optimized: tool.restoreFaces };
  if (tool.operation === "restore")
    return { colorize: tool.colorize, repair_scratches: tool.repairScratches };
  return {};
}

function Toggle({
  id,
  label,
  checked,
  onChange,
}: {
  id: string;
  label: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <Label htmlFor={id} className="font-normal">
        {label}
      </Label>
      <Switch id={id} checked={checked} onCheckedChange={onChange} />
    </div>
  );
}

export function ToolTray({
  tool,
  onChange,
  onRun,
  disabledReason,
  running,
  fixedOptions = false,
}: {
  tool: ToolState;
  onChange: (tool: ToolState) => void;
  onRun: () => void;
  disabledReason: string | null;
  running: boolean;
  /** Demo mode: results are pre-made, so the options cannot change them. */
  fixedOptions?: boolean;
}) {
  const selected = OPERATIONS.find((operation) => operation.id === tool.operation)!;

  return (
    <section aria-labelledby="tools-heading" className="flex flex-col">
      <h2 id="tools-heading" className="font-display text-2xl font-semibold">
        What should Vrixo do?
      </h2>

      <div role="radiogroup" aria-labelledby="tools-heading" className="mt-4 border-t border-border">
        {OPERATIONS.map((operation) => {
          const active = operation.id === tool.operation;
          return (
            <button
              key={operation.id}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => onChange({ ...tool, operation: operation.id })}
              className={cn(
                "flex w-full items-start gap-3 border-b border-border px-1 py-3 text-left",
                active ? "bg-surface" : "hover:bg-surface/60",
              )}
            >
              <span
                aria-hidden
                className={cn(
                  "mt-1 size-3.5 shrink-0 rounded-full border border-ink",
                  active && "border-4 border-ink bg-signal",
                )}
              />
              <span>
                <span className="block font-medium">{operation.name}</span>
                <span className="block text-sm text-graphite">{operation.description}</span>
              </span>
            </button>
          );
        })}
      </div>

      {fixedOptions && tool.operation === "upscale" && (
        <p className="mt-5 text-sm text-graphite">
          The sample was upscaled 4× with face restoration on.
        </p>
      )}

      {!fixedOptions && tool.operation === "upscale" && (
        <div className="mt-5 grid gap-4">
          <fieldset>
            <legend className="text-sm font-medium">How much larger</legend>
            <div className="mt-2 grid grid-cols-3 border border-ink">
              {([2, 4, 8] as const).map((scale) => (
                <button
                  key={scale}
                  type="button"
                  aria-pressed={tool.scale === scale}
                  onClick={() => onChange({ ...tool, scale })}
                  className={cn(
                    "h-10 border-r border-ink font-display text-xl font-semibold last:border-r-0",
                    tool.scale === scale ? "bg-ink text-surface" : "hover:bg-surface",
                  )}
                >
                  {scale}×
                </button>
              ))}
            </div>
          </fieldset>
          <Toggle
            id="restore-faces"
            label="Also restore faces"
            checked={tool.restoreFaces}
            onChange={(restoreFaces) => onChange({ ...tool, restoreFaces })}
          />
        </div>
      )}

      {!fixedOptions && tool.operation === "restore" && (
        <div className="mt-5 grid gap-4">
          <Toggle
            id="repair-scratches"
            label="Repair scratches"
            checked={tool.repairScratches}
            onChange={(repairScratches) => onChange({ ...tool, repairScratches })}
          />
          <Toggle
            id="colorize"
            label="Correct faded colour"
            checked={tool.colorize}
            onChange={(colorize) => onChange({ ...tool, colorize })}
          />
        </div>
      )}

      <Button
        onClick={onRun}
        disabled={disabledReason !== null || running}
        aria-describedby={disabledReason ? "run-hint" : undefined}
        className="mt-6 h-12 w-full bg-signal text-base font-semibold text-ink hover:bg-signal/85"
      >
        {running ? "Sending…" : selected.name}
      </Button>
      {disabledReason && (
        <p id="run-hint" className="mt-2 text-sm text-graphite">
          {disabledReason}
        </p>
      )}
    </section>
  );
}
