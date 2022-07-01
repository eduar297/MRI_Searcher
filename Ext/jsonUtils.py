import json

class Utils:
    def save_as_json(data,name):
        with open("Jsons/"+name+".json","w",encoding="utf8", errors="ignored") as fb:
            json.dump(data, fb)

    def get_json_as_dict(name):
        with open("Jsons/"+name+".json","r", encoding="utf8", errors="ignored") as fb:
            return json.load(fb)