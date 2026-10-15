"""Coleta dos números do GitHub e do Veryon.

Sem token usa só endpoints públicos. Com token (na Action, o GITHUB_TOKEN)
usa a API com limite maior e o GraphQL para o calendário de contribuições.
"""
import collections
import datetime
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request

CACHE = None  # pasta de cache opcional, usada só em desenvolvimento
CABECALHOS = {"User-Agent": "perfil-gerador", "Accept": "application/vnd.github+json"}


def _pedir(url, token=None, corpo=None, extra=None):
    """GET (ou POST, se houver corpo) com cache opcional em disco."""
    chave = None
    if CACHE and corpo is None:
        chave = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest())
        if os.path.exists(chave):
            return open(chave, "rb").read()
    cab = dict(CABECALHOS)
    if extra:
        cab.update(extra)
    if token and "api.github.com" in url:
        cab["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=corpo, headers=cab)
    with urllib.request.urlopen(req, timeout=30) as resp:
        dados = resp.read()
    if chave:
        os.makedirs(CACHE, exist_ok=True)
        open(chave, "wb").write(dados)
    return dados


def _api(caminho, token=None):
    return json.loads(_pedir(f"https://api.github.com{caminho}", token))


# --- calendário de contribuições -------------------------------------------

def _calendario_html(usuario, ano):
    """Lê o calendário pelo endpoint público que o próprio perfil usa."""
    url = f"https://github.com/users/{usuario}/contributions?from={ano}-01-01&to={ano}-12-31"
    pagina = _pedir(url, extra={"X-Requested-With": "XMLHttpRequest"}).decode("utf-8", "replace")
    datas = {}
    for tag in re.findall(r"<td\b[^>]*data-date=[^>]*>", pagina):
        data = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        ident = re.search(r'\bid="(contribution-day-component-[\d-]+)"', tag)
        if data and ident:
            datas[ident.group(1)] = data.group(1)
    dias = {}
    for ident, texto in re.findall(r'<tool-tip\b[^>]*\bfor="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)', pagina):
        if ident in datas:
            numero = re.match(r"\s*(\d+)", texto)
            dias[datas[ident]] = int(numero.group(1)) if numero else 0
    if len(dias) < 300:
        raise RuntimeError(f"calendário de {ano} veio incompleto ({len(dias)} dias)")
    return dias


def _calendario_graphql(usuario, ano, token):
    consulta = (
        "query($u:String!,$a:DateTime!,$b:DateTime!){user(login:$u){contributionsCollection(from:$a,to:$b)"
        "{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"
    )
    corpo = json.dumps({"query": consulta, "variables": {
        "u": usuario, "a": f"{ano}-01-01T00:00:00Z", "b": f"{ano}-12-31T23:59:59Z"}}).encode()
    resposta = json.loads(_pedir("https://api.github.com/graphql", token, corpo=corpo,
                                    extra={"Content-Type": "application/json"}))
    semanas = resposta["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {d["date"]: d["contributionCount"] for s in semanas for d in s["contributionDays"]}


def calendario(usuario, ano_inicial, token=None):
    """Retorna {data: contribuições} de todos os anos desde a criação da conta."""
    dias = {}
    for ano in range(ano_inicial, datetime.date.today().year + 1):
        parte = None
        if token:
            try:
                parte = _calendario_graphql(usuario, ano, token)
            except Exception as erro:  # cai para o HTML se o GraphQL falhar
                print(f"aviso: GraphQL falhou em {ano} ({erro}); usando o endpoint público")
        if parte is None:
            parte = _calendario_html(usuario, ano)
        dias.update(parte)
    return dias


def sequencias(dias, hoje):
    """Sequência atual e maior sequência de dias seguidos com contribuição."""
    ordenados = sorted(d for d, n in dias.items() if n > 0 and d <= hoje.isoformat())
    maior = atual = 0
    anterior = None
    for texto in ordenados:
        dia = datetime.date.fromisoformat(texto)
        atual = atual + 1 if anterior and (dia - anterior).days == 1 else 1
        maior = max(maior, atual)
        anterior = dia
    # a sequência atual só vale se terminou hoje ou ontem
    corrente = 0
    if anterior and (hoje - anterior).days <= 1:
        corrente = atual
    return corrente, maior


# --- repositórios -----------------------------------------------------------

EXTENSOES = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
             ".jsx": "JavaScript", ".css": "CSS", ".html": "HTML", ".sh": "Shell", ".sql": "SQL",
             ".mako": "Mako"}
IGNORAR = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock"}


def contar_linhas(raiz):
    """Linhas de código (sem linhas em branco) por linguagem, nos arquivos versionados."""
    nomes = subprocess.run(["git", "-C", raiz, "ls-files"], capture_output=True, text=True,
                           encoding="utf-8", check=True).stdout.splitlines()
    linhas = collections.Counter()
    for rel in nomes:
        base = os.path.basename(rel)
        if base in IGNORAR or rel.startswith(("reports/output/", "docs/guias/")):
            continue
        linguagem = "Dockerfile" if base.lower().startswith("dockerfile") else EXTENSOES.get(os.path.splitext(base)[1].lower())
        if not linguagem:
            continue
        try:
            with open(os.path.join(raiz, rel), encoding="utf-8", errors="ignore") as arq:
                linhas[linguagem] += sum(1 for linha in arq if linha.strip())
        except OSError:
            pass
    return dict(linhas)


def contar_commits(raiz):
    try:
        saida = subprocess.run(["git", "-C", raiz, "rev-list", "--count", "HEAD"], capture_output=True,
                               text=True, check=True).stdout.strip()
        return int(saida)
    except Exception:
        return None


# --- tudo junto -------------------------------------------------------------

def coletar(perfil, token=None, veryon=None):
    usuario = perfil["usuario"]
    hoje = datetime.datetime.now(datetime.timezone.utc).date()
    conta = _api(f"/users/{usuario}", token)
    criada = datetime.date.fromisoformat(conta["created_at"][:10])
    repos = [r for r in _api(f"/users/{usuario}/repos?per_page=100&type=owner", token) if not r["fork"]]
    linguagens = set()
    for repo in repos:
        linguagens.update(_api(f"/repos/{repo['full_name']}/languages", token).keys())
    dias = calendario(usuario, criada.year, token)
    corrente, maior = sequencias(dias, hoje)
    limite = (hoje - datetime.timedelta(days=365)).isoformat()
    ano = {d: n for d, n in dias.items() if limite < d <= hoje.isoformat()}
    meses = (hoje.year - criada.year) * 12 + hoje.month - criada.month
    dados = {
        "gerado_em": hoje,
        "contribuicoes": sum(ano.values()),
        "dias_ativos": sum(1 for n in ano.values() if n > 0),
        "sequencia_atual": corrente,
        "maior_sequencia": maior,
        "xp_total": sum(dias.values()),
        "repositorios": len(repos),
        "seguidores": conta["followers"],
        "meses_conta": meses,
        "linguagens": len(linguagens),
        "linhas": {},
        "linhas_total": 0,
        "commits_veryon": None,
    }
    if veryon:
        linhas = contar_linhas(veryon)
        dados["linhas"] = linhas
        dados["linhas_total"] = sum(linhas.values())
        dados["commits_veryon"] = contar_commits(veryon)
    return dados
