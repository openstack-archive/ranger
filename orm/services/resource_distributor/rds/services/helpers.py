import re
import yaml


def create_final_yaml(title, description, resources, outputs):
    """put all yaml strings together.

    :param title: ther version of yaml
    :param description: file description
    :param resources: body of the yaml file
    :param outputs: the output of the yaml
    :return: the full string of yaml file
    """
    title_yaml = re.sub("'", "", yaml.dump(title, default_flow_style=False)).strip()
    description_yaml = yaml.dump(description, default_flow_style=False).strip()
    resources_yaml = re.sub(r"'{,2}", '',
                            yaml.dump(resources, default_flow_style=False)).strip()
    outputs_yaml = yaml.dump(outputs).strip()

    return '\n'.join([
        title_yaml,
        description_yaml,
        resources_yaml,
        outputs_yaml
    ])
