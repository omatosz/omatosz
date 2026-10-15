"""Paleta, fontes e pequenos utilitários de SVG usados por todas as peças."""
import html

# Cores. Os cartões têm fundo próprio (escuro), então funcionam nos temas
# claro e escuro do GitHub.
P = {
    "fundo": "#060b14",
    "fundo2": "#0b1a2f",
    "painel": "#0e1a2e",
    "painel2": "#12233d",
    "linha": "#1c3050",
    "texto": "#e6f0ff",
    "mudo": "#8aa0c0",
    "fraco": "#5b7191",
    "ciano": "#22d3ee",
    "ciano_claro": "#67e8f9",
    "azul": "#3b82f6",
    "verde": "#34d399",
    "ambar": "#fbbf24",
    "vermelho": "#fb7185",
    "violeta": "#a78bfa",
}

# Imagem SVG no GitHub não carrega fonte externa, então usamos as do sistema.
FONTE_MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono","DejaVu Sans Mono",monospace'
FONTE_SANS = 'system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif'

CSS_BASE = (
    f".m{{font-family:{FONTE_MONO}}}"
    f".s{{font-family:{FONTE_SANS}}}"
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


def svg(largura, altura, titulo, descricao, corpo, defs="", css=CSS_BASE):
    """Monta o documento SVG completo. O título e a descrição ajudam leitores de tela."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" '
        f'width="{largura}" height="{altura}" role="img">'
        f"<title>{esc(titulo)}</title><desc>{esc(descricao)}</desc>"
        f"<defs><style>{css}</style>{defs}</defs>{corpo}</svg>\n"
    )


def ciclo(duracao, corpo):
    """Faz o grupo aparecer, ficar visível e sumir em fade a cada ciclo.

    As animações de contagem recomeçam no fim de cada ciclo; o fade esconde o
    "pulo" de volta ao zero. Assim quem rola a página depois do carregamento
    ainda vê os números rodando.
    """
    return (
        '<g opacity="0">'
        f'<animate attributeName="opacity" dur="{f(duracao)}s" repeatCount="indefinite" '
        'keyTimes="0;0.02;0.94;0.985;1" values="0;1;1;0;0"/>'
        f"{corpo}</g>"
    )


def painel(largura, altura, raio=22, id_="rc"):
    """Retorna (defs, fundo): clip arredondado e o retângulo de fundo com gradiente."""
    defs = (
        f'<clipPath id="{id_}"><rect width="{largura}" height="{altura}" rx="{raio}"/></clipPath>'
        '<linearGradient id="fundo" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{P["fundo"]}"/><stop offset="1" stop-color="{P["fundo2"]}"/>'
        "</linearGradient>"
        '<pattern id="grade" width="40" height="40" patternUnits="userSpaceOnUse">'
        f'<path d="M40 0H0V40" fill="none" stroke="{P["linha"]}" stroke-width="1" opacity="0.55"/>'
        "</pattern>"
    )
    fundo = (
        f'<rect width="{largura}" height="{altura}" rx="{raio}" fill="url(#fundo)"/>'
        f'<rect width="{largura}" height="{altura}" rx="{raio}" fill="url(#grade)" opacity="0.5"/>'
        f'<rect x="0.5" y="0.5" width="{largura - 1}" height="{altura - 1}" rx="{raio}" '
        f'fill="none" stroke="{P["linha"]}"/>'
    )
    return defs, fundo
