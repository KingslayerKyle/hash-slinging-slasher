"""Overnight high-yield autonomous recovery suite across Black Ops 4 and Cold War.

Designed for unattended execution (~8 hours):
- Alternates titles (BLKOPS04 and BLKOPSCW) to advance both active games.
- Periodic preflight refresh every 2 hours (refreshes cod-name-db tables and open PR claims).
- Prioritizes measured high-yield methods based on historical recovery logs:
    1. Black Ops 4 SAB sound all-boundary cores x uncarried endings (largest pool opportunity: 70k+ unnamed)
    2. All-boundary sound uncarried endings (segments 2, 1, 3) across both titles
    3. All-boundary general uncarried endings (segments 2, 3, 1, 4) across both titles
    4. Confirmed-only all-boundary cores (cores existing strictly in confirmed/merged findings)
    5. Mined axes, equivalence classes, and indels (mined_axes)
    6. Sound final byte solved backwards (with game-correct backslashes on BO4)
    7. Multi-core tails (lengths 4 and 5)
- Automatically triggers derive_closure and community submit.exe after every finding.
"""

import datetime
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

LOG_FILE = ROOT / "logs" / "overnight_suite.log"


def log(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Error writing to log: {e}", file=sys.stderr)


def run_cmd(cmd, cwd=ROOT, check=False, timeout=None):
    log(f"Executing: {' '.join(str(c) for c in cmd)}")
    try:
        res = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
        for out_line in lines[-20:]:
            log(f"  > {out_line}")
        return res.returncode, res.stdout
    except Exception as e:
        log(f"Command error: {e}")
        return -1, str(e)


def run_pipeline(producer_cmd, consumer_cmd, cwd=ROOT, timeout=7200):
    log(f"Pipeline: {' '.join(str(c) for c in producer_cmd)} | {' '.join(str(c) for c in consumer_cmd)}")
    try:
        p1 = subprocess.Popen(producer_cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(
            consumer_cmd,
            cwd=str(cwd),
            stdin=p1.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        p1.stdout.close()
        stdout, _ = p2.communicate(timeout=timeout)
        p1.wait(timeout=30)
        lines = [ln for ln in stdout.splitlines() if ln.strip()]
        for out_line in lines[-20:]:
            log(f"  > {out_line}")
        return p2.returncode, stdout
    except Exception as e:
        log(f"Pipeline error: {e}")
        return -1, str(e)


def post_pass_actions(game: str = None):
    """Run derive_closure and submit immediately after any finding."""
    log("Running post-pass derivation closure...")
    closure_cmd = [sys.executable, str(ROOT / "scripts" / "derive_closure.py")]
    if game:
        closure_cmd.extend(["--game", game])
    run_cmd(closure_cmd, timeout=900)

    log("Submitting findings to community...")
    submit_bin = ROOT / "bin" / "windows" / "submit.exe"
    if submit_bin.exists():
        run_cmd([str(submit_bin)], timeout=300)


def preflight_sync():
    """Run start.exe to refresh hash tables, survey open PRs, and renew lease."""
    start_bin = ROOT / "bin" / "windows" / "start.exe"
    if start_bin.exists():
        log("Running preflight sync & table refresh...")
        run_cmd([str(start_bin)], timeout=300)


# =========================================================================
# JOB DEFINITIONS
# =========================================================================

def job_bo4_sound_allboundary(segments: int = 2, top: int = 60000):
    """Target the largest single unrecovered pool: BO4 sound_asset (70k+ unnamed, unfolded)."""
    log(f"--- [JOB] BO4 SAB Sound All-boundary: Segments={segments}, Top={top} ---")
    script = ROOT / "scripts" / "contributed" / "bo4_sound_allboundary_20260823-151952.py"
    plan_file = ROOT / "plans" / "bo4_sab_allboundary.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    if not script.exists() or not confirm_bin.exists():
        return

    code, _ = run_cmd([sys.executable, str(script), "--segments", str(segments), "--top", str(top)], timeout=600)
    if code == 0 and plan_file.exists():
        code2, out = run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                "BLKOPS04",
                "--no-fold",
                "--anyway",
                "--label",
                f"bo4 sound asset allboundary cores x uncarried {segments}-segment endings",
                "--script",
                "scripts/contributed/bo4_sound_allboundary_20260823-151952.py",
            ],
            timeout=7200,
        )
        if "this run added 0" not in out and "this run added" in out:
            post_pass_actions("BLKOPS04")


def job_allboundary_sound(game: str, segments: int, top: int = 60000):
    """All-boundary sound pass (highest single yield in past runs: 170+ names per pass)."""
    log(f"--- [JOB] All-boundary Sound: Game={game}, Segments={segments}, Top={top} ---")
    script = ROOT / "scripts" / "contributed" / "uncarried_endings_allboundary_20260823-134935.py"
    plan_file = ROOT / "plans" / "ab_sound_uncarried.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    if not script.exists() or not confirm_bin.exists():
        return

    code, _ = run_cmd([sys.executable, str(script), "--sound-pass", "--segments", str(segments), "--top", str(top)], timeout=600)
    if code == 0 and plan_file.exists():
        flags = [
            str(confirm_bin),
            str(plan_file),
            "--game",
            game,
            "--anyway",
            "--label",
            f"sound, uncarried {segments}-segment endings over all-boundary cores",
            "--script",
            "scripts/contributed/uncarried_endings_allboundary_20260823-134935.py",
        ]
        if game == "BLKOPS04":
            flags.append("--no-fold")
        code2, out = run_cmd(flags, timeout=7200)
        if "this run added 0" not in out and "this run added" in out:
            post_pass_actions(game)


def job_allboundary_general(game: str, segments: int, top: int = 100000):
    """All-boundary general pass (non-sound models, materials, images, anims)."""
    log(f"--- [JOB] All-boundary General: Game={game}, Segments={segments}, Top={top} ---")
    script = ROOT / "scripts" / "contributed" / "uncarried_endings_allboundary_20260823-134935.py"
    plan_file = ROOT / "plans" / "ab_uncarried.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    if not script.exists() or not confirm_bin.exists():
        return

    code, _ = run_cmd([sys.executable, str(script), "--segments", str(segments), "--top", str(top)], timeout=600)
    if code == 0 and plan_file.exists():
        code2, out = run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                game,
                "--anyway",
                "--label",
                f"uncarried {segments}-segment endings over all-boundary cores",
                "--script",
                "scripts/contributed/uncarried_endings_allboundary_20260823-134935.py",
            ],
            timeout=7200,
        )
        if "this run added 0" not in out and "this run added" in out:
            post_pass_actions(game)


def job_allboundary_confirmed_only(game: str, sound: bool = False, segments: int = 2, top: int = 60000):
    """Cores that exist strictly in findings/ and merged submissions, never tested in initial sweeps."""
    kind = "Sound" if sound else "General"
    log(f"--- [JOB] All-boundary Confirmed-Only ({kind}): Game={game}, Segments={segments} ---")
    script = ROOT / "scripts" / "contributed" / "uncarried_endings_allboundary_20260823-134935.py"
    plan_file = ROOT / "plans" / ("ab_sound_uncarried.txt" if sound else "ab_uncarried.txt")
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    if not script.exists() or not confirm_bin.exists():
        return

    args = [sys.executable, str(script), "--confirmed-only", "--segments", str(segments), "--top", str(top)]
    if sound:
        args.append("--sound-pass")

    code, _ = run_cmd(args, timeout=600)
    if code == 0 and plan_file.exists():
        label = f"confirmed-only {'sound ' if sound else ''}all-boundary cores x uncarried {segments}-segment endings"
        flags = [
            str(confirm_bin),
            str(plan_file),
            "--game",
            game,
            "--anyway",
            "--label",
            label,
            "--script",
            "scripts/contributed/uncarried_endings_allboundary_20260823-134935.py",
        ]
        if sound and game == "BLKOPS04":
            flags.append("--no-fold")
        code2, out = run_cmd(flags, timeout=7200)
        if "this run added 0" not in out and "this run added" in out:
            post_pass_actions(game)


def job_mined_axes(game: str, top: int = 400, classes: bool = False, indels: bool = False):
    """Corpus-mined substitutions, equivalence classes, and indels."""
    log(f"--- [JOB] Mined Axes: Game={game}, Top={top}, Classes={classes}, Indels={indels} ---")
    script = ROOT / "scripts" / "contributed" / "mined_axes_20260825-113712.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    if classes:
        prod.append("--classes")
    elif indels:
        prod.append("--indels")
    else:
        prod.extend(["--top", str(top)])

    label = "corpus-mined substitutions"
    if classes:
        label += " (equivalence classes)"
    elif indels:
        label += " (indels)"
    else:
        label += f" (top {top})"

    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        label,
        "--script",
        "scripts/contributed/mined_axes_20260825-113712.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=2400)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions(game)


def job_sound_final_byte(game: str):
    """Sound-specific backwards final-byte solve with game-correct backslashes."""
    log(f"--- [JOB] Sound Final Byte: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "sound_final_byte_20260825-043818.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script), "--game", game]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "sound final byte solved backwards",
        "--script",
        "scripts/contributed/sound_final_byte_20260825-043818.py",
    ]
    if game == "BLKOPS04":
        cons.append("--no-fold")
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions(game)


def job_tails(game: str, length: int = 4):
    """Full-space tails generator."""
    log(f"--- [JOB] Tails: Game={game}, Length={length} ---")
    script = ROOT / "scripts" / "tails.py"
    plan_file = ROOT / "plans" / f"tails{length}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"
    if not script.exists() or not confirm_bin.exists():
        return

    code, _ = run_cmd([sys.executable, str(script), "--length", str(length), "--write-plan", str(plan_file)], timeout=600)
    if code == 0 and plan_file.exists():
        code2, out = run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                game,
                "--anyway",
                "--label",
                f"tails of length {length}",
            ],
            timeout=7200,
        )
        if "this run added 0" not in out and "this run added" in out:
            post_pass_actions(game)


def job_measured_shells(game: str, head: int = 6, tail: int = 6, top: int = 800):
    """Head 6 + Tail 6 cross-products."""
    log(f"--- [JOB] Measured Shells: Game={game}, Head={head}, Tail={tail}, Top={top} ---")
    script = ROOT / "scripts" / "contributed" / "measured_shells_20260825-045514.py"
    plan_file = ROOT / "plans" / f"shell_h{head}t{tail}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"
    if not script.exists() or not confirm_bin.exists():
        return

    code, _ = run_cmd([sys.executable, str(script), "--head", str(head), "--tail", str(tail), "--top", str(top)], timeout=600)
    if code == 0 and plan_file.exists():
        code2, out = run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                game,
                "--anyway",
                "--label",
                f"measured shells, head {head} tail {tail}, top {top}",
                "--script",
                "scripts/contributed/measured_shells_20260825-045514.py",
            ],
            timeout=7200,
        )
        if "this run added 0" not in out and "this run added" in out:
            post_pass_actions(game)


# =========================================================================
# MAIN ORCHESTRATION LOOP (8 HOURS)
# =========================================================================

def main():
    log("=== STARTING 8-HOUR AUTONOMOUS RECOVERY SUITE ===")
    start_time = time.time()
    max_duration_sec = 8 * 3600  # 8 hours

    # 1. Initial preflight sync & readiness refresh
    preflight_sync()
    post_pass_actions()

    iteration = 1
    last_preflight_time = time.time()

    while time.time() - start_time < max_duration_sec:
        elapsed = time.time() - start_time
        remaining = max(0, max_duration_sec - elapsed)
        log(f"================ ROUND {iteration} (Elapsed: {elapsed/3600:.2f}h, Remaining: {remaining/3600:.2f}h) ================")

        # Periodically refresh preflight every 2 hours to avoid 12-hr readiness expiration
        if time.time() - last_preflight_time > 7200:
            preflight_sync()
            last_preflight_time = time.time()

        # -------------------------------------------------------------
        # 1. Black Ops 4 SAB Sound All-boundary (Targeting 70k Unnamed Pool)
        # -------------------------------------------------------------
        if time.time() - start_time >= max_duration_sec:
            break
        for seg in [2, 1, 3]:
            job_bo4_sound_allboundary(segments=seg, top=60000)
            if time.time() - start_time >= max_duration_sec:
                break

        # -------------------------------------------------------------
        # 2. Sound-Specific Backwards Final-Byte Solve
        # -------------------------------------------------------------
        if time.time() - start_time >= max_duration_sec:
            break
        job_sound_final_byte("BLKOPS04")
        job_sound_final_byte("BLKOPSCW")

        # -------------------------------------------------------------
        # 3. All-Boundary Sound Uncarried Endings (Highest Past Yield)
        # -------------------------------------------------------------
        if time.time() - start_time >= max_duration_sec:
            break
        for seg in [2, 1, 3]:
            job_allboundary_sound("BLKOPSCW", segments=seg, top=60000)
            job_allboundary_sound("BLKOPS04", segments=seg, top=60000)
            if time.time() - start_time >= max_duration_sec:
                break

        # -------------------------------------------------------------
        # 4. All-Boundary General Uncarried Endings (High Non-Sound Yield)
        # -------------------------------------------------------------
        if time.time() - start_time >= max_duration_sec:
            break
        for seg in [2, 3, 1, 4]:
            job_allboundary_general("BLKOPSCW", segments=seg, top=100000)
            job_allboundary_general("BLKOPS04", segments=seg, top=100000)
            if time.time() - start_time >= max_duration_sec:
                break

        # -------------------------------------------------------------
        # 5. Confirmed-Only All-Boundary Cores (Unpublished Recovered Cores)
        # -------------------------------------------------------------
        if time.time() - start_time >= max_duration_sec:
            break
        job_allboundary_confirmed_only("BLKOPSCW", sound=True, segments=2, top=60000)
        job_allboundary_confirmed_only("BLKOPS04", sound=True, segments=2, top=60000)
        job_allboundary_confirmed_only("BLKOPSCW", sound=False, segments=2, top=100000)
        job_allboundary_confirmed_only("BLKOPS04", sound=False, segments=2, top=100000)

        # -------------------------------------------------------------
        # 6. Mined Axes, Equivalence Classes & Indels
        # -------------------------------------------------------------
        if time.time() - start_time >= max_duration_sec:
            break
        job_mined_axes("BLKOPSCW", top=400)
        job_mined_axes("BLKOPS04", top=400)
        job_mined_axes("BLKOPSCW", top=800)
        job_mined_axes("BLKOPS04", top=800)
        job_mined_axes("BLKOPSCW", classes=True)
        job_mined_axes("BLKOPS04", classes=True)
        job_mined_axes("BLKOPSCW", indels=True)
        job_mined_axes("BLKOPS04", indels=True)

        # -------------------------------------------------------------
        # 7. Measured Shells (Head 6 + Tail 6 Cross Products)
        # -------------------------------------------------------------
        if time.time() - start_time >= max_duration_sec:
            break
        job_measured_shells("BLKOPSCW", head=6, tail=6, top=800)
        job_measured_shells("BLKOPS04", head=6, tail=6, top=800)

        # -------------------------------------------------------------
        # 8. Tails Generator (Length 4)
        # -------------------------------------------------------------
        if time.time() - start_time >= max_duration_sec:
            break
        job_tails("BLKOPSCW", length=4)
        job_tails("BLKOPS04", length=4)

        iteration += 1

    log("=== OVERNIGHT SUITE COMPLETED (8 HOURS) ===")
    post_pass_actions()


if __name__ == "__main__":
    main()
