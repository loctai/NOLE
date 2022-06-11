import os
from flask import render_template, send_from_directory


def init_standard_views(app):
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )
    @app.route('/sitemap.xml')
    def sitemap():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
    @app.route('/hypes.txt')
    def hypes():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'hypes.txt')
    @app.errorhandler(404)
    def missing_page(exception):
        print(exception)
        """Catch internal 404 errors, display
            a nice error page and log the error.
        """
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden_page(exception):
        """Catch internal 404 errors, display
            a nice error page and log the error.
        """
        return render_template("403.html"), 403
    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def internal_error(exception):
        print(exception)
        return render_template('500.html'), 500
    # @app.errorhandler(500)
    # @app.errorhandler(Exception)
    # def internal_error(exception):
    #     """Catch internal exceptions and 500 errors, display
    #         a nice error page and log the error.
    #     """
    #     return render_template("500.html"), 500