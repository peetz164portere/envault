"""CLI subcommands for export and import in envault."""

import getpass
import sys

from envault.export import export_env, import_env


def cmd_export(args):
    """Handle the 'export' CLI subcommand."""
    password = getpass.getpass(f"Password for '{args.project}': ")
    try:
        out_path = export_env(
            project=args.project,
            password=password,
            output_path=args.output,
        )
        print(f"Exported '{args.project}' to {out_path}")
    except KeyError:
        print(f"Error: project '{args.project}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_import(args):
    """Handle the 'import' CLI subcommand."""
    password = getpass.getpass(f"Password for '{args.project}': ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Error: passwords do not match.", file=sys.stderr)
        sys.exit(1)
    try:
        env_vars = import_env(
            project=args.project,
            password=password,
            input_path=args.file,
        )
        print(f"Imported {len(env_vars)} variable(s) into '{args.project}'.")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def register_export_commands(subparsers):
    """Register export/import subcommands onto an argparse subparsers object."""
    # export
    p_export = subparsers.add_parser("export", help="Export a project to a .env file")
    p_export.add_argument("project", help="Project name")
    p_export.add_argument("-o", "--output", default=None, help="Output file path")
    p_export.set_defaults(func=cmd_export)

    # import
    p_import = subparsers.add_parser("import", help="Import a .env file into a project")
    p_import.add_argument("project", help="Project name")
    p_import.add_argument("file", help="Path to .env file to import")
    p_import.set_defaults(func=cmd_import)
