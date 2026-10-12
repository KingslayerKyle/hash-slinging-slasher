//! Stops a search that has stopped finding anything, so a loop nobody is watching cannot spin.
//!
//! `readiness` gates on "is the world current". This gates on "is this still producing", which is
//! the failure that actually wasted a day here.
//!
//! ## What happened
//!
//! On 2026-08-22 an agent wrote a runner that ground a plan in a loop, was told that was the wrong
//! shape, reverted it, and wrote a long commit explaining why a rotation gives away the only
//! advantage this project has. A second loop of its own was already running at the time and was
//! not noticed for **seven and a half hours**. From its fourth round onward, every stage produced
//! **nothing at all** -- ten empty rounds in eight minutes -- while competing for every core with
//! the passes launched beside it and silently ruining their timings.
//!
//! `AGENTS.md` already said not to do this. It said so before the loop was written, and the same
//! session wrote one anyway. **Documentation did not prevent it and there is no reason to expect
//! it to next time**, so the tools stop cooperating instead.
//!
//! ## What this does
//!
//! Every confirming run records whether it added anything. Three consecutive runs that add nothing
//! and the next one refuses to start.
//!
//! That is not a judgement about the method. Finding nothing is a perfectly good outcome -- §3
//! calls a submission of zero worth more than a submission of duplicates -- and one empty pass
//! proves the ground is clear, which is information. What it cannot be is a *habit*: three in a
//! row means whatever is choosing the passes has stopped responding to their results, and that is
//! true whether the thing choosing is a shell loop or a person.
//!
//! ## Why refusing is right rather than warning
//!
//! A warning is read by whoever is at the keyboard, and the case this exists for is precisely the
//! one where nobody is. It has to be the tool that declines.
//!
//! `--anyway` overrides it, and the message says so. Somebody who knows they are grinding a long
//! shot on purpose loses one flag; a loop that nobody is watching loses the night it would have
//! wasted. Any confirmed name resets the count to zero, so a productive grind never sees this.

use std::fs;
use std::path::PathBuf;

/// How many consecutive empty runs before a search declines to start.
///
/// Three, not one. A single empty pass is a normal and useful result -- the method was worth
/// asking and the answer was no. Two can be luck. Three in a row is a loop.
pub const PATIENCE: usize = 3;

/// Below this many candidates, a run that found nothing is a probe and not a lost shift.
///
/// See [`record`] for why the streak cannot be a bare run count. Ten million is two orders of
/// magnitude above the largest derivation `derive_closure.py` runs on a quiet corpus and two
/// orders below the smallest real pass in this repository, which puts the line in the gap between
/// the two things the count has to tell apart.
pub const NOT_A_LOSS: u64 = 10_000_000;

/// The flag that overrides this, shared with `readiness` because they mean the same thing to a
/// caller: *I know, do it anyway*.
pub const OVERRIDE: &str = crate::readiness::OVERRIDE;

fn ledger() -> PathBuf {
    crate::paths::state().join("empty_runs.txt")
}

/// How many confirming runs in a row have added nothing.
pub fn empty_streak() -> usize {
    fs::read_to_string(ledger())
        .ok()
        .and_then(|text| text.trim().parse().ok())
        .unwrap_or(0)
}

/// Records what a run added. Any names at all resets the streak.
///
/// Called after the results are written rather than before, so a run killed halfway through does
/// not count as empty -- it counts as nothing, which is correct: it never finished asking.
///
/// `tested` is how many candidates the run actually asked about, when the tool knows. A run that
/// asked about fewer than [`NOT_A_LOSS`] is a probe, not a pass: it cost seconds, it is *expected*
/// to come back empty, and three of them say nothing about whether whoever is choosing passes is
/// reacting to what they return.
///
/// This exists because `derive_closure.py` was being stopped by its own ledger. Measured
/// 2026-10-12 on a machine whose previous pass had just confirmed 15 names, so the count started at
/// zero: one invocation ran three derivations -- materials from image cores (6.7M candidates),
/// image channel completion (2.9M) and final byte (23.5K) -- each of which added nothing, and then
/// its *fourth* derivation refused to start. Eight of the nine derivations in that round never
/// ran, and the notes said `6 of 7 derivations refused to run this round, so nothing is known to be
/// closed`, which reads like an exhausted corpus and describes a bookkeeping artifact. Every
/// contributor is told to run that script after every pass, so every productive grind ended by
/// locking the machine against the next invented pass -- the one thing §2 says this project is for.
///
/// The floor is deliberately not a wall: the runner that motivated this file ground *full passes*,
/// prefix list times stem list times suffix list, billions of candidates a round and ten empty
/// rounds in eight minutes. Nothing at that scale is disarmed by refusing to count a 23,510-name
/// probe. A tool that cannot say how much it searched passes `None` and is counted as before.
pub fn record(added: usize, tested: Option<u64>) {
    if added > 0 {
        write_ledger(0);
        return;
    }
    if matches!(tested, Some(count) if count < NOT_A_LOSS) {
        return;
    }
    write_ledger(empty_streak() + 1);
}

fn write_ledger(streak: usize) {
    let _ = fs::create_dir_all(crate::paths::state());
    let _ = fs::write(ledger(), streak.to_string());
}

/// Refuses to start when the last `PATIENCE` runs all found nothing.
///
/// Returns quietly otherwise, so this costs a productive grind exactly one file read.
pub fn require() {
    if std::env::args().any(|argument| argument == OVERRIDE) {
        return;
    }

    let streak = empty_streak();
    if streak < PATIENCE {
        return;
    }

    eprintln!(
        "The last {streak} confirming runs on this machine each found nothing.\n\n\
         That is not a complaint about the method -- one empty pass is a real result and worth\n\
         having. Three in a row means whatever is choosing the passes has stopped reacting to what\n\
         they return, and if that is a loop it will keep going all night for nothing. It has\n\
         happened here: a runner ground ten empty rounds in eight minutes while nobody was\n\
         watching, and took every core with it.\n\n\
         The corpus is closed to what is being run. The thing worth doing now is not another pass:\n\n\
         \x20   python scripts/methods_report.py --efficiency    what still pays, and per hour\n\
         \x20   python scripts/seams.py                          relations nothing has mined\n\
         \x20   python scripts/derive_closure.py                 free, and it refills after any gain\n\n\
         Any run that confirms a single name clears this. To search anyway, pass {OVERRIDE}."
    );

    std::process::exit(2);
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The streak has to count *consecutive* empties and reset on any find, or a machine that has
    /// ever been productive could never trip it and a machine that has not could never recover.
    #[test]
    fn a_single_find_clears_the_streak() {
        let ledger = ledger();
        let restore = fs::read_to_string(&ledger).ok();

        // Start from a known streak. `record` counts *on top of* whatever the ledger already
        // holds, so without this the test asserts against the machine's live count and fails on
        // any clone whose last pass happened to find nothing -- which is a normal, correct state
        // for this tool to be in, and was exactly the state on 2026-08-23. Recording a find is
        // the documented way to clear it, so this uses the same path a real run would.
        record(1, None);

        record(0, None);
        record(0, None);
        let after_two = empty_streak();

        record(7, None);
        let after_a_find = empty_streak();

        record(0, None);
        let after_one_more = empty_streak();

        // A probe that asked about less than the floor is not a wasted pass, so it does not move
        // the count at all -- three cheap derivations out of `derive_closure` included.
        record(0, Some(NOT_A_LOSS - 1));
        record(0, Some(1));
        record(0, Some(0));
        let after_probes = empty_streak();

        // At the floor it is a real run and it counts, and so is any tool that cannot say.
        record(0, Some(NOT_A_LOSS));
        let after_a_real_empty = empty_streak();

        // Put the machine's real count back before asserting, so a failure here cannot leave a
        // contributor's tools refusing to run.
        match restore {
            Some(text) => {
                let _ = fs::write(&ledger, text);
            }
            None => {
                let _ = fs::remove_file(&ledger);
            }
        }

        assert_eq!(after_two, 2, "two empty runs in a row is a streak of two");
        assert_eq!(after_a_find, 0, "a find clears it");
        assert_eq!(after_one_more, 1, "and counting starts again from there");
        assert_eq!(after_probes, 1, "cheap empty probes are not wasted passes");
        assert_eq!(
            after_a_real_empty, 2,
            "but a run at the floor is a real pass, and the guard still sees it"
        );
        assert!(PATIENCE > 1, "one empty pass is a result, not a fault");
    }
}
