# Builds the publishable artifact page from index.html:
#  - keeps only the ARTIFACT-START..ARTIFACT-END body
#  - embeds the tournament data (seed.json, or a JSON backup exported from the app)
#  - inlines the club logo as a data URI
# Usage: python3 tools/build_artifact.py OUT.html [--data backup.json]
import sys, os, re, json, base64
root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
args = sys.argv[1:]
data_path = os.path.join(root, "seed.json")
if "--data" in args:
    i = args.index("--data"); data_path = args[i + 1]; del args[i:i + 2]
out = args[0] if args else os.path.join(root, "dist", "galil-3x3.html")

src = open(os.path.join(root, "index.html"), encoding="utf-8").read()
body = re.search(r"<!-- ARTIFACT-START -->\n(.*)<!-- ARTIFACT-END -->", src, re.S).group(1)

data = json.load(open(data_path, encoding="utf-8"))
data = {k: data.get(k) for k in ("settings", "teams", "houses", "games")}
js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("<!--", "<\\!--")
body, n = re.subn(r'(<script type="application/json" id="tournament-data">)[\s\S]*?(</script>)', lambda m: m.group(1) + js + m.group(2), body)
assert n == 1, "data block not found"

logo = os.path.join(root, "assets", "logo-224.jpg")
b64 = base64.b64encode(open(logo, "rb").read()).decode()
body, n = re.subn(r'src="assets/logo-224\.jpg"', f'src="data:image/jpeg;base64,{b64}"', body)
assert n == 1, "logo tag not found"

os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, "w", encoding="utf-8").write(body)
print(f"wrote {out}: {len(body)} bytes, data from {os.path.relpath(data_path, root)}")
