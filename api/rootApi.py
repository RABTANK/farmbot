import asyncio
from datetime import datetime
import logging
from flask import Blueprint, request
from classes.commandHandler import CommandHandler
from classes.messageHandler import GroupAtMessageHandler, create_message_handler
from classes.requestHandler import RequestHandler
from classes.messageSender import GroupMessageSender
import methons.authentication.callbackAuthentication as callbackauth
from qbot_static import Static

root_bt = Blueprint("root", __name__)
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(os.path.join(Static.WORKPATH,(f"logs/err/{datetime.now().strftime('%Y%m%d')}.logs"))),
                        logging.StreamHandler()
                    ])


def callbackHandler(handler):
    mh = create_message_handler(handler.get_body())
    if type(mh) == GroupAtMessageHandler:
        mh.print_main_data()
        if mh.is_function_command():
            command_handler = CommandHandler(mh.message_raw, mh.user_union_id)
            back=command_handler.execute_command()
            msg_sender=GroupMessageSender(mh.group_id,0)
            msg_sender.message=back
            msg_sender.pre_message_id=mh.message_id
            asyncio.run(msg_sender.send())
            
    else:
        print("unknow command")


@root_bt.route("/fishbot", methods=["GET", "POST"])
def root():
    try:
        handler = RequestHandler()
        # 回调验证请求
        if handler.get_op() == 13:
            return callbackauth.build_callback_body(handler)

        if handler.get_op() == 0:
            callbackHandler(handler)

        return "Request processed."
    except Exception as e:
        logging.error(f"Error sending message: {e}", exc_info=True)
        