"""CLI commands for template export/apply."""

from __future__ import annotations

import argparse
import sys

from envault.template import export_template, apply_template, list_template_keys, TemplateError


def cmd_template_export(args: argparse.Namespace) -> None:
    try:
        export_template(
            args.project,
            args.password,
            args.output,
            mask_values=not args.no_mask,
        )
        print(f"Template written to {args.output}")
    except TemplateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_template_apply(args: argparse.Namespace) -> None:
    if args.password != args.confirm_password:
        print("Error: passwords do not match.", file=sys.stderr)
        sys.exit(1)
    try:
        written = apply_template(
            args.project,
            args.password,
            args.template,
            overwrite=args.overwrite,
        )
        if written:
            print(f"Applied {len(written)} key(s) to project '{args.project}':")
            for key in sorted(written):
                print(f"  {key}")
        else:
            print("No new keys applied (all keys already exist; use --overwrite to replace them).")
    except TemplateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_template_keys(args: argparse.Namespace) -> None:
    try:
        keys = list_template_keys(args.template)
        if keys:
            for key in keys:
                print(key)
        else:
            print("No keys found in template.")
    except TemplateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_template_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # template-export
    p_exp = subparsers.add_parser("template-export", help="Export a project as a .env template")
    p_exp.add_argument("project", help="Project name")
    p_exp.add_argument("password", help="Vault password")
    p_exp.add_argument("output", help="Output file path")
    p_exp.add_argument("--no-mask", action="store_true", help="Include actual values (default: mask them)")
    p_exp.set_defaults(func=cmd_template_export)

    # template-apply
    p_app = subparsers.add_parser("template-apply", help="Apply a .env template to a project")
    p_app.add_argument("project", help="Project name")
    p_app.add_argument("password", help="Vault password")
    p_app.add_argument("confirm_password", help="Confirm vault password")
    p_app.add_argument("template", help="Template file path")
    p_app.add_argument("--overwrite", action="store_true", help="Overwrite existing keys")
    p_app.set_defaults(func=cmd_template_apply)

    # template-keys
    p_keys = subparsers.add_parser("template-keys", help="List keys defined in a template file")
    p_keys.add_argument("template", help="Template file path")
    p_keys.set_defaults(func=cmd_template_keys)
