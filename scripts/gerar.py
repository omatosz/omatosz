#!/usr/bin/env python3
"""Gera os SVGs animados do perfil (banner, Veryon, números, troféus, stack,
botões e a moldura da cobrinha). Usa só a biblioteca padrão do Python.

Uso local:
    python scripts/gerar.py --saida dist --veryon ../SOC.SIEM

Na Action do GitHub, o repositório do Veryon é clonado numa pasta e passado
em --veryon. Os textos e números fixos ficam em perfil.json.
"""
import argparse
import datetime
import json
import os
import sys
import xml.etree.ElementTree as ET

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import banner  # noqa: E402
import botoes  # noqa: E402
import cartao_github  # noqa: E402
import cartao_veryon  # noqa: E402
import cobrinha  # noqa: E402
import dados as coleta  # noqa: E402
import stack  # noqa: E402
import trofeus  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Gera os SVGs do perfil.")
    ap.add_argument("--saida", default="dist", help="pasta onde os SVGs são gravados")
    ap.add_argument("--perfil", default=os.path.join(AQUI, "..", "perfil.json"))
    ap.add_argument("--veryon", required=True, help="pasta com um clone do repositório do Veryon")
    ap.add_argument("--cobrinha", help="SVG bruto da cobrinha, para embrulhar no cartão")
    ap.add_argument("--cache", help="pasta de cache das respostas (só para desenvolvimento)")
    args = ap.parse_args()

    with open(args.perfil, encoding="utf-8") as arq:
        perfil = json.load(arq)
    coleta.CACHE = args.cache
    token = os.environ.get("GITHUB_TOKEN") or None
    dados = coleta.coletar(perfil, token, args.veryon)

    pecas = {
        "banner.svg": banner.desenhar(perfil),
        "veryon.svg": cartao_veryon.desenhar(perfil, dados),
        "github.svg": cartao_github.desenhar(perfil, dados),
        "trofeus.svg": trofeus.desenhar(perfil, dados),
        "stack.svg": stack.desenhar(perfil, dados),
    }
    for nome, texto in botoes.desenhar_todos().items():
        pecas[nome + ".svg"] = texto
    if args.cobrinha:
        with open(args.cobrinha, encoding="utf-8") as arq:
            pecas["cobrinha.svg"] = cobrinha.compor(arq.read())

    # só grava depois de tudo pronto e válido, para nunca deixar arquivo pela metade
    for nome, texto in pecas.items():
        ET.fromstring(texto)
    os.makedirs(args.saida, exist_ok=True)
    for nome, texto in pecas.items():
        with open(os.path.join(args.saida, nome), "w", encoding="utf-8", newline="\n") as arq:
            arq.write(texto)
        print(f"{nome:<18} {len(texto.encode('utf-8')) / 1024:6.1f} KB")
    print(f"Gerado em {datetime.date.today():%d/%m/%Y}: {dados['contribuicoes']} contribuições, "
          f"{dados['linhas_total']} linhas, nível {dados['xp_total'] // perfil['xp_por_nivel'] + 1}.")


if __name__ == "__main__":
    main()
