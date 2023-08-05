#!/usr/bin/env python
import pprint
from completers import ClusterCompleter


class CmdConfig(ClusterCompleter):
    """
    config [<cluster_tag> ...]

    Show various sections from the config
    """
    names = ['config', 'cfg']

    def addopts(self, parser):
        parser.add_option("-s", "--show-ssh-status", dest="show_ssh_status",
                          action="store_true", default=False,
                          help="output whether SSH is up on each node or not")

    def execute(self, args):
        pprint.pprint(self.cfg.aws)
