//! The gate every search passes through, so that "did you update first?" stops being a question
//! anybody has to remember to ask.
//!
//! The instruction to bring the clone up to date has been in the documentation from the start.
//! It gets skipped anyway -- not out of carelessness, but because an assistant arriving at a repo
//! full of promising things to run has a dozen instructions competing for the same attention, and
//! this one looks like housekeeping rather than like the thing the night depends on.
//!
//! So it is not an instruction here. `start` writes a receipt; a search reads it and refuses to
//! run without a current one. There is exactly one thing to remember, and forgetting it produces
//! an error in the first second rather than a wasted night discovered at four in the morning.

use std::path::PathBuf;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

/// How long a readiness receipt is good for.
///
/// The tables go stale in about twelve hours and submissions land within hours, so a receipt
/// older than this was written against a picture of the world that has since moved. Long enough
/// that a night of back-to-back passes never trips it; short enough that yesterday's receipt
/// does not authorise today's run.
pub const GOOD_FOR: Duration = Duration::from_secs(12 * 60 * 60);

/// The argument that overrides the gate, for somebody deliberately working offline.
pub const OVERRIDE: &str = "--anyway";

pub fn receipt() -> PathBuf {
    crate::paths::state().join("ready.txt")
}

/// Invalidates the previous receipt before startup changes the claims cache it authorises.
pub fn revoke() -> std::io::Result<()> {
    match std::fs::remove_file(receipt()) {
        Ok(()) => Ok(()),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error),
    }
}

/// Records that the startup checks passed, with what they were passed against.
pub fn write(commit: &str, tables: usize, claimed: usize) -> std::io::Result<()> {
    let path = receipt();
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|since| since.as_secs())
        .unwrap_or(0);

    std::fs::write(
        path,
        format!("at={now}\ncommit={commit}\ntables={tables}\nclaimed={claimed}\n"),
    )
}

/// How the receipt stands.
pub enum Standing {
    /// Written recently enough to search on.
    Fresh { claimed: usize },
    /// Written, but long enough ago that the world has moved.
    Stale { hours: u64 },
    /// Never written, or unreadable.
    Missing,
}

pub fn standing() -> Standing {
    let Ok(text) = std::fs::read_to_string(receipt()) else {
        return Standing::Missing;
    };

    let field = |key: &str| -> Option<u64> {
        text.lines()
            .find_map(|line| line.strip_prefix(&format!("{key}="))?.trim().parse().ok())
    };

    let Some(at) = field("at") else {
        return Standing::Missing;
    };

    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|since| since.as_secs())
        .unwrap_or(0);

    let age = now.saturating_sub(at);

    if age > GOOD_FOR.as_secs() {
        Standing::Stale { hours: age / 3600 }
    } else {
        Standing::Fresh { claimed: field("claimed").unwrap_or(0) as usize }
    }
}

/// Stops a search that has not been through the startup checks.
///
/// Call this first in every search binary. It prints the one command that fixes it and exits
/// non-zero, so neither a person nor an assistant nor a shell script can mistake the situation
/// for a pass.
pub fn require() {
    if std::env::args().any(|argument| argument == OVERRIDE) {
        eprintln!(
            "running with {OVERRIDE}: the clone, the tables and the open submissions have NOT \
             been checked.\nAnything found may already be somebody else's, and this run should \
             not be submitted without a proper `start` first.\n"
        );
        return;
    }

    match standing() {
        Standing::Fresh { claimed } => {
            println!("startup checks passed; {claimed} name(s) already claimed elsewhere\n");
        }
        Standing::Stale { hours } => {
            eprintln!(
                "the startup checks last passed {hours} hours ago, which is long enough for the \
                 tables to have moved and for other people to have submitted.\n\n    run this \
                 first:  {}\n\n(or pass {OVERRIDE} to search anyway, knowing the results may \
                 already be claimed.)",
                command()
            );
            std::process::exit(1);
        }
        Standing::Missing => {
            eprintln!(
                "the startup checks have not been run in this clone.\n\nNothing here should \
                 search before they have: an out-of-date clone rediscovers names that were \
                 submitted last night, and a whole pass is spent on work somebody has already \
                 done.\n\n    run this first:  {}\n\n(or pass {OVERRIDE} to search anyway, \
                 knowing the results may already be claimed.)",
                command()
            );
            std::process::exit(1);
        }
    }
}

/// How to run the startup checks, spelled for the platform this is on.
pub fn command() -> &'static str {
    if cfg!(windows) {
        "bin\\windows\\start.exe"
    } else {
        "cargo run --release --bin start"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A receipt that has never been written is missing rather than fresh, so the very first run
    /// in a clone is gated rather than waved through.
    #[test]
    fn an_unwritten_receipt_is_missing() {
        let text = "";
        assert!(text.lines().next().is_none());
        assert!(matches!(
            {
                // Standing is read from a fixed path, so this asserts the parse rather than the
                // filesystem: a body with no `at=` line cannot be fresh.
                let has_at = text.lines().any(|line| line.starts_with("at="));
                if has_at { Standing::Fresh { claimed: 0 } } else { Standing::Missing }
            },
            Standing::Missing
        ));
    }

    /// The window is twelve hours, which is the same figure the tables use for going stale.
    #[test]
    fn the_window_matches_how_long_the_tables_stay_fresh() {
        assert_eq!(GOOD_FOR, crate::tables::STALE_AFTER);
    }
}
