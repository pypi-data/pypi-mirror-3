from pyramid_formalchemy.i18n import _
from pyramid_formalchemy import actions
from pyramid_formalchemy.actions import Actions
from pyramid_formalchemy.actions import action; action


class UIButton(actions.UIButton):
    """Overwrite default pyramid_formalchemy action to support bootstrap style."""

    body = '''<a class="${_class}" tal:attributes="%(attributes)s">${content}</a>'''


class TabAction(actions.Action):
    """New action type - comaptible with boostrap style."""
    body = u'<li tal:attributes="class action.isActive(request) and \'active\' or \'\'"><a tal:attributes="%(attributes)s">${content}</a></li>'

    def isActive(self, request):
        for _id in self.rcontext.get('children', ()):
            if _id in request.matchdict.get('traverse'):
                return True
        return self.id == request.action


new = UIButton(
        id='new',
        content=_('New ${model_label}'),
        permission='new',
        _class='btn primary',
        attrs=dict(href="request.fa_url(request.model_name, 'new')"),
        )


save = UIButton(
        id='save',
        content=_('Save'),
        permission='edit',
        _class='btn success',
        attrs=dict(onclick="jQuery(this).parents('form').submit();"),
        )

save_and_add_another = UIButton(
        id='save_and_add_another',
        content=_('Save and add another'),
        permission='edit',
        _class='btn success',
        attrs=dict(onclick=("var f = jQuery(this).parents('form');"
                            "jQuery('#next', f).val(window.location.href);"
                            "f.submit();")),
        )

edit = UIButton(
        id='edit',
        content=_('Edit'),
        permission='edit',
        _class='btn info',
        attrs=dict(href="request.fa_url(request.model_name, request.model_id, 'edit')"),
        )

back = UIButton(
        id='back',
        content=_('Back'),
        _class='btn',
        attrs=dict(href="request.fa_url(request.model_name)"),
        )

delete = UIButton(
        id='delete',
        content=_('Delete'),
        permission='delete',
        _class='btn danger',
        attrs=dict(onclick=("var f = jQuery(this).parents('form');"
                      "f.attr('action', window.location.href.replace('/edit', '/delete'));"
                      "f.submit();")),
        )

cancel = UIButton(
        id='cancel',
        content=_('Cancel'),
        permission='view',
        _class='btn',
        attrs=dict(href="request.fa_url(request.model_name)"),
        )

defaults_actions = actions.defaults_actions.copy()
defaults_actions['listing_buttons'] = Actions(new)
defaults_actions['new_buttons'] = Actions(save, save_and_add_another, cancel)
defaults_actions['edit_buttons'] = Actions(save, delete, cancel)
defaults_actions['show_buttons'] = Actions(edit, back)
