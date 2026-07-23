#!/usr/bin/env python3
"""Shared Azure AI client for the Indian History anime-comic engine.

Wraps the three Azure calls we need, with the auth + retry behaviour proven in the
Indian Tales pipeline:
  * token()      - AAD bearer token for the cognitiveservices resource
  * chat_json()  - gpt-4o, JSON-object response (character bibles + storyboards)
  * gen_image()  - gpt-image-2 images/generations (text -> image; character sheets, covers)
  * edit_image() - gpt-image-2 images/edits with reference image(s) -> character-consistent panels

Auth = `Bearer <token>` where the token comes from
`az account get-access-token --resource https://cognitiveservices.azure.com`.
Each high-quality 1024-1536px image call takes ~2 min, so KEEP the keepactive guard running.
"""
import base64, io, json, os, pathlib, subprocess, sys, tempfile, time
import urllib.error, urllib.request

ENDPOINT = "https://ai-contosohub530569751908.cognitiveservices.azure.com"
IMG_DEPLOY = "gpt-image-2"
IMG_APIV = "2025-04-01-preview"
CHAT_DEPLOY = "gpt-4o"
CHAT_APIV = "2025-01-01-preview"
CS_SCOPE = "https://cognitiveservices.azure.com"


def token(tries=3):
    """Fetch an AAD bearer token for the cognitiveservices resource.

    `az` output is written to a temp FILE (not a PIPE): on Windows a piped
    subprocess whose grandchild (az.cmd -> python) keeps the pipe open will
    DEADLOCK when `timeout` fires (kill hits cmd.exe but communicate() blocks
    on the still-open inherited pipe). Writing to a file has no pipe to drain,
    so a hung `az` is killed cleanly and we retry instead of hanging forever.
    """
    for i in range(1, tries + 1):
        tf = None
        try:
            tf = tempfile.NamedTemporaryFile(prefix="aad_", suffix=".txt", delete=False)
            tf.close()
            with open(tf.name, "w") as fh:
                subprocess.run(["az", "account", "get-access-token", "--resource", CS_SCOPE,
                                "--query", "accessToken", "-o", "tsv"],
                               stdout=fh, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                               shell=True, timeout=90)
            t = pathlib.Path(tf.name).read_text().strip()
            if t:
                return t
        except subprocess.TimeoutExpired:
            print(f"    az token timed out (try {i}/{tries})", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"    az token err (try {i}/{tries}): {e!r}", flush=True)
        finally:
            if tf is not None:
                try:
                    os.unlink(tf.name)
                except OSError:
                    pass
        time.sleep(3 * i)
    raise RuntimeError("No AAD token after retries. Run `az login`.")


def chat_json(system, user, tok=None, max_tokens=6500, tries=4):
    """gpt-4o call returning a parsed JSON object. Returns (result, tok)."""
    tok = tok or token()
    body = json.dumps({"messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}],
                       "response_format": {"type": "json_object"},
                       "max_completion_tokens": max_tokens}).encode("utf-8")
    url = f"{ENDPOINT}/openai/deployments/{CHAT_DEPLOY}/chat/completions?api-version={CHAT_APIV}"
    last = None
    for i in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Authorization", f"Bearer {tok}")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=240) as r:
                data = json.loads(r.read())
            return json.loads(data["choices"][0]["message"]["content"]), tok
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:200]!r}"
            if e.code in (401, 403):
                tok = token()
            time.sleep(4 * i)
        except Exception as e:  # noqa: BLE001
            last = repr(e)
            time.sleep(4 * i)
    raise RuntimeError(f"chat_json failed: {last}")


def gen_image(prompt, out, tok, size="1024x1024", quality="high", tries=8):
    """images/generations (text -> image). Returns tok (refreshed on 401). Writes `out`.
    Returns None-token only on hard failure (leaves `out` absent)."""
    url = f"{ENDPOINT}/openai/deployments/{IMG_DEPLOY}/images/generations?api-version={IMG_APIV}"
    body = json.dumps({"prompt": prompt, "size": size, "n": 1, "quality": quality}).encode()
    out = pathlib.Path(out)
    for i in range(1, tries + 1):
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Authorization", f"Bearer {tok}")
        req.add_header("Content-Type", "application/json")
        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=300) as r:
                out.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
            print(f"    gen {out.name} {out.stat().st_size}B {time.time()-t0:.0f}s", flush=True)
            return tok
        except urllib.error.HTTPError as e:
            msg = e.read()[:200]
            print(f"    gen HTTP {e.code} (try {i}/{tries}): {msg!r}", flush=True)
            if e.code in (401, 403):
                tok = token(); wait = 3
            elif e.code == 429:
                ra = e.headers.get("Retry-After"); wait = (int(ra) + 3) if (ra and ra.isdigit()) else 45
            elif e.code >= 500:
                wait = 12 * i  # transient Azure server error (500/502/503) — back off longer
            else:
                wait = 5 * i
            time.sleep(wait)
        except Exception as e:  # noqa: BLE001
            print(f"    gen err (try {i}/{tries}): {e}", flush=True); time.sleep(5 * i)
    print(f"    FAILED gen {out}", flush=True)
    return tok


def edit_image(prompt, refs, out, tok, size="1024x1024", quality="high",
               input_fidelity="high", tries=8):
    """images/edits with reference image(s) -> a character-consistent image.

    `refs` = list of image paths fed as `image[]`. `input_fidelity="high"` asks the model
    to preserve the reference's identity/detail; if the deployment rejects it (HTTP 400 on
    that param) we transparently drop it and retry. Returns tok. Writes `out`."""
    url = f"{ENDPOINT}/openai/deployments/{IMG_DEPLOY}/images/edits?api-version={IMG_APIV}"
    refs = [pathlib.Path(r) for r in refs]
    out = pathlib.Path(out)
    use_fidelity = bool(input_fidelity)
    for i in range(1, tries + 1):
        boundary = f"----ihist{int(time.time()*1000)}"
        buf = io.BytesIO()

        def w(s):
            buf.write(s.encode() if isinstance(s, str) else s)

        for ref in refs:
            w(f"--{boundary}\r\n")
            w(f'Content-Disposition: form-data; name="image[]"; filename="{ref.name}"\r\n')
            w("Content-Type: image/png\r\n\r\n")
            w(ref.read_bytes()); w("\r\n")
        fields = [("prompt", prompt), ("n", "1"), ("size", size), ("quality", quality)]
        if use_fidelity:
            fields.append(("input_fidelity", input_fidelity))
        for k, v in fields:
            w(f"--{boundary}\r\n")
            w(f'Content-Disposition: form-data; name="{k}"\r\n\r\n')
            w(f"{v}\r\n")
        w(f"--{boundary}--\r\n")

        req = urllib.request.Request(url, data=buf.getvalue(), method="POST")
        req.add_header("Authorization", f"Bearer {tok}")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=300) as r:
                out.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
            print(f"    edit {out.name} {out.stat().st_size}B {time.time()-t0:.0f}s", flush=True)
            return tok
        except urllib.error.HTTPError as e:
            msg = e.read()[:200]
            print(f"    edit HTTP {e.code} (try {i}/{tries}): {msg!r}", flush=True)
            if e.code == 400 and use_fidelity and b"input_fidelity" in msg:
                use_fidelity = False; continue  # retry immediately without the param
            if e.code in (401, 403):
                tok = token(); wait = 3
            elif e.code == 429:
                ra = e.headers.get("Retry-After"); wait = (int(ra) + 3) if (ra and ra.isdigit()) else 45
            elif e.code >= 500:
                wait = 12 * i  # transient Azure server error (500/502/503) — back off longer
            else:
                wait = 5 * i
            time.sleep(wait)
        except Exception as e:  # noqa: BLE001
            print(f"    edit err (try {i}/{tries}): {e}", flush=True); time.sleep(5 * i)
    print(f"    FAILED edit {out}", flush=True)
    return tok
