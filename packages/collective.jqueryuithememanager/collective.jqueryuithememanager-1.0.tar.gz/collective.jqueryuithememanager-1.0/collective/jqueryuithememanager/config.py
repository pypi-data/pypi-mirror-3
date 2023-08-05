try:
    from collective.js.jqueryui.config import *
except ImportError:
    VERSION = '1.8.16'

PRELOADEDS = ('base', 'black-tie', 'blitzer', 'cupertino', 'dark-hive',
              'dot-luv','eggplant','excite-bike','flick','hot-sneaks',
              'humanity','le-frog','mint-choc','overcast', 'pepper-grinder',
              'redmond', 'smoothness','south-street','start','sunny',
              'swanky-purse','trontastic','ui-darkness','ui-lightness','vader')

CUSTOM_THEMEID = 'custom'
BASE_THEMEID = 'sunburst'

CDN_URL = 'http://ajax.googleapis.com/ajax/libs/jqueryui/%s/themes/%s/jquery-ui.css'

BASE_JQUERYUI_URL = "http://jqueryui.com/themeroller/?ctl=themeroller&"
ZIP_JQUERYUI_URL = "http://jquery-ui.googlecode.com/files/jquery-ui-themes-1.8.16.zip"
BASE_CSS_PATH = "portal_resources/jqueryuitheme/css/%(id)s/jquery-ui-%(version)s.custom.css"
THEME_RESOURCE_NAME = "jqueryuitheme"

THEME_SETTINGS = ('fwDefault',
    'bgTextureHover',
    'cornerRadiusShadow',
    'fcHover',
    'bgTextureShadow',
    'fcHighlight',
    'iconColorHover',
    'fcHeader',
    'bgColorError',
    'bgImgOpacityHover',
    'bgTextureContent',
    'thicknessShadow',
    'borderColorHighlight',
    'bgImgOpacityError',
    'iconColorDefault',
    'fcDefault',
    'opacityShadow',
    'bgImgOpacityDefault',
    'fcActive',
    'bgImgOpacityHighlight',
    'bgTextureOverlay',
    'bgImgOpacityOverlay',
    'bgColorOverlay',
    'bgTextureError',
    'borderColorHover',
    'bgColorHeader',
    'fsDefault',
    'iconColorHighlight',
    'bgColorHighlight',
    'iconColorContent',
    'opacityOverlay',
    'borderColorContent',
    'ffDefault',
    'iconColorHeader',
    'fcContent',
    'bgImgOpacityContent',
    'borderColorHeader',
    'fcError',
    'iconColorActive',
    'borderColorActive',
    'bgColorActive',
    'cornerRadius',
    'bgTextureHeader',
    'bgTextureHighlight',
    'bgColorDefault',
    'borderColorError',
    'bgColorHover',
    'bgColorShadow',
    'bgTextureDefault',
    'offsetLeftShadow',
    'bgColorContent',
    'iconColorError',
    'bgImgOpacityShadow',
    'bgImgOpacityHeader',
    'bgTextureActive',
    'borderColorDefault',
    'bgImgOpacityActive',
    'ctl',
    'offsetTopShadow')

FILES=['ui.core.js',
'ui.widget.js',
'ui.mouse.js',
'ui.position.js',
'ui.draggable.js',
'ui.droppable.js',
'ui.resizable.js',
'ui.selectable.js',
'ui.sortable.js',
'ui.accordion.js',
'ui.autocomplete.js', #is in conflict with plone.formwidget.autocomplete
'ui.dialog.js',
'ui.slider.js',
'ui.tabs.js', #is in conflict with jquerytools
'ui.datepicker.js',
'ui.progressbar.js',
'effects.core.js',
'effects.blind.js',
'effects.bounce.js',
'effects.clip.js',
'effects.drop.js',
'effects.explode.js',
'effects.fade.js',
'effects.fold.js',
'effects.highlight.js',
'effects.pulsate.js',
'effects.scale.js',
'effects.shake.js',
'effects.slide.js',
'effects.transfer.js',
]
