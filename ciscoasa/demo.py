#!/usr/local/bin/python3
from ciscoconfparse import CiscoConfParse


class ASA_Obj:
    def __init__(self, name, type, group=0):
        self.name = name
        self.type = type
        self.group = group
        self.children = []

    @staticmethod
    def search_objects(config) -> dict:
        if not isinstance(config, CiscoConfParse):
            # print("CiscoConfParse Object is required.")
            return None

        obj_dict = dict()
        for obj in config.find_objects('^object'):
            obj_line = obj.text.split(" ")
            # object or object-group xxx
            isgroup = 0 if obj_line[0] == "object" else 1
            # 创建 ASA 自定义对象
            asa_obj = ASA_Obj(' '.join(obj_line[2:]), obj_line[1], isgroup)
            if not obj.children:
                continue
            for item in obj.children:
                asa_obj.add_child(item.text.strip())
            if not obj_dict.get(str(asa_obj)):
                obj_dict[str(asa_obj)] = []
            obj_dict[str(asa_obj)].append(asa_obj)
        return obj_dict

    def add_child(self, obj):
        self.children.append(obj)

    def rm_child(self, obj):
        if obj in self.children:
            self.children.pop(obj)

    def __str__(self) -> str:
        return self.name


config = CiscoConfParse("conf/dmz-asa.txt", syntax="asa")
obj_all = ASA_Obj.search_objects(config)

for name, item in obj_all.items():
    print(name)
    for i in item:
        print('\n'.join(i.children))
    
