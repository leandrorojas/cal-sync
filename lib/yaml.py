import yaml

class YAMLConfig:
    __yaml_file = None

    @property
    def yaml_file(self):
        global __yaml_file
        return __yaml_file

    @yaml_file.setter
    def yaml_file(self, value):
        global __yaml_file
        __yaml_file = value

    def read_yaml_setting(self, section:str, key:str):
        with open(self.yaml_file) as local_yaml_file:
            yaml_config = yaml.safe_load(local_yaml_file)

            return yaml_config[section][key]