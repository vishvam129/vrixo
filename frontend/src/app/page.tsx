"use client";

import { useCallback, useEffect, useState } from "react";
import { AuthScreen } from "@/components/auth-screen";
import { Workspace } from "@/components/workspace";
import { api, token, type User } from "@/lib/api";

type Session = { state: "checking" } | { state: "signed-out" } | { state: "signed-in"; user: User };

/** Who is signed in, judging by the stored token (cleared if the server rejects it). */
async function currentSession(): Promise<Session> {
  if (!token.get()) return { state: "signed-out" };
  try {
    return { state: "signed-in", user: await api.me() };
  } catch {
    token.clear(); // expired or invalid
    return { state: "signed-out" };
  }
}

export default function Home() {
  const [session, setSession] = useState<Session>({ state: "checking" });

  const load = useCallback(async () => {
    setSession(await currentSession());
  }, []);

  useEffect(() => {
    let current = true;
    currentSession().then((next) => current && setSession(next));
    return () => {
      current = false;
    };
  }, []);

  if (session.state === "checking") return null;
  if (session.state === "signed-out") return <AuthScreen onSignedIn={load} />;
  return <Workspace user={session.user} onSignedOut={() => setSession({ state: "signed-out" })} />;
}
