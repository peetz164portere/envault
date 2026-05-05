"""Password rotation for envault vaults."""

from envault.vault import load_env, save_env, list_projects
from envault.audit import record_event


class RotationError(Exception):
    pass


def rotate_project(project: str, old_password: str, new_password: str, vault_dir: str = None) -> None:
    """Re-encrypt a single project's vault with a new password."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}

    try:
        env_vars = load_env(project, old_password, **kwargs)
    except Exception as e:
        raise RotationError(f"Failed to decrypt '{project}' with old password: {e}") from e

    try:
        save_env(project, env_vars, new_password, **kwargs)
    except Exception as e:
        raise RotationError(f"Failed to re-encrypt '{project}' with new password: {e}") from e

    record_event("rotate", project, details="password rotated", vault_dir=vault_dir)


def rotate_all(old_password: str, new_password: str, vault_dir: str = None) -> dict:
    """Rotate password for all projects. Returns a dict of project -> 'ok' or error message."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    projects = list_projects(**kwargs)
    results = {}

    for project in projects:
        try:
            rotate_project(project, old_password, new_password, vault_dir=vault_dir)
            results[project] = "ok"
        except RotationError as e:
            results[project] = str(e)

    return results
