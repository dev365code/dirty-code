#!/usr/bin/env python3
"""E1 예비 관찰: 내 컴퓨터의 코딩 에이전트(Claude Code)가 한 달 동안 얼마나 읽고 실행했나.

Claude Code는 세션 기록을 ~/.claude/projects/ 아래 .jsonl 파일로 남긴다.
이 스크립트는 그 기록에서 도구 호출을 세기만 한다. 내용은 읽지 않고 바깥으로 보내지도 않는다.

  사용: python3 experiments/e1_count.py [며칠] [끝나는 때(UTC, 2026-11-11T13:00:00 꼴)]

세는 것
  - 도구 호출을 호출 id로 한 번씩만 센다(같은 호출이 기록에 두 번 남는 일이 있다).
  - 파일 읽기 도구(Read)가 연 파일을 확장자로 갈라, 코드 파일만 따로 센다.
  - 명령 실행(Bash) 가운데 읽는 명령(grep, cat, sed 따위)으로 시작하는 것을 어림으로 센다.

세지 못하는 것
  - 명령 실행 안에서 실제로 몇 개 파일을 읽었는지.
  - 사람이 직접 연 파일 수.
  - 다른 도구(Codex 등)의 기록.
"""
import collections
import datetime
import glob
import json
import os
import sys

ROOT = os.path.expanduser("~/.claude/projects")
CODE = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rs", ".c", ".h",
        ".cc", ".cpp", ".hpp", ".cs", ".rb", ".php", ".swift", ".sh", ".sql", ".html", ".css"}
READ_COMMANDS = ("grep", "rg", "cat", "sed", "head", "tail", "less", "awk", "find", "ls", "wc", "git diff", "git show", "git log")


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    until = (datetime.datetime.strptime(sys.argv[2], "%Y-%m-%dT%H:%M:%S") if len(sys.argv) > 2
             else datetime.datetime.utcnow())
    since = until - datetime.timedelta(days=days)
    lo, hi = since.strftime("%Y-%m-%dT%H:%M:%S"), until.strftime("%Y-%m-%dT%H:%M:%S")

    seen, tools = set(), collections.Counter()
    read_files, read_calls, code_calls, reading_cmds = {}, 0, 0, 0
    record_files = 0
    for path in glob.glob(ROOT + "/**/*.jsonl", recursive=True):
        used = False
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if '"tool_use"' not in line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                stamp = obj.get("timestamp", "")
                if not (lo <= stamp[:19] <= hi):
                    continue
                content = (obj.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    if block.get("id") in seen:
                        continue
                    seen.add(block.get("id"))
                    used = True
                    name, args = block.get("name", ""), block.get("input") or {}
                    tools[name] += 1
                    if name == "Read":
                        fp = args.get("file_path", "")
                        ext = os.path.splitext(fp)[1].lower()
                        read_calls += 1
                        read_files[fp] = ext
                        if ext in CODE:
                            code_calls += 1
                    elif name == "Bash":
                        cmd = (args.get("command") or "").lstrip()
                        if cmd.startswith(READ_COMMANDS):
                            reading_cmds += 1
        record_files += used

    code_files = sum(1 for ext in read_files.values() if ext in CODE)
    print("기간(UTC): %s ~ %s (%d일)" % (lo, hi, days))
    print("도구 호출이 든 기록 파일: %d개" % record_files)
    print("명령 실행(Bash): %d번, 그 가운데 읽는 명령으로 시작한 것(어림): %d번" % (tools["Bash"], reading_cmds))
    print("파일 읽기 도구(Read): %d번, 서로 다른 파일 %d개" % (read_calls, len(read_files)))
    print("  그 가운데 코드 파일: %d번, 서로 다른 파일 %d개" % (code_calls, code_files))
    print("파일 쓰기(Write): %d번, 파일 고치기(Edit): %d번" % (tools["Write"], tools["Edit"]))
    top = collections.Counter(read_files.values()).most_common(6)
    print("읽기 도구가 연 파일의 확장자 상위: " + ", ".join("%s %d" % (e or "(없음)", n) for e, n in top))


if __name__ == "__main__":
    main()
