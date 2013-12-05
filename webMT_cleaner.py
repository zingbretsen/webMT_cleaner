import csv
import math
import glob
import os
import sys

MT_NON_DATA_ROWS = 24
MT_DATA_BLOCK_NUM = 6
MT_BLOCK_NAMES = ["Obsolete", "Scaled X", "Scaled Y", "Raw X", "Raw Y", "Time"]
MAX_TIME_GAP = 20
DESIRED_TIME_GAP = 15


def read_file(input_file):
    if v > 2:
        with open(input_file, 'r', newline='') as fileObj:
            mt_reader = csv.reader(fileObj, delimiter=", ", )
            for mtLine in mt_reader:
                try:
                    if mtLine[0] != '':
                        mt_contents.append(mtLine)
                    else:
                        mt_contents.append([])
                except:
                    mt_contents.append([])
    else:
        with open(input_file, 'r') as fileObj:
            mt_reader = csv.reader(fileObj, delimiter=", ", )
            for mtLine in mt_reader:
                try:
                    if mtLine[0] != '':
                        mt_contents.append(mtLine)
                    else:
                        mt_contents.append([])
                except:
                    mt_contents.append([])

    while mt_contents[-1] == [''] or mt_contents[-1] == []:
        mt_contents.pop()
    return


def parse_first_line(first_line):
    global subj_id
    subj_id = str(first_line[0])
    global trial_num
    trial_num = int(first_line[1])
    print("\nSubject: " + subj_id + " supposedly completed " + str(trial_num) + " trials.")
    return


def find_block_boundaries():
    global block_boundaries
    for mt_line in range(mt_length):
        try:
            if mt_contents[mt_line][0] == '':
                blank_lines.append(mt_line)
        except:
            blank_lines.append(mt_line)
    for blank_line in range(len(blank_lines)):
        if blank_line % 2 == 0:
            block_boundaries[int(blank_line / 2)].append(blank_lines[blank_line] + 1)
        else:
            block_boundaries[int(blank_line / 2)].append(blank_lines[blank_line] - 1)
    block_boundaries[MT_DATA_BLOCK_NUM - 1].append(mt_length - 1)


def check_block_lengths(attempt=1):
    global trial_num
    global block_size
    for block_num, block_name in zip(range(MT_DATA_BLOCK_NUM), MT_BLOCK_NAMES):
        block_size = block_boundaries[block_num][1] - block_boundaries[block_num][0]
        block_lengths.append(block_size)
    block_min = min(block_lengths)
    for n in range(len(block_lengths)):
        if block_lengths[n] > block_min:
            block_boundaries[n][1] = block_boundaries[n][0] + block_min
    global mt_contents
    if mt_contents[0][1] != block_min:
        mt_contents[0][1] = block_min - 1
        print("\nNumber of trials successfully corrected in header!")
    else:
        print("\nAll blocks have the proper length\n")
        # if all(blockLength == trialNum+1 for blockLength in blockLengths):
        # if attempt==1:

        # return
        # else:
        # global mtContents
        # mtContents[0][1] = trialNum

        # return
    if all(blockLength != trial_num + 1 for blockLength in block_lengths):
        print("\nNo block lengths match the number of trials in the .mt header")
        if attempt == 1:
            print("\nAttempting to auto-correct")
            trial_num = block_lengths[0] - 1
            check_block_lengths(2)
        else:
            raise Exception('Failed to auto-correct block lengths. Check number of trials in each block.')
    if block_size != trial_num + 1:
        print(MT_BLOCK_NAMES[block_num] + ' block has the wrong number (' + str(block_size) + ') of trials')


def check_time_series():
    global obsolete_list, scaled_x_list, scaled_y_list, raw_x_list, raw_y_list, time_list, mt_contents
    obsolete_list = mt_contents[block_boundaries[0][0] + 2:block_boundaries[0][1] + 1]
    obsolete_header = mt_contents[block_boundaries[0][0]:block_boundaries[0][0] + 2]
    scaled_x_list = mt_contents[block_boundaries[1][0] + 2:block_boundaries[1][1] + 1]
    scaled_x_header = mt_contents[block_boundaries[1][0]:block_boundaries[1][0] + 2]
    scaled_y_list = mt_contents[block_boundaries[2][0] + 2:block_boundaries[2][1] + 1]
    scaled_y_header = mt_contents[block_boundaries[2][0]:block_boundaries[2][0] + 2]
    raw_x_list = mt_contents[block_boundaries[3][0] + 2:block_boundaries[3][1] + 1]
    raw_x_header = mt_contents[block_boundaries[3][0]:block_boundaries[3][0] + 2]
    raw_y_list = mt_contents[block_boundaries[4][0] + 2:block_boundaries[4][1] + 1]
    raw_y_header = mt_contents[block_boundaries[4][0]:block_boundaries[4][0] + 2]
    time_list = mt_contents[block_boundaries[5][0] + 2:block_boundaries[5][1] + 1]
    time_header = mt_contents[block_boundaries[5][0]:block_boundaries[5][0] + 2]
    for i, time in enumerate(time_list):
        if int(time[17]) == 0:
            time_list[i].pop(17)
            time_list[i].insert(17, 1)
        elif int(time[17]) > MAX_TIME_GAP:
            scaled_x_list[i].insert(17, 0)
            scaled_y_list[i].insert(17, 0)
            raw_x_list[i].insert(17, 400)
            raw_y_list[i].insert(17, 600)
            time_list[i].insert(17, 1)
            print('x')
        while time[-1] == '' or time[-1] == time[-2]:  # Get rid of duplicates at the end
            #print("time[-1] = " + time[-1])
            #print("scaledXList[i][-1]: " + scaledXList[i][-1])
            scaled_x_list[i].pop(-1)
            scaled_y_list[i].pop(-1)
            raw_x_list[i].pop(-1)
            raw_y_list[i].pop(-1)
            time_list[i].pop(-1)
        j = 17
        while True:
        #for j in range(17, len(time)):
            try:
                time[j + 1]
            except IndexError:
                break
            time_range = int(time[j]) + 5
            next_time = int(time[j + 1])
            while time[j + 1] != '' and time_range >= next_time and time[j + 1] != time[-1]:
                scaled_x_list[i].pop(j + 1)
                scaled_y_list[i].pop(j + 1)
                raw_x_list[i].pop(j + 1)
                raw_y_list[i].pop(j + 1)
                time_list[i].pop(j + 1)
                next_time = int(time_list[i][j + 1])
            try:
                difference = int(time[j + 1]) - int(time[j])
            except:
                continue
            if difference > MAX_TIME_GAP:
                steps = int(math.floor(difference / DESIRED_TIME_GAP))
                if difference % DESIRED_TIME_GAP == 0:
                    steps -= 1
                if v > 2:
                    temp_range = range(steps)
                else:
                    temp_range = xrange(steps)
                for step in temp_range:
                    scaled_x_list[i].insert(int(j) + int(step) + 1, float(scaled_x_list[i][j]))
                    scaled_y_list[i].insert(int(j) + int(step) + 1, float(scaled_y_list[i][j]))
                    raw_x_list[i].insert(int(j) + int(step) + 1, int(round(float(raw_x_list[i][j]))))
                    raw_y_list[i].insert(int(j) + int(step) + 1, int(round(float(raw_y_list[i][j]))))
                    time_list[i].insert(int(j) + int(step) + 1,
                                        int(time_list[i][j]) + ((int(step) + 1) * int(DESIRED_TIME_GAP)))
            j += 1
        if time_list[i][-1] == time_list[i][-2]:
            scaled_x_list[i].pop(-1)
            scaled_y_list[i].pop(-1)
            raw_x_list[i].pop(-1)
            raw_y_list[i].pop(-1)
            time_list[i].pop(-1)
    for n, scaledX in enumerate(scaled_x_list):
        for nX, X in enumerate(scaledX):
            if nX >= 17:
                if float(X) > 1:
                    scaled_x_list[n][nX] = 1
                elif float(X) < -1:
                    scaled_x_list[n][nX] = -1
    for n, scaledY in enumerate(scaled_y_list):
        for nY, Y in enumerate(scaledY):
            if nY >= 17:
                if float(Y) > 1.5:
                    scaled_y_list[n][nY] = 1.5
                elif float(Y) < 0:
                    scaled_y_list[n][nY] = 0
    mt_contents = [mt_contents[0]]
    mt_contents.extend([[]])
    lists = (obsolete_list, scaled_x_list, scaled_y_list, raw_x_list, raw_y_list, time_list)
    headers = (obsolete_header, scaled_x_header, scaled_y_header, raw_x_header, raw_y_header, time_header)
    for mt_blockList, mt_header in zip(lists, headers):
        mt_contents.extend(mt_header)
        for mt_line in mt_blockList:
            mt_contents.append(mt_line)
        mt_contents.extend([[], []])


def fix_scaled_xy():
    for n, scaledX in enumerate(scaled_x_list):
        for nX, X in enumerate(scaledX):
            if nX >= 17:
                if float(X) > 1:
                    scaled_x_list[n][nX] = 1
                elif float(X) > -1:
                    scaled_x_list[n][nX] = -1
    for n, scaledY in enumerate(scaled_y_list):
        for nY, Y in enumerate(scaledY):
            if nY >= 17:
                if float(Y) > 1.5:
                    scaled_y_list[n][nY] = 1.5
                elif float(Y) > 0:
                    scaled_y_list[n][nY] = 0


def write_csv(input_file, attempt=1):
    print("\nWriting new .mt file to " + input_file)
    try:
        if v > 2:
            with open(input_file, 'w', newline='') as fileObj:
                mt_writer = csv.writer(fileObj, delimiter=", ", )
                for mtLine in mt_contents:
                    mt_writer.writerow(mtLine)
        else:
            with open(input_file, 'w') as fileObj:
                mt_writer = csv.writer(fileObj, delimiter=", ", )
                for mtLine in mt_contents:
                    mt_writer.writerow(mtLine)
    except IOError:
        if attempt == 2:
            exit()
        print('\nMaking "corrected" subfolder...')
        os.makedirs(os.path.dirname(input_file))
        write_csv(input_file, attempt=2)
    print("\nSuccessfully wrote new .mt file to " + input_file)
    return


def get_input(prompt):
    if v < 3:
        my_input = str(raw_input(prompt))
    else:
        my_input = input(prompt)
    return my_input


def bad_file(input_file):
    split_file_name = os.path.split(input_file)
    return os.path.join(split_file_name[0], 'bad/', split_file_name[1])


if __name__ == "__main__":
    v = int(sys.version.split()[0].split('.')[0])
    #filePath = get_input('Please enter the path to the files?\n')
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
    else:  # You can hard code the path in here if you want
        file_path = ''
    if file_path == '':
        print('\nUsage: python webMT_cleaner.py /path/to/folder/with/mt/files')
        exit()
    else:
        #filePath = filePath.replace('\\', '/')
        mt_list = glob.glob(file_path + "/*.mt")
    print(mt_list)
    if not os.path.exists(os.path.join(file_path, '/bad/')):
        os.mkdir(os.path.join(file_path, '/bad/'))
    for mt_file in mt_list:
        print(mt_file)
        #if file already exists,  go on to next
        if os.path.isfile(mt_file.replace(os.path.basename(mt_file), "corrected/" + os.path.basename(mt_file))):
            continue
        mt_contents = list()
        subj_id = int()
        trial_num = int()
        block_lengths = list()
        block_boundaries = [[], [], [], [], [], []]
        blank_lines = list()
        obsolete_list = []
        scaled_x_list = []
        scaledXListOrig = []
        scaled_y_list = []
        raw_x_list = []
        raw_y_list = []
        time_list = []
        mt_length = int()
        print("-------------\nReading " + mt_file)
        read_file(mt_file)
        parse_first_line(mt_contents[0])
        mt_length = len(mt_contents)
        find_block_boundaries()
        check_block_lengths()
        try:
            check_time_series()
        except:
            badFileName = bad_file(mt_file)
            os.rename(mt_file, badFileName)
            continue
            #fixScaledXY()
        write_csv(mt_file.replace(os.path.basename(mt_file), "corrected/" + os.path.basename(mt_file)))
