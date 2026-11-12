
import os
import argparse


def list_files(directory="./algorithms", show_all=False):
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return

    files = os.listdir(directory)
    files = [f for f in files if os.path.isfile(os.path.join(directory, f))]

    if show_all:
        result = sorted(files)
    else:
        # Remove extensions and keep unique names
        result = sorted({os.path.splitext(f)[0] for f in files})

    for name in result:
        print(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List algorithm files.")
    parser.add_argument(
        "directory",
        nargs="?",
        default="./algorithms",
        help="Directory to scan (default: ../algorithms)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all files, including different extensions of the same name"
    )

    args = parser.parse_args()
    list_files(args.directory, args.all)
