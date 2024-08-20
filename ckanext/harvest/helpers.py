
import datetime
from ckan import logic
from ckan import model
import ckan.lib.helpers as h
import ckan.plugins as p

from ckanext.harvest.model import UPDATE_FREQUENCIES, UPDATE_TIMES
from ckanext.harvest.utils import (
    DATASET_TYPE_NAME
)
from ckanext.harvest.interfaces import IHarvester


c = p.toolkit.c
request = p.toolkit.request


def get_harvest_source(source_id=None):

    context = {'model': model, 'session': model.Session}
    if source_id:
        return p.toolkit.get_action('harvest_source_show')(context, {'id': source_id})
    elif hasattr(c, 'pkg_dict'):
        return c.pkg_dict
    elif hasattr(c, 'pkg'):
        return p.toolkit.get_action('harvest_source_show')(context, {'id': c.pkg.id})

    return None


def package_list_for_source(source_id):
    '''
    Creates a dataset list with the ones belonging to a particular harvest
    source.

    It calls the package_list snippet and the pager.
    '''
    limit = 20
    page = int(request.args.get('page', 1))
    fq = '+harvest_source_id:"{0}"'.format(source_id)
    search_dict = {
        'fq': fq,
        'rows': limit,
        'sort': 'metadata_modified desc',
        'start': (page - 1) * limit,
    }

    context = {'model': model, 'session': model.Session}
    harvest_source = get_harvest_source(source_id)
    owner_org = harvest_source.get('owner_org', '')
    if owner_org:
        user_member_of_orgs = [org['id'] for org
                               in h.organizations_available('read')]
        if (harvest_source and owner_org in user_member_of_orgs):
            context['ignore_capacity_check'] = True

    query = logic.get_action('package_search')(context, search_dict)

    base_url = h.url_for(
        '{0}.read'.format(DATASET_TYPE_NAME),
        id=harvest_source['name']
    )

    def pager_url(q=None, page=None):
        url = base_url
        if page:
            url += '?page={0}'.format(page)
        return url

    pager = h.Page(
        collection=query['results'],
        page=page,
        url=pager_url,
        item_count=query['count'],
        items_per_page=limit
    )
    pager.items = query['results']

    if query['results']:
        out = h.snippet('snippets/package_list.html', packages=query['results'])
        out += pager.pager()
    else:
        out = h.snippet('snippets/package_list_empty.html')

    return out


def package_count_for_source(source_id):
    '''
    Returns the current package count for datasets associated with the given
    source id
    '''
    fq = '+harvest_source_id:"{0}"'.format(source_id)
    search_dict = {'fq': fq}
    context = {'model': model, 'session': model.Session}
    result = logic.get_action('package_search')(context, search_dict)
    return result.get('count', 0)


def harvesters_info():
    context = {'model': model, 'user': p.toolkit.c.user or p.toolkit.c.author}
    return logic.get_action('harvesters_info_show')(context, {})


def harvester_types():
    harvesters = harvesters_info()
    return [{'text': p.toolkit._(h['title']), 'value': h['name']}
            for h in harvesters]


def harvest_frequencies():
    return [{'text': p.toolkit._(f.title()), 'value': f}
            for f in UPDATE_FREQUENCIES]


def harvest_times():
    return [{'text': time, 'value': time}
            for time in UPDATE_TIMES]


def harvest_default_time():
    default_time = datetime.datetime.now().strftime('%I:00 %p')
    return default_time


def link_for_harvest_object(id=None, guid=None, text=None):

    if not id and not guid:
        return None

    if guid:
        context = {'model': model, 'user': p.toolkit.c.user or p.toolkit.c.author}
        obj = logic.get_action('harvest_object_show')(context, {'id': guid, 'attr': 'guid'})
        id = obj.id

    url = h.url_for('harvester.object_show', id=id)
    text = text or guid or id
    link = '<a href="{url}">{text}</a>'.format(url=url, text=text)

    return p.toolkit.literal(link)


def harvest_source_extra_fields():
    fields = {}
    for harvester in p.PluginImplementations(IHarvester):
        if not hasattr(harvester, 'extra_schema'):
            continue
        fields[harvester.info()['name']] = list(harvester.extra_schema().keys())
    return fields


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Harvest search page to
    render the remove link for the tag pills.
    '''
    if p.toolkit.check_ckan_version(min_version='2.9.0'):
        search_route = 'harvest.search'
    else:
        search_route = 'harvest_search'

    return h.remove_url_param(
        key,
        value=value,
        replace=replace,
        alternative_url=h.url_for(search_route)
    )


def get_latest_job(harvest_id):
    context = {'model': model, 'session': model.Session, 'user': p.toolkit.c.user or p.toolkit.c.author}
    try:
        harvest_source = p.toolkit.get_action('harvest_source_show')(context, {'id': harvest_id})
        last_job = harvest_source.get('status', {}).get('last_job', {})
        job = get_job(context, last_job.get('id')) if last_job else {}
        return job
    except (p.toolkit.ObjectNotFound, p.toolkit.NotAuthorized):
        return {}


def get_job(context, job_id):
    try:
        job = p.toolkit.get_action('harvest_job_show')(context, {'id': job_id})
        return job
    except (p.toolkit.ObjectNotFound, p.toolkit.NotAuthorized):
        return {}


def get_harvest_errors_url(current_url):
    harvest_error_url = current_url
    if 'show_errors' not in current_url:
        if '?' not in current_url:
            harvest_error_url = h.current_url() + '?show_errors=true'
        else:
            harvest_error_url = h.current_url() + '&show_errors=true'
    else:
        harvest_error_url = facet_remove_field('show_errors')
    return harvest_error_url
