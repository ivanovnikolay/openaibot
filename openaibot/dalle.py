import openai
from base64 import b64decode
from io import BytesIO
from PIL import Image


async def new_images(prompt, size, count):
    response = await openai.Image.acreate(
        prompt=prompt,
        n=count,
        size=size,
        response_format='b64_json',
    )
    return _parse_response(response)


async def var_images(image, size, count):
    response = await openai.Image.acreate_variation(
        image=image,
        n=count,
        size=size,
        response_format='b64_json',
    )
    return _parse_response(response)


async def edit_images(image, mask, prompt, size, count):
    response = await openai.Image.acreate_edit(
        image=image,
        mask=mask,
        prompt=prompt,
        n=count,
        size=size,
        response_format='b64_json',
    )
    return _parse_response(response)


def _parse_response(response):
    return ((b, _create_thumb(b)) for b in (b64decode(i['b64_json']) for i in response.data))


def _create_thumb(data):
    with Image.open(BytesIO(data)) as img:
        img.thumbnail((256, 256))
        return img.tobytes()
