import numpy as np
import json
from math import log
from box import *
from util import *
# Point = namedtuple('Point', ['x', 'y'])



# example for annotations for a image
"""
id : 10
imgUrl : https://img.ibingli.cn/signature/CMWGTUhghiTnTpwd.jpg
baseline : [{'label': '8', 'pos': ((0.3799, 0.3118), (0.5551, 0.5951)), 'auditorId': '897a5dbcde49d31b'}]
annotation : [{'label': '69', 'pos': ((0.4467, 0.4127), (0.5509, 0.5919)), 'auditorId': 'cfdc8c9ae93f4098'}, {'label': '10', 'pos': ((0.3895, 0.2741), (0.586, 0.6054)), 'auditorId': 'cef1d5d702278e2b'}, {'label': '8', 'pos': ((0.4302, 0.2892), (0.575, 0.6054)), 'auditorId': '045c578053fc6052'}, {'label': '40', 'pos': ((0.3607, 0.1852), (0.6275, 0.637)), 'auditorId': 'a0fdceb8afde02dd'}, {'label': '10', 'pos': ((0.4158, 0.4111), (0.5513, 0.5542)), 'auditorId': 'dfc84641a2a8c4d3'}]
"""
num_people = 50
tolerate = True
dataset = "data/"+str(num_people)+"_people_annotation.txt"
all_annotations = data_process(dataset)
# print(all_annotations[0])
# for k,v in all_annotations[0].items():
#     print(k,":",v)
if tolerate:
    image_clusters = box_clustering_tolerate(all_annotations)
else:
    image_clusters = box_clustering(all_annotations)
c0 = 0
c1 = 0
c2 = 0
c3 = 0
abnormal = 0
for i, (annotations, clusters) in enumerate(zip(all_annotations, image_clusters)):
    # print(len(annotations['baseline']), len(clusters['clusters']), len(annotations['annotation']))
    # print(annotations['annotation'])
    # if i>100:
    #     break
    # pass
    c0 += len(annotations['baseline'])
    c1 += len(clusters['clusters'])
    c2 += len(annotations['annotation'])
    c3 += len(clusters['clusters']) / len(annotations['annotation'])

    baseline = annotations['baseline']
    cs = clusters['clusters']
    # visualization
    no_match = True
    visited = set()
    for ba in baseline:
        ba_box = ba['pos']
        match_index = -1
        # find match box
        for j, c in enumerate(cs):
            if j in visited:
                continue
            center = c['center']
            if box_match_center(center, ba_box):
                visited.add(j)
                match_index = j
                break
        if match_index != -1:
            # if any match box
            bl = ba['label']
            cls = []
            for annotation in cs[match_index]['annotation']:
                l = annotation['label']
                cls.append(l)

            auditorId = []
            for annotation in all_annotations[i]['annotation']:
                auditorId.append(annotation['auditorId'])
            no_match = False
        if match_index == -1:
            has_over_lap = False
            has_match_label = False
            print(i,"th image")
            for annotation in annotations['annotation']:
                box = annotation['pos']
                overlap = box_overlap(box, ba_box)
                # print(is_box_annotate_sameobj(box, ba_box))
                if box_area(overlap) >0:
                    has_over_lap = True
                    if is_box_annotate_sameobj(box, ba_box):
                        print("annotate same object")
                    if annotation['label'] == ba['label']:
                        has_match_label = True
            #108
            # if has_over_lap and has_match_label:
            #     # image_visualize_single_baseline(all_annotations[i],ba, show=True)
            #     # image_visualize(all_annotations[i],show=True)
            #     # print(image_cluster)
            #     image_visualize_with_cluster(all_annotations[i],cs, show=True)
            #     print(i,"th picture")
            #     # image_visualize_single_baseline(all_annotations[i],ba,show=True)
            #     input("Press the <ENTER> key to continue...")
    #     #visualize
    #     url = annotations['imgUrl']
    #     if tolerate:
    #         path = "tolerate/" + "check" + str(num_people) + "/" + str(abnormal) + ".jpg"
    #     else:
    #         path = "non_tolerate/" + "check" + str(num_people) + "/" + str(abnormal) + ".jpg"
    #     image_visualize(annotations,path=path,save=True)
    #     abnormal += 1
    #     # img.show()
    #     if abnormal > 50:
    #         break

print("baseline {}, cluster {}, annotation {}".format(c0, c1, c2, c3 / len(all_annotations)))

# check the number of cluster center match the baseline
match_c = 0
possible_match_c = 0 # the baseline required to have label
non_overlap_with_cluster_c = 0 # non box match the baseline
non_label_with_cluster_c = 0 #non label match the baseline
rate = 0
for i, clusters in enumerate(image_clusters):
    baseline = clusters['baseline']
    cs = clusters['clusters']

    visited = set()
    for ba in baseline:
        ba_box = ba['pos']
        match_index = -1
        # find match box
        for j, c in enumerate(cs):
            if j in visited:
                continue
            center = c['center']
            if box_match_center(center, ba_box):
                match_c += 1
                visited.add(j)
                match_index = j
                break
        if match_index != -1:
            # if any match box
            bl = ba['label']
            cls = []
            for annotation in cs[match_index]['annotation']:
                l = annotation['label']
                cls.append(l)

            auditorId = []
            for annotation in all_annotations[i]['annotation']:
                auditorId.append(annotation['auditorId'])
            # print(len(cls), len(set(auditorId)))

            # if len(cls) < len(set(auditorId))/3:
            #     match_c -=1
            rate += len(cls) / len(set(auditorId))

        # see how many basline box has no any boxes overlap with it

        any_overlap = False
        for j,c in enumerate(cs):
            center = c['center']
            if box_overlap_center(center, ba_box):
                any_overlap = True
        if not any_overlap:
            non_overlap_with_cluster_c += 1

        # see how many baseline box has no any label as it (even with any overlap)
        has_same_label = False
        for j, c in enumerate(cs):
            cas = c['annotation']
            for ca in cas:
                ca_box = ca['pos']
                ca_l = ca['label']
                overlap = box_overlap(ca_box,ba_box)
                overlap_area = box_area(overlap)
                if overlap_area > 0:
                    if ca_l == ba['label']:
                        has_same_label = True
        if not has_same_label:
            non_label_with_cluster_c +=1

        if match_index != -1 and has_same_label:
            possible_match_c += 1

print("baseline nerver has match box {}, rate {}".format(non_overlap_with_cluster_c,non_overlap_with_cluster_c/c0))
print("baseline nerver has match label {}, rate {}".format(non_label_with_cluster_c,non_label_with_cluster_c/c0))
print("maximum possible match box rate {}".format(1 - non_overlap_with_cluster_c/c0 ))
print("maximum possible match box and label rate {}".format(1 - non_label_with_cluster_c/c0 ))

print("cluster box match baseline count {}, match rate {}".format(match_c,match_c/c0))
print("cluster box match possible baseline count {}, match rate {}".format(possible_match_c, possible_match_c/c0))

# calculate how many boxes provided by worker versus baseline
# user_num_boxes = defaultdict(int)
# user_contribute_image_c = defaultdict(int)
# for annotations in all_annotations:
#     num_baseline = len(annotations['baseline'])
#     worker_annotations = annotations['annotation']
#     count_dict = defaultdict(int)
#     for worker in worker_annotations:
#         auditorId = worker['auditorId']
#         count_dict[auditorId] += 1
#     for auditorId in count_dict:
#         user_contribute_image_c[auditorId] += 1
#         user_num_boxes[auditorId] += count_dict[auditorId] / num_baseline
#
# for auditorId in user_num_boxes:
#     user_num_boxes[auditorId]/= user_contribute_image_c[auditorId]
#
# for auditorId in user_num_boxes:
#     print(auditorId, user_num_boxes[auditorId])




print("test",rate/match_c)

print("------------------------------------------------------")
print("majority vote")
majority_vote(image_clusters, all_annotations)

print("------------------------------------------------------")
print("truth discovery")
truth_discovery(image_clusters, all_annotations)

# print("------------------------------------------------------")
# print("two layer truth discovery")
# two_level_truth_discovery(image_clusters, all_annotations)
#
