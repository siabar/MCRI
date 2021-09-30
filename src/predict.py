import json
import os
import xlsxwriter
import logging
import metamap
from ontoserver import API
from preprocessing import Preprocess
from utility import Utils
from datetime import datetime
import const
from pymetamap import MetaMap
import logging

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)


involved_concepts = Utils.load_json(os.path.join(Utils.data_dir, "direct_involved_concepts.json"))
# semi_direct_involved_concepts = Utils.load_json(os.path.join(Utils.data_dir, "semi_direct_involved_concepts.json"))

# semi_all_possible_reasons_and_synonyms = Utils.load_json(os.path.join(Utils.data_dir, "semi_all_possible_reasons_and_synonyms.json"))
all_possible_reasons_and_synonyms = Utils.load_json(
    os.path.join(Utils.data_dir, "direct_all_possible_reasons_and_synonyms.json"))

extra_categories = Utils.load_json(os.path.join(Utils.data_dir, "direct_extra_categories.json"))

main_codes = Utils.load_json(os.path.join(Utils.data_dir, "direct_main_codes.json"))

phrase_code_category = Utils.load_json(os.path.join(Utils.data_dir, "direct_phrase_code_category.json"))

predicted_rfv = Utils.load_json(os.path.join(Utils.data_dir, "predicted.json"))




# all_possible_reasons_and_synonyms = Utils.merge(direct_all_possible_reasons_and_synonyms, semi_all_possible_reasons_and_synonyms)


# involved_concepts = Utils.merge(direct_involved_concepts, semi_direct_involved_concepts)

def check_categories_distance(reason, preprocessing=True):
    # original_reason = reason.lower()

    original_reason_found_in_a_category = False
    reasons_list = []

    if preprocessing:
        all_possible_reasons_lower = Preprocess.get_pre_post_processed_v2(reason)
    else:
        all_possible_reasons_lower = [reason]
    #reason = Preprocess.get_removed_punctuation(reason)
    reason = reason.lower()
    reason_punc = Preprocess.get_removed_punctuation(reason)

    if reason:
        for cats in const.CATEGORY_NAME:
            preprocessed_reason_original = reason

            # if cats == "95320005|Disorder of skin":
            #     chek = 0


            matched_concept = {}
            phrase_code = phrase_code_category.get(cats)

            if reason in phrase_code:
                original_reason_found_in_a_category = True
                matched_concept['code'] = phrase_code.get(reason).split("|")[-1]
                matched_concept['display'] = phrase_code.get(reason).split("|")[0]
                best_score = 0
                synonym = 0
                synonym_code = API.get_all_synonym_candidate(matched_concept["code"])
                synonym_code_lower = [x.lower() for x in synonym_code]
                if reason in synonym_code_lower:
                    priority = 0
                    print("       priority", cats)
                else:
                    priority = 1
                reasons_list.append(
                    {"synonym": synonym, "involved": "Seen", "priority": priority, "category": cats,
                     "matched_score": best_score,
                     "matched_concept": matched_concept['display'] + "|" + matched_concept['code'], "preprocessed_reason": preprocessed_reason_original})
                continue


            # all_possible_reasons_lower = [x.lower() for x in all_possible_reasons]

            synonym_list = all_possible_reasons_and_synonyms.get(cats)
            cat_list = cats.split('#')
            best_score = const.BEST_SCORE

            # matched_score = None
            involved = None
            synonym = 1
            pre_syn = 1
            synonym_word = ""
            pre_preprocessed_reason = ""
            only_candidate = False
            extra_order = 1
            extra_info_used = ""
            cat_original = ""

            extra_category = extra_categories.get(cats)
            cat_list += extra_category

            original_reason_found_in_a_category_extra = False

            priority = 1
            for cat in cat_list:

                # # if we found a candidate in one of the original categories, not check in the next original categories
                if original_reason_found_in_a_category_extra:
                    break
                # if we found a candidate in original categories, not check in extra categories
                if matched_concept and cat in extra_category:
                    break
                # processed_reason, result, _ = API.get_all_candidates(cat.split("|")[0], reason)

                for preprocessed_reason in all_possible_reasons_lower:

                    if original_reason_found_in_a_category and preprocessed_reason != reason:
                        # original_reason_found_in_a_category_extra = True
                        break
                    if preprocessed_reason in phrase_code:
                        matched_concept['code'] = phrase_code.get(preprocessed_reason).split("|")[-1]
                        matched_concept['display'] = phrase_code.get(preprocessed_reason).split("|")[0]
                        best_score = 0
                        synonym = 0
                        synonym_code = API.get_all_synonym_candidate(matched_concept["code"])
                        synonym_code_lower = [x.lower() for x in synonym_code]
                        if preprocessed_reason in synonym_code_lower:
                            priority = 0
                            print("       priority", cats)
                        else:
                            priority = 1
                        print("     X   CHECK NEEDED")
                        original_reason_found_in_a_category_extra = True
                        preprocessed_reason_original = preprocessed_reason
                        # reasons_list.append(
                        #     {"synonym": synonym, "involved": "Seen", "priority": priority, "category": cats,
                        #      "matched_score": best_score,
                        #      "matched_concept": matched_concept['display'] + "|" + matched_concept['code'],
                        #      "preprocessed_reason": preprocessed_reason_original})
                        break

                    result = API.call_ontoserver_extend_api(cat.split("|")[0], preprocessed_reason.strip())

                    if result is not None:

                        if len(result) == 1:
                            # matched_score = const.DIRECT_MATCHED_SCORE
                            _, allconceptid = API.get_involved_concepts(cat.split("|")[0], result[0]["code"])
                            API.call_init_transitive_closure(cats)
                            transitivec_closure_table = {}
                            if cats in involved_concepts.keys():
                                all_concpets = involved_concepts.get(cats) + allconceptid
                                all_concpets = list(set(all_concpets))
                                set_codes = API.convert_concepts_to_closure_format(all_concpets)

                                transitivec_closure_table = API.call_transitivec_closure_set_codes(cats, set_codes)

                            path = Utils.shortest_path(transitivec_closure_table, result[0]["code"], cat.split("|")[0])

                            # intersection_concepts = list(set(involved_concepts.get(cats)) & set(allconceptid))
                            #
                            # if len(intersection_concepts) != 0:
                            #     matched_score = len(intersection_concepts)
                            # else:

                            # if result[0]["code"] in main_codes.get(cats):
                            #     print("1 code was seen in gold standard", cats, cat, result[0])
                            synonym_code = API.get_all_synonym_candidate(result[0]["code"])
                            synonym_code_lower = [x.lower() for x in synonym_code]
                            if path and (len(path) < best_score or reason in synonym_code_lower):
                            # if path and len(path) < best_score:
                                cat_original = cat
                                preprocessed_reason_original = preprocessed_reason
                                only_candidate = True
                                if len(cat.split("|")) == 1:
                                    extra_info_used = cat
                                else:
                                    extra_info_used = ""

                                # synonym_reason, matched_reason = Utils.similarity_words(result[0]['display'].lower(),
                                #                                                         synonym_list)

                                # if result[0]['display'].lower() not in synonym_list:
                                #     synonym_list.append(result[0]['display'].lower())
                                # changed reason -> preprocessed_reason
                                synonym_word, synonym = Utils.similarity_words(preprocessed_reason, synonym_list)
                                # if matched:
                                #     synonym = True
                                # else:
                                #     synonym = False

                                if not pre_syn and synonym:
                                    print("Only Candidate", "category->", cats, "cat->", cat,
                                          "BEST: ", preprocessed_reason, result[0], len(path),
                                          "OLD: ", pre_preprocessed_reason, matched_concept, best_score)

                                matched_concept = result[0]
                                # matched_score = len(path)
                                involved = len(allconceptid)
                                pre_syn = synonym
                                best_score = len(path)
                                pre_preprocessed_reason = preprocessed_reason

                                if reason in synonym_code_lower:
                                    original_reason_found_in_a_category_extra = True
                                    priority = 0
                                    print("     priority")
                                    break
                            # break
                        elif len(result) > 1:
                            for counter, res in enumerate(result):

                                if counter > const.THRESHOLD:
                                    break

                                _, allconceptid = API.get_involved_concepts(cat.split("|")[0], res["code"])

                                API.call_init_transitive_closure(cats)
                                transitivec_closure_table = {}
                                if cats in involved_concepts.keys():
                                    all_concpets = involved_concepts.get(cats) + allconceptid
                                    all_concpets = list(set(all_concpets))
                                    set_codes = API.convert_concepts_to_closure_format(all_concpets)

                                    transitivec_closure_table = API.call_transitivec_closure_set_codes(cats, set_codes)

                                path = Utils.shortest_path(transitivec_closure_table, res["code"],
                                                           cat.split("|")[0])

                                # intersection_concepts = []
                                # if cats in involved_concepts:
                                # intersection_concepts = list(
                                #     set(involved_concepts.get(cats)) & set(allconceptid))

                                # if res["code"] in main_codes.get(cats):
                                #     print("2 code was seen in gold standard", cats, cat, res)
                                synonym_code = API.get_all_synonym_candidate(res["code"])
                                synonym_code_lower = [x.lower() for x in synonym_code]
                                if path and (len(path) < best_score or reason in synonym_code_lower) :
                                # if path and len(path) < best_score :
                                    preprocessed_reason_original = preprocessed_reason
                                    cat_original = cat
                                    only_candidate = False
                                    if len(cat.split("|")) == 1:
                                        extra_info_used = cat
                                    else:
                                        extra_info_used = ""

                                    # synonym_reason, matched_reason = Utils.similarity_words(res['display'].lower(),
                                    #                                                         synonym_list)
                                    # if res['display'].lower() not in synonym_list:
                                    #     synonym_list.append(res['display'].lower())
                                    synonym_word, synonym = Utils.similarity_words(preprocessed_reason, synonym_list)

                                    # if matched:
                                    #     synonym = True
                                    # else:
                                    #     synonym = False
                                    if not pre_syn and synonym:
                                        print("More Candidate", "category->", cats, "cat->", cat,
                                              "BEST: ", preprocessed_reason, res, len(path),
                                              "OLD: ", pre_preprocessed_reason, matched_concept, best_score)

                                    matched_concept = res
                                    best_score = len(path)
                                    involved = len(allconceptid)
                                    pre_syn = synonym

                                    if reason in synonym_code_lower:
                                        priority = 0
                                        print("     priority")
                                        original_reason_found_in_a_category_extra = True
                                        original_reason_found_in_a_category = True
                                        break

                                    # elif cat.split("|")[0] == res['code']:
                                #     matched_concept = res
                                #     matched_score = const.MATCHED_SCORE
                                #     break
                                if best_score <= const.MATCHED_SCORE:
                                    break
                        # if matched_score and matched_score < best_score:
                        #     best_score = matched_score

                        # If candidate's score is same as the matched score, do not check the rest possible reasons
                        if best_score <= const.MATCHED_SCORE:
                            break

                        # If original reason has a candidate, do not check the other possible reasons
                        if preprocessed_reason == reason and matched_concept:
                            original_reason_found_in_a_category = True
                            original_reason_found_in_a_category_extra = True
                            break
                    elif not matched_concept and preprocessed_reason in phrase_code:
                        matched_concept['code'] = phrase_code.get(preprocessed_reason).split("|")[-1]
                        matched_concept['display'] = phrase_code.get(preprocessed_reason).split("|")[0]
                        best_score = 0
                        synonym = 0
                        synonym_code = API.get_all_synonym_candidate(matched_concept["code"])
                        synonym_code_lower = [x.lower() for x in synonym_code]
                        if preprocessed_reason in synonym_code_lower:
                            priority = 0
                            print("       priority", cats)
                        else:
                            priority = 1
                        print("     CHECK NEEDED")
                        original_reason_found_in_a_category_extra = True
                        preprocessed_reason_original = preprocessed_reason
                        # reasons_list.append(
                        #     {"synonym": synonym, "involved": "Seen", "priority": priority, "category": cats,
                        #      "matched_score": best_score,
                        #      "matched_concept": matched_concept['display'] + "|" + matched_concept['code'],
                        #      "preprocessed_reason": preprocessed_reason_original})
                        break

            if best_score == const.BEST_SCORE:
                synonym_list = all_possible_reasons_and_synonyms.get(cats)
                synonym_word, matched = Utils.similarity_words(reason, synonym_list)
                if not matched:
                    best_score = 0
                    code = phrase_code.get(synonym_word)
                    if code:
                        matched_concept = {"display": phrase_code.get(synonym_word).split("|")[0], "code": phrase_code.get(synonym_word).split("|")[-1]}
                    else:
                        matched_concept = {"display": synonym_word, "code": "None"}
                    involved = "Vocab"
                    synonym = 0

            if matched_concept:
                # synonym_code = API.get_all_synonym_candidate(matched_concept["code"])
                # synonym_code_lower = [x.lower() for x in synonym_code]
                # if reason in synonym_code_lower:
                #     priority = 0
                #     print("       priority")
                # else:
                #     priority = 1

                if not synonym and not priority and reason_punc in phrase_code:
                    print(" XXX")
                    matched_concept['code'] = phrase_code.get(reason_punc).split("|")[-1]
                    matched_concept['display'] = phrase_code.get(reason_punc).split("|")[0]
                    best_score = 0
                    synonym = 0
                    synonym_code = API.get_all_synonym_candidate(matched_concept["code"])
                    synonym_code_lower = [x.lower() for x in synonym_code]
                    if reason_punc in synonym_code_lower:
                        priority = 0
                        print("     priority", cats)
                    else:
                        priority = 1

                    reasons_list.append(
                        {"synonym": synonym, "involved": "Seen", "priority": priority, "category": cats,
                         "matched_score": best_score,
                         "matched_concept": matched_concept['display'] + "|" + matched_concept['code'],
                         "preprocessed_reason": preprocessed_reason_original})
                    continue

                if len(extra_info_used) > 0:

                    reasons_list.append({"synonym": synonym, "involved": involved, "priority": priority,
                                         "category": extra_info_used + " (extra info)- " + cats,
                                         "cat_original": cat_original,
                                         "matched_score": best_score,
                                         "matched_concept": matched_concept['display'] + "|" + matched_concept['code'],
                                         "only_candidate": only_candidate, "synonym_word": synonym_word,
                                         "preprocessed_reason": preprocessed_reason_original})
                else:

                    reasons_list.append(
                        {"synonym": synonym, "involved": involved, "priority": priority,
                         "category": cats , "cat_original": cat_original,
                         "matched_score": best_score,
                         "matched_concept": matched_concept['display'] + "|" + matched_concept['code'],
                         "only_candidate": only_candidate, "synonym_word": synonym_word,
                         "preprocessed_reason": preprocessed_reason_original})
        if original_reason_found_in_a_category:
            reasons_list_new = []
            for reason_l in reasons_list:
                if not ("preprocessed_reason" in reason_l and reason_l["preprocessed_reason"] != reason):
                    reasons_list_new.append(reason_l)

            reasons_list = reasons_list_new

        check_true = False
        other_check = False
        for reason_l in reasons_list:
            if reason_l["preprocessed_reason"] in const.CHECK_LIST:
                check_true = True
            else:
                other_check = True
        if check_true and other_check:
            reasons_list_new = []
            for reason_l in reasons_list:
                if not reason_l["preprocessed_reason"] in const.CHECK_LIST:
                    reasons_list_new.append(reason_l)
            reasons_list = reasons_list_new

    return reasons_list, all_possible_reasons_lower


def predict(reason, mm):
    matched_concepts, all_possible_reasons_lower = check_categories_distance(reason)
    matched_concepts_final = []
    if not matched_concepts:
        # multi_words = phrasemachine.get_phrases(reason)
        # list_mv = list(multi_words['counts'])

        list_mv, _ = metamap.annotate(reason, mm)
        # list_mv = ["check", "x ray"]
        # list_mv_order = sorted(list_mv, key=len, reverse=True)

        for reason_s in list_mv:
            if reason_s != reason and reason_s not in all_possible_reasons_lower and Preprocess.check_string_has_alphabet(reason_s) and not Preprocess.is_stopwords(reason_s) and len(reason_s) >= 2:
                matched_concepts, _ = check_categories_distance(reason_s, preprocessing=False)
                if matched_concepts:
                    print("found in split reason metamap: ", reason_s)
                    matched_concepts_final += matched_concepts
        matched_concepts = matched_concepts_final

    if not matched_concepts:
        reason_split = reason.split()
        for reason_s in reason_split:
            if Preprocess.check_string_has_alphabet(reason_s) and not Preprocess.is_stopwords(reason_s) and len(reason_s) >= 2:
                matched_concepts, _ = check_categories_distance(reason_s)
                if matched_concepts:
                    print("found in split reason: ", reason_s)
                    break



    return matched_concepts
    # if matched_concept:
    #     return category, matched_concept
    # else:
    #     category, matched_concept = check_subcategories(reason)
    #     return category, matched_concept


if __name__ == '__main__':

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    logging.info('Staring time:' + current_time)

    seen_rfv = Utils.get_seen_rfv(phrase_code_category)

    all_seen_reasons = Utils.get_seen_reason()

    prediction_xlsx = os.path.join(Utils.output_dir, "prediction.xlsx")
    workbook_prediction = xlsxwriter.Workbook(prediction_xlsx)
    worksheet_analysis = workbook_prediction.add_worksheet("Prediction")

    # prediction_xlsx_normolized = os.path.join(Utils.data_dir, "prediction_normolized.xlsx")
    # workbook_prediction_normolized = xlsxwriter.Workbook(prediction_xlsx_normolized)
    # worksheet_analysis_normolized = workbook_prediction_normolized.add_worksheet("Prediction")

    worksheet_analysis.write(0, 0, "Reason")
    # worksheet_analysis_normolized.write(0, 0, "Reason")

    mm = MetaMap.get_instance("/metamap/public_mm/bin/metamap20")

    all_unseen_reason = []

    reasons_freq = Utils.read_cats_reason(os.path.join(Utils.input_dir, "Reasons_Freq.csv"))
    reasons = reasons_freq['Var1'].dropna()

    # reasons = ["care plans"]

    # try:
    all_result = {}
    row = 0

    count_seen_in_gold_standard = 0
    count_cannot_found = 0
    count_duplicated_in_unseen_pharase = 0
    count_error = 0

    highest_distance = const.MATCHED_SCORE
    matched_concepts_json = json.load(open(os.path.join(Utils.data_dir, 'matched_concepts.json')))
    # os.remove(os.path.join(Utils.data_dir, 'matched_concepts.json'))
    # outfile = open(os.path.join(Utils.data_dir, 'matched_concepts.json'), 'w')
    # outfile.write("{\n")
    total = 0
    saved_counter = 0

    for number, reason in enumerate(reasons):
        logging.info('RFV: ' + reason)

        original_reason = reason

        print(number, reason)
        reason = reason.strip()
        # reason = Preprocess.get_preprocess_prediction(reason)
        # reason = "Ankle pain"
        # if number == 1:
        #     break
        total = number
        true_synonym = 0
        try:

            # if original_reason in const.SEEN_UNSEEN:
            #     continue

            # if reason.lower() in all_seen_reasons:
            #     count_seen_in_gold_standard += 1
            #     continue
            #
            # if reason.lower() in all_unseen_reason:
            #     count_duplicated_in_unseen_pharase += 1
            #     continue
            matched_concept = []
            if reason.lower() in seen_rfv:
                for category in seen_rfv.get(reason.lower()):
                    matched_concept.append(
                    {"synonym": 1, "involved": "Seen", "priority": 1, "category": category,
                     "matched_score": 0,
                     "matched_concept":  "-|-", "preprocessed_reason": ""})

            elif reason.lower() in matched_concepts_json:
                matched_concept = matched_concepts_json.get(reason.lower())
            elif reason.lower() in predicted_rfv:
                matched_concept = predicted_rfv.get(reason.lower())
            else:
                matched_concept = predict(reason, mm)
                matched_concepts_json[reason.lower()] = matched_concept
            # print(matched_concept)
            #
            # if number != 0 and saved_counter != 0:
            #     outfile.write(",")
            # saved_counter += 1
            # outfile.write("\"" + str(number) + "_" + reason + "\"" + ":" + json.dumps(matched_concept))
            #
            #
            #
            # all_unseen_reason.append(reason.lower())
            #
            # # matched_concept = None
            #
            # # if matched_concept:
            # #     all_result[reason] = matched_concept
            # #
            # #     vars_ordered = sorted(matched_concept, key=lambda entity: entity['matched_score'])
            # #     highest_score_list = vars_ordered[-1]['matched_score']
            # #     if highest_score_list > highest_distance:
            # #         highest_distance = highest_score_list
            # # else:
            # #     all_result[reason] = None
            #
            logging.info(matched_concept)
            seen_categories = []
            if matched_concept:
                vars_ordered = sorted(matched_concept, key=lambda entity: (entity['synonym'], entity['priority'], entity['matched_score']))

                for column, reason_cat_score in enumerate(vars_ordered):
                    if not reason_cat_score['synonym']:
                        true_synonym += 1

                    if true_synonym > 1:
                        print("more than one true: ", reason, reason_cat_score['category'],
                              reason_cat_score['matched_concept'])
                        true_synonym -= 1



                    score = reason_cat_score['matched_score']
                    # confidence = score * 95 / (highest_score_list+2)
                    # print(confidence)
                    # Confidence = reason_cat_score['matched_score']

                    if column == 0:
                        worksheet_analysis.write(row + 1, 0, reason)

                    # if highest_score >= 50:
                    #     break
                    if reason_cat_score['category'] not in seen_categories:
                        seen_categories.append(reason_cat_score['category'])
                        worksheet_analysis.set_column(column + 1, column + 1, 40)
                        worksheet_analysis.write(0, column + 1, "Category")
                        worksheet_analysis.write(row + 1, column + 1, const.CATEGORY_NAME_MAP.get(reason_cat_score['category']))

                    # worksheet_analysis.set_column(column * 6 + 5, column * 6 + 5, 40)
                    # worksheet_analysis.set_column(column * 6 + 6, column * 6 + 6, 30)
                    # if reason_cat_score['preprocessed_reason'] != reason.lower():
                    #     worksheet_analysis.write(row + 1, column * 6 + 1, reason_cat_score['preprocessed_reason'])
                    #
                    # worksheet_analysis.write(row + 1, column * 6 + 2, score)
                    # if reason_cat_score['priority'] == 0:
                    #     worksheet_analysis.write(row + 1, column * 6 + 3, "priority")
                    # else:
                    #     worksheet_analysis.write(row + 1, column * 6 + 3, reason_cat_score['involved'])
                    # worksheet_analysis.write(row + 1, column * 6 + 4,
                    #                          True if not reason_cat_score['synonym'] else False)
                    # worksheet_analysis.write(row + 1, column * 6 + 5, reason_cat_score['category'])
                    # worksheet_analysis.write(row + 1, column * 6 + 6, reason_cat_score['matched_concept'])
                    #
                    # worksheet_analysis.write(0, column * 6 + 1, "Subword")
                    # worksheet_analysis.write(0, column * 6 + 2, "Ontological Distance")
                    # worksheet_analysis.write(0, column * 6 + 3, "#Involved Concepts")
                    # worksheet_analysis.write(0, column * 6 + 4, "Seen in Gold Standard (Synonyms)")
                    # worksheet_analysis.write(0, column * 6 + 5, "Category")
                    # worksheet_analysis.write(0, column * 6 + 6, "ConceptID")
            else:
                count_cannot_found += 1
                worksheet_analysis.write(row + 1, 0, reason)

            row += 1
        except Exception as e:
            # count_error += 1
            print("Error Happened: ", reason, "error", e)
            continue

    workbook_prediction.close()
    json.dump(matched_concepts_json, open(os.path.join(Utils.data_dir, "matched_concepts.json"), 'w'))
    # outfile.write("}")
    # outfile.close()
    # print("count_cannot_found:", count_cannot_found,
    #       "\ncount_seen_in_gold_standard:", count_seen_in_gold_standard,
    #       "\ncount_duplicated_in_unseen_pharase", count_duplicated_in_unseen_pharase,
    #       "\ncount_error", count_error,
    #         "\nTotal", total+1)

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    logging.info('Ending Time: ' + current_time)

