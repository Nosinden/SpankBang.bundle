####################################################################################################
#                                                                                                  #
#                               Plex Channel Bookmark Class                                        #
#                                                                                                  #
####################################################################################################

class Bookmark(object):

    def __init__(self, title, prefix, bm_add_icon=None, bm_rm_icon=None):
        self.title = title
        self.prefix = prefix
        self.bm_add_icon = bm_add_icon
        self.bm_rm_icon = bm_rm_icon

        Route.Connect(self.prefix + '/bookmark/add', self.add)
        Route.Connect(self.prefix + '/bookmark/remove', self.remove)

    ################################################################################################
    def bookmark_exist(self, item_id, category):
        """Test if bookmark exist"""

        bm = Dict['Bookmarks']
        return ((True if [b['id'] for b in bm[category] if b['id'] == item_id] else False) if category in bm.keys() else False) if bm else False

    ################################################################################################
    def message_container(self, header, message):
        """Setup MessageContainer depending on Platform"""

        if Client.Platform in ['Plex Home Theater', 'OpenPHT']:
            oc = ObjectContainer(title1=self.title, title2=header, no_cache=True,
                no_history=True, replace_parent=True)
            oc.add(PopupDirectoryObject(title=header, summary=message))

            return oc
        else:
            return MessageContainer(header, message)

    ################################################################################################
    def add(self, title, href, thumb, category, item_id, duration, summary):
        """Add bookmark to Dict"""

        new_bookmark = {
            'id': item_id, 'title': title, 'href': href, 'thumb': thumb,
            'category': category, 'duration': duration, 'summary': summary
            }
        bm = Dict['Bookmarks']

        if not bm:
            Dict['Bookmarks'] = {category: [new_bookmark]}
            Dict.Save()

            return self.message_container('Bookmarks',
                '\"%s\" has been added to your \"%s\" bookmark list.' %(title, category))
        elif category in bm.keys():
            if (True if [b['id'] for b in bm[category] if b['id'] == item_id] else False):

                return self.message_container('Warning',
                    '\"%s\" is already in your \"%s\" bookmark list.' %(title, category))
            else:
                temp = {}
                temp.setdefault(category, bm[category]).append(new_bookmark)
                Dict['Bookmarks'][category] = temp[category]
                Dict.Save()

                return self.message_container('\"%s\" Bookmark Added' %title,
                    '\"%s\" added to your \"%s\" bookmark list.' %(title, category))
        else:
            Dict['Bookmarks'].update({category: [new_bookmark]})
            Dict.Save()

            return self.message_container('\"%s\" Bookmark Added' %title,
                '\"%s\" added to your \"%s\" bookmark list.' %(title, category))

    ################################################################################################
    def remove(self, title, item_id, category):
        """
        Remove Bookmark from Bookmark Dictionary
        If Bookmark to remove is the last Bookmark in the Dictionary,
        then Remove the Bookmark Dictionary also
        """

        bm = Dict['Bookmarks']
        if self.bookmark_exist(item_id, category):
            bm_c = bm[category]
            for i in xrange(len(bm_c)):
                if bm_c[i]['id'] == item_id:
                    bm_c.pop(i)
                    Dict.Save()
                    break

            if len(bm_c) == 0:
                del bm_c
                Dict.Save()

                return self.message_container('Remove Bookmark',
                    '\"%s\" bookmark was the last, so removed \"%s\" bookmark section' %(title, category))
            else:
                return self.message_container('Remove Bookmark',
                    '\"%s\" removed from your \"%s\" bookmark list.' %(title, category))
        elif Client.Platform in ['Plex Home Theater', 'OpenPHT']:
            return self.message_container('\"%s\" Bookmark Removed' %title,
                '\"%s\" removed from your \"%s\" bookmark list.' %(title, category))
        else:
            return self.message_container('Error',
                'ERROR: \"%s\" not found in \"%s\" bookmark list.' %(title, category))

    ################################################################################################
    def add_remove_bookmark(self, oc, bm_info=dict):
        """Test if bookmark exist"""

        if self.bookmark_exist(bm_info['id'], bm_info['category']):
            oc.add(DirectoryObject(
                key=Callback(self.remove, title=bm_info['title'], item_id=bm_info['id'], category=bm_info['category']),
                title='Remove Bookmark',
                summary='Remove \"%s\" from your Bookmarks list.' %bm_info['title'],
                thumb=R(self.bm_rm_icon)
                ))
        else:
            oc.add(DirectoryObject(
                key=Callback(self.add,
                    title=bm_info['title'], thumb=bm_info['thumb'], href=bm_info['href'],
                    category=bm_info['category'], item_id=bm_info['id'],
                    duration=bm_info['duration'], summary=bm_info['summary']),
                title='Add Bookmark',
                summary='Add \"%s\" to your Bookmarks list.' %bm_info['title'],
                thumb=R(self.bm_add_icon)
                ))
