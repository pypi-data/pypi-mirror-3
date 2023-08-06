
class Colors(object):
    BLUE = '0;34'
    DEFAULT = '0'

class BashPromptPart(object):
    def __init__(self, text, color=Colors.DEFAULT):
        self.text = text
        self.color = color

    def __str__(self):
        return r'\[\033[{color}m\]{text}'.format(**self.__dict__)
