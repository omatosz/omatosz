"""Cartão de números do GitHub: contadores, sequências e nível por XP."""
import math

from animacao import odometro
from base import CSS_BASE, P, ciclo, esc, f, painel, svg

LARGURA, ALTURA = 1200, 330
CICLO = 16


def _tiles(dados):
    itens = [
        (dados["contribuicoes"], "contribuições em 12 meses", P["ciano_claro"]),
        (dados["dias_ativos"], "dias com atividade", P["verde"]),
        (dados["sequencia_atual"], "dias seguidos agora", P["ambar"]),
        (dados["maior_sequencia"], "maior sequência de dias", P["violeta"]),
        (dados["repositorios"], "repositórios públicos", "#7dd3fc"),
        (dados["meses_conta"], "meses no GitHub", P["ciano_claro"]),
    ]
    caixas, numeros = [], []
    for i, (valor, rotulo, cor) in enumerate(itens):
        x = 48 + (i % 3) * 252
        y = 88 + (i // 3) * 112
        caixas.append(
            f'<rect x="{x}" y="{y}" width="238" height="100" rx="14" fill="{P["painel2"]}" fill-opacity="0.55" stroke="{P["linha"]}"/>'
            f'<text class="s" x="{x + 22}" y="{y + 84}" font-size="13.5" fill="{P["mudo"]}">{esc(rotulo)}</text>'
        )
        corpo, _ = odometro(str(valor), x + 22, y + 52, 40, cor, CICLO, esquerda=True)
        numeros.append(corpo)
    return "".join(caixas) + ciclo(CICLO, "".join(numeros))


def _nivel(perfil, dados):
    por_nivel = perfil["xp_por_nivel"]
    xp = dados["xp_total"]
    nivel = xp // por_nivel + 1
    progresso = (xp % por_nivel) / por_nivel
    faltam = por_nivel - xp % por_nivel
    cx, cy, raio = 991, 178, 56
    circ = 2 * math.pi * raio
    corpo_nivel, _ = odometro(str(nivel), cx, cy + 16, 44, P["texto"], CICLO)
    anel = (
        f'<circle cx="{cx}" cy="{cy}" r="{raio}" fill="none" stroke="{P["linha"]}" stroke-width="12"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{raio}" fill="none" stroke="{P["ciano"]}" stroke-width="12" stroke-linecap="round" '
        f'stroke-dasharray="{f(circ)}" stroke-dashoffset="{f(circ)}" transform="rotate(-90 {cx} {cy})">'
        f'<animate attributeName="stroke-dashoffset" dur="{CICLO}s" repeatCount="indefinite" calcMode="spline" '
        f'keyTimes="0;0.03;0.2;1" values="{f(circ)};{f(circ)};{f(circ * (1 - progresso))};{f(circ * (1 - progresso))}" '
        'keySplines="0 0 1 1;0.2 0.8 0.2 1;0 0 1 1"/></circle>'
    )
    return (
        f'<rect x="804" y="88" width="348" height="212" rx="14" fill="{P["painel2"]}" fill-opacity="0.55" stroke="{P["linha"]}"/>'
        f'<text class="m" x="{cx}" y="{cy - 20}" text-anchor="middle" font-size="12" letter-spacing="2" fill="{P["fraco"]}">NÍVEL</text>'
        + ciclo(CICLO, anel + corpo_nivel)
        + f'<text class="s" x="{cx}" y="266" text-anchor="middle" font-size="14" fill="{P["mudo"]}">faltam {faltam} contribuições para o nível {nivel + 1}</text>'
        f'<text class="m" x="{cx}" y="286" text-anchor="middle" font-size="12" fill="{P["fraco"]}">{dados["xp_total"]} contribuições desde que a conta existe</text>'
    )


def desenhar(perfil, dados):
    defs, fundo = painel(LARGURA, ALTURA, 22, "rc")
    atualizado = dados["gerado_em"].strftime("%d/%m/%Y")
    corpo = (
        fundo
        + '<g clip-path="url(#rc)">'
        f'<text class="m" x="48" y="52" font-size="13" letter-spacing="2" fill="{P["ciano"]}">GITHUB EM NÚMEROS</text>'
        f'<text class="m" x="1152" y="52" text-anchor="end" font-size="12" fill="{P["fraco"]}">atualizado em {atualizado}</text>'
        + _tiles(dados)
        + _nivel(perfil, dados)
        + "</g>"
    )
    return svg(LARGURA, ALTURA, "Números do GitHub de omatosz",
               "Contribuições, dias ativos, sequências, repositórios e nível calculado pelas contribuições.",
               corpo, defs, CSS_BASE)
