import idaapi
from idaapi import *

# While opening in IDA, set processor options to ARMv7-M for firmware targets
# Otherwise, some instructions will be interpreted as data rather than instructions

SegEnd = get_segm_end
GetFunctionName = get_func_name

al = []

def collect_post_call_instruction_starts():
    global al

    temp =[]
    for a in al:
        temp.append(a.split(' ')[0])
    # collect all heads following calls within functions
    for segea in Segments():
        for funcea in Functions(segea, SegEnd(segea)):
            functionName = GetFunctionName(funcea)
            for (startea, endea) in Chunks(funcea):
                for head in Heads(startea, endea):
                    mnem = print_insn_mnem(prev_head(head, head-4))
                    if (mnem and "bl" in mnem.lower()) and ("0x{:x}".format(head) not in temp):
                        al.append("0x{:x} 0x{:x}".format(head, idc.next_head(head)))

def collect_bbs_from_flowchart():
    global al
    for fn_addr in Functions():
        f = idaapi.FlowChart(idaapi.get_func(fn_addr))

        for block in f:
            al.append("0x{:x} 0x{:x}".format(block.start_ea, block.end_ea))
            for succ_block in block.succs():
                    al.append("0x{:x} 0x{:x}".format(succ_block.start_ea,succ_block.end_ea))
            for pred_block in block.preds():
                    al.append("0x{:x} 0x{:x}".format(pred_block.start_ea,pred_block.end_ea))
    #al start and end address of bb


def dump_bbl_txt(out_file_path="valid_basic_block_range.txt"):
    ans_all = []
    num_ans_all = []
    temp = []
    collect_bbs_from_flowchart()
    collect_post_call_instruction_starts()

    for a in al:
        if a not in ans_all:
            ans_all.append(a)

    #find start address == end address push
    for ans in ans_all:
        if int(ans.split(' ')[0], 16) <= int(ans.split(' ')[1], 16): #start address < end address
            num_ans_all.append([int(ans.split(' ')[0], 16), int(ans.split(' ')[1], 16)])

    num_ans_all.sort()

    num_start = []
    for t in num_ans_all:
        num_start.append(t[0])

    num_re_start = []
    num_not_re_start = []

    for st in num_start:
        if st not in num_not_re_start:
            num_not_re_start.append(st)
        else:
            num_re_start.append(st)

    for r in num_re_start:
        for a in num_ans_all[:]:
            if r == a[0] and r == a[1]:
                num_ans_all.remove(a)

    num_start.clear()
    num_not_re_start.clear()
    num_re_start.clear()
    #----------------------------------

    #find duplicate end address
    num_ans_all.sort()

    num_end = []
    for t in num_ans_all:
        num_end.append(t[1])

    num_re_end = []
    num_not_re_end = []

    for en in num_end:
        if en not in num_not_re_end:
            num_not_re_end.append(en)
        else:
            num_re_end.append(en)

    num_all_re_end = []
    for r in num_re_end:
        for a in num_ans_all[:]:
            if r == a[1]:
                num_all_re_end.append(a)
                num_ans_all.remove(a)  # remove and add back

    i = 0
    re_end_flag = 0
    while re_end_flag != len(num_all_re_end)-1:
        temp.append(num_all_re_end[i])
        for j in range(i+1, len(num_all_re_end)):
            if num_all_re_end[i][1] == num_all_re_end[j][1]:
                temp.append(num_all_re_end[j])
                re_end_flag = j
            else:
                i = j
                break
        if(len(temp) == 2):
            num_ans_all.append([temp[0][0],temp[1][0]])
            num_ans_all.append(temp[1])
        else:
            for k in range(0,len(temp)-1):
                num_ans_all.append([temp[k][0],temp[k+1][0]])
            num_ans_all.append(temp[len(temp)-1])
        temp.clear()


    num_end.clear()
    num_re_end.clear()
    num_not_re_end.clear()
    num_all_re_end.clear()
    #remove wrong end address


    #bl further divide

    num_ans_all.sort()
    num_bb_overlap = []
    for a_large in num_ans_all:
        for a_in in num_ans_all:
            if a_in[0] > a_large[0] and a_in[1] < a_large[1]:
                if a_large not in num_bb_overlap:
                    num_bb_overlap.append(a_large)
                num_bb_overlap.append(a_in)

    num_bb_overlap.sort()
    for bb in num_bb_overlap[:]:
        num_ans_all.remove(bb)


    temp = []
    i = 0
    flag = 0
    while flag != len(num_bb_overlap)-1:
        temp.append(num_bb_overlap[i])
        for j in range(i + 1, len(num_bb_overlap)):
            if num_bb_overlap[i][0] < num_bb_overlap[j][0] and num_bb_overlap[i][1] > num_bb_overlap[j][1]:
                temp.append(num_bb_overlap[j])
                flag = j
            else:
                i = j
                break
        if len(temp) == 2:
            num_ans_all.append([temp[0][0], temp[1][0]])
            num_ans_all.append([temp[1][0], temp[1][1]])
            num_ans_all.append([temp[1][1], temp[0][1]])
        else:
            for k in range(1, len(temp) - 1):
                num_ans_all.append([temp[k][1], temp[k + 1][0]])
            for k in range(1, len(temp)):
                num_ans_all.append([temp[k][0], temp[k][1]])
            num_ans_all.append([temp[0][0], temp[1][0]])
            num_ans_all.append([temp[len(temp) - 1][1], temp[0][1]])
        temp.clear()

    num_ans_all.sort()
    ans_all.clear()
    for num_ans in num_ans_all:
        ans_all.append("0x{:x} 0x{:x}".format(num_ans[0],num_ans[1]))

    str_wr = '\n'
    f = open(out_file_path, "w")
    f.write(str_wr.join(ans_all))
    f.close()

def main():
    dump_bbl_txt()

if __name__=='__main__':
	main()
