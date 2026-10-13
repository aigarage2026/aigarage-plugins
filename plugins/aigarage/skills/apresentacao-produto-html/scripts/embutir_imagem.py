"""Converte uma imagem em data URI base64 para colar no <img src>.
Uso: python embutir_imagem.py telas/dashboard.jpg > dashboard.b64.txt
"""
import sys, base64, mimetypes
f = sys.argv[1]
mime = mimetypes.guess_type(f)[0] or "image/jpeg"
print(f"data:{mime};base64," + base64.b64encode(open(f, "rb").read()).decode())
