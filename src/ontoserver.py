import requests
from preprocessing import Preprocess
from utility import Utils


class API:

    #sct = "http://snomed.info/sct/32506021000036107/version/20210331"
    sct = "http://snomed.info/sct"
    server = "100.1000.0.1:8080"

    @staticmethod
    def call_ontoserver_extend_api(category, reason):
        url = "http://" + API.server + "/fhir/ValueSet/$expand?url=" + API.sct + "?"
        _filter = reason

        payload = "<file contents here>"
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url + "fhir_vs=" + "ecl/<<" + category + "&filter" + "=" + _filter,
                                    headers=headers, data=payload)

        result = response.json()

        if 'expansion' in result.keys() and 'contains' in result['expansion'].keys():
            return result['expansion']['contains']
        return None


    # @staticmethod
    # def call_ontoserver_valueset_parent_api(code):
    #     url = "https://r4.ontoserver.csiro.au/fhir/CodeSystem/$lookup?system=http://snomed.info/sct" + "&version=" + API.sct + "&property=parent&"
    #     # url = "https://r4.ontoserver.csiro.au/fhir/CodeSystem/$lookup?system=http://snomed.info/sct" + "&property=parent&"
    #
    #     payload = "<file contents here>"
    #     headers = {
    #         'Content-Type': 'text/plain'
    #     }
    #
    #     response = requests.request("GET", url + "code=" + code,
    #                                 headers=headers, data=payload)
    #
    #     result = response.json()
    #
    #     all_parents = []
    #
    #     if 'parameter' in result.keys():
    #         for parameter in result["parameter"]:
    #             if parameter.get("name") == "property" and "part" in parameter.keys():
    #                 for part in parameter["part"]:
    #                     if part.get("name") == "value" and "valueCode" in part.keys():
    #                         all_parents.append(part.get("valueCode"))
    #     return all_parents

    @staticmethod
    def call_init_transitive_closure(category):
        url = "http://" + API.server + "/fhir/$closure"

        payload = {"resourceType": "Parameters",
                   "parameter": [
                       {
                           "name": "name",
                           "valueString": category
                       }
                   ]
                   }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=str(payload))

        return response.text

    @staticmethod
    def call_all_transitive_closure(category):
        url = "http://" + API.server + "/fhir/$closure"

        payload = {"resourceType": "Parameters",
                   "parameter": [
                       {
                           "name": "name",
                           "valueString": category
                       },
                        {
                          "name" : "version",
                          "valueId" : "0"
                        }
                   ]
                   }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=str(payload))

        result = response.json()

        if 'group' in result.keys() and 'element' in result['group'][0].keys():
            return result['group'][0]['element']
        return None

    @staticmethod
    def convert_concepts_to_closure_format(set_codes):
        list_codes = []
        for code in set_codes:
            closure_format = {
                "name": "concept",
                "valueCoding": {
                    "system": API.sct,
                    "code": code
                }
            }
            list_codes.append(closure_format)
        return list_codes

    @staticmethod
    def call_transitivec_closure_set_codes(category, set_codes):

        url = "http://" + API.server + "/fhir/$closure"

        parameter = [
            {
            "name": "name",
            "valueString": category
        }
        ]
        parameter += set_codes
        payload = {"resourceType": "Parameters",
                   "parameter": parameter
                   }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=str(payload))

        result = response.json()

        if 'group' in result.keys() and 'element' in result['group'][0].keys():
            return result['group'][0]['element']
        return None



    @staticmethod
    def get_all_synonym_candidate(code):
        url = "http://" + API.server + "/fhir/CodeSystem/$lookup?system=http://snomed.info/sct" + "&version=" + API.sct + "&property=designation&"
        # url = "https://r4.ontoserver.csiro.au/fhir/CodeSystem/$lookup?system=http://snomed.info/sct" + "&property=designation&"

        payload = "<file contents here>"
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url + "code=" + code,
                                    headers=headers, data=payload)

        result = response.json()

        all_synonym = []

        if 'parameter' in result.keys():
            for parameter in result["parameter"]:
                if parameter.get("name") == "designation" and "part" in parameter.keys():
                    for part in parameter["part"]:
                        if part.get("name") == "value" and "valueString" in part.keys():
                            all_synonym.append(part.get("valueString").lower())
        return all_synonym

    @staticmethod
    def get_all_candidates(category, reason):
        all_possible_reasons = Preprocess.get_pre_post_processed(reason)

        # Calculate the effect of pre-processing
        # all_possible_reasons = Preprocess.get_not_processed(reason)

        all_possible_reasons_lower = [x.lower() for x in all_possible_reasons]

        for preprocessed_reasons in all_possible_reasons:
            result = API.call_ontoserver_extend_api(category, preprocessed_reasons.strip())
            if result is not None:
                return preprocessed_reasons, result, all_possible_reasons_lower
        return ", ".join(all_possible_reasons), None, None

    @staticmethod
    def get_involved_concepts(cat, code):
        url = "http://" + API.server + "/fhir/ValueSet/$expand?url=" + API.sct + "?"

        payload = "<file contents here>"
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url + "fhir_vs=" + "ecl/<<" + cat + " AND >>" + code,
                                    headers=headers, data=payload)

        result = response.json()

        if 'expansion' in result.keys() and 'contains' in result['expansion'].keys():
            allconceptid = []
            for concept in result['expansion']['contains']:
                allconceptid.append(concept.get("code"))
            return result['expansion']['contains'], allconceptid
        return None, []


if __name__ == '__main__':
    # print(API.call_init_transitive_closure("x"))
    x = ["43878008", "312422001", "312118003", "54150009", "312117008", "275498002"]
    x1 = ["43878008", "312422001", "312118003", "54150009", "312117008", "275498002"]


    # x2 = ["43878008", "312422001", "54150009", "275498002"]

    # x2 = ["106028002"]
    # set_codes = API.convert_concepts_to_closure_format(x2)
    # ontology = API.call_transitivec_closure_set_codes("x", set_codes)
    # print(ontology)

    print(API.call_init_transitive_closure("x1"))
    set_codes = API.convert_concepts_to_closure_format(x1)
    ontology = API.call_transitivec_closure_set_codes("x1", set_codes)
    print(ontology)
    path = Utils.shortest_path(ontology, "43878008", "312117008")
    print(path)
    #
    # print(API.call_init_transitive_closure("x"))
    # set_codes = API.convert_concepts_to_closure_format(x2)
    # ontology = API.call_transitivec_closure_set_codes("x", set_codes)
    # print(ontology)
    #

    # print(API.call_all_transitive_closure("x"))