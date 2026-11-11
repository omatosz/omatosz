"""Cartão do Veryon, no desenho do projeto em destaque do portfólio: faixa
vermelha no topo, o nome gigante com o quadrado pulsando, os números contando e
o caminho de um ataque, que avança sozinho de etapa em etapa como no site.
"""
import datetime
import random

from animacao import conta, embaralha, janela, tremor
from base import MARGEM, LARGURA, P, SOFT, cartao, ciclo, f, milhar, movimento, svg
from texto import Tinta, altura_cap, largura, quebrar

CICLO_NUMEROS = 20
CICLO_NOME = 16
ETAPA = 3.2  # segundos por etapa, como no site
TAM_NOME = 150

CSS = (
    "@keyframes ping{0%{transform:scale(1);opacity:.6}80%,100%{transform:scale(1.85);opacity:0}}"
    ".ping{transform-box:fill-box;transform-origin:center;animation:ping 2.2s cubic-bezier(0,0,.2,1) infinite}"
)


def _numeros(t, itens, x0, y0, larg):
    """Grade 2 x 3 com bordas finas; número vermelho contando e o rótulo embaixo."""
    cw, ch = larg / 2, 128
    linhas = "".join(f"M{f(x0)} {f(y0 + k * ch + 0.5)}H{f(x0 + larg)}" for k in range(4))
    linhas += "".join(f"M{f(x0 + k * cw + 0.5)} {f(y0)}V{f(y0 + 3 * ch)}" for k in range(3))
    grade = f'<path d="{linhas}" stroke="{P["linha"]}"/>'
    animados, parados, rotulos = [], [], []
    for i, (valor, rotulo) in enumerate(itens):
        cx, cy = x0 + (i % 2) * cw + 20, y0 + (i // 2) * ch
        animados.append(conta(t, valor, cx, cy + 66, "titulo70", 58, P["vermelho"], CICLO_NUMEROS))
        parados.append(t.texto(milhar(valor), cx, cy + 66, "titulo70", 58, P["vermelho"]))
        for k, linha in enumerate(quebrar(rotulo.upper(), "mono", 13, cw - 40, 0.18)[:2]):
            rotulos.append(t.texto(linha, cx, cy + 95 + k * 19, "mono", 13, P["creme500"], 0.18))
    return grade + movimento(ciclo(CICLO_NUMEROS, "".join(animados)), "".join(parados)) + "".join(rotulos)


def _caminho(t, v, y0, rng):
    """As 10 etapas: barra segmentada com a etapa ativa andando e o detalhe embaixo."""
    etapas = v["etapas"]
    n = len(etapas)
    total = n * ETAPA
    larg = LARGURA - 2 * MARGEM
    vao = 6
    sw = (larg - vao * (n - 1)) / n
    passo = sw + vao
    y_num, y_barra, y_curto = y0 + 96, y0 + 108, y0 + 142
    cabeca = (f'<path d="M{MARGEM} {y0 + 0.5}H{LARGURA - MARGEM}" stroke="{P["linha"]}"/>'
              + t.texto(v["caminho"].upper(), MARGEM, y0 + 52, "mono", 15, P["vermelho"], 0.18)
              + t.texto(v["dica"].upper(), LARGURA - MARGEM, y0 + 52, "mono", 13, P["creme500"], 0.18, "end"))
    base, passadas, ativos_txt, inativos_txt = [], [], [], []
    for i, e in enumerate(etapas):
        x = MARGEM + i * passo
        base.append(f'<rect x="{f(x)}" y="{y_barra}" width="{f(sw)}" height="10" fill="{P["linha"]}"/>')
        if i < n - 1:
            passadas.append(f'<rect x="{f(x)}" y="{y_barra}" width="{f(sw)}" height="10" fill="{P["vermelho700"]}" '
                            f'visibility="hidden">{janela(total, (i + 1) * ETAPA)}</rect>')
        numero, curto = f"{i + 1:02d}", e["curto"].upper()
        inativos_txt.append(t.texto(numero, x, y_num, "mono", 13, P["creme500"], 0.18)
                            + t.texto(curto, x, y_curto, "mono", 13, P["creme500"], 0.18))
        ativos_txt.append(f'<g visibility="hidden">{janela(total, i * ETAPA, (i + 1) * ETAPA)}'
                          + t.texto(numero, x, y_num, "mono", 13, P["creme"], 0.18)
                          + t.texto(curto, x, y_curto, "mono", 13, P["creme"], 0.18) + "</g>")
    # bloco vermelho da etapa ativa: desliza de um segmento para o outro
    pontos = [(0, 0.0)]
    for i in range(1, n):
        pontos += [(i * ETAPA, (i - 1) * passo), (i * ETAPA + 0.4, i * passo)]
    pontos += [(total - 0.45, (n - 1) * passo), (total, 0.0)]
    splines = ";".join("0 0 1 1" if a[1] == b[1] else SOFT for a, b in zip(pontos, pontos[1:]))
    bloco = (f'<rect x="{MARGEM}" y="{y_barra}" width="{f(sw)}" height="10" fill="{P["vermelho"]}">'
             f'<animateTransform attributeName="transform" type="translate" dur="{f(total)}s" repeatCount="indefinite" '
             f'calcMode="spline" keyTimes="{";".join(f"{a / total:.5f}" for a, _ in pontos)}" '
             f'values="{";".join(f"{f(b)} 0" for _, b in pontos)}" keySplines="{splines}"/></rect>')

    # detalhe da etapa: número grande, nome que embaralha ao trocar, fato e texto
    y_det = y0 + 182
    x_det = MARGEM + 200
    larg_texto = LARGURA - MARGEM - x_det
    detalhes, fundo = [], y_det
    parado_detalhe = ""
    for i, e in enumerate(etapas):
        ini, fim = i * ETAPA, (i + 1) * ETAPA
        y_numero = y_det + 44 + altura_cap("titulo70", 108)
        bloco_txt = (t.texto(f"{i + 1:02d}", MARGEM, y_numero, "titulo70", 108, P["vermelho"])
                     + t.texto(e["fato"].upper(), x_det, y_det + 110, "mono", 14, P["creme300"], 0.18))
        corpo, alt = t.paragrafo(e["texto"], x_det, y_det + 150, "texto", 18, P["creme300"], larg_texto, 1.6)
        fundo = max(fundo, y_det + 150 + alt - 18 * 1.6)
        nome = embaralha(t, e["nome"].upper(), x_det, y_det + 76, "titulo75", 44, P["creme"], total, ini, fim, rng,
                         duracao=0.36)
        detalhes.append(f'<g>{tremor(total, ini, 0.22, rng, 2.5)}'
                        f'<g visibility="hidden">{janela(total, ini, fim)}{bloco_txt}{corpo}</g>{nome}</g>')
        if i == 0:
            parado_detalhe = bloco_txt + corpo + t.texto(e["nome"].upper(), x_det, y_det + 76, "titulo75", 44, P["creme"])
    separador = f'<path d="M{MARGEM} {y_det + 0.5}H{LARGURA - MARGEM}" stroke="{P["linha"]}"/>'
    animado = "".join(passadas) + bloco + "".join(ativos_txt) + "".join(detalhes)
    parado = (f'<rect x="{MARGEM}" y="{y_barra}" width="{f(sw)}" height="10" fill="{P["vermelho"]}"/>'
              + t.texto("01", MARGEM, y_num, "mono", 13, P["creme"], 0.18)
              + t.texto(etapas[0]["curto"].upper(), MARGEM, y_curto, "mono", 13, P["creme"], 0.18)
              + parado_detalhe)
    return cabeca + "".join(base) + "".join(inativos_txt) + separador + movimento(animado, parado), fundo


def desenhar(perfil, dados):
    v = perfil["veryon"]
    t = Tinta()
    rng = random.Random(11)
    x0 = MARGEM
    col_esq = 600
    x_dir = 704
    larg_dir = LARGURA - MARGEM - x_dir

    # selo, período e data em que os números foram conferidos
    y_selo = 64
    selo_txt = v["rotulo"].upper()
    w_selo = largura(selo_txt, "mono", 14, 0.18) + 24
    verificado = datetime.date.fromisoformat(v["verificado_em"]).strftime("%d/%m/%Y")
    selo = (f'<rect x="{x0}" y="{y_selo}" width="{f(w_selo)}" height="30" fill="{P["vermelho"]}"/>'
            + t.texto(selo_txt, x0 + 12, y_selo + 20, "mono", 14, P["fundo"], 0.18)
            + t.texto(v["periodo"].upper(), x0 + w_selo + 16, y_selo + 20, "mono", 14, P["creme500"], 0.18)
            + t.texto(f"NÚMEROS CONFERIDOS EM {verificado}", LARGURA - MARGEM, y_selo + 20, "mono", 13,
                      P["creme500"], 0.18, "end"))

    # nome gigante (embaralha de novo a cada ciclo) e o quadrado pulsando
    nome_txt = v["nome"].upper()
    cap = altura_cap("titulo", TAM_NOME)
    y_nome = round(y_selo + 30 + 46 + cap)
    w_nome = largura(nome_txt, "titulo", TAM_NOME)
    nome = movimento(
        embaralha(t, nome_txt, x0, y_nome, "titulo", TAM_NOME, P["creme"], CICLO_NOME, 0, None, rng, duracao=0.5),
        t.texto(nome_txt, x0, y_nome, "titulo", TAM_NOME, P["creme"]),
    )
    lado = TAM_NOME * 0.16
    qx, qy = x0 + w_nome + 14, y_nome - cap + 6
    quadrado = (f'<rect class="ping" x="{f(qx)}" y="{f(qy)}" width="{f(lado)}" height="{f(lado)}" fill="{P["vermelho"]}"/>'
                f'<rect x="{f(qx)}" y="{f(qy)}" width="{f(lado)}" height="{f(lado)}" fill="{P["vermelho"]}"/>')

    # linha de destaque e descrição
    y_linha = y_nome + 66
    linhas = quebrar(v["linha"], "forte90", 30, col_esq)
    destaque = "".join(t.texto(l, x0, y_linha + i * 38, "forte90", 30, P["creme"]) for i, l in enumerate(linhas))
    y_desc = y_linha + (len(linhas) - 1) * 38 + 52
    descricao, alt_desc = t.paragrafo(v["descricao"], x0, y_desc, "texto", 19, P["creme300"], col_esq, 1.6)
    fundo_esq = y_desc + alt_desc - 19 * 1.6

    # números: o de linhas de código vem da contagem feita na Action
    itens = [(dados["linhas_total"] if n["chave"] == "linhas" else n["valor"], n["rotulo"]) for n in v["numeros"]]
    alt_grade = 3 * 128
    y_grade = max(y_nome - cap, fundo_esq + 12 - alt_grade)
    numeros = _numeros(t, itens, x_dir, y_grade, larg_dir)

    y_caminho = max(fundo_esq, y_grade + alt_grade) + 60
    caminho, fundo_caminho = _caminho(t, v, y_caminho, rng)
    y_stack = fundo_caminho + 62
    stack = t.texto("  /  ".join(v["stack"]).upper(), x0, y_stack, "mono", 14, P["creme500"], 0.18)
    altura = round(y_stack + 50)

    corpo = (
        cartao(LARGURA, altura)
        + f'<rect width="{LARGURA}" height="8" fill="{P["vermelho"]}"/>'
        + selo + nome + quadrado + destaque + descricao + numeros + caminho + stack
    )
    numeros_alt = ", ".join(f"{milhar(valor)} {rotulo}" for valor, rotulo in itens)
    alt = f'{v["nome"]}: {v["linha"]}. {v["descricao"]} {numeros_alt}.'
    return svg(LARGURA, altura, f'{v["nome"]}, projeto em destaque', alt, corpo, t.defs(), CSS)
