#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 GitHub Git Data API 推送本地快照（绕过 git 协议的代理问题）"""
import base64
import json
import os
import sys
import urllib.request

TOKEN = os.environ["GH_TOKEN"]
OWNER, REPO = "Huqiming444", "DIAGNOSEX"
API = "https://api.github.com"
ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "remote-diag"}
SKIP_SUFFIX = {".pyc"}


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "diagnosex-push")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def collect():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1] in SKIP_SUFFIX:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            files.append((rel, full))
    return sorted(files)


def main():
    ref = call("GET", f"/repos/{OWNER}/{REPO}/git/ref/heads/main")
    base_commit = ref["object"]["sha"]
    print("base commit:", base_commit)

    tree_entries = []
    for rel, full in collect():
        with open(full, "rb") as f:
            content = f.read()
        # 超过 40MB 需用 blob API，本项目无此情况
        blob = call("POST", f"/repos/{OWNER}/{REPO}/git/blobs",
                    {"content": base64.b64encode(content).decode(), "encoding": "base64"})
        tree_entries.append({"path": rel, "mode": "100755" if rel.endswith(".sh") else "100644",
                             "type": "blob", "sha": blob["sha"]})
        print("  blob ok:", rel, len(content), "bytes")

    tree = call("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"tree": tree_entries})
    print("tree:", tree["sha"])

    msg = ("升级至新版：一页纸诊断报告导出 + macOS/Linux 一键启动\n\n"
           "- 新增逐家一页纸诊断结果导出（HTML 单页 / Markdown / 完整七章报告 / 批量 ZIP）\n"
           "- 新增 run_DIAGNOSEX.sh（macOS/Linux 一键启动，逻辑与 .bat 一致）\n"
           "- 更新主程序 DIAGNOSEX.py 至最新版（含导出功能）\n"
           "- README 补充跨平台启动说明与导出功能文档\n"
           "- 新增使用说明与一页纸报告示例")
    commit = call("POST", f"/repos/{OWNER}/{REPO}/git/commits",
                  {"message": msg, "tree": tree["sha"], "parents": [base_commit]})
    print("commit:", commit["sha"])

    call("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/main", {"sha": commit["sha"]})
    print("ref updated ->", commit["sha"])


if __name__ == "__main__":
    main()
