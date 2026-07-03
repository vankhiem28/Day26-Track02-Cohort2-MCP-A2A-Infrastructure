import json
nb = json.load(open("day26_mcp_a2a_lab.ipynb"))
for c in nb["cells"]:
    if c["cell_type"] != "code":
        continue
    src = "".join(c["source"])
    if "SINH VIÊN ĐIỀN" in src:
        exec(src)
        break