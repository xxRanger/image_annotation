import json 
import numpy as np
from collections import defaultdict
from math import log

truth_threshold = 0.2
overlap_threshold = 0.75
image_num = 1000

def read_json(file):
	f = open(file)
	data = json.load(f)
	f.close()
	return data


p5 = read_json('5_people_results.json')
p50 = read_json('50_people_results.json')
# print(p5['200'])




def get_settings(data):
	# get user id
	# get clusters number for each problem
	# get image cluster labels
	# get maximum label id 
	userid = set()
	cluster_num = [0] * image_num
	# image_cluster_labels = []
	print(data['3'])

	label_id = set()
	for i in range(image_num):
		info = data[str(i)]
		clusters = info['clusters']
		cluster_num[i] = len(clusters)

		# cluster_label = []

		for cluster in clusters:
			labels = []

			region_labels = cluster['region_labels']
			for rl in region_labels:
				uid = rl['auditor_id']
				userid.add(uid)
				lid = int(rl['label_id'])
				labels.append(lid)
				label_id.add(lid)
			# cluster_label.append(labels)
			# image_cluster_labels.append(labels)


	return list(userid), cluster_num, max(label_id)

def get_ground_truth(data):
	ground_truth = []
	for i in range(image_num):
		ground_truth.append(data[str(i)]['ground_truth'])
	return ground_truth

def get_clusters(data):
	clusters = []
	for i in range(image_num):
		clusters.append(data[str(i)]['clusters'])
	return clusters

def majority_vote(data):
	image_truth = []
	# update truth
	for i in range(image_num):
		info = data[str(i)]
		clusters = info['clusters']

		cluster_truth = []
		for j, cluster in enumerate(clusters):
			new_truth = np.zeros(max_label_id)
			labels = cluster['region_labels']

			user_label = defaultdict(list) # a user may provide several label for a cluster
			for label in labels:
				uid = label['auditor_id']
				label_id = int(label['label_id'])
				user_label[uid].append(label_id)

			total_w = 0
			for uid in user_label:
				w = user_weight[uid]
				total_w += w
				one_hot_encoder = np.zeros(max_label_id)
				for label_id in user_label[uid]:
					one_hot_encoder[label_id] = 1
				new_truth += w* one_hot_encoder

			new_truth /= total_w
			cluster_truth.append(new_truth)
		image_truth.append(cluster_truth)

	# update weight
	new_weight = defaultdict(int)
	#first get weight of every one
	for i in range(image_num):
		info = data[str(i)]
		clusters = info['clusters']

		for j, cluster in enumerate(clusters):
			labels = cluster['region_labels']

			user_label = defaultdict(list) 
			for label in labels:
				uid = label['auditor_id']
				label_id = int(label['label_id'])
				user_label[uid].append(label_id)

			truth = image_truth[i][j]
			for uid in user_label:
				one_hot_encoder = np.zeros(max_label_id)
				for label_id in user_label[uid]:
					one_hot_encoder[label_id] = 1
				distance = np.linalg.norm(one_hot_encoder - truth)
				new_weight[uid] += distance


#initialize weight

def truth_discovery(data):
	max_iter = 100
	userid, cluster_num, max_label_id = get_settings(data)
	max_label_id = max_label_id+1
	# print(cluster_num)
	user_num = len(userid)
	user_weight = dict() 
	# set equal weight 
	for uid in userid:
		user_weight[uid] = 1


	for iter_round in range(max_iter):
		image_truth = []
		# update truth
		for i in range(image_num):
			info = data[str(i)]
			clusters = info['clusters']

			cluster_truth = []
			for j, cluster in enumerate(clusters):
				new_truth = np.zeros(max_label_id)
				labels = cluster['region_labels']

				user_label = defaultdict(list) # a user may provide several label for a cluster
				for label in labels:
					uid = label['auditor_id']
					label_id = int(label['label_id'])
					user_label[uid].append(label_id)

				total_w = 0
				for uid in user_label:
					w = user_weight[uid]
					total_w += w
					one_hot_encoder = np.zeros(max_label_id)
					for label_id in user_label[uid]:
						one_hot_encoder[label_id] = 1
					new_truth += w* one_hot_encoder

				new_truth /= total_w
				cluster_truth.append(new_truth)
			image_truth.append(cluster_truth)

		# update weight
		new_weight = defaultdict(int)
		#first get weight of every one
		for i in range(image_num):
			info = data[str(i)]
			clusters = info['clusters']

			for j, cluster in enumerate(clusters):
				labels = cluster['region_labels']

				user_label = defaultdict(list) 
				for label in labels:
					uid = label['auditor_id']
					label_id = int(label['label_id'])
					user_label[uid].append(label_id)

				truth = image_truth[i][j]
				for uid in user_label:
					one_hot_encoder = np.zeros(max_label_id)
					for label_id in user_label[uid]:
						one_hot_encoder[label_id] = 1
					distance = np.linalg.norm(one_hot_encoder - truth)
					new_weight[uid] += distance
		# normalzie weight
		total_w = sum(new_weight.values())
		equal = True
		for uid in new_weight:
			w = new_weight[uid]
			w /= total_w
			w = -log(w)
			new_weight[uid] = w 
			if w!= user_weight[uid]:
				equal = False
		if equal:
			print("converge at iterations",iter_round)
			break
		user_weight = new_weight
		# print("iteration",iter_round,"weight")
		# print(user_weight)
	# get truth label 
	# print(image_truth[:10])
	for i in range(image_num):
		for j in range(cluster_num[i]):
			image_truth[i][j] = np.argmax(image_truth[i][j])
	return image_truth, user_weight


def cluster_ground_truth(clusters, ground_truth):
	for i in range(image_num):
		cls = clusters[i]
		ts = ground_truth[i]
		# assign cluster label, if no overlap exists, assign -1
		for t in ts:
			overlap = np.zeros(len(cls))
			t_two_points = t['two_points']
			t_upper_left = t_two_points['upper_left_point']
			t_lower_right_point = t_two_points['lower_right_point']
			t_area = abs(t_upper_left['x']-t_lower_right_point['x'])*abs(t_upper_left['y'] - t_lower_right_point['y'])
			# print(t_area)
			for j, c in enumerate(cls):
				c_two_points = c['two_points']
				# print(t_two_points, c_two_points)
				c_upper_left = c_two_points['upper_left_point']
				c_lower_right_point = c_two_points['lower_right_point']				
				
				olp_x = min(c_lower_right_point['x'] - t_upper_left['x'], t_lower_right_point['x']- c_upper_left['x'])
				olp_y = min(t_lower_right_point['y'] - c_upper_left['y'] , c_lower_right_point['y'] - t_upper_left['y'] )
				# check overlap
				if olp_x <= 0 or olp_y<=0:
					olp = 0
				else:
					# print('else')
					olp = olp_x * olp_y / t_area
				overlap[j] = olp 
				# print(olp)
			if len(overlap) == 0:
				t['cluster_index'] = -1
				continue
			max_index = np.argmax(overlap)
			if overlap[max_index] >= 0.75:
				t['cluster_index'] = max_index
			else:
				t['cluster_index'] = -1

def evaluate_result(image_truth, ground_truth):
	acc_total_user_clusters = 0
	acc_right_clusters = 0 # right in total

	acc_miss_clusters = 0 # ground_truth cluster has not been provided by user

	acc_precision = 0
	acc_recall = 0
	acc_f1 = 0

	for i in range(image_num):
		total_user_clusters = len(image_truth[i])

		right_clusters = 0 # right in total

		miss_clusters = 0 # ground_truth cluster has not been provided by user

		for gt in ground_truth[i]:
			cluster_index = gt['cluster_index']
			if cluster_index == -1:
				miss_clusters+=1
				continue
			gt_label = int(gt['label_id'])
			# print(cluster_index)
			label = image_truth[i][cluster_index]
			# print(gt_label, label)
			if gt_label == label:
				right_clusters+=1
			# else:
			# 	print(i, gt, label)


		acc_total_user_clusters += total_user_clusters
		acc_right_clusters += right_clusters
		acc_miss_clusters += miss_clusters

		precision = right_clusters/(total_user_clusters) if right_clusters else 0
		recall = right_clusters/ (right_clusters + miss_clusters) if right_clusters else 0
		f1 = 2* (precision*recall)/ (precision+ recall) if right_clusters else 0

		acc_precision += precision
		acc_recall += recall
		acc_f1 += f1 
	print(acc_total_user_clusters)
	print(acc_right_clusters)
	print(acc_miss_clusters)

	acc_precision/=image_num
	acc_recall/=image_num
	acc_f1 /= image_num
	
	return acc_precision,acc_recall,acc_f1


def remove_cluster(clusters, image_truth, user_weight):
	total_weight = sum(user_weight.values())
	for i in range(image_num):
		new_cluster = []
		new_truth = []
		for j, cluster in enumerate(clusters[i]):
			labels = cluster['region_labels']
			user = set() 
			for label in labels:
				uid = label['auditor_id']
				# label_id = int(label['label_id'])
				# user_label[uid].append(label_id)
				user.add(uid)
			acc_w = 0
			for uid in user:
				acc_w += user_weight[uid]
			if acc_w <= total_weight/len(user_weight):
				continue
			new_cluster.append(clusters[i][j])
			new_truth.append(image_truth[i][j])
		clusters[i] = new_cluster
		image_truth[i] = new_truth
		

def get_user_acc(ground_truth, data):
	u_score = dict()
	for i in range(image_num):
		clusters = data[str(i)]['clusters']
		gt = ground_truth[i]
		uid_label = defaultdict(list)
		for j,c in enumerate(clusters):
			user_labels = c['region_labels']
			# if uid not in u_score:
			# 	u_score[uid] = [0,0]
			for ul in user_labels:
				uid = ul['auditor_id']
				l = ul['label_id']
				uid_label[uid].append((j, l)) # (cluster, label)
		u_sub_score = dict()
		for g in gt:
			for uid in uid_label:
				miss_cluster = 0
				right_cluster = 0
				if g['cluster_index'] == -1:
					miss_cluster +=1
				else:
					match = False
					for ul in uid_label[uid]:
						if ul[0] == g['cluster_index'] and ul[1] == g['label_id']:
							match = True
					if match:
						right_cluster+=1
					else:
						miss_cluster+=1
				if uid not in u_sub_score:
					u_sub_score[uid] = [0,0,0]
				u_sub_score[uid][0] += right_cluster
				u_sub_score[uid][1] += miss_cluster
				u_sub_score[uid][2] += len(uid_label[uid])
		for u in u_sub_score:
			right_clusters = u_sub_score[u][0]
			miss_clusters = u_sub_score[u][1]
			total_user_clusters = u_sub_score[u][2]
			precision = right_clusters/(total_user_clusters) 
			recall = right_clusters/ (right_clusters + miss_clusters) 
		
			if u not in u_score:
				u_score[u] = [0,0,0,0]
			u_score[u][0] += precision
			u_score[u][1] += recall
			# print(right_clusters, miss_clusters, total_user_clusters)
			u_score[u][2] += 2* (precision*recall)/ (precision+ recall) if right_clusters else 0
			u_score[u][3] += 1

	for u in u_score:
		u_score[u][0] = u_score[u][0] / u_score[u][3]
		u_score[u][1] = u_score[u][1] / u_score[u][3]
		u_score[u][2] = u_score[u][2] / u_score[u][3]

	return u_score



data = p5
image_truth,user_weight = truth_discovery(data)
ground_truth = get_ground_truth(data)
clusters = get_clusters(data)
# remove low quality clusters 
remove_cluster(clusters, image_truth, user_weight)

# print(clusters)

# assign cluster to ground truth
cluster_ground_truth(clusters, ground_truth)
# print(ground_truth[:5])

pre,recall,f1 = evaluate_result(image_truth, ground_truth)
if data == p5:
	print("5 people")
else:
	print("50 people")
print("Aggregate average accuracy:{}, recall:{}, f1:{}".format(pre,recall,f1))
u_score = get_user_acc(ground_truth,data)
for u,v in u_score.items():
	print(v)
# print(u_score)
# print(user_weight)
print(user_weight)
print(u_score)
u_pre,u_recall,u_f1 = 0,0,0

accs = []
recalls = []
f1s = []
for u in u_score:
	u_pre += u_score[u][0]
	u_recall += u_score[u][1]
	u_f1 += u_score[u][2]

	accs.append(u_score[u][0])
	recalls.append(u_score[u][1])
	f1s.append(u_score[u][2])

u_pre/=len(u_score)
u_recall/=len(u_score)
u_f1/=len(u_score)
print("User average accuracy:{}, recall:{}".format(u_pre, u_recall, u_f1))

print("User max acc: {}, min acc: {}".format(max(accs),min(accs)))
print("User max recall: {}, min recall: {}".format(max(recalls),min(recalls)))




# print(user_weight)

# print(user_weight)
# print(image_truth[:10])
# truth_discovery(p5)