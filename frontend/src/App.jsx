import { useState, useEffect } from 'react';

const API = import.meta.env.VITE_API_URL;

const COLORS = {
  bg: '#0a0a0a', panel: '#131313', panelBorder: '#232323', card: '#161f16',
  cardBorder: '#243024', accent: '#8fe08a', accentDim: '#5b8f58',
  text: '#e8e6df', textDim: '#8a8a85', danger: '#2a1414', dangerBorder: '#3a1c1c',
};

const NAV_ITEMS = [
  { key: 'heykivi', label: 'hey kivi', icon: '\u25CF' },
  { key: 'feed', label: 'history', icon: '\u23F1' },
  { key: 'record', label: 'record', icon: '\u25CF' },
  { key: 'shortcuts', label: 'shortcuts', icon: '\u26A1' },
  { key: 'memory', label: 'memory viewer', icon: '\u2726' },
];

function authHeaders(token) {
  return { Authorization: `Bearer ${token}` };
}

export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem('kivi_token'));
  const [userName, setUserName] = useState(() => sessionStorage.getItem('kivi_user_name'));
  const [tab, setTab] = useState('heykivi');
  const [heyKiviTurns, setHeyKiviTurns] = useState([]);

  const handleAuthed = (accessToken, name) => {
    sessionStorage.setItem('kivi_token', accessToken);
    sessionStorage.setItem('kivi_user_name', name);
    setToken(accessToken);
    setUserName(name);
  };

  const logout = () => {
    sessionStorage.removeItem('kivi_token');
    sessionStorage.removeItem('kivi_user_name');
    setToken(null);
    setUserName(null);
    setHeyKiviTurns([]);
  };

  if (!token) {
    return <AuthScreen onAuthed={handleAuthed} />;
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: COLORS.bg, color: COLORS.text }}>
      <Sidebar tab={tab} setTab={setTab} userName={userName} onLogout={logout} />
      <main style={{ flex: 1, padding: '32px 40px', maxWidth: 920 }}>
        {tab === 'heykivi' && <HeyKivi token={token} turns={heyKiviTurns} setTurns={setHeyKiviTurns} />}
        {tab === 'feed' && <DictationFeed token={token} />}
        {tab === 'record' && <RecordTab token={token} />}
        {tab === 'shortcuts' && <ShortcutsTab token={token} />}
        {tab === 'memory' && <MemoryViewer token={token} />}
      </main>
    </div>
  );
}

function AuthScreen({ onAuthed }) {
  const [mode, setMode] = useState('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setError('');
    setLoading(true);
    const path = mode === 'login' ? '/auth/login' : '/auth/signup';
    const body = mode === 'login' ? { email, password } : { name, email, password };
    try {
      const res = await fetch(`${API}${path}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Something went wrong');
      } else {
        onAuthed(data.access_token, data.name);
      }
    } catch (e) {
      setError('Could not reach the server');
    }
    setLoading(false);
  };

  return (
    <div style={{
      minHeight: '100vh', background: COLORS.bg, color: COLORS.text,
      display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui, sans-serif',
    }}>
      <div style={{ width: 360, padding: 32, background: COLORS.panel, border: `1px solid ${COLORS.panelBorder}`, borderRadius: 14 }}>
        <div style={{ fontFamily: 'Fraunces, serif', fontSize: 30, fontWeight: 600, color: COLORS.accent, marginBottom: 4 }}>kivi</div>
        <div style={{ fontSize: 12, color: COLORS.textDim, marginBottom: 24 }}>by Sarvam</div>

        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          <button onClick={() => setMode('login')}
            style={{
              flex: 1, padding: '8px 0', borderRadius: 8, cursor: 'pointer', fontSize: 13,
              background: mode === 'login' ? COLORS.accent : 'transparent',
              color: mode === 'login' ? '#0a0a0a' : COLORS.textDim,
              border: `1px solid ${mode === 'login' ? COLORS.accent : COLORS.panelBorder}`,
            }}>Log in</button>
          <button onClick={() => setMode('signup')}
            style={{
              flex: 1, padding: '8px 0', borderRadius: 8, cursor: 'pointer', fontSize: 13,
              background: mode === 'signup' ? COLORS.accent : 'transparent',
              color: mode === 'signup' ? '#0a0a0a' : COLORS.textDim,
              border: `1px solid ${mode === 'signup' ? COLORS.accent : COLORS.panelBorder}`,
            }}>Sign up</button>
        </div>

        {mode === 'signup' && (
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Your name"
            style={inputStyle} />
        )}
        <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email"
          style={inputStyle} />
        <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Password"
          onKeyDown={e => e.key === 'Enter' && submit()}
          style={inputStyle} />

        {error && <div style={{ color: '#e08a8a', fontSize: 13, marginBottom: 12 }}>{error}</div>}

        <button onClick={submit} disabled={loading}
          style={{
            width: '100%', padding: '10px 0', background: COLORS.accent, color: '#0a0a0a',
            border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 600, fontSize: 14, marginTop: 4,
          }}>
          {loading ? '...' : mode === 'login' ? 'Log in' : 'Create account'}
        </button>
      </div>
    </div>
  );
}

const inputStyle = {
  width: '100%', padding: 10, marginBottom: 10, background: '#0a0a0a', color: '#e8e6df',
  border: `1px solid ${COLORS.panelBorder}`, borderRadius: 8, boxSizing: 'border-box', outline: 'none', fontSize: 14,
};

function Sidebar({ tab, setTab, userName, onLogout }) {
  return (
    <div style={{
      width: 220, borderRight: `1px solid ${COLORS.panelBorder}`, padding: '28px 20px',
      display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '100vh',
    }}>
      <div>
        <div style={{ fontFamily: 'Fraunces, serif', fontSize: 28, fontWeight: 600, color: COLORS.text, marginBottom: 4 }}>kivi</div>
        <div style={{ fontSize: 11, color: COLORS.textDim, letterSpacing: 0.5, marginBottom: 32 }}>by Sarvam</div>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {NAV_ITEMS.map(item => (
            <button key={item.key} onClick={() => setTab(item.key)}
              style={{
                display: 'flex', alignItems: 'center', gap: 10, padding: '9px 12px',
                background: tab === item.key ? '#182018' : 'transparent',
                color: tab === item.key ? COLORS.accent : '#b5b3ac',
                border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14, textAlign: 'left',
              }}>
              <span style={{ fontSize: 10, opacity: 0.7 }}>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </div>
      <div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10, padding: '10px 8px',
          borderTop: `1px solid ${COLORS.panelBorder}`, paddingTop: 16, marginBottom: 8,
        }}>
          <div style={{
            width: 30, height: 30, borderRadius: '50%', background: COLORS.accentDim,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 600, color: '#0a0a0a',
          }}>{(userName || '?')[0].toUpperCase()}</div>
          <div style={{ fontSize: 13, color: COLORS.text }}>{userName}</div>
        </div>
        <button onClick={onLogout}
          style={{
            width: '100%', padding: '7px 0', background: 'none', border: `1px solid ${COLORS.panelBorder}`,
            color: COLORS.textDim, borderRadius: 6, cursor: 'pointer', fontSize: 12.5,
          }}>Log out</button>
      </div>
    </div>
  );
}

function SectionHeading({ children, subtitle }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <h1 style={{ fontFamily: 'Fraunces, serif', fontWeight: 500, fontSize: 26, margin: 0, color: COLORS.text }}>{children}</h1>
      {subtitle && <p style={{ color: COLORS.textDim, fontSize: 14, marginTop: 6 }}>{subtitle}</p>}
    </div>
  );
}

function HeyKivi({ token, turns, setTurns }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(null);

  const ask = async () => {
    if (!input.trim()) return;
    setLoading(true);
    const res = await fetch(`${API}/hey-kivi/ask`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
      body: JSON.stringify({ request_text: input }),
    });
    const data = await res.json();
    setTurns(t => [...t, { request: input, ...data }]);
    setInput('');
    setLoading(false);
  };

  return (
    <div>
      <SectionHeading subtitle="Ask about anything you've told Kivi across your apps.">Hey Kivi</SectionHeading>
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && ask()}
          placeholder='Try: "What does PRJ-FLC stand for?"'
          style={{ flex: 1, padding: '12px 14px', fontSize: 14.5, background: COLORS.panel, color: COLORS.text, border: `1px solid ${COLORS.panelBorder}`, borderRadius: 10, outline: 'none' }} />
        <button onClick={ask} disabled={loading}
          style={{ padding: '0 22px', background: COLORS.accent, color: '#0a0a0a', border: 'none', borderRadius: 10, cursor: 'pointer', fontWeight: 600, fontSize: 14 }}>
          {loading ? '...' : 'Ask'}
        </button>
      </div>
      {turns.length === 0 && (
        <div style={{ color: COLORS.textDim, fontSize: 14, padding: '40px 0', textAlign: 'center', border: `1px dashed ${COLORS.panelBorder}`, borderRadius: 10 }}>No takes yet today.</div>
      )}
      {turns.slice().reverse().map((t, i) => (
        <div key={i} style={{ marginBottom: 14, padding: 16, borderRadius: 10, background: t.abstained ? COLORS.danger : COLORS.card, border: `1px solid ${t.abstained ? COLORS.dangerBorder : COLORS.cardBorder}` }}>
          <div style={{ color: COLORS.textDim, fontSize: 12.5, marginBottom: 6 }}>{t.request}</div>
          <div style={{ whiteSpace: 'pre-wrap', fontSize: 14.5, lineHeight: 1.5 }}>{t.response}</div>
          <button onClick={() => setExpanded(expanded === i ? null : i)}
            style={{ marginTop: 10, fontSize: 11.5, background: 'none', border: `1px solid ${COLORS.panelBorder}`, color: COLORS.textDim, borderRadius: 5, padding: '3px 10px', cursor: 'pointer' }}>
            {expanded === i ? 'hide why' : 'why? / memories used'}
          </button>
          {expanded === i && (
            <pre style={{ fontSize: 11, background: '#0a0a0a', padding: 10, marginTop: 8, overflowX: 'auto', color: COLORS.accent, borderRadius: 6, border: `1px solid ${COLORS.panelBorder}` }}>
              tool: {t.tool}{'\n'}memories used: {t.memories_used?.length || 0}{'\n'}latency: {t.latency_ms}ms{'\n'}
              {JSON.stringify(t.tool_output, null, 2).slice(0, 1500)}
            </pre>
          )}
        </div>
      ))}
    </div>
  );
}

function DictationFeed({ token }) {
  const [dictations, setDictations] = useState(null);
  const [appFilter, setAppFilter] = useState('');

  const load = (app) => {
    setDictations(null);
    const url = `${API}/debug/dictations?limit=30` + (app ? `&app=${encodeURIComponent(app)}` : '');
    fetch(url, { headers: authHeaders(token) }).then(r => r.json()).then(d => setDictations(d.dictations || []));
  };
  useEffect(() => load(appFilter), [appFilter]);

  return (
    <div>
      <SectionHeading subtitle="A chronological replay of what's entered Kivi's memory.">History</SectionHeading>
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {['', 'Slack', 'Google Docs', 'Outlook', 'Notes'].map(a => (
          <button key={a || 'all'} onClick={() => setAppFilter(a)}
            style={{ padding: '6px 14px', borderRadius: 20, cursor: 'pointer', fontSize: 13, background: appFilter === a ? COLORS.accent : COLORS.panel, color: appFilter === a ? '#0a0a0a' : COLORS.textDim, border: `1px solid ${appFilter === a ? COLORS.accent : COLORS.panelBorder}` }}>{a || 'All'}</button>
        ))}
      </div>
      {dictations === null && <p style={{ color: COLORS.textDim }}>Loading...</p>}
      {dictations && dictations.length === 0 && <p style={{ color: COLORS.textDim }}>No dictations found.</p>}
      {dictations && dictations.map(d => (
        <div key={d.id} style={{ padding: '12px 14px', marginBottom: 8, background: COLORS.card, border: `1px solid ${COLORS.cardBorder}`, borderRadius: 8 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11.5, color: COLORS.textDim, marginBottom: 5 }}>
            <span style={{ color: COLORS.accent }}>{d.app}</span>
            <span>{new Date(d.timestamp).toLocaleString()}</span>
          </div>
          <div style={{ fontSize: 14, lineHeight: 1.45 }}>{d.llm_formatted}</div>
        </div>
      ))}
    </div>
  );
}

function RecordTab({ token }) {
  const [text, setText] = useState('');
  const [app, setApp] = useState('Slack');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    const res = await fetch(`${API}/dictate`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
      body: JSON.stringify({ text, app }),
    });
    const data = await res.json();
    setResult(data);
    setText('');
    setLoading(false);
  };

  return (
    <div>
      <SectionHeading subtitle="Simulates a live dictation. Taught shortcuts expand automatically before Kivi remembers it.">Record</SectionHeading>
      <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
        {['Slack', 'Google Docs', 'Outlook', 'Notes'].map(a => (
          <button key={a} onClick={() => setApp(a)}
            style={{ padding: '6px 14px', borderRadius: 20, cursor: 'pointer', fontSize: 13, background: app === a ? COLORS.accent : COLORS.panel, color: app === a ? '#0a0a0a' : COLORS.textDim, border: `1px solid ${app === a ? COLORS.accent : COLORS.panelBorder}` }}>{a}</button>
        ))}
      </div>
      <textarea value={text} onChange={e => setText(e.target.value)} placeholder='Try: "Hey team, wrapping up for today. my sign-off"' rows={4}
        style={{ width: '100%', padding: 14, fontSize: 14.5, background: COLORS.panel, color: COLORS.text, border: `1px solid ${COLORS.panelBorder}`, borderRadius: 10, boxSizing: 'border-box', outline: 'none', resize: 'vertical' }} />
      <button onClick={submit} disabled={loading}
        style={{ marginTop: 10, padding: '10px 22px', background: COLORS.accent, color: '#0a0a0a', border: 'none', borderRadius: 10, cursor: 'pointer', fontWeight: 600, fontSize: 14 }}>
        {loading ? 'Recording...' : 'Record'}
      </button>
      {result && (
        <div style={{ marginTop: 24, padding: 16, background: COLORS.card, borderRadius: 10, border: `1px solid ${COLORS.cardBorder}` }}>
          <div style={{ color: COLORS.textDim, fontSize: 11.5, marginBottom: 4 }}>ORIGINAL</div>
          <div style={{ marginBottom: 14, fontSize: 14, color: COLORS.textDim }}>{result.original_text}</div>
          <div style={{ color: COLORS.textDim, fontSize: 11.5, marginBottom: 4 }}>EXPANDED & SAVED</div>
          <div style={{ whiteSpace: 'pre-wrap', fontSize: 14.5, lineHeight: 1.5 }}>{result.expanded_text}</div>
          {result.shortcuts_applied.length > 0 && (
            <div style={{ marginTop: 12, fontSize: 12.5, color: COLORS.accent }}>&#9889; shortcut applied: "{result.shortcuts_applied[0].trigger_phrase}"</div>
          )}
        </div>
      )}
    </div>
  );
}

function ShortcutsTab({ token }) {
  const [shortcuts, setShortcuts] = useState([]);
  const [trigger, setTrigger] = useState('');
  const [expansion, setExpansion] = useState('');
  const [showForm, setShowForm] = useState(false);

  const load = () => {
    fetch(`${API}/shortcuts`, { headers: authHeaders(token) }).then(r => r.json()).then(d => setShortcuts(d.shortcuts));
  };
  useEffect(load, []);

  const save = async () => {
    if (!trigger.trim() || !expansion.trim()) return;
    await fetch(`${API}/shortcuts`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
      body: JSON.stringify({ trigger_phrase: trigger, expansion_text: expansion }),
    });
    setTrigger(''); setExpansion(''); setShowForm(false);
    load();
  };

  const remove = async (id) => {
    await fetch(`${API}/shortcuts/${id}`, { method: 'DELETE', headers: authHeaders(token) });
    load();
  };

  return (
    <div>
      <SectionHeading subtitle="Teach Kivi a phrase that always expands to the same text.">Shortcuts</SectionHeading>
      {shortcuts.map(s => (
        <div key={s.id} style={{ padding: 16, marginBottom: 10, background: COLORS.card, border: `1px solid ${COLORS.cardBorder}`, borderRadius: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ fontFamily: 'Fraunces, serif', fontStyle: 'italic', color: COLORS.accent, fontSize: 15 }}>you say "{s.trigger_phrase}"</div>
            <div style={{ whiteSpace: 'pre-wrap', marginTop: 8, color: '#c9c7bf', fontSize: 13.5, lineHeight: 1.5 }}>{s.expansion_text}</div>
          </div>
          <button onClick={() => remove(s.id)} style={{ background: 'none', border: 'none', color: '#c47a7a', cursor: 'pointer', fontSize: 12.5 }}>delete</button>
        </div>
      ))}
      {!showForm ? (
        <button onClick={() => setShowForm(true)}
          style={{ padding: '14px 16px', background: 'transparent', border: `1px dashed ${COLORS.panelBorder}`, color: COLORS.accent, borderRadius: 10, cursor: 'pointer', width: '100%', fontSize: 14 }}>
          + teach kivi a shortcut
        </button>
      ) : (
        <div style={{ padding: 16, background: COLORS.card, border: `1px solid ${COLORS.cardBorder}`, borderRadius: 10 }}>
          <input value={trigger} onChange={e => setTrigger(e.target.value)} placeholder='you say... (e.g. "my sign-off")'
            style={{ width: '100%', marginBottom: 10, padding: 10, background: COLORS.panel, color: COLORS.text, border: `1px solid ${COLORS.panelBorder}`, borderRadius: 8, boxSizing: 'border-box', outline: 'none' }} />
          <textarea value={expansion} onChange={e => setExpansion(e.target.value)} placeholder='kivi writes... (e.g. "Warm regards,\nPriya Menon\nLoopwork")' rows={3}
            style={{ width: '100%', marginBottom: 10, padding: 10, background: COLORS.panel, color: COLORS.text, border: `1px solid ${COLORS.panelBorder}`, borderRadius: 8, boxSizing: 'border-box', outline: 'none', resize: 'vertical' }} />
          <button onClick={save} style={{ padding: '9px 18px', background: COLORS.accent, color: '#0a0a0a', border: 'none', borderRadius: 8, cursor: 'pointer', marginRight: 8, fontWeight: 600, fontSize: 13.5 }}>Save</button>
          <button onClick={() => setShowForm(false)} style={{ padding: '9px 18px', background: 'none', border: `1px solid ${COLORS.panelBorder}`, color: COLORS.textDim, borderRadius: 8, cursor: 'pointer', fontSize: 13.5 }}>Cancel</button>
        </div>
      )}
    </div>
  );
}

function MemoryViewer({ token }) {
  const [mem, setMem] = useState(null);
  useEffect(() => {
    fetch(`${API}/debug/memories`, { headers: authHeaders(token) }).then(r => r.json()).then(setMem);
  }, []);

  return (
    <div>
      <SectionHeading subtitle="Everything Kivi has learned, organized by memory type.">Memory Viewer</SectionHeading>
      {!mem && <p style={{ color: COLORS.textDim }}>Loading...</p>}
      {mem && ['factual', 'episodic', 'preference'].map(type => (
        <div key={type} style={{ marginBottom: 26 }}>
          <h3 style={{ textTransform: 'capitalize', color: COLORS.accent, fontSize: 14, fontWeight: 600, letterSpacing: 0.3, marginBottom: 10 }}>
            {type} <span style={{ color: COLORS.textDim, fontWeight: 400 }}>({mem[type]?.length || 0})</span>
          </h3>
          <div style={{ background: COLORS.card, border: `1px solid ${COLORS.cardBorder}`, borderRadius: 10, overflow: 'hidden' }}>
            {mem[type]?.slice(0, 15).map((m, idx) => (
              <div key={m.id} style={{ padding: '10px 14px', fontSize: 13.5, lineHeight: 1.5, borderBottom: idx < mem[type].length - 1 ? `1px solid ${COLORS.cardBorder}` : 'none' }}>
                <b style={{ color: '#c9c7bf' }}>{m.scope}</b>: {m.content}
                {m.expires_at && <span style={{ color: '#c99', fontSize: 11.5 }}> (expires {m.expires_at.slice(0, 10)})</span>}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}