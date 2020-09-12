from .clustering import *
from math import log
from collections import defaultdict
import copy
# import matplotlib.pyplot as plt
from util import *

EMPTY_BOX_LABEL = 10000   # define label for no box

def majority_vote(image_clusters, all_annotations):
    santized_cluster_c = 0
    box_match_c = 0  # only box match
    all_match_c = 0  # box + label match
    baseline_c = 0
    total_miss_c = 0

    image_difficulty = compute_image_difficulty(image_clusters, all_annotations)
    for i, image_cluster in enumerate(image_clusters):
        annotations = all_annotations[i]
        auditor_id = set()

        difficulty = image_difficulty[i]

        for annotation in annotations['annotation']:
            auditor_id.add(annotation['auditorId'])
        # print(image_cluster)
        # input("prompt")
        # remove unnecessary cluster (object)
        clusters = image_cluster['clusters']
        sanitized_clusters = []
        for cluster in clusters:
            num_support = len(cluster['annotation']) # worker support this object

            cluster_auditor_id = set()
            for cluster_annotation in cluster['annotation']:
                cluster_auditor_id.add(cluster_annotation['auditorId'])

            num_non_support = len(auditor_id) - len(cluster_auditor_id)
            if num_support * difficulty >= num_non_support: #majority
            # relax to 1/3
            # if num_support > 1:
                sanitized_clusters.append(cluster)
            # else:
            #     print(num_support, len(auditorId))
        clusters = sanitized_clusters
        santized_cluster_c += len(clusters)

        baseline = image_cluster['baseline']
        baseline_c += len(baseline)
        visited = set()

        has_box_match = False
        for t, ba in enumerate(baseline):
            ba_box = ba['pos']
            match_index = -1
            # find match box
            for j, c in enumerate(clusters):
                if j in visited:
                    continue
                center = c['center']
                # print(i,"th picture",t,"th baseline","match",box_match_center(center, ba_box))
                if box_match_center(center, ba_box):
                    box_match_c += 1
                    # visited.add(j)
                    match_index = j
                    break
            if match_index != -1:
                has_box_match=True
                # if any match box
                bl = ba['label']
                cls = []
                annotate_auditor_id = []
                for annotation in clusters[match_index]['annotation']:
                    l = annotation['label']
                    cls.append(l)
                    annotate_auditor_id.append(annotation['auditorId'])
                try:
                    if(len(annotate_auditor_id)!=len(set(annotate_auditor_id))):
                        raise Exception("two box by same worker in one cluster")
                except:
                    pass

                # use major vote to get correct label
                # num_annotate_auditor = len(annotate_auditor_id)
                count_dict = defaultdict(int)
                for l in cls:
                    count_dict[l] +=1
                count_list = [(k,v) for k,v in count_dict.items()]
                count_list.sort(key = lambda x:x[1], reverse=True)
                estimate_label = count_list[0][0]
                if bl == estimate_label:
                    all_match_c += 1
                else:
                    # print(bl,cls)
                    pass

                if bl not in cls:
                    total_miss_c +=1
                #     print(bl, cls)
                #     show_image_from_url(image_cluster['imgUrl'])
                #     input("Press the <ENTER> key to continue...")

                # auditorId = []
                # for annotation in all_annotations[i]['annotation']:
                #     auditorId.append(annotation['auditorId'])
                # print(len(cls), len(set(auditorId)))

                # if len(cls) < len(set(auditorId))/3:
                #     box_match_c -=1
            # if not has_box_match:
            #     # if has overlap with any box
            #     has_over_lap = False
            #     for annotation in annotations['annotation']:
            #         box = annotation['pos']
            #         overlap = box_overlap(box, ba_box)
            #         # print(is_box_annotate_sameobj(box, ba_box))
            #         if box_area(overlap) >0:
            #             has_over_lap = True
            #             print("any overlap", is_box_annotate_sameobj(box, ba_box))
            #             break
            #     if has_over_lap:
            #         # image_visualize_single_baseline(all_annotations[i],ba, show=True)
            #         # image_visualize(all_annotations[i],show=True)
            #         # print(image_cluster)
            #         image_visualize_with_cluster(all_annotations[i],clusters,show=True)
            #         input("Press the <ENTER> key to continue...")
    print("cluster num after sanitized",santized_cluster_c)
    print("box match baseline count {}, match rate {}".format(box_match_c, box_match_c/baseline_c))
    print("all match basline count {}, accuracy {}, match rate {}".format(all_match_c, all_match_c/santized_cluster_c ,all_match_c/baseline_c))
    print("not possible count {}".format(total_miss_c))


def compute_image_difficulty(image_clusters, all_annotations):
    image_diffculty = []
    for i, image_cluster in enumerate(image_clusters):
        # get auditor id annotate this image
        annotations = all_annotations[i]

        annotate_auditor_id = set()
        for annotation in annotations['annotation']:
            annotate_auditor_id.add(annotation['auditorId'])

        num_cluster = len(image_cluster['clusters'])
        num_annotation = len(annotations['annotation'])
        num_worker = len(annotate_auditor_id)
        difficulty = (num_cluster * num_worker / num_annotation) ** 0.5
        image_diffculty.append(difficulty)
        # if 1<difficulty < 1.5:
        #     image_visualize(all_annotations[i],show=True)
        #     input("prompt")
    # visualize
    # num_bins = 20
    # plt.hist(image_diffculty, num_bins, facecolor='blue', alpha=0.5)
    # plt.show()
    # input("prompt")

    return image_diffculty


def truth_discovery(image_clusters, all_annotations):
    # tmp_image_clusters = copy.deepcopy(image_clusters)

    sanitized_cluster_c = 0
    box_match_c = 0  # only box match
    all_match_c = 0  # box + label match
    baseline_c = 0
    total_miss_c = 0

    # truth discovery to discover label
    # initialize weight
    weight = dict()
    # get all user id
    all_auditor_id = set()
    for annotations in all_annotations:
        for annotation in annotations['annotation']:
            all_auditor_id.add(annotation['auditorId'])
    for k in all_auditor_id:
        weight[k] = 1


    # worker quality
    # worker_quality = dict()
    # for auditorId in all_auditor_id:
    #     worker_quality[auditorId] = [0,0]   # num of correct box and correct label

    # truth discovery to discover label
    # use new initialize weight


    # estimate image difficulty
    # difficuly = cluster_num * worker_Num / annotations
    image_diffculty = compute_image_difficulty(image_clusters, all_annotations)


    T = 10  # truth discovery round
    for t in range(T):
        # initialize distance
        distance = dict()
        for k in all_auditor_id:
            distance[k] = 0
        for i, image_cluster in enumerate(image_clusters):
            # get auditor id annotate this image
            annotations = all_annotations[i]
            difficulty = image_diffculty[i]
            annotate_auditor_id = set()
            for annotation in annotations['annotation']:
                annotate_auditor_id.add(annotation['auditorId'])

            for cluster in image_cluster['clusters']:
                count_dict = defaultdict(int)
                cluster_total_w = 0

                # calculate new label
                # label for workers in cluster
                cluster_auditor_id = []
                for annotation in cluster['annotation']:
                    l = annotation['label']
                    auditorId = annotation['auditorId']
                    w = weight[auditorId] * difficulty
                    cluster_total_w += w
                    count_dict[l] += w
                    cluster_auditor_id.append(auditorId)
                try:
                    if len(cluster_auditor_id) != len(set(cluster_auditor_id)):
                        raise Exception("two or more boxes by one auditor in a cluster")
                except:
                    pass
                # for work not in cluster, use empty label instead
                cluster_auditor_id = set(cluster_auditor_id)
                for auditorId in annotate_auditor_id:
                    if auditorId not in cluster_auditor_id:
                        w = weight[auditorId]
                        count_dict[EMPTY_BOX_LABEL] += w
                        cluster_total_w += w
                # average weight
                for k in count_dict:
                    count_dict[k] /= cluster_total_w

                # calculate distance for each worker
                # get label of workers
                auditor_annotation = defaultdict(list)
                # label of workers in cluster
                for annotation in cluster['annotation']:
                    l = annotation['label']
                    auditorId = annotation['auditorId']
                    auditor_annotation[auditorId].append(l)
                # label of workers not in cluster
                for auditorId in annotate_auditor_id:
                    if auditorId not in cluster_auditor_id:
                        auditor_annotation[auditorId].append(EMPTY_BOX_LABEL)

                # distance  Euclidean distance
                # distance for worker in clusters
                sub_distance = defaultdict(int)
                for label in count_dict:
                    w = count_dict[label]
                    for auditorId in auditor_annotation:
                        label_count = 0
                        for al in auditor_annotation[auditorId]:
                            if al == label:
                                label_count += 1
                        if label_count !=0:
                            dis = label_count* (1 - w) ** 2
                        else:
                            dis =  w ** 2
                        sub_distance[auditorId] += dis
                        # sub_distance[auditorId] += dis if label == EMPTY_BOX_LABEL else  dis/difficulty

                for auditorId in sub_distance:
                    sub_distance[auditorId] = sub_distance[auditorId] ** 0.5
                    # add to total distance
                    distance[auditorId] += sub_distance[auditorId]
        # calculate new_weight
        total_distance = sum(distance.values())
        for auditorId in weight:
            weight[auditorId] = -log(distance[auditorId] / total_distance)
            # weight[auditorId] = total_distance/ distance[auditorId]


    # remove unnecessary cluster
    for i, image_cluster in enumerate(image_clusters):
        # get auditor id annotate this image
        annotations = all_annotations[i]
        difficulty = image_diffculty[i]
        annotate_auditor_id = set()
        for annotation in annotations['annotation']:
            annotate_auditor_id.add(annotation['auditorId'])

        sanitized_cluster = []
        for cluster in image_cluster['clusters']:
            count_dict = defaultdict(int)
            cluster_total_w = 0

            # calculate new label
            # label for workers in cluster
            cluster_auditor_id = []
            for annotation in cluster['annotation']:
                l = annotation['label']
                auditorId = annotation['auditorId']
                w = weight[auditorId] * difficulty
                cluster_total_w += w
                count_dict[l] += w
                cluster_auditor_id.append(auditorId)

            # if len(cluster_auditor_id) != len(set(cluster_auditor_id)):  # has checked before
            #     raise Exception("two or more boxes by one auditor in a cluster")
            # for work not in cluster, use empty label instead

            cluster_auditor_id = set(cluster_auditor_id)
            for auditorId in annotate_auditor_id:
                if auditorId not in cluster_auditor_id:
                    w = weight[auditorId]
                    count_dict[EMPTY_BOX_LABEL] += w
                    cluster_total_w += w
            # average weight
            # for k in count_dict:
            #     count_dict[k] /= cluster_total_w
            # find the label with largest label
            count_list = [(k, v) for k, v in count_dict.items()]
            count_list.sort(key=lambda x: x[1], reverse=True)
            estimate_label = count_list[0][0]
            if estimate_label == EMPTY_BOX_LABEL:
                continue
            sanitized_cluster_c += 1
            sanitized_cluster.append(cluster)
        image_cluster['clusters'] = sanitized_cluster

    # benchmark cluster label
    for i, image_cluster in enumerate(image_clusters):
        # get auditor id annotate this image
        annotations = all_annotations[i]

        annotate_auditor_id = set()
        for annotation in annotations['annotation']:
            annotate_auditor_id.add(annotation['auditorId'])

        clusters = image_cluster['clusters']

        baseline = image_cluster['baseline']
        # baseline_c += len(baseline)
        visited = set()
        for ba in baseline:
            baseline_c+=1
            ba_box = ba['pos']
            match_index = -1
            # find match box
            for j, c in enumerate(clusters):
                if j in visited:
                    continue
                center = c['center']
                if box_match_center(center, ba_box):
                    # visited.add(j)
                    match_index = j
                    break
            if match_index != -1:
                # if any match box
                box_match_c+=1
                cluster = clusters[match_index]
                bl = ba['label']
                cls = []
                count_dict = defaultdict(int)
                cluster_total_w = 0
                # calculate new label
                for annotation in cluster['annotation']:
                    l = annotation['label']
                    cls.append(l)
                    auditorId = annotation['auditorId']
                    w = weight[auditorId]
                    cluster_total_w += w
                    count_dict[l] += w
                # for k in count_dict:
                #     count_dict[k] /= cluster_total_w
                count_list = [(k, v) for k, v in count_dict.items()]
                count_list.sort(key=lambda x: x[1], reverse=True)
                estimate_label = count_list[0][0]
                if bl == estimate_label:
                    all_match_c += 1
                else:
                    # print(bl, cls, estimate_label)
                    pass
                if bl not in cls:
                    total_miss_c += 1
    # for auditorId in weight:
    #     print(auditorId, weight[auditorId],distance[auditorId]/total_distance)
    print("cluster num after sanitized", sanitized_cluster_c)
    print("box match baseline count {}, match rate {}".format(box_match_c, box_match_c / baseline_c))
    print("all match basline count {}, accuracy {}, match rate {}".format(all_match_c, all_match_c / sanitized_cluster_c,
                                                                          all_match_c / baseline_c))
    print("not possible count {}".format(total_miss_c))

# this works as majority vote
def two_level_truth_discovery(image_clusters, all_annotations):
    sanitized_cluster_c = 0
    box_match_c = 0  # only box match
    all_match_c = 0  # box + label match
    baseline_c = 0

    image_difficulty = compute_image_difficulty(image_clusters, all_annotations)
    # truth discovery to remove unnecessary cluster (object)
    # initialize weight
    weight = dict()
    # get all user id
    all_auditor_id = set()
    for annotations in all_annotations:
        for annotation in annotations['annotation']:
            all_auditor_id.add(annotation['auditorId'])
    for k in all_auditor_id:
        weight[k] = 1

    T1 = 10  # truth discovery round
    for t in range(T1):
        # initialize distance
        distance = dict()
        for k in all_auditor_id:
            distance[k] = 0
        for i, image_cluster in enumerate(image_clusters):
            # get auditor id annotate this image
            annotations = all_annotations[i]
            difficulty = image_difficulty[i]
            annotate_auditor_id = set()
            for annotation in annotations['annotation']:
                annotate_auditor_id.add(annotation['auditorId'])

            for cluster in image_cluster['clusters']:
                count_dict = dict()
                cluster_total_w = 0
                # calculate box indicator (if the box is necessary)
                support_auditor_id = []
                for annotation in cluster['annotation']:
                    auditorId = annotation['auditorId']
                    support_auditor_id.append(auditorId)

                if len(support_auditor_id)!= len(set(support_auditor_id)):
                    raise Exception("worker support same cluster twice")
                support_auditor_id = set(support_auditor_id)

                non_support_auditor_id = set()
                for auditorId in annotate_auditor_id:
                    if auditorId not in support_auditor_id:
                        non_support_auditor_id.add(auditorId)

                # calculate weight for support and non-support
                support_weight = 0
                non_support_weight = 0
                for auditorId in support_auditor_id:
                    w = weight[auditorId]
                    support_weight += w * difficulty

                for auditorId in non_support_auditor_id:
                    w = weight[auditorId]
                    non_support_weight += w

                total_w = support_weight + non_support_weight
                support_weight /= total_w
                non_support_weight /= total_w

                for auditorId in support_auditor_id:
                    distance[auditorId] += (non_support_weight ** 2 + (1-support_weight) ** 2) ** 0.5

                for auditorId in non_support_auditor_id:
                    distance[auditorId] += ((1-non_support_weight) ** 2 + support_weight ** 2) ** 0.5
        # calculate new_weight
        total_distance = sum(distance.values())
        for auditorId in weight:
            # weight[auditorId] = -log(distance[auditorId] / total_distance)
            weight[auditorId] = total_distance / distance[auditorId]

    # remove unnecessary cluster
    for i, image_cluster in enumerate(image_clusters):
        # get auditor id annotate this image
        annotations = all_annotations[i]

        annotate_auditor_id = set()
        for annotation in annotations['annotation']:
            annotate_auditor_id.add(annotation['auditorId'])

        clusters = image_cluster['clusters']
        sanitized_clusters = []
        for cluster in clusters:
            count_dict = dict()
            cluster_total_w = 0
            # calculate box indicator (if the box is necessary)
            support_auditor_id = []
            for annotation in cluster['annotation']:
                auditorId = annotation['auditorId']
                support_auditor_id.append(auditorId)

            if len(support_auditor_id) != len(set(support_auditor_id)):
                raise Exception("worker support same cluster twice")
            support_auditor_id = set(support_auditor_id)

            non_support_auditor_id = set()
            for auditorId in annotate_auditor_id:
                if auditorId not in support_auditor_id:
                    non_support_auditor_id.add(auditorId)

            # calculate weight for support and non-support
            support_weight = 0
            non_support_weight = 0
            for auditorId in support_auditor_id:
                w = weight[auditorId]
                support_weight += w * difficulty

            for auditorId in non_support_auditor_id:
                w = weight[auditorId]
                non_support_weight += w

            total_w = support_weight + non_support_weight
            support_weight /= total_w
            non_support_weight /= total_w
            if support_weight >= non_support_weight:
                sanitized_clusters.append(cluster)
        clusters = sanitized_clusters
        image_cluster['clusters'] = clusters
        sanitized_cluster_c += len(clusters)

        baseline = image_cluster['baseline']
        baseline_c += len(baseline)
        visited = set()
        for ba in baseline:
            ba_box = ba['pos']
            match_index = -1
            # find match box
            for j, c in enumerate(clusters):
                if j in visited:
                    continue
                center = c['center']
                if box_match_center(center, ba_box):
                    box_match_c += 1
                    visited.add(j)
                    match_index = j
                    break
    print("cluster num after sanitized", sanitized_cluster_c)
    print("box match baseline count {}, match rate {}".format(box_match_c, box_match_c / baseline_c))
    # v = list(weight.values())
    # print(v[:20])

    # truth discovery to discover label
    #use new initialize weight
    weight = dict()
    for k in all_auditor_id:
        weight[k] = 1

    # use previous weight
    T2 = 10  # truth discovery round
    for t in range(T2):
        # initialize distance
        distance = dict()
        for k in all_auditor_id:
            distance[k] = 0
        for i, image_cluster in enumerate(image_clusters):
            # get auditor id annotate this image
            annotations = all_annotations[i]

            annotate_auditor_id = set()
            for annotation in annotations['annotation']:
                annotate_auditor_id.add(annotation['auditorId'])

            for cluster in image_cluster['clusters']:
                count_dict = dict()
                cluster_total_w = 0
                # calculate new label
                for annotation in cluster['annotation']:
                    l = annotation['label']
                    auditorId = annotation['auditorId']
                    w = weight[auditorId]
                    cluster_total_w += w
                    if l not in count_dict:
                        count_dict[l] = w
                    else:
                        count_dict[l] += w
                for k in count_dict:
                    count_dict[k]/= cluster_total_w
                # calculate distance for each worker
                auditor_annotation = defaultdict(list)
                for annotation in cluster['annotation']:
                    l = annotation['label']
                    auditorId = annotation['auditorId']
                    auditor_annotation[auditorId].append(l)

                # check if two or more annotation by one auditor in a cluster
                for auditorId in auditor_annotation:
                    if len(auditor_annotation[auditorId]) != 1:
                        raise Exception("two or more annotation by one auditor in a cluster")

                # distance    Euclidean distance
                sub_distance = dict()
                for auditorId in auditor_annotation:
                    sub_distance[auditorId] = 0

                for label in count_dict:
                    w = count_dict[label]
                    for auditorId in auditor_annotation:
                        if label in auditor_annotation[auditorId]:
                            sub_distance[auditorId] += (1-w)**2
                        else:
                            sub_distance[auditorId] += w**2

                for auditorId in sub_distance:
                    sub_distance[auditorId] = sub_distance[auditorId] ** 0.5
                    # add to total distance
                    distance[auditorId] += sub_distance[auditorId]
        # calculate new_weight
        total_distance = sum(distance.values())
        for auditorId in weight:
            weight[auditorId] = -log(distance[auditorId]/total_distance)

    # benchmark cluster label
    for i, image_cluster in enumerate(image_clusters):
        # get auditor id annotate this image
        annotations = all_annotations[i]

        annotate_auditor_id = set()
        for annotation in annotations['annotation']:
            annotate_auditor_id.add(annotation['auditorId'])

        clusters = image_cluster['clusters']

        baseline = image_cluster['baseline']
        # baseline_c += len(baseline)
        visited = set()
        for ba in baseline:
            ba_box = ba['pos']
            match_index = -1
            # find match box
            for j, c in enumerate(clusters):
                if j in visited:
                    continue
                center = c['center']
                if box_match_center(center, ba_box):
                    visited.add(j)
                    match_index = j
                    break
            if match_index != -1:
                # if any match box
                cluster = clusters[match_index]
                bl = ba['label']
                cls=[]
                count_dict = dict()
                cluster_total_w = 0
                # calculate new label
                for annotation in cluster['annotation']:
                    l = annotation['label']
                    cls.append(l)
                    auditorId = annotation['auditorId']
                    w = weight[auditorId]
                    cluster_total_w += w
                    if l not in count_dict:
                        count_dict[l] = w
                    else:
                        count_dict[l] += w
                for k in count_dict:
                    count_dict[k] /= cluster_total_w
                count_list = [(k, v) for k, v in count_dict.items()]
                count_list.sort(key=lambda x: x[1], reverse=True)
                estimate_label = count_list[0][0]
                if bl == estimate_label:
                    all_match_c += 1
                else:
                    # print(bl, cls, estimate_label)
                    pass
    print("all match basline count {}, accuracy {}, match rate {}".format(all_match_c, all_match_c/sanitized_cluster_c ,all_match_c/baseline_c))
