"""CLI commands for managing project policies in envault."""

import sys
from envault.policy import (
    PolicyError,
    set_policy,
    get_policy,
    delete_policy,
)
from envault.storage import ensure_vault_dir


def _vault_dir(args):
    return getattr(args, "vault_dir", None) or ensure_vault_dir()


def cmd_policy_set(args):
    """Set or update a policy for a project."""
    required = args.required.split(",") if args.required else None
    forbidden = args.forbidden.split(",") if args.forbidden else None
    min_len = args.min_password_length
    try:
        set_policy(
            _vault_dir(args),
            args.project,
            required_keys=required,
            forbidden_keys=forbidden,
            min_password_length=min_len,
        )
        print(f"Policy updated for project '{args.project}'.")
    except PolicyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_policy_get(args):
    """Show the current policy for a project."""
    policy = get_policy(_vault_dir(args), args.project)
    if not policy:
        print(f"No policy set for project '{args.project}'.")
        return
    print(f"Policy for '{args.project}':")
    if "required_keys" in policy:
        print(f"  Required keys : {', '.join(policy['required_keys'])}")
    if "forbidden_keys" in policy:
        print(f"  Forbidden keys: {', '.join(policy['forbidden_keys'])}")
    if "min_password_length" in policy:
        print(f"  Min password  : {policy['min_password_length']} characters")


def cmd_policy_delete(args):
    """Delete the policy for a project."""
    try:
        delete_policy(_vault_dir(args), args.project)
        print(f"Policy deleted for project '{args.project}'.")
    except PolicyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def register_policy_commands(subparsers):
    p_set = subparsers.add_parser("policy-set", help="Set policy for a project")
    p_set.add_argument("project")
    p_set.add_argument("--required", default=None, help="Comma-separated required keys")
    p_set.add_argument("--forbidden", default=None, help="Comma-separated forbidden keys")
    p_set.add_argument("--min-password-length", type=int, default=None, dest="min_password_length")
    p_set.set_defaults(func=cmd_policy_set)

    p_get = subparsers.add_parser("policy-get", help="Show policy for a project")
    p_get.add_argument("project")
    p_get.set_defaults(func=cmd_policy_get)

    p_del = subparsers.add_parser("policy-delete", help="Delete policy for a project")
    p_del.add_argument("project")
    p_del.set_defaults(func=cmd_policy_delete)
