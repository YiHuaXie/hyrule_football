import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import asyncio
import json
import threading
from hyrule_football.utils import get_logger
from hyrule_football.store import LarkUserStore
from hyrule_football.agents.hyrule_agent import HyruleAgent
from hyrule_football.config import settings

logger = get_logger(__name__)

lark_log_level = lark.LogLevel.DEBUG if settings.APP_ENV == "dev" else lark.LogLevel.INFO

client = (
    lark.Client.builder()
    .app_id(settings.LARK_APP_ID)
    .app_secret(settings.LARK_APP_SECRET)
    .log_level(lark_log_level)
    .build()
)


def create_streaming_card(content: str = "") -> str:
    """创建流式卡片的 JSON 模板（使用 Markdown 卡片）"""
    card = {
        "config": {
            "wide_screen_mode": True,
        },
        "elements": [
            {
                "tag": "markdown",
                "content": content or "正在思考...",
            }
        ],
    }
    return json.dumps(card, ensure_ascii=False)


async def send_streaming_reply(chat_id: str, agent_response_stream):
    """发送流式回复"""
    message_id = None
    accumulated_text = ""

    try:
        # 1. 创建初始流式卡片
        initial_card = create_streaming_card("正在思考...")

        create_request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("interactive")  # 使用 interactive 类型发送卡片
                .content(initial_card)
                .build()
            )
            .build()
        )

        # 发送初始卡片
        create_response = client.im.v1.message.create(create_request)

        if not create_response.success():
            logger.error(
                f"Failed to create streaming card: {create_response.code}: {create_response.msg}"
            )
            return

        message_id = create_response.data.message_id
        logger.info(f"Created streaming card with message_id: {message_id}")

        # 2. 流式更新卡片内容
        async for chunk in agent_response_stream:
            accumulated_text += chunk

            # 更新卡片内容
            updated_card = create_streaming_card(accumulated_text)

            patch_request = (
                PatchMessageRequest.builder()
                .message_id(message_id)
                .request_body(PatchMessageRequestBody.builder().content(updated_card).build())
                .build()
            )

            patch_response = client.im.v1.message.patch(patch_request)

            if not patch_response.success():
                logger.error(
                    f"Failed to update streaming card: {patch_response.code}: {patch_response.msg}"
                )
                break

            # 控制更新频率，避免过于频繁（避免触发飞书 API 限流）
            await asyncio.sleep(0.3)

        logger.info(f"Streaming reply completed: {accumulated_text}")

    except Exception as e:
        logger.error(f"Error in streaming reply: {e}", exc_info=True)
        # 如果出错，发送错误消息
        if message_id:
            error_card = create_streaming_card("抱歉，处理消息时出现错误。")
            patch_request = (
                PatchMessageRequest.builder()
                .message_id(message_id)
                .request_body(PatchMessageRequestBody.builder().content(error_card).build())
                .build()
            )
            client.im.v1.message.patch(patch_request)


async def process_message_async(message_text: str, user_id: str, message_id: str, chat_id: str):
    """异步处理消息并回复"""
    try:
        logger.info(f"Processing message from {user_id}: {message_text}")
        # 记录用户信息
        LarkUserStore.add_user(user_id, {"user_id": user_id, "chat_id": chat_id})

        agent = HyruleAgent()

        # 检查 agent 是否支持流式输出
        if hasattr(agent, "run_agent_stream"):
            # 使用流式回复
            response_stream = agent.run_agent_stream(message_text, user_id=user_id)
            await send_streaming_reply(chat_id, response_stream)
        else:
            # 使用普通回复
            reply_text = await agent.run_agent(message_text, user_id=user_id)
            logger.info(f"Generated reply: {reply_text}")

            # 构造消息内容
            content = json.dumps({"text": reply_text}, ensure_ascii=False)

            # 构造发送消息请求
            request = (
                CreateMessageRequest.builder()
                .receive_id_type("chat_id")
                .request_body(
                    CreateMessageRequestBody.builder()
                    .receive_id(chat_id)
                    .msg_type("text")
                    .content(content)
                    .build()
                )
                .build()
            )

            # 发送回复
            send_response = client.im.v1.message.create(request)

            if send_response.success():
                logger.info(f"Successfully sent reply to chat {chat_id}")
            else:
                logger.error(f"Failed to send reply: {send_response.code}: {send_response.msg}")

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)


def _do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    """处理接收消息事件"""

    try:
        logger.info(f"receive message, data: {lark.JSON.marshal(data, indent=4)}")

        event = data.event
        # 检查是否是机器人发送的消息，避免循环
        sender = event.sender
        if sender.sender_type == "app":
            logger.info("Ignored bot message")
            return

        # 获取消息信息
        message = event.message
        message_type = message.message_type
        chat_id = message.chat_id
        message_id = message.message_id

        # 获取用户ID - 修正获取方式
        user_id = (
            sender.sender_id.user_id
            if sender.sender_id and hasattr(sender.sender_id, "user_id")
            else (
                sender.sender_id.open_id
                if sender.sender_id and hasattr(sender.sender_id, "open_id")
                else None
            )
        )

        logger.info(f"message_type: {message_type}, chat_id: {chat_id}, message_id: {message_id}")

        # 只处理文本消息
        if message_type == "text":
            try:
                content_json = json.loads(message.content)
                message_text = content_json.get("text", "").strip()

                if message_text and (user_id or chat_id):
                    logger.info(
                        f"Received text message from {user_id} in chat {chat_id}: {message_text}"
                    )
                    # 将异步任务添加到当前事件循环
                    asyncio.create_task(
                        process_message_async(message_text, user_id or chat_id, message_id, chat_id)
                    )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message content as JSON: {e}")
            except Exception as e:
                logger.error(f"Error processing text message: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error in message event handler: {e}", exc_info=True)


def _do_p2p_chat_entered(data: P2ImChatAccessEventBotP2pChatEnteredV1) -> None:
    """处理用户进入会话事件"""
    # 可以在这里调用发送欢迎消息的逻辑
    logger.info(f"用户进入会话, data: {lark.JSON.marshal(data, indent=4)}")


def start_lark_client():
    try:
        logger.info("Starting WebSocket Client")
        # 创建事件处理器 - 使用正确的Builder模式
        event_handler = (
            lark.EventDispatcherHandler.builder(
                verification_token=settings.LARK_VERIFICATION_TOKEN,
                encrypt_key="",  # 如果有加密key，在这里填写
            )
            # https://open.feishu.cn/document/server-side-sdk/python--sdk/handle-events
            .register_p2_im_message_receive_v1(_do_p2_im_message_receive_v1)
            .register_p2_im_chat_access_event_bot_p2p_chat_entered_v1(_do_p2p_chat_entered)
            .build()
        )

        logger.info("Event handler registered successfully")

        # 创建 WebSocket 客户端并启动
        ws_client = lark.ws.Client(
            app_id=settings.LARK_APP_ID,
            app_secret=settings.LARK_APP_SECRET,
            event_handler=event_handler,
            log_level=lark_log_level,
        )

        logger.info("Starting WebSocket connection...")
        ws_client.start()
    except Exception as e:
        logger.error(f"Error in WebSocket Client: {e}", exc_info=True)
