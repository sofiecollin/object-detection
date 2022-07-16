
path = 'test.txt'
#Read a line. Test if len > 0
data = open(path)

line = data.readline()


while len(line) > 0:
    line_arr = line.split(',')
    frame_nr = line_arr[0]
    id = line_arr[1]
    x_top_left = line_arr[2]
    y_top_left = line_arr[3]
    width = line_arr[4]
    height = line_arr[5]

    print(x_top_left)

    #Update
    line = data.readline()





data.close()
