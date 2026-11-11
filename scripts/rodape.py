"""Rodapé, igual ao do portfólio: o nome cheio num tom quase igual ao fundo,
ocupando a largura. No site ele fica vermelho com o mouse; aqui o vermelho
passa por ele letra por letra de tempos em tempos.
"""
from base import MARGEM, LARGURA, P, SOFT, f, movimento, svg
from texto import Tinta, altura_cap, largura

CICLO = 12


def desenhar(perfil, dados):
    t = Tinta()
    nome = perfil["nome"].upper()
    larg = LARGURA - 2 * MARGEM
    tam = larg / largura(nome, "titulo", 100) * 100
    cap = altura_cap("titulo", tam)
    y_nome = round(64 + cap)
    animado = []
    for i, (ch, x, _) in enumerate(t.letras(nome, MARGEM, y_nome, "titulo", tam)):
        if ch == " ":
            continue
        ini = 2.0 + i * 0.06
        kt = ";".join(f"{v / CICLO:.4f}" for v in (0, ini, ini + 0.7, ini + 2.2, ini + 2.9, CICLO))
        animado.append(t.glifo(ch, x, y_nome, "titulo", tam, P["painel2"], filhos=(
            f'<animate attributeName="fill" values="{P["painel2"]};{P["painel2"]};{P["vermelho"]};{P["vermelho"]};'
            f'{P["painel2"]};{P["painel2"]}" keyTimes="{kt}" dur="{CICLO}s" repeatCount="indefinite" '
            f'calcMode="spline" keySplines="0 0 1 1;{SOFT};0 0 1 1;{SOFT};0 0 1 1"/>')))
    parado = t.texto(nome, MARGEM, y_nome, "titulo", tam, P["painel2"])
    y_linha = y_nome + 48
    y_txt = y_linha + 44
    ano = dados["gerado_em"].year
    rodape = (
        f'<path d="M0 {y_linha + 0.5}H{LARGURA}" stroke="{P["linha"]}"/>'
        + t.texto(f"© {ano} {nome}", MARGEM, y_txt, "mono", 13, P["creme500"], 0.18)
        + t.texto(perfil["rodape"].upper(), LARGURA / 2, y_txt, "mono", 13, P["creme500"], 0.18, "middle")
        + t.texto("GITHUB.COM/" + perfil["usuario"].upper(), LARGURA - MARGEM, y_txt, "mono", 13, P["creme300"],
                  0.18, "end")
    )
    altura = y_txt + 34
    corpo = (f'<rect width="{LARGURA}" height="{altura}" fill="{P["fundo"]}"/>'
             + movimento("".join(animado), parado) + rodape)
    return svg(LARGURA, altura, f"{perfil['nome']}, rodapé", f"© {ano} {perfil['nome']}. {perfil['rodape']}.",
               corpo, t.defs())
