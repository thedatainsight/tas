import os
import signal
import atexit
import json
import time
from pathlib import Path
import subprocess
import argparse
import pprint
from distutils.util import strtobool

children_pid = []


@atexit.register
def kill_child():
    for child_pid in children_pid:
        os.kill(child_pid, signal.SIGTERM)

cmd_parser = argparse.ArgumentParser(add_help=False)
cmd_parser.add_argument(
    "cmd", type=str, choices=["new", "del", "run", "set", "list"], help="Main command",
)
args = cmd_parser.parse_known_args()[0]
PATH_TO_SETTINGS = Path.home() / Path(".tas.json")


def get_default_settings():
    return {
        "namespaces": [
            {
                "name": "default",
                "path": str(Path.home() / Path("Documents/tas_projects/")),
            }
        ],
        "templates": [
            {
                "name": "default",
                "actions": [
                    {"type": "venv"},
                    {"type": "dir", "path": "py"},
                    {"type": "dir", "path": "py/src"},
                    {"type": "dir", "path": "sql"},
                    {"type": "dir", "path": "resources"},
                    {"type": "file", "path": "README.md"},
                    {"type": "requirements", "packages": ["jupyter"]},
                    {"type": "file_link", "url": ""}
                ],
            }
        ],
        "projects": [],
    }


def load_settings():
    if not PATH_TO_SETTINGS.exists():
        return get_default_settings()
    with open(PATH_TO_SETTINGS) as f:
        return json.load(f)


def save_settings():
    with open(PATH_TO_SETTINGS, "w+") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def lookup_in_list_of_dicts(l, name, return_index=False):
    for i, val in enumerate(l):
        if val["name"] == name:
            return val if not return_index else (i, val)
    return None if not return_index else (None, None)


def get_proj(args, should_exist, ns_path):
    proj_name = f"{args.namespace}.{args.name}"
    proj_path = Path(ns_path) / Path(args.name)
    exists = lookup_in_list_of_dicts(settings["projects"], proj_name)
    if exists and not should_exist:
        raise Exception("Project already exists!")
    elif not exists and should_exist:
        raise Exception("Project not found!")
    return exists if exists else {"name": proj_name, "path": proj_path}


def get_args(cmd):
    # TODO: create allowed combinations of args
    if cmd == "set":
        args_parser = argparse.ArgumentParser(parents=[cmd_parser])
        args_parser.add_argument("namespace", type=str, help="Namespace")
        args_parser.add_argument("path", type=str, help="PosixPath")
    elif cmd == "del":
        args_parser = argparse.ArgumentParser(parents=[cmd_parser])
        args_parser.add_argument("name", type=str, help="Name of an object")
        args_parser.add_argument(
            "-namespace", "-ns", type=str, default="default", help="Namespace"
        )
        args_parser.add_argument("type", type=str, choices=["n", "p"], default="p")
    elif cmd == "list":
        args_parser = argparse.ArgumentParser(parents=[cmd_parser])
        args_parser.add_argument(
            "type", type=str, choices=["n", "t", "p", "a"], default="p"
        )
    elif cmd == "new":
        args_parser = argparse.ArgumentParser(parents=[cmd_parser])
        args_parser.add_argument("name", type=str, help="Name")
        args_parser.add_argument(
            "-template", "-t", type=str, default="default", help="Template"
        )
        args_parser.add_argument(
            "-namespace", "-ns", type=str, default="default", help="Namespace"
        )
        args_parser.add_argument("-path", "-p", type=str, help="PosixPath")
    elif cmd == "run":
        args_parser = argparse.ArgumentParser(parents=[cmd_parser])
        args_parser.add_argument(
            "-namespace", "-ns", type=str, default="default", help="Namespace"
        )
        args_parser.add_argument("name", type=str, help="Project name")
    return args_parser.parse_args()


def interactive_y_n(question):
    while True:
        try:
            reply = str(input(question + " (y/n): ")).lower().strip()
            return strtobool(reply)
        except ValueError as e:
            pprint.pprint("Please enter yes or no!")
            pass


settings = load_settings()

if __name__ == "__main__":
    extra_args = get_args(args.cmd)
    if args.cmd == "set":
        # TODO: make it interactive?
        ns_id, ns = lookup_in_list_of_dicts(
            settings["namespaces"], extra_args.namespace, return_index=True
        )
        if ns_id != None:
            settings["namespaces"][ns_id] = {**ns, "path": extra_args.path}
        else:
            settings["namespaces"].append(
                {"name": extra_args.namespace, "path": extra_args.path}
            )
        save_settings()
    elif args.cmd == "del":
        # TODO: interactive and delete projects
        if extra_args.type == "n":
            target = "namespaces"
            name = args.name
        elif extra_args.type == "p":
            target = "projects"
            ns = lookup_in_list_of_dicts(settings["namespaces"], extra_args.namespace)
            proj = get_proj(extra_args, True, ns["path"])
            name = proj["name"]
        target_id, ns = lookup_in_list_of_dicts(
            settings[target], name, return_index=True
        )
        if target_id is None:
            raise Exception("No such name!")
        del settings[target][target_id]
        save_settings()
    elif args.cmd == "list":
        if extra_args.type == "n":
            pprint.pprint(settings["namespaces"])
        elif extra_args.type == "p":
            pprint.pprint(settings["projects"])
        elif extra_args.type == "t":
            pprint.pprint(settings["templates"])
        elif extra_args.type == "a":
            pprint.pprint(settings)
    elif args.cmd == "new":
        ns = lookup_in_list_of_dicts(settings["namespaces"], extra_args.namespace)
        proj = get_proj(extra_args, False, ns["path"])
        template = lookup_in_list_of_dicts(settings["templates"], extra_args.template)
        if proj["path"].exists():
            if not interactive_y_n("Path already exists. Should we proceed?"):
                exit()
        else:
            proj["path"].mkdir(parents=True)
        for action in template["actions"]:
            if action["type"] == "dir":
                (proj["path"] / Path(action["path"])).mkdir(
                    parents=False, exist_ok=True
                )
            elif action["type"] == "file":
                filepath = proj["path"] / Path(action["path"])
                filepath.touch()
            elif action["type"] == "requirements":
                os.chdir(proj["path"])
                subprocess.call(
                    [
                        "python",
                        "-m",
                        "venv",
                        "--system-site-packages",
                        str(proj["path"] / Path("env")),
                    ]
                )
                if action["packages"]:
                    subprocess.call(
                        ["./env/bin/python", "-m", "pip", "install"]
                        + action["packages"]
                    )
                filepath = proj["path"] / Path("requirements.txt")
                with filepath.open("w+") as f:
                    f.write("\n".join(action["packages"]))
        settings["projects"].append({"name": proj["name"], "path": str(proj["path"])})
        save_settings()
    elif args.cmd == "run":
        ns = lookup_in_list_of_dicts(settings["namespaces"], extra_args.namespace)
        proj = get_proj(extra_args, True, ns["path"])
        os.chdir(Path(proj["path"]))
        child = subprocess.Popen(
            ["./env/bin/python", "-m", "jupyter", "notebook", "--log-level=0"]
        )
        children_pid.append(child.pid)
        time.sleep(2)
        while not interactive_y_n("Would you like to end?"):
            continue
