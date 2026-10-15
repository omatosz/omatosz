"""Botões de contato em SVG (cada um vira um link no README)."""
from base import FONTE_MONO, P, esc, f

BOTOES = [
    ("btn-linkedin", "LINKEDIN"),
    ("btn-email", "E-MAIL"),
    ("btn-portfolio", "PORTFÓLIO"),
    ("btn-landing", "LANDING DO VERYON"),
]


def _botao(rotulo):
    largura = len(rotulo) * 9.9 + 56
    altura = 46
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(largura)} {altura}" width="{f(largura)}" height="{altura}" role="img">'
        f"<title>{esc(rotulo)}</title>"
        f'<defs><clipPath id="p"><rect width="{f(largura)}" height="{altura}" rx="23"/></clipPath>'
        f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{P["fundo2"]}"/><stop offset="1" stop-color="{P["painel2"]}"/></linearGradient></defs>'
        f'<rect width="{f(largura)}" height="{altura}" rx="23" fill="url(#g)"/>'
        f'<g clip-path="url(#p)"><rect x="-70" y="-10" width="36" height="70" fill="#ffffff" opacity="0.10" transform="skewX(-20)">'
        f'<animateTransform attributeName="transform" type="translate" from="-80 0" to="{f(largura + 120)} 0" dur="4.5s" repeatCount="indefinite"/></rect></g>'
        f'<rect x="0.75" y="0.75" width="{f(largura - 1.5)}" height="{altura - 1.5}" rx="22.25" fill="none" stroke="{P["ciano"]}" stroke-opacity="0.65" stroke-width="1.5"/>'
        f'<text x="{f(largura / 2)}" y="28.5" text-anchor="middle" font-family=\'{FONTE_MONO}\' font-size="14" font-weight="700" '
        f'letter-spacing="1.5" fill="{P["ciano_claro"]}">{esc(rotulo)}</text></svg>\n'
    )


def desenhar_todos():
    return {nome: _botao(rotulo) for nome, rotulo in BOTOES}
