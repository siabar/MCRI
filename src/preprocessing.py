import re
import string
import inflect
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


class Preprocess:
    # nltk.download('stopwords')
    # nltk.download('wordnet')

    delimiters = "(&", "(+", " - ", "/", ";", "*", ",", "+", "-"
    regexPattern = '|'.join(map(re.escape, delimiters))

    p = inflect.engine()
    wordnet_lemmatizer = WordNetLemmatizer()

    @staticmethod
    def get_lemma(candidate):
        lemma = Preprocess.wordnet_lemmatizer.lemmatize(candidate, pos="n")

        return lemma.strip()

    @staticmethod
    def get_split(candidate):
        candidates = re.split(Preprocess.regexPattern, candidate)
        if len(candidates) > 1:
            candidates = [candidates[0].strip()] + [candidates[1].replace(")", "").strip()]
            return candidates
        return []

    @staticmethod
    def get_removed_punctuation(candidate):
        regex = re.compile('[^a-zA-Z ]')
        candidate = regex.sub('', candidate)
        # for char in candidate:
        #     if char in string.punctuation:
        #         candidate = candidate.replace(char, "")
        # cand = " ".join(Preprocess.get_split(candidate))
        # if cand == "":
        #     cand = candidate
        return candidate.strip()


    @staticmethod
    def get_removed_non_char(candidate):
        regex = re.compile('[^a-zA-Z]')
        candidate = regex.sub('', candidate)
        return candidate.strip()

    @staticmethod
    def get_removed_view_plan_investigation(candidate):
        candidate = candidate.replace("review", "").replace("investigation", "").replace("action", "")
        # regex = re.compile('[^a-zA-Z ]')
        # candidate = regex.sub('', candidate)
        # for char in candidate:
        #     if char in string.punctuation:
        #         candidate = candidate.replace(char, "")
        # cand = " ".join(Preprocess.get_split(candidate))
        # if cand == "":
        #     cand = candidate
        return candidate.strip()


    @staticmethod
    def get_split_slash(candidate):
        candidates = candidate.split("/")
        if len(candidates) <= 1:
            return []
        if len(candidates) == 2:
            left = candidates[0].split()
            right = candidates[1].split()
            if len(left) == len(right) or not (len(left) == 1 or len(right) == 1):
                return candidates
            if len(left) > len(right):
                origin = left.copy()
                left[-1] = right[0]
                return [" ".join(origin), " ".join(left)]
            if len(left) < len(right):
                origin = right.copy()
                right[0] = left[0]
                return [" ".join(right), " ".join(origin)]

        if len(candidates) > 2:
            return candidates

    @staticmethod
    def get_singular(candidate):
        singular = Preprocess.p.singular_noun(candidate)
        if singular:
            return singular
        return candidate

    @staticmethod
    def get_exist(candidate, candidates):
        if candidate.strip().lower() not in candidates and Preprocess.check_string_has_alphabet(candidate):
            candidates.append(candidate.strip().lower())
        return candidates

    @staticmethod
    def detect_extra_information(reason, candidate):
        temp = reason.split('(')
        if len(temp)>1:
            cleaned_temp = Preprocess.get_removed_punctuation(temp[1])
            if cleaned_temp.isupper():
                candidate = Preprocess.get_exist(temp[0].lower().strip(), candidate)
                candidate = Preprocess.get_exist(cleaned_temp.lower().strip(), candidate)
                # candidate.append(temp[0].lower().strip())
                # candidate.append(cleaned_temp.lower().strip())

            else:
                candidate = Preprocess.get_exist(temp[0].lower().strip(), candidate)
                # candidate.append(temp[0].lower().strip())

        return temp[0], candidate


    @staticmethod
    def get_pre_post_processed_v2(reason, synonym=False):
        # reason = "Impetigo / school sores"
        candidates = [reason.lower()]

        # remove 'reviews, plan, investigation,
        removed_view_plan_investigation = Preprocess.get_removed_view_plan_investigation(reason)
        candidates = Preprocess.get_exist(removed_view_plan_investigation, candidates)

        # Remove punctuation
        removed_punct = Preprocess.get_removed_punctuation(reason)
        candidates = Preprocess.get_exist(removed_punct, candidates)

        # -> Removed punctuation lemma
        removed_punct_list = removed_punct.split()
        for index, candidate in enumerate(removed_punct_list):
            removed_punct_list[index] = Preprocess.get_lemma(candidate)
        candidates = Preprocess.get_exist(" ".join(removed_punct_list), candidates)

        # -> Removed punctuation singular
        removed_punct_list = removed_punct.split()
        for index, candidate in enumerate(removed_punct_list):
            removed_punct_list[index] = Preprocess.get_singular(candidate)
        candidates = Preprocess.get_exist(" ".join(removed_punct_list), candidates)

        # Find extra information that includes parenthesis "("
        pure_candidate, candidates = Preprocess.detect_extra_information(reason, candidates)

        if not synonym:
            # Find all possible combination with slash  "Impetigo / school sores" -> Impetigo or Impetigo sores
            split_slash_list = Preprocess.get_split_slash(pure_candidate)
            split_slash_list_other = split_slash_list.copy()

            for candidate in split_slash_list:
                candidates = Preprocess.get_exist(candidate, candidates)

            # -> remove punctuation from all candidates of slash
            for index, candidate in enumerate(split_slash_list):
                split_slash_list[index] = Preprocess.get_removed_punctuation(candidate)
            for candidate in split_slash_list:
                candidates = Preprocess.get_exist(candidate, candidates)

            # -> get all lemma of candidates of slash
            split_slash_list_copy = split_slash_list.copy()
            for i, candidate in enumerate(split_slash_list_copy):
                candidate_list = candidate.split()
                for j, cand in enumerate(candidate_list):
                    candidate_list[j] = Preprocess.get_lemma(cand)
                split_slash_list_copy[i] = " ".join(candidate_list)
            for candidate in split_slash_list_copy:
                candidates = Preprocess.get_exist(candidate, candidates)

            # -> get all singular of candidates of slash
            split_slash_list_copy = split_slash_list.copy()
            for i, candidate in enumerate(split_slash_list_copy):
                candidate_list = candidate.split()
                for j, cand in enumerate(candidate_list):
                    candidate_list[j] = Preprocess.get_singular(cand)
                split_slash_list_copy[i] = " ".join(candidate_list)
            for candidate in split_slash_list_copy:
                candidates = Preprocess.get_exist(candidate, candidates)


            # If we do not have any slash candidate, select pure candidate (removed parenthesis) as a candidate
            need_split_list = split_slash_list_other.copy()
            if len(need_split_list) == 0:
                need_split_list = [pure_candidate]
        else:
            need_split_list = [pure_candidate]

        # Split the slash candidates or reason by specific punctuations
        split_list = []
        for split_l in need_split_list:
            split_list += Preprocess.get_split(split_l)
        for candidate in split_list:
            candidates = Preprocess.get_exist(candidate, candidates)

        # -> lemma for Split the slash candidates or reason by specific punctuations
        split_list_copy = split_list.copy()
        for i, candidate in enumerate(split_list_copy):
            candidate_list = candidate.split()
            for j, cand in enumerate(candidate_list):
                candidate_list[j] = Preprocess.get_lemma(cand)
            split_list_copy[i] = " ".join(candidate_list)
        for candidate in split_list_copy:
            candidates = Preprocess.get_exist(candidate, candidates)

        # -> Singular for Split the slash candidates or reason by specific punctuations
        split_list_copy = split_list.copy()
        for i, candidate in enumerate(split_list_copy):
            candidate_list = candidate.split()
            for j, cand in enumerate(candidate_list):
                candidate_list[j] = Preprocess.get_singular(cand)
            split_list_copy[i] = " ".join(candidate_list)

        for candidate in split_list_copy:
            candidates = Preprocess.get_exist(candidate, candidates)

        return candidates

    @staticmethod
    def get_pre_processed(reason):
        candidates = [reason.lower()]

        # ->  lemma
        reason_list = reason.split()
        for index, candidate in enumerate(reason_list):
            reason_list[index] = Preprocess.get_lemma(candidate)
        candidates = Preprocess.get_exist(" ".join(reason_list), candidates)

        # -> singular
        reason_list = reason.split()
        for index, candidate in enumerate(reason_list):
            reason_list[index] = Preprocess.get_singular(candidate)
        candidates = Preprocess.get_exist(" ".join(reason_list), candidates)


        return candidates

    @staticmethod
    def get_pre_post_processed(reason):
        # reason = "Impetigo / school sores"
        candidates = [reason]
        removed_punct = Preprocess.get_removed_punctuation(reason)
        candidates = Preprocess.get_exist(removed_punct, candidates)

        removed_punct_list = removed_punct.split()
        for index, candidate in enumerate(removed_punct_list):
            removed_punct_list[index] = Preprocess.get_lemma(candidate)
        candidates = Preprocess.get_exist(" ".join(removed_punct_list), candidates)

        removed_punct_list = removed_punct.split()
        for index, candidate in enumerate(removed_punct_list):
            removed_punct_list[index] = Preprocess.get_singular(candidate)
        candidates = Preprocess.get_exist(" ".join(removed_punct_list), candidates)

        split_slash_list = Preprocess.get_split_slash(reason)
        split_slash_list_other = split_slash_list.copy()
        for candidate in split_slash_list:
            candidates = Preprocess.get_exist(candidate, candidates)

        for index, candidate in enumerate(split_slash_list):
            split_slash_list[index] = Preprocess.get_removed_punctuation(candidate)
        for candidate in split_slash_list:
            candidates = Preprocess.get_exist(candidate, candidates)

        split_slash_list_copy = split_slash_list.copy()
        for i, candidate in enumerate(split_slash_list_copy):
            candidate_list = candidate.split()
            for j, cand in enumerate(candidate_list):
                candidate_list[j] = Preprocess.get_lemma(cand)
            split_slash_list_copy[i] = " ".join(candidate_list)
        for candidate in split_slash_list_copy:
            candidates = Preprocess.get_exist(candidate, candidates)

        split_slash_list_copy = split_slash_list.copy()
        for i, candidate in enumerate(split_slash_list_copy):
            candidate_list = candidate.split()
            for j, cand in enumerate(candidate_list):
                candidate_list[j] = Preprocess.get_singular(cand)
            split_slash_list_copy[i] = " ".join(candidate_list)
        for candidate in split_slash_list_copy:
            candidates = Preprocess.get_exist(candidate, candidates)

        need_split_list = split_slash_list_other.copy()
        if len(need_split_list) == 0:
            need_split_list = [reason]

        split_list = []
        for split_l in need_split_list:
            split_list += Preprocess.get_split(split_l)

        for candidate in split_list:
            candidates = Preprocess.get_exist(candidate, candidates)

        split_list_copy = split_list.copy()
        for i, candidate in enumerate(split_list_copy):
            candidate_list = candidate.split()
            for j, cand in enumerate(candidate_list):
                candidate_list[j] = Preprocess.get_lemma(cand)
            split_list_copy[i] = " ".join(candidate_list)
        for candidate in split_list_copy:
            candidates = Preprocess.get_exist(candidate, candidates)

        split_list_copy = split_list.copy()
        for i, candidate in enumerate(split_list_copy):
            candidate_list = candidate.split()
            for j, cand in enumerate(candidate_list):
                candidate_list[j] = Preprocess.get_singular(cand)
            split_list_copy[i] = " ".join(candidate_list)
        for candidate in split_list_copy:
            candidates = Preprocess.get_exist(candidate, candidates)

        return candidates

    @staticmethod
    def get_not_processed(reason):
        candidate = [reason]
        return candidate

    @staticmethod
    def get_preprocess_prediction(reason):
        reason = reason.replace("?", "")
        return reason

    @staticmethod
    def check_string_has_alphabet(reason):
        candidate = Preprocess.get_removed_non_char(reason)
        result = candidate.isalpha()
        return result

    @staticmethod
    def is_stopwords(reason):
        if reason.lower() in stopwords.words('english'):
            return True
        else:
            return False

