"""Troféus com nota (D a SSS) e os marcos do Veryon como selos."""
from animacao import odometro
from base import CSS_BASE, P, ciclo, esc, f, milhar, painel, svg

LARGURA = 1200
CICLO = 16
NOTAS = ["C", "B", "A", "S", "SS", "SSS"]
COR_NOTA = {"D": "#64748b", "C": "#94a3b8", "B": "#38bdf8", "A": "#34d399", "S": "#fbbf24", "SS": "#fb923c", "SSS": "#f472b6"}

CSS = CSS_BASE


def nota_de(valor, faixas):
    """Retorna (nota, indice, alvo_da_proxima, base_da_faixa_atual)."""
    indice = -1
    for i, limite in enumerate(faixas):
        if valor >= limite:
            indice = i
    nota = NOTAS[indice] if indice >= 0 else "D"
    alvo = faixas[indice + 1] if indice + 1 < len(faixas) else None
    base = faixas[indice] if indice >= 0 else 0
    return nota, indice, alvo, base


def _icone(nome, cor):
    tracos = f'fill="none" stroke="{cor}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"'
    if nome == "barras":
        return (f'<rect x="-16" y="2" width="9" height="13" rx="2" fill="{cor}"/>'
                f'<rect x="-4.5" y="-6" width="9" height="21" rx="2" fill="{cor}"/>'
                f'<rect x="7" y="-15" width="9" height="30" rx="2" fill="{cor}"/>')
    if nome == "commit":
        return f'<circle r="7" {tracos}/><path d="M-20 0H-7M7 0H20" {tracos}/>'
    if nome == "codigo":
        return f'<text class="m" y="7" text-anchor="middle" font-size="20" font-weight="700" fill="{cor}">&lt;/&gt;</text>'
    if nome == "repo":
        return f'<path d="M-11 -15H10a3 3 0 0 1 3 3V15H-8a3 3 0 0 1-3-3Z" {tracos}/><path d="M-11 8H13" {tracos}/>'
    if nome == "chaves":
        return f'<text class="m" y="8" text-anchor="middle" font-size="24" font-weight="700" fill="{cor}">{{ }}</text>'
    return f'<path d="M-13 1L-4 11L14 -11" {tracos}/>'  # check


def _valores(perfil, dados):
    return {
        "contribuicoes": dados["contribuicoes"],
        "commits_veryon": dados["commits_veryon"] or 0,
        "linhas": dados["linhas_total"],
        "repositorios": dados["repositorios"],
        "linguagens": dados["linguagens"],
        "testes": perfil["veryon"]["numeros"]["testes"],
    }


def _tiles(perfil, dados):
    valores = _valores(perfil, dados)
    caixas, dinamico = [], []
    for i, t in enumerate(perfil["trofeus"]):
        valor = valores[t["id"]]
        nota, indice, alvo, base = nota_de(valor, t["faixas"])
        cor = COR_NOTA[nota]
        x = 48 + i * 186
        y = 80
        proximo = NOTAS[indice + 1] if indice + 1 < len(NOTAS) else None
        legenda = f"{proximo} em {milhar(alvo)}" if alvo else "nota máxima"
        progresso = 1.0 if not alvo else max(0.0, min(1.0, (valor - base) / (alvo - base)))
        largura_nota = 16 + 14 * len(nota)
        caixas.append(
            f'<rect x="{x}" y="{y}" width="174" height="238" rx="16" fill="{P["painel2"]}" fill-opacity="0.55" stroke="{P["linha"]}"/>'
            f'<circle cx="{x + 87}" cy="{y + 54}" r="32" fill="{P["painel"]}" stroke="{cor}" stroke-width="2.5"/>'
            f'<g transform="translate({x + 87} {y + 54})">{_icone(t["icone"], cor)}</g>'
            f'<rect x="{x + 174 - largura_nota - 12}" y="{y + 12}" width="{largura_nota}" height="26" rx="8" fill="{cor}"/>'
            f'<text class="m" x="{x + 174 - largura_nota / 2 - 12}" y="{y + 31}" text-anchor="middle" font-size="16" font-weight="800" fill="#06101d">{nota}</text>'
            f'<text class="s" x="{x + 87}" y="{y + 150}" text-anchor="middle" font-size="15.5" font-weight="700" fill="{P["texto"]}">{esc(t["titulo"])}</text>'
            f'<text class="s" x="{x + 87}" y="{y + 170}" text-anchor="middle" font-size="12.5" fill="{P["mudo"]}">{esc(t["sub"])}</text>'
            f'<rect x="{x + 20}" y="{y + 190}" width="134" height="8" rx="4" fill="{P["linha"]}"/>'
            f'<text class="m" x="{x + 87}" y="{y + 222}" text-anchor="middle" font-size="12" fill="{P["fraco"]}">{esc(legenda)}</text>'
        )
        numero, _ = odometro(milhar(valor), x + 87, y + 125, 32, P["texto"], CICLO)
        barra = (
            f'<svg x="{x + 20}" y="{y + 190}" width="0" height="8">'
            f'<animate attributeName="width" dur="{CICLO}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;0.04;0.2;1" values="0;0;{f(134 * progresso)};{f(134 * progresso)}" keySplines="0 0 1 1;0.2 0.8 0.2 1;0 0 1 1"/>'
            f'<rect width="134" height="8" rx="4" fill="{cor}"/></svg>'
        )
        dinamico.append(numero + barra)
    return "".join(caixas) + ciclo(CICLO, "".join(dinamico))


def _marcos(perfil):
    chips = []
    x, y = 48, 372
    for i, texto in enumerate(perfil["marcos"]):
        largura = len(texto) * 7.9 + 50
        if x + largura > 1152:
            x, y = 48, y + 44
        chips.append(
            f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{i * 0.08:.2f}s" dur="0.5s" fill="freeze"/>'
            f'<rect x="{f(x)}" y="{y}" width="{f(largura)}" height="34" rx="17" fill="{P["verde"]}" fill-opacity="0.08" stroke="{P["verde"]}" stroke-opacity="0.45"/>'
            f'<path d="M{f(x + 16)} {y + 17}l4 4 8-9" fill="none" stroke="{P["verde"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<text class="s" x="{f(x + 38)}" y="{y + 22}" font-size="14" fill="{P["texto"]}">{esc(texto)}</text></g>'
        )
        x += largura + 10
    return "".join(chips), y + 34


def desenhar(perfil, dados):
    marcos, fim = _marcos(perfil)
    altura = fim + 36
    defs, fundo = painel(LARGURA, altura, 22, "rc")
    corpo = (
        fundo
        + '<g clip-path="url(#rc)">'
        f'<text class="m" x="48" y="52" font-size="13" letter-spacing="2" fill="{P["ciano"]}">TROFÉUS</text>'
        f'<text class="m" x="1152" y="52" text-anchor="end" font-size="12" fill="{P["fraco"]}">nota por faixa de valor, as faixas estão em perfil.json</text>'
        + _tiles(perfil, dados)
        + f'<text class="m" x="48" y="352" font-size="13" letter-spacing="2" fill="{P["ciano"]}">MARCOS DO VERYON</text>'
        + marcos
        + "</g>"
    )
    return svg(LARGURA, altura, "Troféus e marcos",
               "Troféus com nota de D a SSS para contribuições, commits, linhas, repositórios, linguagens e testes, e os marcos do Veryon.",
               corpo, defs, CSS)
