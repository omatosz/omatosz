"""Cartão de números do GitHub: a grade de números contando, como as do
portfólio, e o nível por contribuições numa barra segmentada que enche.
"""
from animacao import conta, janela
from base import MARGEM, LARGURA, P, cartao, ciclo, f, milhar, movimento, svg
from texto import Tinta, altura_cap, quebrar

CICLO = 20
ALTURA = 432


def _grade(t, itens, x0, y0, larg):
    cw, ch = larg / 3, 136
    linhas = "".join(f"M{f(x0)} {f(y0 + k * ch + 0.5)}H{f(x0 + larg)}" for k in range(3))
    linhas += "".join(f"M{f(x0 + k * cw + 0.5)} {f(y0)}V{f(y0 + 2 * ch)}" for k in range(4))
    animados, parados, rotulos = [], [], []
    for i, (valor, rotulo) in enumerate(itens):
        cx, cy = x0 + (i % 3) * cw + 22, y0 + (i // 3) * ch
        animados.append(conta(t, valor, cx, cy + 70, "titulo70", 60, P["vermelho"], CICLO))
        parados.append(t.texto(milhar(valor), cx, cy + 70, "titulo70", 60, P["vermelho"]))
        for k, linha in enumerate(quebrar(rotulo.upper(), "mono", 13, cw - 44, 0.18)[:2]):
            rotulos.append(t.texto(linha, cx, cy + 100 + k * 19, "mono", 13, P["creme500"], 0.18))
    return (f'<path d="{linhas}" stroke="{P["linha"]}"/>'
            + movimento(ciclo(CICLO, "".join(animados)), "".join(parados)) + "".join(rotulos))


def _nivel(t, perfil, dados, x0, y0, larg, alt):
    por_nivel = perfil["xp_por_nivel"]
    xp = dados["xp_total"]
    nivel = xp // por_nivel + 1
    feito = xp % por_nivel
    faltam = por_nivel - feito
    x = x0 + 26
    caixa = f'<rect x="{f(x0 + 0.5)}" y="{f(y0 + 0.5)}" width="{f(larg - 1)}" height="{f(alt - 1)}" fill="none" stroke="{P["linha"]}"/>'
    rotulo = t.texto("NÍVEL", x, y0 + 40, "mono", 13, P["creme500"], 0.18)
    numero = t.texto(f"{nivel:02d}", x, y0 + 52 + altura_cap("titulo", 120), "titulo", 120, P["creme"])
    # barra com um segmento por contribuição do nível; os feitos acendem em fila
    vao = 3
    sw = (larg - 52 - vao * (por_nivel - 1)) / por_nivel
    y_barra = y0 + 178
    base, acesos, parados = [], [], []
    for k in range(por_nivel):
        sx = x + k * (sw + vao)
        base.append(f'<rect x="{f(sx)}" y="{y_barra}" width="{f(sw)}" height="22" fill="{P["linha"]}"/>')
        if k < feito:
            acesos.append(f'<rect x="{f(sx)}" y="{y_barra}" width="{f(sw)}" height="22" fill="{P["vermelho"]}" '
                          f'visibility="hidden">{janela(CICLO, 0.5 + k * 0.06, CICLO - 0.6)}</rect>')
            parados.append(f'<rect x="{f(sx)}" y="{y_barra}" width="{f(sw)}" height="22" fill="{P["vermelho"]}"/>')
    textos = (t.texto(f"FALTAM {faltam} PARA O NÍVEL {nivel + 1}", x, y_barra + 50, "mono", 13, P["creme300"], 0.18)
              + t.texto(f"{milhar(xp)} CONTRIBUIÇÕES NO TOTAL", x, y_barra + 71, "mono", 13, P["creme500"], 0.18))
    return caixa + rotulo + numero + "".join(base) + movimento("".join(acesos), "".join(parados)) + textos


def desenhar(perfil, dados):
    t = Tinta()
    atualizado = dados["gerado_em"].strftime("%d/%m/%Y")
    cabeca = (t.texto("[ GITHUB EM NÚMEROS ]", MARGEM, 70, "mono", 16, P["vermelho"], 0.18)
              + t.texto(f"ATUALIZADO EM {atualizado}", LARGURA - MARGEM, 70, "mono", 13, P["creme500"], 0.18, "end"))
    itens = [
        (dados["contribuicoes"], "contribuições em 12 meses"),
        (dados["dias_ativos"], "dias com atividade"),
        (dados["sequencia_atual"], "dias seguidos agora"),
        (dados["maior_sequencia"], "maior sequência de dias"),
        (dados["repositorios"], "repositórios públicos"),
        (dados["meses_conta"], "meses no GitHub"),
    ]
    y0 = 104
    larg_grade = 756
    corpo = (
        cartao(LARGURA, ALTURA)
        + cabeca
        + _grade(t, itens, MARGEM, y0, larg_grade)
        + _nivel(t, perfil, dados, MARGEM + larg_grade + 32, y0, LARGURA - 2 * MARGEM - larg_grade - 32, 272)
    )
    alt = ", ".join(f"{milhar(v)} {r}" for v, r in itens)
    return svg(LARGURA, ALTURA, "Números do GitHub de omatosz", alt + ".", corpo, t.defs())
