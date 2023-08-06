from custom_delete_selected.actions import delete_selected


class CustomDeleteSelected(object):

    def get_actions(self, request):
        actions = super(CustomDeleteSelected, self).get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                delete_selected,
                'delete_selected',
                delete_selected.short_description
            )
        return actions
