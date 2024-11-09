import flet as ft
import Model
import threading
import logging
import time
import asyncio
from functools import partial
class ViewModel:

    Model_ = Model.Model()
    service_list=[]
    
    def close_banner(self,e):
        self.Model_.Banner_flag=0
        self.page.close(self.banner)


    #灰度两个事件的绑定
    def grey_change(self,e):
        self.switch_service()
        self.on_grey_change()

    #阈值的事件绑定
    def theshold_change(self,e):
        self.switch_service()
        if self.threshold_switch.value:
            self.Model_.logger.info("已开启阈值模式")
        else:
            self.Model_.logger.info("已关闭阈值模式")

    def switch_service(self):
        # 移除不需要的服务，保留未关闭的服务名称
        self.service_list = [
            func for func in self.service_list
            if (func != "grey_process" or self.grey_switch.value) and
            (func != "threshold_process" or self.threshold_switch.value)
        ]

        # 根据灰度开关状态添加灰度处理服务
        if self.grey_switch.value:
            # 如果灰度服务未在列表中，添加它
            if "grey_process" not in self.service_list:
                self.service_list.append("grey_process")

        # 根据阈值开关状态添加阈值处理服务
        if self.threshold_switch.value:
            # 如果阈值服务未在列表中，添加它
            if "threshold_process" not in self.service_list:
                self.service_list.append("threshold_process")

        # 记录当前服务状态
        #self.Model_.logger.info("当前的服务列表为：" + ", ".join(self.service_list) if self.service_list else "所有服务均已关闭")
        print("service_list:", self.service_list)

        #刷新Model.py的服务
        self.Model_.service_list = self.service_list


        
    #相机开关
    camera_switch = ft.CupertinoSwitch(
            label="开启相机",
            value=False,
            active_color=ft.colors.GREEN,
            focus_color=ft.colors.GREY,
            track_color=ft.colors.RED,
        )
    
    #灰度开关
    grey_switch = ft.CupertinoSwitch(
            label="开启灰度",
            value=False,
            active_color=ft.colors.GREEN,
            focus_color=ft.colors.GREY,
            track_color=ft.colors.RED,
        )
    
    #阈值开关
    threshold_switch = ft.CupertinoSwitch(
            label="开启阈值",
            value=False,
            active_color=ft.colors.GREEN,
            focus_color=ft.colors.GREY,
            track_color=ft.colors.RED,
        )
    
    
    #阈值滑动条
    slider=ft.CupertinoSlider(
        divisions=255,
        min=0,
        max=255,
        active_color=ft.colors.PURPLE,
    )
    
    # 阈值滑动条状态提示
    slider_status = ft.Text(value="hreshold", expand=True,width=200,height=20,
                           
                           )
    
    # 阈值滑动条值提示
    slider_value = ft.Text(value="灰度阈值:1.0", expand=True,width=200,height=20,
                           
                           )
    
    # 日志显示的 Text 控件
    log_text = ft.Text(value="", expand=True,width=1300,height=600,
                           
                           )
    
    log_head = ft.Text(value="日志输出：",style=ft.TextStyle(
        color=ft.colors.WHITE60,
        weight=ft.FontWeight.BOLD,
        size=20       # 设置字体大小
    ))

    log_column = ft.Column(
        [
            log_head,
            log_text
        ],
        horizontal_alignment=ft.CrossAxisAlignment.START
    )

    slider_column = ft.Column(
        [
            slider_value,
            slider,
            slider_status
        ],
        horizontal_alignment=ft.CrossAxisAlignment.START
    )

    #日志容器控件
    log_container = ft.Container(
        content=log_column,
        bgcolor=ft.colors.BROWN_200,
        padding=10,
        margin=10,
        border_radius=ft.border_radius.all(10),
    )

    # 创建页面的占位符
    page_home = ft.View("/" ,bgcolor=ft.colors.BROWN)
    page1 = ft.View("/page1",bgcolor=ft.colors.BROWN)
    page2 = ft.View("/page2",bgcolor=ft.colors.BROWN)

    img_1 = ft.Image(
            src_base64="",  # 替换为你的图片URL或 base64
            width=640,
            height=480
        )
    
    img_2 = ft.Image(
            src_base64="",  # 替换为你的图片URL或 base64
            width=640,
            height=480
        )
    

    #图像控件
    img_control_1 = ft.Container(
        content=img_1,
        # 设置边框颜色和宽度
        border=ft.border.all(3, ft.colors.BLACK),  # 3像素的黑色边框
        border_radius=ft.border_radius.all(5),     # 设置圆角，可选
        padding=5                                  # 可选的内部边距
    )

    img_control_2 = ft.Container(
        content=img_2,
        # 设置边框颜色和宽度
        border=ft.border.all(3, ft.colors.BLACK),  # 3像素的黑色边框
        border_radius=ft.border_radius.all(5),     # 设置圆角，可选
        padding=5                                  # 可选的内部边距
    )
    
    row_1=ft.Row(
        [
            
            img_control_1,
            img_control_2
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # 将两个图像在行中居中对齐
    )

    row_2=ft.Row(
        [
            camera_switch,
            grey_switch,
            threshold_switch
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # 将两个图像在行中居中对齐
    )

    # 创建一个带有页面边距的容器
    container_home = ft.Container(
        bgcolor=ft.colors.BLUE_200,
        margin=ft.margin.all(5),  # 设置与页面四边的外边距为 5 像素
        border_radius=ft.border_radius.all(10),  # 可选，设置圆角
        content=row_1
    )
    
    # 创建导航栏实例（共享）
    navigation_bar = None
    animated_switcher = None

    action_button_style = ft.ButtonStyle(color=ft.colors.BLUE)
    #初始化
    def __init__(self,page):
        
        self.Model_ = Model.Model()
        self.camera_switch.on_change = self.on_camera_change
        self.grey_switch.on_change = self.grey_change
        self.threshold_switch.on_change = self.theshold_change
        self.slider.on_change = self.handle_change
        
        #阈值滑动条绑定事件
        self.slider.on_change_start=self.handle_change_start
        self.slider.on_change = self.handle_change
        self.slider.on_change_end=self.handle_change_end

        self.banner_1 = False
        self.page = page

        # 将类属性 banner 和 page 绑定到实例属性
        self.banner = ft.Banner(
            bgcolor=ft.colors.AMBER_100,
            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40),
            content=ft.Text(
                value="点的太快了，等待一下相机！",
                color=ft.colors.BLACK,
            ),
            actions=[
                ft.TextButton(text="豪德", style=self.action_button_style, on_click=self.close_banner),
            ],
        )
        
    @staticmethod
    def init_navigation_bar(page):
        # 只初始化一次导航栏
        if ViewModel.navigation_bar is None:
            ViewModel.navigation_bar = ft.CupertinoNavigationBar(
                bgcolor=ft.colors.AMBER_100,
                inactive_color=ft.colors.GREY,
                active_color=ft.colors.BLACK,
                on_change=lambda e: ViewModel.on_tab_change(e, page),
                destinations=[
                    ft.NavigationBarDestination(icon=ft.icons.HOME, label="Home"),
                    ft.NavigationBarDestination(icon=ft.icons.COMMUTE, label="Commute"),
                    ft.NavigationBarDestination(
                        icon=ft.icons.BOOKMARK_BORDER,
                        selected_icon=ft.icons.BOOKMARK,
                        label="Explore",
                    ),
                ]
            )
        return ViewModel.navigation_bar
    
    # 处理导航栏标签的切换事件
    @staticmethod
    def on_tab_change(e, page):
        #print("转到："+str(e.control.selected_index))
        logging.info("跳转到了:", e.control.selected_index)

        # 清除当前视图
        page.views.clear()
        
        # 根据选中的标签索引添加不同的视图
        selected_index = e.control.selected_index
        if selected_index == 0:
            page.views.append(ViewModel.page_home)  # 直接添加主页视图
        elif selected_index == 1:
            page.views.append(ViewModel.page1)  # 直接添加 Page 1 视图
        elif selected_index == 2:
            page.views.append(ViewModel.page2)  # 直接添加 Page 2 视图

        # 刷新页面显示
        page.update()

    # def update_image(self,page):

    #     self.img_1.src_base64 = f"{self.Model_.frame_img_base64}"
    #     self.img_2.src_base64 = f"{self.Model_.frame_img_base64}"
    #     print("初始图像："+self.img_1.src_base64)

    #     if self.Model_.frame_img_base64  == "None":
            
    #         #print(self.Model_.none_img_base64)
    #         none_img_base64 = self.Model_.none_img_base64
    #         # 更新第一个摄像头的画面
    #         ViewModel.img_1.src_base64 = f"{none_img_base64}"
    #         ViewModel.img_2.src_base64 = f"{none_img_base64}"
            
    #         # 刷新页面显示
    #         page.update()

    #         # 每秒调用一次 update_log
    #         timer = threading.Timer(1, self.update_image, args=[page])
    #         timer.daemon = True  # 将 Timer 设为守护线程
    #         timer.start()
    
    def read_frame(self):
        self.Model_.capture_get()

    def handle_change_start(self,e):
        self.slider_status.value = "Sliding"

    def handle_change(self,e):
        self.slider_value.value = "灰度阈值:"+str(e.control.value)
                # 打印日志，确认函数是否被触发
        #self.Model_.logger.info("handle_change 已触发，当前 slider 值: " + str(e.control.value))
        
        # 更新显示的 slider_value 文本
        self.slider_value.value = "灰度阈值: " + str(e.control.value)
        
        # 更新 Model 中的 slider_value 参数
        self.Model_.update_param('slider_value', int(e.control.value))

        # 触发服务更新，确保 serivces_hub 使用最新参数
        self.switch_service()

    def handle_change_end(self,e):
        self.slider_status.value = "Finished sliding"

    #更新日志
    def update_log(self, page):
        # 获取日志内容并更新到页面

        # 刷新 log_stream 缓冲区并重置游标位置
        self.Model_.log_stream.flush()
        #self.Model_.log_stream.seek(0)  # 重置游标到开始位置

        self.log_text.value = self.Model_.log_stream.getvalue()

        page.update()
        
        # 每秒调用一次 update_log
        timer = threading.Timer(1, self.update_log, args=[page])
        timer.daemon = True  # 将 Timer 设为守护线程
        timer.start()


    #相机调用事件
    def on_camera_change(self,e):

        try:
            # 通过 self.flag 控制逻辑
            if self.camera_switch.value == True:
                self.Model_.logger.info("摄像头已开启")
                # 启动摄像头逻辑
                self.Model_.start_capture_thread()

            if self.camera_switch.value == False:
                self.Model_.logger.info("摄像头已关闭")
                self.Model_.stop_capture_thread()
                self.Model_.frame_img_base64 = None
        except Exception as e:
            self.Model_.logger.error(e)

    
            #sprint(self.Model_.log_stream.getvalue())

    #灰度作为处理的开始
    def on_grey_change(self):

        if self.grey_switch.value == True:
            self.Model_.logger.info("已开启灰度模式")
            self.grey_thread = threading.Thread(target=self.Model_.serivces_hub) # 创建线程，运用灰度
            self.grey_thread.daemon = True  # 设置为守护线程
            self.Model_.hub_flag = 1
            self.grey_thread.start()  # 启动线程

        if self.grey_switch.value == False:
            self.Model_.logger.info("已关闭灰度模式")
            self.Model_.hub_flag = 0
            if self.grey_thread.is_alive():
                self.grey_thread.join()
                self.Model_.grey_img_base64=None # 清空
                self.Model_.frame2_img_base64=None
                print("灰度 已停止")

    # 图像刷新线程
    def update_image_thread(self, page):
        while True:
            if self.Model_.frame_img_base64 is None:
                self.img_1.src_base64 = f"{self.Model_.none_img_base64}"
            else:
                self.img_1.src_base64 = f"{self.Model_.frame_img_base64}"
                
            if self.Model_.frame2_img_base64 is None:
                self.img_2.src_base64 = f"{self.Model_.none_img_base64}"
            else:
                self.img_2.src_base64 = f"{self.Model_.frame2_img_base64}"
            
            if self.Model_.Banner_flag:
                page.open(self.banner)
            
            page.update()
            time.sleep(0.02)  # 控制刷新频率
    # 启动图像刷新线程
    def start_capture_thread(self, page):
        self.img_thread = threading.Thread(target=self.update_image_thread, args=(page,))
        self.img_thread.daemon = True  # 设置为守护线程
        self.img_thread.start()  # 启动线程
    
    # 停止图像刷新线程
    def stop_capture_thread(self):
        self.update_flag = False  # 停止标志
        if self.img_thread.is_alive():
            self.img_thread.join()  # 等待线程安全结束


