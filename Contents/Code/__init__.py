####################################################################################################
#                                                                                                  #
#                                     SpankBang Plex Channel                                       #
#                                                                                                  #
####################################################################################################
import messages
import bookmarks
from updater import Updater
from DumbTools import DumbKeyboard

TITLE = 'SpankBang'
PREFIX = '/video/spankbang'
BASE_URL = 'http://spankbang.com'

ICON = 'icon-default.png'
ICON_BM = 'icon-bookmarks.png'
ICON_BM_ADD = 'icon-add-bookmark.png'
ICON_BM_REMOVE = 'icon-remove-bookmark.png'
ICON_CAT = 'icon-category.png'
ICON_POP = 'icon-popular.png'
ICON_TREND = 'icon-trending.png'
ICON_NEW = 'icon-newest.png'
ICON_TIME = 'icon-time.png'
ICON_STAR = 'icon-star.png'
ICON_LIKED = 'icon-liked.png'
ICON_VIDEO = 'icon-video.png'
ICON_PHOTOALBUM = 'icon-photoalbum.png'
ICON_SEARCH = 'icon-search.png'
ART = 'art-default.jpg'

ORDER = [
    ('order=trending', 'Trending Videos'), ('order=popular', 'Most Popular Videos'),
    ('order=rated', 'Most Liked Videos'), ('order=longest', 'Longest Videos')
    ]
PERIOD = [
    ('', 'Any Time'), ('period=today', 'Today'), ('period=week', 'This Week'),
    ('period=month', 'This Month'), ('period=season', 'Three Months'),
    ('period=year', 'This Year')
    ]
SEARCH_ORDER = [
    ('order=top', 'Popular Videos'), ('order=new', 'New Videos'), ('order=hot', 'Hot Videos')
    ]
SEARCH_LENGTH = [
    ('length=long', 'Long (20min+)'), ('length=medium', 'Medium (5-20min)'),
    ('length=short', 'Short (1-5min)')
    ]

MC = messages.NewMessageContainer(PREFIX, TITLE)
BM = bookmarks.Bookmark(TITLE, PREFIX, ICON_BM_ADD, ICON_BM_REMOVE)

####################################################################################################
def Start():
    HTTP.CacheTime = CACHE_1HOUR

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

    PhotoAlbumObject.thumb = R(ICON_PHOTOALBUM)

    # migrate old bookmarks to new bookmark class
    if not Dict['bm_upgrade']:
        if not Dict['Bookmarks']:
            Dict['bm_upgrade'] = True
        else:
            migrate_old_bm_to_new()
            Dict['bm_upgrade'] = True
        Dict.Save()

####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():
    """Setup Main Menu, Includes Updater"""

    oc = ObjectContainer(title2=TITLE, no_cache=True)

    Updater(PREFIX + '/updater', oc)

    oc.add(DirectoryObject(
        key=Callback(CategoryList, title='Categories'), title='Categories', thumb=R(ICON_CAT)))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList, title='Trending', href='/trending_videos/', page=1),
        title='Trending', thumb=R(ICON_TREND)))
    oc.add(DirectoryObject(
        key=Callback(DirectoryList, title='New', href='/new_videos/', page=1),
        title='New', thumb=R(ICON_NEW)))
    oc.add(DirectoryObject(
        key=Callback(PeriodList, title='Popular', href='/most_popular/?'),
        title='Popular', thumb=R(ICON_POP)))
    oc.add(DirectoryObject(
        key=Callback(PeriodList, title='Most Liked', href='/top_rated/?'),
        title='Most Liked', thumb=R(ICON_LIKED)))
    oc.add(DirectoryObject(
        key=Callback(PeriodList, title='Longest', href='/longest_videos/?'),
        title='Longest', thumb=R(ICON_TIME)))
    oc.add(DirectoryObject(
        key=Callback(PornstarsList, href='/pornstars', page=1),
        title='Pornstars', thumb=R(ICON_STAR)))

    oc.add(DirectoryObject(key=Callback(MyBookmarks), title='My Bookmarks', thumb=R(ICON_BM)))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R(ICON_SEARCH))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search),
            title='Search', summary='Search SpankBang',
            prompt='Search for...', thumb=R(ICON_SEARCH)
            ))

    return oc

####################################################################################################
@route(PREFIX + '/categorylist')
def CategoryList(title):
    """Setup Category List"""

    oc = ObjectContainer(title2=title)

    url = BASE_URL + '/categories'

    html = HTML.ElementFromURL(url)
    for genre_node in html.xpath('//h1[text()="All porn categories"]/following-sibling::div[@class="categories"]/a'):
        chref = genre_node.get('href').split('?')[0]
        img = genre_node.xpath('./img')[0].get('src')
        name = genre_node.xpath('./span/text()')[0]
        oc.add(DirectoryObject(
            key=Callback(HDOptList, title='Category | %s' %name, href=chref),
            title=name, summary='%s Genre List ' %name, thumb=BASE_URL + img
            ))

    return oc

####################################################################################################
@route(PREFIX + '/pornstars/list', page=int)
def PornstarsList(href, page):
    oc = ObjectContainer(title2='Pornstars')
    html = HTML.ElementFromURL(BASE_URL + href)
    for a in html.xpath('//a[contains(@href, "/pornstar/")]'):
        if a.xpath('./img'):
            title = a.xpath('./img/@title')[0].strip()
            thumb = a.xpath('./img/@src')[0]
            thumb = 'http:' + thumb if thumb.startswith('//') else thumb

            views = a.xpath('.//span[@class="views"]/text()')[0].strip()
            videos = a.xpath('.//span[@class="videos"]/text()')[0].strip()

            oc.add(DirectoryObject(
                key=Callback(PornstarPage, title=title, href=a.get('href'), pid=String.Quote(title, True), thumb=thumb),
                title=title, thumb=thumb, tagline="{} Views, {} Videos".format(views, videos)))
    if len(oc) != 0:
        nextpg = html.xpath('//li[@class="next"]/a')
        if nextpg:
            npage = page+1
            oc.add(NextPageObject(
                key=Callback(PornstarsList, href=nextpg[0].get('href'), page=npage),
                title='Page {} >>'.format(npage)))
    return oc

####################################################################################################
@route(PREFIX + '/pornstar/page')
def PornstarPage(title, href, pid, thumb):
    """Link to video list and bookmark option"""

    oc = ObjectContainer(title2=title, no_cache=True)

    oc.add(DirectoryObject(
        key=Callback(DirectoryList, title='Videos', href=href, page=1),
        title='Videos', thumb=R(ICON_VIDEO)
        ))

    info = {
        'title': title, 'thumb': thumb, 'href': href, 'category': 'Pornstar',
        'id': pid, 'duration': 'NA', 'summary': 'NA'
        }

    BM.add_remove_bookmark(oc, dict(info))

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
@route(PREFIX + '/periodlist', search=bool)
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

    query = query.strip()
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
        return MC.message_container('Bookmarks', 'Bookmark List Empty')

    oc = ObjectContainer(title2='My Bookmarks', no_cache=True)

    for key in sorted(bm.keys()):
        if len(bm[key]) == 0:
            del Dict['Bookmarks'][key]
            Dict.Save()
        else:
            oc.add(DirectoryObject(
                key=Callback(BookmarksSub, category=key),
                title=key, summary='Display Pornstar Bookmarks',
                thumb=R(ICON_STAR) if key.lower() == 'pornstar' else R('icon-%s.png' %key.lower())
                ))

    if len(oc) > 0:
        return oc
    return MC.message_container('Bookmarks', 'Bookmark List Empty')

####################################################################################################
@route(PREFIX + '/bookmark/sub')
def BookmarksSub(category):
    """List Bookmarks Alphabetically"""

    bm = Dict['Bookmarks']
    if not category in bm.keys():
        return MC.message_container('Error',
            '%s Bookmarks list is dirty, or no %s Bookmark list exist.' %(category, category))

    oc = ObjectContainer(title2='My Bookmarks / %s' %category, no_cache=True)

    for bookmark in sorted(bm[category], key=lambda k: k['title']):
        title = bookmark['title']
        thumb = bookmark['thumb']
        href = bookmark['href']
        item_id = bookmark['id']
        duration = bookmark['duration']

        if category == 'Video':
            video_info = {
                'id': item_id, 'title': title, 'duration': int(duration),
                'thumb': thumb, 'url': BASE_URL + href, 'href': href, 'category': category
                }
            oc.add(DirectoryObject(
                key=Callback(VideoPage, video_info=video_info),
                title=title, thumb=thumb
                ))
        elif category == 'Pornstar':
            oc.add(DirectoryObject(
                key=Callback(PornstarPage, title=title, href=href, pid=item_id, thumb=thumb),
                title=title, thumb=thumb
                ))

    if len(oc) > 0:
        return oc
    return MC.message_container('Bookmarks', '%s Bookmarks list Empty' %category)

####################################################################################################
def migrate_old_bm_to_new():

    bm = Dict['Bookmarks']
    for b in sorted(bm.keys()):
        url = bm[b]['url']
        href = url.split(url.split('/')[2])[-1]
        bid = bm[b]['id']
        BM.add(
            bm[b]['title'], href, bm[b]['thumb'], 'Video',
            bid, bm[b]['duration'], bm[b]['summary']
            )

        if (True if bid in bm.keys() else False) if bm else False:
            del Dict['Bookmarks'][bid]

    return

####################################################################################################
@route(PREFIX + '/directorylist', page=int)
def DirectoryList(title, href, page):
    """List Videos by page"""

    url = BASE_URL + href

    html = HTML.ElementFromURL(url)

    if html.xpath('//h1[text()="No results"]'):
        search = url.split('/')[-1]
        return MC.message_container('Search Warning',
            'Sorry... your search for \"%s\" returned no videos. Repeat your search with another keyword. Search only works with english words.' %search)

    nextpg_node = html.xpath('//li[@class="next"]/a')
    if page == 1 and not nextpg_node:
        main_title = title
    else:
        main_title = '%s | Page %i' %(title, page) if nextpg_node else '%s | Page %i | Last Page' %(title, page)

    oc = ObjectContainer(title2=main_title, view_group='Coverflow')

    for node in html.xpath('//div[@class="video-list video-rotate"]/div[@class="video-item"]'):
        a_node = node.xpath('./a')[0]
        vhref = a_node.get('href')
        vurl = BASE_URL + vhref
        thumb = 'http:' + a_node.xpath('./img/@src')[0]
        name = a_node.xpath('./img/@alt')[0].strip()
        hd_node = a_node.xpath('./span[@class="i-hd"]')
        if hd_node:
            vtitle = name + ' (HD)'
        else:
            vtitle = name
        duration = 60000 * int(a_node.xpath('./span[@class="i-len"]')[0].text_content().strip())
        vid = vhref.split('/')[-1]

        video_info = {
            'id': vid, 'title': vtitle, 'duration': duration, 'thumb': thumb,
            'href': vhref, 'url': vurl, 'category': 'Video'
            }

        oc.add(DirectoryObject(key=Callback(VideoPage, video_info=video_info), title=vtitle, thumb=thumb))

    if nextpg_node:
        href = nextpg_node[0].get('href')
        oc.add(NextPageObject(
            key=Callback(DirectoryList, title=title, href=href, page=page+1),
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
    match = BM.bookmark_exist(item_id=video_info['id'], category='Video')
    video_removed = html.xpath('//div[@id="video_removed"]')

    if match and video_removed:
        header = video_info['title']
        message = 'This video is no longer available.'
    elif not match and video_removed:
        return MC.message_container('Warning', 'This video is no longer available.')

    oc = ObjectContainer(title2=video_info['title'], header=header, message=message, no_cache=True)

    if not video_removed:
        for node in html.xpath('//section[@class="details"]'):
            if not 'summary' in video_info.keys():
                summary = 'NA'
                summary_node = node.xpath('.//p/text()')
                if len(summary_node) > 1:
                    temp_summary = summary_node[1].strip()
                    if temp_summary != 'Category:':
                        summary = temp_summary
                video_info.update({'summary': summary})
            if not 'genres' in video_info.keys():
                video_info.update({'genres': node.xpath('.//a[contains(@href, "/category/")]/text()')})

        oc.add(VideoClipObject(
            title=video_info['title'], summary=video_info['summary'], genres=video_info['genres'],
            duration=video_info['duration'], thumb=video_info['thumb'], url=video_info['url'],
            ))

        oc.add(PhotoAlbumObject(
            key=Callback(PhotoBin, title=video_info['title'], thumb=video_info['thumb'], url=video_info['url']),
            rating_key = video_info['url']+'/thumbs', source_title='SpankBang',
            title='Video Thumbs', art=R(ART)
            ))


    similar_node = html.xpath('//div[@class="video-similar video-rotate"]')
    if similar_node:
        info = []
        for node in similar_node[0].xpath('./div[@class="video-item"]'):
            a_node = node.xpath('./a')[0]
            vhref = a_node.get('href')
            vurl = BASE_URL + vhref
            vid = vhref.split('/')[-1]
            thumb = 'http:' + a_node.xpath('./img/@src')[0]
            name = a_node.xpath('./img/@alt')[0].strip()
            duration = 1000 * int(a_node.xpath('./span[@class="len"]/text()')[0].strip())

            hd_node = node.xpath('./span[@class="i-hd"]')
            if hd_node:
                name = name + ' (HD)'

            info.append({
                'id': vid, 'title': name, 'duration': duration, 'thumb': thumb,
                'url': vurl, 'href': vhref, 'category': 'Video'
                })

        oc.add(DirectoryObject(
            key=Callback(SimilarVideos, title='Similar Videos', info=info),
            title='Similar Videos', thumb=info[0]['thumb']))

    pstar_list = html.xpath('//a[contains(@href, "/pornstar/")]')
    if pstar_list:
        plstar = []
        for ps in pstar_list:
            pnstar = ps.text
            phstar = ps.get('href')
            plstar.append((pnstar, phstar))
        if len(plstar) == 1:
            pid = String.Quote(plstar[0][0].lower(), usePlus=True)
            pthumb = HTTP.Request('http://www.cliphunter.com/a/modelthumb?name=%s' %pid).content
            oc.add(DirectoryObject(
                key=Callback(PornstarPage, title=plstar[0][0], href=plstar[0][1], pid=pid, thumb=pthumb),
                title=plstar[0][0], thumb=pthumb
                ))
        elif len(plstar) > 1:
            oc.add(DirectoryObject(
                key=Callback(PornstarList, title=video_info['title'], plstar=plstar),
                title='Pornstars', thumb=R(ICON_STAR)
                ))

    BM.add_remove_bookmark(oc, dict(video_info))

    return oc

####################################################################################################
@route(PREFIX + '/similarvideos', info=list)
def SimilarVideos(title, info):
    """Display similar videos"""

    oc = ObjectContainer(title2=title)

    for item in info:
        oc.add(DirectoryObject(
            key=Callback(VideoPage, video_info=item),
            title=item['title'], thumb=item['thumb']
            ))

    return oc

####################################################################################################
@route(PREFIX + '/pstar/list', plstar=list)
def PornstarList(title, plstar):
    """Display Adult stars in video"""

    oc = ObjectContainer(title2='Pornstars in %s' %title)
    for n, h in plstar:
        pid = String.Quote(n.lower(), usePlus=True)
        pthumb = HTTP.Request('http://www.cliphunter.com/a/modelthumb?name=%s' %pid).content
        oc.add(DirectoryObject(
            key=Callback(PornstarPage, title=n, href=h, pid=pid, thumb=pthumb),
            title=n, thumb=pthumb
            ))

    return oc

####################################################################################################
@route(PREFIX + '/video/thumbs/bin')
def PhotoBin(title, thumb, url):
    """Create PhotoAlbum for photos in href"""

    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url)
    for img in html.xpath('//figure[@class="thumbnails"]/img'):
        src = img.get('src')
        title = img.get('title')
        oc.add(CreatePhotoObject(
            title=title.replace('Watch from ', ''),
            url=src if src.startswith('http') else ('http:' + src)
            ))

    return oc

####################################################################################################
@route(PREFIX + '/create/photo/object', include_container=bool)
def CreatePhotoObject(title, url, include_container=False, *args, **kwargs):
    """create photo object"""

    photo_object = PhotoObject(
        key=Callback(CreatePhotoObject, title=title, url=url, include_container=True),
        rating_key=url, source_title='SpankBang', title=title, thumb=url, art=R(ART),
        items=[MediaObject(parts=[PartObject(key=url)])]
        )

    if include_container:
        return ObjectContainer(objects=[photo_object])
    return photo_object
