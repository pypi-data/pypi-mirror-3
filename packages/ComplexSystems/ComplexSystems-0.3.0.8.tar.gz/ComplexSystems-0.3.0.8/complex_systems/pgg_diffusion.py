#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Copyright (c) 2012 Vincent Gauthier.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# -------------------------------------------------------------------------------

__author__ = """\n""".join(['Abhik Banerjee', 'Vincent Gauthier'])

import networkx as nx
import random as RD
import numpy as N


class PGG_diffusion:

    def __init__(
        self,
        G,
        synergy,
        nb_simulation_step=1,
        nb_seeder=1,
        cooperator_ratio=0.0,
        noise_var=0.0,
        maxlen_queue=200,
        ):

        import collections
        self._noise_var = noise_var
        self._G = G
        self._synergy = synergy
        self._nb_node = len(G.nodes())
        self._nb_seeder = nb_seeder
        self._nb_simulation_step = int(nb_simulation_step)
        self._nb_coop = collections.deque(maxlen=maxlen_queue)
        self._nb_def = collections.deque(maxlen=maxlen_queue)
        self._infected_node = [RD.randint(0,self._nb_node-1) for x in xrange(self._nb_seeder)]
        self._simulation_time = 0
        self.reset_send_update()
        for nd in self._G.nodes_iter():

            # Initialize payoff and fitness values of nodes

            self.reset_payoffs()

            # Assign initial strategy

            if RD.random() < cooperator_ratio:
                self._G.node[nd]['strategy'] = 'C'
            else:
                self._G.node[nd]['strategy'] = 'D'
            self._G.node[nd]['state'] = 'S'
            self._G.node[nd]['time_stamp'] = 0.0

    def compute_payoffs(self, dealer):
        '''
        Compute the payoffs 
        '''

        import numpy as np

        dealer_neighborhood = self._G.neighbors(dealer)
        dealer_neighborhood.append(dealer)
        if self._noise_var > 0:
            noise = np.random.normal(loc=0.0, scale=self._noise_var,
                    size=1)
        else:
            noise = 0.0

        if self._G.node[dealer]['strategy'] == 'C':
            cost_y = 1.0
        else:
            cost_y = 0

        cost_i = 0
        for i in dealer_neighborhood:
            if self._G.node[i]['strategy'] == 'C' and self._G.node[i]['sent_update'] == 1:
                Ki = self._G.degree(i)
                cost_i += 1.0 / (Ki + 1)
        self._G.node[dealer]['payoff'] = self._synergy * cost_i \
            - cost_y + noise

    def diffusion_step(self):
        H = self._G.copy()
        node_list = H.nodes()
        RD.shuffle(node_list)
        for node in node_list:
            if H.node[node]['state'] == 'I' and H.node[node]['strategy'] == 'C':
                neighbors = H.neighbors(node)
                for neighbor in neighbors:
                    if RD.random() < H.edge[node][neighbor]['weight']:
                        if H.node[neighbor]['state'] == 'S':
                            H.node[neighbor]['state'] = 'I'
                            H.node[neighbor]['time_stamp'] = \
                                H.node[node]['time_stamp']
                            H.node[node]['sent_update'] = 1
                        else:
                           if H.node[node]['time_stamp'] > H.node[neighbor]['time_stamp']:
                                H.node[neighbor]['time_stamp'] = H.node[node]['time_stamp']
                                H.node[node]['sent_update'] = 1
        self._G = H.copy()

    def run_game(self, nb_simulation_step=None):
        if nb_simulation_step != None:
            nb_step = int(nb_simulation_step)
        else:
            nb_step = self._nb_simulation_step
        for i in xrange(int(nb_step)):
            self._simulation_time += 1 
            for dealer in self._G.nodes_iter():
                self.compute_payoffs(dealer)
            
            for infected in self._infected_node:
                self.set_time_stamp(infected, self._simulation_time)
            self.reset_send_update()
            self.diffusion_step()
            #for nd in self._G.nodes_iter():
            #    if self._G.node[nd]['sent_update'] == 1:
            #        print 'node ', nd, ' sent a packet with time stamp = ', self._G.node[nd]['time_stamp'], ' at simulation time=', self._simulation_time
            # Update the simuations variable
            self.store_cooperator_defector_counter()
            self.updateStrategy()
            self.reset_payoffs()

        nb_coop = sum(self._nb_coop) / len(self._nb_coop)
        return float(nb_coop) / len(self._G.nodes())

    def updateStrategy(self):
        import random as rd
        import numpy as np

        # We create a copy of the graph so that the transitions in the same time slot
        # do not impact each other.
        # Since nodes update their strategies based on payoffs in the previous slot

        H = self._G.copy()

        # Update strategies. In this version, the adaptation of PGG is limited
        # to the payoffs only, as done above. The strategy update takes place
        # irrespective of whether a node has new packets or not.

        for nd in self._G.nodes_iter():

            # Choose a random neighbor and change strategy with probability
            # proportional to the difference

            nd_deg = self._G.degree(nd)
            nd_nblist = self._G.neighbors(nd)

            if nd_deg != 0:
                comp_nb = nd_nblist[int(np.floor(rd.random() * nd_deg))]
                pyoff_diff = self._G.node[nd]['payoff'] \
                    - self._G.node[comp_nb]['payoff']
                if rd.random() < 1 / (1 + np.exp(pyoff_diff / 0.1)):
                    H.node[nd]['strategy'] = \
                        self._G.node[comp_nb]['strategy']

        self._G = H.copy()

    #
    # Set
    #

    def set_payoffs(self, payoffs):
        for node in self._G.nodes_iter():
            self._G.node[node]['payoff'] = payoffs[node]

    def set_strategies(self, strategies):
        for node in self._G.nodes_iter():
            self._G.node[node]['strategy'] = strategies[node]

    def set_node_have_packet_to_send(self, packet_to_send):
        for node in self._G.nodes_iter():
            self._G.node[node]['packet_to_send'] = packet_to_send[node]

    def set_time_stamps(self, time_stamps):
        for (key, val) in time_stamps.iteritems():
            self._G.node[key]['time_stamp'] = val
            self._simulation_time = max(val, self._simulation_time)

    def set_seeder(self, seeder):
        self._infected_node = seeder

    def set_nodes_states(self, nodes_states):
        for (key, val) in nodes_states.iteritems():
            self._G.node[key]['state'] = val

    def set_time_stamp(self, node_id, time_stamp):
        self._G.node[node_id]['state'] = 'I'
        self._G.node[node_id]['strategy'] = 'C'
        self._G.node[node_id]['time_stamp'] = time_stamp

    def set_sent_update(self, sent_update):
       for (key, val) in sent_update.iteritems():
            self._G.node[key]['sent_update'] = val

    #
    # Get
    #

    def get_strategies(self):
        strategies = {}
        for node in self._G.nodes_iter():
            strategies[node] = self._G.node[node]['strategy']
        return strategies

    def get_payoffs(self):
        payoffs = {}
        for node in self._G.nodes_iter():
            payoffs[node] = self._G.node[node]['payoff']
        return payoffs

    def get_time_stamps(self):
        time_stamps = {}
        for node in self._G.nodes():
            time_stamps[node] = self._G.node[node]['time_stamp']
        return time_stamps

    def get_states(self):
        states = {}
        for node in self._G.nodes():
            states[node] = self._G.node[node]['state']
        return states

    def get_sent_update(self):
        sent_update = {}
        for node in self._G.nodes():
            sent_update[node] = self._G.node[node]['sent_update']
        return sent_update

    def get_seeder(self):
        return self._infected_node
    #
    # Reset
    #

    def reset_payoffs(self):
        for nd in self._G.nodes_iter():
            self._G.node[nd]['payoff'] = 0.0

    def reset_payoffs_selected_player(self, player):
        self._G.node[player]['payoff'] = 0.0

    def reset_send_update(self):
        for nd in self._G.nodes_iter():
            self._G.node[nd]['sent_update'] = 0

    #
    # Counter
    #

    def compute_avg_payoffs(self):
        avg_pay_c = 0
        avg_pay_d = 0
        avg_pay = 0
        for node in self._G.nodes_iter():
            avg_pay += self._G.node[node]['payoff']
            if self._G.node[node]['strategy'] == 'C':
                avg_pay_c += self._G.node[node]['payoff']
            else:
                avg_pay_d += self._G.node[node]['payoff']
        nbcoop = self.cooperator_counter()
        if nbcoop != 0:
            avg_pay_c = avg_pay_c / nbcoop
        else:
            avg_pay_c = 0
        nbdef = self.defector_counter()
        if nbdef != 0:
            avg_pay_d = avg_pay_d / self.defector_counter()
        else:
            avg_pay_d = 0
        avg_pay = avg_pay / len(self._G.nodes())
        return (avg_pay_c, avg_pay_d, avg_pay)

    def cooperator_counter(self):
        return [self._G.node[i]['strategy'] for i in
                self._G.nodes_iter()].count('C')

    def store_cooperator_defector_counter(self):
        self._nb_coop.append(self.cooperator_counter())
        self._nb_def.append(self.defector_counter())

    def defector_counter(self):
        return [self._G.node[i]['strategy'] for i in
                self._G.nodes_iter()].count('D')

    def cooperator_in_neighborhood_counter(self, node):
        return [self._G.node[neighbor]['strategy'] for neighbor in
                self._G.neighbors_iter(node)].count('C')
