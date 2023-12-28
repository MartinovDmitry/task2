import csv
from enum import Enum

import _asyncio
import aiohttp

from config import settings


class CSVHelper:
    header = ['userId', 'result', 'postId']

    def __init__(self, file):
        self.file = file

    def dict_writer(self):
        dict_writer = csv.DictWriter(self.file, fieldnames=self.header, lineterminator="\r")
        dict_writer.writeheader()
        return dict_writer


class Status(Enum):
    finished = 'The task is finished'
    failed = 'The task is failed'


def return_status_of_task(task: _asyncio.Task):
    if task.done:
        return Status.finished.value
    else:
        return Status.failed.value


async def process_row(row):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=settings.URL, data=row) as response:
            if response.status == 201:
                result = await response.json()
                print(f'{result=}')
                return result
            else:
                return row
