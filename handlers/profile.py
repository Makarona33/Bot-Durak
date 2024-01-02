from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from vkbottle import AiohttpClient, PhotoMessageUploader
from vkbottle.bot import Message
from vkbottle.framework.labeler import BotLabeler

from config import api
from tools.db import manager, Users

labeler = BotLabeler()
labeler.vbml_ignore_case = True


@labeler.private_message(text=['профиль', 'Профиль📊'])
async def profile(message: Message):
    user = await manager.get(Users, user_id=message.from_id)
    await message.answer('📊Твой профиль:', await photo(user))


async def photo(user: Users) -> str:
    background: Image = Image.open(f'sources/backgrounds/default.jpg')
    base = Image.open('sources/profile/base.png')
    background.paste(base, (0, 0), base)
    draw = ImageDraw.Draw(background)

    avatar = Image.open(
        BytesIO(await AiohttpClient().request_content(
            (await api.users.get(user.user_id, ['photo_200_orig']))[0].photo_200_orig))
    ).resize((266, 266))

    background.paste(avatar, (829, 245), Image.open('sources/profile/circle.png').resize((266, 266)))

    main_font = ImageFont.truetype('sources/fonts/Bebas Neue Cyrillic.ttf', 90)

    draw.text((590, 770), f'{user.wins:,}', 'white', main_font, 'mm', stroke_width=5, stroke_fill=(143, 144, 141))
    draw.text((1019, 770), f'{user.loses:,}', 'white', main_font, 'mm', stroke_width=5, stroke_fill=(143, 144, 141))
    draw.text((1388, 770), f'{user.money:,}', 'white', main_font, 'mm', stroke_width=5, stroke_fill=(143, 144, 141))

    second_font = ImageFont.truetype(r'sources/fonts/Bebas Neue Cyrillic.ttf', 62)

    draw.text((963, 218), f'{user.nick}', 'white', second_font, 'mm', stroke_width=3, stroke_fill=(137, 137, 137),
              embedded_color=True)
    draw.text((963, 553), f'ID: {user.user_id}', 'white', second_font, 'mm',
              stroke_width=3, stroke_fill=(137, 137, 137))

    image_content = BytesIO()
    background.save(image_content, format='JPEG')
    return await PhotoMessageUploader(api).upload(image_content)
