"""Stack: os ícones das tecnologias (acendem em vermelho um por um, como o mouse
passando por cima da faixa da foto no site) e a tabela de ferramentas por área,
igual à do Sobre do portfólio.
"""
import json
import os

from base import MARGEM, LARGURA, P, cartao, f, movimento, svg
from texto import Tinta, altura_cap, quebrar

CICLO = 12
POR_LINHA = 7


def _icones():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icones.json")
    with open(caminho, encoding="utf-8") as arq:
        return json.load(arq)["icones"]


def desenhar(perfil, dados=None):
    t = Tinta()
    icones = _icones()
    s = perfil["stack"]
    cabeca = t.texto(f'[ {s["titulo"]} ]'.upper(), MARGEM, 70, "mono", 16, P["vermelho"], 0.18)

    larg = (LARGURA - 2 * MARGEM) / POR_LINHA
    lado = 36
    itens, acesos = [], []
    for i, item in enumerate(s["icones"]):
        icone = icones[item["slug"]]
        cx = MARGEM + (i % POR_LINHA) * larg + larg / 2
        y = 108 + (i // POR_LINHA) * 112
        desenho = (f'<g transform="translate({f(cx - lado / 2)} {y}) scale({lado / 24:.4f})">'
                   f'<path d="{icone["d"]}"/></g>')
        itens.append(f'<g fill="{P["creme"]}" fill-opacity="0.8">{desenho}</g>'
                     + t.texto(item["nome"].upper(), cx, y + lado + 30, "mono", 12, P["creme500"], 0.18, "middle"))
        ini = 1.0 + i * 0.32
        kt = ";".join(f"{v / CICLO:.4f}" for v in (0, ini, ini + 0.3, ini + 0.9, ini + 1.4, CICLO))
        acesos.append(
            f'<g fill="{P["vermelho_claro"]}" opacity="0">{desenho}'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{CICLO}s" '
            f'repeatCount="indefinite"/></g>'
        )
    linhas_icones = -(-len(s["icones"]) // POR_LINHA)
    y_tabela = 108 + linhas_icones * 112 + 40

    # tabela: nome da área em Anybody, itens em mono separados por barra
    x_itens = MARGEM + 300
    larg_itens = LARGURA - MARGEM - x_itens
    linhas, y = [], y_tabela
    linhas.append(f'<path d="M{MARGEM} {y + 0.5}H{LARGURA - MARGEM}" stroke="{P["linha"]}"/>')
    for g in s["grupos"]:
        texto_itens = quebrar("  /  ".join(g["itens"]).upper(), "mono", 14, larg_itens, 0.12)
        alt = max(68, 44 + len(texto_itens) * 22)
        base_nome = y + alt / 2 + altura_cap("titulo75", 30) / 2
        linhas.append(t.texto(g["grupo"], MARGEM, base_nome, "titulo75", 30, P["creme"]))
        topo_itens = y + alt / 2 - (len(texto_itens) * 22) / 2 + 15
        for k, linha in enumerate(texto_itens):
            linhas.append(t.texto(linha, x_itens, topo_itens + k * 22, "mono", 14, P["creme300"], 0.12))
        y += alt
        linhas.append(f'<path d="M{MARGEM} {f(y + 0.5)}H{LARGURA - MARGEM}" stroke="{P["linha"]}"/>')
    altura = round(y + 56)
    corpo = cartao(LARGURA, altura) + cabeca + "".join(itens) + movimento("".join(acesos), "") + "".join(linhas)
    alt = "; ".join(f'{g["grupo"]}: {", ".join(g["itens"])}' for g in s["grupos"]) + "."
    return svg(LARGURA, altura, "Ferramentas e tecnologias", alt, corpo, t.defs())
