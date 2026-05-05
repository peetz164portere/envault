"""Command-line interface for envault."""

import sys
import getpass
import argparse

from envault.vault import save_env, load_env, remove_env, project_exists, list_projects


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Secure local .env file manager with encrypted storage.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # envault set <project> <envfile>
    set_parser = subparsers.add_parser("set", help="Encrypt and store a .env file for a project.")
    set_parser.add_argument("project", help="Project name")
    set_parser.add_argument("envfile", help="Path to the .env file")

    # envault get <project>
    get_parser = subparsers.add_parser("get", help="Decrypt and print env vars for a project.")
    get_parser.add_argument("project", help="Project name")

    # envault remove <project>
    rm_parser = subparsers.add_parser("remove", help="Remove stored env for a project.")
    rm_parser.add_argument("project", help="Project name")

    # envault list
    subparsers.add_parser("list", help="List all stored projects.")

    return parser.parse_args(argv)


def cmd_set(project: str, envfile: str) -> int:
    try:
        with open(envfile, "r") as f:
            env_data = f.read()
    except FileNotFoundError:
        print(f"error: file not found: {envfile}", file=sys.stderr)
        return 1

    password = getpass.getpass("Enter password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("error: passwords do not match.", file=sys.stderr)
        return 1

    save_env(project, env_data, password)
    print(f"Saved env for project '{project}'.")
    return 0


def cmd_get(project: str) -> int:
    if not project_exists(project):
        print(f"error: no vault found for project '{project}'.", file=sys.stderr)
        return 1

    password = getpass.getpass("Enter password: ")
    try:
        env_data = load_env(project, password)
    except Exception:
        print("error: failed to decrypt — wrong password or corrupted vault.", file=sys.stderr)
        return 1

    print(env_data, end="")
    return 0


def cmd_remove(project: str) -> int:
    if not project_exists(project):
        print(f"error: no vault found for project '{project}'.", file=sys.stderr)
        return 1

    remove_env(project)
    print(f"Removed env for project '{project}'.")
    return 0


def cmd_list() -> int:
    projects = list_projects()
    if not projects:
        print("No projects stored.")
    else:
        print("Stored projects:")
        for p in sorted(projects):
            print(f"  {p}")
    return 0


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.command == "set":
        return cmd_set(args.project, args.envfile)
    elif args.command == "get":
        return cmd_get(args.project)
    elif args.command == "remove":
        return cmd_remove(args.project)
    elif args.command == "list":
        return cmd_list()
    return 0


if __name__ == "__main__":
    sys.exit(main())
