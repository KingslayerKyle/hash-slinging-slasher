"""Exercise the submission-validation workflow against local Git histories."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest


def workflow_script():
    workflow = Path(__file__).resolve().parents[1] / ".github/workflows/validate.yml"
    lines = workflow.read_text(encoding="utf-8").splitlines()
    marker = lines.index("        id: changed")
    if lines[marker + 1].strip() != "run: |":
        raise ValueError("the changed-files step must contain a shell block")
    script = []
    for line in lines[marker + 2:]:
        if line and not line.startswith("          "):
            break
        script.append(line)
    return textwrap.dedent("\n".join(script))


def find_bash(git):
    if os.name != "nt":
        return shutil.which("bash")

    # Git may be on PATH through a package-manager shim. Its executable directory and
    # --exec-path both lead back to the installation containing Git Bash.
    locations = [Path(git).resolve()]
    result = subprocess.run(
        [git, "--exec-path"], capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0:
        locations.append(Path(result.stdout.strip()))
    for location in locations:
        for parent in location.parents:
            for relative in ("bin/bash.exe", "usr/bin/bash.exe"):
                candidate = parent / relative
                if candidate.is_file():
                    return str(candidate)
    for variable in ("ProgramFiles", "ProgramFiles(x86)", "LocalAppData"):
        if root := os.environ.get(variable):
            for relative in ("Git/bin/bash.exe", "Programs/Git/bin/bash.exe"):
                candidate = Path(root) / relative
                if candidate.is_file():
                    return str(candidate)
    return None


class SubmissionDiffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.git_executable = shutil.which("git")
        if not cls.git_executable:
            raise unittest.SkipTest("Git is required for local workflow fixtures")
        cls.bash = find_bash(cls.git_executable)
        if not cls.bash:
            raise unittest.SkipTest("Bash (Git Bash on Windows) is unavailable")
        cls.script = workflow_script()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hss-submission-diff-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.environment = os.environ.copy()
        self.environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Workflow regression fixture")
        self.git("config", "user.email", "ci-fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("remote", "add", "origin", ".")
        self.write_submission("base")
        self.initial = self.commit("base")

    def git(self, *arguments):
        result = subprocess.run(
            [self.git_executable, "-C", str(self.root), *arguments],
            env=self.environment, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result.stdout.strip()

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def write_submission(self, batch, contents="1234,example\n"):
        path = self.root / "submissions" / batch / "image.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")

    def run_workflow(self, event, expected, before=""):
        script = self.script.replace("${{ github.event_name }}", event)
        script = script.replace("${{ github.base_ref }}", "main")
        script = script.replace("${{ github.event.before }}", before)
        output = self.root / "output.txt"
        output.write_text("", encoding="utf-8")
        environment = self.environment.copy()
        environment["GITHUB_OUTPUT"] = str(output)
        result = subprocess.run(
            [self.bash, "--noprofile", "--norc", "-e", "-c", script],
            cwd=self.root, env=environment, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        changed = self.root / "changed.txt"
        files = set(changed.read_text(encoding="utf-8").splitlines()) if changed.exists() else set()
        self.assertEqual(files, set(expected))
        self.assertEqual(output.read_text(encoding="utf-8").strip(), "any=true")

    def test_pull_request_uses_merge_base_and_excludes_upstream_changes(self):
        self.git("checkout", "-b", "feature")
        self.write_submission("feature")
        self.commit("feature submission")
        self.git("checkout", "main")
        self.write_submission("base", "4321,upstream_update\n")
        self.write_submission("upstream")
        self.commit("independent upstream changes")
        self.git("checkout", "feature")

        self.run_workflow("pull_request", ["submissions/feature/image.txt"])

    def test_normal_push_validates_its_new_submission(self):
        self.write_submission("push")
        self.commit("new submission")

        self.run_workflow("push", ["submissions/push/image.txt"], self.initial)

    def test_missing_before_validates_every_current_submission(self):
        self.write_submission("push")
        self.commit("new submission")

        self.run_workflow(
            "push", ["submissions/base/image.txt", "submissions/push/image.txt"], "0" * 40,
        )

    def test_unrelated_force_push_compares_trees_without_a_merge_base(self):
        self.git("checkout", "--orphan", "replacement")
        self.git("rm", "-rf", "--", "submissions")
        self.write_submission("replacement")
        self.commit("unrelated replacement history")

        self.run_workflow("push", ["submissions/replacement/image.txt"], self.initial)

    def test_renamed_submission_is_validated_under_its_new_type(self):
        self.git("mv", "submissions/base/image.txt", "submissions/base/material.txt")
        self.commit("change claimed asset type")
        self.assertTrue(self.git("diff", "--name-status", self.initial, "HEAD").startswith("R100"))

        self.run_workflow("push", ["submissions/base/material.txt"], self.initial)


if __name__ == "__main__":
    unittest.main()
