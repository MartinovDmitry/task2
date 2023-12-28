import asyncio
import csv

from fastapi import FastAPI, UploadFile, File
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from starlette.staticfiles import StaticFiles

from config import settings
from exceptions import IncorrectContentTypeError
from utils import process_row, return_status_of_task, CSVHelper

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='templates')


@app.get('/file', response_class=HTMLResponse)
async def get_file_form(request: Request):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template('file.html')
    rendered_template = template.render()
    return rendered_template


@app.post('/file')
async def post_file_form(file: UploadFile = File(...)):
    if file.content_type != settings.FORMAT:
        return IncorrectContentTypeError

    file_payload = await file.read()
    fieldnames = ['userId', 'title', 'body']
    reader = csv.DictReader(file_payload.decode('utf-8').splitlines(), fieldnames=fieldnames)
    next(reader)

    results_of_processed_rows = list()

    tasks = list()
    for row in reader:
        task = asyncio.create_task(process_row(row=row))
        tasks.append(task)

    limit = asyncio.Semaphore(7)
    async with limit:
        with open('result.csv', 'a') as file:
            csv_helper = CSVHelper(file=file)
            dict_writer = csv_helper.dict_writer()
            for task in tasks:
                dict_of_result = {'userId': None, 'result': None, 'postId': None}
                result = await task
                if result.get('id'):  # type: dict
                    results_of_processed_rows.append(result)
                    dict_of_result.update(
                        userId=result.get('userId'),
                        result=return_status_of_task(task=task),
                        postId=result.get('id')
                    )
                    dict_writer.writerow(dict_of_result)
                else:
                    dict_of_result.update(
                        userId=result.get('userId'),
                        result=return_status_of_task(task=task),
                        postId=None
                    )
                    dict_writer.writerow(dict_of_result)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('result.html')
    rendered_template = template.render(results=results_of_processed_rows)

    return rendered_template
