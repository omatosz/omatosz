"""Troféus com nota (D a SSS) e os marcos do Veryon, no visual do portfólio:
nota gigante em vermelho, valor contando, barra até a próxima nota e a lista de
marcos com o quadradinho vermelho dos tópicos do site.
"""
from animacao import conta
from base import MARGEM, LARGURA, P, cartao, ciclo, f, milhar, movimento, svg
from texto import Tinta, altura_cap, largura

CICLO = 20
NOTAS = ["C", "B", "A", "S", "SS", "SSS"]


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


def _valores(perfil, dados):
    testes = next(n["valor"] for n in perfil["veryon"]["numeros"] if n["chave"] == "testes")
    return {
        "contribuicoes": dados["contribuicoes"],
        "commits_veryon": dados["commits_veryon"] or 0,
        "linhas": dados["linhas_total"],
        "repositorios": dados["repositorios"],
        "linguagens": dados["linguagens"],
        "testes": testes,
    }


def _trofeus(t, perfil, dados, y0):
    valores = _valores(perfil, dados)
    vao = 16
    w = (LARGURA - 2 * MARGEM - 2 * vao) / 3
    h = 184
    caixas, animados, parados = [], [], []
    for i, tr in enumerate(perfil["trofeus"]):
        valor = valores[tr["id"]]
        nota, indice, alvo, base = nota_de(valor, tr["faixas"])
        proxima = NOTAS[indice + 1] if indice + 1 < len(NOTAS) else None
        legenda = f"{proxima} EM {milhar(alvo)}" if alvo else "NOTA MÁXIMA"
        progresso = 1.0 if not alvo else max(0.0, min(1.0, (valor - base) / (alvo - base)))
        x, y = MARGEM + (i % 3) * (w + vao), y0 + (i // 3) * (h + vao)
        xi = x + 24
        # a nota fica à direita, do tamanho que couber sem encostar no valor
        larg_valor = largura(milhar(valor), "titulo70", 52)
        tam_nota = 116
        while x + w - 24 - largura(nota, "titulo", tam_nota) < xi + larg_valor + 20 and tam_nota > 60:
            tam_nota -= 4
        larg_barra = min(210, w - 48 - largura(nota, "titulo", tam_nota) - 24)
        caixas.append(
            f'<rect x="{f(x + 0.5)}" y="{f(y + 0.5)}" width="{f(w - 1)}" height="{h - 1}" fill="none" stroke="{P["linha"]}"/>'
            + t.texto(tr["titulo"], xi, y + 46, "titulo75", 30, P["creme"])
            + t.texto(tr["sub"].upper(), xi, y + 70, "mono", 12, P["creme500"], 0.18)
            + t.texto(nota, x + w - 24, y + 40 + altura_cap("titulo", tam_nota), "titulo", tam_nota, P["vermelho"],
                      ancora="end")
            + f'<rect x="{f(xi)}" y="{y + 146}" width="{f(larg_barra)}" height="6" fill="{P["linha"]}"/>'
            + t.texto(legenda, xi, y + 170, "mono", 12, P["creme500"], 0.18)
        )
        cheia = larg_barra * progresso
        animados.append(
            conta(t, valor, xi, y + 128, "titulo70", 52, P["creme"], CICLO)
            + f'<rect x="{f(xi)}" y="{y + 146}" width="0" height="6" fill="{P["vermelho"]}">'
              f'<animate attributeName="width" dur="{CICLO}s" repeatCount="indefinite" calcMode="spline" '
              f'keyTimes="0;0.01;0.11;1" values="0;0;{f(cheia)};{f(cheia)}" '
              f'keySplines="0 0 1 1;0.22 1 0.36 1;0 0 1 1"/></rect>'
        )
        parados.append(t.texto(milhar(valor), xi, y + 128, "titulo70", 52, P["creme"])
                       + f'<rect x="{f(xi)}" y="{y + 146}" width="{f(cheia)}" height="6" fill="{P["vermelho"]}"/>')
    fundo = y0 + 2 * h + vao
    return "".join(caixas) + movimento(ciclo(CICLO, "".join(animados)), "".join(parados)), fundo


def _marcos(t, marcos, y0):
    colunas = 3
    larg = (LARGURA - 2 * MARGEM) / colunas
    linhas = -(-len(marcos) // colunas)
    itens = []
    for i, texto in enumerate(marcos):
        col, lin = i // linhas, i % linhas
        x, y = MARGEM + col * larg, y0 + lin * 38
        itens.append(f'<rect x="{f(x)}" y="{f(y - 11)}" width="7" height="7" fill="{P["vermelho"]}"/>'
                     + t.texto(texto, x + 20, y, "texto", 18, P["creme100"]))
    return "".join(itens), y0 + (linhas - 1) * 38


def desenhar(perfil, dados):
    t = Tinta()
    cabeca = (t.texto("[ TROFÉUS ]", MARGEM, 70, "mono", 16, P["vermelho"], 0.18)
              + t.texto("NOTA POR FAIXA DE VALOR, DE D A SSS", LARGURA - MARGEM, 70, "mono", 13, P["creme500"],
                        0.18, "end"))
    trofeus, fundo = _trofeus(t, perfil, dados, 104)
    y_marcos = fundo + 72
    rotulo = t.texto("[ MARCOS DO VERYON ]", MARGEM, y_marcos, "mono", 16, P["vermelho"], 0.18)
    marcos, fim = _marcos(t, perfil["marcos"], y_marcos + 52)
    altura = round(fim + 52)
    corpo = cartao(LARGURA, altura) + cabeca + trofeus + rotulo + marcos
    valores = _valores(perfil, dados)
    alt = "; ".join(f'{tr["titulo"]} {tr["sub"]}: {milhar(valores[tr["id"]])}, nota {nota_de(valores[tr["id"]], tr["faixas"])[0]}'
                    for tr in perfil["trofeus"])
    alt += ". Marcos do Veryon: " + ", ".join(perfil["marcos"]) + "."
    return svg(LARGURA, altura, "Troféus e marcos", alt, corpo, t.defs())
