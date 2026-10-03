import { useEffect, useState } from 'react'
import { Activity, ArrowRight, BarChart3, Bell, Check, CheckCircle2, Clock3, FlaskConical, LayoutDashboard, LogOut, Menu, Monitor, Play, RefreshCw, ShieldCheck, Ticket, Users, Volume2, VolumeX, X } from 'lucide-react'
import { api } from './api.js'

const titles = { overview: 'Visão geral', service: 'Atendimentos', panel: 'Painel de chamadas', reports: 'Relatórios' }
const types = { SP: 'Prioritária', SG: 'Geral', SE: 'Retirada de exames' }
const hhmm = (d) => d ? new Date(d).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '—'

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('nt-token') || '')
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('nt-user') || 'null'))
  const [page, setPage] = useState('overview')
  const [queue, setQueue] = useState({ senhas: [], por_tipo: {} })
  const [panel, setPanel] = useState({ chamadas: [] })
  const [guiches, setGuiches] = useState([])
  const [guiche, setGuiche] = useState('')
  const [active, setActive] = useState(null)
  const [report, setReport] = useState(null)
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [monthly, setMonthly] = useState(false)
  const [error, setError] = useState('')
  const [online, setOnline] = useState(false)
  const [busy, setBusy] = useState(false)
  const [announcement, setAnnouncement] = useState(null)
  const [audio, setAudio] = useState(false)
  const [mobile, setMobile] = useState(false)
  const manager = user?.perfil === 'GESTOR'

  async function refresh() {
    try {
      const [p, q, g] = await Promise.all([api('/painel'), api('/senhas/fila'), api('/guiches/get?incluir_inativos=false')])
      setPanel(p); setQueue(q); setGuiches(g); setOnline(true); setError('')
      if (!guiche && g.length) setGuiche(String(user?.guiche_id || g[0].id))
    } catch (e) { setOnline(false); setError(e.message || 'API indisponível. Inicie o backend e o banco de dados.') }
  }
  function openTotem() {
    setAnnouncement(null)
    setError('')
    setPage('totem')
    refresh()
  }

  useEffect(() => { refresh(); const id = setInterval(refresh, 10000); return () => clearInterval(id) }, [token])
  useEffect(() => { if (audio && panel.chamadas?.[0] && 'speechSynthesis' in window) { const u = new SpeechSynthesisUtterance(panel.chamadas[0].audio_texto); u.lang = 'pt-BR'; speechSynthesis.cancel(); speechSynthesis.speak(u) } }, [audio, panel.chamadas?.[0]?.chamada_em])

  async function act(path, options = {}) {
    setBusy(true); setError('')
    try {
      const result = await api(path, { token, ...options })
      if (result.codigo) setActive(result)
      if (/finalizar|nao-compareceu/.test(path)) setActive(null)
      await refresh()
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  async function emit(type) {
    setBusy(true); setError(''); setAnnouncement(null)
    try { setAnnouncement(await api('/senhas/emissir', { method: 'POST', body: JSON.stringify({ tipo: type }) })); await refresh() }
    catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  async function signIn(event) {
    event.preventDefault(); setBusy(true); setError('')
    const data = new FormData(event.currentTarget)
    try {
      const result = await api('/auth/login', { method: 'POST', body: JSON.stringify({ login: data.get('login'), senha: data.get('senha') }) })
      localStorage.setItem('nt-token', result.access_token); localStorage.setItem('nt-user', JSON.stringify(result.usuario))
      setToken(result.access_token); setUser(result.usuario); setPage('overview')
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  async function loadReport() {
    if (!token || !manager || page !== 'reports') return
    setBusy(true)
    try { setReport(await api(monthly ? `/relatorios/mensal?ano=${date.slice(0,4)}&mes=${Number(date.slice(5,7))}` : `/relatorios/diario?data=${date}`, { token })) }
    catch (e) { setError(e.message); setReport(null) } finally { setBusy(false) }
  }
  useEffect(() => { loadReport() }, [page, date, monthly, token])

  if (page === 'totem') return <Totem goBack={() => setPage(token ? 'overview' : 'login')} emit={emit} busy={busy} error={error} announcement={announcement} />
  if (page === 'panel' && !token) return <PublicPanel panel={panel} online={online} audio={audio} setAudio={setAudio} goBack={() => setPage('login')} />
  if (page === 'login' || !token) return <Login submit={signIn} busy={busy} error={error} goTotem={openTotem} goPanel={() => setPage('panel')} />
  const nav = [['overview', LayoutDashboard], ['service', Users], ['panel', Monitor], ...(manager ? [['reports', BarChart3]] : [])]
  return <div className="layout">
    <aside className={`sidebar ${mobile ? 'open' : ''}`}><Brand /><small className="nav-title">MENU PRINCIPAL</small><nav>{nav.map(([id, Icon]) => <button className={page === id ? 'selected' : ''} key={id} onClick={() => { setPage(id); setMobile(false) }}><Icon size={18}/>{titles[id]}{id === 'service' && queue.total_aguardando > 0 && <b className="count">{queue.total_aguardando}</b>}</button>)}</nav><button className={"nav-public "+(page==="totem"?"selected":"")} onClick={() => { openTotem(); setMobile(false) }}><Ticket size={18}/>Emitir senha</button><div className="grow"/><div className="connection"><i className={online ? 'on' : ''}/><span><b>{online ? 'Sistema online' : 'Conectando à API'}</b><small>{online ? 'Atualizado agora' : 'Tentando reconectar'}</small></span></div><div className="profile"><div className="avatar">{(user?.nome || '?')[0]}</div><span><b>{user?.nome || user?.login}</b><small>{manager ? 'Gestor' : 'Atendente'}</small></span><button className="icon" aria-label="Sair" onClick={() => { localStorage.clear(); setToken(''); setUser(null) }}><LogOut size={17}/></button></div></aside>
    {mobile && <button className="scrim" onClick={() => setMobile(false)} aria-label="Fechar navegação"/>}
    <main className="main"><header className="topbar"><button className="icon menu" onClick={() => setMobile(!mobile)} aria-label="Abrir navegação"><Menu/></button><span>Laboratório <i>/</i> {titles[page]}</span><div><Clock3 size={15}/>{new Date().toLocaleDateString('pt-BR',{weekday:'short',day:'2-digit',month:'short'})}</div></header><section className="content">
      {error && <div className="alert" role="alert"><Activity size={17}/>{error}<button onClick={() => setError('')} aria-label="Fechar aviso"><X size={16}/></button></div>}
      {page === 'overview' && <><Heading eyebrow="OPERAÇÃO DE HOJE" title="Visão geral" desc="Acompanhe a fila e o ritmo dos atendimentos em tempo real." action={<button className="secondary" onClick={refresh}><RefreshCw size={16}/>Atualizar</button>}/><div className="metrics">{[['Na fila agora',queue.total_aguardando || 0,'Aguardando atendimento',Ticket,'blue'],['Prioritárias',queue.por_tipo?.SP || 0,'SP · prioridade',ShieldCheck,'amber'],['Retirada de exames',queue.por_tipo?.SE || 0,'SE · retirada rápida',FlaskConical,'green'],['Atendimento geral',queue.por_tipo?.SG || 0,'SG · fila geral',Users,'violet']].map(([l,v,d,I,c]) => <Metric key={l} label={l} value={v} detail={d} icon={I} tone={c}/>)}</div><div className="columns"><section className="card"><CardHead title="Fila de atendimento" desc="Senhas aguardando chamada" action={<button className="link" onClick={() => setPage('service')}>Ver fila <ArrowRight size={15}/></button>}/><div className="table"><div className="row th"><span>Senha</span><span>Categoria</span><span>Emitida</span><span>Status</span></div>{queue.senhas?.slice(0,7).map(t => <QueueRow key={t.id} item={t}/>)}{!queue.senhas?.length && <Empty title="Fila vazia" desc="As novas senhas aparecerão aqui."/>}</div></section><section className="card"><CardHead title="Última chamada" desc="Painel de atendimento" action={<button className="icon" onClick={() => setPage('panel')} aria-label="Abrir painel"><ArrowRight size={18}/></button>}/>{panel.chamadas?.[0] ? <div className="current"><small>{types[panel.chamadas[0].tipo]}</small><strong>{panel.chamadas[0].codigo}</strong><span>⌖ Guichê {panel.chamadas[0].guiche_numero}</span><span><Clock3 size={14}/> {hhmm(panel.chamadas[0].chamada_em)}</span></div> : <Empty title="Nenhuma chamada" desc="As chamadas recentes aparecerão aqui."/>}</section></div><div className="notice"><Clock3 size={19}/><span><b>Expediente de atendimento</b><small>Segunda a sexta, das 07:00 às 17:00</small></span><Pill online={online}/></div></>}
      {page === 'service' && <><Heading eyebrow="ESTAÇÃO DE ATENDIMENTO" title="Atendimentos" desc="Chame a próxima pessoa e acompanhe cada etapa." action={<button className="secondary" onClick={refresh}><RefreshCw size={16}/>Atualizar</button>}/><div className="columns service-columns"><section className="card"><div className="service-head"><div><small>GUICHÊ DE ATENDIMENTO</small><h2>Pronto para atender</h2></div><label>Guichê<select value={guiche} onChange={e => setGuiche(e.target.value)}>{guiches.map(g => <option key={g.id} value={g.id}>{g.nome || `Guichê ${g.numero}`}</option>)}</select></label></div>{(active || queue.senhas?.find(t => ['CHAMADA','CHAMADA_NOVAMENTE','EM_ATENDIMENTO'].includes(t.estado))) ? <div className="serving"><small>SENHA EM ATENDIMENTO</small><strong>{(active || queue.senhas.find(t => ['CHAMADA','CHAMADA_NOVAMENTE','EM_ATENDIMENTO'].includes(t.estado))).codigo}</strong><TypeBadge type={(active || queue.senhas.find(t => ['CHAMADA','CHAMADA_NOVAMENTE','EM_ATENDIMENTO'].includes(t.estado))).tipo}/><p>Chamadas: {(active || queue.senhas.find(t => ['CHAMADA','CHAMADA_NOVAMENTE','EM_ATENDIMENTO'].includes(t.estado))).chamadas}</p>{(() => { const t = active || queue.senhas.find(x => ['CHAMADA','CHAMADA_NOVAMENTE','EM_ATENDIMENTO'].includes(x.estado)); return t.estado === 'EM_ATENDIMENTO' ? <button className="primary" disabled={busy} onClick={() => act(`/atendimento/${t.id}/finalizar`,{method:'POST'})}><Check/>Finalizar atendimento</button> : <div className="actions"><button className="primary" disabled={busy} onClick={() => act(`/atendimento/${t.id}/iniciar`,{method:'POST'})}><Play/>Iniciar atendimento</button><button className="secondary" disabled={busy || t.chamadas >= 2} onClick={() => act(`/atendimento/${t.id}/chamar-novamente`,{method:'POST'})}><Bell/>Chamar novamente</button><button className="link" disabled={busy} onClick={() => act(`/atendimento/${t.id}/nao-compareceu`,{method:'POST'})}>Não compareceu</button></div> })()}</div> : <div className="idle"><div><Users size={25}/></div><b>Nenhum atendimento em andamento</b><span>Chame a próxima senha para começar.</span><button className="primary" disabled={busy || !guiche} onClick={() => act('/atendimento/proxima',{method:'POST',body:JSON.stringify({guiche_id:Number(guiche)})})}><Bell/>Chamar próxima senha</button></div>}</section><section className="card"><CardHead title="Fila de espera" desc={`${queue.total_aguardando || 0} aguardando`}/>{queue.senhas?.map((t,i)=><div className="wait-row" key={t.id}><i>{String(i+1).padStart(2,'0')}</i><span><b>{t.codigo}</b><small>{types[t.tipo]}</small></span><small>{hhmm(t.emissao_em)}</small></div>)}{!queue.senhas?.length && <Empty title="Fila vazia" desc="Nenhuma senha aguardando."/>}</section></div><div className="priority-note"><ShieldCheck size={18}/><span><b>Ordem de prioridade</b><small>SP → SE → SG, conforme disponibilidade e alternância da fila.</small></span></div></>}
      {page === 'panel' && <><Heading eyebrow="PAINEL PÚBLICO" title="Últimas chamadas" desc="As cinco senhas mais recentes. A próxima senha não aparece antes de ser chamada." action={<button className="secondary" onClick={() => setAudio(!audio)}>{audio?<Volume2 size={16}/>:<VolumeX size={16}/>} Áudio {audio?'ligado':'desligado'}</button>}/><div className="called-grid">{panel.chamadas?.map((t,i)=><article className={`called ${i===0?'latest':''}`} key={t.codigo}><small>{types[t.tipo]} · {i===0?'AGORA':hhmm(t.chamada_em)}</small><strong>{t.codigo}</strong><span>⌖ Guichê <b>{t.guiche_numero}</b></span>{t.ultima_chamada && <em>ÚLTIMA CHAMADA</em>}</article>)}</div>{!panel.chamadas?.length && <Empty title="Aguardando novas chamadas" desc="As senhas chamadas serão exibidas aqui."/>}</>}
      {page === 'reports' && manager && <><Heading eyebrow="ACOMPANHAMENTO" title="Relatórios" desc="Indicadores e histórico dos atendimentos."/><section className="card filters"><label>Período<select value={monthly?'mensal':'diario'} onChange={e=>setMonthly(e.target.value==='mensal')}><option value="diario">Diário</option><option value="mensal">Mensal</option></select></label><label>{monthly?'Mês de referência':'Data'}<input type={monthly?'month':'date'} value={monthly?date.slice(0,7):date} onChange={e=>setDate(monthly?e.target.value+'-01':e.target.value)}/></label></section>{report && <><div className="metrics">{[['Emitidas',report.quantitativos?.emitidas,'No período',Ticket,'blue'],['Atendidas',report.quantitativos?.atendidas,'Concluídas',CheckCircle2,'green'],['Não atendidas',report.quantitativos?.nao_atendidas,'Abandonadas/descartadas',Activity,'amber'],['Tempo médio',report.tempo_medio_geral_minutos==null?'—':report.tempo_medio_geral_minutos.toFixed(1)+' min','Por atendimento',Clock3,'violet']].map(([l,v,d,I,c])=><Metric key={l} label={l} value={v??0} detail={d} icon={I} tone={c}/>)}</div><section className="card report"><CardHead title="Resumo por categoria" desc={report.periodo}/>{['SP','SE','SG'].map(t=><div className="report-row" key={t}><TypeBadge type={t}/><span>Emitidas <b>{report.quantitativos?.emitidas_por_tipo?.[t]||0}</b></span><span>Atendidas <b>{report.quantitativos?.atendidas_por_tipo?.[t]||0}</b></span></div>)}</section><section className="card report"><CardHead title="Detalhamento de senhas" desc={`${report.senhas?.length||0} registros`}/><div className="table"><div className="row th"><span>Senha</span><span>Categoria</span><span>Emissão</span><span>Atendimento</span></div>{report.senhas?.map(t=><div className="row" key={t.codigo}><b>{t.codigo}</b><TypeBadge type={t.tipo}/><span>{hhmm(t.emissao_em)}</span><span>{hhmm(t.atendimento_inicio)}</span></div>)}</div></section><div className="columns"><section className="card report"><CardHead title="Tempo médio por categoria" desc="Duração dos atendimentos concluídos"/>{report.tempo_medio?.map(t=><div className="report-row" key={t.tipo}><TypeBadge type={t.tipo}/><span>Média <b>{t.tm_medio_minutos == null ? '—' : t.tm_medio_minutos.toFixed(1)+' min'}</b></span><span>Esperado <b>{t.tm_esperado_minutos} min</b></span></div>)}</section><section className="card report"><CardHead title="Auditoria de chamadas" desc={`${report.auditoria?.length||0} eventos`}/>{report.auditoria?.length ? report.auditoria.slice(0,8).map((a,i)=><div className="audit-row" key={a.senha_codigo+'-'+i}><b>{a.senha_codigo||'—'}</b><span>{a.atendente_login||'—'} · Guichê {a.guiche_numero||'—'}</span><small>1ª {hhmm(a.primeira_chamada)} · 2ª {hhmm(a.segunda_chamada)} · Início {hhmm(a.inicio_atendimento)} · Fim {hhmm(a.fim_atendimento)}</small></div>) : <Empty title="Sem eventos de auditoria" desc="Não há chamadas registradas neste período."/>}</section></div></>}</>}
    </section></main>
  </div>
}

function Brand(){return <div className="brand"><div className="brand-icon"><FlaskConical size={20}/></div><span><b>nassau<span>Tickets</span></b><small>CONTROLE DE ATENDIMENTO</small></span></div>}
function Heading({eyebrow,title,desc,action}){return <div className="heading"><div><small>{eyebrow}</small><h1>{title}</h1><p>{desc}</p></div>{action}</div>}
function CardHead({title,desc,action}){return <div className="card-head"><div><h2>{title}</h2><p>{desc}</p></div>{action}</div>}
function Metric({label,value,detail,icon:Icon,tone}){return <article className="metric"><div className={`metric-icon ${tone}`}><Icon size={19}/></div><span>{label}</span><b>{value}</b><small>{detail}</small></article>}
function TypeBadge({type}){return <span className={`badge ${type?.toLowerCase()}`}><i/>{type} · {types[type]}</span>}
function QueueRow({item}){return <div className="row"><b>{item.codigo}</b><TypeBadge type={item.tipo}/><span>{hhmm(item.emissao_em)}</span><span className="waiting">Aguardando</span></div>}
function Empty({title,desc}){return <div className="empty"><span><Check size={20}/></span><b>{title}</b><small>{desc}</small></div>}
function Pill({online}){return <span className={`pill ${online?'ok':''}`}><i/>{online?'Operação normal':'Sem conexão'}</span>}
function Login({submit,busy,error,goTotem,goPanel}){return <div className="login"><section className="login-art"><Brand/><div><small>ATENDIMENTO ORGANIZADO</small><h1>Cuidar bem começa com <i>esperar menos.</i></h1><p>Uma experiência mais simples para quem chega. Mais clareza para quem atende.</p><div className="login-facts"><span><b>07—17h</b><small>horário de atendimento</small></span><span><b>03</b><small>tipos de atendimento</small></span></div></div><footer>LABORATÓRIO DE ANÁLISES CLÍNICAS</footer></section><section className="login-side"><form onSubmit={submit}><small>ÁREA RESTRITA</small><h2>Bem-vindo de volta</h2><p>Acesse sua conta para gerenciar os atendimentos.</p>{error&&<div className="alert">{error}</div>}<label>Usuário<input name="login" autoComplete="username" placeholder="Seu usuário" required/></label><label>Senha<input name="senha" type="password" autoComplete="current-password" placeholder="Sua senha" required/></label><button className="primary full" disabled={busy}>{busy?'Entrando…':'Entrar'}<ArrowRight size={17}/></button><hr/><small className="public-label">OU ACESSE UMA TELA PÚBLICA</small><div className="public-links"><button type="button" onClick={goTotem}><Ticket size={16}/>Emitir senha no totem</button><button type="button" onClick={goPanel}><Monitor size={16}/>Painel de chamadas</button></div><div className="secure"><ShieldCheck size={16}/>Acesso protegido para a equipe do laboratório.</div></form><footer>nassauTickets · Sistema de atendimento</footer></section></div>}
function Totem({goBack,emit,busy,error,announcement}){return <div className="totem"><header><Brand/><button className="link" onClick={goBack}>Área da equipe</button></header><main><small>SEJA BEM-VINDO(A)</small><h1>Qual atendimento<br/>você precisa?</h1><p>Toque em uma opção para retirar sua senha.</p>{error&&<div className="alert">{error}</div>}{announcement?<div className="issued"><CheckCircle2 size={28}/><small>SUA SENHA</small><b>{announcement.codigo}</b><TypeBadge type={announcement.tipo}/><p>Aguarde sua chamada no painel.</p><button className="primary" onClick={goBack}>Concluir</button></div>:<div className="options">{[['SP','Atendimento prioritário','Para idosos, gestantes e pessoas com prioridade.'],['SG','Atendimento geral','Consultas e demais serviços do laboratório.'],['SE','Retirada de exames','Para retirar resultados de exames.']].map(([t,h,p])=><button key={t} disabled={busy} onClick={()=>emit(t)}><i>{t==='SE'?<FlaskConical/>:<Ticket/>}</i><span><b>{h}</b><small>{p}</small></span><ArrowRight/></button>)}</div>}<div className="secure"><ShieldCheck size={16}/>Não é necessário informar seus dados pessoais para emitir uma senha.</div></main></div>}

function PublicPanel({panel,online,audio,setAudio,goBack}) {
  return <div className="public-screen"><header><Brand/><span className="connection-label"><i className={online?'on':''}/>{online?'PAINEL AO VIVO':'CONECTANDO'}</span><button className="secondary" onClick={()=>setAudio(!audio)}>{audio?<Volume2 size={16}/>:<VolumeX size={16}/>} Áudio {audio?'ligado':'desligado'}</button></header><main><small>ACOMPANHE AS CHAMADAS</small><h1>Senhas chamadas</h1><p>Por favor, dirija-se ao guichê indicado.</p>{panel.chamadas?.length?<div className="called-grid">{panel.chamadas.map((c,i)=><article className={"called "+(i===0?'latest':'')} key={c.codigo}><small>{types[c.tipo]} · {i===0?'AGORA':hhmm(c.chamada_em)}</small><strong>{c.codigo}</strong><span>⌖ Guichê <b>{c.guiche_numero}</b></span>{c.ultima_chamada&&<em>ÚLTIMA CHAMADA</em>}</article>)}</div>:<Empty title="Aguardando novas chamadas" desc="As senhas chamadas serão exibidas aqui."/>}</main><footer><span>LABORATÓRIO DE ANÁLISES CLÍNICAS</span><button className="link" onClick={goBack}>Área da equipe</button></footer></div>
}
