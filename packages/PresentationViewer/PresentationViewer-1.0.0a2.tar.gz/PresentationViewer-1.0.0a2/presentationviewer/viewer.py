#! /usr/bin/env python
"""LibreOffice/OpenOffice Impress Viewer script 

For use in rendering unattended presentations, this should allow you to call:

    presentation-viewer /path/to/presentation 

and have the presentation load, switch to presentation mode, and auto
advance through the presentation until the end of the presentation,
even if the presentation is not already set up for auto-advancing.

Intended to optionally allow looping or not...
"""
import os, sys, subprocess, time, pprint, urllib,logging
from optparse import OptionParser
import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.presentation.FadeEffect import UNCOVER_TO_RIGHT, NONE as TRANSITION_NONE
log = logging.getLogger( __name__ )

CAPTIVE = None
def captive( port=2002 ):
    return subprocess.Popen(
        [
            'libreoffice',
            '--invisible',
            '--accept=socket,host=localhost,port=%(port)s;urp;'%locals(),
            '--norestore',
            '--nologo',
            '--nolockcheck',
            '--nodefault',
        ]
    )

DESKTOP = None
def desktop( port=2002 ):
    global DESKTOP
    if DESKTOP is None:
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
            'com.sun.star.bridge.UnoUrlResolver', localContext
        )
        context = resolver.resolve(
            'uno:socket,host=localhost,port=%(port)s;urp;StarOffice.ComponentContext'%locals()
        )
        DESKTOP = context.ServiceManager.createInstance('com.sun.star.frame.Desktop')
    return DESKTOP

def new( port = 2002 ):
    return load( "private:factory/simpress", port )
def load_file( filename, port=2002 ):
    filename = os.path.abspath( filename )
    file_url = 'file://'+ urllib.quote( filename ) # apparently unohelpers has this already
    return load( file_url, port )
def load( url, port=2002 ):
    """Load the given Impress/PPT document"""
    return desktop().loadComponentFromURL(url, "_blank", 0, properties(Hidden=False))

def properties( **named ):
    """Convert a dictionary of values to a set of property records for PyUNO"""
    result = []
    for key,value in named.items():
        p = PropertyValue()
        p.Name = key 
        p.Value = value 
        result.append( p )
    return tuple(result)

def connect_and_load( filename ):
    """Connect to the openoffice client and load given filename"""
    impress = None
    for i in range( 20 ):
        # ick, entirely machine dependent
        time.sleep( .1 * (1.5**i) )
        try:
            log.info( 'Attempting to load file: %s', filename )
            return load_file(filename)
        except Exception, err:
            pass # Yes, yes, when the basics work...
    raise RuntimeError( "Unable to connect to libreoffice" )
    
def configure_autoadvance( impress, default_duration=20 ):
    """Attempt to configure impress document such that all pages are auto-advancing
    
    This currently affects the GUI, but doesn't actually make the presentations 
    auto-advance...
    """
    durations = []
    pages = impress.getDrawPages()
    for i in range( pages.getCount()):
        page = pages.getByIndex( i )
        if page.getPropertyValue('Change') == 1:
            durations.append( page.getPropertyValue( 'Duration' ) )
        else:
            page.setPropertyValue('Change', 1 )
            page.setPropertyValue( 'Duration', default_duration )
            durations.append( default_duration )
        # TODO: Only if there is no, or an invalid duration, set to the short period
        # This isn't necessary, AFAICS, at least, it doesn't seem to help...
        # page.setPropertyValue('Effect',TRANSITION_NONE)
    return durations
    
def start_presentation( presentation, display=0 ):
    """Start the presentation, return the controller object for running it"""
    pres_properties = properties(
        IsEndless = True,
        IsMouseVisible = False,
        IsAutomatic = True, # loop
        IsFullScreen = True,
        IsAlwaysOnTop = True, # Fine, but annoying during testing...
        AllowAnimations = True,
        Pause = 0, # don't display black screen on finish
        StartWithNavigator = False,
        
        # Display = display, # crashes LibreOffice ARGH!
        # IsTransitionOnClick = False, # Crashes LibreOffice
        # IsShowLogo = False, # Crashes LibreOffice

    )
    presentation.startWithArguments( pres_properties )
    controller = presentation.getController()
    for i in range( 200 ):
        controller = presentation.getController()
        if controller:
            return controller
        time.sleep( 0.01 ) # sigh, return it from start, or give me a blocking operation...
    raise RuntimeError( "Unable to retrieve slideshow controller" )

def run_presentation( controller, durations, loop = False, default_duration=15 ):
    """Run the presentation, forcing auto-advance if necessary
    
    http://www.openoffice.org/api/docs/common/ref/com/sun/star/presentation/XSlideShowController.html
    """
    count = controller.getSlideCount()
    assert count == len(durations), """Some weird presentation that has more pages than the document?"""
    last = None 
    stop_time = 0
    # There must be *some* way to convince LibreOffice to actually advance 
    # the slides as the user intends...
    while controller.isRunning():
        try:
            current = controller.getCurrentSlideIndex()
        except Exception, err:
            log.error( 'Unable to retrieve current slide' )
        else:
            if current != last:
                last = current
                try:
                    target_duration = durations[current]
                    log.info( 'Slide: %s of %s, expected duration %ss', current, count, target_duration )
                    stop_time = time.time() + target_duration
                except IndexError, err:
                    stop_time = time.time() + default_duration
            elif time.time() > stop_time:
                #controller.gotoNextSlide()
                if not loop and last == count - 1:
                    return True 
                controller.gotoNextEffect()
        time.sleep( .1 ) # yeah, ick...

def view( filename, default_duration=20, loop=False, display=-1 ):
    """Main viewing operation"""
    CAPTIVE = captive()
    try:
        impress = connect_and_load( filename )
        durations = configure_autoadvance( impress, default_duration=default_duration )
        presentation = impress.getPresentation()
        
        # Argh, the property is there, what does it want!
        # I want to be able to launch OOo on display Xvfb and show the presentation 
        # only on the main monitor, but *no*
        log.debug( 'Presentation on display %s', presentation.getPropertyValue( 'Display' ) )
        
        presentation.setPropertyValue( 'Display', display+1 )
        # pprint.pprint( presentation.getPropertySetInfo().getProperties())
        
        controller = start_presentation( presentation, display=display )
        run_presentation( controller, durations, loop=loop )
        presentation.end() # crashes with 
        while presentation.isRunning():
            time.sleep( 0.01 )
        log.info( 'Closing captive client' )
    finally:
        # TODO: properly send shut down signals, maybe save modified file to cache 
        # to avoid startup penalty
        impress.setModified( False )
        desktop().terminate()
        CAPTIVE.kill()
    
def main():
    parser = OptionParser()
    parser.add_option( 
        '-d','--display', 
        dest='display', 
        default=-1, 
        type="int",
        help="Display number (X windows display integer) to use for presentation (default -1 (default))",
    )
    parser.add_option( 
        '-l','--loop', 
        dest='loop', 
        default=False, 
        action="store_true",
        help="If true, loop the presentation when completed",
    )
    parser.add_option( 
        '--default', 
        dest='default_duration', 
        default=20, 
        type="int",
        help="Specify the default duration for slides which are not set to auto-advance",
    )
    options,args = parser.parse_args()
    # Startup time to presentation showing is 6 seconds!  That's ARGH
    # One instance per display reading files from a pipe might be doable, though...
    view( args[0], options.default_duration, options.loop, options.display )
    return 0
    
if __name__ == "__main__":
    logging.basicConfig( level=logging.INFO )
    main()
