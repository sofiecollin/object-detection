from RootClass import Root
from BoxClass import Box
path = 'MOTdata.txt'
r = Root()
gt = 'gt'
det = 'det'

r.add_MOT_root_frames_n_boxes(path,det)
r.add_MOT_root_frames_n_boxes(path,gt)
# r.get_a_frame(15,gt).get_a_box(1).set_xstart(1500)
# r.get_a_frame(15,det).add_box(Box(id = 300))
# r.get_a_frame(15,gt).add_box(Box(id = 1000))



print(r.get_summed_Scores())
#print(r.get_results())
