from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
             Number, Operator, Generic

class OmblogStyle(Style):
    default_style=''
    styles = {
            Comment: 'italic #888',
            Keyword: 'bg:#f90 #90f',
            }
