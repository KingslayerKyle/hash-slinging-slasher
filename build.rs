use std::env;
#[cfg(windows)]
use std::ffi::OsString;
use std::path::{Path, PathBuf};
use std::process::Command;

fn find_on_path(name: &str) -> Option<PathBuf> {
    env::split_paths(&env::var_os("PATH")?)
        .map(|p| p.join(name))
        .find(|p| p.is_file())
}

fn fail(message: &str) -> ! {
    eprintln!("CUDA feature build failed: {message}\n\
        CPU builds need no CUDA: omit --features cuda. Before installing anything, confirm that the computer running GPU searches has a supported NVIDIA GPU (compute capability 7.5+): https://developer.nvidia.com/cuda-gpus\n\
        Only then, to build this optional feature, use a compatible NVIDIA CUDA Toolkit and its supported C++ host compiler.\n\
        Toolkit: https://developer.nvidia.com/cuda-downloads\n\
        Windows compiler/setup: https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/\n\
        Linux compiler/setup: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/\n\
        Nothing is installed automatically. A built CUDA-enabled binary uses the static runtime; running it needs a compatible NVIDIA driver, not the Toolkit.");
    std::process::exit(1)
}

// Cargo's MSVC linker discovery does not necessarily initialize cl.exe's INCLUDE/LIB.
// Reuse an existing developer shell, or read the installed VS developer environment.
#[cfg(windows)]
fn msvc_environment() -> Vec<(OsString, OsString)> {
    if env::var_os("VSCMD_VER").is_some() {
        return Vec::new();
    }
    let vswhere = env::var_os("ProgramFiles(x86)")
        .map(PathBuf::from)
        .map(|p| p.join("Microsoft Visual Studio/Installer/vswhere.exe"))
        .filter(|p| p.is_file())
        .or_else(|| find_on_path("vswhere.exe"))
        .unwrap_or_else(|| fail("MSVC developer environment was not found. Run Cargo from an x64 Native Tools developer shell."));
    let mut installation = String::new();
    for version in [Some("[17.0,18.0)"), None] {
        let mut command = Command::new(&vswhere);
        command.args([
            "-latest",
            "-products",
            "*",
            "-requires",
            "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "-property",
            "installationPath",
        ]);
        if let Some(version) = version {
            command.args(["-version", version]);
        }
        if let Ok(output) = command.output() {
            if output.status.success() {
                installation = String::from_utf8_lossy(&output.stdout).trim().to_owned();
                if !installation.is_empty() {
                    break;
                }
            }
        }
    }
    let script = Path::new(&installation).join("VC/Auxiliary/Build/vcvars64.bat");
    if installation.is_empty() || !script.is_file() {
        fail("The installed Visual Studio C++ x64 build tools could not be located.");
    }
    let mut command = Command::new("cmd.exe");
    use std::os::windows::process::CommandExt;
    command.raw_arg(format!("/d /s /c \"\"{}\" >nul && set\"", script.display()));
    let output = command
        .output()
        .unwrap_or_else(|e| fail(&format!("Cannot initialize the installed MSVC tools: {e}")));
    if !output.status.success() {
        fail("MSVC developer environment initialization failed.");
    }
    String::from_utf8_lossy(&output.stdout)
        .lines()
        .filter_map(|line| line.split_once('='))
        .filter(|(key, _)| !key.is_empty())
        .map(|(key, value)| (OsString::from(key), OsString::from(value)))
        .collect()
}

fn main() {
    println!("cargo:rerun-if-changed=src/cuda/backend.cu");
    println!("cargo:rerun-if-changed=src/cuda/backend.h");
    for key in [
        "NVCC",
        "CUDA_PATH",
        "CUDA_HOME",
        "SLASHER_CUDA_ARCH",
        "CXX",
        "CUDAHOSTCXX",
    ] {
        println!("cargo:rerun-if-env-changed={key}");
    }
    if env::var_os("CARGO_FEATURE_CUDA").is_none() {
        return;
    }
    let os = env::var("CARGO_CFG_TARGET_OS").unwrap_or_default();
    if !matches!(os.as_str(), "windows" | "linux")
        || env::var("CARGO_CFG_TARGET_POINTER_WIDTH").as_deref() != Ok("64")
    {
        fail("This optional CUDA backend supports 64-bit Windows and Linux. Use the default CPU build on other targets.");
    }
    if env::var("HOST") != env::var("TARGET") {
        fail("Cross-compiling the CUDA feature is not supported; use a native build or the CPU feature set.");
    }
    if os == "windows" && env::var("CARGO_CFG_TARGET_ENV").as_deref() != Ok("msvc") {
        fail("Windows CUDA builds require the MSVC Rust target.");
    }
    let sdk = env::var_os("CUDA_PATH")
        .or_else(|| env::var_os("CUDA_HOME"))
        .map(PathBuf::from);
    let executable = if os == "windows" { "nvcc.exe" } else { "nvcc" };
    let nvcc = env::var_os("NVCC").map(PathBuf::from)
        .or_else(|| sdk.as_ref().map(|p| p.join("bin").join(executable)).filter(|p| p.is_file()))
        .or_else(|| find_on_path(executable))
        .unwrap_or_else(|| fail("nvcc was not found. Set CUDA_PATH/CUDA_HOME to an installed Toolkit or NVCC to its compiler executable."));
    let resolved_nvcc = if nvcc.components().count() == 1 {
        find_on_path(nvcc.to_str().unwrap_or(executable)).unwrap_or(nvcc)
    } else {
        nvcc
    };
    // Resolve an nvcc symlink before inferring /usr/local/cuda (or an SDK install).
    let inferred_nvcc = resolved_nvcc
        .canonicalize()
        .unwrap_or_else(|_| resolved_nvcc.clone());
    let sdk = sdk
        .or_else(|| inferred_nvcc.parent()?.parent().map(Path::to_path_buf))
        .unwrap_or_else(|| fail("Cannot determine CUDA Toolkit root; set CUDA_PATH or CUDA_HOME."));
    let library_name = if os == "windows" {
        "cudart_static.lib"
    } else {
        "libcudart_static.a"
    };
    let architecture = env::var("CARGO_CFG_TARGET_ARCH").unwrap_or_default();
    let candidates = if os == "windows" {
        vec![sdk.join("lib/x64")]
    } else {
        vec![
            sdk.join("lib64"),
            sdk.join(format!("targets/{architecture}-linux/lib")),
            sdk.join("targets/sbsa-linux/lib"),
            sdk.join(format!("lib/{architecture}-linux-gnu")),
            PathBuf::from(format!("/usr/lib/{architecture}-linux-gnu")),
        ]
    };
    let library = candidates
        .into_iter()
        .find(|p| p.join(library_name).is_file())
        .unwrap_or_else(|| {
            fail(
                "The Toolkit static CUDA runtime library was not found; check CUDA_PATH/CUDA_HOME.",
            )
        });
    let out = PathBuf::from(env::var_os("OUT_DIR").unwrap());
    let output = out.join(if os == "windows" {
        "slasher_cuda.lib"
    } else {
        "libslasher_cuda.a"
    });
    let mut command = Command::new(&resolved_nvcc);
    command.args(["--lib", "-O3", "-std=c++17", "--cudart=static"]);
    if let Some(arch) = env::var_os("SLASHER_CUDA_ARCH") {
        let arch = arch.to_string_lossy();
        if arch.is_empty()
            || !arch.bytes().all(|b| b.is_ascii_digit())
            || arch.parse::<u32>().unwrap_or(0) < 75
        {
            fail("SLASHER_CUDA_ARCH must be a numeric compute capability at least 75, for example 120 for Blackwell.");
        }
        command.arg(format!(
            "-gencode=arch=compute_{arch},code=[sm_{arch},compute_{arch}]"
        ));
    } else {
        // A Toolkit can emit newer PTX than an otherwise compatible installed driver
        // can JIT. Bundle every generic SASS architecture that this nvcc supports;
        // retain baseline PTX for later devices, whose compatibility the probe tests.
        let supported = Command::new(&resolved_nvcc)
            .arg("--list-gpu-code")
            .output()
            .unwrap_or_else(|e| {
                fail(&format!(
                    "Cannot query nvcc's supported GPU architectures: {e}"
                ))
            });
        if !supported.status.success() {
            fail("nvcc --list-gpu-code failed. Use a Toolkit supporting that query or set SLASHER_CUDA_ARCH to an explicit supported architecture.");
        }
        let architectures: std::collections::BTreeSet<u32> =
            String::from_utf8_lossy(&supported.stdout)
                .lines()
                .filter_map(|line| line.trim().strip_prefix("sm_"))
                .filter(|text| !text.is_empty() && text.bytes().all(|b| b.is_ascii_digit()))
                .filter_map(|text| text.parse::<u32>().ok())
                .filter(|&arch| arch >= 75)
                .collect();
        if architectures.is_empty() {
            fail("nvcc reports no generic compute capability 7.5+ target. Use a compatible Toolkit or the CPU build.");
        }
        for arch in architectures {
            command.arg(format!("-gencode=arch=compute_{arch},code=sm_{arch}"));
        }
        command.arg("-gencode=arch=compute_75,code=compute_75");
    }
    if os == "windows" {
        #[cfg(windows)]
        command
            .envs(msvc_environment())
            .args(["-Xcompiler", "/MD,/EHsc"]);
        #[cfg(not(windows))]
        fail("Windows CUDA compilation requires a native Windows host.");
    } else {
        command.args(["-Xcompiler", "-fPIC"]);
    }
    if let Some(host) = env::var_os("CUDAHOSTCXX").or_else(|| env::var_os("CXX")) {
        command.arg("-ccbin").arg(host);
    }
    let status = command
        .arg("src/cuda/backend.cu")
        .arg("-o")
        .arg(&output)
        .status()
        .unwrap_or_else(|e| fail(&format!("Cannot run nvcc: {e}")));
    if !status.success() {
        fail("nvcc rejected the backend. Check the compiler diagnostic above and the Toolkit's supported host compiler/driver versions.");
    }
    println!("cargo:rustc-link-search=native={}", out.display());
    println!("cargo:rustc-link-search=native={}", library.display());
    println!("cargo:rustc-link-lib=static=slasher_cuda");
    println!("cargo:rustc-link-lib=static=cudart_static");
    if os == "linux" {
        for lib in ["stdc++", "dl", "rt", "pthread"] {
            println!("cargo:rustc-link-lib={lib}");
        }
    }
}
