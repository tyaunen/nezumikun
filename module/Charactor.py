import yaml
import os

class Charactor:
    """
    キャラクターの設定などを管理するファイル
    現在は起動時にのみファイルを読み込むため、随時プロンプトを更新したい場合は
    このファイルを変更するのがよい
    """
    def __init__(self):
        self.save_object = {}
        self.file_path = "./charactor.yaml"
        self.load_file()


    def load_file(self):
        """
        YAMLファイルを読み込む
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    self.save_object = yaml.load(f, Loader=yaml.FullLoader)  # YAMLファイルを読み込む
                except yaml.YAMLError:
                    pass  # 破損している場合はリセット

    def get_sample_message(self):
        return self.save_object["message_sample"]

    def get_system_role(self, props):
        return self.save_object["system_role"].format(**props)