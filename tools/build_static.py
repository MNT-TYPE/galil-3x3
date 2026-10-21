# Builds the GitHub Pages site into docs/ from index.html + seed.json:
#   docs/index.html  - parents' page (view-only; loads docs/data.json and refreshes every minute)
#   docs/admin.html  - management page (edits saved to the repository through the GitHub API)
#   docs/data.json   - the data file both pages read
# Usage: python3 tools/build_static.py [--data backup.json] [--out docs] [--github OWNER/REPO@BRANCH:docs/data.json] [--share-url URL]
import sys, os, re, json, base64
root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
args = sys.argv[1:]
def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default
data_path = opt("--data", os.path.join(root, "seed.json")); out = opt("--out", os.path.join(root, "docs"))
github = opt("--github"); share = opt("--share-url")

src = open(os.path.join(root, "index.html"), encoding="utf-8").read().replace("<!-- ARTIFACT-START -->\n", "").replace("<!-- ARTIFACT-END -->\n", "")
data = json.load(open(data_path, encoding="utf-8"))
data = {k: data.get(k) for k in ("settings", "teams", "houses", "games")}
if share: data["settings"] = dict(data["settings"] or {}, shareUrl=share)
js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("<!--", "<\\!--")
b64 = base64.b64encode(open(os.path.join(root, "assets", "logo-224.jpg"), "rb").read()).decode()

def page(attrs):
    s, n = re.subn(r'(<script type="application/json" id="tournament-data")(>)[\s\S]*?(</script>)', lambda m: m.group(1) + attrs + ">" + js + m.group(3), src); assert n == 1
    s, n = re.subn(r'src="assets/logo-224\.jpg"', f'src="data:image/jpeg;base64,{b64}"', s); assert n == 1
    return s

import time
build = time.strftime("%Y%m%d-%H%M%S")
os.makedirs(out, exist_ok=True)
json.dump({"build": build}, open(os.path.join(out, "version.json"), "w"))
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page(f' data-public="1" data-build="{build}"'))
json.dump(data, open(os.path.join(out, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
made = ["index.html", "data.json", "version.json"]
if github:
    open(os.path.join(out, "admin.html"), "w", encoding="utf-8").write(page(f' data-github="{github}" data-build="{build}"')); made.append("admin.html")
print(f"wrote {', '.join(made)} in {os.path.relpath(out, root)}/ (data from {os.path.relpath(data_path, root)})")
