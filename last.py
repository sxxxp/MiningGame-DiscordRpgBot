from discord import app_commands, Interaction, ui, ButtonStyle, SelectOption, TextStyle
from discord.ext import tasks
import discord
import random
import datetime
import pymysql
from enum import Enum
from itertools import chain
import random
import math
import asyncio
import json

GUILD_ID = '934824600498483220'
LEVEL_PER_STAT = 2
KST = datetime.timezone(datetime.timedelta(hours=9))
ticket = {
    -0: 2, -1: 2, -2: 2, -3: 2, -4: 2, -5: 2, -6: 2, -8: 4}


class MyClient(discord.Client):

    @tasks.loop(time=datetime.time(hour=0, minute=0, second=0, tzinfo=KST))
    async def reward(self):
        weekday = datetime.datetime.now().weekday()
        cur = con.cursor()
        cur.execute("SELECT id FROM user_info")
        user = cur.fetchall()
        for i in user:
            cur.execute(
                "SELECT item_id FROM user_item WHERE id = %s AND item_id = %s", (i[0], 2))
            daily_ticket = cur.fetchone()
            if weekday == 3:
                cur.execute(
                    "SELECT item_id FROM user_item WHERE id = %s ANd item_id = %s", (i[0], 4))
                weekly_ticket = cur.fetchone()
                if not weekly_ticket:
                    cur.execute("INSERT INTO user_item VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                (4, "주간광산 입장권", "주간광산에 입장할 수 있는 아이템이다.", "X", 0, False, i[0]))
                cur.execute(
                    "UPDATE user_item SET amount = 1 WHERE item_id = %s", 4)
            if not daily_ticket:
                cur.execute(
                    "INSERT INTO user_item VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (2, "요일광산 입장권", "요일광산에 입장할 수 있는 아이템이다.", "X", 0, False, i[0]))

        cur.execute("UPDATE user_item SET amount = 1 WHERE item_id = %s", 2)
        con.commit()

    @tasks.loop(seconds=30)
    async def change_message(self):
        for i in ['개발', '0.0.1a버전 관리', '버그 제보 부탁']:
            await client.change_presence(status=discord.Status.online, activity=discord.Game(i))
            await asyncio.sleep(5)

    async def on_ready(self):
        await self.wait_until_ready()
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        setup()
        await self.reward.start()
        await self.change_message()
        print(f"{self.user} 에 로그인하였습니다!")


intents = discord.Intents.all()
client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)
con = pymysql.connect(host='localhost', password='0000',
                      user='root', port=3306, database='miner', charset='utf8')
adventrue_inventory = {}
mining_dic = {}
cnt = {}


class miningEnum(Enum):
    기본광산 = 1
    요일광산 = -datetime.datetime.today().weekday()
    주간광산 = -8


class statusEnum(Enum):
    힘 = 'power'
    체력 = 'hp'
    중량 = 'str'
    크리티컬데미지 = 'crit_damage'


def block_exp(level: int, exp: int):
    guild = client.get_guild(884259665964314655)
    name = ["0_", "1_", "2_", "3_", "4_", "5_", "6_", "7_", "8_", "9_", "10"]
    block = [discord.utils.get(guild.emojis, name=i) for i in name]
    level_file = open("./final/json/level.json", "r", encoding="utf-8")
    level_info = json.load(level_file)
    percent = round(exp/level_info[str(level)]*100)
    string = ''
    cnt = 0
    for _ in range(int(percent/10)):
        string += str(block[10])
        cnt += 1
    string += str(block[int(percent % 10)])
    cnt += 1
    for _ in range(10-cnt):
        string += str(block[0])
        cnt += 1
    return string, level_info[str(level)]


def is_levelup(level: int, exp: int, id: int):
    level_file = open("./final/json/level.json", "r", encoding="utf-8")
    level_info = json.load(level_file)
    num = 0
    while level_info[str(level+num)] <= exp:
        exp -= level_info[str(level+num)]
        num += 1
    cur = con.cursor()
    cur.execute(
        "UPDATE user_info SET level = level + %s , exp = %s WHERE id = %s", (num, exp, id))
    cur.execute(
        "UPDATE user_stat SET point = point + %s WHERE id = %s", (num*LEVEL_PER_STAT, id))
    con.commit()
    return num


def makeDictionary(keys: list, values: tuple):
    dictionary = {}
    for i in range(len(keys)):
        dictionary.update({keys[i]: values[i]})
    return dictionary


def getOption(option: str):
    power = hp = str = crit = damage = 0
    if option:
        for i in option.split(" "):
            if i[0] == 'p':
                power += i[1:]
            elif i[0] == 'h':
                hp += i[1:]
            elif i[0] == 'a':
                hp += i[1:]
                str += i[1:]
                power += i[1:]
                crit += i[1:]
                damage += i[1:]
            elif i[0] == "c":
                crit += i[1:]
            elif i[0] == "d":
                damage += i[1:]
    return {'power': power, 'hp': hp, 'str': str, 'crit': crit, 'damage': damage}


def authorize(id: int):  # 유저 정보가 있으면 True
    cur = con.cursor()
    cur.execute("SELECT * FROM user_info WHERE id = %s", id)
    return cur.fetchone() != None


def getStatus(id: int):  # 유저 스텟 불러오기
    cur = con.cursor()
    # 갑옷 힘,체력,중량 불러오기
    cur.execute(
        "SELECT SUM(power),SUM(hp),SUM(str) FROM user_wear WHERE id=%s AND wear = 1 ", id)
    wear = makeDictionary(['power', 'hp', 'str'], cur.fetchone())
    cur.execute(
        "SELECT power,damage,`option` FROM user_weapon WHERE id=%s AND wear = 1", id)
    weapon = makeDictionary(['power', 'damage', 'option'], cur.fetchone())
    option = getOption(weapon['option'])
    cur.execute(
        "SELECT power,hp*3,str/10,crit,crit_damage,point FROM user_stat WHERE id=%s", id)
    stat = makeDictionary(['power', 'hp', 'str', 'crit',
                          'crit_damage', 'point'], cur.fetchone())
    final = {'power': 0, 'hp': 25, "str": 0,
             'damage': 0, 'crit': 0, 'crit_damage': 0, 'maxhp': 0, 'point': 0}
    for key, value in chain(wear.items(), weapon.items(), option.items(), stat.items()):
        if value:
            final[key] += value
    final['damage'] /= 100
    final['crit_damage'] /= 100
    final['maxhp'] = final['hp']
    return final


def getSuccess(num: int, all: int):  # 확률 계산기
    return num >= random.uniform(1, all)


def setup():  # 데이터베이스 테이블 생성
    cur = con.cursor()  # 유저 데이터 테이블 생성
    # user_info 유저 정보(이름,경험치,레벨,돈,역할,생성일자)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_info
                (nickname TEXT,id TEXT,exp INT,level INT,money INT,role INT,create_at DATE)""")
    # user_stat 유저 스텟(칭호,힘,체력,무게,치명타,치명타데미지,포인트)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_stat 
                (id TEXT,title TEXT,power INT,hp INT,str INT,crit INT,crit_damage INT,point INT)""")
    # user_weapon 유저 무기(아이템아이디,이름,강화,등급,레벨,힘,데미지,옵션,착용여부,거래여부,아이디,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_weapon 
                (item_id INT PRIMARY KEY AUTO_INCREMENT,name TEXT,upgrade INT,`rank` TEXT,level INT, power INT,damage INT,`option` TEXT,wear BOOLEAN,trade BOOLEAN,id TEXT,url TEXT)""")
    # user_wear 유저 갑옷(아이템아이디,이름,강화,등급,레벨,힘,체력,무게,옵션,착용부위,착용여부,거래여부,아이디,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_wear 
                (item_id INT PRIMARY KEY AUTO_INCREMENT,name TEXT,upgrade INT,`rank` TEXT,level INT,power INT,hp INT,str INT, part INT,wear BOOLEAN, trade BOOLEAN,id TEXT,url TEXT)""")
    # user_item 유저 아이템(아이템아이디,이름,등급,가격,설명,거래여부,아이디,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_item
                (item_id INT, name TEXT,`rank` TEXT, price INT,description TEXT,trade BOOLEAN,amount INT,id TEXT)""")
    # weapon 무기 테이블(이름,등급,레벨,힘,데미지,옵션,옵션확률,거래여부,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS weapon
                (name TEXT,`rank` TEXT,level INT,power TEXT, damage TEXT,`option` TEXT,option_percent TEXT,trade BOOLEAN,url TEXT)""")
    # wear 갑옷 테이블(이름,등급,레벨,힘,체력,무게,옵션,옵션확률,착용부위,거래여부,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS wear
                (name TEXT,`rank` TEXT,level INT,power TEXT,hp TEXT,str TEXT,part INT,trade BOOLEAN,url TEXT)""")
    # enemy 광석(이름,힘,체력,층,드롭아이템코드,드롭아이템확률,드롭아이템개수,유틸아이템코드,유틸아이템드롭확률,유틸아이템드롭개수,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS enemy
                (name TEXT,power INT,hp INT,floor INT,exp INT,item_code TEXT,item_percent TEXT,item_amount TEXT,util_code TEXT,util_percent TEXT,util_amount TEXT,url TEXT)""")


@tree.command(guild=discord.Object(id=GUILD_ID), name="아이템거래", description="거래")
async def trade(interaction: Interaction, 유저: discord.Member, 코드: int, 개수: int):
    if not authorize(interaction.user.id) or not authorize(유저.id):
        return await interaction.response.send_message("`회원가입`이 필요하거나 상대방이 가입하지 않았습니다. ", ephemeral=True)
    cur = con.cursor()
    cur.execute("SELECT trade,amount FROM user_item WHERE id = %s AND item_id = %s",
                (interaction.user.id, 코드))
    try:
        canTrade, amount = cur.fetchone()
    except:
        return await interaction.response.send_message("아이템이 없습니다", ephemeral=True)
    else:
        if canTrade:
            if amount >= 개수:
                cur.execute(
                    "UPDATE user_item SET amount = amount - %s WHERE id = %s AND item_id = %s", (개수, interaction.user.id, 코드))
                cur.execute(
                    "SELECT amount FROM user_item WHERE id = %s AND item_id = %s", (유저.id, 코드))
                if cur.fetchone():
                    cur.execute(
                        "UPDATE user_item SET amount = amount + %s WHERE id = %s AND item_id = %s", (개수, 유저.id, 코드))
                else:
                    item_json = open('./final/json/util.json',
                                     'r', encoding="utf-8")
                    item_data: dict = json.load(item_json)
                    item = [코드]
                    for i in item_data[str(코드)].values():
                        item.append(i)
                    item.append(개수)
                    item.append(유저.id)
                    cur.execute(
                        "INSERT INTO user_item VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", item)
                con.commit()
                return await interaction.response.send_message(f"`{유저.display_name}`님에게 `{item_data[str(코드)]['name']}`를 `{개수}` 개 전달했습니다.", ephemeral=True)
            else:
                return await interaction.response.send_message("아이템이 부족합니다.", ephemeral=True)
        else:
            return await interaction.response.send_message("거래할 수 없는 아이템 입니다.", ephemeral=True)


@tree.command(guild=discord.Object(id=GUILD_ID), name="스텟", description="스테이터스")
async def status(interaction: Interaction, 스텟: statusEnum, 포인트: int):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    message = ''
    if 0 >= 포인트:
        message = '포인트는 `0`보다 큰 숫자여야 합니다.'
    else:
        cur = con.cursor()
        cur.execute("SELECT point FROM user_stat WHERE id = %s",
                    interaction.user.id)
        point = cur.fetchone()[0]
        if point < 포인트:
            message = f'포인트는 `현재 보유 포인트: {point}` 보다 작은 숫자여야 합니다.'
        else:
            cur.execute(f"""UPDATE user_stat SET
            point = point - {포인트} , 
            {스텟.value.replace("'","")} = {스텟.value.replace("'","")} + {포인트} 
            WHERE id = {interaction.user.id}""",)
            con.commit()
            message = f'`{스텟.name} +{포인트}`'
    await interaction.response.send_message(message, ephemeral=True)


@tree.command(guild=discord.Object(id=GUILD_ID), name="회원가입", description="회원가입입니다.")
async def register(interaction: Interaction, 닉네임: str):
    cur = con.cursor()
    if authorize(interaction.user.id):
        await interaction.response.send_message("아이디가 있습니다.", ephemeral=True)
    else:
        cur.execute("""INSERT INTO user_info(nickname,id,exp,level,money,role,create_at) 
                    VALUES(%s,%s,%s,%s,%s,%s,%s)""", (닉네임, interaction.user.id, 0, 1, 100, 0, datetime.today()))
        cur.execute("INSERT INTO user_stat(id,power,hp,str,crit,crit_damage,point) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (interaction.user.id, 1, 5, 5, 5, 50, 0))
        cur.execute("""INSERT INTO user_weapon(name,upgrade,`rank`,level,power,damage,wear,trade,id,url)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    ('기본 곡괭이', 0, 'F', 1, 5, 100, 1, 0, interaction.user.id, "https://cdn.discordapp.com/attachments/988424121878741022/1040198148661973022/pickaxe1.png"))
        con.commit()
        await interaction.response.send_message("아이디가 생성되었습니다.", ephemeral=True)


@tree.command(guild=discord.Object(id=GUILD_ID), name="정보", description="정보")
async def info(interaction: Interaction, 유저: discord.Member = None):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)

    async def setting(interaction: Interaction):
        cur = con.cursor()
        id = interaction.user.id if not 유저 else 유저.id
        cur.execute(
            "SELECT nickname,exp,level,money,create_at FROM user_info WHERE id=%s", id)
        user = makeDictionary(
            ['nickname', 'exp', 'level', 'money', 'create_at'], cur.fetchone())
        stat = getStatus(id)
        view = ui.View(timeout=None)
        button = ui.Button(label="새로고침")
        view.add_item(button)
        button.callback = setting
        embed = discord.Embed(title=user['nickname'])
        string_block, level_info = block_exp(user['level'], user['exp'])
        embed.add_field(
            name=f"Lv. {user['level']} {user['exp']}/{level_info}({round(user['exp']/level_info*100)}%)", value=string_block, inline=True)
        embed.add_field(name=f"{user['money']}💰", value="\u200b", inline=False)
        embed.add_field(name=f"힘 : \n{stat['power']}", value='\u200b')
        embed.add_field(name=f"데미지배수 : \nx{stat['damage']}", value="\u200b")
        embed.add_field(name=f"체력 : \n{stat['hp']}", value='\u200b')
        embed.add_field(name=f"중량 : \n{round(stat['str'],3)}", value='\u200b')
        embed.add_field(
            name=f"크리티컬 확률 : \n{round(stat['crit'])}%", value='\u200b')
        embed.add_field(
            name=f"크리티컬 데미지 : \n{round(stat['crit_damage']*100)}%", value='\u200b')
        embed.add_field(
            name=f"스텟 포인트 : {stat['point']}", value='\u200b', inline=False)
        embed.set_footer(text=f"생성일자 : {user['create_at']}")
        try:
            await interaction.response.edit_message(embed=embed, view=view)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)
    await interaction.response.send_message("정보 로딩중...", ephemeral=True)
    await setting(interaction)


@tree.command(guild=discord.Object(id=GUILD_ID), name="인벤토리", description="인벤토리")
async def inventory(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    page = {}
    page[interaction.user.id] = 0

    async def next_callback(interaction: Interaction):
        page[interaction.user.id] += 1
        await setup(interaction)

    async def previous_callback(interaction: Interaction):
        page[interaction.user.id] -= 1
        await setup(interaction)

    async def setup(interaction: Interaction):
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM user_item WHERE id = %s",
                    interaction.user.id)
        count = cur.fetchone()[0]
        cur.execute("SELECT name,description,`rank`,price,trade,amount FROM user_item WHERE id = %s ORDER BY item_id ASC LIMIT %s,10",
                    (interaction.user.id, page[interaction.user.id] * 10))
        embed = discord.Embed(title="인벤토리")
        for i in cur.fetchall():
            embed.add_field(
                name=f"{i[0]}[{i[2]}]({'거래가능' if i[4]==1 else '거래불가'}) {i[5]}개", value=i[1], inline=False)
        embed.set_footer(text=f"{page[interaction.user.id]+1} 페이지")
        view = ui.View(timeout=None)
        previous = ui.Button(
            label="이전으로", disabled=not page[interaction.user.id] > 0)
        next = ui.Button(label="다음으로", disabled=not (
            page[interaction.user.id]+1)*10 < count)
        view.add_item(previous)
        view.add_item(next)
        previous.callback = previous_callback
        next.callback = next_callback
        try:
            await interaction.response.edit_message(embed=embed, view=view)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)
    await interaction.response.send_message("아이템을 가져오는 중입니다.", ephemeral=True)
    await setup(interaction)


@tree.command(guild=discord.Object(id=GUILD_ID), name="채광초기화", description="채광이 버그가 나서 초기화가 필요할때 쓰세요.")
async def miningReset(interaction: Interaction):
    try:
        cnt[interaction.user.id]
    except KeyError:
        cnt[interaction.user.id] = -1
    if cnt[interaction.user.id] > 0:
        await interaction.response.send_message("초기화 할 수 없습니다.", ephemeral=True)
    else:
        mining_dic[interaction.user.id] = False
        await interaction.response.send_message("성공적으로 초기화 했습니다.", ephemeral=True)


@tree.command(guild=discord.Object(id=GUILD_ID), name="채광", description="채광")
async def mining(interaction: Interaction, 광산: miningEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    try:
        mining_dic[interaction.user.id]
    except KeyError:
        mining_dic[interaction.user.id] = True
    else:
        if mining_dic[interaction.user.id]:
            return await interaction.response.send_message("이미 광산에 들어와 있습니다.", ephemeral=True)
    cnt[interaction.user.id] = -1
    cur = con.cursor()
    if 광산.value <= 0:
        cur.execute("SELECT amount FROM user_item WHERE id= %s AND item_id=%s",
                    (interaction.user.id, ticket[광산.value]))
        getTicket = cur.fetchone()
        if not getTicket or getTicket[0] == 0:
            mining_dic[interaction.user.id] = False
            return await interaction.response.send_message("입장권이 없습니다.", ephemeral=True)
        else:
            cur.execute("UPDATE user_item SET amount=0 WHERE id = %s AND item_id=%s",
                        (interaction.user.id, ticket[광산.value]))
            con.commit()
        if 광산.value > -7:
            cnt[interaction.user.id] = 3
    stat = getStatus(interaction.user.id)
    adventrue_inventory[interaction.user.id] = makeDictionary(
        ['weight', 'items', 'names'], (0.0, [], []))

    async def remove_callback(interaction: Interaction):  # 아이템버리기
        view = ui.View(timeout=None)
        options = [SelectOption(
            label="뒤로가기", description="혹시 취소버튼을 눌렀다면 이걸 누르세요.", value="bug-bug-bug")]
        for item in adventrue_inventory[interaction.user.id]['items']:
            options.append(SelectOption(
                label=f"{item['name']} {item['amount']}개 ({item['price']*item['amount']}💰)",
                description=f"개당 중량 : {item['weight']} 총 중량 : {round(item['weight']*item['amount'],2)}",
                value=f"{item['name']}-{item['amount']}-{item['weight']}"
            ))
        items = ui.Select(placeholder="버릴 아이템을 골라주세요.",
                          options=options, disabled=not len(options))
        view.add_item(items)

        async def item_remove_callback(interaction: Interaction):
            name, amount, weight = items.values[0].split("-")
            if name == "bug":
                await interaction.response.edit_message(content="버그가 고쳐졌습니다.")
                return await start()

            class amountModal(ui.Modal, title=f"{name} {amount}개"):
                answer = ui.TextInput(
                    label="개수", placeholder="제거할 개수를 선택해주세요.", required=True)

                async def on_submit(self, interaction: Interaction):
                    try:
                        int(self.answer.value)
                    except:
                        pass
                    if int(self.answer.value) > int(amount) or int(self.answer.value) < 0:
                        pass
                    else:
                        adventrue_inventory[interaction.user.id]['weight'] -= int(
                            self.answer.value)*float(weight)
                        for i in adventrue_inventory[interaction.user.id]['items']:
                            if i['name'] == name:
                                i['amount'] -= int(self.answer.value)
                                if i['amount'] == 0:
                                    adventrue_inventory[interaction.user.id]['items'].remove(
                                        i)
                                    adventrue_inventory[interaction.user.id]['names'].remove(
                                        name)
                                break
                        await interaction.response.edit_message(content=f"{name}을 {self.answer.value}개 버렸습니다.\n중량 -{round(int(self.answer.value)*float(weight),3)}")
                        await start()
            await interaction.response.send_modal(amountModal())
        items.callback = item_remove_callback
        await interaction.response.edit_message(view=view)

    async def go_callback(interaction: Interaction):  # 탐험진행
        cur.execute(
            "SELECT name,power,hp,exp,item_code,item_percent,item_amount,util_code,util_percent,util_amount,url FROM enemy WHERE floor=%s ORDER BY RAND() LIMIT 1", 광산.value)
        enemy = makeDictionary(['name', 'power', 'hp', 'exp', 'item_code', "item_percent",
                               "item_amount", "util_code", "util_percent", "util_amount", "url"], cur.fetchone())
        stat['hp'] = stat['maxhp']

        async def run_callback(interaction: Interaction):  # 도망치기
            await interaction.response.edit_message(content="도망쳤습니다.")
            return await start()

        async def end_win_callback(interaction: Interaction):  # 전투 끝날때
            cnt[interaction.user.id] -= 1
            if cnt[interaction.user.id] == 0:
                return await stop_callback(interaction)
            await interaction.response.edit_message(content="재정비...")
            await start()

        async def win(interaction: Interaction):  # 이겼을때
            item_json = open('./final/json/stone.json', 'r', encoding='utf-8')
            util_json = open('./final/json/util.json', 'r', encoding='utf-8')
            util_data = json.load(util_json)
            stone_data = json.load(item_json)
            util_code = enemy['util_code'].split(" ")
            util_percent = enemy['util_percent'].split(" ")
            util_amount = enemy['util_amount'].split(" ")
            item_code = enemy['item_code'].split(" ")
            item_percent = enemy['item_percent'].split(" ")
            item_amount = enemy['item_amount'].split(" ")
            cur.execute("UPDATE user_info SET exp = exp + %s WHERE id = %s",
                        (enemy['exp'], interaction.user.id))
            con.commit()
            cur.execute(
                "SELECT level,exp FROM user_info WHERE id = %s", interaction.user.id)
            level, exp = cur.fetchone()
            num = is_levelup(level, exp, interaction.user.id)
            embed = discord.Embed(title="보상 요약")
            embed.add_field(
                name=f"{enemy['exp']} 경험치를 획득했습니다.", value="\u200b", inline=False)
            if num:
                embed.add_field(
                    name=f"{level+num} 레벨이 되었습니다.", value="\u200b", inline=False)
            view = ui.View(timeout=None)
            for i in range(len(item_percent)):
                if getSuccess(int(item_percent[i]), 100):
                    stone: dict = stone_data[item_code[i]]
                    min, max = item_amount[i].split("~")
                    total = random.randint(int(min), int(max))
                    if stone['name'] in adventrue_inventory[interaction.user.id]['names']:
                        for i in adventrue_inventory[interaction.user.id]['items']:
                            if i['name'] == stone['name']:
                                i['amount'] += total
                                adventrue_inventory[interaction.user.id]['weight'] += total * \
                                    stone['weight']
                                break
                    else:
                        stone.update({"amount": total})
                        adventrue_inventory[interaction.user.id]['items'].append(
                            stone)
                        adventrue_inventory[interaction.user.id]['weight'] += total * \
                            stone['weight']
                        adventrue_inventory[interaction.user.id]['names'].append(
                            stone['name'])
                    embed.add_field(
                        name=f"{stone['name']} {total}개 획득!", inline=False, value="\u200b")
            for i in range(len(util_percent)):
                if getSuccess(int(util_percent[i]), 100):
                    util: dict = util_data[util_code[i]]
                    cur.execute("SELECT item_id FROM user_item WHERE id = %s AND item_id = %s", (
                        interaction.user.id, util_code[i]))
                    isItem = cur.fetchone()
                    min, max = util_amount[i].split("~")
                    total = random.randint(int(min), int(max))
                    if not isItem:
                        item = [util_code[i]]
                        for value in util.values():
                            item.append(value)
                        item.append(total)
                        item.append(interaction.user.id)
                        cur.execute(
                            "INSERT INTO user_item(item_id,name,description,`rank`,price,trade,amount,id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", item)
                    else:
                        cur.execute(
                            "UPDATE user_item SET amount = amount + %s WHERE id = %s", (total, interaction.user.id))
                    con.commit()
                    embed.add_field(
                        name=f"{util['name']} {total}개 획득!", inline=False, value="\u200b")
            end_win = ui.Button(label="정비하기", style=ButtonStyle.green)
            end_win.callback = end_win_callback
            view.add_item(end_win)
            await interaction.response.edit_message(content="", embed=embed, view=view)

        async def lose(interaction: Interaction):  # 졌을때
            embed = discord.Embed(title="기절했습니다.")
            for i in adventrue_inventory[interaction.user.id]['items']:
                max = math.ceil(i['amount']/2)
                total = random.randint(0, max)
                i['amount'] -= total
                adventrue_inventory[interaction.user.id]['weight'] -= total*i['weight']
                if i['amount'] <= 0:
                    adventrue_inventory[interaction.user.id]['names'].remove(
                        i['name'])
                    adventrue_inventory[interaction.user.id]['items'].remove(i)
                if total > 0:
                    embed.add_field(
                        name=f"{i['name']}을 {total}개 잃어버렸습니다..", value="\u200b", inline=False)
            view = ui.View(timeout=None)
            end_win = ui.Button(label="정비하기", style=ButtonStyle.green)
            end_win.callback = end_win_callback
            view.add_item(end_win)
            await interaction.response.edit_message(content="", embed=embed, view=view)

        async def attack_callback(interaction: Interaction):  # 공격했을때
            if getSuccess(stat['crit'], 100):
                enemy['hp'] -= stat['power']+stat['power']*stat['crit_damage']
            else:
                enemy['hp'] -= stat['power']
            stat['hp'] -= enemy['power']
            if enemy['hp'] <= 0:
                if stat['hp'] >= enemy['hp']:
                    await win(interaction)
                else:
                    await lose(interaction)
            elif stat['hp'] <= 0:
                await lose(interaction)
            await try_callback(interaction)

        async def try_callback(interaction: Interaction):  # 도전하기
            embed = discord.Embed(title=enemy['name'])
            embed.add_field(name=f"{round(enemy['hp'],3)}❤", value="\u200b")
            embed.add_field(name=f"{enemy['power']}⚡", value="\u200b")
            embed.add_field(name=f"나", value="\u200b", inline=False)
            embed.add_field(name=f"{stat['hp']}❤", value='\u200b')
            embed.add_field(name=f"{stat['power']}⛏", value='\u200b')
            embed.set_thumbnail(url=enemy['url'])
            view = ui.View(timeout=None)
            attack = ui.Button(emoji="⛏", style=ButtonStyle.green)
            view.add_item(attack)
            attack.callback = attack_callback
            try:
                await interaction.response.edit_message(content="", embed=embed, view=view)
            except discord.errors.InteractionResponded:
                pass

        async def meet_enemy():  # 적과 만났을때
            embed = discord.Embed(title=enemy['name'])
            embed.add_field(name=f"{enemy['hp']}❤", value="\u200b")
            embed.add_field(name=f"{enemy['power']}⚡", value="\u200b")
            embed.set_thumbnail(url=enemy['url'])
            view = ui.View(timeout=None)
            try_button = ui.Button(
                label='도전하기', emoji='⛏', style=ButtonStyle.green)
            run_button = ui.Button(
                label='도망치기', emoji="👟", style=ButtonStyle.red)
            view.add_item(try_button)
            view.add_item(run_button)
            try_button.callback = try_callback
            run_button.callback = run_callback
            await interaction.response.edit_message(embed=embed, view=view)
        await meet_enemy()

    async def stop_callback(interaction: Interaction):  # 탐험중단
        embed = discord.Embed(title="탐험 요약")
        result = 0
        for i in adventrue_inventory[interaction.user.id]['items']:
            result += i['amount']*i['price']
            embed.add_field(name=i['name'], value=f"{i['amount']}개")
        embed.set_footer(text=f"예상 수익 : {result}골드")
        cur.execute("UPDATE user_info SET money = money + %s WHERE id = %s",
                    (result, interaction.user.id))
        con.commit()
        mining_dic[interaction.user.id] = False
        return await interaction.response.edit_message(content="", embed=embed, view=None)

    async def start():  # 기본 정비 함수
        rest = discord.Embed(title="정비")
        weight = abs(
            round(adventrue_inventory[interaction.user.id]['weight'], 2))
        disabled = round(stat['str'], 2) < weight-0.001
        rest.add_field(
            name=f"가방(용량:{weight}/{round(stat['str'],2)})", value="\u200b",)
        rest.add_field(name=광산.name, value='\u200b', inline=False)
        if disabled:
            rest.set_footer(text="가방이 너무 무겁습니다!")
        view = ui.View(timeout=None)
        remove = ui.Button(label="아이템버리기", emoji="🗑", style=ButtonStyle.gray,
                           disabled=(weight == 0.0), row=2)
        go = ui.Button(label="탐험진행", emoji='⛏',
                       disabled=disabled, style=ButtonStyle.green)
        stop = ui.Button(label="탐험중단", emoji="💨",
                         disabled=disabled, style=ButtonStyle.red)
        remove.callback = remove_callback
        go.callback = go_callback
        stop.callback = stop_callback
        for i in [remove, go, stop]:
            view.add_item(i)
        try:
            await interaction.response.send_message(embed=rest, view=view, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=rest, view=view)
    await start()
client.run("ODc0NjE1MDAxNTI3MjM0NTYw.GANMZ1.dOH8tKjN6wi8-62MRGCS-J3yB3_CvXoR3YdVG8")
