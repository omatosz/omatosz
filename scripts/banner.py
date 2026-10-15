"""Banner do topo: nome, texto digitando, radar girando e faixa de tecnologias."""
import math

from animacao import digitacao
from base import P, esc, f, painel, svg

LARGURA, ALTURA = 1200, 340
RADAR = (985, 158, 124)  # centro x, centro y, raio
VOLTA = 6  # segundos por volta do radar


def _fatia(cx, cy, raio, a0, a1):
    """Setor circular entre dois ângulos (graus, sentido horário)."""
    x0 = cx + raio * math.cos(math.radians(a0))
    y0 = cy + raio * math.sin(math.radians(a0))
    x1 = cx + raio * math.cos(math.radians(a1))
    y1 = cy + raio * math.sin(math.radians(a1))
    return f"M{cx} {cy} L{f(x0)} {f(y0)} A{raio} {raio} 0 0 1 {f(x1)} {f(y1)} Z"


def _radar():
    cx, cy, raio = RADAR
    partes = []
    for k, tracejado in ((1, ""), (0.75, ' stroke-dasharray="3 7"'), (0.5, ""), (0.25, ' stroke-dasharray="3 7"')):
        partes.append(f'<circle cx="{cx}" cy="{cy}" r="{f(raio * k)}" fill="none" stroke="{P["linha"]}" stroke-width="1.5"{tracejado}/>')
    partes.append(f'<path d="M{cx - raio} {cy}H{cx + raio}M{cx} {cy - raio}V{cy + raio}" stroke="{P["linha"]}" stroke-width="1.2" opacity="0.7"/>')
    # varredura: fatias com opacidade decrescente deixam um rastro atrás da linha
    fatias = []
    for s in range(18):
        opacidade = 0.36 * (1 - s / 18) ** 1.7
        fatias.append(f'<path d="{_fatia(cx, cy, raio, -(s + 1) * 3.2, -s * 3.2)}" fill="{P["ciano"]}" opacity="{opacidade:.3f}"/>')
    partes.append(
        "<g>"
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="{VOLTA}s" repeatCount="indefinite"/>'
        + "".join(fatias)
        + f'<path d="M{cx} {cy}H{cx + raio}" stroke="{P["ciano_claro"]}" stroke-width="2" stroke-linecap="round"/>'
        + "</g>"
    )
    # alvos: acendem quando a linha de varredura passa por eles
    alvos = [(0.62, 38, "vermelho"), (0.86, 112, "ambar"), (0.42, 205, "verde"),
             (0.78, 262, "vermelho"), (0.55, 322, "ambar"), (0.9, 165, "verde")]
    for fracao, angulo, nome in alvos:
        x = cx + raio * fracao * math.cos(math.radians(angulo))
        y = cy + raio * fracao * math.sin(math.radians(angulo))
        inicio = angulo / 360 * VOLTA
        cor = P[nome]
        partes.append(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="5" fill="{cor}" opacity="0">'
            f'<animate attributeName="opacity" dur="{VOLTA}s" begin="{inicio:.2f}s" repeatCount="indefinite" keyTimes="0;0.06;1" values="1;1;0"/></circle>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="5" fill="none" stroke="{cor}" stroke-width="2" opacity="0">'
            f'<animate attributeName="r" dur="{VOLTA}s" begin="{inicio:.2f}s" repeatCount="indefinite" keyTimes="0;0.25;1" values="5;20;20"/>'
            f'<animate attributeName="opacity" dur="{VOLTA}s" begin="{inicio:.2f}s" repeatCount="indefinite" keyTimes="0;0.25;1" values="0.9;0;0"/></circle>'
        )
    partes.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{P["ciano_claro"]}"/>')
    return "".join(partes)


def _faixa(tecnologias):
    """Texto de tecnologias rolando na base, em laço contínuo."""
    texto = "   ·   ".join(tecnologias) + "   ·   "
    cw = 8.4  # fonte 14 monoespaçada
    largura = len(texto) * cw
    copias = int(LARGURA / largura) + 2
    letras = "".join(
        f'<text class="m" x="{f(i * largura)}" y="{ALTURA - 15}" font-size="14" fill="{P["fraco"]}" '
        f'textLength="{f(largura)}" lengthAdjust="spacing" xml:space="preserve">{esc(texto)}</text>'
        for i in range(copias)
    )
    return (
        f'<rect y="{ALTURA - 42}" width="{LARGURA}" height="42" fill="#04070e" opacity="0.72"/>'
        f'<path d="M0 {ALTURA - 42}H{LARGURA}" stroke="{P["linha"]}"/>'
        "<g>"
        f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{f(largura)} 0" '
        f'dur="{f(largura / 38)}s" repeatCount="indefinite"/>{letras}</g>'
    )


def desenhar(perfil):
    defs_painel, fundo = painel(LARGURA, ALTURA, 22, "rc")
    dig_defs, dig_corpo = digitacao(perfil["frases"], 98, 252, 26, P["ciano_claro"], "dg")
    defs = defs_painel + dig_defs + (
        f'<linearGradient id="nome" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{P["ciano_claro"]}"/></linearGradient>'
        f'<linearGradient id="varre" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["ciano"]}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{P["ciano"]}" stop-opacity="0.10"/><stop offset="1" stop-color="{P["ciano"]}" stop-opacity="0"/></linearGradient>'
        f'<radialGradient id="brilho"><stop offset="0" stop-color="{P["ciano"]}" stop-opacity="0.22"/><stop offset="1" stop-color="{P["ciano"]}" stop-opacity="0"/></radialGradient>'
    )
    cx, cy, raio = RADAR
    chip = (
        f'<rect x="64" y="36" width="290" height="34" rx="17" fill="{P["ciano"]}" fill-opacity="0.08" stroke="{P["ciano"]}" stroke-opacity="0.5"/>'
        f'<circle cx="86" cy="53" r="5" fill="{P["verde"]}">'
        '<animate attributeName="r" values="4;6.5;4" dur="2s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="1;0.45;1" dur="2s" repeatCount="indefinite"/></circle>'
        f'<text class="m" x="104" y="58" font-size="14" letter-spacing="1.6" fill="{P["ciano"]}">{esc(perfil["faixa"])}</text>'
    )
    nome = (
        '<g opacity="0">'
        '<animate attributeName="opacity" from="0" to="1" begin="0.15s" dur="0.9s" fill="freeze"/>'
        '<animateTransform attributeName="transform" type="translate" from="-26 0" to="0 0" begin="0.15s" dur="0.9s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.16 1 0.3 1"/>'
        f'<text class="s" x="62" y="192" font-size="68" font-weight="800" fill="url(#nome)">{esc(perfil["nome"])}</text></g>'
    )
    corpo = (
        fundo
        + f'<g clip-path="url(#rc)">'
        f'<circle cx="{cx}" cy="{cy}" r="{raio + 70}" fill="url(#brilho)"/>'
        f'<rect y="-90" width="{LARGURA}" height="90" fill="url(#varre)">'
        f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {ALTURA + 90}" dur="7s" repeatCount="indefinite"/></rect>'
        + _radar()
        + chip
        + f'<text class="m" x="64" y="116" font-size="17" fill="{P["fraco"]}">~/omatosz $ whoami</text>'
        + nome
        + f'<text class="m" x="64" y="252" font-size="26" fill="{P["verde"]}">&gt;</text>'
        + dig_corpo
        + _faixa(perfil["tecnologias_faixa"])
        + "</g>"
    )
    return svg(LARGURA, ALTURA, f'{perfil["nome"]}, blue team em formação',
               "Banner animado com o nome, frases digitadas e um radar de detecção girando.", corpo, defs)
