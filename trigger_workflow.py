import subprocess
import os

os.environ["GH_TOKEN"] = "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"

def trigger():
    subprocess.run([
        "gh", "workflow", "run", "Deploy Blog to GitHub Pages",
        "--repo", "francky07/ia-net-blog-pro"
    ], capture_output=True)
    print("✅ Workflow GitHub déclenché")

if __name__ == "__main__":
    trigger()
