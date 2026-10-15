"""Cartão do Veryon: contadores que rolam, o caminho do ataque e as linguagens."""
import datetime

from animacao import odometro
from base import CSS_BASE, P, ciclo, esc, f, milhar, painel, svg

LARGURA, ALTURA = 1200, 560
CICLO = 16  # segundos até os contadores recomeçarem

CSS = CSS_BASE + (
    "@keyframes pulso{0%,100%{opacity:.12}50%{opacity:.8}}"
    "@keyframes fluxo{to{stroke-dashoffset:-28}}"
    ".pulso{animation:pulso 3.2s ease-in-out infinite}"
    ".fluxo{animation:fluxo 1.4s linear infinite}"
)

CORES_NUMERO = [P["ciano_claro"], P["verde"], P["ambar"], P["violeta"], "#7dd3fc", P["ciano_claro"]]
CORES_LINGUAGEM = [P["ciano"], P["azul"], P["violeta"], P["ambar"], P["verde"], P["fraco"]]


def _contadores(perfil, dados):
    n = perfil["veryon"]["numeros"]
    itens = [
        (n["servicos"], "serviços no ar"),
        (n["sinais"], "sinais de API"),
        (n["politicas"], "políticas de prevenção"),
        (n["trilhos"], "trilhos de segurança"),
        (n["testes"], "testes automatizados"),
        (dados["linhas_total"], "linhas de código"),
    ]
    caixas, numeros = [], []
    for i, (valor, rotulo) in enumerate(itens):
        x = 48 + i * 186
        caixas.append(
            f'<rect x="{x}" y="150" width="174" height="108" rx="14" fill="{P["painel2"]}" fill-opacity="0.55" stroke="{P["linha"]}"/>'
            f'<text class="s" x="{x + 87}" y="243" text-anchor="middle" font-size="13.5" fill="{P["mudo"]}">{esc(rotulo)}</text>'
        )
        corpo, _ = odometro(milhar(valor), x + 87, 212, 46, CORES_NUMERO[i], CICLO)
        numeros.append(corpo)
    return "".join(caixas) + ciclo(CICLO, "".join(numeros))


def _caminho(perfil):
    etapas = perfil["veryon"]["etapas"]
    n = len(etapas)
    passo = 1104 / n
    xs = [48 + passo * (i + 0.5) for i in range(n)]
    y = 354
    partes = [
        f'<text class="m" x="48" y="312" font-size="13" letter-spacing="2" fill="{P["fraco"]}">O CAMINHO DO ATAQUE</text>',
        f'<path d="M{f(xs[0])} {y}H{f(xs[-1])}" stroke="{P["linha"]}" stroke-width="3" stroke-linecap="round"/>',
        f'<path class="fluxo" d="M{f(xs[0])} {y}H{f(xs[-1])}" stroke="{P["ciano"]}" stroke-width="3" stroke-dasharray="6 8" opacity="0.55"/>',
    ]
    # legenda das cores dos pacotes
    lx = 790
    for cor, texto in ((P["vermelho"], "ataque"), (P["ambar"], "alerta"), (P["verde"], "resolvido")):
        partes.append(f'<circle cx="{lx}" cy="308" r="5" fill="{cor}"/><text class="m" x="{lx + 12}" y="312" font-size="13" fill="{P["mudo"]}">{texto}</text>')
        lx += 120
    for i, (etapa, x) in enumerate(zip(etapas, xs)):
        atraso = f"{i * 0.32:.2f}s"
        partes.append(
            f'<circle class="pulso" style="animation-delay:{atraso}" cx="{f(x)}" cy="{y}" r="27" fill="none" stroke="{P["ciano"]}" stroke-width="2"/>'
            f'<circle cx="{f(x)}" cy="{y}" r="19" fill="{P["painel"]}" stroke="{P["ciano"]}" stroke-width="2"/>'
            f'<text class="m" x="{f(x)}" y="{y + 5}" text-anchor="middle" font-size="14" font-weight="700" fill="{P["ciano_claro"]}">{i + 1}</text>'
            f'<text class="s" x="{f(x)}" y="{y + 52}" text-anchor="middle" font-size="15" font-weight="600" fill="{P["texto"]}">{esc(etapa["nome"])}</text>'
            f'<text class="m" x="{f(x)}" y="{y + 71}" text-anchor="middle" font-size="12" fill="{P["fraco"]}">{esc(etapa["detalhe"])}</text>'
        )
    # pacotes: entram vermelhos, viram alerta na detecção e saem resolvidos na prevenção
    dur = 9
    corte_alerta = 2 / (n - 1)
    corte_resolvido = 6 / (n - 1)
    for inicio in (0, 3, 6):
        trocas = f'calcMode="discrete" keyTimes="0;{corte_alerta:.3f};{corte_resolvido:.3f}" values="{P["vermelho"]};{P["ambar"]};{P["verde"]}"'
        base = f'dur="{dur}s" begin="{inicio}s" repeatCount="indefinite"'
        partes.append(
            f'<circle r="7" fill="{P["vermelho"]}" stroke="{P["vermelho"]}" stroke-opacity="0.35" stroke-width="5" opacity="0">'
            f'<animateMotion path="M{f(xs[0])} {y}H{f(xs[-1])}" {base}/>'
            f'<animate attributeName="fill" {base} {trocas}/>'
            f'<animate attributeName="stroke" {base} {trocas}/>'
            f'<animate attributeName="opacity" {base} keyTimes="0;0.04;0.94;1" values="0;1;1;0"/></circle>'
        )
    return "".join(partes)


def _linguagens(dados):
    linhas = sorted(dados["linhas"].items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in linhas) or 1
    principais = linhas[:5]
    resto = sum(v for _, v in linhas[5:])
    if resto:
        principais.append(("outras", resto))
    larg = 1104
    x = 0
    segmentos, legenda = [], []
    for i, (nome, valor) in enumerate(principais):
        w = larg * valor / total
        cor = CORES_LINGUAGEM[i % len(CORES_LINGUAGEM)]
        segmentos.append(f'<rect x="{f(x)}" y="0" width="{f(max(w - 2, 1))}" height="16" rx="3" fill="{cor}"/>')
        x += w
        lx = 48 + i * 184
        legenda.append(
            f'<rect x="{lx}" y="505" width="10" height="10" rx="2" fill="{cor}"/>'
            f'<text class="m" x="{lx + 17}" y="514" font-size="13" fill="{P["mudo"]}">{esc(nome)} {milhar(valor)}</text>'
        )
    revelacao = (
        f'<svg x="48" y="470" width="0" height="16">'
        f'<animate attributeName="width" dur="{CICLO}s" repeatCount="indefinite" calcMode="spline" '
        f'keyTimes="0;0.04;0.2;1" values="0;0;{larg};{larg}" keySplines="0 0 1 1;0.2 0.8 0.2 1;0 0 1 1"/>'
        f'{"".join(segmentos)}</svg>'
    )
    return (
        f'<text class="m" x="48" y="458" font-size="13" letter-spacing="2" fill="{P["fraco"]}">LINHAS DE CÓDIGO POR LINGUAGEM</text>'
        f'<rect x="48" y="470" width="{larg}" height="16" rx="3" fill="{P["painel2"]}" fill-opacity="0.6"/>'
        + ciclo(CICLO, revelacao + "".join(legenda))
    )


def desenhar(perfil, dados):
    v = perfil["veryon"]
    defs, fundo = painel(LARGURA, ALTURA, 22, "rc")
    verificado = datetime.date.fromisoformat(v["verificado_em"]).strftime("%d/%m/%Y")
    corpo = (
        fundo
        + '<g clip-path="url(#rc)">'
        f'<text class="m" x="48" y="52" font-size="13" letter-spacing="2" fill="{P["ciano"]}">PROJETO EM DESTAQUE</text>'
        f'<text class="m" x="1152" y="52" text-anchor="end" font-size="12" fill="{P["fraco"]}">números conferidos em {verificado}</text>'
        f'<text class="s" x="48" y="98" font-size="34" font-weight="700" fill="{P["texto"]}">{esc(v["titulo"])}</text>'
        f'<text class="s" x="48" y="128" font-size="17" fill="{P["mudo"]}">{esc(v["subtitulo"])}</text>'
        + _contadores(perfil, dados)
        + _caminho(perfil)
        + _linguagens(dados)
        + "</g>"
    )
    return svg(LARGURA, ALTURA, "Veryon, SOC feito do zero",
               "Números do Veryon, o caminho de um ataque pelas dez etapas e as linguagens do código.",
               corpo, defs, CSS)
