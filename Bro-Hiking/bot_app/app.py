from flask import Flask, request, abort, send_from_directory, render_template
import requests
import json
import os
import sys


from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.models import (
    UnknownEvent
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent,
    StickerMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    AudioMessageContent,
    FileMessageContent,
    UserSource,
    RoomSource,
    GroupSource,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
    PostbackEvent,
    BeaconEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    MulticastRequest,
    BroadcastRequest,
    TextMessage,
    ApiException,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    TemplateMessage,
    FlexMessage,
    Emoji,
    QuickReply,
    QuickReplyItem,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    FlexContainer,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
    ErrorResponse
)

# Get environment variables
channel_secret = "3aad6b3d4d27a919cc910dababc8a9d6"  # Fetch environment variable LINE_CHANNEL_SECRET
channel_access_token = "EC3YLKJdMfgQSrp3Kh0PxIxq3j+HAHuxkyTveb2DeGpgDMkSUUPvD/5pIEE3780xN02397R0OX4TH7utZHPf49x4GcKphP/Z6JximfWCG2BdAKkSXpR8tNyTs9B36zedaf8EunbOA9kraVV0xS15PQdB04t89/1O/w1cDnyilFU="  # Fetch environment variable LINE_CHANNEL_ACCESS_TOKEN
liff_id = "2007153411-nGyMjr9N"  # Fetch environment variable LIFF_ID

# init app
app = Flask(__name__)
handler = WebhookHandler(channel_secret)
configuration = Configuration(
    access_token=channel_access_token
)

# standard LINE webhook
@app.route("/webhook", methods=["POST"])
def line_webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# text message handler
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    text = event.message.text     
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # check station
        if text.startswith("#"):
            req = requests.get(rest_station_api + text[1:])
            data = req.json()
            resp_text = str(data["data"])
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=resp_text)]
                )
            )
        # check asset
        elif text.startswith("*"):
            req = requests.get(rest_asset_api + text[1:])
            data = req.json()
            resp_text = str(data["data"])
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=resp_text)]
                )
            )
        # not commands
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=text)]
                )
            )

# LIFF
@app.route("/liff", methods=["GET"])
def liff():
    return render_template("liff.html", liff_id=liff_id)
