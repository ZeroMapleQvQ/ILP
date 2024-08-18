import json
from pathlib import Path


class Config:
    def __init__(self, file_path=None):
        self.file_path = Path(file_path)
        if file_path != None:
            if not self.file_path.exists():
                self.init_cfg()
            self.read_cfg()
            self.load_cfg(self.__cfg)
            self.check_cfg()

    def read_cfg(self):
        with open("config.json", "r", encoding="utf-8") as f:
            self.__cfg = json.loads(f.read())
        return self.__cfg

    def load_cfg(self, cfg):
        for key, value in cfg.items():
            if isinstance(value, dict):
                setattr(self, key, self.load_cfg(value))
            elif isinstance(value, list):
                setattr(self, key, [self.load_cfg(item) if isinstance(
                    item, dict) else item for item in value])
            else:
                setattr(self, key, value)
        return self

    def check_cfg(self):
        DATA_PATH = Path(self.PATHS.DATA_PATH)
        LOGS_PATH = Path(self.PATHS.LOGS_PATH)
        NOVELS_PATH = Path(self.PATHS.NOVELS_PATH)
        NOVELS_NEW_PATH = Path(self.PATHS.NOVELS_NEW_PATH)
        POSTERS_PATH = Path(self.PATHS.POSTERS_PATH)
        DB_PATH = Path(self.PATHS.DB_PATH)
        self.PATHS.DATA_PATH = DATA_PATH
        self.PATHS.LOGS_PATH = DATA_PATH/LOGS_PATH
        self.PATHS.NOVELS_PATH = DATA_PATH/NOVELS_PATH
        self.PATHS.NOVELS_NEW_PATH = DATA_PATH/NOVELS_NEW_PATH
        self.PATHS.POSTERS_PATH = DATA_PATH/POSTERS_PATH
        self.PATHS.DB_PATH = DB_PATH

        self.PATHS.DATA_PATH.mkdir(exist_ok=True)
        self.PATHS.LOGS_PATH.mkdir(exist_ok=True)
        self.PATHS.NOVELS_PATH.mkdir(exist_ok=True)
        self.PATHS.NOVELS_NEW_PATH.mkdir(exist_ok=True)
        self.PATHS.POSTERS_PATH.mkdir(exist_ok=True)

    def init_cfg(self):
        cfg_dict = {
            "PATHS": {
                "DATA_PATH": "./data",
                "NOVELS_PATH": "novels",
                "NOVELS_NEW_PATH": "novels_new",
                "LOGS_PATH": "logs",
                "POSTERS_PATH": "posters",
                "DB_PATH": "novels.db"
            },
            "MAX_WORKERS": 7,
            "SLEEP_TIME": 0.2,
            "sites": ["fanqie", "qidian"]
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(cfg_dict, indent=4))


if __name__ == '__main__':
    cfg = Config("config.json")
