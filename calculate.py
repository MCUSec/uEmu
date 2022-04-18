import sys

Path_bb = sys.argv[1]
Path_bb_map = sys.argv[2]
f1=open(Path_bb)
f2=open(Path_bb_map)

bbs=[]
bb_maps=[]
for line in f1:
    bbs.append(line.strip())
for line in f2:
    bb_maps.append(line.strip())

num_bbs = []
num_bb_maps = []

for bb in bbs:
    num_bbs.append([int(bb.split()[0], 16), int(bb.split()[1], 16)])

for bb_m in bb_maps:
    num_bb_maps.append([int(bb_m.split()[0], 16), int(bb_m.split()[1], 10)])

ans = []

for bb_map in num_bb_maps[:]:
    flag = 0
    frequency = 0
    start = 0
    end = 0
    for num_bb in num_bbs:
        if num_bb[0] <= bb_map[0] and bb_map[0] < num_bb[1]:
            frequency = frequency + bb_map[1]
            flag = 1
            start = num_bb[0]
            end = num_bb[1]
    if flag == 0:
        for num_bb in num_bbs:
            if bb_map[0] == num_bb[1]:
                frequency = frequency + bb_map[1]
                flag = 1
                start = num_bb[0]
                end = num_bb[1]
    if flag == 1:
        ans.append("0x{:x} 0x{:x} {}".format(start,end,frequency))

str_wr = '\n'
f_out = open(Path_bb_map+"-cov.csv", "w")
f_out.write(str_wr.join(ans))
f_out.close()