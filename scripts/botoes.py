"""Botões no desenho dos botões do portfólio (cada um vira um link no README).

No site, o mouse faz uma tarja entrar da esquerda e a cor do texto trocar.
Aqui a tarja entra sozinha de tempos em tempos, um botão logo depois do outro.
"""
import math

from base import P, f, svg
from texto import Tinta, altura_cap, largura

ALTURA = 52
TAM = 15
ESPACO = 0.12
CICLO = 8
SETA = "M7 7h10v10M7 17 17 7"  # ArrowUpRight, do lucide

# fundo, borda, tarja, cor do texto, cor do texto com a tarja
ESTILOS = {
    "vermelho": (P["vermelho"], None, P["creme"], P["creme"], P["fundo"]),
    "claro": (P["creme"], None, P["vermelho"], P["fundo"], P["creme"]),
    "contorno": (P["fundo"], P["creme"], P["vermelho"], P["creme"], P["creme"]),
}


def css(ciclo=CICLO):
    return (
        "@keyframes bw{0%,9%{transform:scaleX(0)}17%,45%{transform:scaleX(1)}53%,100%{transform:scaleX(0)}}"
        f".bw{{transform-box:fill-box;transform-origin:0 50%;transform:scaleX(0);"
        f"animation:bw {ciclo}s cubic-bezier(.7,0,.2,1) infinite}}"
        "@keyframes bt{0%,11%{fill:var(--c0)}17%,47%{fill:var(--c1)}53%,100%{fill:var(--c0)}}"
        f".bt{{animation:bt {ciclo}s linear infinite}}"
        "@keyframes ba{0%,11%{stroke:var(--c0);transform:none}"
        "17%,47%{stroke:var(--c1);transform:translate(2px,-2px)}53%,100%{stroke:var(--c0);transform:none}}"
        f".ba{{animation:ba {ciclo}s linear infinite}}"
    )


def medida(rotulo):
    return math.ceil(24 + largura(rotulo.upper(), "forte", TAM, ESPACO) + 12 + 16 + 24)


def desenho(t, rotulo, estilo, x, y, atraso):
    """O botão em (x, y), para usar solto ou dentro de um cartão. Retorna (svg, largura)."""
    fundo, borda, tarja, cor, cor_tarja = ESTILOS[estilo]
    texto = rotulo.upper()
    larg = medida(rotulo)
    base = y + ALTURA / 2 + altura_cap("forte", TAM) / 2
    atraso_css = f"animation-delay:{atraso:.2f}s"
    if borda:
        caixa = (f'<rect x="{f(x)}" y="{f(y)}" width="{f(larg)}" height="{ALTURA}" fill="{fundo}"/>'
                 f'<rect class="bw" style="{atraso_css}" x="{f(x + 1)}" y="{f(y + 1)}" width="{f(larg - 2)}" '
                 f'height="{ALTURA - 2}" fill="{tarja}"/>'
                 f'<rect x="{f(x + 0.5)}" y="{f(y + 0.5)}" width="{f(larg - 1)}" height="{ALTURA - 1}" '
                 f'fill="none" stroke="{borda}" stroke-opacity="0.3"/>')
    else:
        caixa = (f'<rect x="{f(x)}" y="{f(y)}" width="{f(larg)}" height="{ALTURA}" fill="{fundo}"/>'
                 f'<rect class="bw" style="{atraso_css}" x="{f(x)}" y="{f(y)}" width="{f(larg)}" '
                 f'height="{ALTURA}" fill="{tarja}"/>')
    cores = f"--c0:{cor};--c1:{cor_tarja};{atraso_css}"
    letras = (f'<g class="bt" style="{cores}" fill="{cor}">'
              f'{t.texto(texto, x + 24, base, "forte", TAM, "", ESPACO)}</g>')
    x_seta = x + larg - 24 - 16
    seta = (f'<g transform="translate({f(x_seta)} {f(y + ALTURA / 2 - 8)}) scale(0.6667)">'
            f'<g class="ba" style="{cores}" fill="none" stroke="{cor}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="{SETA}"/></g></g>')
    return caixa + letras + seta, larg


def desenhar_todos(perfil):
    pecas = {}
    for i, b in enumerate(perfil["botoes"]):
        t = Tinta()
        corpo, larg = desenho(t, b["rotulo"], b["estilo"], 0, 0, 1.0 + b.get("ordem", i) * 0.3)
        pecas[b["arquivo"]] = svg(round(larg), ALTURA, b["rotulo"], f'Botão: {b["rotulo"]}', corpo, t.defs(), css())
    return pecas
