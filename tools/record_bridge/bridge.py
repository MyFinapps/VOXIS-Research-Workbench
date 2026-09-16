#!/usr/bin/env python3
"""VOXIS C01: local record intake. Python standard library only."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys

import store


def default_store():
    root = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return root / "VOXIS" / "RecordBridge" / "index.sqlite"


def output(value):
    # Escaping also keeps imported control characters from acting on terminals.
    print(json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False))


def ask_path(prompt):
    return Path(input(prompt).strip().strip('"'))


def menu(path):
    print("VOXIS Record Bridge 0.1\nLocal record intake and inspection")
    print("Index: " + str(path))
    print("Structure checks do not validate geometry or manuscript meaning.")
    while True:
        print("\n1 Import JSON   2 List records   3 Inspect record   4 Export original   5 Verify index   Q Quit")
        choice = input("Choose: ").strip().lower()
        if choice == "q":
            return 0
        try:
            if choice == "1":
                source = ask_path("Paste the JSON file path (quotes are okay): ")
                session = input("Existing Search Session reference (Enter leaves it unassigned): ").strip() or None
                output(store.ingest(path, source, session))
            elif choice == "2":
                output(store.records(path))
            elif choice in ("3", "4"):
                items = store.records(path)
                if not items:
                    print("No records yet.")
                    continue
                for n, item in enumerate(items, 1):
                    print(str(n) + " " + json.dumps(item["name"], ensure_ascii=True) + " [" + item["status"] + "]")
                n = int(input("Record number: "))
                if not 1 <= n <= len(items):
                    raise ValueError("Choose a listed record number")
                rid = items[n - 1]["id"]
                if choice == "3":
                    _, summary = store.retrieve(path, rid)
                    output({"id": rid, "summary": summary})
                else:
                    output(store.export_original(path, rid, ask_path("New output file path: ")))
            elif choice == "5":
                output(store.verify(path))
            else:
                print("Choose 1-5 or Q.")
        except (ValueError, OSError, sqlite3.Error) as exc:
            print("Could not complete: " + str(exc))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=default_store(), help="Local intake SQLite path")
    sub = parser.add_subparsers(dest="command")
    imp = sub.add_parser("import", help="Retain original JSON and index a structural summary")
    imp.add_argument("file", type=Path)
    imp.add_argument("--session", help="Reference an existing Search Session; does not create or predeclare one")
    sub.add_parser("list")
    show = sub.add_parser("show"); show.add_argument("id")
    exp = sub.add_parser("export"); exp.add_argument("id"); exp.add_argument("file", type=Path)
    sub.add_parser("verify")
    args = parser.parse_args(argv)
    try:
        if args.command is None:
            return menu(args.store)
        if args.command == "import":
            result = store.ingest(args.store, args.file, args.session)
            output(result)
            return 0 if result["summary"]["status"] == "structure_checked" else 2
        if args.command == "list":
            output(store.records(args.store))
        elif args.command == "show":
            _, summary = store.retrieve(args.store, args.id)
            output({"id": args.id, "summary": summary})
        elif args.command == "export":
            output(store.export_original(args.store, args.id, args.file))
        elif args.command == "verify":
            result = store.verify(args.store); output(result)
            return 0 if result["ok"] else 2
        return 0
    except (ValueError, OSError, sqlite3.Error, EOFError, KeyboardInterrupt) as exc:
        print("Record bridge: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
