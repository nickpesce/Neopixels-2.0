import controls as np
import time, random, math, sys, getopt, threading, signal, atexit
__author__="Nick Pesce"
__email__="npesce@terpmail.umd.edu"

SPEED = 0b10
COLOR = 0b1

stop_event = threading.Event()
t = None

def start(effect, **args): 
    global stop_event
    global t
    if not is_effect(effect):
        return (help(), False)
    if "speed" in args:
        args["speed"] = 10**((args["speed"]-50)/50.0)
    try:
        effect_fun = effects[effect.lower()]
        stop_event.set()
        if t is not None:
            t.join()
        stop_event.clear()
        t = threading.Thread(target=effect_fun, kwargs=args)
        t.daemon = True
        t.start()
        return (effect + " started!",  True)
    except Exception, e:
        return (str(e), False)

def help():
    return """Effects:\n    ~ """ + ("\n    ~ ".join(d["name"] + " " + modifiers_to_string(d["modifiers"]) for d in commands))

def modifiers_to_string(modifiers):
    ret = ""
    if(modifiers & SPEED):
        ret += "[-s speed]"
    if(modifiers & COLOR):
        ret += "[-c (r,g,b)]"
    return ret

def get_effects():
    return commands

def get_colors():
    return colors
    
def slide(speed = 1, **extras):
    """The full color spectrum is shown and it "slides"/translates across the string

    Param speed: How fast it slides. Scales the default speed."""
    global stop_event
    off = 0
    while(not stop_event.is_set()):
        for n in range(0, np.LED_COUNT):
            np.set_pixel_hsv(n, ((n+off)/60.0)%1, 1, 1)
        off+=.1
        np.show()
        stop_event.wait(.05/speed)
        
def bounce(speed=1, **extras):
    """Two pixels start on either end and move along the string changing color.
    When the end is hit, they change  direction

    Param speed: Scales the default speed."""
    global stop_event
    x = 0
    dx = .1
    while(not stop_event.is_set()):
        np.off()
        np.set_pixel_hsv(int(x), (x/float(np.LED_COUNT))%1, 1, 1)
        np.set_pixel_hsv(int(np.LED_COUNT-x), ((np.LED_COUNT-x)/float(np.LED_COUNT))%1, 1, 1)
        x+=dx
        if(x+dx >=np.LED_COUNT or x+dx <0):
            dx = -dx
        np.show()
        stop_event.wait(.01/speed)

def christmas(speed=1, **extras):
    """Lights up green and red. Pattern "slides" along the string.

    Param speed: Scales the default speed"""

    global stop_event
    for n in range(0, np.LED_COUNT):
        x = math.fabs((np.LED_COUNT/2 - n)/float(np.LED_COUNT/2))
        np.set_pixel(n, int(255-(x*255)), int(x*255), 0)
            
    while(not stop_event.is_set()):
        first = np.get_pixel(0)
        for n in range(0, np.LED_COUNT-1):
            np.set_pixel(n, *np.get_pixel(n+1))
            np.set_pixel(np.LED_COUNT-1, *first)
        np.show()
        stop_event.wait(.2/speed)
        
def cycle(speed=1, **extras):
    """Cycles through the color spectrum. Entire string is the same color.
    
    Param speed: Scales the default speed."""

    global stop_event
    while not stop_event.is_set():
        for h in range(0, 1000):
            if stop_event.is_set():
                break
            np.set_all_pixels_hsv(h/1000.0, 1, 1)
            np.show()
            stop_event.wait(.05/speed)

def rave(speed=1, **extras):
    """Each individual light displays a different random color, changing rapidly.

    Param speed: Scales the default speed."""

    global stop_event
    while(not stop_event.is_set()):
        for n in range(0, np.LED_COUNT):
            np.set_pixel(n, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        np.show();
        stop_event.wait(.1/speed)

def strobe(speed=1, color = [255, 255, 255], **extras):
    """Entire string flashes rapidly.
    
    Param speed: Scales the default speed.
    Param r, g, b: Default white. RGB values for light color. [0, 255]"""
    
    global stop_event
    while(not stop_event.is_set()):
        np.set_all_pixels(color[0], color[1], color[2])
        np.show()
        stop_event.wait(.1/speed)
        np.off()
        stop_event.wait(.1/speed)
        
def throb(speed=1, color=[255, 255, 255], **extras):
    """Entire string cycles through brightness levels. Starts off, gradually gets brighters, the darker, and repeats.
    
    Param speed: Scales the default speed.
    Param r, g, b: Default white. RGB values for light color. [0, 255]"""

    global stop_event
    np.set_all_pixels(color[0], color[1], color[2])
    brightness = 0
    db = .01
    while(not stop_event.is_set()):
        np.brightness(brightness)
        np.show()
        if brightness + db > 1 or brightness + db < 0:
            db = -db
        brightness += db
        stop_event.wait(.01/speed)
    np.brightness(1)

def on(color = [255, 255, 255], **extras):
    """Turns the entire string on.
    Param r, g, b: Default white. RGB values for light color. [0, 255]"""

    global stop_event
    np.set_all_pixels(color[0], color[1], color[2])
    np.show()
    stop_event.wait()

def disco(speed=1, **extras):
    """Pattern formed when the color spectrum is repeated and condensed, then reversed
    
    Param speed: Scales the default speed."""

    global stop_event
    off = 0
    while not stop_event.is_set():
        for n in range(0, np.LED_COUNT):
            np.set_pixel_hsv(n, ((n*off)/float(np.LED_COUNT))%1, 1, 1)
        off+=.1
        np.show()
        stop_event.wait(.05/speed)

def chase(speed = 1, **extras):
    """Each light sequentially lights up a color untill the string is filled with that color,
    then it is repeated with the next color. Each color is .2 hue away in HSV.

    Param speed: Scales the default speed."""

    global stop_event
    hue = 0;
    while not stop_event.is_set():
        for n in range(0, np.LED_COUNT):
            if stop_event.is_set():
                break
            np.set_pixel_hsv(n, hue, 1, 1)
            np.show()
            stop_event.wait(.05/speed)
        hue += .2
        hue %= 1

def drip(color=[0, 200, 255], speed=1, **extras):
    """Lights increase in brightness randomly, then drop off, making an effect like water
    dropplets falling

    Param color: The color of the lights. Defaults to (0, 200, 255), which is a dark teal color.
    Param speed: Scales the default speed"""

    global stop_event
    dullness = [15]*np.LED_COUNT
    while not stop_event.is_set():
        for n in range(0, np.LED_COUNT):
            np.set_pixel(n, int(color[0]/dullness[n]), int(color[1]/dullness[n]), int(color[2]/dullness[n]))
            dullness[n] -= random.random()/20
            if dullness[n]<=1 or random.randint(0, int(dullness[n]*20)) == 0:
                dullness[n] = (random.random()*2)+4
        np.show()
        stop_event.wait(.05/speed)

def christmas_lights(**extras):
    """Lights light up in the colors and pattern of traditional christmas lights"""

    lights = []
    for n in range(0, np.LED_COUNT):
        seq = n%5
        if seq == 0:
            lights.append([100, 0, 0])
        elif seq == 1:
            lights.append([100, 0, 50])
        elif seq == 2:
            lights.append([0, 100, 0])
        elif seq == 3:
            lights.append([150, 100, 0])
        elif seq == 4:
            lights.append([0, 0, 100])
    each(tuple(lights)) 

def flash(speed = 1, **extras) :
    """All lights display the same color and change every second(by default).
    
    Param speed: Scales the default speed."""

    global stop_event
    while not stop_event.is_set():
        color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        np.set_all_pixels(color[0], color[1], color[2])
        np.show()
        stop_event.wait(1/speed)

def each(each, **extras):
    """Lights the string according to the defined colors for each pixel passed in.
    
    Param each: List of tuples containing r, g, b values for each respective pixel in order."""
    
    np.set_pixels(each)
    np.show()

def stop(**extras):
    """Turns the string off."""
    np.off()
    
#Maps string names to functions
effects = {'cycle' : cycle,
           'slide' : slide,
           'bounce' : bounce,
           'christmas' : christmas,
           'rave' : rave,
           'strobe' : strobe,
           'disco' : disco,
           'on' : on,
           'chase' : chase,
           'throb' : throb,
           'stop' : stop,
           'off' : stop,
           'each' : each,
           'drip' : drip,
           'christmas_lights' : christmas_lights,
           'flash' : flash
    }

commands = [
        {'name' : 'on', 'modifiers' : COLOR},
        {'name' : 'off', 'modifiers' : 0},
        {'name' : 'cycle', 'modifiers' : SPEED},
        {'name' : 'slide', 'modifiers' : SPEED},
        {'name' : 'bounce', 'modifiers' : SPEED},
        {'name' : 'christmas', 'modifiers' : SPEED},
        {'name' : 'rave', 'modifiers' : SPEED},
        {'name' : 'strobe', 'modifiers' : COLOR | SPEED},
        {'name' : 'disco', 'modifiers' : SPEED},
        {'name' : 'chase', 'modifiers' : SPEED},
        {'name' : 'throb', 'modifiers' : COLOR | SPEED},
        {'name' : 'drip', 'modifiers' : COLOR | SPEED},
        {'name' : 'christmas_lights', 'modifiers' : 0},
        {'name' : 'flash', 'modifiers' : SPEED},
    ]

colors = [
        {'name' : 'white', 'color' : [255,255,255]},
        {'name' : 'soft', 'color' : [125, 113, 76]}, 
        {'name' : 'soft blue', 'color' : [95, 105, 135]},
        {'name' : 'maroon', 'color' : [128,0,0]},
        {'name' : 'dark red', 'color' : [139,0,0]},
        {'name' : 'brown', 'color' : [165,42,42]},
        {'name' : 'firebrick', 'color' : [178,34,34]},
        {'name' : 'crimson', 'color' : [220,20,60]},
        {'name' :  'red', 'color' : [255,0,0]},
        {'name' : 'tomato', 'color' : [255,99,71]},
        {'name' : 'coral', 'color' : [255,127,80]},
        {'name' :  'indian red', 'color' : [205,92,92]},
        {'name' : 'light coral', 'color' : [240,128,128]},
        {'name' : 'dark salmon', 'color' : [233,150,122]},
        {'name' : 'salmon', 'color' : [250,128,114]},
        {'name' : 'light salmon', 'color' : [255,160,122]},
        {'name' : 'orange red', 'color' : [255,69,0]},
        {'name' : 'dark orange', 'color' : [255,140,0]},
        {'name' : 'orange', 'color' : [255,165,0]},
        {'name' : 'gold', 'color' : [255,215,0]},
        {'name' : 'dark golden rod', 'color' : [184,134,11]},
        {'name' : 'golden rod', 'color' : [218,165,32]},
        {'name' : 'pale golden rod', 'color' : [238,232,170]},
        {'name' : 'dark khaki', 'color' : [189,183,107]},
        {'name' : 'khaki', 'color' : [240,230,140]},
        {'name' : 'olive', 'color' : [128,128,0]},
        {'name' : 'yellow', 'color' : [255,255,0]},
        {'name' : 'yellow green', 'color' : [154,205,50]},
        {'name' : 'dark olive green', 'color' : [85,107,47]},
        {'name' : 'olive drab', 'color' : [107,142,35]},
        {'name' : 'lawn green', 'color' : [124,252,0]},
        {'name' : 'chartreuse', 'color' : [127,255,0]},
        {'name' : 'green yellow', 'color' : [173,255,47]},
        {'name' : 'dark green', 'color' : [0,100,0]},
        {'name' : 'green', 'color' : [0,128,0]},
        {'name' : 'forest green', 'color' : [34,139,34]},
        {'name' : 'lime', 'color' : [0,255,0]},
        {'name' : 'lime green', 'color' : [50,205,50]},
        {'name' : 'light green', 'color' : [144,238,144]},
        {'name' : 'pale green', 'color' : [152,251,152]},
        {'name' : 'dark sea green', 'color' : [143,188,143]},
        {'name' : 'medium spring green', 'color' : [0,250,154]},
        {'name' : 'spring green', 'color' : [0,255,127]},
        {'name' : 'sea green', 'color' : [46,139,87]},
        {'name' : 'medium aqua marine', 'color' : [102,205,170]},
        {'name' : 'medium sea green', 'color' : [60,179,113]},
        {'name' : 'light sea green', 'color' : [32,178,170]},
        {'name' : 'dark slate gray', 'color' : [47,79,79]},
        {'name' : 'teal', 'color' : [0,128,128]},
        {'name' : 'dark cyan', 'color' : [0,139,139]},
        {'name' : 'aqua', 'color' : [0,255,255]},
        {'name' : 'cyan', 'color' : [0,255,255]},
        {'name' : 'light cyan', 'color' : [224,255,255]},
        {'name' : 'dark turquoise', 'color' : [0,206,209]},
        {'name' : 'turquoise', 'color' : [64,224,208]},
        {'name' : 'medium turquoise', 'color' : [72,209,204]},
        {'name' : 'pale turquoise', 'color' : [175,238,238]},
        {'name' : 'aqua marine', 'color' : [127,255,212]},
        {'name' : 'powder blue', 'color' : [176,224,230]},
        {'name' : 'cadet blue', 'color' : [95,158,160]},
        {'name' : 'steel blue', 'color' : [70,130,180]},
        {'name' : 'corn flower blue', 'color' : [100,149,237]},
        {'name' : 'deep sky blue', 'color' : [0,191,255]},
        {'name' : 'dodger blue', 'color' : [30,144,255]},
        {'name' : 'light blue', 'color' : [173,216,230]},
        {'name' : 'sky blue', 'color' : [135,206,235]},
        {'name' : 'light sky blue', 'color' : [135,206,250]},
        {'name' : 'midnight blue', 'color' : [25,25,112]},
        {'name' : 'navy', 'color' : [0,0,128]},
        {'name' : 'dark blue', 'color' : [0,0,139]},
        {'name' : 'medium blue', 'color' : [0,0,205]},
        {'name' : 'blue', 'color' : [0,0,255]},
        {'name' : 'royal blue', 'color' : [65,105,225]},
        {'name' : 'blue violet', 'color' : [138,43,226]},
        {'name' : 'indigo', 'color' : [75,0,130]},
        {'name' : 'dark slate blue', 'color' : [72,61,139]},
        {'name' : 'slate blue', 'color' : [106,90,205]},
        {'name' : 'medium slate blue', 'color' : [123,104,238]},
        {'name' : 'medium purple', 'color' : [147,112,219]},
        {'name' : 'dark magenta', 'color' : [139,0,139]},
        {'name' : 'dark violet', 'color' : [148,0,211]},
        {'name' : 'dark orchid', 'color' : [153,50,204]},
        {'name' : 'medium orchid', 'color' : [186,85,211]},
        {'name' : 'purple', 'color' : [128,0,128]},
        {'name' : 'thistle', 'color' : [216,191,216]},
        {'name' : 'plum', 'color' : [221,160,221]},
        {'name' : 'violet', 'color' : [238,130,238]},
        {'name' : 'magenta', 'color' : [255,0,255]},
        {'name' : 'fuchsia', 'color' : [255,0,255]},
        {'name' : 'orchid', 'color' : [218,112,214]},
        {'name' : 'medium violet red', 'color' : [199,21,133]},
        {'name' : 'pale violet red', 'color' : [219,112,147]},
        {'name' : 'deep pink', 'color' : [255,20,147]},
        {'name' : 'hot pink', 'color' : [255,105,180]},
        {'name' : 'light pink', 'color' : [255,182,193]},
        {'name' : 'pink', 'color' : [255,192,203]},
        {'name' : 'antique white', 'color' : [250,235,215]},
        {'name' : 'beige', 'color' : [245,245,220]},
        {'name' : 'bisque', 'color' : [255,228,196]},
        {'name' : 'blanched almond', 'color' : [255,235,205]},
        {'name' : 'wheat', 'color' : [245,222,179]},
        {'name' : 'corn silk', 'color' : [255,248,220]},
        {'name' : 'lemon chiffon', 'color' : [255,250,205]},
        {'name' : 'light golden rod yellow', 'color' : [250,250,210]},
        {'name' : 'light yellow', 'color' : [255,255,224]},
        {'name' : 'saddle brown', 'color' : [139,69,19]},
        {'name' : 'sienna', 'color' : [160,82,45]},
        {'name' : 'chocolate', 'color' : [210,105,30]},
        {'name' : 'peru', 'color' : [205,133,63]},
        {'name' : 'sandy brown', 'color' : [244,164,96]},
        {'name' : 'burly wood', 'color' : [222,184,135]},
        {'name' : 'tan', 'color' : [210,180,140]},
        {'name' : 'rosy brown', 'color' : [188,143,143]},
        {'name' : 'moccasin', 'color' : [255,228,181]},
        {'name' : 'navajo white', 'color' : [255,222,173]},
        {'name' : 'peach puff', 'color' : [255,218,185]},
        {'name' : 'misty rose', 'color' : [255,228,225]},
        {'name' : 'lavender blush', 'color' : [255,240,245]},
        {'name' : 'linen', 'color' : [250,240,230]},
        {'name' : 'old lace', 'color' : [253,245,230]},
        {'name' : 'papaya whip', 'color' : [255,239,213]},
        {'name' : 'sea shell', 'color' : [255,245,238]},
        {'name' : 'mint cream', 'color' : [245,255,250]},
        {'name' : 'slate gray', 'color' : [112,128,144]},
        {'name' : 'light slate gray', 'color' : [119,136,153]},
        {'name' : 'light steel blue', 'color' : [176,196,222]},
        {'name' : 'lavender', 'color' : [230,230,250]},
        {'name' : 'floral white', 'color' : [255,250,240]},
        {'name' : 'alice blue', 'color' : [240,248,255]},
        {'name' : 'ghost white', 'color' : [248,248,255]},
        {'name' : 'honeydew', 'color' : [240,255,240]},
        {'name' : 'ivory', 'color' : [255,255,240]},
        {'name' : 'azure', 'color' : [240,255,255]},
        {'name' : 'snow', 'color' : [255,250,250]},
        {'name' : 'black', 'color' : [0,0,0]},
        {'name' : 'dim gray', 'color' : [105,105,105]},
        {'name' : 'dim grey', 'color' : [105, 105, 105]},
        {'name' : 'gray', 'color' : [128,128,128]},
        {'name' : 'grey', 'color' : [128,128,128]},
        {'name' : 'dark gray', 'color' : [169,169,169]},
        {'name' : 'dark grey', 'color' : [169,169,169]},
        {'name' : 'silver', 'color' : [192,192,192]},
        {'name' : 'light grey', 'color' : [211,211,211]},
        {'name' : 'light gray', 'color' : [211,211,211]},
        {'name' : 'gainsboro', 'color' : [220,220,220]},
        {'name' : 'white smoke', 'color' : [245,245,245]}
]

speeds = {
        'fastest' : 10,
        'faster' : 5,
        'fast' : 3,
        'slow' : .3333,
        'slower' : .2,
        'slowest' : .1
}

def combine_colors_in_list(list):
    """Takes a list of strings, and combines adjacent strings that are not known to be speeds"""
    ret = []
    cat = None
    for i in range(0, len(list)):
        if speeds.has_key(list[i].lower()):
            if not cat is None:
                ret.append(cat)
                cat = None
            ret.append(list[i].lower())
        else:
            if cat is None:
                cat = list[i].lower()
            else:
                cat += " " + list[i].lower()
    if not cat is None:
        ret.append(cat)
    return ret

def is_effect(name):
    return name in effects

if __name__ == "__main__":
    print "This is module can not be run. Import it and call start()"

def _clean_shutdown():
    global stop_event
    global t
    stop_event.set()
    if t is not None:
        t.join()
signal.signal( signal.SIGHUP, _clean_shutdown )
signal.signal( signal.SIGTERM, _clean_shutdown )
atexit.register(_clean_shutdown)

