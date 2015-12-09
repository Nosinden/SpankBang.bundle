####################################################################################################
#                                                                                                  #
#                                     SpankBang Plex Channel                                       #
#                                                                                                  #
####################################################################################################
#from updater import Updater

TITLE = L('title')
PREFIX = '/video/spankbang'
BASE_URL = 'http://spankbang.com'

ICON = 'icon-default.png'
ICON_BM = 'icon-bookmarks.png'
ICON_BM_ADD = 'icon-add-bookmark.png'
ICON_BM_REMOVE = 'icon-remove-bookmark.png'
ICON_LIST = 'icon-list.png'
ICON_POP = 'icon-popular.png'
ICON_LIKED = 'icon-liked.png'
ART = 'art-default.jpg'

ORDER = [
    ('order=trending', 'Trending Videos'), ('order=popular', 'Most Popular Videos'),
    ('order=rated', 'Most Liked Videos'), ('order=longest', 'Longest Videos')
    ]
PERIOD = [
    ('period=today', 'Today'), ('period=week', 'This Week'), ('period=month', 'This Month'),
    ('period=season', 'Three Months'), ('period=year', 'This Year')
    ]
SEARCH_ORDER = [
    ('order=top', 'Popular Videos'), ('order=new', 'New Videos'), ('order=hot', 'Hot Videos')
    ]
SEARCH_LENGTH = [
    ('length=long', 'Long (20min+)'), ('length=medium', 'Medium (5-20min)'),
    ('length=short', 'Short (1-5min)')
    ]

####################################################################################################
def Start():
    HTTP.CacheTime = 300  # 5mins

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

    #ValidatePrefs()

####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
    """Setup Main Menu, Includes Updater"""

    oc = ObjectContainer(title2=TITLE)

    #Updater(PREFIX + '/updater', oc)

    oc.add(DirectoryObject(key=Callback(MainList, title='Explore'), title='Explore', thumb=R(ICON_LIST)))
    oc.add(DirectoryObject(key=Callback(MainList, title='Popular Videos'), title='Popular Videos', thumb=R(ICON_POP)))
    oc.add(DirectoryObject(key=Callback(MainList, title='Most Liked Videos'), title='Most Liked Videos', thumb=R(ICON_LIKED)))
    oc.add(DirectoryObject(key=Callback(MyBookmarks), title='My Bookmarks', thumb=R(ICON_BM)))
    #oc.add(PrefsObject(title='Preferences'))
    oc.add(InputDirectoryObject(
        key=Callback(Search),
        title='Search', summary='Search SpankBang', prompt='Search for...', thumb=R('icon-search.png')))

    return oc

####################################################################################################
@route(PREFIX + '/validateprefs')
def ValidatePrefs():
    """
    Validate Prefs
    No Prefs to validate yet
    """

####################################################################################################
@route(PREFIX + '/mainlist')
def MainList(title):
    """Create sub list for Explore, Popular Videos, and Most liked Videos"""

    oc = ObjectContainer(title2=title)

    if title == 'Explore':
        oc.add(DirectoryObject(
            key=Callback(CategoryList, title='%s | Categories' %title), title='Categories'))
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, title='%s | New Videos' %title, href='/new_videos/', page=1),
            title='New Videos'))
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, title='%s | Hot & Trending Videos' %title, href='/trending_videos/', page=1),
            title='Hot & Trending Videos'))
        oc.add(DirectoryObject(
            key=Callback(PeriodList, title='%s | Longest Videos' %title, href='/longest_videos/?'),
            title='Longest Videos'))

        return oc
    elif title == 'Popular Videos':
        href = '/most_popular/?'
    elif title == 'Most Liked Videos':
        href = '/top_rated/?'

    return PeriodList(title=title, href=href)

####################################################################################################
@route(PREFIX + '/categorylist')
def CategoryList(title):
    """Setup Category List"""

    oc = ObjectContainer(title2=title)

    url = BASE_URL + '/categories'

    html = HTML.ElementFromURL(url)
    for genre_node in html.xpath('//h1[@class="alt"][text()="All porn categories"]/following-sibling::div[@class="categories"]/a'):
        chref = genre_node.get('href')
        img = genre_node.xpath('./img')[0].get('src')
        name = genre_node.xpath('./span/text()')[0]
        oc.add(DirectoryObject(
            key=Callback(HDOptList, title='Category | %s' %name, href=chref),
            title=name, summary='%s Genre List ' %name, thumb=BASE_URL + img
            ))

    return oc

####################################################################################################
@route(PREFIX + '/hd-opt-list')
def HDOptList(title, href, search=False):
    """
    Setup hd and all list
    All, and HD
    """

    oc = ObjectContainer(title2=title)

    name = title.split('|')[1].strip()

    if not search:
        oc.add(DirectoryObject(
            key=Callback(CategoryOptList, title='%s | All' %title, href='%s?hd=0' %href),
            title='All (SD & HD)'))
        oc.add(DirectoryObject(
            key=Callback(CategoryOptList, title='%s | HD' %title, href='%s?hd=1' %href),
            title='HD (HD Only)'))
    else:
        oc.add(DirectoryObject(
            key=Callback(SearchOptList, title='%s | All' %title, href='%s?hd=0' %href),
            title='All (SD & HD)'))
        oc.add(DirectoryObject(
            key=Callback(SearchOptList, title='%s | HD' %title, href='%s?hd=1' %href),
            title='HD (HD Only)'))

    return oc

####################################################################################################
@route(PREFIX + '/category-opt-list')
def CategoryOptList(title, href):
    """
    Setup category option list
    New Videos, Trending Videos, Most Popular Videos, Most Liked Videos, Longest Videos
    """

    oc = ObjectContainer(title2=title)

    oc.add(DirectoryObject(
        key=Callback(DirectoryList, title='%s | New Videos' %title, href=href, page=1),
        title='New Videos'))
    OrderList(title, href, oc)

    return oc

####################################################################################################
@route(PREFIX + '/periodlist')
def PeriodList(title, href, search=False):
    """
    Setup period option
    Today, This Week, This Month, Three Months, This Year
    """

    oc = ObjectContainer(title2=title)

    for phref, p in PERIOD:
        if not search:
            oc.add(DirectoryObject(
                key=Callback(DirectoryList, title='%s | %s' %(title, p), href='%s&%s' %(href, phref), page=1),
                title=p))
        else:
            oc.add(DirectoryObject(
                key=Callback(SearchCategoryList, title='%s | %s | Categories' %(title, p), href='%s&%s' %(href, phref)),
                title=p))

    return oc

####################################################################################################
@route(PREFIX + 'orderlist')
def OrderList(title, href, oc=None):
    """
    Setup category order options
    Trending Videos, Most Popular Videos, Most Liked Videos, Longest Videos
    """
    if not oc:
        oc = ObjectContainer(title2=title)

    for ohref, o in ORDER:
        if 'trending' in ohref:
            oc.add(DirectoryObject(
                key=Callback(DirectoryList, title='%s | %s' %(title, o), href='%s&%s' %(href, ohref), page=1),
                title=o))
        else:
            oc.add(DirectoryObject(
                key=Callback(PeriodList, title='%s | %s' %(title, o), href='%s&%s' %(href, ohref)),
                title=o))

    return oc

####################################################################################################
@route(PREFIX + '/search-opt-list')
def SearchOptList(title, href):
    """
    Setup Search option list
    All, Relevant Videos, Categories, Length
    """

    oc = ObjectContainer(title2=title)

    oc.add(DirectoryObject(
        key=Callback(SearchRPNHList, title='%s | Relevant' %title, href=href),
        title='Relevant Videos'))

    for shref, s in SEARCH_ORDER:
        name = s.replace('Videos', '').strip()
        oc.add(DirectoryObject(
            key=Callback(SearchRPNHList, title='%s | %s' %(title, name), href='%s&%s' %(href, shref)),
            title=s))

    return oc

####################################################################################################
@route(PREFIX + '/search-rpnh-list')
def SearchRPNHList(title, href):
    """
    Setup Relevant Video Directory
    All Relevant, Categories, Length
    """

    kind = title.split('|')[-1].strip()

    oc = ObjectContainer(title2=title)

    oc.add(DirectoryObject(
        key=Callback(DirectoryList, title='%s | All' %title, href=href, page=1),
        title='All %s Videos' %kind))

    if (kind == 'Popular' or kind == 'Hot'):
        oc.add(DirectoryObject(
            key=Callback(PeriodList, title='%s | Date' %title, href=href, search=True),
            title='Limit by Date'))

    oc.add(DirectoryObject(
        key=Callback(SearchCategoryList, title='%s | Categories' %title, href=href),
        title='Limit by Categories'))
    oc.add(DirectoryObject(
        key=Callback(SearchLengthList, title='%s | Length' %title, href=href),
        title='Limit by Length'))

    return oc

####################################################################################################
@route(PREFIX + '/search-category-list')
def SearchCategoryList(title, href):
    """Parse top Categories for Search"""

    oc = ObjectContainer(title2=title)

    oc.add(DirectoryObject(
        key=Callback(SearchLengthList, title=title.split(' | Categories')[0], href=href),
        title='Any Category'))

    url = BASE_URL + href
    html = HTML.ElementFromURL(url)
    title = title.replace('Categories', 'Category')
    for c in html.xpath('//p[@class="t cat tt"]/a'):
        chref = c.get('href').replace(' ', '%20')
        name = c.text.strip()
        oc.add(DirectoryObject(
            key=Callback(SearchLengthList, title='%s | %s' %(title, name), href=chref),
            title=name))

    return oc

####################################################################################################
@route(PREFIX + '/search-length-list')
def SearchLengthList(title, href):
    """Setup sort by video length"""

    oc = ObjectContainer(title2=title)

    oc.add(DirectoryObject(
        key=Callback(DirectoryList, title=title, href=href, page=1),
        title='Any Length'))

    for lhref, l in SEARCH_LENGTH:
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, title='%s | %s' %(title, l), href='%s&%s' %(href, lhref), page=1),
            title=l))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Search SpankBang"""

    search = Regex('[^a-zA-Z0-9-_*.]').sub(' ', String.StripDiacritics(query))
    href = '/s/%s/' %String.Quote(search, usePlus=True)
    title = 'Search | %s' %search

    return HDOptList(title, href, True)

####################################################################################################
@route(PREFIX + '/bookmarks')
def MyBookmarks():
    """List Custom Bookmarks"""
    bm = Dict['Bookmarks']
    if not bm:
        return MessageContainer('Bookmarks', 'Bookmark List Empty')

    oc = ObjectContainer(title2='My Bookmarks')

    for b in sorted(Dict['Bookmarks'].keys()):
        summary = bm[b]['summary']
        video_info = {
            'id': bm[b]['id'],
            'title': bm[b]['title'],
            'duration': bm[b]['duration'],
            'thumb': bm[b]['thumb'],
            'url': bm[b]['url']
            }

        oc.add(DirectoryObject(
            key=Callback(VideoPage, video_info=video_info),
            title=video_info['title'], summary=summary if summary else None,
            tagline=str(Datetime.Delta(milliseconds=video_info['duration'])),
            thumb=video_info['thumb']))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Bookmarks', 'Bookmark List Empty')

####################################################################################################
@route(PREFIX + '/directorylist', page=int)
def DirectoryList(title, href, page):
    """List Videos by page"""

    url = BASE_URL + href

    html = HTML.ElementFromURL(url)

    if html.xpath('//main[@class="remodal-bg"]//h1[text()="No results"]'):
        search = url.split('/')[-1]
        return MessageContainer('Search Warning',
            'Sorry... your search for \"%s\" returned no videos. Repeat your search with another keyword. Search only works with english words.' %search)

    nextpg_node = html.xpath('//nav[@class="paginate-bar"]/a[@class="next"]')
    if page == 1 and not nextpg_node:
        main_title = title
    else:
        main_title = '%s | Page %i' %(title, page) if nextpg_node else '%s | Page %i | Last Page' %(title, page)

    oc = ObjectContainer(title2=main_title)

    for node in html.xpath('//div[@class="video-list video-rotate"]/div[@class="video-item"]'):
        a_node = node.xpath('./a')[0]
        vhref = BASE_URL + a_node.get('href')
        thumb = 'http:' + a_node.xpath('./img/@src')[0]
        name = a_node.xpath('./img/@alt')[0].strip()
        hd_node = a_node.xpath('./span[@class="i-hd"]')
        if hd_node:
            vtitle = name + ' (HD)'
        else:
            vtitle = name
        duration = 60000 * int(a_node.xpath('./span[@class="len"]/text()')[0].strip())
        vid = vhref.split('/')[-1]

        video_info = {
            'id': vid,
            'title': vtitle,
            'duration': duration,
            'thumb': thumb,
            'url': vhref
            }

        oc.add(DirectoryObject(key=Callback(VideoPage, video_info=video_info), title=vtitle, thumb=thumb))

    if nextpg_node:
        href = nextpg_node[0].get('href')
        nextpg = int(href.split('/')[-2])
        oc.add(NextPageObject(
            key=Callback(DirectoryList, title=title, href=href, page=nextpg),
            title='Next Page>>'))

    return oc

####################################################################################################
@route(PREFIX + '/videopage', video_info=dict)
def VideoPage(video_info):
    """
    Video Sub Page
    Includes Similar Videos and Bookmark Option
    """

    html = HTML.ElementFromURL(video_info['url'])

    bm = Dict['Bookmarks']
    header = None
    message = None
    match = ((True if video_info['id'] in bm else False) if bm else False)
    video_removed = html.xpath('//div[@id="video_removed"]')

    if match and video_removed:
        header = video_info['title']
        message = 'This video is no longer available.'
    elif not match and video_removed:
        return MessageContainer('Warning', 'This video is no longer available.')

    oc = ObjectContainer(title2=video_info['title'], header=header, message=message)

    if not video_removed:
        oc.add(VideoClipObject(
            title=video_info['title'],
            duration=video_info['duration'],
            thumb=video_info['thumb'],
            url=video_info['url']))


    similar_node = html.xpath('//div[@class="video-similar video-rotate"]')
    if similar_node:
        for i, node in enumerate(similar_node[0].xpath('./div[@class="video-item"]')):
            a_node = node.xpath('./a')[0]
            vhref = BASE_URL + a_node.get('href')
            vid = vhref.split('/')[-1]
            thumb = 'http:' + a_node.xpath('./img/@src')[0]
            name = a_node.xpath('./img/@alt')[0].strip()
            duration = 1000 * int(a_node.xpath('./span[@class="len"]/text()')[0].strip())
            hd_node = node.xpath('./span[@class="i-hd"]')
            if hd_node:
                name = name + ' (HD)'

            if i == 0:
                info = [{
                    'id': vid, 'title': name, 'duration': duration,
                    'thumb': thumb, 'url': vhref}]
            else:
                info.append({
                    'id': vid, 'title': name, 'duration': duration,
                    'thumb': thumb, 'url': vhref})
        oc.add(DirectoryObject(
            key=Callback(SimilarVideos, title='Videos Similar to \"%s\"' %video_info['title'], info=info),
            title='Similar Videos', thumb=info[0]['thumb']))

    if match:
        oc.add(DirectoryObject(
            key=Callback(RemoveBookmark, video_info=video_info),
            title='Remove Bookmark',
            summary='Remove \"%s\" from your Bookmarks list.' %video_info['title'],
            thumb=R(ICON_BM_REMOVE)
            ))
    else:
        oc.add(DirectoryObject(
            key=Callback(AddBookmark, video_info=video_info),
            title='Add Bookmark',
            summary='Add \"%s\" to your Bookmarks list.' %video_info['title'],
            thumb=R(ICON_BM_ADD)
            ))

    return oc

####################################################################################################
@route(PREFIX + '/similarvideos', info=list)
def SimilarVideos(title, info):
    """Display similar videos"""

    oc = ObjectContainer(title2=title)

    for item in info:
        oc.add(DirectoryObject(
            key=Callback(VideoPage, video_info=item),
            title=item['title'], thumb=item['thumb']))

    return oc

####################################################################################################
@route(PREFIX + '/addbookmark', video_info=dict)
def AddBookmark(video_info):
    """Add Bookmark"""

    html = HTML.ElementFromURL(video_info['url'])

    bm = Dict['Bookmarks']
    summary = ''
    genres = ''
    for node in html.xpath('//div[@class="content"][@id="about"]/div[@class="info"]'):
        summary = node.xpath('./p[@class="desc"]/text()')
        if summary:
            summary = summary[0].strip()

        genres = node.xpath('./p[@class="cat"]')
        if genres:
            genre_list = genres[0].text_content().strip().replace('Category:', '').replace(' ', '').split(',')
            genres = ' '.join([g.replace(' ', '_') for g in genre_list])

    new_bookmark = {
        'id': video_info['id'], 'url': video_info['url'], 'title': video_info['title'],
        'duration': video_info['duration'], 'summary': summary if summary else '',
        'genres': genres if genres else '', 'thumb': video_info['thumb']
        }

    if not bm:
        Dict['Bookmarks'] = {video_info['id']: new_bookmark}
        Dict.Save()

        return MessageContainer('Bookmarks',
                '\"%s\" has been added to your bookmarks.' %video_info['title'])
    else:
        if video_info['url'] in bm.keys():
            return MessageContainer('Warning',
                '\"%s\" is already in your bookmarks.' %video_info['title'])
        else:
            Dict['Bookmarks'].update({video_info['id']: new_bookmark})
            Dict.Save()

            return MessageContainer('Bookmarks',
                '\"%s\" has been added to your bookmarks.' %video_info['title'])

####################################################################################################
@route(PREFIX + '/removebookmark', video_info=dict)
def RemoveBookmark(video_info):
    """Remove Bookmark from Bookmark Dictionary"""

    bm = Dict['Bookmarks']

    if (True if video_info['id'] in bm.keys() else False) if bm else False:
        del Dict['Bookmarks'][video_info['id']]
        Dict.Save()

        return MessageContainer('Remove Bookmark',
            '\"%s\" has been removed from your bookmarks.' %video_info['title'])
    else:
        return MessageContainer('Remove Bookmark Error',
            'ERROR \"%s\" cannot be removed. The Bookmark does not exist!' %video_info['title'])
