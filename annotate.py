import rtoml, re, argparse, pathlib

parser = argparse.ArgumentParser(description="Annotate data")
parser.add_argument("target", help="target path")
args = parser.parse_args()

print("----\nStart annotation")
structure_doc = rtoml.load(open(args.target+"/mid/structure.toml"))
keyword_dict = dict()
keyword_list = list()
for keyword_path in sorted(list(pathlib.Path(args.target).glob('keyword-*.toml'))):
    keyword_doc = rtoml.load(open(keyword_path))
    unique_list = [n for n in keyword_doc.keys() if n not in keyword_list]
    duplicate_list = [n for n in keyword_doc.keys() if n in keyword_list]
    if len(duplicate_list) > 0:
        print("ERROR: duplicate list ~ {}".format(duplicate_list))
    keyword_list.extend(unique_list)
    keyword_dict.update(keyword_doc)
def check(input_str,exclude,do_re=str()):
    include_list = list()
    exclude_list = list()
    for key_str,detail_dict in structure_doc.items():
        name_str = detail_dict["name"]
        include_bool = (input_str in name_str)
        if do_re != str():
            key_re = re.compile(do_re)
            if key_re.match(name_str):
                include_bool = True
        if include_bool:
            exclude_bool = False
            for exclude_str in exclude:
                if exclude_str in name_str:
                    exclude_bool = True
            if exclude_bool:
                exclude_list.append(key_str)
            else:
                include_list.append(key_str)
    return include_list, exclude_list
for entry_name in keyword_list:
    entry_detail = keyword_dict[entry_name]
    inclusive_collect_list = list()
    exclusive_collect_list = list()
    for inclusive_str in entry_detail['inclusive']:
        inclusive_list, exclusive_list = check(inclusive_str,entry_detail['exclusive'],do_re=entry_detail.get('re',str()))
        inclusive_collect_list.extend([n for n in inclusive_list if n not in inclusive_collect_list])
        exclusive_collect_list.extend([n for n in exclusive_list if n not in exclusive_collect_list])
    if len(inclusive_collect_list) > 1:
        print(F"[{entry_name}]\n  found in: ({len(inclusive_collect_list)})")
        print("    {}".format("\n    ".join(inclusive_collect_list)))
        print(F"  Excluded: ({len(exclusive_collect_list)})")
        print("    {}".format("\n    ".join(exclusive_collect_list)))
    for episode_str in inclusive_collect_list:
        episode_table = structure_doc[episode_str]
        episode_tag_list = episode_table["tag"]
        episode_tag_list.append(entry_name)
        episode_table["tag"] = episode_tag_list
        episode_tag_list = episode_table["category"]
        episode_tag_list.extend(entry_detail["category"])
        episode_table["category"] = episode_tag_list
        structure_doc[episode_str] = episode_table
with open(args.target+"/mid/keyword.toml",'w') as target_handler:
    rtoml.dump(keyword_dict,target_handler)
with open(args.target+"/mid/annotation.toml",'w') as target_handler:
    target_handler.write("# Add your own tag to each episode\n\n")
with open(args.target+"/mid/annotation.toml",'a') as target_handler:
    rtoml.dump(structure_doc,target_handler)
print("    ----\nEnd annotation")