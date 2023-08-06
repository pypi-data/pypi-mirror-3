# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

def make_btn(url, **kwargs):
    """
    Easy generating of Bootstrap link (with button style).
    
    Kwargs available are the following :
      - css : CSS style of the button. Allowed values : 'primary', 'info', 'success',
              'warning', 'danger' or 'inverse'. By default, display a standard gray button.
      - size : Size of the button. Allowed values are : 'large', 'small' or 'mini'.
               By default, use the normal size.
      - align : 'right' or 'left'. By default is None
      - type : Predefined Configuration of txt and icon.
               Allowed values : 'edit'.
      - txt : Text value of the button
      - icon : Suffix of a Glyphicons label (e.g. 'edit', 'music', ...)
      - icon_white : True if you want white icon (default = False)
    """
    # Initialization
    item_class = 'btn'
    item_txt = 'Action'
    item_icon_type = item_icon_white = item_icon = ''
    # Make class button
    if 'css' in kwargs:
        item_class += ' btn-%s' % kwargs['css']
    if 'size' in kwargs:
        item_class += ' btn-%s' % kwargs['size']
    if 'align' in kwargs:
        item_class += ' pull-%s' % kwargs['align']
    item_class = u' class="%s"' % item_class
    # Standard Configurations
    std_type = kwargs.get('type', None)
    if std_type == 'edit':
        item_txt = _(u'Edit')
        item_icon_type = 'edit'
    # elif type == '':
    #     item_txt = 
    #     item_icon_type =
    # Make icon white ?
    if kwargs.get('icon_white', False):
        item_icon_white = ' icon-white'
    # Customization
    if 'text' in kwargs:
        item_txt = kwargs['txt']
    if 'icon' in kwargs:
        item_icon_type = kwargs['icon']
    # Make icon
    if item_icon_type:
        item_icon = '<i class="icon-%s%s"></i>&nbsp;' % (item_icon_type, item_icon_white)
    # Make button
    button = '<a%s href="%s">%s%s</a>' % (item_class, url,
                                          item_icon, item_txt)
    return button
