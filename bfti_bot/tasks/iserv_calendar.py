from asyncio.events import get_event_loop
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from logging import getLogger
from typing import List, Optional
from caldav import davclient, Principal
from attr import dataclass
from discord import Embed, Colour
from icalendar import Calendar

from ..config import config

from bfti_bot.bot import Bot

from ..background_task import DefaultScheduler, Task

log = getLogger('tasks.iserv_calendar')

@dataclass
class Event:
    uid: str = None
    dateStart: datetime = None
    dateEnd: datetime = None
    summary: str = None
    description: str = None
    createdAt: datetime = None
    location: str = None
    categories: str = None


class IServCalendar(Task):
    def __init__(self, bot: Bot):
        self.name = self._get_name(__file__)
        self.bot = bot
        self.shown_events = self.bot.db.table('shown_events')

        self.calendar_url = f'https://{config.iserv_hostname}/caldav/klasse.bfti20a/calendar'
        self.client: Optional[davclient.DAVClient]

        self.executor = ThreadPoolExecutor(1)
        self.loop = get_event_loop()

    async def run_once(self) -> None:
        await self.bot.channel_available.wait()
        await self.loop.run_in_executor(self.executor, self._init_calendar)

    async def run(self) -> None:
        events = await self.loop.run_in_executor(self.executor, self._get_events)

        shown_event_uids = [elem['uid'] for elem in self.shown_events.all()]
        not_shown_events = [event for event in events if event.uid not in shown_event_uids]
        for event in not_shown_events:
            self.shown_events.insert({'uid': event.uid})

        for event in not_shown_events:
            embed = await self._generate_embed(event)
            await self.bot.calendar_channel.send(content='@everyone', embed=embed)
    
    def _init_calendar(self) -> None:
        self.client      = davclient.DAVClient(
            url=self.calendar_url, 
            username=config.iserv_username, 
            password=config.iserv_password
            )

    def _get_events(self) -> List[Event]:
        calendar=self.client.calendar(url=self.calendar_url)
        rawevents = calendar.events()
        events = []

        for eventraw in rawevents:
            event = Calendar.from_ical(eventraw._data)
            for component in event.walk():
                if component.name == "VEVENT":
                    event = Event()
                    startDate = component.get('dtstart')
                    event.dateStart = startDate.dt

                    endDate = component.get('dtend')
                    event.dateEnd = endDate.dt

                    if component.get('summary'): 
                        event.summary = component.get('summary').title()
                    if component.get('description'):
                        event.description = component.get('description').title()
                    if component.get('location'):
                        event.location = component.get('location').title()
                    if component.get('categories'):
                        event.categories = [vtext.title() for vtext in component.get('categories').cats]
                    
                    event.uid = component.get('uid').title()
                    event.createdAt = component.get('created').dt


                    events.append(event)
        return events

    async def _generate_embed(self, event: Event) -> Embed:
        embed = Embed(
            title=f'`Neuer Termin: {event.summary}`',
            type='rich',
            colour=Colour.dark_blue(),
        )

        if event.description:
            embed.add_field(name='Beschreibung', value=event.description)
        embed.add_field(name='Start', value=event.dateStart.strftime('%m/%d/%Y %H:%M'))
        embed.add_field(name='Ende', value=event.dateEnd.strftime('%m/%d/%Y %H:%M'))
        embed.add_field(name='Erstellt', value=event.createdAt.strftime('%m/%d/%Y %H:%M'), inline=False)  
        embed.set_footer(text=self.bot.signature)

        return embed

def setup(bot: Bot) -> None:
    bot.add_task(IServCalendar(bot), DefaultScheduler(120.0, bot))
