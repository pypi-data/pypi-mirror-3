from middleware import MinifyMiddleware

def plugme(app_config, options):
    def mount_minify_middleware(app):
        return MinifyMiddleware(app)
    app_config.register_hook('after_config', mount_minify_middleware)
    return dict(appid='tgext.minify')
