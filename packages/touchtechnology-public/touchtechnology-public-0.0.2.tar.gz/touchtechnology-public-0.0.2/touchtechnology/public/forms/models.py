from django.forms import ModelForm


class RedefineModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RedefineModelForm, self).__init__(*args, **kwargs)
        for field_name, _kw in getattr(self.Meta, 'redefine', ()):
            kw = {}
            for key, val in _kw.items():
                if callable(val) and not type(val) == type:
                    kw[key] = val(self.fields[field_name])
                else:
                    kw[key] = val
            field = self.Meta.model._meta.get_field(field_name)
            self.fields[field_name] = field.formfield(**kw)
