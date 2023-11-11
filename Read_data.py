import os
import time

import natsort
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

filepath = "./Solution_1/"


class Readpch():

    def __init__(self, filepath, file, num_features, actuator):
        self.filepath = filepath
        self.file = file
        self.num_features = num_features
        self.actuator = actuator

    def read_data(self):
        with open(os.path.join(self.filepath, self.file), 'r') as df:
            lines = df.readlines()
        df.close()

        lines = [_.strip() for _ in lines]
        lines = [_.replace('\n', '') for _ in lines]
        self.lines = [_[:74] for _ in lines]

        tmp_line = []
        nodes = []
        time_sol = []
        fields = []

        for line in self.lines:

            if (not line[:6] == '$TITLE') and \
                    (not line[:10] == '$SUBTITLE=') and \
                    (not line[:6] == '$LABEL') and \
                    (not line[:5] == '$REAL') and \
                    (not line[:8] == '$SUBCASE') and \
                    (not line[:6] == '-CONT-'):
                tmp_line.append(line)

                if line[:6] == '$POINT':
                    nodes.append(int(line[13:26]))

                if line[:1] != '$':
                    time_sol.append(line)

                if line[:6] != '$POINT' and line[:1] == '$':
                    if (line[1:50].replace(' ', '')) not in fields: fields.append(str(line[1:50].replace(' ', '')))

        nodes = nodes[:int(np.shape(nodes)[0] / num_features)]
        Dofs = int(np.shape(nodes)[0])  # number of nodes
        time_steps = int(np.shape(time_sol)[0] / Dofs / num_features)
        print('Time steps: ', time_steps)
        print('Dofs: ', Dofs)
        print('Fiels to compute:: ', fields)

        new_line = [line for line in tmp_line if line[0] != '$']

        field_x_total = []
        field_y_total = []
        field_z_total = []

        data = {}

        for field in fields:
            for node in range(Dofs):
                result = new_line[node * time_steps: (node + 1) * time_steps]
                result = [_.strip() for _ in result]
                result = [_.split() for _ in result]

                data[field, 'x', nodes[node]] = [float(line[2]) for line in result]
                data[field, 'y', nodes[node]] = [float(line[3]) for line in result]
                data[field, 'z', nodes[node]] = [float(line[4]) for line in result]

                # plot
                fig, ax = plt.subplots(3, 1)
                ax[0].plot(data[field, 'x', nodes[node]],
                           label=f'Act: {self.actuator}, Data:  {field.lower()}, node: {nodes[node]}, axis:x')
                ax[0].legend()

                ax[1].plot(data[field, 'y', nodes[node]],
                           label=f'Act: {self.actuator}, Data:  {field.lower()}, node: {nodes[node]}, axis:y')
                ax[1].legend()

                ax[2].plot(data[field, 'z', nodes[node]],
                           label=f'Act: {self.actuator}, Data:  {field.lower()}, node: {nodes[node]}, axis:z')
                ax[2].legend()

                plt.savefig(f'./plots/{field}_{nodes[node]}_{self.actuator}_{field.lower()}.png')
                plt.close()


name_sim = []
for file in os.listdir(filepath):
    # if file.startswith('Solution_1'):
    name_sim.append(file)

sim_short_ = natsort.natsorted(name_sim)

# construct the projected data
snapshot_mat = []
num_features = 2
for file in sim_short_:
    file_ = file.replace('3dplate_fem1_sim1-actuator_', '').replace('.pch', '')
    actuator = 'act' + file_
    data = Readpch(filepath, file, num_features, actuator).read_data()
uhjk