"use client";
import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const api = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
export default function LoginPage() {
  const [error, setError] = useState(""); const [loading, setLoading] = useState(false); const router = useRouter();
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setLoading(true); setError(""); const form = new FormData(event.currentTarget);
    try { const response = await fetch(`${api}/api/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: form.get("email"), password: form.get("password") }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || "Could not sign in"); localStorage.setItem("roomfund_access_token", data.access_token); localStorage.setItem("roomfund_refresh_token", data.refresh_token); router.push("/dashboard"); } catch (err) { setError(err instanceof Error ? err.message : "Could not sign in"); } finally { setLoading(false); }
  }
  return <main className="auth"><form onSubmit={submit} className="auth-card"><Link href="/" className="brand">RoomFund</Link><h1>Welcome back</h1><label>Email<input required name="email" type="email" autoComplete="email" /></label><label>Password<input required name="password" type="password" autoComplete="current-password" /></label>{error && <p className="error">{error}</p>}<button className="button" disabled={loading}>{loading ? "Signing in…" : "Sign in"}</button><p className="muted">New here? <Link href="/register">Create an account</Link></p></form></main>;
}
