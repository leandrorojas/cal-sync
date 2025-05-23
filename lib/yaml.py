import yaml

class YAMLConfig:
    __yaml_file = None

    @property
    def yaml_file(self):
        return self.__yaml_file

    @yaml_file.setter
    def yaml_file(self, value):
        self.__yaml_file = value

    def read_yaml_setting(self, section:str, key:str):
        with open(self.yaml_file) as local_yaml_file:
            yaml_config = yaml.safe_load(local_yaml_file)

            return yaml_config[section][key]