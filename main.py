import flet as ft
import ViewModel

def main(page: ft.Page):

    page.window_width=1400
    page.window_height=800

    # 设置窗口是否可调整大小
    page.window.resizable = False  # 禁止调整窗口大小

    ViewModel_=ViewModel.ViewModel(page) # 创建 ViewModel 实例,传入page
    
    # 初始化共享的导航栏
    ViewModel_.init_navigation_bar(page)
    
    ViewModel_.page_home.controls = [
        ViewModel_.navigation_bar,
        ViewModel_.row_1,
        ViewModel_.row_2,
        ViewModel_.slider_column,
    ]

     # 设置 Page 1 的内容
    ViewModel_.page1.controls = [
        ViewModel_.navigation_bar,

        ft.Text("This is Page 1", style="headlineMedium"),
    ]

    # 设置 Page 2 的内容
    ViewModel_.page2.controls = [
        ViewModel_.navigation_bar,
        ViewModel_.log_container,
    ]
    
    page.views.append(ViewModel_.page_home)
    page.go("/")
    page.update()
    #print(len(ViewModel_.img_control_1.src_base64))
    #ViewModel_.update_image(page)
    # 启动日志更新任务
    ViewModel_.update_log(page)
    #启动图像刷新
    ViewModel_.start_capture_thread(page)

ft.app(target=main)
