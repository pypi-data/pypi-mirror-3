from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import \
    BatchingDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ptg.uigallery')

class IuigalleryDisplaySettings(IBaseSettings):
    uigallery_columns = schema.Int(
        title=_(u"label_uigallery_columns",
            default=u"Number of images before a forced new row (use a high "
                    u"number if you dont want this)"),
        default=3,
        min=1)
    uigallery_imagewidth = schema.Int(
        title=_(u"label_uigallery_imagewidth",
            default=u"Width of (each) image"),
        default=400,
        min=50)
    uigallery_imageheight = schema.Int(
        title=_(u"label_uigallery_imageheight",
            default=u"Height of (each) image"),
        default=260,
        min=50)
    uigallery_use_icons = schema.Bool(
        title=_(u"label_uigallery_use_icons",
            default=u"Use Thumbnail size instead of Size"),
        default=False)
    uigallery_effect = schema.Choice(
        title=_(u"label_uigallery_effect",
                default=u"effect"),
        default="shake",
        vocabulary=SimpleVocabulary([
            SimpleTerm("blind", "blind",
                _(u"label_uigallery_effect0",
                    default=u"blind")),
            SimpleTerm("bounce", "bounce",
                _(u"label_uigallery_effect1",
                    default=u"bounce")),
            SimpleTerm("clip", "clip",
                _(u"label_uigallery_effect2", 
                    default=u"clip")),
            SimpleTerm("drop", "drop",
                _(u"label_uigallery_effect3", 
                    default=u"drop")),
            SimpleTerm("explode", "explode",
                _(u"label_uigallery_effect4",
                    default=u"explode")),
            SimpleTerm("fade", "fade",
                _(u"label_uigallery_effect5", 
                    default=u"fade")),
            SimpleTerm("fold", "fold",
                _(u"label_uigallery_effect6",
                    default=u"fold")),
            SimpleTerm("highlight", "highlight",
                _(u"label_uigallery_effect7",
                    default=u"highlight")),
            SimpleTerm("puff", "puff",
                _(u"label_uigallery_effect8",
                    default=u"puff")),
            SimpleTerm("pulsate", "pulsate",
                _(u"label_uigallery_effect9",
                    default=u"pulsate")),
           SimpleTerm("scale", "scale",
                _(u"label_uigallery_effect10",
                    default=u"scale")),
           SimpleTerm("shake", "shake",
                _(u"label_uigallery_effect11",
                    default=u"shake")),
           SimpleTerm("size", "size",
                _(u"label_uigallery_effect12",
                    default=u"size (not working yet)")),
           SimpleTerm("slide", "slide",
                _(u"label_uigallery_effect13",
                    default=u"slide")),
            SimpleTerm("transfer", "transfer",
                _(u"label_uigallery_effect14",
                    default=u"transfer (not working yet)")
            )
        ]))
    uigallery_toppadding = schema.TextLine(
        title=_(u"label_uigallery_toppadding",
            default=u"Padding above imagetitle"),
        default=u"90px")
    uigallery_bottompadding = schema.TextLine(
        title=_(u"label_uigallery_bottompadding",
            default=u"Padding below imagedescription"),
        default=u"70px")

    uigallery_style = schema.Choice(
        title=_(u"label_uigallery_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_uigallery_style_default",
                    default=u"Default")),
            SimpleTerm("no_style.css", "no_style.css",
                _(u"label_uigallery_style_no",
                    default=u"No style / css file")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_uigallery_style_custom",
                    default=u"Custom css file")
            )
        ]))

    uigallery_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class uigalleryDisplayType(BatchingDisplayType):
    name = u"uigallery"
    schema = IuigalleryDisplaySettings
    description = _(u"label_uigallery_display_type",
        default=u"uigallery")

    def javascript(self):
        return u"""
<script type="text/javascript">
$(document).ready(function() {
        var selectedEffect = "%(effect)s"
        // some effects have required parameters
	    if ( selectedEffect === "scale" ) {
	    options = { percent: 10 };   
		} else if ( selectedEffect === "transfer" ) {
			options = { to: "#content", className: "ui-effects-transfer" };
		} else if ( selectedEffect === "explode" ) {
			options = { pieces: 6 };	
		} else if ( selectedEffect === "size" ) {
			options = { to: { width: 50, height: 30 } };
		}

        var options = {};
        $(".imagebox").effect("%(effect)s", options, %(speed)i, function() {
            //  to bring a hidden box back
	        $(".imagebox").fadeIn();
	    });
        $(this).find('.image-title').slideDown(%(speed)i);
        $(this).find('.image-desc').slideDown(%(speed)i);
});
</script>
""" % {
    'speed': self.settings.duration,
    'effect': self.settings.uigallery_effect,
}

    def css(self):
        relpath = '++resource++ptg.uigallery'
        style = '%s/%s/%s' % (self.portal_url, relpath,
            self.settings.uigallery_style)

        if self.settings.uigallery_style == 'custom_style':
            style = '%s/%s' % (self.portal_url,
                self.settings.uigallery_custom_style)

        return u"""
        <style>
.uigallery div {
    height: %(boxheight)ipx;
    width: %(boxwidth)ipx;
}

.uigallery h3.image-title {
    padding-top: %(toppadding)s;
}

.uigallery p.image-desc {
    padding-bottom: %(bottompadding)s;
}

.imagebox:hover {
    opcaity: 0.2;
}

</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'columns': self.settings.uigallery_columns,
        'boxheight': self.settings.uigallery_imageheight,
        'boxwidth': self.settings.uigallery_imagewidth,
        'bottompadding' : self.settings.uigallery_bottompadding,
        'toppadding' : self.settings.uigallery_toppadding,
        'style': style
       }
uigallerySettings = createSettingsFactory(uigalleryDisplayType.schema)
