"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import "./dashboard.css";

const api = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
type Room = { id: string; name: string; location?: string | null; currency: string };
type Member = { user_id: string; name: string; net_balance_minor: number; total_paid_minor: number; total_share_minor: number };
type Expense = { id: string; title: string; amount_minor: number; expense_date: string };
type User = { id: string; name: string; email: string };
const money = (value: number, currency = "INR") => new Intl.NumberFormat("en-IN", { style: "currency", currency }).format(value / 100);

export default function DashboardPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [room, setRoom] = useState<Room | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [error, setError] = useState("");
  const [showChoice, setShowChoice] = useState(false);
  const [showShared, setShowShared] = useState(false);
  const [showPersonal, setShowPersonal] = useState(false);

  const request = useCallback(async (path: string, init?: RequestInit) => {
    const response = await fetch(`${api}${path}`, { ...init, headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...(init?.headers || {}) } });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Something went wrong");
    return data;
  }, [token]);

  const loadWorkspace = useCallback(async (selectedRoom: Room) => {
    const [balances, sharedExpenses] = await Promise.all([request(`/api/rooms/${selectedRoom.id}/balances`), request(`/api/rooms/${selectedRoom.id}/expenses`)]);
    setMembers(balances.members);
    setExpenses(sharedExpenses);
  }, [request]);

  useEffect(() => {
    const access = localStorage.getItem("roomfund_access_token");
    if (!access) { router.replace("/login"); return; }
    setToken(access);
  }, [router]);

  useEffect(() => {
    if (!token) return;
    Promise.all([request("/api/auth/me"), request("/api/rooms")])
      .then(async ([profile, rooms]: [User, Room[]]) => {
        setUser(profile);
        if (rooms[0]) { setRoom(rooms[0]); await loadWorkspace(rooms[0]); }
      })
      .catch((err) => setError(err.message));
  }, [token, request, loadWorkspace]);

  const totals = useMemo(() => {
    const mine = members.find((member) => member.user_id === user?.id);
    return {
      room: members.reduce((total, member) => total + member.total_paid_minor, 0),
      owe: Math.abs(Math.min(mine?.net_balance_minor || 0, 0)),
      receive: Math.max(mine?.net_balance_minor || 0, 0),
    };
  }, [members, user]);

  async function saveShared(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!room) return;
    const form = new FormData(event.currentTarget);
    try {
      await request(`/api/rooms/${room.id}/expenses`, {
        method: "POST",
        body: JSON.stringify({
          title: form.get("title"),
          amount_minor: Math.round(Number(form.get("amount")) * 100),
          currency: room.currency,
          expense_type: "COMMON",
          expense_date: new Date().toISOString().slice(0, 10),
          split_method: "EQUAL",
          participants: members.map((member) => ({ user_id: member.user_id, share_amount_minor: 0 })),
        }),
      });
      setShowShared(false);
      await loadWorkspace(room);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save shared payment"); }
  }

  async function savePersonal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await request("/api/personal-payments", {
        method: "POST",
        body: JSON.stringify({ title: form.get("title"), amount_minor: Math.round(Number(form.get("amount")) * 100), currency: room?.currency || "INR", expense_date: new Date().toISOString().slice(0, 10) }),
      });
      setShowPersonal(false);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save personal payment"); }
  }

  const openShared = () => { setShowChoice(false); setShowShared(true); };
  const openPersonal = () => { setShowChoice(false); setShowPersonal(true); };
  return <main className="shell">
    <aside>
      <a className="brand" href="/dashboard">RoomFund</a>
      <p className="sidebar-note">Shared money, clearly managed.</p>
      <nav>
        <a className="active" href="/dashboard">Dashboard</a><a href="/shared-expenses">Shared payments</a><a href="/personal-payments">Personal payments</a><a href="/members">Members</a><a href="/activity">Activity log</a>
      </nav>
      <button className="text-button" onClick={() => { localStorage.clear(); router.push("/login"); }}>Sign out</button>
    </aside>
    <section className="content">
      <header>
        <div><p className="eyebrow">SHARED WORKSPACE</p><h1>{room?.name || "Workspace unavailable"}</h1><p className="muted">{room ? `${room.location || "Location not added"} · Shared with ${members.length} members` : "Ask an admin to add your Gmail address."}</p></div>
        <button className="button" disabled={!room} onClick={() => setShowChoice(true)}>+ Add payment</button>
      </header>
      {error && <p className="error banner">{error}</p>}
      {room && <><section className="cards"><Summary label="Room spending" value={money(totals.room, room.currency)} /><Summary label="I owe" value={money(totals.owe, room.currency)} tone="negative" /><Summary label="I receive" value={money(totals.receive, room.currency)} tone="positive" /><Summary label="Members" value={String(members.length)} /></section>
      <section className="grid">
        <article className="panel"><div className="panel-heading"><h2>Shared payments</h2><a className="text-button" href="/shared-expenses">View all</a></div>{expenses.length ? expenses.slice(0, 4).map((expense) => <PaymentRow key={expense.id} title={expense.title} subtitle={expense.expense_date} value={money(expense.amount_minor, room.currency)} />) : <p className="muted">No shared payments yet.</p>}</article>
        <article className="panel"><div className="panel-heading"><h2>Balances</h2></div>{members.map((member) => <PaymentRow key={member.user_id} title={member.name} subtitle={`Paid ${money(member.total_paid_minor, room.currency)} · Share ${money(member.total_share_minor, room.currency)}`} value={member.net_balance_minor === 0 ? "Settled" : `${member.net_balance_minor > 0 ? "+" : "−"}${money(Math.abs(member.net_balance_minor), room.currency)}`} tone={member.net_balance_minor > 0 ? "positive" : member.net_balance_minor < 0 ? "negative" : undefined} />)}</article>
      </section>
      <section className="quick-actions" aria-label="Quick payment actions">
        <p className="eyebrow">QUICK PAYMENT</p>
        <div className="payment-action-grid">
          <PaymentAction icon="🏠" title="Shared payment" description="Add a payment for the room or flat" impact="Affects shared balances" action="Add shared payment →" onClick={openShared} />
          <PaymentAction icon="🔒" title="Personal payment" description="Keep a payment private to your account" impact="Does not affect shared balances" action="Add personal payment →" onClick={openPersonal} />
        </div>
      </section></>}
      {!room && <section className="empty"><h2>You are not in a workspace</h2><a className="text-button" href="/setup">Set up the first workspace</a></section>}
      {showChoice && <Modal title="What are you adding?" close={() => setShowChoice(false)}><p className="muted">Choose how this payment should be recorded.</p><div className="choice-grid"><PaymentAction icon="🏠" title="Shared payment" description="Shared with the room members" impact="Affects balances and settlements" action="Continue →" onClick={openShared} /><PaymentAction icon="🔒" title="Personal payment" description="Private — visible only to you" impact="Does not affect room balances" action="Continue →" onClick={openPersonal} /></div></Modal>}
      {showShared && <Modal title="Add shared payment" close={() => setShowShared(false)}><form className="form" onSubmit={saveShared}><label>Payment purpose<input name="title" required placeholder="Electricity bill" /></label><label>Amount (₹)<input name="amount" type="number" min="0.01" step="0.01" required /></label><p className="hint">Paid by <strong>{user?.name || "your account"}</strong><br />✓ Automatically detected from your account</p><button className="button">Save shared payment</button></form></Modal>}
      {showPersonal && <Modal title="Add personal payment" close={() => setShowPersonal(false)}><form className="form" onSubmit={savePersonal}><label>Payment purpose<input name="title" required placeholder="Personal shopping" /></label><label>Amount (₹)<input name="amount" type="number" min="0.01" step="0.01" required /></label><p className="hint">🔒 Only you can see this payment.</p><button className="button">Save personal payment</button></form></Modal>}
    </section>
  </main>;
}
function Summary({ label, value, tone }: { label: string; value: string; tone?: string }) { return <article className="card"><span>{label}</span><strong className={tone}>{value}</strong></article>; }
function PaymentRow({ title, subtitle, value, tone }: { title: string; subtitle: string; value: string; tone?: string }) { return <div className="row"><div><strong>{title}</strong><small>{subtitle}</small></div><strong className={tone}>{value}</strong></div>; }
function PaymentAction({ icon, title, description, impact, action, onClick }: { icon: string; title: string; description: string; impact: string; action: string; onClick: () => void }) { return <button className="payment-action" onClick={onClick}><span className="payment-icon">{icon}</span><strong>{title}</strong><span>{description}</span><small>{impact}</small><b>{action}</b></button>; }
function Modal({ title, children, close }: { title: string; children: React.ReactNode; close: () => void }) { return <div className="modal-backdrop" role="presentation"><section className="modal" role="dialog" aria-modal="true" aria-label={title}><div className="panel-heading"><h2>{title}</h2><button className="close" onClick={close} aria-label="Close">×</button></div>{children}</section></div>; }
