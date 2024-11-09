import cv2
import base64
from io import BytesIO
from io import StringIO
from PIL import Image
import logging
from datetime import datetime
import os
import threading
import time
from typing import List, Callable, get_type_hints
import inspect
from functools import partial
class Model:

    Banner_flag=False
    frame = None
    frame2 = None
    frame_process = None
    frame_img_base64=None
    frame2_img_base64=None
    slider_value = 0
    hub_flag = 1  # 用于控制灰度处理线程的标志
    
    def grey_process(self): #处理灰度
        try:
            grey_frame = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
            self.frame_process = grey_frame
            self.grey_img_base64 = self.base64_process(grey_frame)
            #print("灰度处理"+str(grey_frame[-10:-1]))
            #print("原图："+str(self.frame[-10:-1]))
        except Exception as e:
            self.Banner_flag=True
            print("灰度处理出错："+str(e))
            self.logger.error("灰度处理出错："+str(e))

    def threshold_process(self):
        try:
            slider_value = self.params['slider_value']
            print("阈值："+str(slider_value))
            _,threshold_frame = cv2.threshold(self.frame_process,slider_value,255,cv2.THRESH_BINARY)
            self.frame_process = threshold_frame
            self.threshold_img_base64 = self.base64_process(threshold_frame)
            
        except Exception as e:
            self.Banner_flag=True
            print("阈值处理出错："+str(e))
            self.logger.error("阈值处理出错："+str())

    def base64_process(self,frame): #处理并返回base64
        try:
            pil_frame = Image.fromarray(frame)
            buffer_frame = BytesIO()
            pil_frame.save(buffer_frame, format="JPEG")
            buffer_frame.seek(0)  # 确保读取从缓冲区的开始位置
            return base64.b64encode(buffer_frame.getvalue()).decode("utf-8")
        except Exception as e: 
            print("base64处理出错："+str(e))
            self.logger.error("base64处理出错："+str(e))

    def serivces_hub(self):  # 服务中心线程
            while self.hub_flag:
                try:
                    print("当前的服务列表：", self.service_list)
                    for func_name in self.service_list:
                        # 使用 getattr 从 self 获取函数对象
                        func = getattr(self, func_name, None)
                        if callable(func):
                            print("正在调用：" + func_name)
                            func()
                            
                        else:
                            print(f"未找到函数 {func_name} 或者它不可调用")

                    # 更新和处理图像等任务
                    self.frame2 = self.frame_process
                    self.frame2_img_base64 = self.base64_process(self.frame2)

                except Exception as e:
                    print("服务处理出错：" + str(e))
                    self.logger.error("服务处理出错：" + str(e))

    def update_param(self, key, value):
        """更新参数字典中的值"""
        self.params[key] = value
        #self.logger.info(f"参数 {key} 更新为 {value}")

    def __init__(self,):

        # 参数字典，用于存储动态参数
        self.params = {
            'slider_value': 0,  # 默认值，可由 slider 更新
            # 其他参数可以根据需要添加
        }


        # 获取当前系统时间，格式化为文件名
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"log_{current_time}.log"

        # 确保日志目录存在
        log_dir = "./logs"
        os.makedirs(log_dir, exist_ok=True)  # 创建 logs 文件夹（如果不存在）

        # 完整的日志文件路径
        log_filepath = os.path.join(log_dir, log_filename)

        # 创建 StringIO 对象用于存储日志
        self.log_stream = StringIO()

        # 创建一个独立的 logger 实例
        self.logger = logging.getLogger("PersistentLogger") #提供应用程序接口
        self.logger.setLevel(logging.DEBUG) #设置日志级别


        # 配置 StreamHandler，将日志写入 StringIO
        stream_handler = logging.StreamHandler(self.log_stream)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(stream_handler)  # 将 stream_handler 添加到 logger


        # 配置 FileHandler 并设置为无缓冲模式
        file_handler = logging.FileHandler(log_filepath, mode='a', delay=False)  # 立即创建文件
        #没有buffer缓冲，直接写入磁盘
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        # 将 FileHandler 添加到 logger
        self.logger.addHandler(file_handler)



        # 写入第一条日志，强制创建文件
        self.logger.debug("日志系统已启动，并保持文件打开状态以持续写入")



        # 添加控制台输出 handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # 设置 console_handler 的日志格式（formatter）
        # logging.Formatter 用于定义日志记录的输出格式
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))           
        # 将 console_handler 添加到 self.logger 中，使得日志信息可以输出到控制台
        # 每当 logger 记录日志时，console_handler 会格式化日志并输出到控制台
        # 多次调用 addHandler 可以为同一个 logger 添加多个处理器，实现多重输出（如文件和控制台）
        self.logger.addHandler(console_handler)
        

        # 测试写入日志
        self.logger.debug("Log等级测试")
        self.logger.info("This is an informational message.")
        self.logger.warning("Careful! Something does not look right.")
        self.logger.error("You have encountered an error.")
        self.logger.critical("The program cannot recover from this situation!")

        # "%(asctime)s - %(levelname)s - %(message)s" 是格式字符串，定义了输出的日志格式：
        # - `%(asctime)s`: 打印日志记录的时间戳，格式为年-月-日 小时:分钟:秒，便于追踪日志发生的时间
        # - `%(levelname)s`: 打印日志的级别名称（如 DEBUG, INFO, WARNING, ERROR, CRITICAL），便于快速识别日志的严重程度
        # - `%(message)s`: 打印日志的具体消息内容，即日志调用时传递的内容
        

        # 刷新 log_stream 缓冲区并重置游标位置
        self.log_stream.flush()
        #self.log_stream.seek(0)  # 重置游标到开始位置
        #print(print("!!!!!!!!"+self.log_stream.read()))
        
        try:

            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("无法打开摄像头")
                self.logger.error("无法打开摄像头")
            
            if self.cap.isOpened():  # 检查摄像头是否打开
                print("摄像头已打开")
                self.logger.info("摄像头准备就绪！")

        except:
            print("释放摄像头")
            self.logger.info("请重新检查相机设备和连接")
            self.cap.release()

        none_img = cv2.imread("./none_img.jpg")
        none_img = cv2.cvtColor(none_img,cv2.COLOR_BGR2RGB)
        
        # 使用 PIL 将图像转为字节流
        pil_img = Image.fromarray(none_img)
        buffer = BytesIO()
        pil_img.save(buffer, format="JPEG")
        self.none_img_base64=base64.b64encode(buffer.getvalue()).decode("utf-8")
        #print("默认图片base64:"+self.none_img_base64)  # 打印 base64 字符串
    
    def capture_get(self):
        while True:

            time.sleep(0.02)

            try:
                ret,frame = self.cap.read()
                #self.logger.info("camera:"+str(ret))

                if not ret:
                    break
                #print("camera:"+str(ret))

                if ret:
                    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                    self.frame = frame
                    #print("原图："+str(self.frame[-10:-1]))
                    self.frame_img_base64 = self.base64_process(frame)
                    #print("默认图片base64:"+self.none_img_base64)  # 打印 base64 字符串

            except  Exception as e:

                self.logger.error(e)
                self.logger.warning("读取帧失败！")

    def start_capture_thread(self):
        self.cap = cv2.VideoCapture(0)
        # 创建相机线程并将其设置为守护线程
        capture_thread = threading.Thread(target=self.capture_get)
        capture_thread.daemon = True  # 设置为守护线程
        capture_thread.start()  # 启动线程

    def stop_capture_thread(self):
        # 停止相机线程
        self.cap.release()

    def log_message(self, message):
        # 写一条日志信息
        self.logger.info(message)

                
            


