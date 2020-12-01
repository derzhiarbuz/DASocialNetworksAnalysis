# Created by Gubanov Alexander (aka Derzhiarbuz) at 29.04.2019
# Contacts: derzhiarbuz@gmail.com

import da_vk_api as vk
import re
import hashlib

VK_USER_META_FIELDS = 'screen_name, first_name, last_name, is_closed, about, activities, bdate, books, can_see_audio,' \
                      ' career, city, connections, contacts, counters, country, education, followers_count,' \
                      ' home_town, interests, deactivated, maiden_name, military, movies, music, nickname, occupation,' \
                      'personal, quotes, relatives, relation, schools, sex, status, tv, universities, verified'
VK_GROUP_META_FIELDS = 'screen_name, name, is_closed, deactivated, type, activity, age_limits, city, contacts, ' \
                       'counters, description, links, place, site, start_date, finish_date, status, trending'


def get_vk_users(user_ids, only_counters=False, batch_size=1000, async_load=False):
    i = 0
    n = 0
    k = 0
    error = None
    uids_str = ''
    users_data = []
    requests = []
    if async_load:
        n_requests = len(vk.get_tokens())
    else:
        n_requests = 1
    if only_counters:
        fields = 'counters, last_seen'
    else:
        fields = VK_USER_META_FIELDS
    for uid in user_ids:
        uids_str += str(uid)
        i += 1
        n += 1
        if i == batch_size or n == len(user_ids):
            requests.append({'user_ids': uids_str, 'fields': fields})
            k += 1
            if k == n_requests or n == len(user_ids):
                if async_load:
                    result = vk.api_batch('users.get', requests, ispost=True)
                    for users in result:
                        if vk.check(users):
                            users_data += users['response']
                        else:
                            error = users
                else:
                    for params in requests:
                        users = vk.api('users.get', params, ispost=True)
                        if vk.check(users):
                            users_data += users['response']
                        else:
                            error = users
            i = 0
            uids_str = ''
        else:
            uids_str += ','

    if error is None:
        return users_data
    else:
        return error


def get_vk_groups(group_ids, only_members=False):
    i = 0
    n = 0
    error = None
    gids_str = ''
    groups_data = []
    for gid in group_ids:
        gids_str += str(abs(gid))
        i += 1
        n += 1
        if i == 500 or n == len(group_ids):
            if only_members:
                groups = vk.api('groups.getById', {'group_ids': gids_str, 'fields': 'members_count'}, ispost=True)
            else:
                groups = vk.api('groups.getById', {'group_ids': gids_str, 'fields': VK_GROUP_META_FIELDS}, ispost=True)
            if vk.check(groups):
                groups_data += groups['response']
            else:
                error = groups
            i = 0
            gids_str = ''
        else:
            gids_str += ','

    if error is None:
        return groups_data
    else:
        return error


def get_friends_for_vk_user(user_id: str, meta=False):
    total = 0
    error = None
    params = {'user_id': user_id, 'offset': 0}
    if meta:
        params['fields'] = VK_USER_META_FIELDS
    friends = vk.api('friends.get', params)
    if vk.check(friends):
        friends_data = friends['response']['items']
        total = friends['response']['count']
        params['offset'] += 5000
    else:
        friends_data = []
        error = friends

    while params['offset'] < total:
        friends = vk.api('friends.get', params)
        if vk.check(friends):
            friends_data += friends['response']['items']
            params['offset'] += 5000
        else:
            params['offset'] = total
            friends_data = []
            error = friends

    if error is None:
        return friends_data
    else:
        return error


def get_groups_for_vk_user(user_id: str):
    offset = 0
    total = 0
    error = None
    groups = vk.api('groups.get', {'user_id': user_id, 'offset': offset})
    if vk.check(groups):
        groups_ids = groups['response']['items']
        total = groups['response']['count']
        offset += 1000
    else:
        groups_ids = []
        error = groups

    while offset < total:
        groups = vk.api('groups.get', {'user_id': user_id, 'offset': offset})
        if vk.check(groups):
            groups_ids += groups['response']['items']
            offset += 1000
        else:
            offset = total
            groups_ids = []
            error = groups

    if error is None:
        return groups_ids
    else:
        return error


def get_members_for_vk_group(group_id: str, user_ids=None, meta=False):
    total = 0
    error = None
    subs_set = set()
    subs_data = []

    if user_ids is None:  # get all subscribers
        params = {'group_id': group_id, 'offset': 0}
        if meta:
            params['fields'] = VK_USER_META_FIELDS
        subs = vk.api('groups.getMembers', params)

        if vk.check(subs):
            subs_data = subs['response']['items']
            total = subs['response']['count']
            params['offset'] += 1000
        else:
            subs_data = []
            error = subs

        while params['offset'] < total:
            subs = vk.api('groups.getMembers', params)
            if vk.check(subs):
                subs_data += subs['response']['items']
                params['offset'] += 1000
            else:
                params['offset'] = total
                subs_data = []
                error = subs
    else:  # get subscribers from list of ids
        i = 0
        n = 0
        idstr = ''
        for user_id in user_ids:
            n += 1
            if i == 0:
                idstr = str(user_id)
            else:
                idstr += ',' + str(user_id)
            i += 1
            if i >= 500 or n == len(user_ids):
                subs = vk.api('groups.isMember', {'group_id': group_id, 'user_ids': idstr}, True, True)
                if vk.check(subs):
                    for memb in subs['response']:
                        if memb['member'] == 1:
                            subs_data.append(int(memb['user_id']))
                else:
                    error = subs
                    break
                i = 0
                idstr = ''

    for sub_data in subs_data:
        subs_set.add(sub_data)
    if error is None:
        return subs_set
    else:
        return error


def check_post_text_md5(post: dict, content_md5: str):
    text = post.get('text')
    if text is not None:
        text = re.sub(r"\n"," ", text)
        if len(text) and hashlib.md5(text.encode('utf-8')).hexdigest() == content_md5:
            return True
    return False


def get_postinfo_for_post(post, owner_id, post_md5=None):
    postinfo = {'type': 'poster'}
    postinfo['copy_history'] = []
    copy_history = post.get('copy_history')
    if copy_history is not None:
        print(copy_history)
    # if post_md5 is not None:
        for copy_post in copy_history:
            postinfo['copy_history'].append({'owner_id': copy_post['owner_id'],
                                             'from_id': copy_post['from_id'],
                                             'date': copy_post['date']})
            # if check_post_text_md5(copy_post, post_md5):
            #     postinfo['copy_from_id'] = copy_post['from_id']
            #     postinfo['copy_date'] = copy_post['date']
            #     break
    # else:
        postinfo['copy_from_id'] = copy_history[0]['from_id']
        postinfo['copy_date'] = copy_history[0]['date']

    postinfo['id'] = post['id']
    postinfo['from_id'] = post['from_id']
    postinfo['date'] = post['date']

    #test stub
    # postinfo['original'] = post

    if post.get('reposts'):
        postinfo['reposts'] = post['reposts']['count']
    else:
        postinfo['reposts'] = 0
    if post.get('views'):
        postinfo['views'] = post['views']['count']
    else:
        postinfo['views'] = 0
    if post.get('comments'):
        postinfo['comments'] = post['comments']['count']
    else:
        postinfo['comments'] = 0
    postinfo['likes'] = get_likes_for_post(str(postinfo['id']), owner_id)

    return postinfo


def get_root_post_for_wall_with_meta(owner_id, post_id):
    print('Getting root post info for: '+str(owner_id)+'_'+str(post_id))
    postmeta = {}
    response = vk.api('wall.getById', {'posts': str(owner_id)+'_'+str(post_id)})
    if vk.check(response):
        if len(response['response']):
            post = response['response'][0]
        else:
            print(response)
            response = {'error':{'error_code':666, 'error_msg':'empty response'}}
            return response
            exit(666)
        postmeta['postinfo'] = get_postinfo_for_post(post, owner_id)
        postmeta['text'] = re.sub(r"\n", " ", post['text'])
        search_words = postmeta['text'].split(' ')
        postmeta['search_string'] = ' '.join(search_words[:20])
        postmeta['md5'] = hashlib.md5(postmeta['text'].encode('utf-8')).hexdigest()
        return postmeta
    else:
        return response


def get_likes_for_post(post_id, owner_id):
    print('Getting likes for post: ' + str(owner_id) + '_' + str(post_id))
    resume = True
    likes = set()
    error = None
    offset = 0
    while resume:
        likesinfo = vk.api('likes.getList', {'type': 'post', 'owner_id': owner_id, 'item_id': post_id,
                                             'count': 1000, 'offset': offset})
        if vk.check(likesinfo):
            likes.update(likesinfo['response']['items'])
            if len(likesinfo['response']['items']) >= 1000:
                offset += 1000
            else:
                resume = False
        else:
            error = likesinfo
            resume = False
    if error is None:
        return likes
    else:
        return error


def find_post_on_wall(owner_id, content_md5: str, search_string: str, original_from_id=0,
                      original_date=None, wallsearch=False, use_cache=False, cache_date_utc=None, original_id = 0):
    print('Finding post on wall: ' + str(owner_id) + ' wallsearch: ' + str(wallsearch))
    if wallsearch:
        posts = vk.api('wall.search',
                            {'type': 'post', 'owner_id': str(owner_id), 'query': search_string, 'count': 100,
                             'owners_only': 1})
        if posts.get('response'):
            print(posts['response'])
        elif posts.get('error'):
            print(posts['error'])
    else:
        posts = vk.api('wall.get', {'type': 'post', 'owner_id': str(owner_id), 'count': 100,
                                    'owners_only': 1}, use_cache=use_cache, cache_date_utc=cache_date_utc)
    postfound = None

    if vk.check(posts):
        for post in posts['response']['items']:
            if check_post_text_md5(post, content_md5):
                postfound = post
                break
            if post['from_id'] == original_from_id and post['id'] == original_id:
                postfound = post
                break
            copy_history = post.get('copy_history')
            if copy_history is not None:
                for copy_post in copy_history:
                    copy_from_id = copy_post['from_id']
                    copy_date = copy_post['date']
                    post_id = copy_post['id']
                    if copy_from_id == original_from_id and post_id == original_id and copy_date == original_date:
                        postfound = post
                        break
                    if check_post_text_md5(copy_post, content_md5):
                        postfound = post
                        copy_from_id = copy_post['from_id']
                        copy_date = copy_post['date']
                        if original_date is None or copy_date == original_date:
                            if original_from_id == 0 or copy_from_id == original_from_id:
                                break
            # print(post)
    else:
        if vk.is_error(posts):
            err_code = posts['error'].get('error_code')
            if err_code is not None:
                if err_code == 29:
                    if wallsearch:
                        print('wall.search limit reached')
                    else:
                        print('wall.get limit reached')
                        if use_cache:
                            vk.remove_from_cache('wall.get', {'type': 'post', 'owner_id': str(owner_id), 'count': 100,
                                                              'owners_only': 1})
                    return posts
                elif err_code <= 10:
                    if use_cache:
                        vk.remove_from_cache('wall.get', {'type': 'post', 'owner_id': str(owner_id), 'count': 100,
                                                          'owners_only': 1})
                    return posts
                else:
                    print('hidden user found')
                    return {'type': 'hidden'}
        print(posts)

    if postfound is None:
        if wallsearch is False:
            if vk.check(posts):
                n_items = len(posts['response']['items'])
                if n_items == 100:
                    last_post_date = posts['response']['items'][n_items - 1].get('date')
                    if last_post_date > original_date:
                        print('we need to go deeper...')
                        return find_post_on_wall(owner_id, content_md5, search_string, original_from_id, original_date,
                                                 True, original_id=original_id)

        return {'type': 'liker'}
    else:
        print('post found')
    return get_postinfo_for_post(postfound, owner_id, content_md5)


def get_posts(owner_id, count, offset=0):
    print('Get posts from wall: ' + str(owner_id) + ' count: ' + str(count) + ' offset: ' + str(offset))
    total = 0
    error = None

    posts = vk.api('wall.get', {'type': 'post', 'owner_id': str(owner_id), 'count': min(count, 100), 'offset': offset})

    if vk.check(posts):
        posts_data = posts['response']['items']
        total = posts['response']['count']
        if total > offset + count:
            total = offset + count
        offset += 100
    else:
        posts_data = []
        error = posts

    while offset < total:
        posts = vk.api('wall.get', {'type': 'post', 'owner_id': str(owner_id), 'count': 100, 'offset': offset})
        if vk.check(posts):
            posts_data += posts['response']['items']
            offset += 100
        else:
            offset = total
            posts_data = []
            error = posts

    if error is None:
        return posts_data
    else:
        return error


def get_posts_by_id(owner_id, ids: set):
    print('Get posts by ids from wall: ' + str(owner_id) + ' count: ' + str(len(ids)))
    total = 0
    checked = 0
    error = None
    ids_string = ''
    posts_data = []

    for post_id in ids:
        total += 1
        checked += 1
        ids_string += str(owner_id) + '_' + str(post_id)
        if total >= 100 or checked == len(ids):
            posts = vk.api('wall.getById', {'posts': ids_string}, ispost=True)
            # print(posts)
            if vk.check(posts):
                posts_data += posts['response']
            else:
                posts_data = []
                error = posts
            total = 0
            ids_string = ''
        else:
            ids_string += ','

    if error is None:
        return posts_data
    else:
        return error