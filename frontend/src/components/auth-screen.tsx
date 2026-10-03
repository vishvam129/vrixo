"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, ApiError } from "@/lib/api";
import { OPERATIONS } from "@/lib/operations";

export function AuthScreen({ onSignedIn }: { onSignedIn: () => void }) {
  const [mode, setMode] = useState<"signup" | "login">("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const action = mode === "signup" ? "Create account" : "Sign in";

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await (mode === "signup" ? api.signup(email, password) : api.login(email, password));
      onSignedIn();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "Something went wrong. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto grid min-h-screen max-w-6xl items-center gap-12 px-6 py-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,420px)]">
      <section>
        <p className="font-display text-2xl font-semibold tracking-wide">Vrixo</p>
        <h1 className="mt-10 max-w-[11ch] font-display text-6xl leading-[0.92] font-bold sm:text-8xl">
          Fix a photo in one step.
        </h1>
        <p className="mt-6 max-w-md text-lg text-graphite">
          Upload a photo, choose what to do with it, and download the result.
        </p>

        {/* the five tools, laid out as a strip of film */}
        <ol className="film-strip mt-10 flex max-w-xl gap-1.5 overflow-x-auto px-1.5 py-5">
          {OPERATIONS.map((operation, index) => (
            <li key={operation.id} className="min-w-28 flex-1 bg-surface px-3 py-3">
              <span className="font-display text-sm font-semibold text-graphite">{index + 1}</span>
              <span className="mt-4 block text-sm leading-snug font-medium">{operation.name}</span>
            </li>
          ))}
        </ol>
      </section>

      <form onSubmit={submit} className="border border-border bg-surface p-7" noValidate={false}>
        <h2 className="font-display text-3xl font-semibold">{action}</h2>

        <div className="mt-6 grid gap-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="h-10 bg-white"
          />
        </div>
        <div className="mt-4 grid gap-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            aria-describedby="password-hint"
            className="h-10 bg-white"
          />
          {mode === "signup" && (
            <p id="password-hint" className="text-sm text-graphite">
              At least 8 characters.
            </p>
          )}
        </div>

        {error && (
          <p role="alert" className="mt-4 border-l-2 border-destructive pl-3 text-sm text-destructive">
            {error}
          </p>
        )}

        <Button type="submit" disabled={busy} className="mt-6 h-11 w-full bg-signal text-base text-ink hover:bg-signal/85">
          {busy ? "One moment…" : action}
        </Button>

        <p className="mt-5 text-sm text-graphite">
          {mode === "signup" ? "Already have an account?" : "New to Vrixo?"}{" "}
          <button
            type="button"
            onClick={() => {
              setMode(mode === "signup" ? "login" : "signup");
              setError(null);
            }}
            className="font-medium text-ink underline underline-offset-4"
          >
            {mode === "signup" ? "Sign in" : "Create account"}
          </button>
        </p>
      </form>
    </main>
  );
}
