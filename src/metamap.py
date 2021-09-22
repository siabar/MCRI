

def annotate(txt, mm):
    m = mm.extract_concepts([txt])[0]

    preferred_list = []
    name_list = []
    anno_spans = set()

    for concept in m:
        # ignore alternative annotations for the same span
        if str(concept.pos_info) in anno_spans:
            continue
        else:
            anno_spans.add(str(concept.pos_info))
        if hasattr(concept, 'mm'):
            preferred_name = concept.preferred_name
            name = txt[int(concept.pos_info.split("/")[0])-1:int(concept.pos_info.split("/")[0])-1 + int(concept.pos_info.split("/")[-1])]
            preferred_list.append(preferred_name)
            name_list.append(name)
        else:
            continue

    return name_list, preferred_list