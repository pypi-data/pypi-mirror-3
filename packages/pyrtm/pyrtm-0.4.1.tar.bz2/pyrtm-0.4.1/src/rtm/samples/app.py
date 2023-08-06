#!/usr/bin/env python
# simple app

from rtm import createRTM

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

def createApp(rtm):
    rspTasks = rtm.tasks.getList(filter='dueWithin:"1 week of today"')
    tasks = []
    if hasattr(rspTasks.tasks, "list") and \
       hasattr(rspTasks.tasks.list, "__getitem__"):
        for l in rspTasks.tasks.list:
            # XXX: taskseries *may* be a list
            if isinstance(l.taskseries, (list, tuple)):
                for t in l.taskseries:
                    tasks.append(t.name)
            else:
                tasks.append(l.taskseries.name)
    print(tasks)
    if not tasks:
        tasks.append('No tasks due within a week')

    root = Tk()
    root.title('My tasks due within a week')
    root.wm_attributes('-topmost', 1)
    root.wm_attributes('-alpha', 0.9)
    l = Label(text='\n'.join(tasks))
    l.pack()
    l.mainloop()

def test(apiKey, secret, token=None):
    rtm = createRTM(apiKey, secret, token)
    createApp(rtm)

def main():
    import sys
    try:
        api_key, secret = sys.argv[1:3]
    except ValueError:
        sys.stderr.write('Usage: rtm_appsample APIKEY SECRET [TOKEN]\n')
    else:
        try:
            token = sys.argv[3]
        except IndexError:
            token = None
        test(api_key, secret, token)

if __name__ == '__main__':
    main()
