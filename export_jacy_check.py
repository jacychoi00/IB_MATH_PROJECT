import os
import json
from project_config import OUTPUT_DIR

def export_jacy_check():
    results = []

    for root, dirs, files in os.walk(OUTPUT_DIR):
        for f in files:
            if f.endswith("_metadata.json"):
                meta_path = os.path.join(root, f)
                with open(meta_path, "r", encoding="utf-8") as fp:
                    meta = json.load(fp)

                for item in meta:
                    if "jacy_check" in item["type"]:
                        results.append(
                            f"{item['image_path']}\t{item['type']}"
                        )

    with open("jacy_check_list.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print("Saved jacy_check_list.txt")

if __name__ == "__main__":
    export_jacy_check()
