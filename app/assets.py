from flask_assets import Environment, Bundle


def compile_main_assets(app):
    """Configure logged-in asset bundles."""
    assets = Environment(app)
    Environment.auto_build = True
    Environment.debug = False
    # Stylesheets Bundle
    assets_css = [
        'assets/vendors/css/vendor.bundle.base.css',
        'assets/vendors/css/vendor.bundle.addons.css',
        'src/less/dashboard.scss',
        'assets/css/shared/style.css',
        'assets/css/demo_1/style.css'
    ]
    less_bundle =  Bundle(
            *assets_css,
            output='dist/css/main.min.css',
            filters='pyscss,cssmin', extra={'rel': 'stylesheet/css'})

   
    account_css = Bundle(
            'account/css/base.css',
            'account/css/styles.css',
            'account/css/media.css',
            'account/css/animation.css',
            'account/plugin/dialog/dialog.css',
            filters='cssmin',
            output="account/dist/css/main.min.css", extra={'rel': 'stylesheet/css'})

    # JavaScript Bundle
    account_js = Bundle(
        'account/js/jquery.js',
        'account/plugin/dialog/dialog.js',
        'account/js/public.js',
        'account/js/scripts.js',
                       filters='jsmin',
                       output='account/dist/js/main.min.js')
    # Register assets
    assets.register('account_css', account_css)
    # assets.register('less_all', less_bundle)
    assets.register('account_js', account_js)
    # Build assets in development mode
    # less_bundle.build()
    account_css.build()
    account_js.build()