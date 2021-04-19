from datetime import datetime
from logging import getLogger
from typing import Iterator, List

from attr import dataclass
from bs4 import BeautifulSoup
from discord import Colour, Embed
from tinydb import where
from tinydb.operations import set

from bfti_bot.bot import Bot
from ..background_task import DefaultScheduler, Task
from ..config import config

log = getLogger('tasks.iserv_exercises')


@dataclass
class Exercise:
    id: int = None
    author: str = None
    title: str = None
    message: str = None
    url: str = None
    end_date: datetime = None


class IservExercises(Task):
    def __init__(self, bot: Bot):
        self.name = self._get_name(__file__)
        self.bot = bot

        self.creds = {
            '_username': config.iserv_username,
            '_password': config.iserv_password,
        }
        self.login_url = f'https://{config.iserv_hostname}/iserv/app/login?target=%2Fiserv%2Fexercise'
        # 22.03.2021 08:00
        self.datetime_format = '%d.%m.%Y %H:%M'

        self.shown_excercises = self.bot.db.table('shown_excercises')

    async def run_once(self) -> None:
        await self.bot.channel_available.wait()

    async def run(self) -> None:
        for id in await self._get_not_shown_exercise_ids():
            exercise = await self._get_exercise(id)
            embed = await self._generate_embed(exercise)
            await self.bot.channel.send(content='@everyone', embed=embed)

            self.shown_excercises.insert(
                {
                    'id': exercise.id,
                    'end_date': exercise.end_date.timestamp(),
                    'reminder_shown': await self._due_in_under(exercise.end_date, 60),
                }
            )

        for id in await self._get_should_be_reminded_ids():
            exercise = await self._get_exercise(id)
            embed = await self._generate_embed(exercise, is_reminder=True)
            await self.bot.channel.send(content='@everyone', embed=embed)

            self.shown_excercises.update(
                set('reminder_shown', True), where('id') == exercise.id
            )

    async def _get_should_be_reminded_ids(self) -> List[int]:
        should_be_reminded = []
        for elem in self.shown_excercises.all():
            if elem['reminder_shown']:
                continue

            if not await self._due_in_under(
                datetime.fromtimestamp(elem['end_date']), 60
            ):
                continue

            should_be_reminded.append(elem['id'])

        return should_be_reminded

    async def _get_not_shown_exercise_ids(self) -> List[int]:
        shown_excercise_ids = [elem['id'] for elem in self.shown_excercises.all()]
        return [
            id
            for id in await self._get_excercise_ids()
            if not id in shown_excercise_ids
        ]

    async def _due_in_under(self, dt: datetime, minutes: int) -> bool:
        delta = dt - datetime.now()
        return delta.days == 0 and (delta.seconds / 60) < minutes

    async def _generate_embed(self, exercise: Exercise, is_reminder=False) -> Embed:
        title = (
            f'Abgabe in 1h: {exercise.title}'
            if is_reminder
            else f'Neue Aufgabe: {exercise.title}'
        )
        embed = Embed(
            title=title,
            type='rich',
            colour=Colour.orange() if is_reminder else Colour.dark_purple(),
            url=exercise.url,
        )

        embed.set_author(name=exercise.author)

        if len(exercise.message) > 1022:
            exercise.message = exercise.message[1018:] + '*...*'
        embed.add_field(
            name='Nachricht',
            value=exercise.message,
        )
        embed.add_field(
            name='Abgabetermin',
            value=exercise.end_date.strftime(self.datetime_format),
        )
        embed.set_footer(text=self.bot.signature)

        return embed

    async def _get_exercise(self, id: int) -> Exercise:
        url = f'https://bbs2celle.eu/iserv/exercise/show/{id}'
        async with self.bot.http_session.get(url) as response:
            exercise = Exercise(
                url=url, id=id
            )  # pyright: reportGeneralTypeIssues=false
            soup = BeautifulSoup(await response.text(), "html.parser")

            info_table = soup.find(class_='bb0')
            info_tds = info_table.find_all('td')
            exercise.author = info_tds[0].find('a').text
            exercise.end_date = datetime.strptime(
                info_tds[2].text, self.datetime_format
            )
            exercise.title = soup.find('h1').text

            msg_ps = soup.find(True, {'class': ['p-3', 'text-break-word']}).findAll('p')
            exercise.message = '\n'.join([p.text for p in msg_ps])

            return exercise

    async def _get_excercise_ids(self) -> Iterator[int]:
        async with self.bot.http_session.post(
            self.login_url, data=self.creds
        ) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")

            exercise_a_tags = (
                td.find("a")
                for td in soup.find_all(class_="iserv-admin-list-field-textarea")
            )
            exercise_urls = (a["href"] for a in exercise_a_tags)
            exercise_ids = (int(url[url.rfind("/") + 1 :]) for url in exercise_urls)

            return exercise_ids


def setup(bot: Bot) -> None:
    bot.add_task(IservExercises(bot), DefaultScheduler(60.0, bot))
