"""Banner do topo, no desenho do topo do portfólio.

O nome gigante embaralha e assenta letra por letra ao carregar, com o efeito de
falha (cópias deslocadas em vermelho e o tremor). Depois, a cada ciclo, as
letras esticam uma por uma, como quando o mouse passa por cima delas no site, e
de vez em quando o nome falha de novo. Embaixo, as duas fitas inclinadas rolam
em sentidos opostos.
"""
import math
import random

from base import MARGEM, LARGURA, P, SOFT, f, marcas, movimento, suave, svg
from texto import Tinta, altura_cap, estilo, largura, quebrar

ALTURA = 650
TAM_NOME = 236
ENTRELINHA_NOME = 0.84
TOPO_NOME = 104          # altura do topo das maiúsculas da primeira linha

GLIFOS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#%&$@/<>01"  # os mesmos do nome no portfólio
QUADRO = 0.045           # segundos por troca de letra no embaralhamento

CICLO = 12               # segundos entre uma onda e a próxima
INICIO = 1.8             # a primeira onda começa logo depois do nome assentar
PASSO_ONDA = 0.3         # o "mouse" passa por uma letra a cada 0,3 s
SOBE, SEGURA, DESCE = 0.32, 0.06, 0.42
FALHA = (7.0, 0.35)      # início e duração da falha dentro do ciclo

CSS = (
    "@keyframes sobe{from{opacity:0;transform:translateY(18px)}}"
    ".sobe{animation:sobe .7s cubic-bezier(.22,1,.36,1) backwards}"
    "@keyframes fita{to{transform:translateX(var(--d))}}"
    ".fita{animation:fita var(--t) linear infinite}"
)


def _tempos_onda(i):
    """keyTimes da letra i dentro do ciclo: parada, sobe, segura, desce, parada."""
    a = i * PASSO_ONDA
    pontos = [0, a, a + SOBE, a + SOBE + SEGURA, a + SOBE + SEGURA + DESCE, CICLO]
    return [p / CICLO for p in pontos]


def _esticado(i, t):
    """Quanto a letra i está esticada (0 a 1) no instante t do ciclo."""
    a = i * PASSO_ONDA
    if t < a or t > a + SOBE + SEGURA + DESCE:
        return 0.0
    if t < a + SOBE:
        return suave((t - a) / SOBE)
    if t < a + SOBE + SEGURA:
        return 1.0
    return 1 - suave((t - a - SOBE - SEGURA) / DESCE)


def _nome(t, linhas, x0, bases):
    """Nome animado (embaralha, estica e falha) e a versão parada."""
    rng = random.Random(7)
    letras = []
    for li, (texto, y) in enumerate(zip(linhas, bases)):
        largas = t.letras(texto, x0, y, "largo", TAM_NOME)
        for k, (ch, x, w) in enumerate(t.letras(texto, x0, y, "titulo", TAM_NOME)):
            letras.append({"ch": ch, "x": x, "y": y, "w": w, "linha": li,
                           "ganho": largas[k][2] - w if ch != " " else 0})
    escala = TAM_NOME / estilo("titulo").upm
    n = len(letras)
    assenta = [0.16 + i * 0.075 + rng.random() * 0.14 for i in range(n)]
    fim_intro = max(assenta) + 0.05
    cores = [(P["creme"], P["vermelho"]), (P["vermelho"], P["creme"])]  # cor normal e "com o mouse"

    grupos = {0: [], 1: []}
    for i, L in enumerate(letras):
        ch, x, y, li = L["ch"], L["x"], L["y"], L["linha"]
        # quadros do embaralhamento
        quadros = []
        for k in range(int(assenta[i] / QUADRO)):
            falsa = rng.choice(GLIFOS)
            quadros.append(t.glifo(falsa, x, y, "titulo", TAM_NOME, extra=' visibility="hidden"',
                                   filhos=f'<set attributeName="visibility" to="visible" begin="{k * QUADRO:.3f}s" dur="{QUADRO}s"/>'))
        # letra final: aparece ao assentar e estica na onda
        tempos = ";".join(f"{v:.4f}" for v in _tempos_onda(i))
        d0 = t.contorno(ch, "titulo")
        d1 = t.contorno(ch, "largo")
        normal, mouse = cores[li]
        splines = f"0 0 1 1;{SOFT};0 0 1 1;{SOFT};0 0 1 1"
        onda = (f'begin="{INICIO}s" dur="{CICLO}s" repeatCount="indefinite" keyTimes="{tempos}" '
                f'calcMode="spline" keySplines="{splines}"')
        forma = (f'<path d="{d0}" transform="translate({f(x)} {f(y)}) scale({escala} -{escala})">'
                 f'<animate attributeName="d" values="{d0};{d0};{d1};{d1};{d0};{d0}" {onda}/>'
                 f'<animate attributeName="fill" values="{normal};{normal};{mouse};{mouse};{normal};{normal}" {onda}/>'
                 "</path>")
        # empurrão: as letras antes desta, na mesma linha, ficam mais largas na onda
        anteriores = [j for j in range(i) if letras[j]["linha"] == li]
        empurra = ""
        if anteriores:
            amostras = []
            passos = int(CICLO * 25)
            for s in range(passos + 1):
                instante = s / 25
                dx = sum(letras[j]["ganho"] * _esticado(j, instante) for j in anteriores)
                amostras.append((s / passos, dx))
            # tira os pontos do meio de trechos parados, para o arquivo ficar menor
            enxuto = [amostras[0]]
            for a, b, c in zip(amostras, amostras[1:], amostras[2:]):
                if not (abs(a[1] - b[1]) < 0.05 and abs(b[1] - c[1]) < 0.05):
                    enxuto.append(b)
            enxuto.append(amostras[-1])
            empurra = (f'<animateTransform attributeName="transform" type="translate" begin="{INICIO}s" '
                       f'dur="{CICLO}s" repeatCount="indefinite" '
                       f'keyTimes="{";".join(f"{k:.4f}" for k, _ in enxuto)}" '
                       f'values="{";".join(f"{f(v)} 0" for _, v in enxuto)}"/>')
        final = (f'<g visibility="hidden"><set attributeName="visibility" to="visible" begin="{assenta[i]:.3f}s" fill="freeze"/>'
                 f"<g>{empurra}{forma}</g></g>")
        grupos[li].append("".join(quadros) + final)

    nome = (f'<g id="nome"><g style="fill:var(--a,{P["creme"]})">{"".join(grupos[0])}</g>'
            f'<g style="fill:var(--b,{P["vermelho"]})">{"".join(grupos[1])}</g></g>')

    # efeito de falha: cópia vermelha e cópia apagada deslocadas, só na hora de falhar.
    # Por opacidade, não visibilidade: as letras marcam a própria visibilidade e
    # furariam um "hidden" vindo de cima.
    ini, dur = FALHA

    def janela(opacidade):
        return (f'<set attributeName="opacity" to="{opacidade}" begin="0s" dur="{fim_intro:.3f}s"/>'
                f'<animate attributeName="opacity" begin="{INICIO}s" dur="{CICLO}s" repeatCount="indefinite" '
                f'calcMode="discrete" keyTimes="0;{ini / CICLO:.4f};{(ini + dur) / CICLO:.4f}" '
                f'values="0;{opacidade};0"/>')

    copias = (
        f'<use href="#nome" x="{f(TAM_NOME * 0.06)}" opacity="0" '
        f'style="--a:{P["vermelho"]};--b:{P["vermelho"]}">{janela(0.85)}</use>'
        f'<use href="#nome" x="-{f(TAM_NOME * 0.05)}" opacity="0">{janela(0.45)}</use>'
    )
    # tremor: pequenos saltos enquanto falha
    saltos = [(0, 0)] + [(rng.uniform(-3, 3), rng.uniform(-1, 1)) for _ in range(9)] + [(0, 0)]
    valores = ";".join(f"{f(a)} {f(b)}" for a, b in saltos)
    tempos_intro = ";".join(f"{k / (len(saltos) - 1):.3f}" for k in range(len(saltos)))
    k_ini, k_fim = ini / CICLO, (ini + dur) / CICLO
    passos = [k_ini + (k_fim - k_ini) * k / (len(saltos) - 1) for k in range(len(saltos))]
    tempos_ciclo = ";".join(f"{v:.4f}" for v in [0] + passos + [1])
    tremor = (
        f'<animateTransform attributeName="transform" type="translate" begin="0s" dur="{fim_intro:.3f}s" '
        f'calcMode="discrete" keyTimes="{tempos_intro}" values="{valores}"/>'
        f'<animateTransform attributeName="transform" type="translate" begin="{INICIO}s" dur="{CICLO}s" '
        f'repeatCount="indefinite" calcMode="discrete" keyTimes="{tempos_ciclo}" values="0 0;{valores};0 0"/>'
    )
    animado = f"<g>{tremor}{copias}{nome}</g>"
    parado = (t.texto(linhas[0], x0, bases[0], "titulo", TAM_NOME, P["creme"])
              + t.texto(linhas[1], x0, bases[1], "titulo", TAM_NOME, P["vermelho"]))
    # quanto o sobrenome chega a crescer na onda, para o texto ao lado não ser atropelado
    segunda = [j for j, L in enumerate(letras) if L["linha"] == 1]
    cresce = max(sum(letras[j]["ganho"] * _esticado(j, s / 25) for j in segunda) for s in range(CICLO * 25))
    return movimento(animado, parado), cresce


def _fita(t, palavras, yc, angulo, chave, tam, cor_fundo, cor_texto, altura, espaco, velocidade, sentido, ident):
    """Fita inclinada com o texto rolando sem emenda (laço de duas cópias)."""
    linha = "".join(f"{p}  ■  " for p in palavras)
    unidade = largura(linha, chave, tam, espaco) + tam * 0.4
    vezes = max(1, math.ceil(1500 / unidade))
    periodo = unidade * vezes
    base = altura_cap(chave, tam) / 2
    copia = "".join(t.texto(linha, -720 + k * unidade, base, chave, tam, cor_texto, espaco) for k in range(vezes))
    if sentido < 0:
        de, ate = 0, -periodo
    else:
        de, ate = -periodo, 0
    duracao = periodo / velocidade
    rolando = (f'<g class="fita" style="--d:{f(ate - de)}px;--t:{duracao:.1f}s">'
               f'<g id="{ident}">{copia}</g><use href="#{ident}" x="{f(periodo)}"/></g>')
    return (f'<g transform="translate({LARGURA / 2} {yc}) rotate({angulo}) scale(1.1 1)">'
            f'<rect x="-720" y="{-altura / 2}" width="1440" height="{altura}" fill="{cor_fundo}"/>'
            f'<g transform="translate({f(de)} 0)">{rolando}</g></g>')


def desenhar(perfil):
    t = Tinta()
    topo = perfil["topo"]
    linhas = [p.upper() for p in perfil["nome"].split()]
    x0 = MARGEM
    base1 = round(TOPO_NOME + altura_cap("titulo", TAM_NOME))
    base2 = round(base1 + TAM_NOME * ENTRELINHA_NOME)
    nome, cresce = _nome(t, linhas, x0, [base1, base2])

    # texto de abertura à direita do sobrenome, alinhado pela base dele
    larg_sobrenome = largura(linhas[1], "titulo", TAM_NOME)
    x_texto = round(x0 + larg_sobrenome + cresce + 48)
    larg_texto = LARGURA - MARGEM - x_texto
    teto = base1 + 24 + altura_cap("texto", 21)  # primeira linha logo abaixo do nome
    piso = base2 + 14                            # última linha perto da base do sobrenome
    for tam_lead, tam_foco in ((21, 17), (20, 16.5), (19, 16)):
        lead = quebrar(topo["lead"], "texto", tam_lead, larg_texto)
        foco = quebrar(topo["foco"], "texto", tam_foco, larg_texto)
        passo_lead, passo_foco = tam_lead * 1.45, tam_foco * 1.5
        y_foco = piso - (len(foco) - 1) * passo_foco
        y_lead = y_foco - tam_foco * 2.1 - (len(lead) - 1) * passo_lead
        if y_lead >= teto:
            break
    else:
        raise ValueError("o texto de abertura não cabe embaixo do nome; encurte o lead ou o foco")
    abertura = (
        "".join(t.texto(l, x_texto, y_lead + i * passo_lead, "texto", tam_lead, P["creme"]) for i, l in enumerate(lead))
        + "".join(t.texto(l, x_texto, y_foco + i * passo_foco, "texto", tam_foco, P["creme500"])
                  for i, l in enumerate(foco))
    )

    rotulos = (
        t.texto(topo["rotulo"].upper(), x0, 66, "mono", 16, P["creme300"], 0.18)
        + t.texto(f'{topo["local"]}  /  {topo["coordenadas"]}'.upper(), LARGURA - MARGEM, 66, "mono", 16,
                  P["creme500"], 0.18, ancora="end")
    )
    palavras = [p.upper() for p in perfil["fita"]]
    yc = ALTURA - 72
    fitas = (
        _fita(t, palavras, yc - 12, 1.6, "mono", 17, P["creme"], P["fundo"], 36, 0.18, 80, 1, "fc")
        # sombra embaixo da fita vermelha, sem filtro (filtro pesa em imagem animada)
        + f'<g transform="translate({LARGURA / 2} {yc}) rotate(-2.2) scale(1.1 1)">'
          f'<rect x="-720" y="30" width="1440" height="34" fill="url(#sombra)"/></g>'
        + _fita(t, palavras, yc, -2.2, "titulo75", 50, P["vermelho"], P["fundo"], 76, 0, 170, -1, "fv")
    )
    defs = (
        t.defs()
        + '<linearGradient id="sombra" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#000" stop-opacity="0.55"/><stop offset="1" stop-color="#000" stop-opacity="0"/>'
          "</linearGradient>"
    )
    corpo = (
        f'<rect width="{LARGURA}" height="{ALTURA}" fill="{P["fundo"]}"/>'
        + marcas(28, 28, LARGURA - 28, ALTURA - 140)
        + f'<g class="sobe" style="animation-delay:.3s">{rotulos}</g>'
        + nome
        + f'<g class="sobe" style="animation-delay:.45s">{abertura}</g>'
        + fitas
    )
    texto_alt = f'{perfil["nome"]}. {topo["rotulo"]}. {topo["lead"]}'
    return svg(LARGURA, ALTURA, perfil["nome"], texto_alt, corpo, defs, CSS)
