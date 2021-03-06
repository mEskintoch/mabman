import json
import os
import numpy as np


def _json_type_conversions(v):
    if isinstance(v, np.ndarray):
        return v.tolist()
    else:
        return v


def arm_components(arms):
    """
    Get arm weights as list of dicts.
    param arms: List[Arm]
    :return:
        List[Dict]
    """
    return [
        {'name': arm.name,
         'weights': {k: _json_type_conversions(v) for k, v in arm.__dict__.items() if k != 'name'}
         }
        for arm in arms
    ]


def experiment_params(experiment):
    return {k: _json_type_conversions(v) for k, v in experiment.__dict__.items()}


def agent_params(agent):
    return {'name': agent.__class__.name,
            'params': {k: _json_type_conversions(v) for k, v in agent.__dict__.items()
                       if k not in ['callbacks', 'arms', 'experiment', 'env']
                       and not k.startswith('_')
                       }
            }


def agent_component_weights(agent):
    """
    Divides to agent / process into three
    functional parts:
        arms, experiment, parameters
    :param agent: process.Process / Agent
    :return:
        Tuple(List[Arm], Experiment, Dict)
    """
    return {
        'arm': arm_components(agent.__dict__.get('arms', [])),
        'experiment': experiment_params(agent.__dict__.get('experiment', None)),
        'agent': agent_params(agent)
    }


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)


def read_json(path):
    file = open(path, 'r')
    data = json.load(file)
    file.close()
    return data


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

