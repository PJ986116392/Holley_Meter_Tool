from iec62056_21.client import Iec6205621Client,messages
import logging,time,datetime



class holley_meter:

    def __init__(self, port):
        self.meter = Iec6205621Client.with_serial_transport(port=port)
        self.meter.connect()
        self.logger = self._setup_logger()
        # 记录上一次操作时间
        self.last_time = time.time

    def _setup_logger(self):
        # 关闭IEC62056-21的日志
        logging.getLogger('iec62056_21').setLevel(logging.CRITICAL) 

        logger = logging.getLogger('Holley_meter')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def handshake(self):
        self.logger.info(f"开始握手，波特率：{self.meter.transport.port.baudrate}")
        # 握手
        self.meter.startup()
        self.meter.rest()
        self.logger.info("握手完成，波特率：{self.meter.transport.port.baudrate}")

    def is_ack(self):

        # 等待返回数据
        response = self.meter._recv_ack()

        # 如果有返回，且返回数据为0x06
        if response and response == '\x06':
            self.logger.info("ACK.")
            return True
        else:
            self.logger.info("NACK")
            return False

    def switch_baudrate(self, mode, baudrate=9600):
        self.logger.info(f"切换波特率到 {mode} 模式")
        mode_char = self.meter.MODE_CONTROL_CHARACTER[mode]
        ack_message = messages.AckOptionSelectMessage(
            mode_char=mode_char, baud_char=self.meter.switchover_baudrate_char
        )

        self.logger.info(f"Sending AckOptionsSelect message: {ack_message}")
        # 发送波特率切换命令
        self.meter.transport.send(ack_message.to_bytes())
        self.meter.rest()
        # 切换上位机波特率
        self.meter.transport.port.baudrate = baudrate
        self.logger.info(f"上位机波特率切换完成，当前波特率：{self.meter.transport.port.baudrate}")

        # 等待电能表回应
        pw_req = self.meter.read_response()

        return pw_req
    
    def password_auth(self, password) -> bool:
        """密码认证"""
        try:
            # 构建密码命令 (01 50 31 02 28 30 30 30 30 30 30 30 30 29 03 61)
            password_hex = password.encode('ascii').hex().upper()
            cmd = bytes.fromhex(f"01 50 31 02 28 {password_hex} 29 03 61")
            # 发送密码命令
            meter.meter.rest()
            self.meter.transport.send(cmd)
            return self.is_ack()

        except Exception as e:
            self.logger.error(f"认证失败: {str(e)}")
            return False

    def enter_factory_mode(self, password="00000000"):
        # 如果超过3秒没有操作，则重新握手和认证
        if time.time() - self.last_time > 3:
            # 300波特率握手
            self.handshake()
            # 波特率切换
            self.switch_baudrate(mode="programming")
            # 密码认证
            self.password_auth(password)
            # 进入工厂模式
            self.meter.rest()

        self.meter.write_single_value(address="A019", data="215A83D7")

        is_ack = self.is_ack()
        
        self.meter.rest()
        self.meter.transport.send(bytes.fromhex(f"01 42 30 03 71"))
        # 更新上一次操作时间
        self.last_time = time.time()
            
    def enter_second_pulse_mode(self):
        # 进入秒脉冲模式
        self.meter.enter_second_pulse_mode()
    
    def exit_second_pulse_mode(self):
        pass

    def exit_factory_mode(self,password="00000000"):
        # 如果超过3秒没有操作，则重新握手和认证
        if time.time() - self.last_time > 3:
            # 300波特率握手
            self.handshake()
            # 波特率切换
            self.switch_baudrate(mode="programming")
            # 密码认证
            self.password_auth(password)
        # 进入工厂模式
        self.meter.rest()
        self.meter.write_single_value(address="A018", data="55")

        is_ack = self.is_ack()
        
        self.meter.rest()
        self.meter.transport.send(bytes.fromhex(f"01 42 30 03 71"))
        # 更新上一次操作时间
        self.last_time = time.time()




if __name__ == "__main__":
    meter = holley_meter(port='COM8')
    try:
        meter.exit_factory_mode()


    finally:
        meter.meter.transport.send(bytes.fromhex(f"01 42 30 03 71"))
        meter.meter.disconnect()
