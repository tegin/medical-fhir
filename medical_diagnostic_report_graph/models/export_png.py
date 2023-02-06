import io
import warnings

from bokeh.embed import file_html
from bokeh.embed.util import FromCurdoc
from bokeh.io import webdriver
from bokeh.io.export import (
    _maximize_viewport as _maximize_viewport,
    _tmp_html,
    wait_until_render_complete,
)
from bokeh.resources import INLINE
from PIL import Image


def get_layout_html(obj, resources=INLINE, theme=FromCurdoc, **kwargs):
    """ """
    resize = False
    if kwargs.get("height") is not None or kwargs.get("width") is not None:
        # Defer this import, it is expensive
        from bokeh.models.plots import Plot

        if not isinstance(obj, Plot):
            warnings.warn(
                "Export method called with height or width "
                "kwargs on a non-Plot layout. "
                "The size values will be ignored."
            )
        else:
            resize = True
            old_height = obj.plot_height
            old_width = obj.plot_width
            obj.plot_height = kwargs.get("height", old_height)
            obj.plot_width = kwargs.get("width", old_width)

    try:
        html = file_html(
            obj,
            resources,
            theme=theme,
            title="",
            suppress_callback_warning=True,
            _always_new=True,
        )
    finally:
        if resize:
            obj.plot_height = old_height
            obj.plot_width = old_width
    return html


def get_screenshot_as_png(
    obj,
    *,
    driver=None,
    timeout=5,
    resources=INLINE,
    width=None,
    height=None,
    theme=None
):
    """Get a screenshot of a ``LayoutDOM`` object.
    Args:
        obj (LayoutDOM or Document) : a Layout (Row/Column), Plot or Widget
            object or Document to export.
        driver (selenium.webdriver) : a selenium webdriver instance to use
            to export the image.
        timeout (int) : the maximum amount of time to wait for initialization.
            It will be used as a timeout for loading Bokeh, then when waiting for
            the layout to be rendered.
    Returns:
        image (PIL.Image.Image) : a pillow image loaded from PNG.
    .. warning::
        Responsive sizing_modes may generate layouts with unexpected size and
        aspect ratios. It is recommended to use the default ``fixed`` sizing mode.
    """

    with _tmp_html() as tmp:
        html = get_layout_html(
            obj, resources=resources, width=width, height=height, theme=theme
        )
        with open(tmp.path, mode="w", encoding="utf-8") as file:
            file.write(html)

        web_driver = (
            driver
            if driver is not None
            else webdriver.create_chromium_webdriver(["--no-sandbox"])
        )
        web_driver.maximize_window()
        web_driver.get(f"file://{tmp.path}")
        wait_until_render_complete(web_driver, timeout)
        [width, height, dpr] = _maximize_viewport(web_driver)
        png = web_driver.get_screenshot_as_png()

    return Image.open(io.BytesIO(png))
