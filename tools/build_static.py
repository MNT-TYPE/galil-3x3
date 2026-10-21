# Builds a single self-contained, VIEW-ONLY index.html for any static host (GitHub Pages, Netlify, a club website).
# Usage: python3 tools/build_static.py [--data backup.json] [--out dist/public/index.html]
import sys, os, re, json, base64
root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
args = sys.argv[1:]
data_path = os.path.join(root, "seed.json"); out = os.path.join(root, "dist", "public", "index.html")
if "--data" in args: i = args.index("--data"); data_path = args[i+1]
if "--out" in args: i = args.index("--out"); out = args[i+1]
share = None
if "--share-url" in args: i = args.index("--share-url"); share = args[i+1]
s = open(os.path.join(root, "index.html"), encoding="utf-8").read()
data = json.load(open(data_path, encoding="utf-8"))
data = {k: data.get(k) for k in ("settings", "teams", "houses", "games")}
if share: data["settings"] = dict(data["settings"] or {}, shareUrl=share)
js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("<!--", "<\\!--")
s, n = re.subn(r'(<script type="application/json" id="tournament-data")(>)[\s\S]*?(</script>)', lambda m: m.group(1) + ' data-public="1">' + js + m.group(3), s); assert n == 1
b64 = base64.b64encode(open(os.path.join(root, "assets", "logo-224.jpg"), "rb").read()).decode()
s, n = re.subn(r'src="assets/logo-224\.jpg"', f'src="data:image/jpeg;base64,{b64}"', s); assert n == 1
s = s.replace("<!-- ARTIFACT-START -->\n", "").replace("<!-- ARTIFACT-END -->\n", "")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, "w", encoding="utf-8").write(s)
print(f"wrote {out}: {len(s)} bytes (view-only, data from {os.path.relpath(data_path, root)})")
