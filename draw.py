import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button

def read_excel_data(file_path):
    """
    从Excel文件中读取墙体和楼板的坐标数据
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        tuple: (wall_data, slab1_data, stair_data) 包含三种结构的坐标数据
    """
    try:
        df_wall = pd.read_excel(file_path, sheet_name='wall')
        df_slab1 = pd.read_excel(file_path, sheet_name='slab1')
        
        # 跳过第一行（标题行），提取第3-6列（x_start, x_end, y_start, y_end）
        wall_data = df_wall.iloc[1:, 2:6].values  # wall表格从第2行开始读
        slab1_data = df_slab1.iloc[2:, 2:6].values  # slab1表格从第3行开始读
        
        # 数据验证：确保数据不为空
        if wall_data.size == 0:
            print("警告：墙体数据为空")
        if slab1_data.size == 0:
            print("警告：楼板数据为空")
        
        return wall_data, slab1_data, None
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return None, None, None
    except Exception as e:
        print(f"读取Excel文件时发生错误：{str(e)}")
        return None, None, None

def read_sensor_data(file_path):
    """
    从Excel文件中读取传感器的坐标数据
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        numpy array: 传感器坐标数据，每行包含(x, y)
    """
    try:
        df_sensor = pd.read_excel(file_path, sheet_name='Sheet1')
        
        # 从第2行开始读，提取D列和E列（x坐标, y坐标）
        sensor_data = df_sensor.iloc[1:, 3:5].values  # D列是索引3，E列是索引4
        
        # 数据验证：确保数据不为空
        if sensor_data.size == 0:
            print("警告：传感器数据为空")
        
        return sensor_data
        
    except FileNotFoundError:
        print(f"错误：找不到传感器文件 {file_path}")
        return None
    except Exception as e:
        print(f"读取传感器Excel文件时发生错误：{str(e)}")
        return None

class BuildingPlanViewer:
    """
    建筑平面图查看器，支持缩放和平移功能
    """
    
    def __init__(self, wall_data, slab1_data, stair_data=None, sensor_data=None, initial_center=None, initial_zoom=1.0):
        self.wall_data = wall_data
        self.slab1_data = slab1_data
        self.stair_data = stair_data
        self.sensor_data = sensor_data
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.base_scale = 1.0
        self.current_scale = 1.0
        self.x_limits = None
        self.y_limits = None
        self.initial_center = initial_center
        self.initial_zoom = initial_zoom
        
        self.setup_plot()
        self.setup_events()
        
    def setup_plot(self):
        """设置绘图内容"""
        # 绘制楼板（底层）
        for row in self.slab1_data:
            x_start, x_end, y_start, y_end = row
            width = x_end - x_start
            height = y_end - y_start
            rect = Rectangle((x_start, y_start), width, height, 
                            facecolor='lightblue', edgecolor='blue', 
                            linewidth=1, alpha=0.5, label='楼板')
            self.ax.add_patch(rect)
        
        # 绘制墙体（中层）
        for row in self.wall_data:
            x_start, x_end, y_start, y_end = row
            width = x_end - x_start
            height = y_end - y_start
            rect = Rectangle((x_start, y_start), width, height, 
                            facecolor='gray', edgecolor='black', 
                            linewidth=2, alpha=0.8, label='墙体')
            self.ax.add_patch(rect)
        
        # 绘制楼梯（顶层） - 仅当楼梯数据存在时绘制
        if self.stair_data is not None and len(self.stair_data) > 0:
            for row in self.stair_data:
                x_start, x_end, y_start, y_end = row
                width = x_end - x_start
                height = y_end - y_start
                rect = Rectangle((x_start, y_start), width, height, 
                                facecolor='orange', edgecolor='red', 
                                linewidth=1.5, alpha=0.6, label='楼梯')
                self.ax.add_patch(rect)
        
        # 绘制传感器点位（最上层） - 仅当传感器数据存在时绘制
        if self.sensor_data is not None and len(self.sensor_data) > 0:
            x_coords = self.sensor_data[:, 0]
            y_coords = self.sensor_data[:, 1]
            self.ax.scatter(x_coords, y_coords, color='red', s=50, marker='o', alpha=0.8, label='传感器点位')
        
        # 设置坐标轴标签和标题
        self.ax.set_xlabel('X轴 (米)', fontsize=12)
        self.ax.set_ylabel('Y轴 (米)', fontsize=12)
        self.ax.set_title('建筑二维平面俯视图\n操作提示：鼠标滚轮缩放 | 拖拽平移 | +/-键缩放 | r键重置', 
                         fontsize=14, pad=20)
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.set_aspect('equal')
        
        # 添加图例
        from matplotlib.lines import Line2D
        from matplotlib.patches import Circle
        legend_elements = [
            Line2D([0], [0], color='lightblue', lw=4, label='楼板'),
            Line2D([0], [0], color='gray', lw=4, label='墙体')
        ]
        
        # 如果有传感器数据，添加传感器图例
        if self.sensor_data is not None and len(self.sensor_data) > 0:
            legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='传感器点位'))
        
        self.ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        # 保存初始坐标范围
        self.x_limits = self.ax.get_xlim()
        self.y_limits = self.ax.get_ylim()
        
        # 设置初始视角到指定位置
        if self.initial_center is not None:
            self.set_initial_view(self.initial_center, self.initial_zoom)
        
        plt.tight_layout()
        
    def setup_events(self):
        """设置事件监听"""
        # 鼠标滚轮事件
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        # 键盘事件
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
    def set_initial_view(self, center, zoom_level):
        """设置初始视角到指定位置和缩放级别
        
        Args:
            center: 元组 (x, y)，视图中心坐标
            zoom_level: 缩放级别，1.0表示原始大小，小于1表示放大，大于1表示缩小
        """
        x_center, y_center = center
        
        # 获取当前视图范围
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        # 计算当前视图的宽度和高度
        current_width = cur_xlim[1] - cur_xlim[0]
        current_height = cur_ylim[1] - cur_ylim[0]
        
        # 根据缩放级别计算新的视图范围
        new_width = current_width * zoom_level
        new_height = current_height * zoom_level
        
        # 设置新的视图范围，以指定坐标为中心
        self.ax.set_xlim([x_center - new_width / 2, x_center + new_width / 2])
        self.ax.set_ylim([y_center - new_height / 2, y_center + new_height / 2])
        
        # 更新初始坐标范围，以便重置时使用
        self.x_limits = self.ax.get_xlim()
        self.y_limits = self.ax.get_ylim()
        
    def on_scroll(self, event):
        """处理鼠标滚轮缩放"""
        if event.inaxes != self.ax:
            return
        
        base_scale = 1.1
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
        
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            scale_factor = 1
        
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        
        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        
        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        
        self.fig.canvas.draw_idle()
        
    def on_key_press(self, event):
        """处理键盘事件"""
        if event.key == 'r' or event.key == 'R':
            self.reset_view()
        elif event.key == '+' or event.key == '=':
            self.zoom(1.2)
        elif event.key == '-':
            self.zoom(0.8)
        elif event.key == 'up':
            self.pan(0, 0.1)
        elif event.key == 'down':
            self.pan(0, -0.1)
        elif event.key == 'left':
            self.pan(-0.1, 0)
        elif event.key == 'right':
            self.pan(0.1, 0)
            
    def zoom(self, scale_factor):
        """缩放视图"""
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        x_center = (cur_xlim[0] + cur_xlim[1]) / 2
        y_center = (cur_ylim[0] + cur_ylim[1]) / 2
        
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        
        self.ax.set_xlim([x_center - new_width / 2, x_center + new_width / 2])
        self.ax.set_ylim([y_center - new_height / 2, y_center + new_height / 2])
        
        self.fig.canvas.draw_idle()
        
    def pan(self, dx, dy):
        """平移视图"""
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        width = cur_xlim[1] - cur_xlim[0]
        height = cur_ylim[1] - cur_ylim[0]
        
        self.ax.set_xlim([cur_xlim[0] + dx * width, cur_xlim[1] + dx * width])
        self.ax.set_ylim([cur_ylim[0] + dy * height, cur_ylim[1] + dy * height])
        
        self.fig.canvas.draw_idle()
        
    def reset_view(self):
        """重置视图到初始状态"""
        self.ax.set_xlim(self.x_limits)
        self.ax.set_ylim(self.y_limits)
        self.fig.canvas.draw_idle()
        
    def save_and_show(self):
        """保存并显示图形"""
        plt.savefig('building_plan.png', dpi=300, bbox_inches='tight')
        print("图形已保存为 building_plan.png")
        print("\n操作说明：")
        print("  - 鼠标滚轮：以鼠标位置为中心缩放")
        print("  - 鼠标拖拽：平移视图")
        print("  - + 键：放大")
        print("  - - 键：缩小")
        print("  - r 键：重置视图")
        print("  - 方向键：平移视图")
        plt.show()

def draw_building_plan(wall_data, slab1_data, stair_data=None, sensor_data=None, initial_center=None, initial_zoom=0.5):
    """
    绘制建筑二维平面俯视图
    
    Args:
        wall_data: 墙体坐标数据
        slab1_data: 楼板坐标数据
        stair_data: 楼梯坐标数据（可选，默认None）
        sensor_data: 传感器坐标数据（可选，默认None）
        initial_center: 初始视图中心坐标 (x, y)，默认为None（显示完整视图）
        initial_zoom: 初始缩放级别，默认0.5（放大2倍）
    """
    viewer = BuildingPlanViewer(wall_data, slab1_data, stair_data, sensor_data, initial_center, initial_zoom)
    viewer.save_and_show()

def main():
    """
    主函数：读取数据并绘制建筑平面图
    """
    # 建筑数据文件路径
    building_file_path = r'corrdinate\2\2边界坐标.xlsx'
    # 传感器数据文件路径
    sensor_file_path = r'传感器\假传感器数据格式蓝色.xlsx'
    
    # 读取建筑数据
    wall_data, slab1_data, stair_data = read_excel_data(building_file_path)
    # 读取传感器数据
    sensor_data = read_sensor_data(sensor_file_path)
    
    # 调试打印：检查传感器数据是否成功读取
    if sensor_data is not None:
        print(f"成功读取传感器数据：{len(sensor_data)}个点位")
        if len(sensor_data) > 0:
            print(f"第一个传感器点位坐标：({sensor_data[0][0]}, {sensor_data[0][1]})")
    else:
        print("传感器数据读取失败或为空")
    
    # 检查数据是否成功读取（传感器数据为可选）
    if wall_data is not None and slab1_data is not None:
        # 设置初始视角中心坐标和缩放级别
        initial_center = (33950, 20000)
        initial_zoom = 0.5
        draw_building_plan(wall_data, slab1_data, stair_data, sensor_data, initial_center, initial_zoom)
    else:
        print("无法绘制建筑平面图：建筑数据读取失败")

if __name__ == '__main__':
    main()
