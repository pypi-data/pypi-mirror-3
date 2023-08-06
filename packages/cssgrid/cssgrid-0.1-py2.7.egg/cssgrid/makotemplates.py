from webhelpers.html.builder import HTML
from mako.runtime import supports_caller


make_tag = HTML.tag


grid_defaults = {
    '960gs': {
        'grid_format': 'grid_{0}',
        'start_class': 'alpha',
        'end_class': 'omega',
        'prefix_format': 'prefix_{0}',
        'suffix_format': 'suffix_{0}',
        'push_format': 'push_{0}',
        'pull_format': 'pull_{0}',
        'tag': 'div',
        'container_format': 'container_{0}',
    },
}


@supports_caller
def grid(context, cols, start=False, end=False, prefix=None, suffix=None, 
    pull=None, push=None, classes=None, tag=None, clear_divs=None,
    data_attrs=None, grid_system='960gs', **tag_attrs):
    grid_params = grid_defaults[grid_system]
    if classes is None:
        classes = []
    else:
        classes = [cls.strip() for cls in classes.split(',')]
    classes.append(grid_params['grid_format'].format(cols))
    if start:
        classes.append(grid_params['start_class'])
    if end:
        classes.append(grid_params['end_class'])
    if prefix is not None:
        classes.append(grid_params['prefix_format'].format(prefix))
    if suffix is not None:
        classes.append(grid_params['suffix_format'].format(suffix))
    if pull is not None:
        classes.append(grid_params['pull_format'].format(pull))
    if push is not None:
        classes.append(grid_params['push_format'].format(push))
    tag_attrs['class_'] = ' '.join(classes)
    tag_attrs['_closed'] = False
    if not tag:
        tag = grid_params['tag']
    if data_attrs is not None:
        for key, value in data_attrs.items():
            tag_attrs['data-' + key] = value
    context.write(make_tag(tag, **tag_attrs))
    context['caller'].body()
    context.write('</{0}>'.format(tag))
    if (end and clear_divs is None) or clear_divs is True:
        context.write(make_tag('div', class_='clear', _closed=False))
        context.write('</div>')
    return ''


@supports_caller
def container(context, cols=12, grid_system='960gs', classes=None, tag=None,
    clear_divs=True, **tag_attrs):
    grid_params = grid_defaults[grid_system]    
    if classes is None:
        classes = []
    else:
        classes = [cls.strip() for cls in classes.split(',')]
    classes.append(grid_params['container_format'].format(cols))
    if not tag:
        tag = grid_params['tag']
    tag_attrs['class_'] = ' '.join(classes)
    tag_attrs['_closed'] = False
    context.write(make_tag(tag, **tag_attrs))
    context['caller'].body()
    context.write('</{0}>'.format(tag))
    if clear_divs is True:
        context.write(make_tag('div', class_='clear', _closed=False))
        context.write('</div>')
    return ''
