import numpy
import math
from pandas import read_csv
from datetime import datetime
import random
import csv

PI_MAX = 45
CI_MAX = 12
NUM_P = 120
ROUNDS = 100
SELECTIONS = 3
MIN_PER = 0.4
BLOCKING = True

input_filename = 'input_data.csv'
names = ['applicant', 'weight', 'unscaled_weight', 'second_weight']
data = read_csv(input_filename, names=names)

c_csv_data = []
s_csv_data = []

data = data.assign(matched=([0] * data.shape[0]))
data = data.assign(num_matches=([0] * data.shape[0]))
data = data.assign(num_interviews=([0] * data.shape[0]))

numpy.random.seed(1)
random.seed(1)


def write_output(data):
    c_filename = "c_" + str(datetime.now().strftime("%Y_%m_%d-%I_%M")) + ".csv"
    s_filename = "s_" + str(datetime.now().strftime("%Y_%m_%d-%I_%M")) + ".csv"

    interviews = [program for sublist in programs for program in sublist]

    top_10 = []
    for i in range(10):
        top_10.append(interviews.count(i + 1))

    top_quarter_10 = []
    for i in range(10):
        top_quarter_10.append(interviews.count(i + 139))

    median_10 = []
    for i in range(10):
        median_10.append(interviews.count(i + 281))

    bottom_quarter_10 = []
    for i in range(10):
        bottom_quarter_10.append(interviews.count(i + 423))

    bottom_10 = []
    for i in range(10):
        bottom_10.append(interviews.count(i + 561))

    with open(c_filename, 'w', newline='') as csv_file:
        c_writer = csv.writer(csv_file, delimiter=' ')

        for element in c_csv_data:
            c_writer.writerow([element])

    with open(s_filename, 'w', newline='') as s_file:
        s_writer = csv.writer(s_file, delimiter=' ')
        for element in s_csv_data:
            s_writer.writerow([element])


def no_blocking():
    global data
    global programs

    for i in range(NUM_P):
        programs.append(numpy.random.choice(data.applicant, size=PI_MAX, replace=False, p=data.weight))


def blocking(m_i):
    global data
    global programs

    if len(data.applicant) * m_i > NUM_P * PI_MAX:

        for i in range(NUM_P):
            s_a = []
            p_a = data.applicant.tolist()

            a_w = data.weight.tolist()

            selections = 0

            while selections < PI_MAX:

                applicant = random.choices(p_a, weights=a_w)[0]

                if data[data['applicant'] == applicant]['num_interviews'].item() < m_i:

                    s_a.append(applicant)

                    data.loc[(applicant - 1), 'num_interviews'] += 1

                    selections += 1

                else:
                    applicant_index = p_a.index(applicant)

                    p_a.pop(applicant_index)
                    a_w.pop(applicant_index)

            programs.append(numpy.asarray(s_a))
    else:
        c_m = math.floor(math.floor(len(data.applicant) * m_i / NUM_P) * MIN_PER)
        c_s = 0

        for i in range(NUM_P):
            s_a = []
            p_a = data.applicant.tolist()
            a_w = data.weight.tolist()

            selections = 0

            while (selections < c_m):

                applicant = random.choices(p_a, weights=a_w)[0]

                if data[data['applicant'] == applicant]['num_interviews'].item() < m_i:

                    s_a.append(applicant)

                    data.loc[(applicant - 1), 'num_interviews'] += 1

                    selections += 1

                    c_s += 1

                else:
                    applicant_index = p_a.index(applicant)

                    p_a.pop(applicant_index)
                    a_w.pop(applicant_index)

            programs.append(numpy.asarray(s_a))

        p_a = data.applicant.tolist()
        a_w = data.weight.tolist()

        while c_s < (len(data.applicant) * m_i):

            program_index = random.randrange(0, NUM_P)

            if len(programs[program_index]) < PI_MAX:

                applicant = random.choices(p_a, weights=a_w)[0]

                if data[data['applicant'] == applicant]['num_interviews'].item() < m_i:

                    programs[program_index] = numpy.append(programs[program_index], applicant)

                    data.loc[(applicant - 1), 'num_interviews'] += 1

                    c_s += 1

                else:
                    applicant_index = p_a.index(applicant)

                    p_a.pop(applicant_index)
                    a_w.pop(applicant_index)


s_c = []
c = []

for i in range(ROUNDS):

    data = data.assign(num_interviews=([0] * data.shape[0]))

    programs = []

    if BLOCKING:
        blocking(CI_MAX)
    else:
        no_blocking()

    program_num = 0

    s = False

    candidates_selected = 0

    for program in programs:

        c = program.tolist()
        selections = 0

        applicant_weights = []
        for candidate in c:
            candidate_index = c.index(candidate)

            applicant_weights.append(data.second_weight[candidate_index])

        while (len(c) > 0 and selections < SELECTIONS) and (s is False):

            m = random.choices(c)[0]

            if not data['matched'].iloc[m - 1].any():

                data.loc[(m - 1), 'matched'] = 1

                data.loc[(m - 1), 'num_matches'] += 1

                selections += 1

            else:
                candidate_index = c.index(m)

                c.pop(candidate_index)
                applicant_weights.pop(candidate_index)

            if len(c) == 0:
                s = True

        if s:
            break

        program_num += 1

    s_row = []
    i_stats = []
    m_stats = []

    for j in range(len(data.applicant)):
        i_count = 0
        for x in programs:
            i_count += numpy.count_nonzero(x == (j + 1))
        i_stats.append(i_count)

    for j in range(len(data.applicant)):
        m_stats.append(data.loc[j, 'matched'])

    s_row = [i_stats, m_stats]

    c_csv_data.append(s_row)

    s_csv_data.append((NUM_P * SELECTIONS) - (((program_num - 1) * SELECTIONS) + selections))

    data = data.assign(matched=([0] * data.shape[0]))

write_output(data)
