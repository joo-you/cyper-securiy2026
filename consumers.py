import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken


class ChatConsumer(AsyncWebsocketConsumer):

    # =========================
    # CONNECT
    # =========================
    async def connect(self):
        try:
            # 🔹 قراءة التوكن
            query_string = self.scope["query_string"].decode()
            params = parse_qs(query_string)
            token = params.get("token")

            if not token:
                await self.close()
                return

            # 🔹 فك JWT
            access_token = AccessToken(token[0])
            user_id = access_token["user_id"]

            # 🔹 جلب المستخدم
            from django.contrib.auth import get_user_model
            User = get_user_model()

            self.user = await User.objects.aget(id=user_id)

            # 🔹 قبول الاتصال
            await self.accept()

            print(f"✅ CONNECTED: {self.user.email}")

        except Exception as e:
            print("❌ CONNECT ERROR:", e)
            await self.close()

    # =========================
    # DISCONNECT
    # =========================
    async def disconnect(self, close_code):
        try:
            print(f"🔌 DISCONNECTED: {getattr(self, 'user', 'unknown')}")
        except Exception as e:
            print("❌ DISCONNECT ERROR:", e)

    # =========================
    # RECEIVE MESSAGE
    # =========================
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            raw_message = data.get("message")
            receiver_id = data.get("receiver")

            # 🔹 validation
            if not raw_message or not receiver_id:
                return

            if int(receiver_id) == self.user.id:
                return

            # =========================
            # 🧠 ROOM (صح للطرفين)
            # =========================
            room_name = f"chat_{min(self.user.id, int(receiver_id))}_{max(self.user.id, int(receiver_id))}"

            # =========================
            # 🔐 ENCRYPT
            # =========================
            from .encryption import encrypt_message
            encrypted_message = encrypt_message(raw_message)

            # =========================
            # 💾 SAVE DB
            # =========================
            from .models import Message
            from django.contrib.auth import get_user_model

            User = get_user_model()
            receiver = await User.objects.aget(id=receiver_id)

            await Message.objects.acreate(
                sender=self.user,
                receiver=receiver,
                message=encrypted_message
            )

            # =========================
            # 👥 JOIN ROOM (مهم جدًا)
            # =========================
            await self.channel_layer.group_add(
                room_name,
                self.channel_name
            )

            # =========================
            # 📡 SEND
            # =========================
            await self.channel_layer.group_send(
                room_name,
                {
                    "type": "chat_message",
                    "message": raw_message,   # اللي هيروح للفرونت
                    "sender": self.user.email,
                    "sender_id": self.user.id
                }
            )

            print(f"📨 {self.user.id} → {receiver_id}")

        except Exception as e:
            print("❌ RECEIVE ERROR:", e)

    # =========================
    # SEND TO CLIENT
    # =========================
    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                "message": event["message"],
                "sender": event["sender"],
                "sender_id": event["sender_id"]
            }))
        except Exception as e:
            print("❌ CHAT MESSAGE ERROR:", e)