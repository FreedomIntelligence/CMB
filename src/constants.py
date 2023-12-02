import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ))

# from workers.huatuo import HuatuoWorker
from workers.huatuo_chat import HuatuoChatWorker
from workers.baichuanchat import BaichuanChatWorker
from workers.bentsao import BentsaoWorker
from workers.doctorglm import DoctorGLMWorker
from workers.bianque_v2 import BianQueV2Worker
from workers.chatglm_med import ChatGLMMedWorker
from workers.chatmed_consult import ChatMedConsultWorker
from workers.medicalgpt import MedicalGPTWorker
from workers.chatglm3_6b import ChatGLM3Worker
from workers.mymodel import MyModelWorker

id2worker_class = {
    # 'huatuo': HuatuoWorker,
    'baichuan-13b-chat': BaichuanChatWorker,
    'huatuo-chat': HuatuoChatWorker,
    'bentsao': BentsaoWorker,
    'doctorglm': DoctorGLMWorker,
    'bianque-v2': BianQueV2Worker,
    'chatglm-med': ChatGLMMedWorker,
    'chatmed-consult': ChatMedConsultWorker,
    'medicalgpt': MedicalGPTWorker,
    'chatglm3_6b': ChatGLM3Worker,
    'my_model': MyModelWorker, # modify here
} 
