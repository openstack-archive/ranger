import yaml


def merge_yamls(document, section):
    document_dict = yaml.safe_load(document)
    section_dict = yaml.safe_load(section)
    merge_dict(section_dict, document_dict)
    new_document = yaml.dump(document_dict)
    return new_document


# source is being merged into destiantion
def merge_dict(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge_dict(value, node)
        else:
            destination[key] = value

    return destination

document = """
    a: 1
    b:
        c: 3
        d: 4
        f:
            h: h1
"""

section = """
    b:
        d: 6
        e: 5
        f:
            g: g1
            h:
                h1: h2
"""

print(merge_yamls(document, section))
