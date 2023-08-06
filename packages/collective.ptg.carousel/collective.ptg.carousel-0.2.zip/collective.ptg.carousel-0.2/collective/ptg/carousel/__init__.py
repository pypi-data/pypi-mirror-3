from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import \
    BatchingDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ptg.carousel')

class ICarouselDisplaySettings(IBaseSettings):
    carousel_width = schema.Int(
        title=_(u"label_carousel_imagewidth",
            default=u"Width of carousel"),
        default=800,
        min=50)
    carousel_imagewidth = schema.Int(
        title=_(u"label_carousel_imagewidth",
            default=u"Width of (each) image (box)"),
        default=400,
        min=16)
    carousel_imageheight = schema.Int(
        title=_(u"label_carousel_imageheight",
            default=u"Height of (each) image"),
        default=260,
        min=16)
    carousel_use_icons = schema.Bool(
        title=_(u"label_carousel_use_icons",
            default=u"Use Thumbnail size instead of Size"),
        default=False)
    carousel_overlay_opacity = schema.Choice(
        title=_(u"label_carousel_overlay_opacity",
                default=u"Opacity on overlay"),
        default=0.3,
        vocabulary=SimpleVocabulary([
            SimpleTerm(0, 0,
                _(u"label_carousel_overlay_opacity0",
                    default=u"0 Hide it completely")),
            SimpleTerm(0.1, 0.1,
                _(u"label_carousel_overlay_opacity1",
                    default=u"0.1 Almost gone")),
            SimpleTerm(0.2, 0.2,
                _(u"label_carousel_overlay_opacity2", default=u"0.2")),
            SimpleTerm(0.3, 0.3,
                _(u"label_carousel_overlay_opacity3", default=u"0.3")),
            SimpleTerm(0.4, 0.4,
                _(u"label_carousel_overlay_opacity4",
                    default=u"0.4 A bit more")),
            SimpleTerm(0.5, 0.5,
                _(u"label_carousel_overlay_opacity5", default=u"0.5")),
            SimpleTerm(0.6, 0.6,
                _(u"label_carousel_overlay_opacity6",
                    default=u"0.6")),
            SimpleTerm(0.7, 0.7,
                _(u"label_carousel_overlay_opacity7",
                    default=u"0.7 Quite a bit")),
            SimpleTerm(0.8, 0.8,
                _(u"label_carousel_overlay_opacity8",
                    default=u"0.8 A bit much")),
            SimpleTerm(0.9, 0.9,
                _(u"label_carousel_overlay_opacity9",
                    default=u"0.9 Almost nothing")),
            SimpleTerm(1, 1,
                _(u"label_carousel_overlay_opacity10",
                    default=u"1 Off")
            )
        ]))
    carousel_toppadding = schema.TextLine(
        title=_(u"label_carousel_toppadding",
            default=u"Padding above imagetitle"),
        default=u"90px")
    carousel_style = schema.Choice(
        title=_(u"label_carousel_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_carousel_style_default",
                    default=u"Default")),
            SimpleTerm("no_style.css", "no_style.css",
                _(u"label_carousel_style_no",
                    default=u"No style / css file")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_carousel_style_custom",
                    default=u"Custom css file")
            )
        ]))

    carousel_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class CarouselDisplayType(BatchingDisplayType):
    name = u"carousel"
    schema = ICarouselDisplaySettings
    description = _(u"label_carousel_display_type",
        default=u"Carousel")

    def javascript(self):
        return u"""
<script type="text/javascript" src="%(portal_url)s/++resource++ptg.carousel/jquery.jcarousel.min.js">
        </script>
        <script type="text/javascript">
        function mycarousel_initCallback(carousel)
{
    // Disable autoscrolling if the user clicks the prev or next button.
    carousel.buttonNext.bind('click', function() {
        carousel.startAuto(0);
    });

    carousel.buttonPrev.bind('click', function() {
        carousel.startAuto(0);
    });

    // Pause autoscrolling if the user moves with the cursor over the clip.
    carousel.clip.hover(function() {
        carousel.stopAuto();
    }, function() {
        carousel.startAuto();
    });
};

jQuery(document).ready(function() {
    jQuery('#mycarousel').jcarousel({
        auto: 2,
        wrap: 'last',
        initCallback: mycarousel_initCallback
    });
});

</script>
""" % {
    'speed': self.settings.duration,
    'portal_url': self.portal_url,
}

    def css(self):
        relpath = '++resource++ptg.carousel'
        style = '%s/%s/%s' % (self.portal_url, relpath,
            self.settings.carousel_style)

        if self.settings.carousel_style == 'custom_style':
            style = '%s/%s' % (self.portal_url,
                self.settings.carousel_custom_style)

        return u"""
        <style>

.jcarousel-item {
    height: %(boxheight)ipx;
    width: %(boxwidth)ipx;
}

.wrap {
    width: %(carousel_width)ipx

.imagebox:hover {
    opcaity: %(overlay_opacity)s);
}

</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'boxheight': self.settings.carousel_imageheight,
        'boxwidth': self.settings.carousel_imagewidth,
        'overlay_opacity': self.settings.carousel_overlay_opacity,
        'carousel_width' : self.settings.carousel_width,
        'style': style
       }
CarouselSettings = createSettingsFactory(CarouselDisplayType.schema)
