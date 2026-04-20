"""
MkDocs macros to inject version and other dynamic content.
"""

from pathlib import Path

def define_env(env):
    """
    Define variables and macros for MkDocs.

    The version is always read from src/disruptsc/_version.py.
    We deliberately do not catch failures here: if the version can't be
    resolved, the docs build should fail loudly rather than silently
    ship a stale hardcoded fallback (as happened before v2).
    """
    version_file = Path(__file__).parent / "src" / "disruptsc" / "_version.py"
    version_content = version_file.read_text()
    version_value = None
    for line in version_content.split('\n'):
        if line.strip().startswith('__version__'):
            version_value = line.split('=')[1].strip().strip('"').strip("'")
            break
    if not version_value:
        raise RuntimeError(
            f"Could not parse __version__ from {version_file}"
        )

    # Set as simple variable instead of function
    env.variables['version'] = version_value
    
    # Also provide as macros for backwards compatibility
    @env.macro
    def get_version():
        """Return the current version."""
        return version_value
    
    @env.macro  
    def version_badge():
        """Return a version badge for the current version."""
        return f"[![Version](https://img.shields.io/badge/version-{version_value}-blue)](https://github.com/ccolon/disrupt-sc/releases/tag/v{version_value})"
    
    @env.macro
    def installation_instructions():
        """Return installation instructions with current version."""
        return f"""```bash
# Clone the repository
git clone https://github.com/ccolon/disrupt-sc.git
cd disrupt-sc

# Checkout specific version (optional)
git checkout v{version_value}

# Create environment
conda env create -f dsc-environment.yml
conda activate dsc
```"""