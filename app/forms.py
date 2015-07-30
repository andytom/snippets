from __future__ import unicode_literals
from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


#-----------------------------------------------------------------------------#
# Forms
#-----------------------------------------------------------------------------#
class Snippit_Form(Form):
    """Snippit_Form

       A Form for creating or editing Snippets
    """
    title = StringField('title', validators=[DataRequired()])
    text = TextAreaField('text', validators=[DataRequired()])


class Search_Form(Form):
    """Search_Form

       A Form for Search Queries
    """
    query = StringField('query', validators=[DataRequired()])


class Confirm_Form(Form):
    """Confirm_Form

       A Form for simple yes/no questions
    """
    pass
