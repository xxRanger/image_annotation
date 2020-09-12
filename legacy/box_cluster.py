import json

intersection_ratio_threshold = 0.75

five_file_path = "/Users/Qiyuan/Downloads/label/图像标注统计_5人标注_1591602800054.txt"
fifty_file_path = "/Users/Qiyuan/Downloads/label/图像标注统计_50人_20200609.txt"

write_to_file_path = '{}_people_results.json'

select = 50
if select==5:
    open_file_path = five_file_path
    write_to_file_path = write_to_file_path.format(5)
else:
    open_file_path = fifty_file_path
    write_to_file_path = write_to_file_path.format(50)

with open(open_file_path, 'r') as f:
    data = f.readlines()[37:]
    data = '\n'.join(data)
    data = json.loads(data)

print("Data type:", type(data))
print("List length:", len(data))


def two_points_to_normalized_two_points(start, end):
    start_x = start['x']
    start_y = start['y']
    end_x = end['x']
    end_y = end['y']
    min_x = min(start_x, end_x)
    max_x = max(start_x, end_x)
    min_y = min(start_y, end_y)
    max_y = max(start_y, end_y)
    point1 = {'x': min_x, 'y': min_y}
    point2 = {'x': max_x, 'y': max_y}
    two_points = {'upper_left_point': point1, 'lower_right_point': point2}
    region_size = (max_x - min_x) * (max_y - min_y)
    return two_points, region_size


def find_out_marker_info(img):
    mark_ans = []
    auditor = 'auditorId'
    key = 'MarkDetailDto'
    for i in range(1, 6):
        auditor_i = auditor + str(i)
        key_i = key + str(i)
        auditor_id = img[auditor_i]
        mark_info = img[key_i]
        if not mark_info:
            continue
        mark_info = json.loads(mark_info)
        mark_items = []
        for item in mark_info:
            label = item['tagOption']
            selectMarkResult = label['selectMarkResult']
            startPoint = item['startPoint']
            endPoint = item['endPoint']
            two_points, region_size = two_points_to_normalized_two_points(startPoint, endPoint)
            item_table = {'label_id': label['id'], 'selectMarkResult': selectMarkResult, 'two_points': two_points,
                          'region_size': region_size}
            mark_items.append(item_table)
        full_mark_info = {'auditor_id': auditor_id, 'mark_region': mark_items}
        mark_ans.append(full_mark_info)
    return mark_ans


def intersection_ratio(region_1, region_2):
    region_size_1 = region_1['region_size']
    region_size_2 = region_2['region_size']
    two_points_1 = region_1['two_points']
    two_points_2 = region_2['two_points']
    upper_left_1 = two_points_1['upper_left_point']
    upper_left_2 = two_points_2['upper_left_point']
    lower_right_1 = two_points_1['lower_right_point']
    lower_right_2 = two_points_2['lower_right_point']
    start_x = max(upper_left_1['x'], upper_left_2['x'])
    start_y = max(upper_left_1['y'], upper_left_2['y'])
    end_x = min(lower_right_1['x'], lower_right_2['x'])
    end_y = min(lower_right_1['y'], lower_right_2['y'])
    if start_x >= end_x or start_y >= end_y:
        return 0
    else:
        intersection_size = (end_x - start_x) * (end_y - start_y)
        ratio = intersection_size / min(region_size_1, region_size_2)
        return ratio


def process_region(mark_ans):
    # list of markers
    # [{auditor_id, mark_region}]
    all_regions = []
    for m in mark_ans:
        auditor_id = m['auditor_id']
        mark_regions = m['mark_region']
        for region in mark_regions:
            region_copy = region.copy()
            region_copy['auditor_id'] = auditor_id
            region_copy['in'] = 0
            all_regions.append((region_copy))

    big_to_small_regions = sorted(all_regions, key=lambda r: r['region_size'], reverse=True)

    all_clusters = []
    i = 0
    tot = len(big_to_small_regions)
    while True:
        cur_region = big_to_small_regions[i]
        if cur_region['in'] == 1:
            i += 1
            if i >= tot:
                break
        else:
            all_points = [[cur_region, i]]
            region_labels = []
            chosen_region = cur_region['two_points']
            while all_points:
                first_region = all_points[0][0]
                index = all_points[0][1]
                all_points.pop(0)
                region_labels.append({'label_id': first_region['label_id'],
                                      'selectMarkResult': first_region['selectMarkResult'],
                                      'auditor_id': first_region['auditor_id']})
                big_to_small_regions[index]['in'] = 1
                for j in range(index + 1, tot):
                    if intersection_ratio(first_region, big_to_small_regions[j]) > intersection_ratio_threshold \
                            and big_to_small_regions[j]['in'] == 0:
                        all_points.append([big_to_small_regions[j], j])

            cluster = {'two_points': chosen_region, 'region_labels': region_labels}
            all_clusters.append(cluster)
    print(len(all_clusters))
    return all_clusters


desired_output = {}

for id, img in enumerate(data):
    desired_output[id] = {}
    img_url = img['imgUrl']
    desired_output[id]['imgUrl'] = img_url
    desired_output[id]['ground_truth'] = []
    correct_answer = img['MarkDetailDto0']
    correct_answer = json.loads(correct_answer)
    for item in correct_answer:
        label = item['tagOption']
        selectMarkResult = label['selectMarkResult']
        startPoint = item['startPoint']
        endPoint = item['endPoint']
        two_points, region_size = two_points_to_normalized_two_points(startPoint, endPoint)
        item_table = {'label_id': label['id'], 'selectMarkResult': selectMarkResult, 'two_points': two_points}
        desired_output[id]['ground_truth'].append(item_table)

    mark_ans = find_out_marker_info(img)
    all_clusters = process_region(mark_ans)
    desired_output[id]['clusters'] = all_clusters

with open(write_to_file_path, 'w') as f:
    json.dump(desired_output, f)
