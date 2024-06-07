import os
import re

file_list = []
target_dir_list = []
base_dir = os.getcwd()
destination = os.path.join(base_dir, "converted");

def list_files(path="."):
    for entry in os.listdir(path):
        rel_path = os.path.join(path, entry)
        if os.path.isdir(rel_path):
            list_files(rel_path)
            target_dir_list.append(os.path.join(destination, rel_path[2:]))
        elif rel_path.endswith('.md'):
            file_list.append(rel_path)

list_files()
#partial_metadata = f"product: {product}\n" \
#           "version:"
#           "author:\n" \
#           f"  - {author}\n" \
#           "reviewer: \n" \
#           f"  - {reviewer}\n" \
#           f"published: {date.today()}\n" \
#           f"reviewed: {date.today()}\n" \
#           "tags:\n" \
#           f"  - {product}\n" \
#           "---\n\n"

#base_dir = os.path.join(os.getcwd(), "Standard-Operating-Procedures")
for d in target_dir_list:
    if not os.path.exists(d):
        os.makedirs(d)

metadata_pattern = re.compile("^---\n")
contributor_pattern = re.compile("\n?\#+?\s*?[Cc]ontribut.+?\n")
contributor_table_pattern = re.compile("\n\|\s*?\**?[Rr]ole.*?[Nn]ame.*?\|\w*?\n\|[\s\-\|]*?\n")
h1_pattern = re.compile("^\#.+?\n")
author_and_reviewer_row_pattern = re.compile("\|\s*?[Aa]uth.+?[Rr]evi.+?\|(.+?)\|\n")
author_row_pattern = re.compile("\|\s*?[Aa]uth.+?\|(.+?)\|\n")
reviewer_row_pattern = re.compile("\|\s*?[Rr]evi.+?\|(.+?)\|\n")
li_tag_pattern = re.compile("\<[Ll]i\/?\>")
tech_writer_row_pattern = re.compile("\|\s*?[Tt]ech.+[Ww]ri.+?\|\n")

counter = 0

#file_list = [f for f in os.listdir(base_dir) if f.endswith('.md')]
for f in file_list:
    source = os.path.join(base_dir, f[2:])

    with open(source, "r", encoding='utf-8') as md_file:
        lines = md_file.read()
        has_contributor_table = contributor_pattern.search(lines)
        has_metadata = contributor_pattern.search(lines)

        if has_contributor_table and has_metadata != None:
            metadata = "---\n"
            title = "title: "
            h1 = h1_pattern.search(lines)
            if h1 != None:
                title += h1.group(0)[1:]
                lines = lines.replace(h1.group(0), "", 1)
            else:
                title += f.split("\\")[-1].replace("-", " ")[:-3]

            metadata += title + "\n"
        
            metadata += "version: 1.0.0\n"
        
            # Remove "## Contributors" heading and table header
            lines = re.sub(contributor_pattern, "", lines)
            lines = re.sub(contributor_table_pattern, "", lines)

            combined_author_and_reviewer_row = author_and_reviewer_row_pattern.search(lines)
            if combined_author_and_reviewer_row != None:
                text_list = combined_author_and_reviewer_row.group(1)
                list = re.split(li_tag_pattern, text_list)
                metadata += "author:\n"
                for name in list:
                    name = name.strip()
                    if len(name) > 0:
                        metadata += f"  - {name}\n"
                metadata += "reviewer:\n"
                for name in list:
                    name = name.strip()
                    if len(name) > 0:
                        metadata += f"  - {name}\n"
                lines = lines.replace(combined_author_and_reviewer_row.group(0), "")
            else:
                author_row = author_row_pattern.search(lines)
                if author_row != None:
                    text_list = author_row.group(1)
                    list = re.split(li_tag_pattern, text_list)
                    metadata += "author:\n"
                    for name in list:
                        name = name.strip()
                        if len(name) > 0:
                            metadata += f"  - {name}\n"
                    lines = lines.replace(author_row.group(0), "")

                reviewer_row = reviewer_row_pattern.search(lines)
                if reviewer_row != None:
                    text_list = reviewer_row.group(1)
                    list = re.split(li_tag_pattern, text_list)
                    metadata += "reviewer:\n"
                    for name in list:
                        name = name.strip()
                        if len(name) > 0:
                            metadata += f"  - {name}\n"
                    lines = lines.replace(reviewer_row.group(0), "")

            lines = re.sub(tech_writer_row_pattern, "", lines)
            metadata += "---\n"

            target = os.path.join(destination, f[2:])
            with open(target, "w", encoding='utf-8') as md_file:
                    md_file.write(metadata + lines)
                    counter += 1

print("Converted", counter, "files.")