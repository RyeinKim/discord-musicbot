import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import json
import re
from collections import deque
from datetime import datetime
import os
import shutil
from typing import Optional

# config.json 파일 읽기
with open('config.json') as config_file:
    config = json.load(config_file)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

url_regex = re.compile(r'(https?://[^\s]+)')

CONTROL_BUTTON_IDS = {"pause", "resume", "skip", "view_queue", "search_song"}

MAX_LOG_ENTRIES = 8

def ensure_activity_log():
    if not hasattr(bot, 'activity_logs'):
        bot.activity_logs = deque(maxlen=MAX_LOG_ENTRIES)
    
def add_activity_log(author: str, action: str):
    ensure_activity_log()
    timestamp = datetime.now().strftime('%H:%M:%S')
    entry = f"[{timestamp}] {author} {action}"
    bot.activity_logs.appendleft(entry)
    return entry

def format_requester(item: dict):
    return item.get('requested_by_mention') or item.get('requested_by') or "알 수 없음"

def format_user(actor: Optional[object]):
    if actor is None:
        return "알 수 없음"
    if isinstance(actor, str):
        return actor
    mention = getattr(actor, "mention", None)
    if mention:
        return mention
    display_name = getattr(actor, "display_name", None)
    if display_name:
        return display_name
    return str(actor)

def get_current_track_title():
    current = getattr(bot, 'current_track', None)
    if current and current.get('title'):
        return current['title']
    return "현재 곡"

def get_ffmpeg_executable():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Windows 로컬 번들(ffmpeg/bin/ffmpeg.exe) 우선 사용
    win_ffmpeg = os.path.join(base_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')
    if os.name == 'nt' and os.path.isfile(win_ffmpeg):
        ffmpeg_dir = os.path.dirname(win_ffmpeg)
        # DLL 탐색을 위해 PATH에 ffmpeg/bin 추가
        current_path = os.environ.get('PATH', '')
        if ffmpeg_dir not in current_path:
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + current_path
        return win_ffmpeg

    # macOS/Linux 등: 일반 경로 탐색
    for candidate in [
        '/opt/homebrew/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
        '/usr/bin/ffmpeg',
        'ffmpeg',
    ]:
        path = shutil.which(candidate) if candidate == 'ffmpeg' else candidate
        if path and (candidate == 'ffmpeg' or os.path.isfile(path)):
            return path if candidate != 'ffmpeg' else path

    # 최후 수단: 이름만 반환(실패 시 오류 메시지로 노출)
    return 'ffmpeg'

FFMPEG_EXECUTABLE = get_ffmpeg_executable()

async def get_music_player(channel) -> 'MusicPlayer':
    # 채널별로 동일한 View/메시지를 재사용
    if not hasattr(bot, 'ui_views'):
        bot.ui_views = {}
    view = bot.ui_views.get(channel.id)
    if view is None:
        view = MusicPlayer(bot)
        bot.ui_views[channel.id] = view
        # 최초 1회 UI 구성
        await view.refresh_panels(channel, status_text="패널 초기화")
    return view

class SearchModal(discord.ui.Modal, title="🎵 노래 검색"):
    """노래 검색을 위한 Modal"""
    search_input = discord.ui.TextInput(
        label="노래 제목 또는 URL",
        placeholder="검색하고 싶은 노래 제목이나 YouTube URL을 입력하세요...",
        required=True,
        max_length=200,
        style=discord.TextStyle.short
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        """Modal 제출 시 처리"""
        search_query = self.search_input.value.strip()

        if not search_query:
            await interaction.response.send_message("검색어를 입력해주세요!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # 음성 채널 연결 확인
        voice_client = interaction.guild.voice_client

        if not voice_client:
            # 사용자가 음성 채널에 있는지 확인
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                await channel.connect()
                voice_client = interaction.guild.voice_client
                print("Bot joined the voice channel via search")
            else:
                await interaction.followup.send("먼저 음성 채널에 접속해주세요!", ephemeral=True)
                return

        # 검색 및 재생
        is_url = url_regex.match(search_query) is not None
        if not is_url:
            search_query += " lyrics"

        ytdl_format_options = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True if not is_url else False,
        }

        try:
            music_player = await get_music_player(interaction.channel)
            await music_player.update_status_panel(interaction.channel, status_text="검색 중...")

            with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                if is_url:
                    info = await asyncio.to_thread(ydl.extract_info, search_query, False)
                    if 'entries' in info and len(info['entries']) > 0:
                        info = info['entries'][0]
                else:
                    info = await asyncio.to_thread(ydl.extract_info, f"ytsearch1:{search_query}", False)
                    if 'entries' in info and len(info['entries']) > 0:
                        info = info['entries'][0]
                    else:
                        info = None

                if info:
                    original_url = info.get('webpage_url') or info.get('url')
                    title = info.get('title', 'Unknown Title')
                    queue_entry = {
                        'url': original_url,
                        'title': title,
                        'requested_by': interaction.user.display_name,
                        'requested_by_id': interaction.user.id,
                        'requested_by_mention': interaction.user.mention
                    }
                    bot.music_queue.append(queue_entry)
                    print(f"노래가 큐에 추가되었습니다 (검색창): {title}")

                    await music_player.refresh_panels(
                        interaction.channel,
                        status_text=f"'{title}' 큐에 추가됨",
                        log_entry=("interact", interaction.user, f"'{title}'을(를) 큐에 추가했습니다.")
                    )

                    await interaction.followup.send(f"✅ **{title}**을(를) 대기열에 추가했습니다!", ephemeral=True)
                else:
                    await interaction.followup.send("노래를 찾을 수 없습니다.", ephemeral=True)
                    return

            if not voice_client.is_playing():
                await play_next(interaction.channel)

        except Exception as e:
            print(f"검색 오류 발생: {e}")
            await interaction.followup.send(f"노래 검색 중 오류가 발생했습니다: {e}", ephemeral=True)

class QueueView(discord.ui.View):
    """대기열 보기 및 삭제를 위한 View"""
    def __init__(self, bot):
        super().__init__(timeout=300)  # 5분 후 타임아웃
        self.bot = bot
        self.add_select_menu()

    def build_queue_embed(self):
        """대기열 Embed 생성"""
        embed = discord.Embed(title="📋 음악 대기열", color=discord.Color.blue())

        # 현재 재생 중인 곡
        current_track = getattr(self.bot, 'current_track', None)
        if current_track:
            requester = format_requester(current_track)
            embed.add_field(
                name="🎵 현재 재생 중",
                value=f"[{current_track.get('title', 'Unknown Title')}]({current_track.get('url', '#')})\n요청자: {requester}",
                inline=False
            )

        # 대기열
        queue_list = list(self.bot.music_queue)
        if queue_list:
            queue_text = []
            for idx, item in enumerate(queue_list, start=1):
                title = item.get('title', 'Unknown Title')
                requester = format_requester(item)
                if len(title) > 40:
                    title = title[:37] + "..."
                queue_text.append(f"`{idx}.` {title} • {requester}")

            # 10개씩 나눠서 표시
            chunk_size = 10
            for i in range(0, len(queue_text), chunk_size):
                chunk = queue_text[i:i+chunk_size]
                field_name = f"대기 중 ({i+1}-{min(i+chunk_size, len(queue_text))})" if len(queue_text) > chunk_size else "대기 중"
                embed.add_field(name=field_name, value="\n".join(chunk), inline=False)

            embed.set_footer(text=f"총 {len(queue_list)}곡 대기 중 • 아래 메뉴에서 삭제할 곡을 선택하세요")
        else:
            embed.add_field(name="대기 중", value="대기열이 비어 있습니다.", inline=False)

        return embed

    def add_select_menu(self):
        """대기열 선택 메뉴 추가"""
        queue_list = list(self.bot.music_queue)
        if not queue_list:
            return

        # Select Menu는 최대 25개 옵션만 가능
        options = []
        for idx, item in enumerate(queue_list[:25], start=1):
            title = item.get('title', 'Unknown Title')
            requester = format_requester(item)

            # 제목이 너무 길면 축약 (label은 최대 100자)
            if len(title) > 60:
                title = title[:57] + "..."

            # description은 최대 100자
            description = f"요청자: {requester}"
            if len(description) > 100:
                description = description[:97] + "..."

            options.append(
                discord.SelectOption(
                    label=f"{idx}. {title}",
                    value=str(idx),
                    description=description,
                    emoji="🗑️"
                )
            )

        if options:
            select = discord.ui.Select(
                placeholder="삭제할 곡을 선택하세요...",
                options=options,
                custom_id="queue_select"
            )
            select.callback = self.select_callback
            self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        """Select Menu 콜백"""
        await interaction.response.defer()

        position = int(interaction.data['values'][0])

        if len(self.bot.music_queue) == 0:
            await interaction.followup.send("대기열이 비어 있습니다.", ephemeral=True)
            return

        if position < 1 or position > len(self.bot.music_queue):
            await interaction.followup.send(f"잘못된 선택입니다.", ephemeral=True)
            return

        # 곡 삭제
        queue_list = list(self.bot.music_queue)
        removed_item = queue_list[position - 1]
        removed_title = removed_item.get('title', 'Unknown Title')

        del queue_list[position - 1]
        self.bot.music_queue = deque(queue_list)

        # 메인 채널 UI 업데이트
        if hasattr(self.bot, 'ui_views'):
            for channel_id, view in self.bot.ui_views.items():
                if view.last_channel:
                    await view.refresh_panels(
                        view.last_channel,
                        status_text=f"'{removed_title}' 삭제됨",
                        log_entry=("interact", interaction.user, f"대기열 {position}번 '{removed_title}'을(를) 삭제했습니다.")
                    )
                    break

        # 업데이트된 대기열 표시
        new_view = QueueView(self.bot)
        new_embed = new_view.build_queue_embed()
        await interaction.edit_original_response(embed=new_embed, view=new_view)
        await interaction.followup.send(f"✅ **{position}번** 곡을 삭제했습니다: {removed_title}", ephemeral=True)

        print(f"대기열에서 삭제됨 (UI): {position}. {removed_title}")

class MusicPlayer(discord.ui.View):
    def __init__(self, bot, title_message=None, button_message=None, event_message=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.title_message = title_message
        self.button_message = button_message
        self.event_message = event_message
        self.log_thread: Optional[discord.Thread] = None
        self.pending_log_messages: dict[str, discord.Message] = {}
        self.last_channel: Optional[discord.TextChannel] = None

    def build_status_embed(self, status_text: Optional[str] = None):
        embed = discord.Embed(title="🎧 음악 제어판", color=discord.Color.blurple())
        current_track = getattr(bot, 'current_track', None)
        if current_track:
            requester = format_requester(current_track)
            embed.add_field(
                name="현재 재생 중",
                value=f"[{current_track.get('title', 'Unknown Title')}]({current_track.get('url', '#')})\n요청자: {requester}",
                inline=False
            )
        else:
            embed.add_field(name="현재 재생 중", value="재생 중인 곡이 없습니다.", inline=False)

        queue_preview = list(bot.music_queue)[:3]
        if queue_preview:
            lines = []
            for idx, item in enumerate(queue_preview, start=1):
                lines.append(f"{idx}. {item.get('title', 'Unknown Title')} • {format_requester(item)}")
            embed.add_field(name="다음 곡", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="다음 곡", value="대기열이 비어 있습니다.", inline=False)

        if status_text:
            bot.last_status_text = status_text
        footer_text = getattr(bot, 'last_status_text', None)
        if footer_text:
            embed.set_footer(text=footer_text)
        return embed

    async def update_status_panel(self, channel, status_text: Optional[str] = None):
        embed = self.build_status_embed(status_text=status_text)
        created_new = False
        if self.title_message:
            await self.title_message.edit(embed=embed)
        else:
            self.title_message = await channel.send(embed=embed)
            created_new = True
        self.last_channel = channel
        if created_new:
            await self.cleanup_old_panels(channel, keep_message_id=self.title_message.id)

    async def refresh_panels(
        self,
        channel,
        *,
        status_text: Optional[str] = None,
        log_entry: Optional[tuple] = None,
        log_token: Optional[str] = None,
        clear_log_token: bool = False,
    ):
        await self.update_status_panel(channel, status_text=status_text)
        await self.update_button_message(channel)
        await self.update_event_message(
            channel,
            log_entry,
            replace_token=log_token,
            clear_token=clear_log_token,
        )
        self.last_channel = channel
 
    async def ensure_log_thread(self, channel) -> Optional[discord.Thread]:
        # 이미 존재하고 아카이브되지 않았다면 재사용
        if self.log_thread and not self.log_thread.archived:
            return self.log_thread

        # 아카이브된 경우 해제 시도
        if self.log_thread and self.log_thread.archived:
            try:
                await self.log_thread.edit(archived=False, locked=False)
                return self.log_thread
            except (discord.Forbidden, discord.HTTPException):
                self.log_thread = None

        if not self.title_message:
            await self.update_status_panel(channel, status_text=getattr(bot, 'last_status_text', None))

        try:
            self.log_thread = await channel.create_thread(
                name="🎵 음악 이벤트 로그",
                message=self.title_message,
                auto_archive_duration=1440
            )
            return self.log_thread
        except (discord.Forbidden, discord.HTTPException):
            return None

    async def cleanup_old_panels(self, channel, keep_message_id: int):
        try:
            async for message in channel.history(limit=50):
                if message.id == keep_message_id:
                    continue
                if (
                    message.author.id == self.bot.user.id
                    and message.embeds
                    and message.embeds[0].title == "🎧 음악 제어판"
                ):
                    await message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def cleanup_old_controls(self, channel, keep_message_id: int):
        try:
            async for message in channel.history(limit=50):
                if message.id == keep_message_id:
                    continue
                if message.author.id != self.bot.user.id:
                    continue
                if not message.components:
                    continue
                for row in message.components:
                    for component in getattr(row, "children", []):
                        if getattr(component, "custom_id", None) in CONTROL_BUTTON_IDS:
                            await message.delete()
                            break
                    else:
                        continue
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

    @discord.ui.button(label="일시정지", style=discord.ButtonStyle.blurple, custom_id="pause")
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await self.refresh_panels(
                interaction.channel,
                log_entry=("interact", interaction.user, "노래를 일시정지했습니다."),
                status_text="일시정지됨"
            )

    @discord.ui.button(label="재생", style=discord.ButtonStyle.green, custom_id="resume")
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await self.refresh_panels(
                interaction.channel,
                log_entry=("interact", interaction.user, "노래를 다시 재생했습니다."),
                status_text="재생 재개"
            )

    @discord.ui.button(label="스킵", style=discord.ButtonStyle.red, custom_id="skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.followup.send("Bot이 음성 채널에 접속해 있지 않습니다.", ephemeral=True)
            return
        if len(bot.music_queue) > 0:
            # 재생 작업 중복 방지 플래그 설정
            if getattr(bot, 'is_playing_next', False):
                await self.refresh_panels(
                    interaction.channel,
                    log_entry=("system", None, "재생 작업이 이미 진행 중입니다."),
                    status_text="재생 준비 중"
                )
                return

            # 스킵 플래그 설정 (after_playback 콜백 방지용)
            bot.skip_requested = True
            skipped_title = get_current_track_title()

            if voice_client.is_playing():
                voice_client.stop()
                # 재생이 완전히 중지될 때까지 대기
                while voice_client.is_playing():
                    await asyncio.sleep(0.1)

            # 스킵 로그를 먼저 기록
            await self.update_event_message(
                interaction.channel,
                log_entry=("interact", interaction.user, f"'{skipped_title}'을(를) 스킵했습니다."),
            )

            # 다음 곡 재생
            await play_next(interaction.channel)
        else:
            if voice_client and voice_client.is_playing():
                voice_client.stop()
            if getattr(bot, 'current_track', None):
                skipped_title = get_current_track_title()
                bot.current_track = None
                await self.refresh_panels(
                    interaction.channel,
                    log_entry=("interact", interaction.user, f"'{skipped_title}' 재생을 중지했습니다."),
                    status_text="대기열 없음"
                )
            else:
                await interaction.followup.send("대기열이 비어 있습니다.", ephemeral=True)

    @discord.ui.button(label="대기열 보기", style=discord.ButtonStyle.gray, custom_id="view_queue")
    async def view_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        if len(bot.music_queue) == 0:
            await interaction.followup.send("대기열이 비어 있습니다.", ephemeral=True)
            return

        # QueueView를 생성하여 표시
        queue_view = QueueView(bot)
        embed = queue_view.build_queue_embed()
        await interaction.followup.send(embed=embed, view=queue_view, ephemeral=True)

    @discord.ui.button(label="🔍 검색", style=discord.ButtonStyle.primary, custom_id="search_song")
    async def search_song(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Modal을 열어서 검색어 입력받기
        modal = SearchModal(bot)
        await interaction.response.send_modal(modal)

    async def update_title_message(self, channel, content: str):
        await self.update_status_panel(channel, status_text=content)

    async def update_button_message(self, channel):
        content = "🎛️ 아래 버튼으로 음악을 제어하세요."
        if self.button_message:
            await self.button_message.edit(content=content, view=self)
        else:
            self.button_message = await channel.send(content, view=self)
            await self.cleanup_old_controls(channel, keep_message_id=self.button_message.id)

    async def update_event_message(
        self,
        channel,
        log_entry: Optional[tuple] = None,
        *,
        replace_token: Optional[str] = None,
        clear_token: bool = False,
    ):
        if not log_entry:
            return
        entry_type, actor, action = log_entry
        if entry_type == "interact":
            author = format_user(actor)
        elif entry_type == "system":
            author = "시스템"
        else:
            author = format_user(actor)
        ensure_activity_log()
        formatted = add_activity_log(author, action)
        thread = await self.ensure_log_thread(channel)
        if not thread:
            await channel.send(formatted)
            return
        if replace_token:
            pending = self.pending_log_messages.get(replace_token)
            if pending:
                try:
                    await pending.edit(content=formatted)
                except (discord.Forbidden, discord.HTTPException):
                    pending = None
            if not pending:
                try:
                    pending = await thread.send(formatted)
                except (discord.Forbidden, discord.HTTPException):
                    pending = None
                if pending:
                    self.pending_log_messages[replace_token] = pending
            if clear_token:
                self.pending_log_messages.pop(replace_token, None)
            return
        try:
            await thread.send(formatted)
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def delete_all_messages(self, channel=None):
        if self.title_message:
            await self.title_message.delete()
            self.title_message = None
        if self.button_message:
            await self.button_message.delete()
            self.button_message = None
        if self.event_message:
            await self.event_message.delete()
            self.event_message = None
        if self.log_thread:
            try:
                await self.log_thread.edit(archived=True, locked=True)
            except (discord.Forbidden, discord.HTTPException):
                pass
            self.log_thread = None
        self.pending_log_messages.clear()
        if not channel:
            channel = self.last_channel
        if channel and hasattr(bot, "ui_views"):
            if bot.ui_views.get(channel.id) is self:
                del bot.ui_views[channel.id]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print(f'Using FFmpeg executable: {FFMPEG_EXECUTABLE}')

@bot.command(name='join', help='Bot을 음성 채널에 참여시킵니다')
async def join(ctx):
    print("join command invoked")
    if not ctx.message.author.voice:
        await ctx.send("음성 채널에 먼저 접속해주세요!")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()
    print("Bot joined the voice channel")

@bot.command(name='leave', help='Bot을 음성 채널에서 나가게 합니다')
async def leave(ctx):
    print("leave command invoked")
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        print("Bot left the voice channel")
    else:
        await ctx.send("Bot이 음성 채널에 접속해 있지 않습니다.")

async def play_next(channel):
    print("play_next invoked")
    
    # 이미 재생 작업이 진행 중이면 중복 실행 방지
    if getattr(bot, 'is_playing_next', False):
        print("이미 재생 작업이 진행 중입니다. 중복 실행 방지.")
        return
    
    # 재생 작업 시작 플래그 설정
    bot.is_playing_next = True
    
    if len(bot.music_queue) > 0:
        next_item = bot.music_queue.popleft()
        next_url = next_item['url']
        title = next_item['title']
        requester = format_requester(next_item)
        requester_actor = next_item.get('requested_by_mention') or next_item.get('requested_by')
        voice_client = channel.guild.voice_client
        if not voice_client:
            bot.current_track = None
            bot.is_playing_next = False
            await channel.send("음성 채널 연결을 찾을 수 없습니다. `!join`으로 다시 연결해주세요.")
            return
        
        # 재생 중이면 완전히 중지될 때까지 대기
        if voice_client.is_playing():
            voice_client.stop()
            while voice_client.is_playing():
                await asyncio.sleep(0.1)
        
        ytdl_format_options = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        try:
            music_player = await get_music_player(channel)
            prep_token = f"prep:{channel.id}:{next_item.get('url')}"
            # 로딩 상태 표시
            await music_player.refresh_panels(
                channel,
                status_text=f"로딩 중: {title}",
                log_entry=("interact", requester_actor, f"님이 요청한 '{title}' 재생을 준비 중입니다."),
                log_token=prep_token,
            )
            with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, next_url, False)
                url2 = None
                if 'formats' in info:
                    for f in info['formats']:
                        if f['ext'] == 'm4a' or f['ext'] == 'webm':
                            url2 = f['url']
                            break
                if not url2:
                    url2 = info.get('url', None)

                if not url2:
                    raise Exception("오디오 스트림 URL을 찾을 수 없습니다.")

                options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -timeout 10000000 -loglevel debug',
                    'options': '-vn'
                }
                print(f"재생 URL: {url2}")
                source = discord.FFmpegOpusAudio(
                    url2,
                    executable=FFMPEG_EXECUTABLE,
                    before_options=options['before_options'],
                    options=options['options']
                )

                def after_playback(error):
                    if error:
                        print(f"재생 중 에러 발생: {error}")
                        return
                    # 스킵이 요청되지 않았을 때만 다음 곡 재생
                    if not getattr(bot, 'skip_requested', False):
                        asyncio.run_coroutine_threadsafe(play_next(channel), bot.loop)
                    else:
                        # 스킵 플래그 초기화 (다음 곡 재생 시)
                        bot.skip_requested = False
                        print("스킵으로 인한 자동 재생 방지")

                voice_client.play(source, after=after_playback)

            bot.current_track = {
                'title': title,
                'url': next_item.get('url'),
                'requested_by': next_item.get('requested_by'),
                'requested_by_id': next_item.get('requested_by_id'),
                'requested_by_mention': next_item.get('requested_by_mention')
            }

            # 재생 시작 상태로 갱신
            await music_player.refresh_panels(
                channel,
                status_text=f"현재 재생 중: {title}",
                log_entry=("interact", requester_actor, f"님이 요청한 '{title}' 재생을 시작했습니다."),
                log_token=prep_token,
                clear_log_token=True,
            )
            print(f"현재 재생 중: {title}")
            
            # 재생 작업 완료 - 플래그 해제
            bot.is_playing_next = False
        except Exception as e:
            print(f"오류 발생: {e}")
            await channel.send(f"노래 재생 중 오류가 발생했습니다: {e}")
            bot.current_track = None
            await music_player.refresh_panels(
                channel,
                status_text="재생 오류",
                log_entry=("system", None, f"'{title}' 재생에 실패했습니다: {e}")
            )
            # 오류 발생 시에도 플래그 해제
            bot.is_playing_next = False
    else:
        # 큐가 비었을 때 상태 갱신
        music_player = await get_music_player(channel)
        bot.current_track = None
        await music_player.refresh_panels(
            channel,
            status_text="대기열이 비어 있습니다.",
            log_entry=("system", None, "대기열이 모두 소진되었습니다.")
        )
        print("큐에 더 이상 노래가 없습니다.")
        # 재생 작업 완료 - 플래그 해제
        bot.is_playing_next = False

@bot.command(name='play', help='노래를 검색하여 재생합니다')
async def play(ctx, *, search: str):
    print("play command invoked")
    is_url = url_regex.match(search) is not None
    if not is_url:
        search += " lyrics"  # 검색어에 'lyrics' 추가
    ytdl_format_options = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        # 검색 단계는 가볍게 메타데이터만 가져오도록 최적화
        'extract_flat': True if not is_url else False,
    }

    voice_client = ctx.message.guild.voice_client

    if not voice_client:
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            voice_client = ctx.message.guild.voice_client
            print("Bot joined the voice channel")
        else:
            await ctx.send("음성 채널에 먼저 접속해주세요!")
            return

    try:
        music_player = await get_music_player(ctx.channel)
        await music_player.update_status_panel(ctx.channel, status_text="검색 중...")
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            if is_url:
                info = await asyncio.to_thread(ydl.extract_info, search, False)
                # 재생목록 등 예외적으로 entries가 있을 수 있어 방어적으로 첫 항목 선택
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
            else:
                # ytsearch1로 1개만 가져오고, extract_flat로 빠른 메타 추출
                info = await asyncio.to_thread(ydl.extract_info, f"ytsearch1:{search}", False)
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                else:
                    info = None

            if info:
                original_url = info.get('webpage_url') or info.get('url')
                title = info.get('title', 'Unknown Title')
                queue_entry = {
                    'url': original_url,
                    'title': title,
                    'requested_by': ctx.author.display_name,
                    'requested_by_id': ctx.author.id,
                    'requested_by_mention': ctx.author.mention
                }
                bot.music_queue.append(queue_entry)
                print(f"노래가 큐에 추가되었습니다: {title}")
                await music_player.refresh_panels(
                    ctx.channel,
                    status_text=f"'{title}' 큐에 추가됨",
                    log_entry=("interact", ctx.author, f"'{title}'을(를) 큐에 추가했습니다.")
                )
            else:
                await ctx.send("노래를 찾을 수 없습니다.")
                return

        if not voice_client.is_playing():
            await play_next(ctx.channel)
        try:
            await ctx.message.delete()  # 사용자의 메시지를 삭제
        except (discord.errors.NotFound, discord.errors.Forbidden):
            pass
    except Exception as e:
        print(f"오류 발생: {e}")
        await ctx.send(f"노래 검색 중 오류가 발생했습니다: {e}")

@bot.command(name='stop', help='현재 재생 중인 음악을 멈춥니다')
async def stop(ctx):
    print("stop command invoked")
    voice_client = ctx.message.guild.voice_client
    music_player = await get_music_player(ctx.channel)
    if voice_client and voice_client.is_playing():
        stopped_title = get_current_track_title()
        voice_client.stop()
        bot.current_track = None
        print("Music stopped")
        await music_player.refresh_panels(
            ctx.channel,
            log_entry=("interact", ctx.author, f"'{stopped_title}' 재생을 중지했습니다."),
            status_text="재생 정지"
        )
    else:
        await ctx.send("현재 재생 중인 음악이 없습니다.")

@bot.command(name='skip', help='현재 노래를 스킵하고 다음 노래를 재생합니다')
async def skip(ctx):
    print("skip command invoked")
    voice_client = ctx.message.guild.voice_client
    if not voice_client:
        await ctx.send("Bot이 음성 채널에 접속해 있지 않습니다.")
        return
    music_player = await get_music_player(ctx.channel)
    if len(bot.music_queue) > 0:
        # 재생 작업 중복 방지 플래그 설정
        if getattr(bot, 'is_playing_next', False):
            await ctx.send("이미 재생 작업이 진행 중입니다.")
            return

        # 스킵 플래그 설정 (after_playback 콜백 방지용)
        bot.skip_requested = True
        skipped_title = get_current_track_title()

        if voice_client.is_playing():
            voice_client.stop()
            # 재생이 완전히 중지될 때까지 대기
            while voice_client.is_playing():
                await asyncio.sleep(0.1)

        await music_player.update_event_message(
            ctx.channel,
            log_entry=("interact", ctx.author, f"'{skipped_title}'을(를) 스킵했습니다."),
        )
        # 다음 곡 재생
        await play_next(ctx.channel)
        await ctx.send("다음 노래가 재생됩니다.")
    else:
        if voice_client and voice_client.is_playing():
            voice_client.stop()
        if getattr(bot, 'current_track', None):
            stopped_title = get_current_track_title()
            bot.current_track = None
            await music_player.refresh_panels(
                ctx.channel,
                log_entry=("interact", ctx.author, f"'{stopped_title}' 재생을 중지했습니다."),
                status_text="대기열 없음"
            )
        else:
            await ctx.send("대기열이 비어 있습니다.")

@bot.command(name='queue', help='현재 대기열의 모든 곡을 표시합니다')
async def queue(ctx):
    print("queue command invoked")
    if len(bot.music_queue) == 0:
        await ctx.send("대기열이 비어 있습니다.")
        return

    embed = discord.Embed(title="📋 음악 대기열", color=discord.Color.blue())

    # 현재 재생 중인 곡 표시
    current_track = getattr(bot, 'current_track', None)
    if current_track:
        requester = format_requester(current_track)
        embed.add_field(
            name="🎵 현재 재생 중",
            value=f"[{current_track.get('title', 'Unknown Title')}]({current_track.get('url', '#')})\n요청자: {requester}",
            inline=False
        )

    # 대기열의 모든 곡 표시 (번호 포함)
    queue_list = list(bot.music_queue)
    queue_text = []
    for idx, item in enumerate(queue_list, start=1):
        title = item.get('title', 'Unknown Title')
        requester = format_requester(item)
        # 제목이 너무 길면 축약
        if len(title) > 50:
            title = title[:47] + "..."
        queue_text.append(f"`{idx}.` {title} • {requester}")

    # Discord embed 필드는 1024자 제한이 있으므로 여러 필드로 나눔
    chunk_size = 10
    for i in range(0, len(queue_text), chunk_size):
        chunk = queue_text[i:i+chunk_size]
        field_name = f"대기 중 ({i+1}-{min(i+chunk_size, len(queue_text))})" if len(queue_text) > chunk_size else "대기 중"
        embed.add_field(name=field_name, value="\n".join(chunk), inline=False)

    embed.set_footer(text=f"총 {len(queue_list)}곡 대기 중 • !remove <번호>로 특정 곡을 삭제할 수 있습니다")

    await ctx.send(embed=embed)
    try:
        await ctx.message.delete()  # 사용자의 메시지를 삭제
    except (discord.errors.NotFound, discord.errors.Forbidden):
        pass

@bot.command(name='remove', help='대기열에서 특정 곡을 삭제합니다 (예: !remove 2)')
async def remove(ctx, position: int):
    print(f"remove command invoked: position={position}")

    if len(bot.music_queue) == 0:
        await ctx.send("대기열이 비어 있습니다.")
        return

    # 유효한 범위 확인
    if position < 1 or position > len(bot.music_queue):
        await ctx.send(f"잘못된 번호입니다. 1부터 {len(bot.music_queue)} 사이의 번호를 입력해주세요.")
        return

    # deque를 리스트로 변환하여 인덱스 접근
    queue_list = list(bot.music_queue)
    removed_item = queue_list[position - 1]
    removed_title = removed_item.get('title', 'Unknown Title')

    # 해당 위치의 곡 삭제
    del queue_list[position - 1]

    # deque 재구성
    bot.music_queue = deque(queue_list)

    # UI 업데이트 (스레드 로그로만 기록)
    music_player = await get_music_player(ctx.channel)
    await music_player.refresh_panels(
        ctx.channel,
        status_text=f"'{removed_title}' 삭제됨",
        log_entry=("interact", ctx.author, f"대기열 {position}번 '{removed_title}'을(를) 삭제했습니다.")
    )

    print(f"대기열에서 삭제됨: {position}. {removed_title}")

    # 사용자 커맨드 메시지 삭제
    try:
        await ctx.message.delete()
    except (discord.errors.NotFound, discord.errors.Forbidden):
        pass

bot.music_queue = deque()
bot.skip_requested = False  # 스킵 요청 플래그 초기화
bot.is_playing_next = False  # 재생 작업 진행 중 플래그 초기화
bot.activity_logs = deque(maxlen=MAX_LOG_ENTRIES)
bot.current_track = None
bot.last_status_text = "대기열 대기 중"

bot.run(config['token'])
