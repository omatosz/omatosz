"""Animações SMIL reutilizáveis: máquina de escrever e odômetro.

SMIL é o jeito de animar SVG sem JavaScript, e o GitHub deixa passar quando o
SVG é carregado como imagem. Todas as animações aqui são por tempo (nada de
clique ou hover, que não funcionam em imagem).
"""
from base import P, esc, f


def _discreto(eventos, duracao):
    """Converte [(tempo, valor), ...] em keyTimes e values para calcMode="discrete"."""
    tempos, valores = [], []
    for tempo, valor in eventos:
        fracao = min(tempo / duracao, 0.9999)
        if tempos and fracao <= tempos[-1]:
            continue
        tempos.append(fracao)
        valores.append(valor)
    return ";".join(f"{t:.5f}" for t in tempos), ";".join(f(v) for v in valores)


def digitacao(frases, x, y, tam, cor, id_="dg", t_digita=0.055, t_retem=1.9, t_apaga=0.022, t_pausa=0.45):
    """Texto que digita, espera, apaga e passa para a próxima frase, em loop.

    Retorna (defs, corpo). Cada frase é revelada por um retângulo de recorte
    cuja largura sobe de caractere em caractere.
    """
    cw = tam * 0.6  # largura de um caractere em fonte monoespaçada
    slots = [len(fr) * t_digita + t_retem + len(fr) * t_apaga + t_pausa for fr in frases]
    total = sum(slots)
    globais = [(0.0, 0.0)]
    defs, corpo = [], []
    inicio = 0.0
    for i, (frase, slot) in enumerate(zip(frases, slots)):
        n = len(frase)
        eventos = [(inicio + k * t_digita, k * cw) for k in range(1, n + 1)]
        t0 = inicio + n * t_digita + t_retem
        eventos += [(t0 + k * t_apaga, (n - k) * cw) for k in range(1, n + 1)]
        globais += eventos
        tempos, larguras = _discreto([(0.0, 0.0)] + eventos, total)
        defs.append(
            f'<clipPath id="{id_}{i}"><rect x="{f(x)}" y="{f(y - tam)}" width="0" height="{f(tam * 1.5)}">'
            f'<animate attributeName="width" dur="{f(total)}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{tempos}" values="{larguras}"/></rect></clipPath>'
        )
        corpo.append(
            f'<text class="m" x="{f(x)}" y="{f(y)}" font-size="{tam}" fill="{cor}" '
            f'textLength="{f(n * cw)}" lengthAdjust="spacing" clip-path="url(#{id_}{i})">{esc(frase)}</text>'
        )
        inicio += slot
    # cursor: acompanha a largura da frase que estiver ativa
    globais.sort()
    tempos, xs = _discreto([(t, x + w + 2) for t, w in globais], total)
    corpo.append(
        f'<rect x="{f(x)}" y="{f(y - tam * 0.9)}" width="{f(tam * 0.5)}" height="{f(tam * 1.1)}" fill="{cor}">'
        f'<animate attributeName="x" dur="{f(total)}s" repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="{tempos}" values="{xs}"/>'
        '<animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="discrete" '
        'keyTimes="0;0.55" values="1;0"/></rect>'
    )
    return "".join(defs), "".join(corpo)


def odometro(texto, cx, y_base, tam, cor, duracao, peso=700, esquerda=False):
    """Número que rola como odômetro até o valor final.

    `texto` já vem formatado (por exemplo '17.824'). Cada dígito é uma tira
    vertical de dígitos dentro de uma janela do tamanho de uma linha; a tira
    sobe até o dígito certo. O dígito da direita dá mais voltas, como num
    contador de verdade. Retorna (corpo, largura_total).
    """
    cw = tam * 0.62  # célula de um dígito
    sw = tam * 0.34  # célula do separador de milhar
    larguras = [cw if c.isdigit() else sw for c in texto]
    total = sum(larguras)
    x = cx if esquerda else cx - total / 2
    linha = tam * 1.25  # distância entre dígitos da tira (maior que a janela)
    janela = tam * 1.15
    topo = y_base - tam * 0.9
    n_digitos = sum(c.isdigit() for c in texto)
    partes = []
    j = 0
    for caractere, largura in zip(texto, larguras):
        if not caractere.isdigit():
            partes.append(
                f'<text class="m" x="{f(x + largura / 2)}" y="{f(y_base)}" text-anchor="middle" '
                f'font-size="{tam}" font-weight="{peso}" fill="{cor}">{esc(caractere)}</text>'
            )
        else:
            digito = int(caractere)
            da_direita = n_digitos - 1 - j
            voltas = 2 if da_direita == 0 else (1 if da_direita == 1 else 0)
            indice = 10 * voltas + digito
            subida = indice * linha
            tira = "".join(
                f'<text class="m" x="{f(largura / 2)}" y="{f(tam * 0.9 + i * linha)}" text-anchor="middle" '
                f'font-size="{tam}" font-weight="{peso}" fill="{cor}">{i % 10}</text>'
                for i in range(indice + 1)
            )
            fim_rolagem = 0.03 + 2.4 / duracao
            partes.append(
                f'<svg x="{f(x)}" y="{f(topo)}" width="{f(largura)}" height="{f(janela)}">'
                '<g><animateTransform attributeName="transform" type="translate" '
                f'dur="{f(duracao)}s" repeatCount="indefinite" calcMode="spline" '
                f'keyTimes="0;0.03;{fim_rolagem:.4f};0.985;1" '
                'keySplines="0 0 1 1;0.16 1 0.3 1;0 0 1 1;0 0 1 1" '
                f'values="0 0;0 0;0 -{f(subida)};0 -{f(subida)};0 0"/>'
                f"{tira}</g></svg>"
            )
            j += 1
        x += largura
    return "".join(partes), total
