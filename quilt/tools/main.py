"""
Parses the command-line arguments and runs a command.
"""

from __future__ import print_function

import argparse
import sys

import requests

from . import command

def main():
    """
    Build and run parser
    """
    parser = argparse.ArgumentParser(description="Quilt Command Line")
    subparsers = parser.add_subparsers(title="Commands", dest='cmd')
    subparsers.required = True

    login_p = subparsers.add_parser("login")
    login_p.set_defaults(func=command.login)

    logout_p = subparsers.add_parser("logout")
    logout_p.set_defaults(func=command.logout)

    log_p = subparsers.add_parser("log")
    log_p.add_argument("package", type=str, help="Owner/Package Name")
    log_p.set_defaults(func=command.log)

    generate_p = subparsers.add_parser("generate")
    generate_p.add_argument("directory", help="Source file directory")
    generate_p.set_defaults(func=command.generate)

    build_p = subparsers.add_parser("build")
    build_p.add_argument("package", type=str, help="Owner/Package Name")
    buildpath_group = build_p.add_mutually_exclusive_group(required=True)
    buildpath_group.add_argument("path", type=str, nargs='?',
                                 help="Path to source files (directory) or the Yaml build file")
    build_p.set_defaults(func=command.build_from_path)

    push_p = subparsers.add_parser("push")
    push_p.add_argument("package", type=str, help="Owner/Package Name")
    push_p.add_argument("--reupload", action="store_true",
                        help="Re-upload all fragments, even if fragment is already in registry")
    push_p.set_defaults(func=command.push)

    version_p = subparsers.add_parser("version")
    version_subparsers = version_p.add_subparsers(title="version", dest='cmd')
    version_subparsers.required = True

    version_list_p = version_subparsers.add_parser("list")
    version_list_p.add_argument("package", type=str, help="Owner/Package Name")
    version_list_p.set_defaults(func=command.version_list)

    version_add_p = version_subparsers.add_parser("add")
    version_add_p.add_argument("package", type=str, help="Owner/Package Name")
    version_add_p.add_argument("version", type=str, help="Version")
    version_add_p.add_argument("pkghash", type=str, help="Package hash")
    version_add_p.set_defaults(func=command.version_add)

    tag_p = subparsers.add_parser("tag")
    tag_subparsers = tag_p.add_subparsers(title="Tag", dest='cmd')
    tag_subparsers.required = True

    tag_list_p = tag_subparsers.add_parser("list")
    tag_list_p.add_argument("package", type=str, help="Owner/Package Name")
    tag_list_p.set_defaults(func=command.tag_list)

    tag_add_p = tag_subparsers.add_parser("add")
    tag_add_p.add_argument("package", type=str, help="Owner/Package Name")
    tag_add_p.add_argument("tag", type=str, help="Tag name")
    tag_add_p.add_argument("pkghash", type=str, help="Package hash")
    tag_add_p.set_defaults(func=command.tag_add)

    tag_remove_p = tag_subparsers.add_parser("remove")
    tag_remove_p.add_argument("package", type=str, help="Owner/Package Name")
    tag_remove_p.add_argument("tag", type=str, help="Tag name")
    tag_remove_p.set_defaults(func=command.tag_remove)

    install_p = subparsers.add_parser("install")
    install_p.add_argument("package", type=str, help="Owner/Package Name")
    install_p.set_defaults(func=command.install)
    install_p.add_argument("-f", "--force", action="store_true", help="Overwrite without prompting")
    install_group = install_p.add_mutually_exclusive_group()
    install_group.add_argument("-x", "--hash", type=str, help="Package hash")
    install_group.add_argument("-v", "--version", type=str, help="Package version")
    install_group.add_argument("-t", "--tag", type=str, help="Package tag - defaults to 'latest'")

    access_p = subparsers.add_parser("access")
    access_subparsers = access_p.add_subparsers(title="Access", dest='cmd')
    access_subparsers.required = True

    access_list_p = access_subparsers.add_parser("list")
    access_list_p.add_argument("package", type=str, help="Owner/Package Name")
    access_list_p.set_defaults(func=command.access_list)

    access_add_p = access_subparsers.add_parser("add")
    access_add_p.add_argument("package", type=str, help="Owner/Package Name")
    access_add_p.add_argument("user", type=str, help="User to add")
    access_add_p.set_defaults(func=command.access_add)

    access_remove_p = access_subparsers.add_parser("remove")
    access_remove_p.add_argument("package", type=str, help="Owner/Package Name")
    access_remove_p.add_argument("user", type=str, help="User to remove")
    access_remove_p.set_defaults(func=command.access_remove)

    search_p = subparsers.add_parser("search")
    search_p.add_argument("query", type=str, help="Search query (max 5 keywords)")
    search_p.set_defaults(func=command.search)

    ls_p = subparsers.add_parser("ls")
    ls_p.set_defaults(func=command.ls)

    inspect_p = subparsers.add_parser("inspect")
    inspect_p.add_argument("package", type=str, help="Owner/Package Name")
    inspect_p.set_defaults(func=command.inspect)

    args = parser.parse_args()

    # Convert argparse.Namespace into dict and clean it up.
    # We can then pass it directly to the helper function.
    kwargs = vars(args)
    del kwargs['cmd']

    func = kwargs.pop('func')

    try:
        func(**kwargs)
        return 0
    except command.CommandException as ex:
        print(ex, file=sys.stderr)
        return 1
    except requests.exceptions.ConnectionError as ex:
        print("Failed to connect: %s" % ex, file=sys.stderr)
        return 1
