from django import forms
from .models import *


class LedgerAdminForm(forms.ModelForm):
    def __init__(self,  *args, **kwargs):
        ledger_choices = list(Ledger.objects.filter(has_sub_code=True
                                                    ))

        a = [
            (i.name, i.name) for i in ledger_choices]
        a.insert(0, ('---', '----'))

        super(LedgerAdminForm, self).__init__(*args, **kwargs)
        self.fields['ledger_head'].choices = a
    ledger_head = forms.ChoiceField(choices=())

    def save(self, commit=True):
        obj = super().save(commit=False)
        data = self.cleaned_data

        if data['ledger_head'] != '---':

            name = Ledger.objects.filter(name=data['ledger_head']).first()
            obj = Ledger(
                name=data['name'], has_sub_code=data['has_sub_code'], groupcode=name.id)
            obj.save()
        obj.save()
        if commit:
            obj.save()
        return obj

    class Meta:
        model = Ledger
        fields = ('name', 'has_sub_code', 'ledger_head')
