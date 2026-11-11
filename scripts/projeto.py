"""Cartão de outro projeto, no desenho dos projetos secundários do portfólio:
selo de status, nome, linha de destaque, descrição, botão e, à direita, os
tópicos e a stack.
"""
from base import MARGEM, LARGURA, P, cartao, f, svg
from texto import Tinta, altura_cap, largura, quebrar
import botoes

TAM_NOME = 96


def desenhar(perfil):
    p = perfil["projeto"]
    t = Tinta()
    x0 = MARGEM
    col_esq = 620
    x_dir = 760
    larg_dir = LARGURA - MARGEM - x_dir

    rotulo = t.texto(f'[ {p["rotulo"]} ]'.upper(), x0, 70, "mono", 16, P["vermelho"], 0.18)
    y_selo = 100
    selo_txt = p["status"].upper()
    w_selo = largura(selo_txt, "mono", 13, 0.18) + 46
    selo = (f'<rect x="{f(x0 + 0.5)}" y="{y_selo + 0.5}" width="{f(w_selo)}" height="29" fill="none" '
            f'stroke="{P["creme"]}" stroke-opacity="0.25"/>'
            f'<rect x="{x0 + 13}" y="{y_selo + 12}" width="6" height="6" fill="{P["vermelho"]}"/>'
            + t.texto(selo_txt, x0 + 28, y_selo + 20, "mono", 13, P["creme100"], 0.18))
    y_nome = round(y_selo + 30 + 40 + altura_cap("titulo", TAM_NOME))
    nome = t.texto(p["nome"].upper(), x0, y_nome, "titulo", TAM_NOME, P["creme"])
    y_linha = y_nome + 54
    destaque = "".join(t.texto(l, x0, y_linha + i * 32, "forte90", 25, P["creme"])
                       for i, l in enumerate(quebrar(p["linha"], "forte90", 25, col_esq)))
    y_desc = y_linha + 46
    descricao, alt_desc = t.paragrafo(p["descricao"], x0, y_desc, "texto", 18, P["creme300"], col_esq, 1.6)
    y_botao = y_desc + alt_desc - 18 * 1.6 + 38
    botao, _ = botoes.desenho(t, p["botao"], "contorno", x0, y_botao, 2.0)
    fundo_esq = y_botao + botoes.ALTURA

    # coluna da direita, alinhada pela base da esquerda
    topicos, alt_topicos = [], 0
    blocos = [quebrar(texto, "texto", 18, larg_dir - 22) for texto in p["pontos"]]
    alt_topicos = sum(len(b) * 29 + 14 for b in blocos)
    linhas_stack = quebrar("  /  ".join(p["stack"]).upper(), "mono", 13, larg_dir, 0.18)
    alt_dir = alt_topicos + 34 + len(linhas_stack) * 21
    y = fundo_esq - alt_dir + 12
    for bloco in blocos:
        topicos.append(f'<rect x="{x_dir}" y="{f(y - 11)}" width="7" height="7" fill="{P["vermelho"]}"/>')
        for k, linha in enumerate(bloco):
            topicos.append(t.texto(linha, x_dir + 22, y + k * 29, "texto", 18, P["creme100"]))
        y += len(bloco) * 29 + 14
    y += 20
    for k, linha in enumerate(linhas_stack):
        topicos.append(t.texto(linha, x_dir, y + k * 21, "mono", 13, P["creme500"], 0.18))
    divisa = f'<path d="M{x_dir - 40.5} {y_selo}V{f(fundo_esq)}" stroke="{P["linha"]}"/>'
    altura = round(fundo_esq + 56)
    corpo = cartao(LARGURA, altura) + rotulo + selo + nome + destaque + descricao + botao + divisa + "".join(topicos)
    alt = f'{p["nome"]}: {p["linha"]}. {p["descricao"]} ' + " ".join(p["pontos"])
    return svg(LARGURA, altura, p["nome"], alt, corpo, t.defs(), botoes.css())
