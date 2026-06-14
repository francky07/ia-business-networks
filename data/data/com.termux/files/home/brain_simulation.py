#!/usr/bin/env python3
import curses, time, sqlite3
def main(stdscr):
    curses.curs_set(0); stdscr.nodelay(1)
    while True:
        stdscr.clear()
        stdscr.addstr(0,0,"🧠 IA BUSINESS – CERVEAU QUANTIQUE")
        stdscr.addstr(2,0, f"Heure: {time.strftime('%H:%M:%S')}")
        stdscr.refresh()
        time.sleep(2)
curses.wrapper(main)
