# -*- coding: utf-8 -*-
"""

This is a simple topology that is meant to be used in Populations and Resources
where nodes come and go.  It starts with a given number of nodes and allows the
rules of the Cell type to add/remove nodes via the add_node and remove_node
methods provided by Topology (and more likely the add_cell and remove_cell
wrappers provided in Population).

TODO: whether or not edges are used, created, or removed is up to the cell
type, but we really want to be able to provide that with a k-d tree.  However,
the downside is that maintaining a k-d tree in all instances may be pretty
expensive.

"""

__author__ = "Brian Connelly <bdc@msu.edu>"
__credits__ = "Brian Connelly"

import networkx as nx

from seeds.SEEDSError import *
from seeds.Topology import *


class GrowthTopology(Topology):
    """
    TODO: doc

    As the initial nodes are created, they are assigned random coordinates.

    Configuration: All configuration options should be specified in the
        GrowthTopology block (unless otherwise specified by the config_section
         parameter).

        start_size
            The number of nodes to start with.  Nodes are given randomly-chosen
            coordinates.  (default: 0)
        dimensions
            The number of dimensions in space that this topology occupies.
            (default: 2)
        periodic
            Whether or not the Experiment should form a torus.  This means that
            nodes on the left border are neighbors with nodes on the right
            border. (default: False)

    Example:
        [GrowthTopology]
        start_size = 100
        periodic = True

    """
    def __init__(self, experiment, label=None):
        """Initialize a GrowthTopology object"""
        super(GrowthTopology, self).__init__(experiment, label=label)

        if self.label:
            self.config_section = "%s:%s" % ("GrowthTopology", self.label)
        else:
            self.config_section = "%s" % ("GrowthTopology")

        self.start_size = self.experiment.config.getint(section=self.config_section,
                                                        name="start_size",
                                                        default=0)
        self.dimensions = self.experiment.config.getint(section=self.config_section,
                                                        name="dimensions",
                                                        default=2)
        self.periodic = self.experiment.config.getboolean(section=self.config_section,
                                                          name="periodic",
                                                          default=False)

        if self.start_size < 0:
            raise ConfigurationError("GrowthTopology: start_size must be positive")
        elif self.dimensions < 1:
            raise ConfigurationError("GrowthTopology: Number of dimensions must be at least 1")

        self.graph = nx.empty_graph()
        self.graph.add_nodes_from(nodes=range(self.start_size))

        for n in self.graph.nodes():
            self.graph.node[n]['coords'] = tuple([random.random() for i in xrange(self.dimensions)])

        self.size = len(self.graph)

    def __str__(self):
        """Produce a string to be used when an object is printed"""
        return 'Growth Topology (%d nodes)' % (self.size, self.radius)
