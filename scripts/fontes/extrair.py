#!/usr/bin/env python3
"""Extrai o desenho das letras das fontes do portfólio para scripts/fontes/letras.json.

Imagem SVG no GitHub não carrega fonte externa. Para o perfil usar as mesmas
fontes do portfólio (Anybody, Archivo e IBM Plex Mono), cada letra vira um
contorno guardado em letras.json, e o gerador monta o texto com esses
contornos. Assim o resultado é igual em qualquer navegador e sistema.

Este script só roda quando for preciso trocar de fonte ou incluir caracteres.
A Action do perfil não usa ele, só o letras.json que ele grava. Diferente do
resto do gerador, precisa de bibliotecas de fora:

    pip install fonttools brotli uharfbuzz
    python scripts/fontes/extrair.py --fontes <pasta node_modules do portfólio>

As fontes são da licença SIL Open Font License 1.1 (textos em fontes/licencas).
"""
import argparse
import io
import json
import os
import re

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

AQUI = os.path.dirname(os.path.abspath(__file__))

ARQUIVOS = {
    "Anybody": r"@fontsource-variable/anybody/files/anybody-latin-standard-normal.woff2",
    "Archivo": r"@fontsource-variable/archivo/files/archivo-latin-standard-normal.woff2",
    "IBM Plex Mono": r"@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2",
}

MAIUSCULAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ"
MINUSCULAS = "abcdefghijklmnopqrstuvwxyzàáâãäçèéêëìíîïñòóôõöùúûüýÿ"
DIGITOS = "0123456789"
# – e — são os traços médio e longo, para o caso de algum texto trazer um
SINAIS = " .,:;!?-/()[]{}&%#@+*=<>_'\"$|\\~^`–—‘’“”•…·°ºª«»©"
TUDO = MAIUSCULAS + MINUSCULAS + DIGITOS + SINAIS

# Cada estilo é uma fonte num ponto dos eixos variáveis, como no CSS do portfólio.
# "caixa_alta" diz que o texto desse estilo sempre sai em maiúsculas.
ESTILOS = {
    "titulo": ("Anybody", {"wdth": 62, "wght": 900}, MAIUSCULAS + DIGITOS + SINAIS, True),
    "titulo70": ("Anybody", {"wdth": 70, "wght": 900}, DIGITOS + " .,:%+-/" + MAIUSCULAS[:26], True),
    "titulo75": ("Anybody", {"wdth": 75, "wght": 900}, MAIUSCULAS + DIGITOS + SINAIS, True),
    "largo": ("Anybody", {"wdth": 100, "wght": 900}, MAIUSCULAS[:26], True),
    "mono": ("IBM Plex Mono", {}, TUDO + "↑↓", False),
    "texto": ("Archivo", {"wdth": 100, "wght": 400}, TUDO, False),
    "forte": ("Archivo", {"wdth": 100, "wght": 600}, MAIUSCULAS + DIGITOS + SINAIS, True),
    "forte90": ("Archivo", {"wdth": 90, "wght": 600}, TUDO, False),
}


def _numero(v):
    return str(round(v))


def _relativo(d):
    """Reescreve o contorno com comandos relativos: números menores, arquivo menor."""
    pedacos = re.findall(r"[MLQCZHV]|-?\d+", d)
    saida, x, y, ix, iy = [], 0, 0, 0, 0
    anterior, i, cmd = None, 0, None
    tamanho = {"M": 2, "L": 2, "Q": 4, "C": 6, "H": 1, "V": 1}
    while i < len(pedacos):
        if pedacos[i].isalpha():
            cmd = pedacos[i]
            i += 1
            if cmd == "Z":
                saida.append("z")
                x, y, anterior = ix, iy, "z"
                continue
        nums = [int(n) for n in pedacos[i:i + tamanho[cmd]]]
        i += tamanho[cmd]
        if cmd == "H":
            rel, x = [nums[0] - x], nums[0]
        elif cmd == "V":
            rel, y = [nums[0] - y], nums[0]
        else:
            rel = []
            for k in range(0, len(nums), 2):
                rel += [nums[k] - x, nums[k + 1] - y]
            x, y = nums[-2], nums[-1]
        letra = cmd.lower()
        if cmd == "M":
            ix, iy = x, y
            cmd = "L"  # números soltos depois de um M são linhas (regra do SVG)
        texto = ""
        for n in rel:
            texto += str(n) if (n < 0 or not texto) else f" {n}"
        if letra == anterior and letra != "m":
            saida.append(texto if texto.startswith("-") else " " + texto)
        else:
            saida.append(letra + texto)
        anterior = letra
    return "".join(saida)


class _Fonte:
    def __init__(self, caminho):
        self.tt = TTFont(caminho)
        self.tt.flavor = None
        bruto = io.BytesIO()
        self.tt.save(bruto)
        self.tt = TTFont(io.BytesIO(bruto.getvalue()))
        self.hb_face = hb.Face(bruto.getvalue())
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm


def _hb_fonte(fonte, eixos):
    f = hb.Font(fonte.hb_face)
    if eixos:
        f.set_variations(eixos)
    return f


def _molda(hbf, texto):
    buf = hb.Buffer()
    buf.add_str(texto)
    buf.guess_segment_properties()
    hb.shape(hbf, buf, {"liga": False, "clig": False, "dlig": False, "calt": False})
    return buf.glyph_infos, buf.glyph_positions


def extrair(pasta_fontes):
    fontes = {nome: _Fonte(os.path.join(pasta_fontes, rel)) for nome, rel in ARQUIVOS.items()}
    saida = {}
    for estilo, (nome, eixos, caracteres, caixa_alta) in ESTILOS.items():
        fonte = fontes[nome]
        glyph_set = fonte.tt.getGlyphSet(location=eixos or None)
        hbf = _hb_fonte(fonte, eixos)
        glifos, avancos = {}, {}
        for ch in dict.fromkeys(caracteres):
            if ord(ch) not in fonte.cmap:
                print(f"aviso: {nome} não tem {ch!r}")
                continue
            nome_glifo = fonte.cmap[ord(ch)]
            caneta = SVGPathPen(glyph_set, ntos=_numero)
            glyph_set[nome_glifo].draw(caneta)
            _, posicoes = _molda(hbf, ch)
            avancos[ch] = posicoes[0].x_advance
            glifos[ch] = [avancos[ch], _relativo(caneta.getCommands())]
        # kerning: a diferença entre o par moldado pelo HarfBuzz e as duas letras soltas
        kern = {}
        letras = [c for c in glifos if c != " "]
        for a in letras:
            for b in letras:
                infos, posicoes = _molda(hbf, a + b)
                if len(infos) != 2:
                    continue
                ajuste = posicoes[0].x_advance - avancos[a]
                if ajuste:
                    kern[a + b] = ajuste
        limites = BoundsPen(glyph_set)
        glyph_set[fonte.cmap[ord("H")]].draw(limites)
        saida[estilo] = {
            "fonte": nome,
            "eixos": eixos,
            "caixa_alta": caixa_alta,
            "upm": fonte.upm,
            "cap": round(limites.bounds[3]),
            "glifos": glifos,
            "kern": kern,
        }
        print(f"{estilo:<9} {len(glifos):>4} letras, {len(kern):>5} pares de kerning")
    # o "largo" serve para a letra esticar: precisa ter os mesmos comandos do "titulo"
    for ch, (_, d) in saida["largo"]["glifos"].items():
        base = saida["titulo"]["glifos"][ch][1]
        if [c for c in d if c.isalpha()] != [c for c in base if c.isalpha()]:
            raise SystemExit(f"o contorno de {ch!r} muda de estrutura entre as larguras")
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fontes", required=True, help="pasta node_modules do portfólio")
    ap.add_argument("--saida", default=os.path.join(AQUI, "letras.json"))
    args = ap.parse_args()
    dados = {
        "sobre": "Contornos das letras gerados por scripts/fontes/extrair.py. "
                 "Fontes sob a SIL Open Font License 1.1, ver scripts/fontes/licencas.",
        "estilos": extrair(args.fontes),
    }
    with open(args.saida, "w", encoding="utf-8", newline="\n") as arq:
        json.dump(dados, arq, ensure_ascii=False, separators=(",", ":"))
        arq.write("\n")
    print(f"gravado {args.saida} ({os.path.getsize(args.saida) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
