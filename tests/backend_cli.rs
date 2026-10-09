//! Diagnostics must work on a fresh installation, before startup or any search.
use std::process::{Command, Output};

fn run(binary: &str, args: &[&str]) -> Output {
    Command::new(binary)
        .args(args)
        .current_dir(std::env::temp_dir())
        .output()
        .expect("run a freshly built CLI")
}

fn text(output: &Output) -> String {
    format!(
        "{}{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    )
}

const BINARIES: &[&str] = &[
    env!("CARGO_BIN_EXE_confirm_plan"),
    env!("CARGO_BIN_EXE_confirm_cw"),
];

#[test]
fn help_explains_opt_in_without_startup_or_a_gpu() {
    for binary in BINARIES {
        let output = run(binary, &["--help"]);
        assert!(output.status.success(), "{}", text(&output));
        let report = text(&output);
        assert!(report.contains("--backend cpu|auto|cuda"));
        assert!(report.contains("--gpu-check"));
        assert!(!report.contains("panicked"));
    }
}

#[test]
fn invalid_backend_flags_fail_before_readiness_or_search() {
    for binary in BINARIES {
        for args in [
            vec!["--backend", "invalid"],
            vec!["--backend"],
            vec!["--cuda-device", "-1"],
            vec!["--gpu-min-candidates", "0"],
        ] {
            let output = run(binary, &args);
            assert_eq!(output.status.code(), Some(2), "{}", text(&output));
            let report = text(&output);
            assert!(!report.contains("panicked"));
            assert!(!report.contains("fingerprint:"));
        }
    }
}

#[test]
fn unavailable_device_is_a_diagnostic_not_a_crash_or_search() {
    for binary in BINARIES {
        let output = run(binary, &["--gpu-check", "--cuda-device", "2147483647"]);
        assert_eq!(output.status.code(), Some(1), "{}", text(&output));
        let report = text(&output);
        assert!(report.contains("CPU searches remain available"));
        assert!(report.contains("docs/GPU.md"));
        assert!(!report.contains("panicked"));
        assert!(!report.contains("fingerprint:"));
    }
}

#[test]
fn diagnostic_mode_rejects_stray_search_arguments() {
    for binary in BINARIES {
        let output = run(binary, &["--gpu-check", "--unknown-flag"]);
        assert_eq!(output.status.code(), Some(2), "{}", text(&output));
        assert!(text(&output).contains("standalone diagnostic"));
    }
}
