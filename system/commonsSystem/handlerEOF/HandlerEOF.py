import logging
from system.commonsSystem.DTO.CalculatorDTO import CalculatorDTO, STATUS_REQUEST, STATUS_RESPONSE
from system.commonsSystem.DTO.EOFDTO import EOFDTO


class HandlerEOF:

    def __init__(self, target_name ="", broker = None, node_id =0, exchange_name = "", name_next_queue ="", total_controllers = 0):
        self.target_name = target_name
        self.target_id = None
        self.broker = broker
        self.data_individual = 0
        self.data_total_accumulated = 0
        self.data_definitive = 0
        self.controllers_recv = 0
        self.total_controllers = total_controllers
        self.node_id = node_id
        self.client_id = 0
        self.exchange_name = exchange_name
        self.name_next_queue = name_next_queue
        self.i_am_lider = False
        self.eof_dto = None

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

    def run(self, calculatorDTO, target_id):
        self.client_id = calculatorDTO.client_id
        self.target_id = target_id
        if (calculatorDTO.status == STATUS_RESPONSE and self.i_am_lider):
            self.data_total_accumulated += calculatorDTO.amount_data
            self.controllers_recv +=1
            logging .info(f"action: information Leader of EOF {self.target_name} 🔥 Amounts: Individual: {self.data_individual}"+
                         f" Total Accumulated: {self.data_total_accumulated} Definitive: {self.data_definitive} | result: success ✅ ")
            if (self.data_total_accumulated + self.data_individual) == self.data_definitive:
                self.broker.public_message(queue_name =self.name_next_queue, message = (EOFDTO.create(self.eof_dto)).serialize())
                logging.info(f"action: Send EOF of {self.target_name} To {self.name_next_queue} 🥇 | result: sucess ✅ ")
            elif self.controllers_recv == (self.total_controllers -1):
                self.broker.public_message(exchange_name =self.exchange_name,
                                        message =CalculatorDTO(client_id =self.client_id, target_type =self.target_id).serialize())
                self.clean_amount()
                logging.info("action: There are still unprocessed games, Sent CalculatorDTO type Request 🗒️ | result :success ✅")
        elif (calculatorDTO.status == STATUS_REQUEST and not self.i_am_lider):
            self.broker.public_message(exchange_name =self.exchange_name, message = CalculatorDTO(client_id =self.client_id,
                                        status =STATUS_RESPONSE, amount_data =self.data_individual, target_type =self.target_id).serialize())
            logging.info(f"action: Sent my CalculatorDTO ({self.target_name}) process : {self.data_individual}"+ 
                         f"💯 🔥  ID: {self.node_id}  | result: success ✅")


