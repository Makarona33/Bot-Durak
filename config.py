from vkbottle import API, BuiltinStateDispenser

from tools.request_rescheduler import RequestRescheduler

TOKEN = ""
DATABASE_NAME = ""
DATABASE_PASSWORD = ""
DATABASE_HOST = ""

api = API(TOKEN, request_rescheduler=RequestRescheduler())
state_dispenser = BuiltinStateDispenser()
