#########################################################################################
#region LOCAL LIBRARIES CHECK AND INSTALLER

import importlib
import importlib.util
import subprocess
import sys
from pathlib import Path


# ==========================================================
# PROJECT ROOT DIRECTORY
# This file must be located at the same level as Main_*.py
# ==========================================================
ROOT = Path(__file__).resolve().parent


# ==========================================================
# LOCAL LIBRARIES
#
# Key      = Python import name
# package  = distribution name from pyproject.toml
# path     = local library project directory
# ==========================================================
LOCAL_LIBRARIES = {
    "Common": {
        "package": "Common-Library",
        "path": ROOT / "Classes" / "Common_Library",
    },

    "Simulator_HFM": {
        "package": "HFM-Simulator",
        "path": ROOT / "HFM" / "Models_Library" / "HFM_Library",
    },

    "Simulator_STHE": {
        "package": "STHE-Simulator",
        "path": ROOT / "STHE" / "Models_Library" / "STHE_Library",
    },
}


# ==========================================================
# CHECK IF MODULE CAN BE IMPORTED
# ==========================================================
def is_importable(module_name: str) -> bool:
    """
    Check whether the requested Python module can actually be imported.

    This is intentionally stronger than only checking whether a module
    specification exists.
    """
    try:
        importlib.import_module(module_name)
        return True

    except Exception:
        return False


# ==========================================================
# INSTALL LOCAL PACKAGE IN EDITABLE MODE
# ==========================================================
def install_editable(path: Path) -> None:
    """
    Install a local Python project using the same Python interpreter
    that is executing the Main file.
    """
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "-e",
        str(path),
    ])


# ==========================================================
# RESTART ORIGINAL MAIN SCRIPT
# ==========================================================
def restart_main() -> None:
    """
    Restart the original Main script with the same Python interpreter
    and the same command-line arguments.
    """

    main_script = Path(sys.argv[0]).resolve()

    print(f"🔄 Restarting: {main_script.name}")

    subprocess.run(
        [
            sys.executable,
            str(main_script),
            *sys.argv[1:],
        ],
        check=False,
    )

    sys.exit(0)


# ==========================================================
# VERIFY / INSTALL REQUIRED LOCAL LIBRARIES
# ==========================================================
def ensure_local_libraries(required_libraries: list[str]) -> None:
    """
    Verify all local libraries requested by the calling Main file.

    If a required library is missing, it is installed in editable mode.
    After a successful installation, the original Main script is restarted.

    Parameters
    ----------
    required_libraries:
        List containing keys defined in LOCAL_LIBRARIES.
    """

    installed_something = False
    failed = []

    print("\n" + "=" * 70)
    print("LOCAL LIBRARIES CHECK")
    print("=" * 70)

    # ------------------------------------------------------
    # Validate requested library names
    # ------------------------------------------------------
    for library_name in required_libraries:

        if library_name not in LOCAL_LIBRARIES:

            print(
                f"❌ [ERROR] Unknown local library: "
                f"'{library_name}'"
            )

            print(
                "   Available libraries: "
                + ", ".join(LOCAL_LIBRARIES.keys())
            )

            sys.exit(1)

    # ------------------------------------------------------
    # Check / install each required library
    # ------------------------------------------------------
    for library_name in required_libraries:

        library = LOCAL_LIBRARIES[library_name]

        module = library_name
        package = library["package"]
        path = library["path"]

        # --------------------------------------------------
        # Library already works
        # --------------------------------------------------
        if is_importable(module):

            print(
                f"✔️  [OK] {library_name} "
                f"({package}) installed and ready"
            )

            continue

        # --------------------------------------------------
        # Library is missing or cannot be imported
        # --------------------------------------------------
        print(
            f"🔄 [INSTALL] {library_name} "
            f"({package}) is not available"
        )

        print(f"   Path: {path}")

        # --------------------------------------------------
        # Validate local project directory
        # --------------------------------------------------
        if not path.exists():

            print(
                f"❌ [ERROR] Library folder does not exist:\n"
                f"   {path}"
            )

            failed.append(library_name)
            continue

        # --------------------------------------------------
        # Validate pyproject.toml
        # --------------------------------------------------
        if not (path / "pyproject.toml").exists():

            print(
                f"❌ [ERROR] pyproject.toml not found in:\n"
                f"   {path}"
            )

            failed.append(library_name)
            continue

        # --------------------------------------------------
        # Install local package
        # --------------------------------------------------
        try:

            install_editable(path)

            installed_something = True

            print(
                f"✔️  [DONE] {library_name} "
                f"installed successfully"
            )

        except subprocess.CalledProcessError as exc:

            print(
                f"❌ [ERROR] Failed to install "
                f"{library_name}"
            )

            print(exc)

            failed.append(library_name)

    print("=" * 70)

    # ------------------------------------------------------
    # Installation failure
    # ------------------------------------------------------
    if failed:

        print(
            "❌ The following local libraries "
            "could not be installed:"
        )

        for library_name in failed:
            print(f"   - {library_name}")

        print("\nExecution aborted.")

        sys.exit(1)

    # ------------------------------------------------------
    # At least one library was installed.
    #
    # IMPORTANT:
    # We intentionally DO NOT try to import the newly installed
    # package in this same interpreter.
    #
    # The Main script will be restarted so Python starts cleanly
    # and performs the real imports again.
    # ------------------------------------------------------
    if installed_something:

        print(
            "✔️  All missing local libraries "
            "were installed successfully."
        )

        print(
            "🔄 Restarting Main so the newly installed "
            "libraries are loaded in a clean Python process."
        )

        print("=" * 70 + "\n")

        restart_main()

    # ------------------------------------------------------
    # Nothing needed installation
    # ------------------------------------------------------
    print(
        "✔️  All required local libraries "
        "are ready."
    )

    print("=" * 70 + "\n")


#endregion
#########################################################################################
