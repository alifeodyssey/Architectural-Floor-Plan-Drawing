# Architectural-Floor-Plan-Drawing
一个通过excel表格里面的点位绘制建筑平面图的程序
一个绘图代码，通过读取我给出的excel表格的坐标数据，表格包含wall（墙体），slab1（楼板）。
绘制建筑的二维平面俯视图像
wall表格从第二行开始读，CDEF列分别是：X轴起点，X轴终点；y轴起点；y轴终点；
slab1表格从第3行开始读，CDEF列分别是：X轴起点，X轴终点；y轴起点；y轴终点；
在building_file_path = r'corrdinate\2\2边界坐标.xlsx'修改相对路径即可
