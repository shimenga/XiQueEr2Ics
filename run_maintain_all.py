#!/usr/bin/env python3
"""
自动运行 schools/ 下所有学校的 maintain.py（校历同步脚本）。

用途：
    每个学期开始前运行一次，批量刷新所有学校的 school_calendar.json。
    这些脚本访问的是公开的校历接口，不需要任何账号密码。

用法：
    python3 run_maintain_all.py
    python3 run_maintain_all.py --only 12623    # 只跑指定学校

退出码：
    0 = 全部成功
    1 = 有学校失败
"""
import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHOOLS_DIR = os.path.join(SCRIPT_DIR, "schools")


def find_school_dirs(only: str | None = None) -> list[str]:
    """找出所有包含 maintain.py 的学校目录"""
    if not os.path.isdir(SCHOOLS_DIR):
        print(f"[错误] 找不到 schools 目录: {SCHOOLS_DIR}")
        sys.exit(1)

    dirs = []
    for name in sorted(os.listdir(SCHOOLS_DIR)):
        full = os.path.join(SCHOOLS_DIR, name)
        maintain_py = os.path.join(full, "maintain.py")
        if os.path.isdir(full) and os.path.isfile(maintain_py):
            dirs.append(name)

    if only:
        if only not in dirs:
            print(f"[错误] 学校 {only} 不存在或没有 maintain.py")
            sys.exit(1)
        dirs = [only]
    return dirs


def run_all(only: str | None = None) -> int:
    school_dirs = find_school_dirs(only)
    if not school_dirs:
        print("[错误] 没有任何学校目录包含 maintain.py")
        return 1

    print(f"发现 {len(school_dirs)} 个学校: {', '.join(school_dirs)}")

    # 优先使用项目 venv 的 python，其次系统 python
    venv_python = os.path.join(SCRIPT_DIR, ".venv", "bin", "python")
    python_bin = venv_python if os.path.isfile(venv_python) else sys.executable

    failed = []
    for school in school_dirs:
        school_dir = os.path.join(SCHOOLS_DIR, school)
        print(f"\n=== 正在同步学校 {school} ===")
        try:
            result = subprocess.run(
                [python_bin, "maintain.py"],
                cwd=school_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            if result.returncode != 0:
                print(f"[失败] 学校 {school} maintain.py 退出码 {result.returncode}")
                failed.append(school)
            else:
                print(f"[成功] 学校 {school} 校历已更新")
        except subprocess.TimeoutExpired:
            print(f"[失败] 学校 {school} maintain.py 超时(300s)")
            failed.append(school)
        except Exception as e:
            print(f"[失败] 学校 {school} 运行出错: {e}")
            failed.append(school)

    print("\n" + "=" * 40)
    if failed:
        print(f"完成，但有失败: {', '.join(failed)}")
        return 1
    print("全部学校校历同步成功 ✅")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量同步所有学校的校历")
    parser.add_argument("--only", help="只同步指定学校代码")
    args = parser.parse_args()
    sys.exit(run_all(args.only))