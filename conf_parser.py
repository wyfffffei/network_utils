import os
from tqdm import tqdm


class NetworkObject(object):
    # 解析的内容
    __parsed_line = []

    def __init__(self, path) -> None:
        self.path = path                            # 配置路径
        self.annotation = []                       # 配置头（注释）
        self.policy = []                            # 策略源数据
        self.configuration = []                     # 配置源数据
        self.parsed_policy = {}                     # 策略（解析后）
        self.parsed_configuration = {}              # 配置（解析后）

    def parse_policy(self) -> any:
        pass

    def _check_anno(self, line) -> bool:
        if line and isinstance(line, str) and line[0] == '#':
            return 1
        return 0
    
    def _parse_ANNO(self, line) -> None:
        self.annotation.append(line)


class FortiGate(NetworkObject):
    # 解析的内容
    __parsed_line = ['#', 'config', 'end', 'edit', 'next', 'set', 'unset']

    def __init__(self, path, max_level=10):
        NetworkObject.__init__(self, path)
        # 支持最大的缩进层级数（飞塔防火墙）
        self.max_level = max_level
        
    def parse_policy(self) -> dict:
        if not os.path.exists(self.path):
            print("File path is invalid.")
            return None
        
        with open(self.path, 'r', encoding="utf-8") as f:
            self.policy = f.readlines()

        level = 1                                   # 缩进层级
        _line_Buf = {}                              # 配置缓冲区
        _out_Buf = {}                               # 配置合并缓冲区
        for i in range(self.max_level):             # 缓冲区初始化
            _line_Buf.update({i+1: []})
            _out_Buf.update({i+1: []})

        for line in tqdm(self.policy):
            line = line.strip()

            if self._check_anno(line):
                self._parse_ANNO(line)

            elif line[:7] == "config " or line[:5] == "edit ":
                _line_Buf[level].append(line)
                level += 1

            elif line[:4] == "next" or line[:3] == "end":
                level -= 1
                _out_Buf[level].append({
                    _line_Buf[level].pop(-1): _line_Buf[level + 1] + _out_Buf[level + 1]
                })
                _line_Buf[level + 1] = []
                _out_Buf[level + 1] = []

            elif line[:4] == "set " or line[:6] == "unset ":
                _line_Buf[level].append(line)

            else:
                # private-key
                pass
        
        # 解析后的文件重新格式化
        for p in _out_Buf[1]:
            self.parsed_policy.update(p)

        del _line_Buf, _out_Buf
        return {"ANNOTATION": self.annotation, "CONFIG": self.parsed_policy}


class CheckPoint(NetworkObject):
    # 解析的内容
    __parsed_line = ["save configuration"]

    def __init__(self, path):
        NetworkObject.__init__(self, path)

    def parse_configuration(self) -> dict:
        if not os.path.exists(self.path):
            print("File path is invalid.")
            return None
        
        with open(self.path, 'r', encoding="utf-8") as f:
            self.configuration = f.readlines()

        for line in tqdm(self.configuration):
            line = line.strip()

            if self._check_anno(line):
                self._parse_ANNO(line)
                continue
            line = line.split(" ")
            self._iter_parse(line)

        return self.parsed_configuration

    def _iter_parse(self, line):
        p = self.parsed_configuration
        for item in line:
            if p.get(item):
                p = p[item]
                continue
            p[item] = {}
            p = p[item]


if __name__ == "__main__":
    CP = CheckPoint("doc/gaia_os_cp_gw.txt")
    conf = CP.parse_configuration()
    print(conf["set"]["installer"]["policy"])

