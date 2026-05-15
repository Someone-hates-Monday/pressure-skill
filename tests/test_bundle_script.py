import json
import os
import subprocess
import sys
from pathlib import Path


def test_bundle_local_script_smoke():
    root = Path(__file__).resolve().parent.parent
    script = root / "scripts" / "bundle_local.py"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--relation",
            "manager",
            "--use-llm",
            "false",
            "--situation",
            "今天必须交",
            "--user-purpose",
            "先稳住对方",
            "--user-leverage",
            "手里还有别的项目优先级更高",
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert "deflect" in data
    assert "readiness" in data
    assert "warnings" in data["readiness"]
    assert "portrait_depth" in data["readiness"]
    assert "收到" in proc.stdout or "收到" in json.dumps(data, ensure_ascii=False)
