"""Texto em SVG desenhado com as fontes do portfólio.

Imagem SVG no GitHub não carrega fonte de fora, então cada letra vem pronta de
scripts/fontes/letras.json (o contorno e a largura de cada caractere). O texto
vira uma fila de <use> apontando para o contorno de cada letra, que aparece uma
vez só no <defs> do arquivo.

Os estilos seguem o CSS do portfólio:
    titulo    Anybody preta condensada (62% de largura), os títulos
    titulo70  a mesma, a 70%, nos números grandes
    titulo75  a mesma, a 75%, na fita e nos nomes das etapas
    largo     a mesma, a 100%, o ponto até onde a letra estica
    mono      IBM Plex Mono, os rótulos em caixa alta
    texto     Archivo normal, os parágrafos
    forte     Archivo seminegrito, os botões
    forte90   Archivo seminegrito a 90%, as linhas de destaque
"""
import json
import os
import sys

from base import f

_ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fontes", "letras.json")
_ESTILOS = {}
_AVISADOS = set()


class Estilo:
    def __init__(self, chave, dados):
        self.chave = chave
        self.upm = dados["upm"]
        self.cap = dados["cap"]
        self.caixa_alta = dados["caixa_alta"]
        self.glifos = dict(dados["glifos"])
        self.kern = dados["kern"]
        # "■" não existe nas fontes; no portfólio ele vem de uma fonte do sistema.
        # Aqui é um quadrado centrado na altura das maiúsculas.
        lado = round(self.cap * 0.6)
        base = round((self.cap - lado) / 2)
        self.glifos["■"] = [round(lado * 1.25), f"M{round(lado * 0.125)} {base}h{lado}v{lado}h-{lado}Z"]

    def prepara(self, texto):
        texto = str(texto)
        if self.caixa_alta:
            texto = texto.upper()
        limpo = []
        for ch in texto:
            if ch in self.glifos:
                limpo.append(ch)
            elif ch == " ":
                limpo.append(" ")
            else:
                if (self.chave, ch) not in _AVISADOS:
                    _AVISADOS.add((self.chave, ch))
                    print(f"aviso: o estilo {self.chave} não tem {ch!r}; trocado por espaço", file=sys.stderr)
                limpo.append(" ")
        return "".join(limpo)

    def avancos(self, texto, espaco=0.0):
        """Posição (em unidades da fonte) de cada letra e a largura total, sem o espaço final."""
        texto = self.prepara(texto)
        extra = espaco * self.upm
        pos, x = [], 0.0
        for i, ch in enumerate(texto):
            pos.append(x)
            x += self.glifos[ch][0]
            if i + 1 < len(texto):
                x += self.kern.get(ch + texto[i + 1], 0) + extra
        return texto, pos, x

    def largura(self, texto, tam, espaco=0.0):
        return self.avancos(texto, espaco)[2] * tam / self.upm


def estilo(chave):
    if not _ESTILOS:
        with open(_ARQUIVO, encoding="utf-8") as arq:
            for nome, dados in json.load(arq)["estilos"].items():
                _ESTILOS[nome] = Estilo(nome, dados)
    return _ESTILOS[chave]


def largura(texto, chave, tam, espaco=0.0):
    return estilo(chave).largura(texto, tam, espaco)


def altura_cap(chave, tam):
    """Altura das maiúsculas, em px, para alinhar texto pelo topo."""
    e = estilo(chave)
    return e.cap * tam / e.upm


def quebrar(texto, chave, tam, largura_max, espaco=0.0):
    """Quebra o texto em linhas que cabem em `largura_max` (por palavra)."""
    linhas, atual = [], ""
    for palavra in str(texto).split():
        tentativa = f"{atual} {palavra}" if atual else palavra
        if atual and largura(tentativa, chave, tam, espaco) > largura_max:
            linhas.append(atual)
            atual = palavra
        else:
            atual = tentativa
    if atual:
        linhas.append(atual)
    return linhas


class Tinta:
    """Junta as letras usadas num SVG; `defs()` escreve cada contorno uma vez."""

    def __init__(self):
        self.usadas = {}

    def _id(self, chave, ch):
        ident = f"{chave}-{ord(ch):x}"
        if ident not in self.usadas:
            self.usadas[ident] = estilo(chave).glifos[ch][1]
        return ident

    def defs(self):
        return "".join(f'<path id="{i}" d="{d}"/>' for i, d in self.usadas.items() if d)

    def texto(self, texto, x, y, chave, tam, cor, espaco=0.0, ancora="start", extra=""):
        """Uma linha de texto com a linha de base em `y`. `espaco` é o letter-spacing em em."""
        e = estilo(chave)
        texto, pos, total = e.avancos(texto, espaco)
        escala = tam / e.upm
        if ancora == "middle":
            x -= total * escala / 2
        elif ancora == "end":
            x -= total * escala
        usos = "".join(
            f'<use href="#{self._id(chave, ch)}" x="{round(p)}"/>' if p else f'<use href="#{self._id(chave, ch)}"/>'
            for ch, p in zip(texto, pos)
            if ch != " "
        )
        if not usos:
            return ""
        # cor em variável CSS (para as cópias do efeito de falha trocarem a cor) vai no style
        pintura = f' style="fill:{cor}"' if cor.startswith("var(") else (f' fill="{cor}"' if cor else "")
        return (f'<g transform="translate({f(x)} {f(y)}) scale({escala:.5f} -{escala:.5f})"'
                f'{pintura}{extra}>{usos}</g>')

    def letras(self, texto, x, y, chave, tam, espaco=0.0):
        """Cada letra com a sua posição em px: [(caractere, x, largura), ...]."""
        e = estilo(chave)
        texto, pos, _ = e.avancos(texto, espaco)
        escala = tam / e.upm
        return [(ch, x + p * escala, e.glifos[ch][0] * escala) for ch, p in zip(texto, pos)]

    def glifo(self, ch, x, y, chave, tam, cor=None, extra="", filhos=""):
        """Uma letra solta, para as animações letra por letra."""
        e = estilo(chave)
        ch = e.prepara(ch)
        if ch == " ":
            return ""
        escala = tam / e.upm
        pintura = f' fill="{cor}"' if cor else ""
        return (f'<use href="#{self._id(chave, ch)}" transform="translate({f(x)} {f(y)}) '
                f'scale({escala:.5f} -{escala:.5f})"{pintura}{extra}>{filhos}</use>')

    def contorno(self, ch, chave):
        """O `d` da letra em unidades da fonte (para animar a forma)."""
        e = estilo(chave)
        return e.glifos[e.prepara(ch)][1]

    def paragrafo(self, texto, x, y, chave, tam, cor, largura_max, entrelinha=1.5, espaco=0.0):
        """Texto quebrado em linhas. `y` é a linha de base da primeira. Retorna (svg, altura)."""
        linhas = quebrar(texto, chave, tam, largura_max, espaco)
        passo = tam * entrelinha
        corpo = "".join(self.texto(linha, x, y + i * passo, chave, tam, cor, espaco) for i, linha in enumerate(linhas))
        return corpo, passo * len(linhas)
