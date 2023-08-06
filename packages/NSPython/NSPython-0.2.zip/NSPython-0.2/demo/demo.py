from nspython import *

class AppDelegate(NSObject):
    
    @types('void', 'id')
    def applicationWillFinishLaunching_(self, notification):
        print 'Hello!'

NSAutoreleasePool.new()
app = NSApplication.sharedApplication()
app.setActivationPolicy_(NSApplicationActivationPolicyRegular)

appdelegate = AppDelegate.new()
app.setDelegate_(appdelegate)

menubar = NSMenu.new().autorelease()
appMenuItem = NSMenuItem.new().autorelease()
menubar.addItem_(appMenuItem)
app.setMainMenu_(menubar)

appMenu = NSMenu.new().autorelease()
appName = NSProcessInfo.processInfo().processName()
quitTitle = at('Quit ').stringByAppendingString_(appName)
quitMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
    quitTitle, sel('terminate:'), at('q')).autorelease()
appMenu.addItem_(quitMenuItem)
appMenuItem.setSubmenu_(appMenu)

window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(0, 0, 200, 200),
    NSTitledWindowMask,
    NSBackingStoreBuffered,
    False).autorelease()

window.cascadeTopLeftFromPoint_(NSMakePoint(20, 20))
window.setTitle_(appName)
window.makeKeyAndOrderFront_(None)

app.activateIgnoringOtherApps_(True)
app.run()
