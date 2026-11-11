"""Paleta, medidas e utilitários de SVG usados por todas as peças.

O visual é o do portfólio (portfolio-leandro-react.vercel.app): preto, vermelho
e cream, cantos retos, bordas finas e rótulos em mono entre colchetes. Os
cartões têm fundo próprio, então funcionam nos temas claro e escuro do GitHub.
"""
import html

# Os mesmos tons do tema do portfólio (src/index.css).
P = {
    "fundo": "#070606",      # ink-950
    "painel": "#0e0c0c",     # ink-900
    "painel2": "#171414",    # ink-800
    "linha": "#262120",      # ink-700
    "linha2": "#3b3432",     # ink-600
    "vermelho_claro": "#ff4b3e",  # red-400
    "vermelho": "#e8251c",   # red-500
    "vermelho600": "#c21a12",
    "vermelho700": "#8a120c",
    "vermelho900": "#3a0905",
    "creme": "#f4ecdc",      # cream-50
    "creme100": "#e9e0cd",
    "creme300": "#c8bfae",
    "creme500": "#8e877b",
}

LARGURA = 1200
MARGEM = 56

# Curvas de movimento do portfólio: "soft" para entradas, "snap" para as tarjas.
SOFT = "0.22 1 0.36 1"
SNAP = "0.7 0 0.2 1"

# Quem pede menos movimento no sistema vê a versão parada (.pr) no lugar da
# animada (.mv). Vale para as animações em CSS e para as em SMIL.
CSS_BASE = (
    ".pr{display:none}"
    "@media (prefers-reduced-motion:reduce){.mv{display:none}.pr{display:inline}"
    "*{animation:none!important}}"
)


def esc(texto):
    """Escapa o texto para ir dentro de um SVG (&, <, > e aspas)."""
    return html.escape(str(texto), quote=True)


def milhar(n):
    """17824 vira '17.824' (padrão brasileiro)."""
    return f"{int(n):,}".replace(",", ".")


def f(n):
    """Número curto para atributo de SVG (sem zeros sobrando)."""
    texto = f"{float(n):.2f}".rstrip("0").rstrip(".")
    return "0" if texto in ("-0", "") else texto


def svg(largura, altura, titulo, descricao, corpo, defs="", css=""):
    """Monta o documento SVG completo. O título e a descrição ajudam leitores de tela."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {f(altura)}" '
        f'width="{largura}" height="{f(altura)}" role="img">'
        f"<title>{esc(titulo)}</title><desc>{esc(descricao)}</desc>"
        f"<defs><style>{CSS_BASE}{css}</style>{defs}</defs>{corpo}</svg>\n"
    )


def movimento(animado, parado):
    """A versão animada e a parada lado a lado; o CSS mostra uma das duas."""
    return f'<g class="mv">{animado}</g><g class="pr">{parado}</g>'


def cartao(largura, altura, fundo=None, borda=None):
    """Fundo do cartão com borda fina e cantos retos, como os do portfólio."""
    fundo = fundo or P["painel"]
    borda = borda or P["linha"]
    return (f'<rect width="{largura}" height="{f(altura)}" fill="{fundo}"/>'
            f'<rect x="0.5" y="0.5" width="{largura - 1}" height="{f(altura - 1)}" fill="none" stroke="{borda}"/>')


def marcas(x0, y0, x1, y1, tam=14, cor=None, opacidade=0.25):
    """Marcas de registro nos quatro cantos, como num visor."""
    cor = cor or P["creme"]
    d = (f"M{x0} {y0 + tam}V{y0}H{x0 + tam}"
         f"M{x1 - tam} {y0}H{x1}V{y0 + tam}"
         f"M{x0} {y1 - tam}V{y1}H{x0 + tam}"
         f"M{x1 - tam} {y1}H{x1}V{y1 - tam}")
    return f'<path d="{d}" fill="none" stroke="{cor}" stroke-opacity="{opacidade}"/>'


def ciclo(duracao, corpo, entrada=0.02, saida=0.94):
    """O grupo aparece, fica e some em fade a cada ciclo, para recomeçar a contagem.

    Imagem não sabe quando entrou na tela; o ciclo garante que quem rola a página
    depois do carregamento ainda veja os números contando.
    """
    return (
        '<g opacity="0">'
        f'<animate attributeName="opacity" dur="{f(duracao)}s" repeatCount="indefinite" '
        f'keyTimes="0;{entrada};{saida};{saida + 0.045:.3f};1" values="0;1;1;0;0"/>'
        f"{corpo}</g>"
    )


def bezier(x1, y1, x2, y2):
    """Curva cubic-bezier do CSS como função de 0..1 para 0..1."""
    def eixo(t, a, b):
        return 3 * a * t * (1 - t) ** 2 + 3 * b * t * t * (1 - t) + t ** 3

    def curva(x):
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        baixo, alto = 0.0, 1.0
        for _ in range(40):
            meio = (baixo + alto) / 2
            if eixo(meio, x1, x2) < x:
                baixo = meio
            else:
                alto = meio
        return eixo((baixo + alto) / 2, y1, y2)

    return curva


suave = bezier(0.22, 1, 0.36, 1)
