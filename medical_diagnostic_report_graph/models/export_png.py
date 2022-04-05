import io
import warnings

import bokeh.io.export as export
from bokeh.embed import file_html
from bokeh.embed.util import FromCurdoc
from bokeh.resources import INLINE
from bokeh.util.dependencies import import_required
from bokeh.util.string import decode_utf8


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


def get_screenshot_as_png(obj, driver=None, **kwargs):
    """Get a screenshot of a ``LayoutDOM`` object.

    Args:
        obj (LayoutDOM or Document) : a Layout (Row/Column), Plot or Widget
            object or Document to export.

        driver (selenium.webdriver) : a selenium webdriver instance to use
            to export the image.

    Returns:
        cropped_image (PIL.Image.Image) : a pillow image loaded from PNG.

    .. warning::
        Responsive sizing_modes may generate layouts with unexpected size and
        aspect ratios. It is recommended to use the default ``fixed`` sizing mode.

    """
    Image = import_required(
        "PIL.Image",
        "To use bokeh.io.export_png you need pillow "
        + '("conda install pillow" or "pip install pillow")',
    )

    with export._tmp_html() as tmp:
        html = get_layout_html(obj, **kwargs)
        with io.open(tmp.path, mode="w", encoding="utf-8") as file:
            file.write(decode_utf8(html))

        web_driver = (
            driver if driver is not None else export.webdriver_control.get()
        )

        web_driver.get("file:///" + tmp.path)
        web_driver.maximize_window()

        # resize for PhantomJS compat
        web_driver.execute_script("document.body.style.width = '100%';")

        export.wait_until_render_complete(web_driver)

        png = web_driver.get_screenshot_as_png()

        b_rect = web_driver.execute_script(export._BOUNDING_RECT_SCRIPT)

    image = Image.open(io.BytesIO(png))
    cropped_image = export._crop_image(image, **b_rect)

    return cropped_image
