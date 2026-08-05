from gdo.base.GDT import GDT
from gdo.core.GDT_Bool import GDT_Bool
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class overview(MethodForm):
    @classmethod
    def gdo_method_config_channel(cls) -> list[GDT]:
        """Channel conversations require an explicit opt-in before forwarding."""
        return [
            GDT_Bool('enabled').not_null().initial('0'),
        ]

    def gdo_parameters(self) -> list[GDT]:
        return []

    def gdo_create_form(self, form: GDT_Form) -> None:
        super().gdo_create_form(form)

    def form_submitted(self):
        return self.msg('%s', 'Yeah!')
    
