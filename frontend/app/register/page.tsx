"use client";
import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
const api = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
export default function RegisterPage() { const [error, setError] = useState(""); const [loading, setLoading] = useState(false); const router = useRouter();
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setLoading(true); setError(""); const form = new FormData(event.currentTarget); try { const response = await fetch(`${api}/api/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: form.get("name"), email: form.get("email"), password: form.get("password") }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || "Could not create account"); router.push("/login"); } catch (err) { setError(err instanceof Error ? err.message : "Could not create account"); } finally { setLoading(false); } }
  return <main className="auth"><form onSubmit={submit} className="auth-card"><Link href="/" className="brand">RoomFund</Link><h1>Create your account</h1><label>Name<input required name="name" /></label><label>Email<input required name="email" type="email" autoComplete="email" /></label><label>Password<input required minLength={8} name="password" type="password" autoComplete="new-password" /></label>{error && <p className="error">{error}</p>}<button className="button" disabled={loading}>{loading ? "Creating…" : "Create account"}</button><p className="muted">Already registered? <Link href="/login">Sign in</Link></p></form></main>;
}
