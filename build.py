"""Builds dark_mode.svg / light_mode.svg: ASCII portrait + neofetch-style stats panel.
Run: python build.py   (needs `gh` logged in, or GH_TOKEN in env)"""
import json, subprocess, html
from datetime import datetime, timezone
from PIL import Image, ImageOps, ImageDraw, ImageFilter

USER = "Tanny28"
COLS, ROWS = 96, 56
RAMP = " .:-=+*#%@"

def gh(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args], text=True))

def ascii_art(invert):
    im = Image.open("me_cut.png").crop((120, 40, 340, 294))
    m = im.getchannel("A").resize((COLS, ROWS), Image.LANCZOS)
    g = Image.new("L", im.size, 0); g.paste(im.convert("L"), mask=im.getchannel("A"))
    g = ImageOps.autocontrast(g.filter(ImageFilter.UnsharpMask(3, 250, 0)).resize((COLS, ROWS), Image.LANCZOS), cutoff=1)
    px, mp, out = g.load(), m.load(), []
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            if mp[x, y] < 100: row += " "; continue          # background stays blank
            v = px[x, y] / 255
            d = 1 - v if invert else v
            row += RAMP[min(int((0.15 + 0.85 * d) ** 0.9 * (len(RAMP) - 1)), len(RAMP) - 1)]
        out.append(row.rstrip())
    return out

def stats():
    u = gh(f"users/{USER}")
    repos = gh(f"users/{USER}/repos?per_page=100&type=owner")
    own = [r for r in repos if not r["fork"]]
    langs = {}
    for r in own:
        if r["language"]: langs[r["language"]] = langs.get(r["language"], 0) + 1
    commits = gh("-H", "Accept: application/vnd.github+json", f"search/commits?q=author:{USER}&per_page=1")["total_count"]
    age = datetime.now(timezone.utc) - datetime.fromisoformat(u["created_at"].replace("Z", "+00:00"))
    return dict(repos=u["public_repos"], followers=u["followers"], stars=sum(r["stargazers_count"] for r in own),
                commits=commits, langs=", ".join(sorted(langs, key=langs.get, reverse=True)[:4]),
                uptime=f"{age.days // 365} years, {age.days % 365 // 30} months")

def svg(invert, s):
    bg, fg, dim, key, val, acc = (("#f6f8fa", "#24292f", "#8c959f", "#bc4c00", "#0550ae", "#1a7f37") if invert
                                  else ("#161b22", "#c9d1d9", "#6e7681", "#ffa657", "#a5d6ff", "#7ee787"))
    art = ascii_art(invert)
    info = [("Role", "AI Engineer | LLMs, Agents, MLOps"),
            ("Status", "OPEN TO WORK: jobs + internships (Jan 2027)"),
            ("Education", "B.Tech AI & ML, PCU Pune | CGPA 8.24"),
            ("Now", "AI Engineer Intern @ Pixaflip (Pixa Agent, 170+ tests)"),
            ("Research", "IEEE EMBS intern: Alzheimer's MRI staging"),
            ("Paper", "Best Paper Award, ICCTVB-25 (co-author)"),
            ("Hackathons", "Top 25/600+ DP World x BITS | GFG x Vultr 2nd"),
            ("Building", "AUTONOMA: LLM agent vs rules for ML drift"),
            ("Shipped", "Drone Agent, Lecture Analyzer, Tradexa"),
            ("# Stack", None),
            ("Languages", "Python, TypeScript, SQL"),
            ("GenAI", "LangChain, LangGraph, RAG, MCP, Groq, Ollama"),
            ("ML", "PyTorch, scikit-learn, XGBoost, MLflow, CLIP"),
            ("Backend", "FastAPI, PostgreSQL, Docker, Prometheus"),
            ("# Contact", None),
            ("Email", "shindetanmay282@gmail.com"),
            ("LinkedIn", "linkedin.com/in/tanmay-shinde-840a05340"),
            ("Web", "tanmay-shinde-28.vercel.app"),
            ("# GitHub Stats", None),
            ("Repos", f'{s["repos"]}  |  Stars: {s["stars"]}'),
            ("Commits", f'{s["commits"]}  |  Followers: {s["followers"]}')]
    L = [f'<text class="a" x="15" y="{16 + i*8.9}" fill="{fg}" xml:space="preserve">{html.escape(r)}</text>' for i, r in enumerate(art)]
    R = [f'<text x="470" y="30" fill="{acc}">Tanmay Shinde<tspan fill="{dim}"> @Tanny28</tspan></text>',
         f'<text x="470" y="38" fill="{dim}">{"-" * 46}</text>']
    y = 38
    for k, v in info:
        if v is None:
            y += 25; R.append(f'<text x="470" y="{y}" fill="{fg}">- {k[2:]} {"-" * (44 - len(k))}</text>'); continue
        y += 19
        dots = "." * max(2, 14 - len(k))
        vc = acc if k == "Status" else val
        R.append(f'<text x="470" y="{y}"><tspan fill="{key}">{k}</tspan><tspan fill="{dim}">:{dots} </tspan>'
                 f'<tspan fill="{vc}">{html.escape(v)}</tspan></text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="985" height="510" viewBox="0 0 985 510">'
            f'<style>text{{font:12px "Courier New",Consolas,monospace}}.a{{font-size:7.5px}}</style>'
            f'<rect width="985" height="510" rx="15" fill="{bg}"/>{"".join(L)}{"".join(R)}</svg>')

if __name__ == "__main__":
    s = stats(); print(s)
    open("dark_mode.svg", "w", encoding="utf-8").write(svg(False, s))
    open("light_mode.svg", "w", encoding="utf-8").write(svg(True, s))
