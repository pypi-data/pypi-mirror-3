# This file contains internal information used to manipulate responses based on
# their type, for example allowing response items to be passed as parameters to
# other methods, etc.

## Contains a mapping of request paths to types returned.
#
# This list does not include /errors/{id} or /comments/{id}/delete
# because they does not (by nature) return a response at all. The
# filter methods are also excluded because Stack.PY provides a
# Filter class to abstract its functionality.
METHOD_TO_TYPE_MAPPING = {
    'access-tokens/*':                 'access_token',
    'access-tokens/*/invalidate':      'access_token',
    'apps/*/de-authenticate':          'access_token',
    'answers':                         'answer',
    'answers/*':                       'answer',
    'answers/*/comments':              'comment',
    'badges':                          'badge',
    'badges/*':                        'badge',
    'badges/*/recipients':             'badge',
    'badges/name':                     'badge',
    'badges/recipients':               'badge',
    'badges/tags':                     'badge',
    'comments':                        'comment',
    'comments/*':                      'comment',
    'comments/*/edit ':                'comment',
    'errors':                          'error',
    'events':                          'event',
    'inbox':                           'inbox_item',
    'inbox/unread':                    'inbox_item',
    'info':                            'info',
    'notifications':                   'notification',
    'notifications/unread':            'notification',
    'posts':                           'post',
    'posts/*':                         'post',
    'posts/*/comments':                'comment',
    'posts/*/comments/add':            'comment',
    'posts/*/revisions':               'revision',
    'posts/*/suggested-edits':         'suggested_edit',
    'privileges':                      'privilege',
    'questions':                       'question',
    'questions/*':                     'question',
    'questions/*/answers':             'answer',
    'questions/*/comments':            'comment',
    'questions/*/linked':              'question',
    'questions/*/related':             'question',
    'questions/*/timeline':            'question_timeline',
    'questions/featured':              'question',
    'questions/unanswered':            'question',
    'questions/no-answers':            'question',
    'revisions/*':                     'revision',
    'search':                          'question',
    'search/advanced':                 'question',
    'similar':                         'question',
    'sites':                           'site',
    'suggested-edits':                 'suggested_edit',
    'suggested-edits/*':               'suggested_edit',
    'tags':                            'tag',
    'tags/*/info':                     'tag',
    'tags/*/faq':                      'question',
    'tags/*/related':                  'tag',
    'tags/*/synonyms':                 'tag_synonym',
    'tags/*/top-answerers/*':          'tag_score',
    'tags/*/top-askers/*':             'tag_score',
    'tags/*/wikis':                    'tag_wiki',
    'tags/moderator-only':             'tag',
    'tags/required':                   'tag',
    'tags/synonyms':                   'tag_synonym',
    'users':                           'user',
    'users/*':                         'user',
    'users/*/answers':                 'answer',
    'users/*/associated':              'network_user',
    'users/*/badges':                  'badge',
    'users/*/comments':                'comment',
    'users/*/comments/*':              'comment',
    'users/*/favorites':               'question',
    'users/*/inbox':                   'inbox_item',
    'users/*/inbox-item':              'inbox_item',
    'users/*/mentioned':               'comment',
    'users/*/merges':                  'account_merge',
    'users/*/notifications':           'notification',
    'users/*/notifications/unread':    'notification',
    'users/*/privileges':              'privilege',
    'users/*/questions':               'question',
    'users/*/questions/featured':      'question',
    'users/*/questions/no-answers':    'question',
    'users/*/questions/unaccepted':    'question',
    'users/*/questions/unanswered':    'question',
    'users/*/reputation':              'reputation',
    'users/*/reputation-history':      'reputation_history',
    'users/*/reputation-history/full': 'reputation_history',
    'users/*/suggested-edits':         'suggested_edit',
    'users/*/tags':                    'tag',
    'users/*/tags/*/top-answers':      'answer',
    'users/*/tags/*/top-questions':    'question',
    'users/*/timeline':                'user_timeline',
    'users/*/top-answer-tags':         'top_tag',
    'users/*/top-question-tags':       'top_tag',
    'users/*/write-permissions':       'write_permission',
    'users/moderators':                'user',
    'users/moderators/elected':        'user',
}

## Returns the string representation of an inbox item.
# @param item a dictionary containing the inbox item
# @return the string representation of the item
def inbox_item_str(item):
    if item['item_type'] == 'comment':
        return 
    #, chat_message, new_answer, careers_message, careers_invitations, meta_question, or post_notice'

## Provides information about each type represented in the API.
#
# The following information is recorded for each type:
# - the field that contains a unique identifier for the type (`id_field`)
# - [optional] the field that contains the string representation of the item (`str_field`) -
#   if none is supplied, then the `id_field` is used instead (also a function may be supplied
#   that accepts a dictionary of the objetc's type and returns the string to use)
# - [optional] a list of all fields that contain timestamps (`date_fields`)
# - [optional] a mapping of any fields that are types themselves to the appropriate type (`type_map`)
#
# The following types are missing from this list for the specified reasons:
# - `badge_count` - extremely simple type
# - `styling` - extremely simple type
# - `write_permission` - extremely simple type
TYPE_INFORMATION = {
    'access_token': {
        'id_field':    'access_token',
        'date_fields': ['expires_on_date',],
    },
    'account_merge': {
        'date_fields': ['merge_date',],
    },
    'answer': {
        'id_field':    'answer_id',
        'str_field':   'title',
        'date_fields': ['community_owned_date', 'creation_date', 'last_activity_date', 'last_edit_date', 'locked_date',],
        'type_map':    {'owner': 'shallow_user',},
    },
    'badge': {
        'id_field':    'badge_id',
        'str_field':   'name',
        'type_map':    {'user': 'shallow_user',},
    },
    'comment': {
        'id_field':    'comment_id',
        'str_field':   'body',
        'date_fields': ['creation_date',],
        'type_map':    {'owner': 'shallow_user', 'reply_to_user': 'shallow_user',},
    },
    'error': {
        'id_field':    'error_id',
        'str_field':   'error_description',
    },
    'event': {
        'str_field':   'excerpt',
        'date_fields': ['creation_date',],
    },
    'inbox_item': {
        'str_field':   'title',
        'date_fields': ['creation_date',],
        'type_map':    {'site': 'site',},
    },
    'info': {
        'type_map':    {'site': 'site',},
    },
    'migration_info': {
        'date_fields': ['on_date',],
        'type_map':    {'other_site': 'site',},
    },
    'network_user': {
        'id_field':    'account_id',
        'str_field':   'site_name',
        'date_fields': ['creation_date', 'last_access_date',],
    },
    'notice': {
        'date_fields': ['creation_date',],
    },
    'notification': {
        'str_field':   'notification_type',
        'date_fields': ['creation_date',],
        'type_map':    {'site': 'site',},
    },
    'post': {
        'id_field':    'post_id',
        'str_field':   'post_type',
        'date_fields': ['creation_date', 'last_activity_date', 'last_edit_date',],
        'type_map':    {'comments': 'comment', 'owner': 'shallow_user'},
    },
    'privilege': {
        'str_field':   'short_description',
    },
    'question': {
        'id_field':    'question_id',
        'str_field':   'title',
        'date_fields': ['bounty_closes_date', 'closed_date', 'community_owned_date', 'creation_date', 'last_activity_date', 'last_edit_date', 'locked_date', 'protected_date',],
        'type_map':    {'answers': 'answer', 'comments': 'comment', 'migrated_from': 'migration_info', 'migrated_to': 'migration_info', 'owner': 'shallow_user',},
    },
    'question_timeline': {
        'str_field':   'timeline_type',
        'date_fields': ['creation_date',],
        'type_map':    {'owner': 'shallow_user', 'user': 'shallow_user',},
    },
    'related_site': {
        'id_field':    'api_site_parameter',
        'str_field':   'name',
    },
    'reputation': {
        'str_field':   'vote_type',
        'date_fields': ['on_date',],
    },
    'reputation_history': {
        'str_field':   'reputation_history_type',
        'date_fields': ['creation_date',],
    },
    'revision': {
        'id_field':    'revision_guid',
        'str_field':   'comment',
        'date_fields': ['creation_date',],
        'type_map':    {'user': 'shallow_user',},
    },
    'shallow_user': {
        'id_field':    'user_id',
        'str_field':   'display_name',
    },
    'site': {
        'id_field':    'api_site_parameter',
        'str_field':   'name',
        'date_fields': ['closed_beta_date', 'launch_date', 'open_beta_date',],
        'type_map':    {'related_sites': 'related-site', 'styling': 'styling',},
    },
    'suggested_edit': {
        'id_field':    'suggested_edit_id',
        'str_field':   'title',
        'date_fields': ['approval_date', 'creation_date', 'rejection_date',],
        'type_map':    {'proposing_user': 'shallow_user',},
    },
    'tag': {
        'id_field':    'name',
        'date_fields': ['last_activity_date',],
    },
    'tag_score': {
        'type_map':    {'user': 'shallow_user',},
    },
    'tag_synonym': {
        'date_fields': ['creation_date', 'last_applied_date',],
    },
    'tag_wiki': {
        'str_field':   'tag_name',
        'date_fields': ['body_last_edit_date', 'excerpt_last_edit_date',],
        'type_map':    {'last_body_editor': 'shallow_user', 'last_excerpt_editor': 'shallow_user',},
    },
    'top_tag': {
        'str_field':   'tag_name',
    },
    'user': {
        'id_field':    'user_id',
        'str_field':   'display_name',
        'date_fields': ['creation_date', 'last_access_date', 'last_modified_date', 'timed_penalty_date',],
        'type_map':    {'badge_counts': 'badge_count',},
    },
    'user_timeline': {
        'str_field':   'timeline_type',
        'date_fields': ['creation_date',],
    },
}