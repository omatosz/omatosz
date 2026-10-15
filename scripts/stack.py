"""Faixa de tecnologias com ícones e a lista do que está em estudo."""
import json
import os

from base import CSS_BASE, P, esc, f, painel, svg

LARGURA = 1200

CSS = CSS_BASE


def _entra(atraso, corpo):
    """Grupo que aparece em fade depois de `atraso` segundos e fica."""
    return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{atraso:.2f}s" '
            f'dur="0.6s" fill="freeze"/>{corpo}</g>')


def _flutua(atraso, corpo):
    """Sobe e desce 5 px devagar, em laço."""
    return (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" '
            f'dur="4.2s" begin="{atraso:.2f}s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>{corpo}</g>')


def _icones():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icones.json")
    with open(caminho, encoding="utf-8") as arq:
        return json.load(arq)["icones"]


def desenhar(perfil, dados=None):
    icones = _icones()
    stack = perfil["stack"]
    passo = 1104 / len(stack)
    itens = []
    for i, item in enumerate(stack):
        icone = icones[item["slug"]]
        cx = 48 + passo * (i + 0.5)
        medalha = (
            f'<circle cx="{f(cx)}" cy="116" r="31" fill="{P["painel2"]}" fill-opacity="0.7" stroke="{P["linha"]}"/>'
            f'<g transform="translate({f(cx - 16)} 100) scale(1.3333)"><path d="{icone["d"]}" fill="{icone["cor"]}"/></g>'
        )
        nome = f'<text class="m" x="{f(cx)}" y="176" text-anchor="middle" font-size="12.5" fill="{P["mudo"]}">{esc(item["nome"])}</text>'
        itens.append(_entra(i * 0.07, _flutua((i * 0.37) % 4, medalha) + nome))
    chips = []
    x, y = 48, 246
    for i, texto in enumerate(perfil["estudo"]):
        largura = len(texto) * 8.6 + 34
        if x + largura > 1152:
            x, y = 48, y + 44
        chips.append(_entra(1 + i * 0.07,
            f'<rect x="{f(x)}" y="{y}" width="{f(largura)}" height="32" rx="16" fill="none" stroke="{P["ciano"]}" stroke-opacity="0.5"/>'
            f'<text class="m" x="{f(x + largura / 2)}" y="{y + 21}" text-anchor="middle" font-size="13.5" fill="{P["ciano_claro"]}">{esc(texto)}</text>'))
        x += largura + 10
    altura = y + 32 + 34
    defs, fundo = painel(LARGURA, altura, 22, "rc")
    corpo = (
        fundo
        + '<g clip-path="url(#rc)">'
        f'<text class="m" x="48" y="52" font-size="13" letter-spacing="2" fill="{P["ciano"]}">COM O QUE EU CONSTRUO</text>'
        + "".join(itens)
        + f'<text class="m" x="48" y="224" font-size="13" letter-spacing="2" fill="{P["ciano"]}">EM ESTUDO</text>'
        + "".join(chips)
        + "</g>"
    )
    return svg(LARGURA, altura, "Stack e estudos",
               "Tecnologias usadas no Veryon e a lista de temas de segurança em estudo.", corpo, defs, CSS)
