import sys
import curses 

from noobhack.ui.common import get_color, size

class Minimap:
    branch_display_names = {
        "main": "Dungeons of Doom",
    }

    def __init__(self):
        self.dungeon = None

    def shop_text_as_buffer(self, shops):
        if len(shops) > 0:
            return ["  Shops:"] + ["    * %s" % s.capitalize() for s in shops]
        else:
            return []

    def feature_text_as_buffer(self, features):
        return ["  * %s" % f.capitalize() 
                for f in sorted(features) 
                if f != "shop"]

    def level_text_as_buffer(self, level):
        buf = self.shop_text_as_buffer(level.shops) + \
              self.feature_text_as_buffer(level.features)
        return ["Level %s:" % level.dlvl] + (buf or ["  (nothing interesting)"])

    def line_to_display(self, text, width, border="|", padding=" "):
        if len(text) > (width + len(border) * 2  + len(padding) * 2):
            # If the text is too long to fit in the width, then trim it.
            text = text[:(width + len(border) * 2 + 2)]
        return "%s%s%s%s%s" % (
            border, padding, 
            text + padding * (width - len(text) - len(border) * 2 - len(padding) * 2), 
            padding, border
        )

    def layout_level_text_buffers(self, levels):
        result = []
        last_level = None
        indices = {}
        for level in levels:
            if last_level is not None and level.dlvl > (last_level.dlvl + 1):
                level_display_buffer = ["...", ""] + \
                                       self.level_text_as_buffer(level) + \
                                       [""]
                indices[level.dlvl] = len(result) + 2
                result += level_display_buffer
            else:
                level_display_buffer = self.level_text_as_buffer(level) + [""]
                indices[level.dlvl] = len(result)
                result += level_display_buffer

            last_level = level

        return indices, result 

    def header_as_buffer(self, text, width):
        return [
            self.line_to_display("-" * (width - 2), width, ".", ""),
            self.line_to_display(text, width),
            self.line_to_display("=" * (width - 2), width, padding=""),
        ]

    def footer_as_buffer(self, width):
        return [self.line_to_display("...", width, "'")]

    def end_as_buffer(self, width):
        return [self.line_to_display("-" * (width - 2), width, "'", "")]

    def unconnected_branch_as_buffer_with_indices(self, display_name, branch, end=False):
        indices, level_texts = self.layout_level_text_buffers(branch)
        max_level_text_width = len(max(level_texts, key=len))

        # The '4' comes from two spaces of padding and two border pipes.
        width = 4 + max(len(display_name), max_level_text_width)

        header = self.header_as_buffer(display_name, width)
        body = [self.line_to_display(t, width) for t in level_texts]
        if not end:
            footer = self.footer_as_buffer(width)
        else:
            footer = self.end_as_buffer(width)

        # Adjust the indices to account for the header
        indices = dict([(dlvl, index + len(header)) 
                       for dlvl, index 
                       in indices.iteritems()])

        return (indices, header + body + footer) 

    def get_plane_for_map(self, levels):
        # Hopefully 10 lines per dungeon level on average is large enough...
        max_height = size()[0] * 3  + len(levels) * 10
        max_width = size()[1] * 3
        return curses.newpad(max_height, max_width)

    def loop_and_listen_for_scroll_events(self, window, plane, bounds, close):
        left, right, top, bottom, current_lvl_x, current_lvl_y = bounds

        mid_screen_x = size()[1] / 2
        mid_screen_y = size()[0] / 2
        scroll_y = current_lvl_y - mid_screen_y
        scroll_x = current_lvl_x - mid_screen_x

        while True:
            plane.noutrefresh(scroll_y, scroll_x, 0, 0, size()[0] - 1, size()[1] - 1)

            # For some reason, curses *really* wants the cursor to be below to the
            # main window, no matter who used it last. Regardless, just move it
            # to the lower left so it's out of the way.
            window.move(window.getmaxyx()[0] - 1, 0)
            window.noutrefresh()

            curses.doupdate()

            # Wait around until we get some input.
            key = sys.stdin.read(1)
            if key == close or key == "\x1b":
                break

            movements = {
                "k": (0, -1), "j": (0, 1), "h": (-1, 0), "l": (1, 0),
                "y": (-1, -1), "u": (1, -1), "b": (-1, 1), "n": (1, 1)
            }

            move_x, move_y = movements.get(key.lower(), (0, 0))

            if key.isupper():
                move_x *= 5
                move_y *= 5

            if move_y > 0:
                scroll_y = min(scroll_y + move_y, bottom - 5)
            else:
                scroll_y = max(scroll_y + move_y, top - size()[0] + 5) 

            if move_x > 0:
                scroll_x = min(scroll_x + move_x, right - 20) 
            else:
                scroll_x = max(scroll_x + move_x, left - size()[1] + 20)

    def _draw_down_connecter(self, plane, x_offset, y_offset, left=False):
        if left:
            syms = ["*", "/", "/"]
        else:
            syms = ["\\", "\\", "*"]

        for i, sym in enumerate(syms):
            plane.addstr(y_offset + i, x_offset + i, sym)

    def _draw_up_connecter(self, plane, x_offset, y_offset, left=False):
        if left:
            syms = ["*", "\\", "\\"]
        else:
            syms = ["/", "/", "*"]

        for i, sym in enumerate(syms):
            if left:
                real_y_offset = y_offset + i - len(syms)
            else: 
                real_y_offset = y_offset - i
            plane.addstr(real_y_offset, x_offset + i, sym)

    def _draw_sub_branches(self, parent, current, plane, 
                           indices, left_x_offset, right_x_offset, y_offset, 
                           color, drawn, left=False, alternate=True):
        left_x, right_x, top_y, bottom_y = plane.getmaxyx()[1], 0, plane.getmaxyx()[0], 0
        bounds = (left_x, right_x, top_y, bottom_y, 0, 0)

        for i, sub_branch in enumerate(parent.sub_branches()):
            if not drawn.has_key(sub_branch.name()):
                drawn.update({sub_branch.name(): True})

                branch_junction = [l for l
                                   in sub_branch.junction.branches()
                                   if l.branch == parent.name()][0]

                if branch_junction.dlvl < sub_branch.start.dlvl:
                    draw = self._draw_branch_at
                    connect = self._draw_down_connecter
                else:
                    draw = self._draw_branch_to
                    connect = self._draw_up_connecter

                if alternate:
                    left = left or (i % 2) == 1

                if left:
                    connect_offset = x_offset = left_x_offset - 3
                else:
                    x_offset = right_x_offset + 3
                    connect_offset = right_x_offset

                connect_at = y_offset + indices[branch_junction.dlvl] - 1
                sub_bounds = draw(sub_branch, current, plane, 
                     x_offset, connect_at, color, 
                     drawn, left, False)

                bounds = (
                    min(sub_bounds[0], bounds[0]),
                    max(sub_bounds[1], bounds[1]),
                    min(sub_bounds[2], bounds[2]),
                    max(sub_bounds[3], bounds[3]),
                    max(sub_bounds[4], bounds[4]),
                    max(sub_bounds[5], bounds[5]),
                )

                connect(plane, connect_offset, connect_at + 1, left)
        return bounds

    def _draw_branch_to(self, branch, current, plane,
                        x_offset, y_offset, color, drawn, 
                        left=False, alternate=True):
        return self._draw_branch(branch, current, plane,
                          x_offset, y_offset, color,
                          drawn, True, left, alternate)

    def _draw_branch_at(self, branch, current, plane, 
                        x_offset, y_offset, color, drawn, 
                        left=False, alternate=True):
        return self._draw_branch(branch, current, plane,
                          x_offset, y_offset, color,
                          drawn, False, left, alternate)

    def _draw_branch(self, branch, current, plane, 
                     x_offset, y_offset, color, drawn,
                     to=False, left=False, alternate=True):
        drawn.update({branch.name(): True})

        indices, buf = self.unconnected_branch_as_buffer_with_indices(
            branch.name(), branch, to
        )

        if to:
            real_y_offset = y_offset - len(buf) + 1
        else:
            real_y_offset = y_offset

        if left:
            real_x_offset = x_offset - len(buf[0])
        else:
            real_x_offset = x_offset

        for index, line in enumerate(buf):
            plane.addstr(real_y_offset + index, real_x_offset, line)

            # Hilight the current level in bold green text if it's in this
            # branch. 
            if current.branch == branch.name() and \
               index >= indices[current.dlvl] and \
               index < indices.get(current.dlvl + 1, len(buf) - 1):
                plane.chgat(
                    real_y_offset + index, 
                    real_x_offset + 1, 
                    len(line) - 2, 
                    curses.A_BOLD | color(curses.COLOR_GREEN)
                )

        # Determine our bounding box.
        left_x = real_x_offset
        right_x = real_x_offset + len(buf[0])
        top_y = real_y_offset
        bottom_y = real_y_offset + len(buf)

        if current.branch == branch.name():
            current_lvl_x = real_x_offset
            current_lvl_y = real_y_offset + indices[current.dlvl]
        else:
            current_lvl_x = left_x 
            current_lvl_y = top_y 

        bounds = (left_x, right_x, top_y, bottom_y, current_lvl_x, current_lvl_y)

        sub_bounds = self._draw_sub_branches(
            branch, current, plane, indices, 
            real_x_offset, real_x_offset + len(buf[0]),
            real_y_offset, color, drawn, left, alternate
        )

        return (
            min(sub_bounds[0], bounds[0]),
            max(sub_bounds[1], bounds[1]),
            min(sub_bounds[2], bounds[2]),
            max(sub_bounds[3], bounds[3]),
            max(sub_bounds[4], bounds[4]),
            max(sub_bounds[5], bounds[5]),
        )

    def draw_dungeon(self, dungeon, plane, x_offset, y_offset, color=get_color):
        return self._draw_branch_at(
            dungeon.main(), dungeon.current, plane, 
            x_offset, y_offset, color, {}
        )

    def display(self, dungeon, window, close="`"):
        plane = self.get_plane_for_map(dungeon.main())
        bounds = self.draw_dungeon(dungeon, plane, plane.getmaxyx()[1] / 2, size()[0])
        self.loop_and_listen_for_scroll_events(window, plane, bounds, close)
