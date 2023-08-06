import os
import logging
import urllib2
import datetime
import xmlrpclib
from M2Crypto import m2urllib2
from M2Crypto import SSL
from .. import util
from .. import https
from ..xmlrpc import ControlNodeProxy
from ..xmlrpc import gen_storage_node_proxy_creator
from .node import ClientNode, ClientNodeConfig

logger = logging.getLogger(__name__)


def create_client_node(control_node_proxy=None,
                       storage_node_proxy_creator=None, config=None):
    """ClientNode Factory"""
    if config is None:
        config = ClientNodeConfig()
    if control_node_proxy is None:
        control_node_proxy = ControlNodeProxy(config)
    if storage_node_proxy_creator is None:
        storage_node_proxy_creator = gen_storage_node_proxy_creator(config)
    return ClientNode(control_node_proxy, storage_node_proxy_creator, config)
