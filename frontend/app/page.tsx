import Link from "next/link";

export default function Home() {
  return <main className="landing"><div className="landing-card"><p className="eyebrow">ROOMFUND</p><h1>Share a home, not financial confusion.</h1><p className="muted">Track shared bills, split them fairly, and settle up with confidence.</p><div className="actions"><Link className="button" href="/register">Create an account</Link><Link className="button secondary" href="/login">Sign in</Link></div></div></main>;
}
