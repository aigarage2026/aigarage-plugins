"""Abre o sistema de verdade e fotografa as telas e os relatórios para a apresentação.

Uso:
    python capturar_sistema.py roteiro.json [--saida telas]

Requer: pip install playwright pillow pymupdf && python -m playwright install chromium

O roteiro (JSON) descreve o que fotografar. Exemplo em
references/roteiro-captura.exemplo.json. Campos:

    base_url        raiz do sistema (ex.: http://localhost:8090)
    viewport        {"width": 1440, "height": 900}
    escala          device_scale_factor (padrão 1)
    tema            opcional: script JS rodado antes de cada página (tema claro/escuro)
    login           {"url", "campos": {seletor: valor}, "enviar": seletor, "esperar": seletor|url}
                    Valores "${VAR}" vêm de variável de ambiente: credencial nunca vai no roteiro.
    mascarar        {"regex": [...], "seletores": [...], "substituto": "•••",
                     "ocultar": [{"seletor": ".font-mono", "regex": "^[A-Z]...$",
                                  "aparar_vizinho": "^\\s*·\\s*"}]}
                    regex troca o trecho por substituto; seletores desfoca; ocultar some
                    com o elemento cujo texto casa (e apara o separador do vizinho).
                    Aplicado antes de CADA print. É assim que a apresentação mostra a tela
                    real sem expor dado de cliente nem o "como" do produto.
    telas           lista de {"nome", "url", "passos": [...], "recorte": seletor?,
                    "pagina_inteira": bool?, "titulo": texto livre p/ o manifesto}
                    passos: {"clicar": sel} {"esperar": ms} {"esperar_seletor": sel}
                            {"digitar": [sel, texto]} {"rolar_ate": sel} {"js": código}
                            {"tecla": "Enter"}
                            {"baixar": sel, "como": "telas/docs/raiox.pdf"}  (salva o download)
                    Tela sem "nome" só executa os passos (útil para baixar relatórios).
    documentos      lista de {"nome", "arquivo": caminho do PDF, "paginas": [1, 2]}
                    Relatório gerado pelo sistema vira imagem de página, mascarado igual
                    (a máscara de PDF cobre o texto que casa com mascarar.regex).

Saída: <saida>/<nome>.jpg (JPEG q82, largura <= 1600) e <saida>/telas.json com o
manifesto (nome, título, arquivo, largura, altura) para montar a galeria.

Revise cada imagem antes de usar: a máscara pega o que o roteiro manda pegar, e só isso.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

LARGURA_MAX = 1600
QUALIDADE = 82

_JS_MASCARA = r"""
(cfg) => {
  const regs = (cfg.regex || []).map(r => new RegExp(r, 'g'));
  const sub = cfg.substituto || '•••';
  const pular = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEXTAREA']);
  const andar = (raiz) => {
    const w = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT);
    let n; while ((n = w.nextNode())) {
      if (!n.parentElement || pular.has(n.parentElement.tagName)) continue;
      let t = n.nodeValue, mudou = false;
      for (const r of regs) { const novo = t.replace(r, sub); if (novo !== t) { t = novo; mudou = true; } }
      if (mudou) n.nodeValue = t;
    }
  };
  andar(document.body);
  document.querySelectorAll('input, textarea').forEach(el => {
    for (const r of regs) if (r.test(el.value)) el.value = sub;
  });
  // ocultar: some com o elemento cujo texto inteiro casa o regex (ex.: o código técnico
  // ao lado do nome de negócio) e apara o separador que sobra no vizinho.
  for (const o of (cfg.ocultar || [])) {
    const re = new RegExp(o.regex);
    document.querySelectorAll(o.seletor).forEach(el => {
      if (!re.test((el.textContent || '').trim())) return;
      el.style.display = 'none';
      const viz = el.nextElementSibling;
      if (viz && o.aparar_vizinho) viz.textContent = viz.textContent.replace(new RegExp(o.aparar_vizinho), '');
    });
  }
  for (const s of (cfg.seletores || [])) {
    document.querySelectorAll(s).forEach(el => { el.style.filter = 'blur(6px)'; el.style.userSelect = 'none'; });
  }
  return true;
}
"""


def _env(valor: str) -> str:
    def troca(m: re.Match) -> str:
        nome = m.group(1)
        if nome not in os.environ:
            sys.exit(f"variável de ambiente {nome} não definida (credenciais ficam fora do roteiro)")
        # Arquivo de credenciais editado à mão costuma trazer \r do Windows ou o
        # prefixo colado duas vezes (APP_USER=APP_USER=...). Os dois quebram o login
        # sem mensagem clara, então são limpos aqui.
        v = os.environ[nome].strip().strip("\r")
        while v.startswith(nome + "="):
            v = v[len(nome) + 1:]
        return v

    return re.sub(r"\$\{([A-Z0-9_]+)\}", troca, valor)


def _salvar_jpg(png: bytes, destino: Path) -> tuple[int, int]:
    from io import BytesIO

    from PIL import Image

    img = Image.open(BytesIO(png)).convert("RGB")
    if img.width > LARGURA_MAX:
        img = img.resize((LARGURA_MAX, round(img.height * LARGURA_MAX / img.width)), Image.LANCZOS)
    img.save(destino, "JPEG", quality=QUALIDADE, optimize=True, progressive=True)
    return img.width, img.height


def _passos(pg, passos: list[dict]) -> None:
    for p in passos:
        if p.get("opcional"):
            # Passo que pode não ter alvo (ex.: relatório que ainda não foi gerado).
            try:
                _passos(pg, [{k: v for k, v in p.items() if k != "opcional"}])
            except Exception as exc:  # noqa: BLE001
                print("pulado (opcional):", list(p)[0], str(exc).splitlines()[0][:120])
            continue
        if "clicar" in p:
            pg.locator(p["clicar"]).first.click()
        elif "esperar" in p:
            pg.wait_for_timeout(int(p["esperar"]))
        elif "esperar_seletor" in p:
            pg.locator(p["esperar_seletor"]).first.wait_for(state="visible", timeout=30000)
        elif "digitar" in p:
            sel, texto = p["digitar"]
            pg.locator(sel).first.fill(_env(texto))
        elif "selecionar" in p:
            # Escolhe a opção de um <select> pelo trecho do rótulo (o texto exato
            # costuma trazer contagens que mudam a cada extração).
            sel, trecho = p["selecionar"]
            caixa = pg.locator(sel).first
            rotulos = caixa.locator("option").all_inner_texts()
            alvo = next((r for r in rotulos if trecho.lower() in r.lower()), None)
            if alvo is None:
                raise ValueError(f"nenhuma opção contém '{trecho}' em {sel}")
            caixa.select_option(label=alvo)
        elif "rolar_ate" in p:
            pg.locator(p["rolar_ate"]).first.scroll_into_view_if_needed()
        elif "tecla" in p:
            pg.keyboard.press(p["tecla"])
        elif "js" in p:
            pg.evaluate(p["js"])
        elif "baixar" in p:
            # Clica e guarda o arquivo que o sistema entrega (relatório gerado).
            with pg.expect_download(timeout=120000) as d:
                pg.locator(p["baixar"]).first.click()
            destino = Path(p["como"])
            destino.parent.mkdir(parents=True, exist_ok=True)
            d.value.save_as(destino)
            print("baixado", destino)
        else:
            raise ValueError(f"passo desconhecido: {p}")


def _capturar_documento(doc: dict, mascarar: dict, saida: Path) -> list[dict]:
    import fitz  # pymupdf

    regs = [re.compile(r) for r in mascarar.get("regex", [])]
    pdf = fitz.open(doc["arquivo"])
    itens = []
    for num in doc.get("paginas", [1]):
        pagina = pdf[num - 1]
        if regs:
            for palavra in pagina.get_text("words"):
                if any(r.fullmatch(palavra[4]) or r.search(palavra[4]) for r in regs):
                    pagina.add_redact_annot(fitz.Rect(palavra[:4]), fill=(0.85, 0.87, 0.9))
            pagina.apply_redactions()
        png = pagina.get_pixmap(dpi=144).tobytes("png")
        nome = f"{doc['nome']}-p{num}"
        w, h = _salvar_jpg(png, saida / f"{nome}.jpg")
        itens.append({"nome": nome, "titulo": doc.get("titulo", doc["nome"]), "arquivo": f"{nome}.jpg",
                      "largura": w, "altura": h, "tipo": "documento"})
        print("ok", nome)
    return itens


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    ap.add_argument("--saida", default="telas")
    args = ap.parse_args()

    cfg = json.loads(Path(args.roteiro).read_text(encoding="utf-8"))
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    mascarar = cfg.get("mascarar", {})
    manifesto: list[dict] = []

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport=cfg.get("viewport", {"width": 1440, "height": 900}),
                              device_scale_factor=cfg.get("escala", 1), locale="pt-BR")
        if cfg.get("tema"):
            ctx.add_init_script(cfg["tema"])
        pg = ctx.new_page()
        base = cfg["base_url"].rstrip("/")

        login = cfg.get("login")
        if login:
            pg.goto(base + login["url"], wait_until="networkidle")
            for sel, valor in login["campos"].items():
                pg.locator(sel).first.fill(_env(valor))
            pg.locator(login["enviar"]).first.click()
            esperar = login.get("esperar")
            try:
                if esperar and esperar.startswith(("http", "**", "/")):
                    pg.wait_for_url(esperar if not esperar.startswith("/") else base + esperar, timeout=30000)
                elif esperar:
                    pg.locator(esperar).first.wait_for(state="visible", timeout=30000)
            except Exception:  # noqa: BLE001
                pg.screenshot(path=str(saida / "_login-falhou.png"))
                nav.close()
                sys.exit(
                    f"login falhou: a tela esperada ({esperar}) não apareceu em 30 s. "
                    "Confira usuário e senha no arquivo de credenciais. "
                    f"A tela no momento da falha está em {saida}/_login-falhou.png"
                )
            pg.wait_for_load_state("networkidle")

        falhas = []
        for i, t in enumerate(cfg.get("telas", [])):
            rotulo = t.get("nome") or f"passo-{i}"
            try:
                if t.get("url"):
                    pg.goto(base + t["url"], wait_until="networkidle")
                _passos(pg, t.get("passos", []))
                if not t.get("nome"):
                    continue
                pg.wait_for_timeout(int(t.get("assentar", 600)))
                pg.evaluate(_JS_MASCARA, mascarar)
                if t.get("recorte"):
                    png = pg.locator(t["recorte"]).first.screenshot(type="png")
                else:
                    png = pg.screenshot(type="png", full_page=bool(t.get("pagina_inteira")))
            except Exception as exc:  # noqa: BLE001
                # Uma tela que falha não derruba as outras: fica o print do momento
                # da falha para ajustar o roteiro, e a captura segue.
                pg.screenshot(path=str(saida / f"_falhou-{rotulo}.png"))
                falhas.append(rotulo)
                print(f"FALHOU {rotulo}: {str(exc).splitlines()[0][:160]}")
                pg.keyboard.press("Escape")
                continue
            w, h = _salvar_jpg(png, saida / f"{t['nome']}.jpg")
            manifesto.append({"nome": t["nome"], "titulo": t.get("titulo", t["nome"]), "arquivo": f"{t['nome']}.jpg",
                              "largura": w, "altura": h, "tipo": "tela"})
            print("ok", t["nome"])
        nav.close()

    for doc in cfg.get("documentos", []):
        manifesto += _capturar_documento(doc, mascarar, saida)

    (saida / "telas.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(manifesto)} imagem(ns) em {saida}/; revise cada uma antes de embutir.")
    if falhas:
        print(f"{len(falhas)} tela(s) falharam: {', '.join(falhas)}. Veja {saida}/_falhou-*.png e ajuste o roteiro.")
        sys.exit(1)


if __name__ == "__main__":
    main()
