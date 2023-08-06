def url_generator(event):
    render_globals = event
    request = event.get("request") or threadlocal.get_current_request()

    try:
        render_globals['context_path'] = request.resource_url(request.context)
        render_globals['context_new'] = request.resource_url(request.context, 'new')
        render_globals['context_edit'] = request.resource_url(request.context, 'edit')
        render_globals['context_delete'] = request.resource_url(request.context, 'delete')
    except:
        pass
    


def includeme(config):
    config.add_subscriber(url_generator, 'pyramid.events.BeforeRender')
    config.add_subscriber(url_generator, 'pyramid.events.BeforeRender')
