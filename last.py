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
import os
# from dotenv import load_dotenv

# load_dotenv()

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
            isExistItem(i[0], 2)
            if weekday == 3:
                isExistItem(i[0], 4)
                cur.execute(
                    "UPDATE user_item SET amount = 1 WHERE item_id = %s", 4)
        cur.execute("UPDATE user_item SET amount = 1 WHERE item_id = %s", 2)

        con.commit()

    @tasks.loop(hours=1)
    async def reconnect_db(self):
        cur = con.cursor()
        cur.execute("SELECT * FROM user_info")

    async def change_message(self):
        while not client.is_closed():
            for i in ['개발', '0.0.1a버전 관리', '버그 제보 부탁']:
                await client.change_presence(status=discord.Status.online, activity=discord.Game(i))
                await asyncio.sleep(5)

    async def on_ready(self):
        await self.wait_until_ready()
        setup()
        self.reward.start()
        # guild = discord.Object(id=GUILD_ID)
        # tree.clear_commands(
        #     guild=guild, type=discord.AppCommandType.chat_input)
        # await tree.sync(guild=guild)
        print(f"{self.user} 에 로그인하였습니다!")
        await self.change_message()


intents = discord.Intents.all()
client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)
con = pymysql.connect(host=os.environ['host'], password=os.environ['password'],
                      user=os.environ['user'], port=int(os.environ['port']), database=os.environ['database'], charset='utf8')
adventrue_inventory = {}
weapon_rein_dic = {}
mining_dic = {}
cnt = {}


class reinEnum(Enum):
    무기 = 0
    투구 = 1
    갑옷 = 2
    장갑 = 3
    신발 = 4


class makeItemEnum(Enum):
    무기 = "weapon"
    방어구 = "wear"
    기타 = "item"


class miningEnum(Enum):
    기본광산 = 1
    광산 = 2
    요일광산EASY = -datetime.datetime.today().weekday()
    주간광산EASY = -8


class statusEnum(Enum):
    힘 = 'power'
    체력 = 'hp'
    중량 = 'str'
    크리티컬데미지 = 'crit_damage'


class rankingEnum(Enum):
    레벨 = 'level'
    자산 = 'money'


def isExistItem(id: int, code: int):
    cur = con.cursor()
    utils = getJson('./json/util.json')
    util = utils[str(code)]
    cur.execute(
        "SELECT * FROM user_item WHERE id = %s AND item_id = %s", (id, code))
    if not cur.fetchone():
        cur.execute("INSERT INTO user_item VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                    (code, util['name'], util['description'], util['rank'], util['price'], util['trade'], 0, id))
    con.commit()
    cur.close()


def getPart(part: int):
    parts = ['', '투구', '갑옷', '장갑', '신발']
    return parts[part]


def translateName(name: str):
    column = ['power', 'hp', 'str', 'crit', 'crit_damage', 'damage']
    korean = ['힘', '체력', '중량', '크리티컬 확률', '크리티컬 데미지', '데미지']
    if name in column:
        return korean[column.index(name)]
    elif name in korean:
        return column[korean.index(name)]


def getPartRein(part: int):
    parts = ['힘', '체력', '중량', '힘', '체력']
    return parts[part]


def getItem(name: str, index: int, id: int, cnt: int):
    cur = con.cursor()
    items = getJson('./json/makeItem.json')
    utils = getJson('./json/util.json')
    item = items['item'][index][name]
    util = utils[item['code']]
    cur.execute(
        "SELECT COUNT(*) FROM user_item WHERE id = %s AND item_id = %s", (id, item['code']))
    if cur.fetchone()[0]:
        cur.execute(
            "UPDATE user_item SET amount = amount + %s WHERE item_id = %s AND id = %s", (cnt, item['code'], id))
    else:
        cur.execute("INSERT INTO user_item VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                    (item['code'], name, util['description'], util['rank'], util['price'], util['trade'], cnt, id))
    con.commit()
    cur.close()


def getWear(name: str, index: int, id: int):
    cur = con.cursor()
    items = getJson("./json/makeItem.json")
    item = items['wear'][index][name]
    a, b = item['power'].split(" ")
    power = random.randint(int(a), int(b))
    a, b = item['hp'].split(" ")
    hp = random.randint(int(a), int(b))
    a, b = item['str'].split(" ")
    str = random.randint(int(a), int(b))
    cur.execute(
        "INSERT INTO user_wear(name,upgrade,`rank`,level,power,hp,`str`,collection,part,wear,trade,id,url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (name, 0, item['rank'], item['level'], power, hp, str, item['collection'], item['part'], 0, item['trade'], id, item['url']))
    con.commit()
    cur.close()


def getWeapon(name: str, index: int, id: int):
    cur = con.cursor()
    items = getJson("./json/makeItem.json")
    item = items['weapon'][index][name]
    a, b = item['power'].split(" ")
    power = random.randint(int(a), int(b))
    a, b = item['damage'].split(" ")
    damage = random.randint(int(a), int(b))
    cur.execute(
        "INSERT INTO user_weapon(name,upgrade,`rank`,level,power,damage,wear,trade,id,url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (item['name'], 0, item['rank'], item['level'], power, damage, 0, item['trade'], id, item['url']))
    con.commit()
    cur.close()


def useNotTradeFirst(name: str, amount: int, id: int):
    cur = con.cursor()
    cur.execute(
        "SELECT amount FROM user_item WHERE id = %s AND name = %s ORDER BY trade ASC", (id, name))
    items = cur.fetchall()
    if len(items) == 2:
        if items[0][0] <= amount:
            cur.execute(
                "UPDATE user_item SET amount = 0 WHERE id = %s AND trade = 0 AND name = %s", (id, name))
            cur.execute("UPDATE user_item SET amount = amount - %s WHERE id = %s AND trade = 1 AND name = %s ",
                        (amount-items[0], id, name))
        else:
            cur.execute(
                "UPDATE user_item SET amount = amount - %s WHERE id = %s AND trade = 0 AND name = %s", (amount, id, name))
    else:
        cur.execute(
            "UPDATE user_item SET amount = amount - %s WHERE id = %s AND name = %s", (amount, id, name))
    con.commit()
    cur.close()


def block_exp(level: int, exp: int):
    guild = client.get_guild(884259665964314655)
    name = ["0_", "1_", "2_", "3_", "4_", "5_", "6_", "7_", "8_", "9_", "10"]
    block = [discord.utils.get(guild.emojis, name=i) for i in name]
    level_info = getJson('./json/level.json')
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
    level_info = getJson('./json/level.json')
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
    if not values:
        return False
    dictionary = {}
    for i in range(len(keys)):
        dictionary.update({keys[i]: values[i]})
    return dictionary


def getOption(option: str):
    power = hp = str = crit = damage = 0
    if option:
        for i in option.split(" "):
            number = int(i[1:])
            if i[0] == 'p':
                power += number
            elif i[0] == 'h':
                hp += number
            elif i[0] == 'a':
                hp += number
                str += number
                power += number
                crit += number
                damage += number
            elif i[0] == "c":
                crit += number
            elif i[0] == "d":
                damage += number
    return {'power': power, 'hp': hp, 'str': str, 'crit': crit, 'damage': damage/100}


def authorize(id: int):  # 유저 정보가 있으면 True
    cur = con.cursor()
    cur.execute("SELECT * FROM user_info WHERE id = %s", id)
    return cur.fetchone() != None


def getJson(url: str):
    file = open(url, 'r', encoding="utf-8")
    data = json.load(file)
    return data


def getStatus(id: int):  # 유저 스텟 불러오기
    cur = con.cursor()
    # 갑옷 힘,체력,중량 불러오기
    cur.execute(
        "SELECT SUM(power),SUM(hp),SUM(str/10) FROM user_wear WHERE id=%s AND wear = 1 ", id)
    wear = makeDictionary(['power', 'hp', 'str'], cur.fetchone())
    cur.execute("""
                SELECT SUM(A.hp),SUM(A.power),SUM(A.str),SUM(A.crit),SUM(A.crit_damage/100),SUM(A.damage/100) FROM collection_effect A JOIN (SELECT collection as col,COUNT(collection) as cnt FROM user_wear WHERE wear=1 AND id=%s GROUP BY collection) B ON B.col = A.collection WHERE B.cnt>=A.value""", id)
    collection = makeDictionary(
        ['hp', 'power', 'str', 'crit', 'crit_damage', 'damage'], cur.fetchone())
    cur.execute(
        "SELECT power,damage/100,`option` FROM user_weapon WHERE id=%s AND wear = 1", id)
    weapon = makeDictionary(['power', 'damage', 'option'], cur.fetchone())
    option = getOption(weapon['option'])
    cur.execute(
        "SELECT power,hp*3,str/10,crit,crit_damage/100,point FROM user_stat WHERE id=%s", id)
    stat = makeDictionary(['power', 'hp', 'str', 'crit',
                          'crit_damage', 'point'], cur.fetchone())
    final = {'power': 0, 'hp': 25, "str": 0,
             'damage': 0, 'crit': 0, 'crit_damage': 0, 'maxhp': 0, 'point': 0}
    for key, value in chain(wear.items(), weapon.items(), option.items(), stat.items(), collection.items()):
        if value:
            final[key] += value

    final['maxhp'] = final['hp']
    final['power'] *= final['damage']
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
    # user_wear 유저 갑옷(아이템아이디,이름,강화,등급,레벨,힘,체력,무게,컬렉션,착용부위,착용여부,거래여부,아이디,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_wear 
                (item_id INT PRIMARY KEY AUTO_INCREMENT,name TEXT,upgrade INT,`rank` TEXT,level INT,power INT,hp INT,str INT,collection TEXT , part INT,wear BOOLEAN, trade BOOLEAN,id TEXT,url TEXT)""")
    # user_item 유저 아이템(아이템아이디,이름,등급,가격,설명,거래여부,아이디,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS user_item
                (item_id INT, name TEXT,`rank` TEXT, price INT,description TEXT,trade BOOLEAN,amount INT,id TEXT)""")
    # enemy 광석(이름,힘,체력,층,드롭아이템코드,드롭아이템확률,드롭아이템개수,유틸아이템코드,유틸아이템드롭확률,유틸아이템드롭개수,이미지)
    cur.execute("""CREATE TABLE IF NOT EXISTS enemy
                (name TEXT,power INT,hp INT,floor INT,exp INT,item_code TEXT,item_percent TEXT,item_amount TEXT,util_code TEXT,util_percent TEXT,util_amount TEXT,url TEXT)""")
    # collection_effect 컬렉션효과(컬렉션,체력,무게,크리티컬,힘,개수)
    cur.execute("""CREATE TABLE IF NOT EXISTS collection_effect
                (collection TEXT, hp INT, `str` INT, crit INT, power INT,crit_damage INT,damage INT, value INT)""")


@tree.command(name="커맨드싱크", description="제작자 전용 명령어")
async def sync(interaction: Interaction):
    if interaction.user.id == 432066597591449600:
        guild = discord.Object(id=interaction.guild.id)
        tree.clear_commands(
            guild=guild, type=discord.AppCommandType.chat_input)
        await tree.sync(guild=guild)
        await tree.sync()


@tree.command(name="세트효과", description="현재 적용받는 세트효과를 보여줍니다.")
async def show_collection(interaction: Interaction):
    cur = con.cursor()
    cur.execute("""SELECT A.collection,A.value,A.hp,A.power,A.str,A.crit,A.crit_damage/100,A.damage/100 FROM 
                collection_effect A JOIN 
                (SELECT collection as col,COUNT(collection) as cnt FROM user_wear
                WHERE wear=1 AND id=%s GROUP BY collection)
                B ON B.col = A.collection WHERE B.cnt>=A.value""", interaction.user.id)
    embed = discord.Embed(title="세트효과")
    values = cur.fetchall()
    for i in values:
        text = ''
        item = makeDictionary(
            ['collection', 'value', 'hp', 'power', 'str', 'crit', 'crit_damage', 'damage'], i)
        for j in ['hp', 'power', 'str', 'crit', 'crit_damage', 'damage']:
            if item[j] != 0:
                text += f"{translateName(j)} {'+' if item[j]>0 else ''}{item[j]}  "
        embed.add_field(
            name=f"{item['collection']} {item['value']}세트", value=text, inline=False)
    if not values:
        embed.add_field(name="세트효과를 받지 않고 있어요!", value='\u200b', inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="스텟초기화", description="스텟초기화")
async def reset_stat(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    cur = con.cursor()
    cur.execute("SELECT amount FROM user_item WHERE id = %s AND item_id = %s",
                (interaction.user.id, 8))
    amount = cur.fetchone()
    if not amount:
        return await interaction.response.send_message("`스텟 초기화 스크롤`이 없습니다.", ephemeral=True)
    else:
        if not amount[0]:
            return await interaction.response.send_message("`스텟 초기화 스크롤`이 없습니다.", ephemeral=True)
        cur.execute(
            "UPDATE user_item SET amount = amount - 1 WHERE id = %s AND item_id = %s", (interaction.user.id, 8))
        cur.execute("SELECT level FROM user_info WHERE id = %s",
                    interaction.user.id)
        level = cur.fetchone()[0]
        cur.execute("UPDATE user_stat SET power = 1 , str = 5, hp = 5, crit_damage=50 ,point = %s WHERE id = %s",
                    (level*LEVEL_PER_STAT, interaction.user.id))
        con.commit()
        await interaction.response.send_message("성공적으로 스텟을 초기화 했습니다.", ephemeral=True)


@tree.command(name="제작소", description="아이템 제작소")
async def makeItem(interaction: Interaction, 종류: makeItemEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    items: dict = getJson("./json/makeItem.json")
    utils: dict = getJson("./json/util.json")
    category = 종류.value
    page = {}
    page[interaction.user.id] = 0
    cur = con.cursor()
    cnt = {}
    cnt[interaction.user.id] = 1

    async def setup(interaction: Interaction):
        embed = discord.Embed(title=f"{종류.name} 제작소")
        view = ui.View(timeout=None)
        options = []
        for index in range(page[interaction.user.id]*10, (page[interaction.user.id]+1)*10):
            if len(items[category]) <= index:
                break
            item = items[category][index]
            for i in item:
                if category == "wear":
                    option = SelectOption(
                        label=f"Lv.{item[i]['level']} {i}", description=f"{item[i]['collection']} 세트", value=index)
                elif category == "item":
                    option = SelectOption(
                        label=i, description=f"{'거래가능' if utils[item[i]['code']]['trade'] else '거래불가'}", value=index)
                else:
                    option = SelectOption(
                        label=f"Lv.{item[i]['level']} {i}", value=index)
                options.append(option)
        if len(items[category]) > (page[interaction.user.id]+1)*10:
            options.append(SelectOption(label="다음페이지", value=-1))
        if not page[interaction.user.id] == 0:
            options.append(SelectOption(label="이전페이지", value=-2))
        select = ui.Select(placeholder="아이템을 선택해주세요.", options=options)

        async def select_callback(interaction: Interaction):
            index = int(select.values[0])
            if index == -1:
                page[interaction.user.id] += 1
                await interaction.response.edit_message(content="")
                return await setup(interaction)
            if index == -2:
                page[interaction.user.id] -= 1
                await interaction.response.edit_message(content="")
                return await setup(interaction)

            async def makeDetail(interaction: Interaction):
                disabled = False
                req_items = []
                req_amounts = []

                for i in items[category][index]:
                    item = items[category][index][i]
                    name = i
                    embed = discord.Embed(title=i)
                    for j in item['required']:
                        req_items.append(utils[j]['name'])
                        req_amounts.append(
                            item['required'][j])
                        embed.add_field(
                            name="재료", value=f"{utils[j]['name']} {item['required'][j]*cnt[interaction.user.id]} 개")
                        cur.execute(
                            "SELECT SUM(amount) FROM user_item WHERE name = %s AND id = %s", (utils[j]['name'], interaction.user.id))
                        allitem = cur.fetchone()
                        if allitem[0] == None:
                            disabled = True
                        else:
                            if allitem[0] < item['required'][j]*cnt[interaction.user.id]:
                                disabled = True
                    percent = item['percent']
                    embed.set_footer(
                        text=f"성공확률 : {item['percent']}%")
                view = ui.View(timeout=None)
                makebutton = ui.Button(
                    label="제작하기", style=ButtonStyle.green, disabled=disabled)
                backbutton = ui.Button(label="제작취소", style=ButtonStyle.red)

                view.add_item(makebutton)
                view.add_item(backbutton)

                async def back_callback(interaction: Interaction):
                    await interaction.response.edit_message(content="")
                    await setup(interaction)

                async def amount_callback(interaction: Interaction):
                    class amountModal(ui.Modal, title=f"개수변경"):
                        answer = ui.TextInput(
                            label="제작할 숫자를 적어주세요.",
                            style=TextStyle.short,
                            placeholder="숫자만 적어주세요.",
                            max_length=3)

                        async def on_submit(self, interaction: Interaction):
                            try:
                                value = int(self.answer.value)
                            except:
                                pass
                            if value < 0:
                                pass
                            cnt[interaction.user.id] = value
                            await makeDetail(interaction)
                    await interaction.response.send_modal(amountModal())

                async def make_callback(interaction: Interaction):
                    for i in range(len(req_amounts)):
                        useNotTradeFirst(
                            req_items[i], req_amounts[i]*cnt[interaction.user.id], interaction.user.id)
                    if category != "item":
                        if getSuccess(percent, 100):
                            if category == "wear":
                                getWear(name, index, interaction.user.id)
                            if category == "weapon":
                                getWeapon(name, index, interaction.user.id)
                            return await interaction.response.edit_message(content="제작 성공!", embed=None, view=None)
                        else:
                            return await interaction.response.edit_message(content="제작 실패...", embed=None, view=None)
                    else:
                        real_cnt = 0
                        for i in range(cnt[interaction.user.id]):
                            if getSuccess(percent, 100):
                                real_cnt += 1
                        getItem(name, index, interaction.user.id, real_cnt)
                        return await interaction.response.edit_message(content=f"{cnt[interaction.user.id]}회 중 {real_cnt}번 성공!", embed=None, view=None)

                makebutton.callback = make_callback
                backbutton.callback = back_callback
                if category == "item":

                    embed.add_field(
                        name=f"제작개수 : {cnt[interaction.user.id]}", value='\u200b', inline=False)
                    amountbutton = ui.Button(label="개수 변경", row=2)
                    view.add_item(amountbutton)
                    amountbutton.callback = amount_callback
                await interaction.response.edit_message(embed=embed, view=view)
            await makeDetail(interaction)

        select.callback = select_callback
        view.add_item(select)
        try:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except:
            await interaction.edit_original_response(embed=embed, view=view)

    await setup(interaction)


@tree.command(name="캐릭터삭제", description="캐릭터 삭제")
async def deleteUser(interaction: Interaction):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)

    class deleteModal(ui.Modal, title="캐릭터삭제"):
        answer = ui.TextInput(label="캐릭터를 한번 삭제하면 되돌릴 수 없어요.",
                              placeholder="'캐릭터삭제' 라고 적어주세요.")

        async def on_submit(self, interaction: Interaction):
            if self.answer.value == "캐릭터삭제":
                cur = con.cursor()
                cur.execute("DELETE FROM user_info WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_stat WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_wear WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_weapon WHERE id = %s",
                            interaction.user.id)
                cur.execute("DELETE FROM user_item WHERE id = %s",
                            interaction.user.id)
                return await interaction.response.send_message("성공적으로 캐릭터를 삭제했습니다.", ephemeral=True)
            else:
                return await interaction.response.send_message("캐릭터 삭제 실패", ephemeral=True)
    await interaction.response.send_modal(deleteModal())


@tree.command(name="기타아이템넣기", description="개발자전용명령어")
async def put_util(interaction: Interaction, 코드: int, 개수: int, 유저: discord.Member):
    if not interaction.user.id == 432066597591449600:
        return
    cur = con.cursor()
    cur.execute("SELECT nickname FROM user_info WHERE id = %s", 유저.id)
    if not cur.fetchone():
        return
    if 유저.id == 874615001527234560:
        cur.execute("SELECT id FROM user_info")
        users = cur.fetchall()
        for i in users:
            isExistItem(i[0], 코드)
        cur.execute(
            "UPDATE user_item SET amount = amount + %s WHERE item_id = %s",
            (개수, 코드))
    else:
        isExistItem(유저.id, 코드)
        cur.execute("UPDATE user_item SET amount = amount+ %s WHERE id = %s AND item_id = %s",
                    (개수, 유저.id, 코드))
    con.commit()
    cur.close()
    return await interaction.response.send_message("성공적으로 넣었습니다", ephemeral=True)


@tree.command(name="강화", description="아이템강화")
async def reinforce_weapon(interaction: Interaction, 종류: reinEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    try:
        if weapon_rein_dic[interaction.user.id]:
            return await interaction.response.send_message("강화할 수 없습니다.", ephemeral=True)
    except KeyError:
        weapon_rein_dic[interaction.user.id] = True
    else:
        weapon_rein_dic[interaction.user.id] = True
    if not authorize(interaction.user.id):
        weapon_rein_dic[interaction.user.id] = False
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    cur = con.cursor()
    reinforce_info = getJson('./json/reinforce.json')
    category = 'weapon' if 종류.value == 0 else 'wear'

    async def setup(interaction: Interaction):
        disabled = False
        try:
            item['upgrade']
        except:
            if 종류.name == "무기":
                cur.execute("SELECT upgrade,`rank`,name FROM user_weapon WHERE id = %s AND wear = 1",
                            interaction.user.id)
                item = makeDictionary(
                    ['upgrade', 'rank', 'name'], cur.fetchone())
            else:
                cur.execute("SELECT upgrade,`rank`,name FROM user_wear WHERE id = %s AND wear = 1 AND part = %s",
                            (interaction.user.id, 종류.value))
                item = makeDictionary(
                    ['upgrade', 'rank', 'name'], cur.fetchone())
            if not item:
                weapon_rein_dic[interaction.user.id] = False
                return await interaction.response.send_message("아이템을 장착하지 않았습니다.", ephemeral=True)
        if item['upgrade'] == 25:
            con.commit()
            weapon_rein_dic[interaction.user.id] = False
            try:
                await interaction.response.send_message("이미 25강화를 완료한 아이템입니다.", ephemeral=True)
            except discord.errors.InteractionResponded:
                await interaction.edit_original_response(content="25강화를 완료 했습니다.")
            return
        embed = discord.Embed(
            title=f"{item['name']}[{item['rank']}] +{item['upgrade']} > +{item['upgrade']+1} 강화")
        req_percent = reinforce_info['percent'][str(item["upgrade"]+1)]
        req_money = reinforce_info['money'][item['rank']][str(
            item['upgrade']+1)]
        req_item = reinforce_info['item'][item['rank']][str(item['upgrade']+1)]
        stat = reinforce_info[category][item['rank']][str(item['upgrade']+1)]
        embed.add_field(
            name=f"강화 확률 : {req_percent}%", value="\u200b")
        embed.add_field(
            name=f"강화 비용 : {req_money}💰", value="\u200b")
        cur.execute("SELECT money FROM user_info WHERE id = %s",
                    interaction.user.id)
        money = cur.fetchone()[0]
        if money < req_money:
            disabled = True
        utils = []
        names = []
        amounts = []
        embed.add_field(name='\u200b', value='\u200b')
        for i in req_item.split(","):
            util, amount = i.split("/")
            embed.add_field(name=f"강화재료 : {util} {amount}개", value="\u200b")
            cur.execute("SELECT amount FROM user_item WHERE id = %s AND name = %s ORDER BY trade ASC",
                        (interaction.user.id, util))
            names.append(util)
            amounts.append(int(amount))
            user_amount = 0
            dump = []
            for j in cur.fetchall():
                user_amount += j[0]
                dump.append(j[0])
            utils.append(dump)
            if user_amount < amounts[-1]:
                disabled = True
        stat_name = getPartRein(종류.value)
        embed.set_footer(
            text=f"강화 성공시 {stat_name} + {stat}")
        view = ui.View(timeout=None)
        button = ui.Button(label="강화하기", disabled=disabled,
                           style=ButtonStyle.green)
        if disabled:
            weapon_rein_dic[interaction.user.id] = False
        view.add_item(button)
        back = ui.Button(label="끝내기", style=ButtonStyle.red)
        view.add_item(back)

        async def back_callback(interacation: Interaction):
            weapon_rein_dic[interaction.user.id] = False
            await interacation.response.edit_message(content=".", embed=None, view=None)
            await interacation.delete_original_response()

        async def button_callback(interaction: Interaction):
            cur = con.cursor()
            for i in range(len(names)):
                useNotTradeFirst(names[i], amounts[i], interaction.user.id)
            cur.execute("UPDATE user_info SET money = money - %s WHERE id = %s",
                        (req_money, interaction.user.id))
            if getSuccess(req_percent, 100):
                if 종류.name == "무기":
                    cur.execute("UPDATE user_weapon SET upgrade = upgrade + 1 , power = power + %s WHERE id = %s AND wear = 1 ",
                                (stat, interaction.user.id))
                else:
                    real_name = translateName(stat_name)
                    cur.execute(
                        f"UPDATE user_wear SET upgrade = upgrade +1, {real_name} = {real_name} + {stat} WHERE id = {interaction.user.id} AND wear = 1 AND part = {종류.value} ")
                item['upgrade'] += 1
                if item["upgrade"] >= 20:
                    await interaction.channel.send(f"`{interaction.user.display_name}`님이 `{item['name']} +{item['upgrade']}` 강화에 성공했습니다!")
                await interaction.response.edit_message(content="강화에 성공했습니다!", view=None, embed=None)
            else:
                await interaction.response.edit_message(content="강화에 실패했습니다!", view=None, embed=None)
            con.commit()
            await asyncio.sleep(2)
            await setup(interaction)
        back.callback = back_callback
        button.callback = button_callback
        try:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)
    await setup(interaction)


@tree.command(name="랭킹", description="랭킹")
async def ranking(interaction: Interaction, 종류: rankingEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    cur = con.cursor()
    embed = discord.Embed(title=f'{종류.name} 랭킹')
    if 종류.value == "level":
        cur.execute(
            "SELECT nickname,level,exp FROM user_info ORDER BY level DESC, exp DESC, create_at ASC LIMIT 0,20 ")
        for i in cur.fetchall():
            block, require = block_exp(i[1], i[2])
            embed.add_field(
                name=f"{i[0]} Lv.{i[1]} ({i[2]}/{require})", value=block, inline=False)
        cur.execute(
            "SELECT DENSE_RANK() OVER (ORDER BY level DESC, exp DESC, create_at ASC) RANKING FROM user_info WHERE id = %s", interaction.user.id)
    elif 종류.value == "money":
        cur.execute(
            "SELECT nickname,money FROM user_info ORDER BY money DESC, create_at ASC LIMIT 0,20")
        for i in cur.fetchall():
            money = format(i[1], ",")
            embed.add_field(name=f"{i[0]} {money}💰",
                            value="\u200b", inline=False)
        cur.execute(
            "SELECT DENSE_RANK() OVER (ORDER BY money DESC, create_at ASC) RANKING FROM user_info WHERE id= %s", interaction.user.id)
    embed.set_footer(text=f"내 순위 : {cur.fetchone()[0]}위")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="아이템거래", description="거래")
async def trade(interaction: Interaction, 유저: discord.Member, 종류: makeItemEnum, 코드: int, 개수: int):
    if not authorize(interaction.user.id) or not authorize(유저.id):
        return await interaction.response.send_message("`회원가입`이 필요하거나 상대방이 가입하지 않았습니다. ", ephemeral=True)
    cur = con.cursor()
    category = 종류.value
    item_data: dict = getJson('./json/util.json')
    if category == "item":
        cur.execute("SELECT trade,amount FROM user_item WHERE id = %s AND item_id = %s",
                    (interaction.user.id, 코드))
        try:
            canTrade, amount = cur.fetchone()
        except:
            return await interaction.response.send_message("아이템이 없습니다", ephemeral=True)
    else:
        cur.execute(f"SELECT trade FROM user_{category} WHERE id = {interaction.user.id} AND item_id = {코드} ",
                    )
        try:
            canTrade = cur.fetchone()[0]
        except:
            return await interaction.response.send_message("아이템이 없습니다.", ephemeral=True)
    if canTrade:
        if category == "item":
            if amount >= 개수:
                cur.execute(
                    "UPDATE user_item SET amount = amount - %s WHERE id = %s AND item_id = %s", (개수, interaction.user.id, 코드))
                isExistItem(interaction.user.id, 코드)
                cur.execute(
                    "UPDATE user_item SET amount = amount + %s WHERE id = %s AND item_id = %s", (개수, 유저.id, 코드))
                con.commit()
                return await interaction.response.send_message(f"`{유저.display_name}`님에게 `{item_data[str(코드)]['name']}`를 `{개수}` 개 전달했습니다.", ephemeral=True)
            else:
                return await interaction.response.send_message("아이템이 부족합니다.", ephemeral=True)
        elif category != "item":
            cur.execute(
                f"UPDATE user_{category} SET id = {유저.id}, wear=0 WHERE item_id = {코드}")
            con.commit()
            cur.execute(
                f"SELECT name FROM user_{category} WHERE item_id = {코드}")
            return await interaction.response.send_message(f"`{유저.display_name}`님에게 `{cur.fetchone()[0]}`를 전달했습니다.", ephemeral=True)

    else:
        return await interaction.response.send_message("거래할 수 없는 아이템 입니다.", ephemeral=True)


@tree.command(name="스텟", description="스테이터스")
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


@tree.command(name="강화초기화", description="운영자를 부르세요.")
async def reinforceReset(interaction: Interaction, 유저: discord.Member):
    if interaction.user.id == 432066597591449600:
        reinforce_weapon[유저.id] = False
    else:
        author = await client.fetch_user(432066597591449600)
        await author.send(f"{interaction.user}님의 호출이에요.")


@tree.command(name="회원가입", description="회원가입입니다.")
async def register(interaction: Interaction, 닉네임: str):
    cur = con.cursor()
    if authorize(interaction.user.id):
        await interaction.response.send_message("아이디가 있습니다.", ephemeral=True)
    else:
        cur.execute("""INSERT INTO user_info(nickname,id,exp,level,money,role,create_at,mooroong) 
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""", (닉네임, interaction.user.id, 0, 1, 100, 0, datetime.datetime.today(), 0))
        cur.execute("INSERT INTO user_stat(id,power,hp,str,crit,crit_damage,point) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (interaction.user.id, 1, 5, 5, 5, 50, 0))
        cur.execute("""INSERT INTO user_weapon(name,upgrade,`rank`,level,power,damage,wear,trade,id,url)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    ('기본 곡괭이', 0, 'F', 1, 5, 100, 1, 0, interaction.user.id, "https://cdn.discordapp.com/attachments/988424121878741022/1040198148661973022/pickaxe1.png"))
        con.commit()
        await interaction.response.send_message("아이디가 생성되었습니다.", ephemeral=True)


@tree.command(name="정보", description="정보")
async def info(interaction: Interaction, 유저: discord.Member = None):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    if 유저:
        if not authorize(유저.id):
            return await interaction.response.send_message("해당 유저는 회원가입 하지 않았습니다.", ephemeral=True)

    async def setting(interaction: Interaction):
        cur = con.cursor()
        id = interaction.user.id if not 유저 else 유저.id
        cur.execute(
            "SELECT nickname,exp,level,money,create_at,mooroong FROM user_info WHERE id=%s", id)
        user = makeDictionary(
            ['nickname', 'exp', 'level', 'money', 'create_at', 'moorong'], cur.fetchone())
        stat = getStatus(id)
        view = ui.View(timeout=None)
        button = ui.Button(label="새로고침")
        view.add_item(button)
        button.callback = setting
        embed = discord.Embed(title=user['nickname'])
        string_block, level_info = block_exp(user['level'], user['exp'])
        money = format(user['money'], ",")
        exp = format(user['exp'], ",")
        level_info_comma = format(level_info, ",")
        embed.add_field(
            name=f"Lv. {user['level']} {exp}/{level_info_comma}({round(user['exp']/level_info*100)}%)", value=string_block, inline=True)
        embed.add_field(name=f"돈 : \n{money}💰", value="\u200b", inline=True)
        embed.add_field(
            name=f"무릉 : \n{user['moorong']}층", value="\u200b", inline=True)
        embed.add_field(name=f"힘 : \n{round(stat['power'],2)}", value='\u200b')
        # embed.add_field(
        #     name=f"데미지배수 : \nx{round(stat['damage'],2)}", value="\u200b")
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


@tree.command(name="인벤토리", description="인벤토리")
async def inventory(interaction: Interaction, 종류: makeItemEnum):
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    page = {}
    category: str = 종류.value
    page[interaction.user.id] = 0
    index = {}

    async def next_callback(interaction: Interaction):
        page[interaction.user.id] += 1
        await setup(interaction)

    async def previous_callback(interaction: Interaction):
        page[interaction.user.id] -= 1
        await setup(interaction)

    async def detail_callback(interaction: Interaction):
        cur = con.cursor()

        if category == "wear":
            cur.execute(
                "SELECT item_id,name,upgrade,`rank`,level,power,hp,str,collection,part,wear,trade,url FROM user_wear WHERE id=%s ORDER BY item_id ASC LIMIT %s, 1",
                (interaction.user.id, page[interaction.user.id]*10+index[interaction.user.id]))
            wear: dict = makeDictionary(['item_id', 'name', 'upgrade', 'rank', 'level', 'power',
                                         'hp', 'str', 'collection', 'part', 'wear', 'trade', 'url'], cur.fetchone())
            cur.execute(
                "SELECT power,hp,str FROM user_wear WHERE id=%s AND part=%s AND wear=1", (interaction.user.id, wear['part']))
            gap = {'power': 0, "hp": 0, "str": 0}
            check = cur.fetchone()
            if check:
                gap['power'] = check[0]
                gap['hp'] = check[1]
                gap['str'] = check[2]
            cur.execute("SELECT level FROM user_info WHERE id = %s",
                        interaction.user.id)
            level = cur.fetchone()[0]
            embed = discord.Embed(
                title=f"Lv.{wear['level']} {wear['name']}[{wear['rank']}] +{wear['upgrade']} ({'거래가능' if wear['trade'] else '거래불가'}) {'착용중' if wear['wear'] else ''}")
            embed.add_field(
                name=f"힘 : {wear['power']}({'+' if wear['power']-gap['power']>0 else ''}{wear['power']-gap['power']})", value="\u200b")
            embed.add_field(
                name=f"체력 : {wear['hp']}({'+' if wear['hp']-gap['hp']>0 else ''}{wear['hp']-gap['hp']})", value='\u200b')
            embed.add_field(
                name=f"중량 : {wear['str']}({'+' if wear['str']-gap['str']>0 else ''}{wear['str']-gap['str']})", value='\u200b')
            embed.add_field(
                name=f"착용부위 : {getPart(wear['part'])}", value='\u200b')
            embed.add_field(name=f"{wear['collection']} 세트", value='\u200b')
            embed.set_thumbnail(url=wear['url'])
            embed.set_footer(text=f"아이템 코드 : {wear['item_id']}")
            view = ui.View()
            equip = ui.Button(label="착용하기", style=ButtonStyle.green,
                              disabled=level < wear['level'])
            back = ui.Button(label="돌아가기", style=ButtonStyle.red)
            view.add_item(equip)
            view.add_item(back)

            async def equip_callback(interaction: Interaction):
                cur.execute("UPDATE user_wear SET wear = 0 WHERE part = %s AND wear = 1 AND id = %s",
                            (wear['part'], interaction.user.id))
                cur.execute(
                    "UPDATE user_wear SET wear = 1 WHERE item_id = %s", wear['item_id'])
                con.commit()
                await detail_callback(interaction)
            equip.callback = equip_callback
            back.callback = setup
            await interaction.response.edit_message(embed=embed, view=view)

        if category == "weapon":
            cur.execute(
                "SELECT item_id,name,upgrade,`rank`,level,power,damage/100,`option`,wear,trade,url FROM user_weapon WHERE id = %s ORDER BY item_id ASC LIMIT %s,1 ",
                (interaction.user.id, index[interaction.user.id]))
            weapon = makeDictionary(['item_id', 'name', 'upgrade', 'rank', 'level',
                                    'power', 'damage', 'option', 'wear', 'trade', 'url'], cur.fetchone())
            cur.execute(
                "SELECT power,damage/100 FROM user_weapon WHERE id=%s AND wear=1", (interaction.user.id))
            gap = {'power': 0, "damage": 0}
            check = cur.fetchone()
            if check:
                gap['power'] = check[0]
                gap['damage'] = check[1]
            cur.execute("SELECT level FROM user_info WHERE id = %s",
                        interaction.user.id)
            level = cur.fetchone()[0]
            embed = discord.Embed(
                title=f"Lv.{weapon['level']} {weapon['name']}[{weapon['rank']}] +{weapon['upgrade']} ({'거래가능' if weapon['trade'] else '거래불가'}) {'착용중' if weapon['wear'] else ''}")
            embed.set_footer(text=f"아이템코드 : {weapon['item_id']}")
            embed.set_thumbnail(url=weapon['url'])
            embed.add_field(
                name=f"힘 : {weapon['power']}({'+' if weapon['power']-gap['power']>0 else ''}{weapon['power']-gap['power']})", value="\u200b")
            embed.add_field(
                name=f"데미지 : {round(weapon['damage'],2)}({'+' if weapon['damage']-gap['damage']>0 else ''}{round(weapon['damage']-gap['damage'],2)})", value='\u200b')
            embed.add_field(name=f"옵션 : {weapon['option']}", value='\u200b')
            view = ui.View()
            equip = ui.Button(label="착용하기", style=ButtonStyle.green,
                              disabled=level < weapon['level'])
            back = ui.Button(label="돌아가기", style=ButtonStyle.red)
            view.add_item(equip)
            view.add_item(back)

            async def equip_callback(interaction: Interaction):
                if category == "wear":
                    cur.execute("UPDATE user_wear SET wear = 0 WHERE part = %s AND wear = 1 AND id = %s",
                                (wear['part'], interaction.user.id))
                    cur.execute(
                        "UPDATE user_wear SET wear = 1 WHERE item_id = %s", wear['item_id'])
                if category == "weapon":
                    cur.execute("UPDATE user_weapon SET wear = 0 WHERE wear = 1 AND id = %s",
                                (interaction.user.id))
                    cur.execute(
                        "UPDATE user_weapon SET wear = 1 WHERE item_id = %s", weapon['item_id'])
                con.commit()
                await detail_callback(interaction)
            equip.callback = equip_callback
            back.callback = setup
            await interaction.response.edit_message(embed=embed, view=view)

    async def checkout_callback(interaction: Interaction):
        class checkoutModal(ui.Modal, title="아이템을 선택해주세요."):
            answer = ui.TextInput(
                label="번호", placeholder="현재 페이지 첫번째는 1입니다. 범위는 1~10까지만 가능합니다.", default=1, required=True, max_length=2)

            async def on_submit(self, interaction: Interaction, /):
                try:
                    value = int(self.answer.value[0])
                except:
                    pass
                else:
                    if value > 10:
                        pass
                    elif value <= 0:
                        pass
                    else:
                        index[interaction.user.id] = value-1
                        await detail_callback(interaction)
        await interaction.response.send_modal(checkoutModal())

    async def setup(interaction: Interaction):
        cur = con.cursor()
        embed = discord.Embed(title="인벤토리")
        cur.execute(
            f"SELECT COUNT(*) FROM user_{category} WHERE id = {interaction.user.id}",)
        count = cur.fetchone()[0]
        if category == "item":
            cur.execute("SELECT name,description,`rank`,price,trade,amount,item_id FROM user_item WHERE id = %s ORDER BY item_id ASC LIMIT %s,10",
                        (interaction.user.id, page[interaction.user.id] * 10))
            for i in cur.fetchall():
                if i[5] > 0:
                    embed.add_field(
                        name=f"[{i[-1]}] {i[0]}[{i[2]}]({'거래가능' if i[4] else '거래불가'}) {i[5]}개", value=i[1], inline=False)
        elif category == "wear":
            cur.execute(
                "SELECT name,upgrade,`rank`,level,collection,part,wear,trade FROM user_wear WHERE id = %s ORDER BY item_id ASC LIMIT %s,10",
                (interaction.user.id, page[interaction.user.id] * 10))
            for i in cur.fetchall():
                embed.add_field(
                    name=f"Lv.{i[3]} {i[0]}[{i[2]}] +{i[1]} ({'거래가능' if i[-1] else '거래불가'}) {'착용중' if i[-2] else ''}", value=f"{i[4]} 세트", inline=False)
        else:
            cur.execute("SELECT name,upgrade,`rank`,level,wear,trade FROM user_weapon WHERE id = %s ORDER BY item_id ASC LIMIT %s,10",
                        (interaction.user.id, page[interaction.user.id]*10))
            for i in cur.fetchall():
                embed.add_field(
                    name=f"Lv.{i[3]} {i[0]}[{i[2]}] +{i[1]} ({'거래가능' if i[-1] else '거래불가'}) {'착용중' if i[-2] else ''}", value='\u200b', inline=False)

        embed.set_footer(text=f"{page[interaction.user.id]+1} 페이지")
        view = ui.View(timeout=None)
        previous = ui.Button(
            label="이전으로", disabled=not page[interaction.user.id] > 0)
        next = ui.Button(label="다음으로", disabled=not (
            page[interaction.user.id]+1)*10 < count)
        reset = ui.Button(label="새로고침")
        view.add_item(previous)
        view.add_item(next)
        view.add_item(reset)
        if category != 'item':
            checkout = ui.Button(label="선택하기", style=ButtonStyle.green, row=2)
            view.add_item(checkout)
            checkout.callback = checkout_callback
        previous.callback = previous_callback
        next.callback = next_callback
        reset.callback = setup
        try:
            await interaction.response.edit_message(embed=embed, view=view)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=embed, view=view)
    await interaction.response.send_message("아이템을 가져오는 중입니다.", ephemeral=True)
    await setup(interaction)


@tree.command(name="채광초기화", description="채광이 버그가 나서 초기화가 필요할때 쓰세요.")
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


@tree.command(name="무릉", description="무릉")
async def mooroong(interaction: Interaction):
    floor = {}
    floor[interaction.user.id] = 1
    if not authorize(interaction.user.id):
        return await interaction.response.send_message("`회원가입` 명령어로 먼저 가입을 해주세요.", ephemeral=True)
    stat = getStatus(interaction.user.id)
    stat['power'] = round(stat['power'], 2)

    async def go_callback(interaction: Interaction):  # 탐험진행
        enemy = makeDictionary(['name', 'power', 'hp'], ("시련의 광석",
                               floor[interaction.user.id]*2, floor[interaction.user.id]*20))

        async def end_win_callback(interaction: Interaction):  # 전투 끝날때
            await interaction.response.edit_message(content="재정비...")
            await start(interaction)

        async def win(interaction: Interaction):  # 이겼을때
            embed = discord.Embed(title="승리!")
            view = ui.View(timeout=None)
            end_win = ui.Button(label="정비하기", style=ButtonStyle.green)
            end_win.callback = end_win_callback

            view.add_item(end_win)
            floor[interaction.user.id] += 1
            await interaction.response.edit_message(content="", embed=embed, view=view)

        async def lose(interaction: Interaction):  # 졌을때
            embed = discord.Embed(
                title=f"기절했습니다. {floor[interaction.user.id]}층 도달.")
            cur = con.cursor()
            cur.execute("UPDATE user_info SET mooroong = %s WHERE id = %s",
                        (floor[interaction.user.id], interaction.user.id))
            con.commit()
            await interaction.response.edit_message(content="", embed=embed, view=None)

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
            view = ui.View(timeout=None)
            attack = ui.Button(emoji="⛏", style=ButtonStyle.green)
            view.add_item(attack)
            attack.callback = attack_callback
            try:
                await interaction.response.edit_message(content="", embed=embed, view=view)
            except discord.errors.InteractionResponded:
                pass

        await try_callback(interaction)

    async def start(interaction: Interaction):  # 기본 정비 함수
        rest = discord.Embed(title="정비")
        rest.add_field(
            name=f"남은 체력 : {stat['hp']}", value="\u200b", inline=False)
        rest.add_field(
            name=f"현재 층 : {floor[interaction.user.id]}", value="\u200b", inline=False)
        view = ui.View(timeout=None)
        go = ui.Button(label="탐험진행", emoji='⛏', style=ButtonStyle.green)
        go.callback = go_callback
        view.add_item(go)
        try:
            await interaction.response.send_message(embed=rest, view=view, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content="", embed=rest, view=view)
    await start(interaction)


@tree.command(name="채광", description="채광")
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
            cur.execute("UPDATE user_item SET amount=0 WHERE id = %s  AND item_id=%s",
                        (interaction.user.id, ticket[광산.value]))
            con.commit()
        if 광산.value > -7:
            cnt[interaction.user.id] = 3
        if 광산.value == -8:
            cnt[interaction.user.id] = 6
    stat = getStatus(interaction.user.id)
    stat['power'] = round(stat['power'], 2)
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
                return await start(interaction)

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
                        await start(interaction)
            await interaction.response.send_modal(amountModal())
        items.callback = item_remove_callback
        await interaction.response.edit_message(view=view)

    async def go_callback(interaction: Interaction):  # 탐험진행
        cnt[interaction.user.id] -= 1
        cur.execute(
            "SELECT name,power,hp,exp,item_code,item_percent,item_amount,util_code,util_percent,util_amount,url FROM enemy WHERE floor=%s ORDER BY RAND() LIMIT 1", 광산.value)
        enemy = makeDictionary(['name', 'power', 'hp', 'exp', 'item_code', "item_percent",
                               "item_amount", "util_code", "util_percent", "util_amount", "url"], cur.fetchone())
        stat['hp'] = stat['maxhp']

        async def run_callback(interaction: Interaction):  # 도망치기
            await interaction.response.edit_message(content="도망쳤습니다.")
            return await start(interaction)

        async def end_win_callback(interaction: Interaction):  # 전투 끝날때
            await interaction.response.edit_message(content="재정비...")
            await start(interaction)

        async def win(interaction: Interaction):  # 이겼을때
            util_data = getJson('./json/util.json')
            stone_data = getJson('./json/stone.json')
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
            embed.add_field(name="광석 :", value='\u200b', inline=False)
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
            embed.add_field(name="기타 :", value='\u200b', inline=False)
            for i in range(len(util_percent)):
                if getSuccess(int(util_percent[i]), 100):
                    util: dict = util_data[util_code[i]]
                    isExistItem(interaction.user.id, util_code[i])
                    min, max = util_amount[i].split("~")
                    total = random.randint(int(min), int(max))
                    cur.execute(
                        "UPDATE user_item SET amount = amount + %s WHERE id = %s AND item_id = %s", (total, interaction.user.id, util_code[i]))
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

    async def start(interaction: Interaction):  # 기본 정비 함수
        rest = discord.Embed(title="정비")
        weight = abs(
            round(adventrue_inventory[interaction.user.id]['weight'], 2))
        disabled = round(stat['str'], 2) < weight-0.001

        rest.add_field(
            name=f"가방(용량:{weight}/{round(stat['str'],2)})", value="\u200b",)
        rest.add_field(name=광산.name, value='\u200b', inline=False)
        if disabled:
            rest.set_footer(text="가방이 너무 무겁습니다!")
        if cnt[interaction.user.id] >= 0:
            rest.add_field(
                name=f"남은 횟수 : {cnt[interaction.user.id]}", value='\u200b')
            if cnt[interaction.user.id] == 0:
                rest.set_footer(text="횟수가 없습니다!")

        view = ui.View(timeout=None)
        remove = ui.Button(label="아이템버리기", emoji="🗑", style=ButtonStyle.gray,
                           disabled=(weight == 0.0), row=2)
        go = ui.Button(label="탐험진행", emoji='⛏',
                       disabled=disabled or cnt[interaction.user.id] == 0, style=ButtonStyle.green)
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
    await start(interaction)
client.run(os.environ['token'])
