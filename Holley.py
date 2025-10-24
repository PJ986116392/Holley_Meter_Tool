from iec62056_21.client import Iec6205621Client,messages
import logging,time,datetime
class holley_meter:

    def __init__(self, port):
        self.meter = Iec6205621Client.with_serial_transport(port=port)
        self.meter.connect()
        self.logger = self._setup_logger()
        # 记录上一次操作时间
        self.last_time = time.time()

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






