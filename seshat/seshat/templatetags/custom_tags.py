from django import template
import json

register = template.Library()


@register.filter
def button_name(file, files):
    '''
    Return the button name from file name
    '''
    name = file.split('-')[0]
    index = files.index(file)
    return f"{name}-{index}"


@register.filter
def get_index(file, files):
    '''
    Return the index of the file in files
    '''
    index = files.index(file)
    return int(index)
