# ============================================================
# (F.R.C) ALL INKLUSIVE ONEFILE SYSTEM WITH INDEX & ASCII
# COMPLETE FIXED VERSION — H2 HEADERS & ABSOLUTE PURE NAMES
# SELF-EXCLUDE SAFE
# EXCLUDES 00. MASKIN LÄSNING
# ============================================================

import os
import json

# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = (
    ".md",
    ".txt",
    ".py",
    ".json",
    ".csv"
     ".log"
)

# ============================================================
# EXCLUDED FOLDERS
# ============================================================

EXCLUDED_FOLDERS = {
    "00. MASKIN LÄSNING"
}

# ============================================================
# ROOT
# ============================================================

ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

# ============================================================
# CURRENT SCRIPT
# ============================================================

THIS_SCRIPT = os.path.abspath(__file__)

# ============================================================
# EXPORT
# ============================================================

BASE_NAME = os.path.basename(ROOT)

EXPORT_FOLDER = (
    "00. MACHINE READING (F.R.C) — "
    + BASE_NAME
)

EXPORT_PATH = os.path.join(
    ROOT,
    EXPORT_FOLDER
)

# ============================================================
# OUTPUT MARKDOWN NAME — (F.R.C) + MAPPNAMN
# ============================================================

OUTPUT_MD_NAME = (
    "(F.R.C)_"
    + BASE_NAME
    + ".md"
)

FULL_MD_PATH = os.path.join(
    EXPORT_PATH,
    OUTPUT_MD_NAME
)

# ============================================================
# FILTER DIRECTORIES
# ============================================================

def filter_dirnames(dirnames):

    dirnames[:] = [
        dirname
        for dirname in dirnames
        if dirname not in EXCLUDED_FOLDERS
        and not dirname.startswith(".")
    ]

# ============================================================
# BUILD INDEX (FOR JSON)
# ============================================================

def build_index(root_dir):

    index_tree = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):

        filter_dirnames(
            dirnames
        )

        abs_dir = os.path.abspath(
            dirpath
        )

        abs_export = os.path.abspath(
            EXPORT_PATH
        )

        if abs_dir.startswith(
            abs_export
        ):
            continue

        rel_dir = os.path.relpath(
            dirpath,
            root_dir
        )

        if rel_dir == ".":
            rel_dir = ""

        parts = (
            rel_dir.split(os.sep)
            if rel_dir
            else []
        )

        pointer = index_tree

        for part in parts:

            if part not in pointer:
                pointer[part] = {}

            pointer = pointer[part]

        files = []

        for filename in sorted(
            filenames
        ):

            lower = filename.lower()

            full_path = os.path.abspath(
                os.path.join(
                    dirpath,
                    filename
                )
            )

            if full_path == THIS_SCRIPT:
                continue

            if lower.endswith(
                ALLOWED_EXTENSIONS
            ):

                files.append(
                    filename
                )

        if files:

            pointer["_files"] = files

    return index_tree

# ============================================================
# RECURSIVE INTERNAL ANCHOR LINK GENERATOR (ABSOLUT RENA NAMN)
# ============================================================

def build_markdown_wiki_index(dirpath, lines):
    abs_dir = os.path.abspath(dirpath)
    abs_export = os.path.abspath(EXPORT_PATH)
    
    if abs_dir.startswith(abs_export):
        return

    try:
        entries = os.listdir(dirpath)
    except PermissionError:
        return

    folders = []
    files = []

    for entry in sorted(entries):
        full_entry_path = os.path.join(dirpath, entry)
        
        if entry in EXCLUDED_FOLDERS or entry.startswith("."):
            continue
            
        if full_entry_path == THIS_SCRIPT or full_entry_path == os.path.abspath(FULL_MD_PATH):
            continue

        if os.path.isdir(full_entry_path):
            folders.append(entry)
        elif os.path.isfile(full_entry_path):
            if entry.lower().endswith(ALLOWED_EXTENSIONS):
                files.append(entry)

    if files:
        if dirpath != ROOT:
            rel_folder_name = os.path.relpath(dirpath, ROOT)
            lines.append("")
            lines.append(f"## 📂 {rel_folder_name}")
            lines.append("---")

        for file in files:
            # Enbart det rena filnamnet för både ankare och visningstext
            anchor = file
            display_name = os.path.splitext(file)[0]
            
            lines.append(f"- **[[#{anchor}|{display_name}]]**")
            lines.append("<br>")

        if dirpath != ROOT:
            lines.append("")
            lines.append("---")
            lines.append("")

    for folder in sorted(folders):
        next_dir = os.path.join(dirpath, folder)
        build_markdown_wiki_index(next_dir, lines)

# ============================================================
# RECURSIVE ASCII TREE GENERATOR
# ============================================================

def has_visible_children(dirpath):
    try:
        entries = os.listdir(dirpath)
    except PermissionError:
        return False

    for entry in entries:
        full_entry_path = os.path.join(dirpath, entry)
        if entry in EXCLUDED_FOLDERS or entry.startswith("."):
            continue
        if full_entry_path == THIS_SCRIPT or full_entry_path == os.path.abspath(FULL_MD_PATH):
            continue
        if os.path.isdir(full_entry_path):
            return True
        if os.path.isfile(full_entry_path) and entry.lower().endswith(ALLOWED_EXTENSIONS):
            return True
    return False

def build_ascii_tree(dirpath, prefix=""):
    abs_dir = os.path.abspath(dirpath)
    abs_export = os.path.abspath(EXPORT_PATH)
    
    if abs_dir.startswith(abs_export):
        return []

    try:
        entries = os.listdir(dirpath)
    except PermissionError:
        return []

    valid_entries = []
    for entry in sorted(entries):
        full_entry_path = os.path.join(dirpath, entry)
        if entry in EXCLUDED_FOLDERS or entry.startswith("."):
            continue
        if full_entry_path == THIS_SCRIPT or full_entry_path == os.path.abspath(FULL_MD_PATH):
            continue
            
        if os.path.isdir(full_entry_path) or (os.path.isfile(full_entry_path) and entry.lower().endswith(ALLOWED_EXTENSIONS)):
            valid_entries.append((entry, full_entry_path))

    lines = []
    for index, (name, full_path) in enumerate(valid_entries):
        is_last = index == len(valid_entries) - 1
        connector = "└── " if is_last else "├── "

        lines.append(prefix + connector + name)

        if os.path.isdir(full_path):
            extension = "    " if is_last else "│   "
            if has_visible_children(full_path):
                lines.append(prefix + extension + "│")
                lines.extend(build_ascii_tree(full_path, prefix + extension))
                if not is_last:
                    lines.append(prefix + extension.rstrip())

    return lines

# ============================================================
# FORMAT CONTENT
# ============================================================

def format_file_content(
    filepath,
    filename
):

    ext = os.path.splitext(
        filename
    )[1].lower()

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            content = f.read()

    except Exception as error:

        return (
            "ERROR READING FILE:\n\n"
            + str(error)
        )

    if ext == ".md":

        return content

    if ext == ".txt":

        return (
            "```text\n"
            + content
            + "\n```"
        )

    if ext == ".py":

        return (
            "```python\n"
            + content
            + "\n```"
        )

    if ext == ".json":

        return (
            "```json\n"
            + content
            + "\n```"
        )

    if ext == ".csv":

        return (
            "```csv\n"
            + content
            + "\n```"
        )

    return content

# ============================================================
# MERGE SYSTEM WITH INTEGRATED LOKAL INDEX & ASCII
# ============================================================

def merge_markdown_files():

    os.makedirs(
        EXPORT_PATH,
        exist_ok=True
    )

    index_data = build_index(
        ROOT
    )

    with open(
        FULL_MD_PATH,
        "w",
        encoding="utf-8"
    ) as outfile:

        # ====================================================
        # 1. JSON INDEX
        # ====================================================

        outfile.write(
            "# JSON INDEX\n\n"
        )

        outfile.write(
            "```json\n"
        )

        outfile.write(
            json.dumps(
                index_data,
                indent=4,
                ensure_ascii=False
            )
        )

        outfile.write(
            "\n```\n"
        )

        outfile.write(
            "\n\n---\n"
        )

        # ====================================================
        # 2. INTEGRATED LOKAL INDEX & ASCII BLOCKS
        # ====================================================
        
        outfile.write("\n---\n>---\n")
        outfile.write(f">  ### **📂 — {BASE_NAME}**\n")
        outfile.write(">---\n---\n\n")

        # Sektion 1: INDEX
        outfile.write(">---\n> > # $$INDEX\\ —\\ 🜁$$\n>---\n\n")
        
        wiki_lines = []
        build_markdown_wiki_index(ROOT, wiki_lines)
        for line in wiki_lines:
            outfile.write(line + "\n")
            
        outfile.write("\n")

        # Sektion 2: ASCII
        outfile.write("---\n>---\n> > # $$ ASCII\\ —\\ 🜁$$\n>---\n---\n")
        outfile.write("````ASCII\n")
        
        outfile.write(BASE_NAME + "\n\n")
        tree_lines = build_ascii_tree(ROOT)
        for line in tree_lines:
            outfile.write(line + "\n")
            
        outfile.write("````\n---\n\n")

        # ====================================================
        # 3. MERGED CONTENT
        # ====================================================

        outfile.write(
            "# MERGED CONTENT\n"
        )

        outfile.write(
            "---\n"
        )

        for dirpath, dirnames, filenames in os.walk(
            ROOT
        ):

            filter_dirnames(
                dirnames
            )

            abs_dir = os.path.abspath(
                dirpath
            )

            abs_export = os.path.abspath(
                EXPORT_PATH
            )

            if abs_dir.startswith(
                abs_export
            ):
                continue

            for filename in sorted(
                filenames
            ):

                lower = filename.lower()

                if not lower.endswith(
                    ALLOWED_EXTENSIONS
                ):
                    continue

                full_path = os.path.abspath(
                    os.path.join(
                        dirpath,
                        filename
                    )
                )

                if full_path == os.path.abspath(
                    FULL_MD_PATH
                ):
                    continue

                if full_path == THIS_SCRIPT:
                    continue

                # Enbart det exakta filnamnet
                header_name = filename

                print(
                    "ADDING:"
                )

                print(
                    header_name
                )

                print()

                # ÄNDRAD TILL TVÅ BRÄDGÅRDAR (##) FÖR ATT SKAPA EN H2-RUBRIK
                header = (
                    "\n\n---\n"
                    "## "
                    + header_name
                    + "\n"
                    "---\n\n"
                )

                outfile.write(
                    header
                )

                content = format_file_content(
                    full_path,
                    filename
                )

                outfile.write(
                    content
                )

                outfile.write(
                    "\n"
                )

    print(
        "================================================"
    )

    print(
        "COMPLETE"
    )

    print(
        FULL_MD_PATH
    )

    print(
        "================================================"
    )

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    merge_markdown_files()

    input(
        "Press ENTER to close..."
    )