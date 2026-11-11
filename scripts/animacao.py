"""Animações reutilizáveis, todas por tempo (imagem não recebe clique nem mouse).

SMIL para o que tem hora marcada dentro de um ciclo (contagem, embaralhamento,
etapas) e CSS para os laços contínuos. Quem usa estas funções coloca ao lado
uma versão parada, para quem pediu menos movimento (ver base.movimento).
"""
from base import f, milhar, suave

QUADRO = 0.045  # segundos por troca de letra, como no Glitch do portfólio
POOLS = {
    "maiuscula": "ABCDEFGHIJKLMNOPQRSTUVWXYZ#%&$",
    "minuscula": "abcdefghijklmnopqrstuvwxyz",
    "digito": "0123456789",
    "outro": "/\\<>[]{}=+*?!",
}


def _pool(ch):
    if ch.isdigit():
        return POOLS["digito"]
    if ch.isalpha():
        return POOLS["maiuscula"] if ch.isupper() else POOLS["minuscula"]
    return POOLS["outro"]


def janela(ciclo, ini, fim=None):
    """<animate> que deixa o elemento visível entre `ini` e `fim` (segundos) de cada ciclo."""
    pontos = []
    if ini > 0:
        pontos.append((0, "hidden"))
    pontos.append((ini, "visible"))
    if fim is not None and fim < ciclo:
        pontos.append((fim, "hidden"))
    tempos = ";".join(f"{t / ciclo:.5f}" for t, _ in pontos)
    valores = ";".join(v for _, v in pontos)
    return (f'<animate attributeName="visibility" dur="{f(ciclo)}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{tempos}" values="{valores}"/>')


def degraus(ciclo, atributo, pontos):
    """<animate> discreto de qualquer atributo: [(segundo, valor), ...], o primeiro em 0."""
    if pontos[0][0] > 0:
        raise ValueError("o primeiro ponto precisa estar no segundo 0")
    tempos = ";".join(f"{t / ciclo:.5f}" for t, _ in pontos)
    valores = ";".join(str(v) for _, v in pontos)
    return (f'<animate attributeName="{atributo}" dur="{f(ciclo)}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{tempos}" values="{valores}"/>')


def conta(t, valor, x, y, chave, tam, cor, ciclo, inicio=0.15, duracao=1.8, ancora="start", formato=milhar):
    """Número que conta de zero até o valor (o CountUp do portfólio: 1,8 s, curva suave)."""
    quadros = []
    n = 30
    for k in range(n + 1):
        v = round(valor * suave(k / n))
        if not quadros or quadros[-1][1] != v:
            quadros.append((inicio + duracao * k / n, v))
    partes = []
    for i, (instante, v) in enumerate(quadros):
        fim = quadros[i + 1][0] if i + 1 < len(quadros) else None
        partes.append(f'<g visibility="hidden">{janela(ciclo, instante, fim)}'
                      f'{t.texto(formato(v), x, y, chave, tam, cor, ancora=ancora)}</g>')
    return "".join(partes)


def embaralha(t, texto, x, y, chave, tam, cor, ciclo, ini, fim, rng, duracao=0.42, espaco=0.0, ancora="start"):
    """O texto aparece em `ini` embaralhado e assenta letra por letra; some em `fim`.

    Igual ao Glitch do portfólio: as letras do começo tendem a assentar antes, e o
    texto inteiro é redesenhado a cada 45 ms.
    """
    n = max(len(texto), 1)
    assenta = [(i / n) * duracao * 0.55 + rng.random() * duracao * 0.45 for i in range(n)]
    quadros = int(max(assenta) / QUADRO) + 1
    partes = []
    for k in range(quadros):
        instante = k * QUADRO
        estado = "".join(
            c if (c == " " or instante >= assenta[i]) else rng.choice(_pool(c)) for i, c in enumerate(texto)
        )
        partes.append(f'<g visibility="hidden">{janela(ciclo, ini + instante, ini + instante + QUADRO)}'
                      f'{t.texto(estado, x, y, chave, tam, cor, espaco, ancora)}</g>')
    partes.append(f'<g visibility="hidden">{janela(ciclo, ini + quadros * QUADRO, fim)}'
                  f'{t.texto(texto, x, y, chave, tam, cor, espaco, ancora)}</g>')
    return "".join(partes)


def tremor(ciclo, ini, duracao, rng, amplitude=3.0):
    """<animateTransform> com os saltinhos do efeito de falha entre `ini` e `ini + duracao`."""
    passos = 8
    pontos = [] if ini <= 0 else [(0, "0 0")]
    for k in range(passos):
        pontos.append((ini + duracao * k / passos,
                       f"{f(rng.uniform(-amplitude, amplitude))} {f(rng.uniform(-amplitude / 3, amplitude / 3))}"))
    pontos.append((ini + duracao, "0 0"))
    tempos = ";".join(f"{t / ciclo:.5f}" for t, _ in pontos)
    valores = ";".join(v for _, v in pontos)
    return (f'<animateTransform attributeName="transform" type="translate" dur="{f(ciclo)}s" '
            f'repeatCount="indefinite" calcMode="discrete" keyTimes="{tempos}" values="{valores}"/>')
