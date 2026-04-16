#!/usr/bin/env python3
"""
Impressor de Etiquetas de Preço - Pimaco A5Q-813
Folha A5 landscape | 13 colunas x 14 linhas = 182 etiquetas por folha
Formato de entrada: uma etiqueta por linha (ex: R$25, R$100)

Uso:
    python imprimir_etiquetas.py etiquetas.txt
    python imprimir_etiquetas.py etiquetas.txt saida.pdf
"""

import sys
import os
from reportlab.lib.pagesizes import landscape, A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ─── Layout da folha A5Q-813 em paisagem ──────────────────────────────────────
PAGE_W, PAGE_H = landscape(A5)   # 595.28 x 419.53 pts  (210 x 148.5 mm)

COLUNAS        = 13
LINHAS         = 14
ETIQ_POR_FOLHA = COLUNAS * LINHAS   # 182

ETIQUETA_W     = 13.0 * mm
ETIQUETA_H     =  8.0 * mm

# Margens calibradas a partir do PDF de referência (medição real)
MARGEM_ESQ     = 8.5 * mm
MARGEM_SUP     =  5.0 * mm

# Gap entre etiquetas calculado para preencher a área útil
GAP_H = (PAGE_W - MARGEM_ESQ * 2 - COLUNAS * ETIQUETA_W) / (COLUNAS - 1)
GAP_V = (PAGE_H - MARGEM_SUP * 2 - LINHAS  * ETIQUETA_H) / (LINHAS  - 1)

PASSO_H = ETIQUETA_W + GAP_H
PASSO_V = ETIQUETA_H + GAP_V

# ─── Fonte e tamanho automático por comprimento do texto ──────────────────────
FONTE = "Times-Roman"

def tamanho_fonte(texto: str) -> float:
    """Ajusta o tamanho da fonte conforme o comprimento do valor."""
    n = len(texto)
    if n <= 3:  return 14.5   # R$5
    if n == 4:  return 14.5   # R$25
    if n == 5:  return 11.5   # R$100
    return 5.5


def parsear_linhas(linhas) -> list[str]:
    etiquetas = []
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        if "x" in linha:
            multiplo, _, texto = linha.partition("x")
            if multiplo.isdigit() and texto:
                etiquetas.extend([texto] * int(multiplo))
                continue
        etiquetas.append(linha)
    return etiquetas


def carregar_etiquetas(caminho_txt: str) -> list[str]:
    if not os.path.exists(caminho_txt):
        print(f"[ERRO] Arquivo não encontrado: {caminho_txt}")
        sys.exit(1)
    with open(caminho_txt, encoding="utf-8") as f:
        etiquetas = parsear_linhas(f)
    print(f"[INFO] {len(etiquetas)} etiqueta(s) lida(s) de '{caminho_txt}'")
    return etiquetas


def gerar_pdf(etiquetas: list[str], destino) -> None:
    total_paginas = max(1, -(-len(etiquetas) // ETIQ_POR_FOLHA))

    c = canvas.Canvas(destino, pagesize=landscape(A5))

    idx = 0
    for _ in range(total_paginas):
        for linha in range(LINHAS):
            for col in range(COLUNAS):
                if idx >= len(etiquetas):
                    break

                texto = etiquetas[idx]
                idx += 1

                x = MARGEM_ESQ + col * PASSO_H
                y = PAGE_H - MARGEM_SUP - (linha + 1) * ETIQUETA_H - linha * GAP_V

                fs = tamanho_fonte(texto)
                c.setFont(FONTE, fs)

                tw = c.stringWidth(texto, FONTE, fs)
                tx = x + (ETIQUETA_W - tw) / 2
                ty = y + (ETIQUETA_H - fs) / 2 + 0.5

                c.drawString(tx, ty, texto)

            else:
                continue
            break

        c.showPage()

    c.save()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    caminho_txt = sys.argv[1]
    caminho_pdf = (
        sys.argv[2] if len(sys.argv) >= 3
        else caminho_txt.rsplit(".", 1)[0] + "_etiquetas.pdf"
    )

    etiquetas = carregar_etiquetas(caminho_txt)
    gerar_pdf(etiquetas, caminho_pdf)


if __name__ == "__main__":
    main()