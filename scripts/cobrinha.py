"""Embrulha o SVG da cobrinha (gerado pela Action Platane/snk) num cartão escuro.

O SVG da cobrinha tem fundo transparente e as cores de célula vazia escuras.
Dentro do cartão ele combina com o resto do perfil nos dois temas do GitHub.
"""
import re

from base import P, esc, f

LARGURA = 1200
FONTE = 'ui-monospace,SFMono-Regular,Menlo,Consolas,monospace'


def compor(texto_snk):
    abertura = re.search(r"<svg\b([^>]*)>", texto_snk)
    if not abertura:
        raise ValueError("SVG da cobrinha sem tag <svg>")
    caixa = re.search(r'viewBox="([^"]+)"', abertura.group(1))
    if not caixa:
        raise ValueError("SVG da cobrinha sem viewBox")
    vx, vy, vw, vh = (float(n) for n in caixa.group(1).split())
    interior = texto_snk[abertura.end(): texto_snk.rindex("</svg>")]
    largura_interna = LARGURA - 96
    altura_interna = largura_interna * vh / vw
    altura = int(78 + altura_interna + 30)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGURA} {altura}" width="{LARGURA}" height="{altura}" role="img">'
        "<title>Cobrinha comendo o gráfico de contribuições</title>"
        "<desc>Animação de uma cobrinha percorrendo o gráfico de contribuições de omatosz no GitHub.</desc>"
        f'<defs><linearGradient id="fundo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{P["fundo"]}"/>'
        f'<stop offset="1" stop-color="{P["fundo2"]}"/></linearGradient></defs>'
        f'<rect width="{LARGURA}" height="{altura}" rx="22" fill="url(#fundo)"/>'
        f'<rect x="0.5" y="0.5" width="{LARGURA - 1}" height="{altura - 1}" rx="22" fill="none" stroke="{P["linha"]}"/>'
        f'<text x="48" y="52" font-family="{FONTE}" font-size="13" letter-spacing="2" fill="{P["ciano"]}">ATIVIDADE, EM FORMA DE JOGO</text>'
        f'<svg x="48" y="78" width="{largura_interna}" height="{f(altura_interna)}" viewBox="{f(vx)} {f(vy)} {f(vw)} {f(vh)}">'
        f"{interior}</svg></svg>\n"
    )
