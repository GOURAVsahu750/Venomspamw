import asyncio
import json
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError, RetryAfter, BadRequest
import aiohttp
import random
import string

# Configuration
TOKEN = "8528820614:AAFwUeP0SAABfDq1yxCZL3jxCccr9KJB530"
OWNER_ID = 7957743011
DEEPSEEK_API = "https://deepseek-op.hosters.club/api/?q={}"



# Storage
user_data = {}
notes = {}
favorites = {}
aliases = {}
reminders = {}
auto_react = {}
logger_chats = set()
raid_tasks = {}
blocked_users = set()
broadcast_list = set()

class TelegramBot:
    def __init__(self):
      
        self.watermark = "🔐 @TITANXCONTACT | Do not redistribute or remove watermark"
        
        self.app = Application.builder().token(TOKEN).build()
        self.setup_handlers()
        
        self.app.add_error_handler(self.error_handler)
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors gracefully"""
        try:
            if isinstance(context.error, RetryAfter):
                await asyncio.sleep(context.error.retry_after)
            
            print(f"Error: {context.error} | Bot: @TITANXCONTACT")
        except Exception as e:
            print(f"Error handler failed: {e} | Bot: @TITANXCONTACT")
    
    def setup_handlers(self):
       
        # Utility 
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("ping", self.ping))
        self.app.add_handler(CommandHandler("info", self.info))
        self.app.add_handler(CommandHandler("sysinfo", self.sysinfo))
        
        # Owner section
        self.app.add_handler(CommandHandler("owner", self.owner_help))
        self.app.add_handler(CommandHandler("broadcast", self.broadcast))
        self.app.add_handler(CommandHandler("stats", self.bot_stats))
        self.app.add_handler(CommandHandler("block", self.block_user))
        self.app.add_handler(CommandHandler("unblock", self.unblock_user))
        self.app.add_handler(CommandHandler("blocklist", self.show_blocklist))
        self.app.add_handler(CommandHandler("chatlist", self.list_chats))
        self.app.add_handler(CommandHandler("shell", self.shell_command))
        self.app.add_handler(CommandHandler("restart", self.restart_bot))
        self.app.add_handler(CommandHandler("logs", self.send_logs))
        
        # URL & QR Commands
        self.app.add_handler(CommandHandler("shorten", self.shorten_url))
        self.app.add_handler(CommandHandler("unshort", self.unshort_url))
        self.app.add_handler(CommandHandler("qr", self.generate_qr))
        
        # Text Styling
        self.app.add_handler(CommandHandler("style", self.style_text))
        self.app.add_handler(CommandHandler("type", self.type_effect))
        self.app.add_handler(CommandHandler("effect", self.text_effect))
        self.app.add_handler(CommandHandler("ascii", self.ascii_art))
        
        # Chat
        self.app.add_handler(CommandHandler("gcnc", self.group_name_change))
        self.app.add_handler(CommandHandler("purge", self.purge_messages))
        self.app.add_handler(CommandHandler("spam", self.spam_messages))
        self.app.add_handler(CommandHandler("flood", self.flood_messages))
        self.app.add_handler(CommandHandler("raid", self.start_raid))
        self.app.add_handler(CommandHandler("stopraid", self.stop_raid))
        self.app.add_handler(CommandHandler("tagall", self.tag_all))
        self.app.add_handler(CommandHandler("tagadmins", self.tag_admins))
        self.app.add_handler(CommandHandler("randping", self.random_ping))
        self.app.add_handler(CommandHandler("join", self.join_group))
        self.app.add_handler(CommandHandler("leave", self.leave_group))
        
        # Admin section
        self.app.add_handler(CommandHandler("ban", self.ban_user))
        self.app.add_handler(CommandHandler("kick", self.kick_user))
        self.app.add_handler(CommandHandler("mute", self.mute_user))
        self.app.add_handler(CommandHandler("unmute", self.unmute_user))
        self.app.add_handler(CommandHandler("promote", self.promote_user))
        self.app.add_handler(CommandHandler("demote", self.demote_user))
        
        # Organization
        self.app.add_handler(CommandHandler("note", self.note_handler))
        self.app.add_handler(CommandHandler("remind", self.set_reminder))
        self.app.add_handler(CommandHandler("fav", self.favorite_handler))
        self.app.add_handler(CommandHandler("alias", self.alias_handler))
        
        # Automation
        self.app.add_handler(CommandHandler("autoreact", self.auto_react_toggle))
        self.app.add_handler(CommandHandler("logger", self.logger_toggle))
        
        # AI Response 
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       
        watermark_notice = "\n\n───────\n🤖 Bot by @TITANXCONTACT"
        await update.message.reply_text(
            "🤖 *Advanced Telegram Bot*\n\n"
            "I'm your all-in-one bot with tons of features!\n"
            "Use /help to see all available commands." + watermark_notice,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """🔧 UTILITIES
/ping - Check bot latency
/info - Chat information
/sysinfo - System statistics
/shorten <url> - Shorten URL
/unshort <url> - Expand shortened URL
/qr <text> - Generate QR code

💬 CHAT TOOLS
/spam <n> <text> <speed> - Spam messages
/gcnc <n> <name> <speed> - Group name change
/flood <n> <text> <speed> - Flood messages
/raid <n> <text> - Start raid mode
/stopraid - Stop active raid
/tagall - Tag all members
/tagadmins - Tag all admins

👮 ADMIN COMMANDS
/ban <user> - Ban a user
/kick <user> - Kick a user
/mute <user> - Mute a user
/unmute <user> - Unmute a user

📝 ORGANIZATION
/note add <name> <content> - Add note
/note get <name> - Get note
/note list - List all notes
/fav add <text> - Add favorite
/fav list - List favorites

⚙️ AUTOMATION
/autoreact on/off - Auto-react
/logger on/off - Log messages"""
        
        
        watermark = "\n\n───────\n© Bot Framework by @TITANXCONTACT\nDo not remove this notice"
        await update.message.reply_text(help_text + watermark)
    
    async def ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        start = time.time()
        msg = await update.message.reply_text("🏓 Pinging...")
        end = time.time()
        latency = round((end - start) * 1000, 2)
       
        await msg.edit_text(f"🏓 Pong!\n⏱ Latency: {latency}ms\n\n🔧 @TITANXCONTACT")
    
    def is_owner(self, user_id: int) -> bool:
        # 💧 Watermark check
        if user_id == OWNER_ID:
            return True
        return False
    
    async def owner_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show owner-only commands"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ This command is only for the bot owner!")
            return
        
        owner_text = """👑 OWNER COMMANDS

📢 Broadcast & Management:
/broadcast <message> - Send message to all chats
/stats - Detailed bot statistics
/chatlist - List all chats bot is in

🚫 User Control:
/block <user_id> - Block user from using bot
/unblock <user_id> - Unblock user
/blocklist - Show blocked users

🔧 System:
/shell <command> - Execute shell command
/restart - Restart the bot
/logs - Get recent logs

💡 Tip: Reply to a user and use /block to block them quickly!"""
        
      
        watermark = "\n\n───────\nBot Framework © @TITANXCONTACT\nUnauthorized redistribution prohibited"
        await update.message.reply_text(owner_text + watermark)
    
    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all chats"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /broadcast <message>")
            return
        
        
        message = ' '.join(context.args)
        watermark = "\n\n───────\n🔧 Powered by @TITANXCONTACT"
        broadcast_message = f"📢 Broadcast:\n\n{message}{watermark}"
        
        sent = 0
        failed = 0
        
        status_msg = await update.message.reply_text("📢 Broadcasting...")
        
        for chat_id in list(broadcast_list):
            try:
                await context.bot.send_message(chat_id, broadcast_message)
                sent += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                failed += 1
                print(f"Broadcast failed for {chat_id}: {e} | Bot: @TITANXCONTACT")
        
        await status_msg.edit_text(f"✅ Broadcast complete!\n✉️ Sent: {sent}\n❌ Failed: {failed}\n\n🔧 @TITANXCONTACT")
    
    async def bot_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot Statistics"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        uptime = time.time() - context.bot_data.get('start_time', time.time())
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        stats = f"""📊 BOT STATISTICS

⏰ Uptime: {hours}h {minutes}m
👥 Total Users: {len(user_data)}
💬 Active Chats: {len(broadcast_list)}
📝 Total Notes: {len(notes)}
⭐ Total Favorites: {sum(len(v) for v in favorites.values())}
🔄 Active Raids: {len(raid_tasks)}
📋 Auto-react Chats: {len(auto_react)}
📊 Logger Chats: {len(logger_chats)}
🚫 Blocked Users: {len(blocked_users)}

───────
🔧 Bot Framework: @TITANXCONTACT
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
🔒 Watermark: Embedded"""
        
        await update.message.reply_text(stats)
    
    async def block_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Block user from using the bot"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        user_id = None
        
        if update.message.reply_to_message:
            user_id = update.message.reply_to_message.from_user.id
        elif context.args:
            try:
                user_id = int(context.args[0])
            except:
                await update.message.reply_text("❌ Invalid user ID")
                return
        else:
            await update.message.reply_text("❌ Reply to a user or provide user ID")
            return
        
        if user_id == OWNER_ID:
            await update.message.reply_text("❌ Cannot block the owner!")
            return
        
        blocked_users.add(user_id)
        await update.message.reply_text(f"✅ User {user_id} has been blocked!\n\n🔧 @TITANXCONTACT")
    
    async def unblock_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unblock user"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /unblock <user_id>")
            return
        
        try:
            user_id = int(context.args[0])
            if user_id in blocked_users:
                blocked_users.remove(user_id)
                await update.message.reply_text(f"✅ User {user_id} has been unblocked!\n\n🔧 @TITANXCONTACT")
            else:
                await update.message.reply_text("❌ User is not blocked")
        except:
            await update.message.reply_text("❌ Invalid user ID")
    
    async def show_blocklist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all blocked users"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        if blocked_users:
            blocklist = '\n'.join([f"• {uid}" for uid in blocked_users])
            await update.message.reply_text(f"🚫 Blocked Users:\n{blocklist}\n\n───────\n🔧 @TITANXCONTACT")
        else:
            await update.message.reply_text("✅ No blocked users\n\n🔧 @TITANXCONTACT")
    
    async def list_chats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all chats the bot is in"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        if broadcast_list:
            chat_info = []
            for chat_id in list(broadcast_list)[:20]:  # Limit to 20
                try:
                    chat = await context.bot.get_chat(chat_id)
                    chat_info.append(f"• {chat.title or chat.first_name} ({chat_id})")
                except:
                    chat_info.append(f"• Unknown ({chat_id})")
            
            text = f"💬 Bot Chats ({len(broadcast_list)} total):\n" + '\n'.join(chat_info)
            if len(broadcast_list) > 20:
                text += f"\n\n... and {len(broadcast_list) - 20} more"
            
            
            watermark = "\n\n───────\n🔍 Bot Framework by @TITANXCONTACT\n© All rights reserved"
            await update.message.reply_text(text + watermark)
        else:
            await update.message.reply_text("📭 No active chats\n\n🔧 @TITANXCONTACT")
    
    async def shell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute shell command (DANGEROUS - Owner only)"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /shell <command>")
            return
        
        command = ' '.join(context.args)
        
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout or result.stderr or "Command executed with no output"
            
            if len(output) > 4000:
                output = output[:4000] + "\n... (truncated)"
            
            t
            watermark = "\n\n───────\n🔧 Shell executed by @TITANXCONTACT bot"
            await update.message.reply_text(f"```\n{output}\n```{watermark}", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def restart_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Restart the bot"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        await update.message.reply_text("🔄 Restarting bot...\n\n🔧 @TITANXCONTACT")
        import os
        import sys
        os.execv(sys.executable, ['python'] + sys.argv)
    
    async def send_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send recent logs"""
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text("❌ Owner only!")
            return
        
        logs = f"""📋 Recent Activity:

👥 Active Users: {len(user_data)}
💬 Chats: {len(broadcast_list)}
📝 Notes: {len(notes)}
🔄 Raids: {len(raid_tasks)}
🚫 Blocked: {len(blocked_users)}

⏰ Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
───────
🔧 Bot Framework: @TITANXCONTACT
🔒 Watermark: Active
📊 Log System: Protected"""
        
        await update.message.reply_text(logs)
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        user = update.effective_user
        
        info_text = f"""📊 Chat Information

Chat ID: {chat.id}
Chat Type: {chat.type}
Chat Title: {chat.title if chat.title else 'N/A'}

Your ID: {user.id}
Username: {user.username if user.username else 'N/A'}
Name: {user.full_name}

───────
🤖 Bot by @TITANXCONTACT
🔧 Advanced Telegram Bot Framework
© Do not redistribute"""
        
        await update.message.reply_text(info_text)
    
    async def sysinfo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = time.time() - context.bot_data.get('start_time', time.time())
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        info = f"""🖥 System Information

⏰ Uptime: {hours}h {minutes}m
📝 Total Notes: {len(notes)}
⭐ Total Favorites: {sum(len(v) for v in favorites.values())}
🔄 Active Raids: {len(raid_tasks)}
📋 Auto-react Chats: {len(auto_react)}
📊 Logger Chats: {len(logger_chats)}

───────
🔧 Bot Framework: @TITANXCONTACT
🔒 Watermark: Embedded
📅 Active since: {datetime.fromtimestamp(context.bot_data.get('start_time', time.time())).strftime('%Y-%m-%d')}"""
        
        await update.message.reply_text(info)
    
    async def shorten_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /shorten <url>\n\n🔧 @TITANXCONTACT")
            return
        
        url = context.args[0]
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"https://tinyurl.com/api-create.php?url={url}", timeout=10) as resp:
                    short_url = await resp.text()
                    await update.message.reply_text(f"✅ Shortened URL:\n{short_url}\n\n🔧 @TITANXCONTACT")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def unshort_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /unshort <url>\n\n🔧 @TITANXCONTACT")
            return
        
        url = context.args[0]
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        async with aiohttp.ClientSession() as session:
            try:
                max_redirects = 10
                current_url = url
                redirect_chain = [url]
                
                for i in range(max_redirects):
                    try:
                        async with session.get(
                            current_url, 
                            allow_redirects=False, 
                            timeout=10,
                            headers={'User-Agent': 'Mozilla/5.0'}
                        ) as resp:
                            
                            if resp.status in (301, 302, 303, 307, 308):
                                location = resp.headers.get('Location')
                                if location:
                                    if location.startswith('/'):
                                        from urllib.parse import urlparse
                                        parsed = urlparse(current_url)
                                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                                    elif not location.startswith('http'):
                                        location = f"https://{location}"
                                    
                                    redirect_chain.append(location)
                                    current_url = location
                                else:
                                    break
                            else:
                                if resp.status == 200:
                                    final_url = str(resp.url)
                                    if final_url not in redirect_chain:
                                        redirect_chain.append(final_url)
                                break
                    except Exception as e:
                        print(f"Redirect error: {e} | Bot: @TITANXCONTACT")
                        break
                
                if len(redirect_chain) > 1:
                    result = "🔗 URL Redirect Chain:\n\n"
                    for idx, link in enumerate(redirect_chain, 1):
                        if idx == len(redirect_chain):
                            result += f"✅ Final: {link}"
                        else:
                            result += f"{idx}. {link}\n↓\n"
                    
                    watermark = "\n\n───────\n🔧 URL Tool by @TITANXCONTACT"
                    await update.message.reply_text(result + watermark)
                else:
                    await update.message.reply_text(f"🔗 No redirects found\nOriginal URL: {url}\n\n🔧 @TITANXCONTACT")
                    
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def generate_qr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /qr <text>\n\n🔧 @TITANXCONTACT")
            return
        
        text = ' '.join(context.args)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={text}"
        await update.message.reply_photo(qr_url, caption="📱 QR Code Generated\n\n🔧 @TITANXCONTACT")
    
    async def style_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /style <bold|italic|code> <text>\n\n🔧 @TITANXCONTACT")
            return
        
        style = context.args[0].lower()
        text = ' '.join(context.args[1:])
        
        if style == 'bold':
            styled = f'*{text}*'
        elif style == 'italic':
            styled = f'_{text}_'
        elif style == 'code':
            styled = f'`{text}`'
        else:
            styled = text
        
        watermark = "\n\n───────\n🔧 Text Tool by @TITANXCONTACT"
        await update.message.reply_text(styled + watermark, parse_mode='Markdown')
    
    async def type_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /type <text>\n\n🔧 @TITANXCONTACT")
            return
        
        text = ' '.join(context.args)
        try:
            msg = await update.message.reply_text(".")
            
            for i in range(1, len(text) + 1):
                await asyncio.sleep(0.15)
                try:
                    await msg.edit_text(text[:i])
                except BadRequest:
                    pass
        except Exception as e:
            print(f"Type effect error: {e} | Bot: @TITANXCONTACT")
    
    async def text_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /effect <reverse|scramble> <text>\n\n🔧 @TITANXCONTACT")
            return
        
        effect = context.args[0].lower()
        text = ' '.join(context.args[1:])
        
        if effect == 'reverse':
            result = text[::-1]
        elif effect == 'scramble':
            result = ''.join(random.sample(text, len(text)))
        else:
            result = text
        
        watermark = "\n\n───────\n🔧 Effect Tool by @TITANXCONTACT"
        await update.message.reply_text(result + watermark)
    
    async def ascii_art(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /ascii <text>\n\n🔧 @TITANXCONTACT")
            return
        
        text = ' '.join(context.args)
        ascii_text = f"```\n{text}\n```"
        watermark = "\n\n───────\n🔧 ASCII Tool by @TITANXCONTACT"
        await update.message.reply_text(ascii_text + watermark, parse_mode='Markdown')
    
    async def group_name_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 3:
            await update.message.reply_text("❌ Usage: /gcnc <n> <name> <speed>\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            n = int(context.args[0])
            name = context.args[1]
            speed = float(context.args[2])
            
            for i in range(min(n, 800)):  # Limit to 800
                await context.bot.set_chat_title(update.effective_chat.id, f"{name} {i+1}")
                await asyncio.sleep(speed)
            
            await update.message.reply_text("✅ Group name change completed!\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def purge_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /purge <number>\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            count = min(int(context.args[0]), 800)  # Limit to 800
            deleted = 0
            message_id = update.message.message_id
            
            for i in range(1, count + 1):
                try:
                    await context.bot.delete_message(update.effective_chat.id, message_id - i)
                    deleted += 1
                    await asyncio.sleep(0.05)  # Rate limiting
                except:
                    pass
            
            msg = await context.bot.send_message(update.effective_chat.id, f"🗑 Deleted {deleted} messages\n\n🔧 @TITANXCONTACT")
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            print(f"Purge error: {e} | Bot: @TITANXCONTACT")
    
    async def spam_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 3:
            await update.message.reply_text("❌ Usage: /spam <n> <text> <speed>\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            n = int(context.args[0])
            text = ' '.join(context.args[1:-1])
            speed = float(context.args[-1])
            
            speed = max(0.08, min(speed, 10.0))
            
            for i in range(min(n, 8000)):
                try:
                   
                    spam_text = f"{text}\n───────\n🔧 @TITANXCONTACT" if i % 5 == 0 else text
                    await update.message.reply_text(spam_text)
                    await asyncio.sleep(speed)
                except RetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                except:
                    break
        except Exception as e:
            print(f"Spam error: {e} | Bot: @TITANXCONTACT")
    
    async def flood_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 3:
            await update.message.reply_text("❌ Usage: /flood <n> <text> <speed>\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            n = int(context.args[0])
            text = ' '.join(context.args[1:-1])
            speed = float(context.args[-1])
            
            speed = max(0.08, min(speed, 10.0))

            for i in range(min(n, 800)):
                try:
                   
                    flood_text = f"{text} #{i+1}\n───────\n🔧 @TITANXCONTACT" if i % 10 == 0 else f"{text} #{i+1}"
                    await context.bot.send_message(update.effective_chat.id, flood_text)
                    await asyncio.sleep(speed)
                except RetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                except:
                    break
        except Exception as e:
            print(f"Flood error: {e} | Bot: @TITANXCONTACT")
    
    async def start_raid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /raid <n> <text>\n\n🔧 @TITANXCONTACT")
            return
        
        chat_id = update.effective_chat.id
        n = int(context.args[0])
        text = ' '.join(context.args[1:])
        
        async def raid_loop():
            for i in range(min(n, 50)):
                if chat_id not in raid_tasks:
                    break
                try:
                    raid_text = f"{text} [Raid {i+1}/{n}]\n───────\n🔧 @TITANXCONTACT" if i % 5 == 0 else f"{text} [Raid {i+1}/{n}]"
                    await context.bot.send_message(chat_id, raid_text)
                    await asyncio.sleep(2)
                except:
                    break
            if chat_id in raid_tasks:
                del raid_tasks[chat_id]
        
        raid_tasks[chat_id] = asyncio.create_task(raid_loop())
        await update.message.reply_text(f"⚔️ Raid started! {min(n, 50)} messages incoming...\n\n🔧 @TITANXCONTACT")
    
    async def stop_raid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if chat_id in raid_tasks:
            raid_tasks[chat_id].cancel()
            del raid_tasks[chat_id]
            await update.message.reply_text("🛑 Raid stopped!\n\n🔧 @TITANXCONTACT")
        else:
            await update.message.reply_text("❌ No active raid\n\n🔧 @TITANXCONTACT")
    
    async def tag_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = update.effective_chat.id
            
            try:
                member_count = await context.bot.get_chat_member_count(chat_id)
            except:
                member_count = 0
            
            members = []
            
            try:
                admins = await context.bot.get_chat_administrators(chat_id)
                for admin in admins:
                    if not admin.user.is_bot:
                        if admin.user.username:
                            members.append(f"@{admin.user.username}")
                        else:
                            members.append(f"[{admin.user.first_name}](tg://user?id={admin.user.id})")
            except Exception as e:
                print(f"Error getting admins: {e} | Bot: @TITANXCONTACT")
            
            if members:
                chunk_size = 5
                for i in range(0, len(members), chunk_size):
                    chunk = members[i:i + chunk_size]
                    text = "👥 Tagging members:\n" + " ".join(chunk)
                    try:
                        await update.message.reply_text(text, parse_mode='Markdown')
                        await asyncio.sleep(1)
                    except:
                        text = "👥 Tagging members:\n" + " ".join([m.split(']')[0].replace('[', '') if '[' in m else m for m in chunk])
                        await update.message.reply_text(text)
                        await asyncio.sleep(1)
                
                watermark = f"\n\n✅ Tagged {len(members)} members (Total in chat: {member_count})\n───────\n🔧 Tag Tool by @TITANXCONTACT"
                await update.message.reply_text(watermark)
            else:
                await update.message.reply_text("❌ No members to tag. Note: Bot can only tag admins in large groups.\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def tag_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = update.effective_chat.id
            admins_list = await context.bot.get_chat_administrators(chat_id)
            
            admin_tags = []
            for admin in admins_list:
                if not admin.user.is_bot:
                    if admin.user.username:
                        admin_tags.append(f"@{admin.user.username}")
                    else:
                        admin_tags.append(f"[{admin.user.first_name}](tg://user?id={admin.user.id})")
            
            if admin_tags:
                chunk_size = 5
                for i in range(0, len(admin_tags), chunk_size):
                    chunk = admin_tags[i:i + chunk_size]
                    text = "👮 Tagging admins:\n" + " ".join(chunk)
                    try:
                        await update.message.reply_text(text, parse_mode='Markdown')
                        await asyncio.sleep(0.5)
                    except:
                        text = "👮 Tagging admins:\n" + " ".join([a.split(']')[0].replace('[', '') if '[' in a else a for a in chunk])
                        await update.message.reply_text(text)
                        await asyncio.sleep(0.5)
                
                watermark = f"\n\n✅ Tagged {len(admin_tags)} admins\n───────\n🔧 Admin Tool by @TITANXCONTACT"
                await update.message.reply_text(watermark)
            else:
                await update.message.reply_text("❌ No admins to tag\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def random_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /randping <n>\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            n = int(context.args[0])
            admins = await context.bot.get_chat_administrators(update.effective_chat.id)
            
            members = []
            for admin in admins:
                if admin.user.username:
                    members.append(f"@{admin.user.username}")
            
            if members:
                selected = random.sample(members, min(n, len(members)))
                text = f"🎲 Random ping ({n}):\n" + " ".join(selected)
                watermark = "\n\n───────\n🔧 Ping Tool by @TITANXCONTACT"
                await update.message.reply_text(text + watermark)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def join_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔗 Add me to a group using my username!\n\n🔧 @TITANXCONTACT")
    
    async def leave_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await context.bot.leave_chat(update.effective_chat.id)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a user to ban\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            user_id = update.message.reply_to_message.from_user.id
            await context.bot.ban_chat_member(update.effective_chat.id, user_id)
            await update.message.reply_text("🔨 User banned!\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def kick_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a user to kick\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            user_id = update.message.reply_to_message.from_user.id
            await context.bot.unban_chat_member(update.effective_chat.id, user_id)
            await update.message.reply_text("👢 User kicked!\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def mute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a user to mute\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            user_id = update.message.reply_to_message.from_user.id
            from telegram import ChatPermissions
            await context.bot.restrict_chat_member(
                update.effective_chat.id, 
                user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await update.message.reply_text("🔇 User muted!\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def unmute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a user to unmute\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            user_id = update.message.reply_to_message.from_user.id
            from telegram import ChatPermissions
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                user_id,
                permissions=ChatPermissions(can_send_messages=True)
            )
            await update.message.reply_text("🔊 User unmuted!\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def promote_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a user to promote\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            user_id = update.message.reply_to_message.from_user.id
            await context.bot.promote_chat_member(
                update.effective_chat.id,
                user_id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True
            )
            await update.message.reply_text("⬆️ User promoted to admin!\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def demote_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a user to demote\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            user_id = update.message.reply_to_message.from_user.id
            await context.bot.promote_chat_member(
                update.effective_chat.id,
                user_id,
                can_change_info=False,
                can_delete_messages=False,
                can_invite_users=False,
                can_restrict_members=False,
                can_pin_messages=False
            )
            await update.message.reply_text("⬇️ User demoted!\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def note_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /note <add|get|list> [name] [content]\n\n🔧 @TITANXCONTACT")
            return
        
        action = context.args[0].lower()
        user_id = update.effective_user.id
        
        if user_id not in notes:
            notes[user_id] = {}
        
        if action == 'add' and len(context.args) >= 3:
            name = context.args[1]
            content = ' '.join(context.args[2:])
            notes[user_id][name] = content
            await update.message.reply_text(f"✅ Note '{name}' saved!\n\n🔧 @TITANXCONTACT")
        
        elif action == 'get' and len(context.args) >= 2:
            name = context.args[1]
            content = notes[user_id].get(name, "Note not found")
            await update.message.reply_text(f"📝 {name}:\n{content}\n\n🔧 @TITANXCONTACT")
        
        elif action == 'list':
            if notes[user_id]:
                note_list = '\n'.join([f"• {name}" for name in notes[user_id].keys()])
                watermark = f"\n\n📋 Your notes:\n{note_list}\n───────\n🔧 Note System by @TITANXCONTACT"
                await update.message.reply_text(watermark)
            else:
                await update.message.reply_text("📋 No notes saved\n\n🔧 @TITANXCONTACT")
    
    async def set_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /remind <minutes> <text>\n\n🔧 @TITANXCONTACT")
            return
        
        try:
            minutes = int(context.args[0])
            text = ' '.join(context.args[1:])
            
            await update.message.reply_text(f"⏰ Reminder set for {minutes} minutes!\n\n🔧 @TITANXCONTACT")
            
            await asyncio.sleep(minutes * 60)
            await update.message.reply_text(f"🔔 Reminder:\n{text}\n\n🔧 @TITANXCONTACT")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}\n\n🔧 @TITANXCONTACT")
    
    async def favorite_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /fav <add|list> [text]\n\n🔧 @TITANXCONTACT")
            return
        
        action = context.args[0].lower()
        user_id = update.effective_user.id
        
        if user_id not in favorites:
            favorites[user_id] = []
        
        if action == 'add' and len(context.args) >= 2:
            text = ' '.join(context.args[1:])
            favorites[user_id].append(text)
            await update.message.reply_text(f"⭐ Added to favorites!\n\n🔧 @TITANXCONTACT")
        
        elif action == 'list':
            if favorites[user_id]:
                fav_list = '\n'.join([f"{i+1}. {fav}" for i, fav in enumerate(favorites[user_id])])
                watermark = f"\n\n⭐ Your favorites:\n{fav_list}\n───────\n🔧 Favorite System by @TITANXCONTACT"
                await update.message.reply_text(watermark)
            else:
                await update.message.reply_text("⭐ No favorites yet\n\n🔧 @TITANXCONTACT")
    
    async def alias_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("❌ Usage: /alias <add|list> [name] [command]\n\n🔧 @TITANXCONTACT")
            return
        
        action = context.args[0].lower()
        user_id = update.effective_user.id
        
        if user_id not in aliases:
            aliases[user_id] = {}
        
        if action == 'add' and len(context.args) >= 3:
            name = context.args[1]
            command = ' '.join(context.args[2:])
            aliases[user_id][name] = command
            await update.message.reply_text(f"✅ Alias '{name}' created!\n\n🔧 @TITANXCONTACT")
        
        elif action == 'list':
            if aliases[user_id]:
                alias_list = '\n'.join([f"• {name} → {cmd}" for name, cmd in aliases[user_id].items()])
                watermark = f"\n\n🔗 Your aliases:\n{alias_list}\n───────\n🔧 Alias System by @TITANXCONTACT"
                await update.message.reply_text(watermark)
            else:
                await update.message.reply_text("🔗 No aliases yet\n\n🔧 @TITANXCONTACT")
    
    async def auto_react_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args or context.args[0].lower() not in ['on', 'off']:
            await update.message.reply_text("❌ Usage: /autoreact <on|off>\n\n🔧 @TITANXCONTACT")
            return
        
        chat_id = update.effective_chat.id
        status = context.args[0].lower() == 'on'
        
        auto_react[chat_id] = status
        await update.message.reply_text(f"✅ Auto-react {'enabled' if status else 'disabled'}!\n\n🔧 @TITANXCONTACT")
    
    async def logger_toggle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args or context.args[0].lower() not in ['on', 'off']:
            await update.message.reply_text("❌ Usage: /logger <on|off>\n\n🔧 @TITANXCONTACT")
            return
        
        chat_id = update.effective_chat.id
        status = context.args[0].lower() == 'on'
        
        if status:
            logger_chats.add(chat_id)
            await update.message.reply_text("✅ Logger enabled!\n\n🔧 @TITANXCONTAC")
        else:
            logger_chats.discard(chat_id)
            await update.message.reply_text("✅ Logger disabled!\n\n🔧 @TITANXCONTACT")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all non-command messages"""
        
        if not update.message or not update.message.text:
            return
        
        user_id = update.effective_user.id
        if user_id in blocked_users:
            return
        
        chat_id = update.effective_chat.id
        broadcast_list.add(chat_id)
        
        if user_id not in user_data:
            user_data[user_id] = {
                'username': update.effective_user.username,
                'first_seen': datetime.now(),
                'message_count': 0
            }
        user_data[user_id]['message_count'] += 1
        
        
        if auto_react.get(chat_id, False):
            reactions = ['👍', '❤️', '🔥', '👏', '😂', '🎉', '💯', '⚡', '🎯', '✨']
            try:
                from telegram import ReactionTypeEmoji
                reaction = ReactionTypeEmoji(emoji=random.choice(reactions))
                await context.bot.set_message_reaction(
                    chat_id=chat_id,
                    message_id=update.message.message_id,
                    reaction=[reaction],
                    is_big=False
                )
            except Exception as e:
                print(f"Auto-react error: {e} | Bot: @TITANXCONTACT")
                pass
        
        if chat_id in logger_chats:
            username = update.effective_user.username or update.effective_user.first_name
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] {username}: {update.message.text} | Bot: @TITANXCONTACT"
            print(log_msg)
        
        if update.message.text and not update.message.text.startswith('/'):
            bot_username = context.bot.username
            bot_mentioned = False
            
            if f"@{bot_username}" in update.message.text.lower():
                bot_mentioned = True
            
            if update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot:
                if update.message.reply_to_message.from_user.id == context.bot.id:
                    bot_mentioned = True
            
            if update.message.chat.type == 'private':
                bot_mentioned = True
            
            if update.message.entities:
                for entity in update.message.entities:
                    if entity.type == 'mention':
                        mention_text = update.message.text[entity.offset:entity.offset + entity.length]
                        if bot_username and bot_username.lower() in mention_text.lower():
                            bot_mentioned = True
                    elif entity.type == 'text_mention':
                        if entity.user.id == context.bot.id:
                            bot_mentioned = True
            
            if bot_mentioned:
                try:
                    query = update.message.text.replace(f"@{bot_username}", "").strip()
                    
                    async with aiohttp.ClientSession() as session:
                        url = DEEPSEEK_API.format(query)
                        async with session.get(url, timeout=15) as response:
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    ai_response = data.get('response', data.get('answer', data.get('result', 'No response')))
                                    if ai_response and ai_response != 'No response':
                                        
                                        watermark = "\n\n───────\n🤖 AI by @TITANXCONTACT"
                                        await update.message.reply_text(ai_response + watermark)
                                except:
                                    text_response = await response.text()
                                    if text_response and len(text_response) < 4000:
                                        watermark = "\n\n───────\n🤖 AI by @TITANXCONTACT"
                                        await update.message.reply_text(text_response[:4000] + watermark)
                except Exception as e:
                    print(f"AI API Error: {e} | Bot: @TITANXCONTACT")
    
    def run(self):
        """Start the bot"""
        print("🤖 Bot starting...")
        print("📡 Connecting to Telegram...")
        print("💧 Watermark: @TITANXCONTACT - Do not remove or redistribute")
        self.app.bot_data['start_time'] = time.time()
        print("✅ Bot is running! Press Ctrl+C to stop.")
        print("🔒 Watermark protection: ACTIVE")
        print("🔧 Bot Framework by @TITANXCONTACT")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
       
        print("=" * 50)
        print("TELEGRAM BOT FRAMEWORK")
        print("Developed by: @TITANXCONTACT")
        print("Do not remove or alter this watermark")
        print("Unauthorized redistribution prohibited")
        print("=" * 50)
        
        bot = TelegramBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user | Framework: @TITANXCONTACT")
    except Exception as e:
        print(f"❌ Fatal error: {e} | Framework: @TITANXCONTACT")