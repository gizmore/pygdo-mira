import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.mira.module_mira import module_mira
from gdotest.TestUtil import cli_plug, reinstall_module, cli_gizmore, GDOTestCase, WebPlug, install_module, web_plug


class module_mira_Test(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        install_module('mira')
        loader.load_modules_db(True)
        WebPlug.COOKIES = {}
        Application.init_cli()
        loader.init_modules(True, True)
        loader.init_cli()

    def test_00_reinstall(self):
        reinstall_module('mira')
        self.assertIs(type(module_mira.instance()), module_mira, "Cannot re-install module mira.")

    def test_01_heartbeat_delay(self):
        self.assertAlmostEqual(1337.420320, module_mira.instance().cfg_heartbeat_delay(), places=6)

    def test_03_overview_cli(self):
        giz =  cli_gizmore()
        out = cli_plug(giz, "$mira.overview")
        self.assertIsNotNone(out, '$mira.overview does not work.')

    def test_02_overview_web(self):
        giz =  cli_gizmore()
        out = web_plug("mira.overview.html")
        self.assertIsNotNone(out, 'mira.overview.html does not work.')


if __name__ == '__main__':
    unittest.main()
