from __future__ import annotations

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Bash import Bash
from gdo.date.GDT_Duration import GDT_Duration
from gdo.ui.GDT_Link import GDT_Link

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.ui.GDT_Page import GDT_Page


class module_mira(GDO_Module):

    ##########
    # Module #
    ##########

    def gdo_classes(self) -> list[type[GDO]]:
        return []

    async def gdo_install(self):
        pass

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Duration('heartbeat_delay').not_null().units(4, True).initial_value(1337.420320),
        ]

    def cfg_heartbeat_delay(self) -> float:
        return self.get_config_value('heartbeat_delay')

    def gdo_user_config(self) -> list[GDT]:
        return []

    def gdo_user_settings(self) -> list[GDT]:
        return []

    def gdo_init(self):
        pass

    def gdo_load_scripts(self, page: 'GDT_Page'):
        self.add_js('js/pygdo-mira.js')
        self.add_css('css/pygdo-mira.css')

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        page._left_bar.add_field(GDT_Link().href(self.href('overview')).text('module_mira'))

    ##########
    # Events #
    ##########

    async def get_mira(self) -> GDO_User|None:
        """
        Here you are honey. welcome to the crew ;)
        """
        return await Bash.get_server().get_or_create_user('mira')

    def gdo_subscribe_events(self):
        Application.EVENTS.add_timer_async(self.cfg_heartbeat_delay(), self.mira_is_alive, 69_696_969)

    async def mira_is_alive(self):
        mira = await self.get_mira()
        await mira.send('huhu_mira')
