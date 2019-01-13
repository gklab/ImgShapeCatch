import cv2
import time
import numpy as np
import math

def extract_contour(imgName):
	# imgName = "WechatIMG11.jpeg"
	img = cv2.imread(imgName)
	source_img = img
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = cv2.GaussianBlur(img, (5, 5), 0, 0);
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
	img = cv2.dilate(img, kernel)
	img = cv2.Canny(img, 30, 120, 3)


	binary, contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	max_area = 0
	max_index = -1

	for i in range(len(contours)):
		tmp_area = abs(cv2.contourArea(contours[i]))
		if max_area < tmp_area:
			max_area = tmp_area
			max_index = i

	if max_index == -1:
		return 0

	temp_caver = np.ones(img.shape,np.uint8)*255
	cv2.drawContours(temp_caver, contours[max_index], -1, (123, 255, 123), 1)

	# 备选拐点
	corners = cv2.goodFeaturesToTrack(temp_caver,25,0.01,10) 
	corners = np.int0(corners)
	point_list = []
	for i in corners:
		x,y = i.ravel()
		point_list.append((x, y))

	corner_point = find_corner(point_list)

	sort_corner_list = sort_corner(corner_point)

	hight, width = calSize(sort_corner_list)

	# quad = cv2.zeros(hight, width, cv2.CV_8UC3)

	aim_size = np.float32([[0,0],[width,0],[width,hight],[0,hight]])
	
	raw_size = []
	for x,y in corner_point:
		raw_size.append([x,y])
	raw_size = np.float32(raw_size)
	translate_map = cv2.getPerspectiveTransform(raw_size, aim_size)
	translate_img = cv2.warpPerspective(source_img, translate_map, (int(width),int(hight)))


	'''
	for tmp_index in corner_point:
		cv2.circle(temp_caver,point_list[tmp_index],3,123,-1)
	print (corner_point)
	'''
	cv2.imwrite("new_WechatIMG11.jpg", translate_img);

def calSize(sort_corner_list):
	h1 = math.sqrt((sort_corner_list[0][0] - sort_corner_list[3][0]) * (sort_corner_list[0][0] - sort_corner_list[3][0]) + (sort_corner_list[0][1] - sort_corner_list[3][1]) * (sort_corner_list[0][1] - sort_corner_list[3][1]))
	h2 = math.sqrt((sort_corner_list[1][0] - sort_corner_list[2][0]) * (sort_corner_list[1][0] - sort_corner_list[2][0]) + (sort_corner_list[1][1] - sort_corner_list[2][1]) * (sort_corner_list[1][1] - sort_corner_list[2][1]))
	hight = max(h1, h2)

	w1 = math.sqrt((sort_corner_list[0][0] - sort_corner_list[1][0]) * (sort_corner_list[0][0] - sort_corner_list[1][0]) + (sort_corner_list[0][1] - sort_corner_list[1][1]) * (sort_corner_list[0][1] - sort_corner_list[1][1]))
	w2 = math.sqrt((sort_corner_list[2][0] - sort_corner_list[3][0]) * (sort_corner_list[2][0] - sort_corner_list[3][0]) + (sort_corner_list[2][1] - sort_corner_list[3][1]) * (sort_corner_list[2][1] - sort_corner_list[3][1]))
	width = max(w1, w2)
	return hight, width
def sort_corner(corner_point):
	# print (corner_point)
	for i in range(len(corner_point)):
		for j in range(i + 1, len(corner_point)):
			if corner_point[i][1] > corner_point[j][1]:
				tmp = corner_point[j]
				corner_point[j] = corner_point[i]
				corner_point[i] = tmp
	top = corner_point[:2]
	bot = corner_point[2:]

	if top[0][0] > top[1][0]:
		tmp = top[1]
		top[1] = top[0]
		top[0] = tmp

	if bot[0][0] > bot[1][0]:
		tmp = bot[1]
		bot[1] = bot[0]
		bot[0] = tmp

	tl = top[0]
	tr = top[1]
	bl = bot[0]
	br = bot[1]
	# print (tl, tr, bl, br)
	corners = [tl, tr, bl, br]
	return corners

def area(a, b, c):
	return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])

def find_corner(point_list):
	corner_num = len(point_list)
	ans = 0.0
	ans_point_index_list = [0, 0, 0, 0]
	m1_point = 0
	m2_point = 0
	for i in range(corner_num):
		for j in range(corner_num):
			if (i == j):
				continue
			m1 = 0.0
			m2 = 0.0
			
			for k in range(corner_num):
				if (k == i or k == j):
					continue
				a = point_list[i][1] - point_list[j][1]
				b = point_list[j][0] - point_list[i][0]
				c = point_list[i][0] * point_list[j][1] - point_list[j][0] * point_list[i][1]
				temp = a * point_list[k][0] + b * point_list[k][1] + c

				if (temp > 0):
					tmp_area = abs(area(point_list[i],point_list[j],point_list[k]) / 2)
					if tmp_area > m1:
						m1 = tmp_area
						m1_point = k

				elif (temp < 0):
					tmp_area = abs(area(point_list[i],point_list[j],point_list[k]) / 2)
					if tmp_area > m2:
						m2 = tmp_area
						m2_point = k

			if (m1 == 0.0 or m2 == 0.0):
				continue
			if (m1 + m2 > ans):
				ans_point_index_list[0] = i
				ans_point_index_list[1] = j
				ans_point_index_list[2] = m1_point
				ans_point_index_list[3] = m2_point
				ans = m1 + m2
	ans_point_list = []
	for i in ans_point_index_list:
		ans_point_list.append(point_list[i])
	return ans_point_list

extract_contour()


