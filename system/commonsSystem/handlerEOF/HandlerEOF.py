import logging
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.CalculatorDTO import CalculatorDTO, STATUS_REQUEST, STATUS_RESPONSE
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.DataPartialDTO import DataPartialDTO, REQUEST_DATA_PARTIAL, RESPONSE_DATA_PARTIAL

class HandlerEOF:

    def __init__(self, target_name ="", broker = None, node_id =0, exchange_name = "", next_queues =[], total_nodes = 0):
        self.target_name = target_name
        self.target_id = None
        self.broker = broker
        self.data_individual = 0
        self.data_total_accumulated = 0
        self.data_definitive = 0
        self.controllers_recv = 0
        self.total_nodes = total_nodes
        self.node_id = node_id
        self.client_id = 0
        self.exchange_name = exchange_name
        self.next_queues = next_queues
        self.sent_first_partial = False
        self.i_am_lider = False
        self.eof_dto = None
        self.ready_to_send_eof = False
        self.sent_eof = False
        self.data_partial_sent = 0 #se usa en el caso de counters nodos q tienen q enviar lo q guardaron primero y al ultimo el EOF. 

    def add_new_processing(self):
        self.data_individual +=1
    
    def clean_amount(self):
        self.controllers_recv = 0
        self.data_total_accumulated = 0
    
    def initialize_lider(self, eof_dto):
        self.i_am_lider = True
        self.eof_dto = eof_dto
        self.client_id = eof_dto.client_id
        logging.info(f"action: Node ID: {self.node_id} Recv EOF! {self.i_am_lider} | result: success ✅")
        self.data_definitive = eof_dto.amount_data

    def init_lider_and_push_eof(self, eof_dto):
        self.initialize_lider(eof_dto)
        self.broker.public_message(exchange_name =self.exchange_name, message = CalculatorDTO(client_id =eof_dto.client_id,
                                    target_type =eof_dto.old_operation_type).serialize())

    def handler_data_partialDTO(self, dataPartialDTO, dto_to_send):
        if not self.i_am_lider and dto_to_send and dataPartialDTO.status == REQUEST_DATA_PARTIAL:
            self.broker.public_message(queue_name =self.next_queues[0], message =dto_to_send.serialize())
            logging.info(f"action: Send Partial Data 📦 to {self.next_queues[0]} | result: success ✅")
            self.broker.public_message(exchange_name=self.exchange_name, message =DataPartialDTO(status =RESPONSE_DATA_PARTIAL).serialize())
            logging.info(f"action: Send DataPartial (Response) to the Leader 🔥 ⚔️ | result: success ✅")
        elif self.i_am_lider and dataPartialDTO.status == RESPONSE_DATA_PARTIAL:
            self.data_partial_sent +=1
            if self.data_partial_sent == (self.total_nodes -1): 
                self.broker.public_message(queue_name =self.next_queues[0], message =dto_to_send.serialize())
                logging.info(f"action: I am the leader 🔥 sent my DataPartial | result: success ✅")
                self.send_eof_next_queues()
    
    def accumulate_calculate(self, calculatorDTO):
        self.data_total_accumulated += calculatorDTO.amount_data
        self.controllers_recv +=1
        logging.info(f"action: information Leader of EOF {self.target_name} 🔥 Amounts: Individual: {self.data_individual}"+
                     f" Total Accumulated: {self.data_total_accumulated} Definitive: {self.data_definitive} | result: success ✅ ")

    def run(self, calculatorDTO, auto_send = True, dto_to_send = None):
        if calculatorDTO.operation_type == OperationType.OPERATION_TYPE_DATA_PARTIAL_DTO:
            self.handler_data_partialDTO(calculatorDTO, dto_to_send)
            return
        self.client_id = calculatorDTO.client_id
        self.target_id = calculatorDTO.target_type
        if (calculatorDTO.status == STATUS_RESPONSE and self.i_am_lider):
            self.accumulate_calculate(calculatorDTO)
            if (self.data_total_accumulated + self.data_individual) == self.data_definitive:
                self.ready_to_send_eof = True
                if (auto_send):
                    self.send_eof_next_queues()
            elif self.controllers_recv == (self.total_nodes -1) and not self.sent_eof:
                self.broker.public_message(exchange_name =self.exchange_name,
                                        message =CalculatorDTO(client_id =self.client_id, target_type =self.target_id).serialize())
                self.clean_amount()
                logging.info("action: There are still unprocessed games, Sent CalculatorDTO type Request 🗒️ | result :success ✅")
        elif (calculatorDTO.status == STATUS_REQUEST and not self.i_am_lider):
            self.send_calculator_to_leader()
    
    def is_ready_eof(self):
        return self.ready_to_send_eof
    
    def try_send_partial_data(self):
        if (self.ready_to_send_eof and self.i_am_lider and not self.sent_first_partial):
            self.broker.public_message(exchange_name=self.exchange_name, message =DataPartialDTO().serialize())
            logging.info("action: I am the leader! 🔥, Send Partial Data Request 📦 | result: success ✅")
            self.sent_first_partial = True
        
    def send_calculator_to_leader(self):
        self.broker.public_message(exchange_name =self.exchange_name, message = CalculatorDTO(client_id =self.client_id,
                                    status =STATUS_RESPONSE, amount_data =self.data_individual, target_type =self.target_id).serialize())
        logging.info(f"action: Sent my CalculatorDTO ({self.target_name}) process : {self.data_individual}"+ 
                     f"💯 🔥  ID: {self.node_id}  | result: success ✅")

    def send_eof_next_queues(self):
        for a_name_queue in self.next_queues:
            self.broker.public_message(queue_name =a_name_queue, message = (EOFDTO.create(self.eof_dto)).serialize())
            logging.info(f"action: Send EOF of {self.target_name} To: {a_name_queue} 🥇 | result: sucess ✅ ")
        self.sent_eof = True
