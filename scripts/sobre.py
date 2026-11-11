"""Cartão "Sobre", no desenho da seção Sobre do portfólio: fundo cream, título
com tarjas pretas que saem palavra por palavra (como um documento sendo
liberado) e as três frentes de atuação embaixo.
"""
from base import MARGEM, LARGURA, P, SNAP, f, movimento, svg
from texto import Tinta, altura_cap, quebrar

CICLO = 16
TAM_TITULO = 92
ENTRELINHA = 0.92


def _titulo(t, texto, destaque, y_base):
    """Título quebrado em linhas, com o trecho destacado em vermelho e as tarjas."""
    palavras = texto.upper().split()
    alvo = destaque.upper().split()
    limpas = [p.strip(".,!?") for p in palavras]
    marcadas = [False] * len(palavras)
    for i in range(len(palavras) - len(alvo) + 1):
        if limpas[i:i + len(alvo)] == alvo:
            for k in range(len(alvo)):
                marcadas[i + k] = True
            break
    linhas = quebrar(" ".join(palavras), "titulo", TAM_TITULO, LARGURA - 2 * MARGEM)
    texto_svg, tarjas, ordem = [], [], 0
    espaco = t.letras(" ", 0, 0, "titulo", TAM_TITULO)[0][2]
    for li, linha in enumerate(linhas):
        y = y_base + li * TAM_TITULO * ENTRELINHA
        x = MARGEM
        for palavra in linha.split():
            cor = P["vermelho"] if marcadas[ordem] else P["fundo"]
            texto_svg.append(t.texto(palavra, x, y, "titulo", TAM_TITULO, cor))
            larg = t.letras(palavra, x, y, "titulo", TAM_TITULO)
            fim = larg[-1][1] + larg[-1][2]
            x0, w = x - TAM_TITULO * 0.04, fim - x + TAM_TITULO * 0.08
            # cobre também os acentos das maiúsculas (o Ê de "defendê-lo")
            topo, alt = y - TAM_TITULO * 0.86, TAM_TITULO * 1.0
            sai = 0.15 + ordem * 0.07
            volta = CICLO - 2.2 + ordem * 0.05
            tempos = [0, sai, sai + 0.55, volta, volta + 0.45, CICLO]
            kt = ";".join(f"{v / CICLO:.4f}" for v in tempos)
            spl = f"0 0 1 1;{SNAP};0 0 1 1;{SNAP};0 0 1 1"
            comum = f'dur="{CICLO}s" repeatCount="indefinite" keyTimes="{kt}" calcMode="spline" keySplines="{spl}"'
            tarjas.append(
                f'<rect x="{f(x0)}" y="{f(topo)}" width="{f(w)}" height="{f(alt)}" fill="{P["fundo"]}">'
                f'<animate attributeName="width" values="{f(w)};{f(w)};0;0;{f(w)};{f(w)}" {comum}/>'
                f'<animate attributeName="x" values="{f(x0)};{f(x0)};{f(x0 + w)};{f(x0)};{f(x0)};{f(x0)}" {comum}/>'
                "</rect>"
            )
            x = fim + espaco
            ordem += 1
    altura = (len(linhas) - 1) * TAM_TITULO * ENTRELINHA
    return "".join(texto_svg), "".join(tarjas), altura


def desenhar(perfil):
    s = perfil["sobre"]
    t = Tinta()
    y_rotulo = 88
    rotulo = t.texto(f'[ {s["rotulo"]} ]'.upper(), MARGEM, y_rotulo, "mono", 17, P["vermelho600"], 0.18)
    y_titulo = round(y_rotulo + 52 + altura_cap("titulo", TAM_TITULO))
    titulo, tarjas, alt_titulo = _titulo(t, s["titulo"], s["destaque"], y_titulo)

    # dois parágrafos lado a lado
    larg_col = (LARGURA - 2 * MARGEM - 52) / 2
    y_texto = y_titulo + alt_titulo + 76
    paragrafos, fundo_texto = [], y_texto
    for i, texto in enumerate(s["texto"]):
        corpo, alt = t.paragrafo(texto, MARGEM + i * (larg_col + 52), y_texto, "texto", 21, P["painel2"],
                                 larg_col, 1.6)
        paragrafos.append(corpo)
        fundo_texto = max(fundo_texto, y_texto + alt - 21 * 1.6)

    # as três frentes, com a linha de cima que fica vermelha (o hover do site)
    y_frentes = fundo_texto + 70
    n = len(s["frentes"])
    larg_f = (LARGURA - 2 * MARGEM - 40 * (n - 1)) / n
    frentes, linhas_vermelhas, fundo = [], [], y_frentes
    for i, fr in enumerate(s["frentes"]):
        x = MARGEM + i * (larg_f + 40)
        y_nome = y_frentes + 26 + altura_cap("titulo75", 40)
        corpo, alt = t.paragrafo(fr["texto"], x, y_nome + 42, "texto", 18, P["painel2"], larg_f, 1.6)
        frentes.append(f'<rect x="{f(x)}" y="{f(y_frentes)}" width="{f(larg_f)}" height="2" fill="{P["fundo"]}"/>'
                       + t.texto(fr["titulo"], x, y_nome, "titulo75", 40, P["fundo"]) + corpo)
        fundo = max(fundo, y_nome + 42 + alt - 18 * 1.6)
        ini = 3.2 + i * 0.35
        kt = ";".join(f"{v / CICLO:.4f}" for v in (0, ini, ini + 0.5, ini + 1.8, ini + 2.3, CICLO))
        linhas_vermelhas.append(
            f'<rect x="{f(x)}" y="{f(y_frentes)}" width="0" height="2" fill="{P["vermelho"]}">'
            f'<animate attributeName="width" values="0;0;{f(larg_f)};{f(larg_f)};0;0" dur="{CICLO}s" '
            f'repeatCount="indefinite" keyTimes="{kt}" calcMode="spline" '
            f'keySplines="0 0 1 1;{SNAP};0 0 1 1;{SNAP};0 0 1 1"/></rect>'
        )
    altura = round(fundo + 72)
    corpo = (
        f'<rect width="{LARGURA}" height="{altura}" fill="{P["creme"]}"/>'
        + rotulo
        + titulo
        + movimento(tarjas, "")
        + "".join(paragrafos)
        + "".join(frentes)
        + movimento("".join(linhas_vermelhas), "")
    )
    alt_texto = " ".join([s["titulo"]] + s["texto"] + [f'{fr["titulo"]}: {fr["texto"]}' for fr in s["frentes"]])
    return svg(LARGURA, altura, "Sobre", alt_texto, corpo, t.defs())
