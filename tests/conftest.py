#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json
from unittest import mock

# Libs
import pytest

# Custom
import synlogger

##################
# Configurations #
##################

HOST = "127.0.0.1"
PORT = 12201 # default port for general unittesting


# IS_SECURED = False
# ADDRESS = f"https://{HOST}:{PORT}" if IS_SECURED else f"http://{HOST}:{PORT}"

# project_id = "test_project"
# expt_id_1 = "test_expt_1"
# expt_id_2 = "test_expt_2"
# run_id_1 = "test_run_1"
# run_id_2 = "test_run_2"
# participant_id_1 = "test_participant_1"
# participant_id_2 = "test_participant_2"

# PROJECT_KEY = {'project_id': project_id}
# EXPT_KEY_1 = {'project_id': project_id, 'expt_id': expt_id_1}
# EXPT_KEY_2 = {'project_id': project_id, 'expt_id': expt_id_2}
# RUN_KEY_1 = {'project_id': project_id, 'expt_id': expt_id_1, 'run_id': run_id_1}
# RUN_KEY_2 = {'project_id': project_id, 'expt_id': expt_id_1, 'run_id': run_id_2}
# RUN_KEY_3 = {'project_id': project_id, 'expt_id': expt_id_2, 'run_id': run_id_2}
# PARTICIPANT_KEY_1 = {'participant_id': participant_id_1}
# PARTICIPANT_KEY_2 = {'participant_id': participant_id_2}
# REG_KEY_1 = {'project_id': project_id, 'participant_id': participant_id_1}
# REG_KEY_2 = {'project_id': project_id, 'participant_id': participant_id_2}
# TAG_KEY_1 = {'project_id': project_id, 'participant_id': participant_id_1}
# TAG_KEY_2 = {'project_id': project_id, 'participant_id': participant_id_2}

# ACTION = "classify"

# EXPT_RECORD = {
#     "created_at": "{TinyDate}:2021-01-28 01:34:40 N",
#     "key": {
#         "expt_id": expt_id_1,
#         "project_id": project_id
#     },
#     "model": [
#         {
#             "activation": "relu",
#             "is_input": True,
#             "l_type": "Conv2d",
#             "structure": {
#                 "in_channels": 1,
#                 "kernel_size": 3,
#                 "out_channels": 4,
#                 "padding": 1,
#                 "stride": 1
#             }
#         },
#         {
#             "activation": None,
#             "is_input": False,
#             "l_type": "Flatten",
#             "structure": {}
#         },
#         {
#             "activation": "softmax",
#             "is_input": False,
#             "l_type": "Linear",
#             "structure": {
#                 "bias": True,
#                 "in_features": 3136,
#                 "out_features": 3
#             }
#         }
#     ]
# }

# RUN_RECORD_1 = {
#     "algorithm": "FedProx",
#     "base_lr": 0.0005,
#     "created_at": "{TinyDate}:2021-01-28 01:34:40 N",
#     "criterion": "NLLLoss",
#     "delta": 0.0,
#     "epochs": 2,
#     "is_snn": False,
#     "key": {
#         "expt_id": expt_id_1,
#         "project_id": project_id,
#         "run_id": run_id_1
#     },
#     "l1_lambda": 0.0,
#     "l2_lambda": 0.0,
#     "lr": 0.001,
#     "lr_decay": 0.1,
#     "lr_scheduler": "CyclicLR",
#     "max_lr": 0.005,
#     "mu": 0.1,
#     "optimizer": "SGD",
#     "patience": 10,
#     "precision_fractional": 5,
#     "rounds": 5,
#     "seed": 42,
#     "weight_decay": 0.0
# }

# RUN_RECORD_2 = {
#     "algorithm": "FedAvg",
#     "base_lr": 0.0005,
#     "created_at": "{TinyDate}:2021-01-28 01:34:40 N",
#     "criterion": "NLLLoss",
#     "delta": 0.0,
#     "epochs": 30,
#     "is_snn": False,
#     "key": {
#         "expt_id": expt_id_1,
#         "project_id": project_id,
#         "run_id": run_id_2
#     },
#     "l1_lambda": 0.0,
#     "l2_lambda": 0.0,
#     "lr": 0.001,
#     "lr_decay": 0.1,
#     "lr_scheduler": "CyclicLR",
#     "max_lr": 0.005,
#     "mu": 0.1,
#     "optimizer": "SGD",
#     "patience": 15,
#     "precision_fractional": 5,
#     "rounds": 7,
#     "seed": 42,
#     "weight_decay": 0.0
# }

# REGISTRATION_RECORDS = [
#     {
#         "created_at": "{TinyDate}:2021-01-28 01:34:40 N",
#         "key": {
#             "participant_id": participant_id_1,
#             "project_id": project_id
#         },
#         "link": {
#             "registration_id": "fd7836d4610811ebb8c60242ac110004"
#         },
#         "role": "guest"
#     },
#     {
#         "created_at": "{TinyDate}:2021-01-28 01:34:40 N",
#         "key": {
#             "participant_id": participant_id_2,
#             "project_id": project_id
#         },
#         "link": {
#             "registration_id": "fd7f743a610811eba6e40242ac110004"
#         },
#         "role": "host"
#     }
# ]

# FEDERATED_CONFIG = {
#     'action': ACTION,
#     'registrations': REGISTRATION_RECORDS,
#     'experiments': [EXPT_RECORD],
#     'runs': [RUN_RECORD_1, RUN_RECORD_2],
#     'auto_align': False,
#     'dockerised': True, 
#     'log_msgs': False, 
#     'verbose': False
# }

# TEST_MESSAGE_COUNT = 50
# TEST_EXCHANGE = 'SynMQ_topic_logs'
# TEST_ROUTING_KEY = 'SynMQ_topic_unittest'
# TEST_QUEUE = 'unittest'

# ###########
# # Helpers #
# ###########


# ######################
# # Component Fixtures #
# ######################

# @pytest.fixture
# def init_params():
#     return {
#         'host': HOST, 
#         'port': PORT, 
#         'is_secured': IS_SECURED, 
#         'address': ADDRESS
#     }


# @pytest.fixture
# def test_kwargs():
#     return FEDERATED_CONFIG


# @pytest.fixture
# def test_message():
#     return json.dumps(FEDERATED_CONFIG, default=str, sort_keys=True)


@pytest.fixture
def root_logger():
    return synlogger.base.RootLogger(
        server=HOST,
        port=PORT,
        logging_variant="graylog"
    )


@pytest.fixture
def sysnetric_logger():
    return synlogger.general.SysmetricLogger(
        server=HOST,
        logger_name="test_source",
        logging_variant="graylog"
    )
