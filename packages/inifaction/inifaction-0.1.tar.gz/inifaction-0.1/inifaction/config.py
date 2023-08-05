from validate import Validator, ValidateError, is_ip_addr
from configobj import ConfigObj, flatten_errors

from inifaction import SECTIONS, CONFIG_SPEC

def is_ip_addr_or_empty(value):
    if value == '':
        return value
    return is_ip_addr(value)

def accept(sentence):
    prompt = '{sentence} (yes/no): '.format(sentence=sentence)
    answer = None
    while answer not in ('yes', 'no'):
        answer = raw_input(prompt).strip()
    return answer == 'yes'

class Config(ConfigObj):
    validator = Validator({'ip_addr': is_ip_addr_or_empty})

    def __init__(self, *args, **kwargs):
        kwargs.update({'configspec': CONFIG_SPEC})
        super(Config, self).__init__(*args, **kwargs)
        self.check()

    def check(self):
        result = self.validate(self.validator, preserve_errors=True)
        if result is not True:
            for (sections, key, result) in flatten_errors(self, result):
                sections = [ '"{0}"'.format(section) for section in sections + [key] ]
                msg = 'At {section} {result}'.format(
                        section=' => '.join(sections), result=result)
                raise ValidateError(msg)
        return result

    def get_login(self):
        user = self['user']
        password = self['password']
        machine = self['machine']
        return user, password, machine

    def get_section(self, section):
        items = []
        for label, conf in self[section].items():
            items.append(SECTIONS[section].from_config(label, **conf))
        return items
