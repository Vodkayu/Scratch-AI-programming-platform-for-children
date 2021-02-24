# 仅用于说明，无法运行该程序
from dazuiniao import kapian_out, predictper, biaoqing, genzong, lianxukapian
from luru import renlianluru
frame = 0
kp = 0
wkp = 0
biaoding = 0
flag_rl = 0
# 输入：图像、卡片出现多少次确定为卡片、无卡片多少次确定为间隔。
# 输出：卡片识别结果，如“A”，当返回0时，认为没有识别到卡片；识别展示图。
out, img = kapian_out(frame, kp, wkp)

# 输入：图像。
# 输出：识别到的所有人员名称，如“张三，李四，王五”，当返回0时，认为没有识别到人；识别展示图。
out, img = predictper(frame)

# 输入：图像。
# 输出：识别到面积最大的人脸表情信息，如“happy”，当返回0时，认为没有识别到人脸表情；识别展示图。
out, img = biaoqing(frame)

# 输入：图像、是否进行标框：biaoding=1时，为对图像帧进行标框操作，为0时，为标框后的跟踪操作。
# 输出：跟踪物体的中心坐标，如123，123，两个整数型；识别展示图。
out1, out2, img = genzong(frame, biaoding)

# 输入：图像、卡片出现多少次确定为卡片、无卡片多少次确定为间隔。
# 输出：连续数字卡片识别结果，如“1+2+3=6”；连续字母卡片识别结果，如“ABC”；识别展示图。
out, img = lianxukapian(frame, kp, wkp)

# 输入：图像，按q进行保存当前帧。
# 输出：将图像保存至./renlian文件夹下（需要进行的操作：将图片在./picture文件夹下归档）。
renlianluru(frame)