#!/usr/bin/env python3
"""E1 예비 관찰: 내 컴퓨터의 코딩 에이전트(Claude Code)가 한 달 동안 얼마나 읽고 실행했나.

Claude Code는 세션 기록을 ~/.claude/projects/ 아래 .jsonl 파일로 남긴다.
이 스크립트는 그 기록에서 도구 호출을 세기만 한다. 결과로 찍는 것은 숫자뿐이고, 기록을 바깥으로 보내지 않는다.

  사용: python3 experiments/e1_count.py [며칠] [끝나는 때(UTC, 2026-11-11T13:00:00 꼴)]

세는 것
  - 도구 호출을 호출 id로 한 번씩만 센다(같은 호출이 기록에 두 번 남는 일이 있다).
  - 파일 읽기 도구(Read)가 연 파일을 확장자로 갈라, 코드 파일만 따로 센다.
  - 명령 실행 도구(Bash)의 호출 하나에는 명령 여럿이 이어져 있다(cd … && grep … | head).
    호출을 명령 하나하나로 쪼개서, 파일 내용을 읽는 명령(cat, grep, sed, head 따위)이 든 호출을 센다.
    그 명령이 코드 확장자 파일을 이름으로 들었는지도 센다.
  - 도구 호출을 모델 이름별로 센다(기록의 응답마다 모델 이름이 적혀 있다).

읽는 명령으로 치는 것과 치지 않는 것
  - 친다: 파이프의 맨 앞에 선 cat, grep, rg, sed, head, tail, less, awk, nl, git diff, git show, git blame.
    `find … | xargs grep`처럼 xargs 뒤에 선 것도 친다.
  - 치지 않는다: 파일에 쓰는 cat(`cat > 파일`, heredoc), 고쳐 쓰는 sed(`sed -i`),
    결과를 파일로 보내는 명령(`grep … > 파일`), 있는지만 묻는 `grep -q`,
    이름과 크기만 보는 ls, find, wc, git log(따로 센다).

세지 못하는 것
  - 읽은 내용이 AI에게 얼마나 갔는지. 뒤에 `| head`나 `| wc -l`이 붙으면 일부나 개수만 간다.
  - 스크립트 안에서 읽은 파일(`python3 -c "open(…)"`), `$( )` 안의 명령.
  - 폴더를 통째로 뒤진 grep이 실제로 연 파일. 읽는 호출로는 세지만 코드 파일을 든 호출로는 세지 못한다.
  - 사람이 직접 연 파일 수, 다른 도구(Codex 등)의 기록.
"""
import collections
import datetime
import glob
import json
import os
import re
import shlex
import statistics
import sys

ROOT = os.path.expanduser("~/.claude/projects")
CODE = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rs", ".c", ".h",
        ".cc", ".cpp", ".hpp", ".cs", ".rb", ".php", ".swift", ".sh", ".sql", ".html", ".css"}
READERS = {"cat", "grep", "egrep", "fgrep", "rg", "sed", "head", "tail", "less", "more", "awk", "nl"}
GIT_READERS = {"diff", "show", "blame"}
GREPS = {"grep", "egrep", "fgrep", "rg"}
QUIET = re.compile(r"^(--quiet|--silent|-[A-Za-z]*q[A-Za-z]*)$")
PATTERN_FIRST = {"grep", "egrep", "fgrep", "rg", "sed", "awk"}   # 첫 인자가 파일이 아니라 검색어나 스크립트인 명령
LISTERS = {"ls", "find", "wc", "tree", "stat", "du"}
GIT_LISTERS = {"log", "status", "ls-files"}
PREFIXES = {"then", "do", "else", "if", "while", "until", "!", "(", "{", "time", "sudo", "command", "exec", "nohup"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def strip_heredocs(cmd):
    """heredoc 본문(<<EOF 와 EOF 사이)을 뺀다. 본문은 명령이 아니라 자료다."""
    out, tag = [], None
    for line in cmd.split("\n"):
        if tag is not None:
            if line.strip() == tag:
                tag = None
            continue
        out.append(line)
        found = HEREDOC.search(line)
        if found:
            tag = found.group(2)
    return "\n".join(out)


def split_commands(cmd):
    """호출 하나를 파이프라인들로, 파이프라인을 단계들로 쪼갠다. 따옴표 안의 ; | & 는 건드리지 않는다."""
    pipelines, stages, buf, quote, i = [], [], [], None, 0
    while i < len(cmd):
        ch, two = cmd[i], cmd[i:i + 2]
        if quote:
            buf.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(cmd):
                buf.append(cmd[i + 1])
                i += 1
            elif ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch == "\\" and i + 1 < len(cmd):
            buf.append(" ")                      # 줄 잇기(\ 뒤 줄바꿈)와 이스케이프는 빈칸으로 본다
            i += 1
        elif two in ("&&", "||") or ch in ";\n":
            stages.append("".join(buf))
            pipelines.append(stages)
            stages, buf = [], []
            i += len(two) - 1 if two in ("&&", "||") else 0
        elif ch == "|":
            stages.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    stages.append("".join(buf))
    pipelines.append(stages)
    return [[s.strip() for s in p if s.strip()] for p in pipelines if any(s.strip() for s in p)]


def words(stage):
    """단계 하나를 낱말로 쪼개고, 앞에 붙은 변수 대입과 셸 예약어를 뗀다."""
    try:
        tokens = shlex.split(stage)
    except ValueError:
        tokens = stage.split()
    while tokens and (ASSIGN.match(tokens[0]) or tokens[0] in PREFIXES):
        tokens = tokens[1:]
    return tokens


def to_file(args):
    """명령의 출력을 파일로 보내는가(> 파일, >> 파일). 2>/dev/null 같은 오류 출력은 치지 않는다."""
    return any(a in (">", ">>") or (a.startswith(">") and not a.startswith(">&")) for a in args)


def classify(stage, first):
    """단계 하나가 하는 일. 반환: ("read" | "list" | None, 그 명령의 인자들)."""
    tokens = words(stage)
    if tokens and tokens[0] == "xargs":                     # find … | xargs grep …
        tokens = [t for t in tokens[1:] if not t.startswith("-")]
        first = True
    if not tokens or not first:
        return None, []
    name, args = os.path.basename(tokens[0]), tokens[1:]
    if name == "git":
        rest, k = [], 0
        while k < len(args):                                 # git -C <폴더> show … 의 폴더는 하위 명령이 아니다
            k += 2 if args[k] in ("-C", "-c", "--git-dir", "--work-tree") else 0
            if k < len(args):
                rest.append(args[k])
            k += 1
        sub = next((a for a in rest if not a.startswith("-")), "")
        if sub in GIT_READERS and not to_file(args):
            return "read", args
        return ("list" if sub in GIT_LISTERS else None), args
    if name in LISTERS:
        return "list", args
    if name not in READERS:
        return None, []
    if name == "cat":
        targets = [a for k, a in enumerate(args)
                   if not a.startswith("-") and not a.startswith(">") and not a.startswith("<")
                   and not (k and args[k - 1] in (">", ">>"))]
        if "<<" in stage or not targets:                    # 파일에 쓰는 cat, 표준 입력을 옮기는 cat
            return None, []
    if name == "sed" and any(a == "--in-place" or (a.startswith("-i") and not a.startswith("--")) for a in args):
        return None, []                                      # 고쳐 쓰는 sed
    if to_file(args) or (name in GREPS and any(QUIET.match(a) for a in args)):
        return None, []                                      # 결과를 파일로 보내거나(> 파일) 있는지만 묻는(grep -q) 명령
    return "read", file_args(name, args)


def file_args(name, args):
    """인자에서 파일 자리가 아닌 것(grep의 검색어, sed와 awk의 스크립트)을 뺀다."""
    if name not in PATTERN_FIRST:
        return args
    out, taken, k = [], False, 0
    while k < len(args):
        a = args[k]
        if a in ("-e", "-f", "--regexp", "--file", "--expression"):
            taken, k = True, k + 2               # 바로 뒤 낱말이 검색어다
        elif a.startswith("-"):
            out.append(a)                        # --include=*.py 같은 옵션 값은 names_code가 본다
            k += 1
        elif not taken:
            taken, k = True, k + 1               # 옵션이 아닌 첫 낱말이 검색어(스크립트)다
        else:
            out.append(a)
            k += 1
    return out


def names_code(args):
    """인자 가운데 코드 확장자 파일(또는 *.py 같은 꼴)이 있는가."""
    for a in args:
        if a.startswith("--") and "=" in a:
            a = a.split("=", 1)[1]
        if os.path.splitext(a.rstrip(":,)"))[1].lower() in CODE:
            return True
    return False


def bash_call(cmd):
    """Bash 호출 하나를 본다. 반환: (든 명령 수, 읽는 명령이 있나, 그것이 코드 파일을 들었나, 목록 명령이 있나)."""
    count, reads, code, lists = 0, False, False, False
    for stages in split_commands(strip_heredocs(cmd)):
        for k, stage in enumerate(stages):
            count += 1
            kind, args = classify(stage, k == 0)
            if kind == "read":
                reads = True
                code = code or names_code(args)
            elif kind == "list":
                lists = True
    return count, reads, code, lists


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    until = (datetime.datetime.strptime(sys.argv[2], "%Y-%m-%dT%H:%M:%S") if len(sys.argv) > 2
             else datetime.datetime.utcnow())
    since = until - datetime.timedelta(days=days)
    lo, hi = since.strftime("%Y-%m-%dT%H:%M:%S"), until.strftime("%Y-%m-%dT%H:%M:%S")

    seen, tools, models = set(), collections.Counter(), collections.Counter()
    read_files, read_calls, code_calls = {}, 0, 0
    sizes, bash_reads, bash_code, bash_lists = [], 0, 0, 0
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
                model = (obj.get("message") or {}).get("model") or "(이름 없음)"
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
                    models[model] += 1
                    if name == "Read":
                        fp = args.get("file_path", "")
                        ext = os.path.splitext(fp)[1].lower()
                        read_calls += 1
                        read_files[fp] = ext
                        if ext in CODE:
                            code_calls += 1
                    elif name == "Bash":
                        count, reads, code, lists = bash_call(args.get("command") or "")
                        sizes.append(count)
                        bash_reads += reads
                        bash_code += code
                        bash_lists += lists and not reads
        record_files += used

    code_files = sum(1 for ext in read_files.values() if ext in CODE)
    total, bash = sum(tools.values()), tools["Bash"]
    print("기간(UTC): %s ~ %s (%d일)" % (lo, hi, days))
    print("도구 호출이 든 기록 파일: %d개, 도구 호출 모두 %d번" % (record_files, total))
    print("명령 실행 도구(Bash) 호출: %d번 (호출 하나에 든 명령의 가운데값 %d개)" % (
        bash, statistics.median(sizes) if sizes else 0))
    print("  파일 내용을 읽는 명령이 든 호출: %d번 (%.1f%%)" % (bash_reads, 100.0 * bash_reads / max(1, bash)))
    print("    그 가운데 코드 파일을 이름으로 든 호출: %d번" % bash_code)
    print("  읽는 명령 없이 이름과 크기만 본 호출(ls, find, wc, git log 따위): %d번" % bash_lists)
    print("파일 읽기 도구(Read): %d번, 서로 다른 파일 %d개" % (read_calls, len(read_files)))
    print("  그 가운데 코드 파일: %d번, 서로 다른 파일 %d개" % (code_calls, code_files))
    print("파일 쓰기(Write): %d번, 파일 고치기(Edit): %d번" % (tools["Write"], tools["Edit"]))
    print("모델별 도구 호출: " + ", ".join("%s %d" % (m, n) for m, n in models.most_common()))
    top = collections.Counter(read_files.values()).most_common(6)
    print("읽기 도구가 연 파일의 확장자 상위: " + ", ".join("%s %d" % (e or "(없음)", n) for e, n in top))


if __name__ == "__main__":
    main()
