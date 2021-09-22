import os

from preprocessing import Preprocess
from utility import Utils
from ontoserver import API
import const


def get_direct_path(cats_reason):
    direct_all_possible_reasons_and_synonyms = {}
    direct_reasons_complete = {}
    direct_involved_concepts = {}
    all_seen_reasons = {}

    all_direct_reasons = []

    all_seen_reasons_list = []

    for cats in cats_reason.columns:
        if not cats.startswith("#"):
            reasons_cat = cats_reason[cats].dropna()
            for reason in reasons_cat:
                reason = reason.strip()
                if reason.strip():
                    if reason.lower() not in all_seen_reasons_list:
                        all_seen_reasons_list.append(reason.lower())
                    cat_list = cats.split('#')
                    break_true = False
                    for cat in cat_list:
                        all_possible_reasons = Preprocess.get_pre_post_processed(reason)
                        all_possible_reasons_lower = [x.lower() for x in all_possible_reasons]
                        for preprocessed_reason in all_possible_reasons_lower:
                            result = API.call_ontoserver_extend_api(cat.split("|")[0], preprocessed_reason.strip())
                            # processed_reason, result, all_possible_reasons_lower = API.get_all_candidates(cat.split("|")[0], reason)
                            # if processed_reason.lower() not in all_seen_reasons_list:
                            #     all_seen_reasons_list.append(processed_reason.lower())
                            if result is not None and len(result) == 1:
                                if result.lower() not in all_direct_reasons:
                                    all_direct_reasons.append(reason.lower())
                                _, allconceptid = API.get_involved_concepts(cat.split("|")[0], result[0])
                                synonym = API.get_all_synonym_candidate(result[0]['code'])
                                res_reason = {"specific": cat, "reason": reason,
                                              "preprocessed_reason": preprocessed_reason,
                                              "result": result[0], "synonym": synonym}
                                if cats not in direct_reasons_complete:
                                    direct_reasons_complete[cats] = [res_reason]

                                    direct_involved_concepts[cats] = allconceptid

                                    direct_all_possible_reasons_and_synonyms[
                                        cats] = synonym + all_possible_reasons_lower
                                else:
                                    temp = direct_reasons_complete.get(cats)
                                    if res_reason not in temp:
                                        temp.append(res_reason)
                                        direct_reasons_complete.update({cats: temp})

                                    temp_allconceptid = direct_involved_concepts.get(cats)
                                    temp_allconceptid = list(set(temp_allconceptid).union(set(allconceptid)))
                                    direct_involved_concepts.update({cats: temp_allconceptid})

                                    temp_reason = direct_all_possible_reasons_and_synonyms.get(cats)
                                    temp_reason_list = synonym + all_possible_reasons_lower
                                    temp_reason = list(set(temp_reason).union(set(temp_reason_list)))
                                    direct_all_possible_reasons_and_synonyms.update({cats: temp_reason})
                                break_true = True
                                break
                        if break_true:
                            break

            if cats not in direct_all_possible_reasons_and_synonyms.keys():
                direct_all_possible_reasons_and_synonyms[cats] = []
                direct_reasons_complete[cats] = []
                direct_involved_concepts[cats] = []

    all_seen_reasons["all"] = all_seen_reasons_list

    return all_direct_reasons, all_seen_reasons, direct_all_possible_reasons_and_synonyms, direct_reasons_complete, direct_involved_concepts


# def get_semi_direct_path(cats_reason, direct_reasons):
#     not_found = {}
#     semi_direct_reasons= {}
#     semi_direct_reasons_complete = {}
#     semi_direct_involved_concepts = {}
#
#     for cats in cats_reason.columns:
#         # API.call_init_transitive_closure(cats)
#         # set_codes = []
#         # ontology = {}
#         # if cats in direct_involved_concepts:
#         #     set_codes = API.convert_concepts_to_closure_format(
#         #         direct_involved_concepts.get(cats))
#         #     ontology = API.call_transitivec_closure_set_codes(cats, set_codes)
#
#         # print(cats)
#         if not cats.startswith("#"):
#             reasons_cat = cats_reason[cats].dropna()
#             for reason in reasons_cat:
#                 reason = reason.strip()
#                 print(reason)
#                 # print(reason)
#                 highest_matched_concept = {}
#                 best_score = const.BEST_SCORE
#                 matched_concept = None
#                 if reason.strip():
#                     cat_list = cats.split('#')
#                     for cat in cat_list:
#
#                         processed_reason, result, all_possible_reasons_lower = API.get_all_candidates(cat.split("|")[0], reason)
#
#                         if result is not None and len(result) > 1:
#
#                             for counter, res in enumerate(result):
#                                 if counter > const.THRESHOLD:
#                                     break
#                                 _, allconceptid = API.get_involved_concepts(cat.split("|")[0], res)
#
#                                 intersection_concepts = []
#                                 if cats in direct_involved_concepts:
#
#                                     intersection_concepts = list(set(direct_involved_concepts.get(cats)) & set(allconceptid))
#                                 highest_matched_concept[res['code']] = {"score" : len(intersection_concepts),
#                                                                         "allconceptid": allconceptid,
#                                                                         "intersection": intersection_concepts,
#                                                                         "specific": cat, "reason": reason,
#                                                                         "preprocessed_reason": processed_reason,
#                                                                         "result": res,
#                                                                         "all_possible_reasons_lower": all_possible_reasons_lower}
#                                 print(res, len(intersection_concepts))
#                                 if len(intersection_concepts) != 0 and len(intersection_concepts) < best_score:
#                                     best_score = len(intersection_concepts)
#                                     matched_concept = res['code']
#                                 elif cat.split("|")[0] == res['code']:
#                                     best_score = const.MATCHED_SCORE
#                                     matched_concept = res['code']
#                                     break
#                             if best_score == const.MATCHED_SCORE:
#                                 break
#
#                         # elif result is None or cats not in direct_involved_concepts:
#                         #     print("category: ", cats, " specific: ", cat, "Preprocessing", " Reason: ", reason, " -> ",
#                         #           processed_reason)
#
#                     if matched_concept and matched_concept in highest_matched_concept:
#                         concept = highest_matched_concept.get(matched_concept)
#                         res_reason = {"specific": concept["specific"], "reason": reason,
#                                       "processed_reason": concept["processed_reason"],
#                                       "result": concept["result"]}
#                         if cats not in semi_direct_reasons_complete:
#                             semi_direct_reasons_complete[cats] = [res_reason]
#
#                             semi_direct_reasons[cats] = [res_reason['result'].get('display').lower()] + concept["all_possible_reasons_lower"]
#
#                             semi_direct_involved_concepts[cats] = concept["allconceptid"]
#                         else:
#                             temp = semi_direct_reasons_complete.get(cats)
#                             if res_reason not in temp:
#                                 temp.append(res_reason)
#                                 semi_direct_reasons_complete.update({cats: temp})
#
#                             temp_reasons = semi_direct_reasons.get(cats)
#                             temp_reason_list = [res_reason['result'].get('display').lower()] +concept["all_possible_reasons_lower"]
#                             temp_reasons = list(set(temp_reasons).union(set(temp_reason_list)))
#                             semi_direct_reasons.update({cats:temp_reasons})
#
#                             temp_allconceptid = semi_direct_involved_concepts.get(cats)
#                             temp_allconceptid = list(set(temp_allconceptid).union(set(concept["allconceptid"])))
#                             semi_direct_involved_concepts.update({cats: temp_allconceptid})
#                     elif cats not in direct_reasons or (cats in direct_reasons and reason.lower() not in direct_reasons[cats]):
#                         if cats not in not_found:
#                             not_found[cats] = [reason]
#                         else:
#                             temp = not_found.get(cats)
#                             temp.append(reason)
#                             not_found.update({cats: temp})
#
#             if cats not in semi_direct_reasons.keys():
#                 semi_direct_reasons[cats] = []
#                 semi_direct_reasons_complete[cats] = []
#                 semi_direct_involved_concepts[cats] = []
#
#
#     return semi_direct_reasons, semi_direct_reasons_complete, semi_direct_involved_concepts, not_found


def assigned_code_to_phrase(cats, code, phrase, direct_phrase_code):
    if phrase.lower() not in direct_phrase_code:
        direct_phrase_code[phrase.lower()] = code.lower()
    elif code.lower() != direct_phrase_code[phrase.lower()]:
        print("error on assigned code phrase: ", cats, "pharase:", phrase, "new:", code, "existed", direct_phrase_code[phrase.lower()])
        direct_phrase_code[phrase.lower()] = code.lower()
    return direct_phrase_code


def get_direct_goldstandar(cats_reason):
    direct_all_possible_reasons_and_synonyms = {}
    direct_reasons_complete = {}
    direct_phrase_code_category = {}
    direct_involved_concepts = {}
    all_seen_reasons = {}
    direct_extra_categories = {}
    direct_main_codes = {}

    all_direct_reasons = []
    all_seen_reasons_list = []

    for columnid, cats in enumerate(cats_reason.columns):
        direct_phrase_code = {}
        if not cats.startswith("#") and (columnid % 2 == 0):
            reasons_cat = cats_reason[cats].dropna()
            for rowid, reason in enumerate(reasons_cat):
                print(reason)
                reason = reason.strip()
                assigned_display_code = cats_reason.iloc[rowid, columnid + 1]
                assigned_code = ""
                assigned_display = ""
                if assigned_display_code == assigned_display_code:
                    assigned_code = assigned_display_code.split("|")[-1]
                    # assigned_display = assigned_display_code.split("|")[0]
                    reason_full_singular_lemma = Preprocess.get_pre_processed(reason)
                    for reason_all in reason_full_singular_lemma:
                        direct_phrase_code = assigned_code_to_phrase(cats, assigned_display_code, reason_all, direct_phrase_code)

                if reason:
                    if reason.lower() not in all_seen_reasons_list:
                        all_seen_reasons_list.append(reason.lower())

                    # all_possible_reasons_lower = [reason.lower()]
                    all_possible_reasons_lower = Preprocess.get_pre_processed(reason)
                    # all_possible_reasons_lower = [x.lower() for x in all_possible_reasons]

                    if reason.lower() not in all_direct_reasons:
                        all_direct_reasons.append(reason.lower())

                    cat_list = cats.split('#')
                    for i, cat in enumerate(cat_list):

                        if assigned_code not in cat and assigned_code in cats:
                            continue

                        cat_name = cat.split("|")[-1]

                        # add category to all possible reasons as well
                        all_possible_reasons_lower = Preprocess.get_exist(cat_name, all_possible_reasons_lower)

                        _, allconceptid = API.get_involved_concepts(cat.split("|")[0], assigned_code)

                        if i != 0 and len(allconceptid) == 0:
                            continue

                        all_synonym = API.get_all_synonym_candidate(assigned_code)
                        synonym = all_possible_reasons_lower
                        for syn_candidate in all_synonym:
                            direct_phrase_code = assigned_code_to_phrase(cats, assigned_display_code, syn_candidate,
                                                                         direct_phrase_code)
                            # all_possible_syn = Preprocess.get_pre_post_processed_v2(syn_candidate, synonym=True)
                            # for possible_syn in all_possible_syn:
                            synonym = Preprocess.get_exist(syn_candidate, synonym)
                        if len(allconceptid) == 0:
                            categ = "not direct connection"
                        else:
                            categ = cat
                        res_reason = {"specific": categ, "reason": reason,
                                      "preprocessed_reason": all_possible_reasons_lower,
                                      "result": assigned_display_code, "synonym": synonym, "main_code": assigned_code,
                                      "involved_concept": allconceptid}

                        if cats not in direct_reasons_complete:
                            direct_reasons_complete[cats] = [res_reason]
                            direct_involved_concepts[cats] = allconceptid
                            direct_all_possible_reasons_and_synonyms[cats] = synonym

                            if assigned_display_code != assigned_display_code:
                                direct_main_codes[cats] = []
                                direct_extra_categories[cats] = []

                            elif len(allconceptid) == 0:
                                direct_main_codes[cats] = [assigned_code]
                                direct_extra_categories[cats] = [assigned_code]
                            else:
                                direct_main_codes[cats] = [assigned_code]
                                direct_extra_categories[cats] = []

                        else:
                            temp = direct_reasons_complete.get(cats)
                            if res_reason not in temp:
                                temp.append(res_reason)
                                direct_reasons_complete.update({cats: temp})

                            temp_allconceptid = direct_involved_concepts.get(cats)
                            temp_allconceptid = list(set(temp_allconceptid).union(set(allconceptid)))
                            direct_involved_concepts.update({cats: temp_allconceptid})

                            temp_reason = direct_all_possible_reasons_and_synonyms.get(cats)
                            temp_reason_list = synonym
                            temp_reason = list(set(temp_reason).union(set(temp_reason_list)))
                            direct_all_possible_reasons_and_synonyms.update({cats: temp_reason})

                            if len(allconceptid) == 0 and assigned_display_code == assigned_display_code:
                                temp_main_codes = direct_main_codes.get(cats)
                                if assigned_code not in temp_main_codes:
                                    temp_main_codes.append(assigned_code)
                                    direct_main_codes.update({cats: temp_main_codes})
                                    temp_extra_category = direct_extra_categories.get(cats)
                                    temp_extra_category.append(assigned_code)
                                    direct_extra_categories.update({cats: temp_extra_category})
                            elif assigned_display_code == assigned_display_code:
                                temp_main_codes = direct_main_codes.get(cats)
                                if assigned_code not in temp_main_codes:
                                    temp_main_codes.append(assigned_code)
                                    direct_main_codes.update({cats: temp_main_codes})

            direct_phrase_code_category[cats] = direct_phrase_code
        # if cats not in direct_all_possible_reasons_and_synonyms.keys():
        #     direct_all_possible_reasons_and_synonyms[cats] = []
        #     direct_reasons_complete[cats] = []
        #     direct_involved_concepts[cats] = []
        #     direct_extra_categories[cats] = []
        #     direct_main_codes[cats] = []

    all_seen_reasons["all"] = all_seen_reasons_list
    return direct_phrase_code_category, all_direct_reasons, all_seen_reasons, direct_all_possible_reasons_and_synonyms, direct_reasons_complete, direct_involved_concepts, direct_extra_categories, direct_main_codes


def get_semi_direct_path_by_distance(cats_reason, direct_reasons, all_direct_reasons):
    not_found = {}
    semi_all_possible_reasons_and_synonyms = {}
    semi_direct_reasons_complete = {}
    semi_direct_involved_concepts = {}
    semi_direct_details = {}

    for cats in cats_reason.columns:
        # print(cats)
        if not cats.startswith("#"):
            reasons_cat = cats_reason[cats].dropna()
            for reason in reasons_cat:
                reason = reason.strip()
                print(reason)
                # print(reason)
                highest_matched_concepts = {}
                best_score = const.BEST_SCORE
                intetsection_score = const.BEST_SCORE
                matched_concept = None
                if reason.strip() and reason.lower() not in all_direct_reasons:
                    cat_list = cats.split('#')
                    for cat in cat_list:

                        all_possible_reasons = Preprocess.get_pre_post_processed(reason)
                        all_possible_reasons_lower = [x.lower() for x in all_possible_reasons]
                        for preprocessed_reason in all_possible_reasons_lower:
                            result = API.call_ontoserver_extend_api(cat.split("|")[0], preprocessed_reason.strip())

                            # processed_reason, result, all_possible_reasons_lower = API.get_all_candidates(cat.split("|")[0], reason)

                            if result is not None and len(result) > 1:

                                for counter, res in enumerate(result):
                                    # if cat.split("|")[0] == res['code'] or res['code'] in direct_involved_concepts.get(cats):
                                    if cat.split("|")[0] == res['code'] or (
                                            cats in direct_all_possible_reasons_and_synonyms and res[
                                        "display"] in direct_all_possible_reasons_and_synonyms.get(cats)) or \
                                            (cats in semi_all_possible_reasons_and_synonyms and res[
                                                "display"] in semi_all_possible_reasons_and_synonyms.get(cats)):
                                        # if cat.split("|")[0] == res['code']:
                                        best_score = const.MATCHED_SCORE
                                        matched_concept = res['code']
                                        highest_matched_concepts[res['code']] = {"score": best_score,
                                                                                 "allconceptid": [res['code']],
                                                                                 "distance": [res['code']],
                                                                                 "specific": cat, "reason": reason,
                                                                                 "processed_reason": preprocessed_reason,
                                                                                 "result": res,
                                                                                 "all_possible_reasons_lower": all_possible_reasons_lower}

                                        break

                                    if counter > const.THRESHOLD:
                                        break
                                    _, allconceptid = API.get_involved_concepts(cat.split("|")[0], res)

                                    intersection_concepts = []
                                    API.call_init_transitive_closure(cats)
                                    set_codes = []
                                    transitivec_closure_table = {}
                                    if cats in direct_involved_concepts:
                                        all_concpets = direct_involved_concepts.get(cats) + allconceptid
                                        set_codes = API.convert_concepts_to_closure_format(all_concpets)

                                        transitivec_closure_table = API.call_transitivec_closure_set_codes(cats,
                                                                                                           set_codes)
                                        intersection_concepts = list(
                                            set(direct_involved_concepts.get(cats)) & set(allconceptid))

                                    path = Utils.shortest_path(transitivec_closure_table, res["code"],
                                                               cat.split("|")[0])
                                    # print(res, len(path))
                                    if len(path) != 0 and (len(path) - 1 < best_score or (
                                            len(path) - 1 == best_score and len(
                                            intersection_concepts) < intetsection_score)):
                                        # if len(path) != 0 and len(path) < best_score:

                                        best_score = len(path) - 1
                                        intetsection_score = len(intersection_concepts)
                                        matched_concept = res['code']

                                        highest_matched_concepts[res['code']] = {"score": len(path) - 1,
                                                                                 "intetsection_score": intetsection_score,
                                                                                 "allconceptid": allconceptid,
                                                                                 "distance": path,
                                                                                 "specific": cat, "reason": reason,
                                                                                 "processed_reason": preprocessed_reason,
                                                                                 "result": res,
                                                                                 "all_possible_reasons_lower": all_possible_reasons_lower
                                                                                 }

                                if best_score == const.MATCHED_SCORE:
                                    break
                        if best_score == const.MATCHED_SCORE:
                            break

                        # elif result is None or cats not in direct_involved_concepts:
                        #     print("category: ", cats, " specific: ", cat, "Preprocessing", " Reason: ", reason, " -> ",
                        #           processed_reason)

                    if matched_concept and matched_concept in highest_matched_concepts:
                        concept = highest_matched_concepts.get(matched_concept)
                        synonym = API.get_all_synonym_candidate(matched_concept)
                        res_reason = {"highest_matched_concepts": highest_matched_concepts,
                                      "specific": concept["specific"], "reason": reason,
                                      "processed_reason": concept["processed_reason"],
                                      "result": concept["result"], "synonym": synonym}
                        if cats not in semi_direct_reasons_complete:
                            semi_direct_reasons_complete[cats] = [res_reason]

                            semi_all_possible_reasons_and_synonyms[cats] = synonym + concept[
                                "all_possible_reasons_lower"]

                            semi_direct_involved_concepts[cats] = concept["allconceptid"]

                            semi_direct_details[cats] = [highest_matched_concepts]
                        else:
                            temp = semi_direct_reasons_complete.get(cats)
                            if res_reason not in temp:
                                temp.append(res_reason)
                                semi_direct_reasons_complete.update({cats: temp})

                            temp_reasons = semi_all_possible_reasons_and_synonyms.get(cats)
                            temp_reason_list = synonym + concept["all_possible_reasons_lower"]
                            temp_reasons = list(set(temp_reasons).union(set(temp_reason_list)))
                            semi_all_possible_reasons_and_synonyms.update({cats: temp_reasons})

                            temp_allconceptid = semi_direct_involved_concepts.get(cats)
                            temp_allconceptid = list(set(temp_allconceptid).union(set(concept["allconceptid"])))
                            semi_direct_involved_concepts.update({cats: temp_allconceptid})

                            temp_semi_direct_details = semi_direct_details.get(cats)
                            temp_semi_direct_details.append(highest_matched_concepts)
                            semi_direct_details.update({cats: temp_semi_direct_details})

                    elif cats not in direct_reasons or (
                            cats in direct_reasons and reason.lower() not in direct_reasons[cats]):
                        if cats not in not_found:
                            not_found[cats] = [reason]
                        else:
                            temp = not_found.get(cats)
                            temp.append(reason)
                            not_found.update({cats: temp})

            if cats not in semi_all_possible_reasons_and_synonyms.keys():
                semi_all_possible_reasons_and_synonyms[cats] = []
                semi_direct_reasons_complete[cats] = []
                semi_direct_involved_concepts[cats] = []
                semi_direct_details[cats] = []

    return semi_all_possible_reasons_and_synonyms, semi_direct_reasons_complete, semi_direct_involved_concepts, semi_direct_details, not_found


if __name__ == '__main__':

    cats_reason = Utils.read_cats_reason(os.path.join(Utils.data_dir, "gold_standard_MCRI.csv"))
    # cats_reason = cats_reason.iloc[:, 4:]

    # Direct

    # all_direct_reasons, all_seen_reasons, direct_all_possible_reasons_and_synonyms, direct_reasons_complete, direct_involved_concepts,direct_extra_categories, direct_main_codes  = get_direct_goldstandar(cats_reason)

    # if os.path.exists(os.path.join(Utils.data_dir, "all_seen_reasons.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "direct_reasons_complete.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "direct_all_possible_reasons_and_synonyms.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "direct_involved_concepts.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "all_direct_reasons.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "direct_extra_categories.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "direct_main_codes.json")):
    #     direct_all_possible_reasons_and_synonyms = Utils.load_json(
    #         os.path.join(Utils.data_dir, "direct_all_possible_reasons_and_synonyms.json"))
    #     direct_reasons_complete = Utils.load_json(os.path.join(Utils.data_dir, "direct_reasons_complete.json"))
    #     direct_involved_concepts = Utils.load_json(os.path.join(Utils.data_dir, "direct_involved_concepts.json"))
    #     all_seen_reasons = Utils.load_json(os.path.join(Utils.data_dir, "all_seen_reasons.json"))
    #     all_direct_reasons = Utils.load_json(os.path.join(Utils.data_dir, "all_direct_reasons.json"))
    #     direct_extra_categories = Utils.load_json(os.path.join(Utils.data_dir, "direct_extra_categories.json"))
    #     direct_main_codes = Utils.load_json(os.path.join(Utils.data_dir, "direct_main_codes.json"))
    # else:
    direct_phrase_code_category, all_direct_reasons, all_seen_reasons, direct_all_possible_reasons_and_synonyms, direct_reasons_complete, direct_involved_concepts, direct_extra_categories, direct_main_codes = get_direct_goldstandar(
        cats_reason)

    Utils.save_json(os.path.join(Utils.data_dir, "direct_phrase_code_category.json"),
                    direct_phrase_code_category)
    Utils.save_json(os.path.join(Utils.data_dir, "direct_all_possible_reasons_and_synonyms.json"),
                    direct_all_possible_reasons_and_synonyms)
    Utils.save_json(os.path.join(Utils.data_dir, "direct_reasons_complete.json"), direct_reasons_complete)
    Utils.save_json(os.path.join(Utils.data_dir, "direct_involved_concepts.json"), direct_involved_concepts)
    Utils.save_json(os.path.join(Utils.data_dir, "all_seen_reasons.json"), all_seen_reasons)
    Utils.save_json(os.path.join(Utils.data_dir, "all_direct_reasons.json"), all_direct_reasons)
    Utils.save_json(os.path.join(Utils.data_dir, "direct_extra_categories.json"), direct_extra_categories)
    Utils.save_json(os.path.join(Utils.data_dir, "direct_main_codes.json"), direct_main_codes)

    # #Semi Direct
    # if os.path.exists(os.path.join(Utils.data_dir, "semi_direct_reasons_complete.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "semi_direct_involved_concepts.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "semi_direct_reasons.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "semi_direct_details.json")) and \
    #         os.path.exists(os.path.join(Utils.data_dir, "not_found.json")):
    #     semi_all_possible_reasons_and_synonyms = Utils.load_json(os.path.join(Utils.data_dir, "semi_all_possible_reasons_and_synonyms.json"))
    #     semi_direct_reasons_complete = Utils.load_json(os.path.join(Utils.data_dir, "semi_direct_reasons_complete.json"))
    #     semi_direct_involved_concepts = Utils.load_json(os.path.join(Utils.data_dir, "semi_direct_involved_concepts.json"))
    #     semi_direct_details = Utils.load_json(os.path.join(Utils.data_dir, "semi_direct_details.json"))
    #     not_found = Utils.load_json(os.path.join(Utils.data_dir, "not_found.json"))
    # else:
    #     semi_all_possible_reasons_and_synonyms, semi_direct_reasons_complete, semi_direct_involved_concepts, semi_direct_details, not_found = get_semi_direct_path_by_distance(cats_reason, direct_all_possible_reasons_and_synonyms, all_direct_reasons)
    #     Utils.save_json(os.path.join(Utils.data_dir, "semi_all_possible_reasons_and_synonyms.json"), semi_all_possible_reasons_and_synonyms)
    #     Utils.save_json(os.path.join(Utils.data_dir, "semi_direct_reasons_complete.json"), semi_direct_reasons_complete)
    #     Utils.save_json(os.path.join(Utils.data_dir, "semi_direct_involved_concepts.json"), semi_direct_involved_concepts)
    #     Utils.save_json(os.path.join(Utils.data_dir, "semi_direct_involved_concepts.json"), semi_direct_involved_concepts)
    #     Utils.save_json(os.path.join(Utils.data_dir, "semi_direct_details.json"), semi_direct_details)
    #     Utils.save_json(os.path.join(Utils.data_dir, "not_found.json"), not_found)
