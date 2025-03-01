import pygame

class DebugMenu:

    # ===Main Debug Menu Settings===
    MENU_WIDTH = 300            #width for the main debug menu
    SCROLL_SPEED = 1                #pixels/frame horizontal scroll
    WAIT_DURATION = 2000    #ms wait at end of scroll before fade-out
    FADE_DURATION = 500          #ms for fade-out/in


    # ===Console Settings===
    CONSOLE_WIDTH = 300
    CONSOLE_LINE_HEIGHT = 24
    CONSOLE_MARGIN_TOP = 10     #vertical gap below main menu
    MAX_CONSOLE_LINES = 6     #how many lines of output to show
    CURSOR_BLINK_INTERVAL = 500  #ms for blinking cursor
    CURSOR_CHAR = "|"

    #colors for different message categories
    COLOR_SUCCESS = (0, 255, 0)
    COLOR_UNKNOWN = (255, 255, 0)
    COLOR_USAGE   = (0, 128, 255)
    COLOR_INFO    = (0, 255, 0)  # default "info" color 
    COLOR_HINT    = (150, 150, 255)


    

    def __init__(self):
        self.visible = False
        self.font = pygame.font.SysFont(None, 24)

        #text input for commands
        self.input_active = False
        self.input_text = ""

        #timing
        self.clock = pygame.time.Clock()
        self.cursor_blink_elapsed = 0
        self.cursor_blink_on = False


        #main debug lines (scroll states)
        self.debug_line_cache = []    #last known text for each debug line
        self.debug_line_states = []   #scrolling/fading state per debug line

        #console lines (scroll states)
        self.console_history = []     #list of (text, color)
        self.console_line_cache = []  #last known text for each console line
        self.console_line_states = [] #scrolling/fading state per console line

        self.add_console_line("Available commands: 'tp <x> <y>', 'tp cave', 'set darkness <value>'", "usage")


    def toggle(self):
        self.visible = not self.visible
        if not self.visible:
            self.input_active = False

    # ===Event Handling===
    def handle_event(self, event, submarine, settings, seabed, lighting):
        if not self.visible:
            return

        if event.type == pygame.KEYDOWN:
            if self.input_active:
                #typing commands
                if event.key == pygame.K_RETURN:
                    self.process_input(self.input_text, submarine, seabed, lighting)
                    self.input_text = ""
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode
            else:
                #debug hotkeys
                if event.key == pygame.K_t:
                    settings["lighting"] = not settings["lighting"]
                elif event.key == pygame.K_f:
                    settings["speed"] += 1
                elif event.key == pygame.K_s:
                    settings["speed"] = max(1, settings["speed"] - 1)
                elif event.key == pygame.K_TAB:
                    self.input_active = True
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    lighting.darkness_factor = min(20.0, lighting.darkness_factor + 0.5)
                    self.add_console_line(f"Darkness Factor Increased: {lighting.darkness_factor}", "success")
                elif event.key == pygame.K_MINUS:
                    lighting.darkness_factor = max(0.1, lighting.darkness_factor - 0.5)
                    self.add_console_line(f"Darkness Factor Decreased: {lighting.darkness_factor}", "success")

    # ===Process Commands Entered in the Console===
    def process_input(self, input_text, submarine, seabed, lighting):
        #called when pressed enter
        #echo typed command
        self.add_console_line(f"> {input_text}", "info")

        try:
            if input_text.startswith("tp cave"):
                self.teleport_to_nearest_cave(submarine, seabed)
            elif input_text.startswith("tp"):
                #expect "tp X Y"
                parts = input_text.split()
                if len(parts) == 3:
                    _, x, y = parts
                    submarine.x = int(x)
                    submarine.y = int(y)
                    self.add_console_line(f"Teleported to ({x}, {y})", "success")
                else:
                    self.add_console_line("Usage: tp <x> <y>", "usage")

            elif input_text.startswith("set darkness"):
                #expect "set darkness <value>"
                parts = input_text.split()
                if len(parts) == 3:
                    _, _, value = parts
                    lighting.darkness_factor = max(0.1, min(5.0, float(value)))
                    self.add_console_line(f"Darkness Factor set to {lighting.darkness_factor}", "success")
                else:
                    self.add_console_line("Usage: set darkness <value>", "usage")

            else:
                #unknown command
                self.add_console_line(f"Unknown command: {input_text}", "unknown")

        except ValueError:
            self.add_console_line(f"Invalid command format: {input_text}", "unknown")

    def teleport_to_nearest_cave(self, submarine, seabed):
        if not hasattr(seabed, "caves") or not seabed.caves:
            self.add_console_line("No caves found!", "unknown")
            return

        #dind nearest cave
        sub_pos = (submarine.x, submarine.y)
        nearest_cave = min(
            seabed.caves,
            key=lambda c: ((c[0] - sub_pos[0]) ** 2 + (c[1] - sub_pos[1]) ** 2)
        )
        cave_x, cave_y, _ = nearest_cave
        submarine.x = cave_x
        submarine.y = cave_y
        self.add_console_line(f"Teleported to ({cave_x}, {cave_y})", "success")

    # ===Add Console Lines with Categories for Color===
    def add_console_line(self, text, category="info"):
        color_map = {
            "success": self.COLOR_SUCCESS,
            "unknown": self.COLOR_UNKNOWN,
            "usage":   self.COLOR_USAGE,
            "info":    self.COLOR_INFO
        }
        color = color_map.get(category, self.COLOR_INFO)
        self.console_history.append((text, color))

        #history short
        if len(self.console_history) > self.MAX_CONSOLE_LINES:
            self.console_history.pop(0)
            

    # ===Drawing===
    def draw(self, screen, submarine, settings, lighting):
        if not self.visible:
            return

        #1) delta time & cursor blink
        dt = self.clock.tick()
        self.update_cursor_blink(dt)

        #2) build main debug lines
        fps = self.clock.get_fps()
        debug_lines = [
            "DEBUG MENU",
            "BuildInfo: Ocean Game 0.0.10g",
            "Toggle Commands: [T] Toggle Lighting, [F/S] Adjust Speed, [+/-] Darkness Factor",
            f"FPS: {fps:.2f}",
            f"Submarine Pos: ({int(submarine.x)}, {int(submarine.y)})",
            f"Depth: {int(submarine.y)}",
            f"Depth (offset): {3000 + submarine.y}",
            f"Seabed Height: {settings.get('seabed_height', 'N/A')}",
            f"Speed: {settings['speed']}",
            f"Lighting: {'On' if settings['lighting'] else 'Off'}",
            f"Darkness Factor: {lighting.darkness_factor:.2f}",
            f"Spotlight Radius: {lighting.current_radius}",
        ]

        console_lines = list(self.console_history)
        hint_text = "[TAB] to type, [ENTER] to submit."
        #append hint line (text, color) so it can scroll
        console_lines.append((hint_text, self.COLOR_HINT))


        #4) update scrolling states for both sets
        self.update_scrolling_debug(debug_lines, dt)
        self.update_scrolling_console(console_lines, dt)

        #MAIN DEBUG MENU (TOP-RIGHT)

        x_offset = screen.get_width() - (self.MENU_WIDTH + 10)
        y_offset = 10

        #20px per line
        line_height = 20
        debug_height = (len(debug_lines) * line_height) + 10

        #draw background for main debug menu first
        bg_main = pygame.Surface((self.MENU_WIDTH, debug_height))
        bg_main.set_alpha(128)       
        bg_main.fill((0, 0, 0))     
        screen.blit(bg_main, (x_offset, y_offset))

        #draw the scrolling debug lines on top of that background
        self.render_scrolling_lines(
            screen,
            debug_lines,
            self.debug_line_states,
            x_offset=x_offset,
            y_offset=y_offset,
            box_width=self.MENU_WIDTH
        )

        #CONSOLE INPUT LINE (below debug menu)
        console_x = x_offset
        input_y = y_offset + debug_height + self.CONSOLE_MARGIN_TOP

        #draw background behind the input line
        input_bg_h = self.CONSOLE_LINE_HEIGHT + 10
        input_bg = pygame.Surface((self.CONSOLE_WIDTH, input_bg_h))
        input_bg.set_alpha(180)
        input_bg.fill((0, 0, 0))
        screen.blit(input_bg, (console_x, input_y))

        

        #if blinking, add cursor char
        input_line = self.input_text
        if self.input_active and self.cursor_blink_on:
            input_line += self.CURSOR_CHAR
        input_text = f"Terminal> {input_line}"

        input_surf = self.font.render(input_text, True, self.COLOR_INFO)
        screen.blit(input_surf, (console_x + 5, input_y + 5))

        #CONSOLE HISTORY + HINT TEXT (below input line)
        console_y = input_y + input_bg_h + 5
        console_h = (len(console_lines) * self.CONSOLE_LINE_HEIGHT) + 10

        console_bg = pygame.Surface((self.CONSOLE_WIDTH, console_h))
        console_bg.set_alpha(180)
        console_bg.fill((0, 0, 0))
        screen.blit(console_bg, (console_x, console_y))

        #ender the scrolling console lines (colored)
        self.render_scrolling_colored_lines(
            screen,
            console_lines,
            self.console_line_states,
            x_offset=console_x,
            y_offset=console_y,
            box_width=self.CONSOLE_WIDTH
        )
        


    # ===Cursor Blinking===
    def update_cursor_blink(self, dt):
        if not self.input_active:
            self.cursor_blink_on = False
            self.cursor_blink_elapsed = 0
            return

        self.cursor_blink_elapsed += dt
        if self.cursor_blink_elapsed >= self.CURSOR_BLINK_INTERVAL:
            self.cursor_blink_on = not self.cursor_blink_on
            self.cursor_blink_elapsed = 0

    # ===Separate Scrolling for Debug and Console===
    def update_scrolling_debug(self, lines, dt):
        if len(lines) != len(self.debug_line_states):
            #rebuild everything
            self.debug_line_states = []
            self.debug_line_cache = lines[:]
            for line in lines:
                self.debug_line_states.append(self._new_line_state(line))
        else:
            #check if any line changed
            for i, (old_text, new_text) in enumerate(zip(self.debug_line_cache, lines)):
                if old_text != new_text:
                    self.debug_line_cache[i] = new_text
                    self.debug_line_states[i] = self._new_line_state(new_text)

        #update each lines state
        for i, text in enumerate(lines):
            text_width = self.font.size(text)[0]
            state = self.debug_line_states[i]
            self._update_line_state(state, dt, text_width, self.MENU_WIDTH)

    def update_scrolling_console(self, lines_with_color, dt):
        #extract just the text for cache comparison
        text_list = [pair[0] for pair in lines_with_color]

        if len(text_list) != len(self.console_line_states):
            self.console_line_states = []
            self.console_line_cache = text_list[:]
            for txt in text_list:
                self.console_line_states.append(self._new_line_state(txt))
        else:
            #check changes
            for i, (old_text, new_text) in enumerate(zip(self.console_line_cache, text_list)):
                if old_text != new_text:
                    self.console_line_cache[i] = new_text
                    self.console_line_states[i] = self._new_line_state(new_text)

        #update each lines scrolling state
        for i, (text, _) in enumerate(lines_with_color):
            text_width = self.font.size(text)[0]
            state = self.console_line_states[i]
            self._update_line_state(state, dt, text_width, self.CONSOLE_WIDTH)

    def _update_line_state(self, state, dt, text_width, box_width):
        #if text fits, reset to no scroll/fade
        if text_width <= box_width:
            state["offset"] = 0
            state["alpha"] = 255
            state["phase"] = "SCROLLING"
            state["time_in_phase"] = 0
            return

        #otherwise do the cycle
        phase = state["phase"]
        if phase == "SCROLLING":
            state["offset"] -= self.SCROLL_SPEED
            max_scroll = -(text_width - box_width)
            if state["offset"] <= max_scroll:
                state["offset"] = max_scroll
                state["phase"] = "WAITING"
                state["time_in_phase"] = 0

        elif phase == "WAITING":
            state["time_in_phase"] += dt
            if state["time_in_phase"] >= self.WAIT_DURATION:
                state["phase"] = "FADING_OUT"
                state["time_in_phase"] = 0

        elif phase == "FADING_OUT":
            alpha_decrement = (255 / self.FADE_DURATION) * dt
            state["alpha"] = max(0, state["alpha"] - alpha_decrement)
            if state["alpha"] <= 0:
                #reset offset & fade in
                state["offset"] = 0
                state["phase"] = "FADING_IN"
                state["time_in_phase"] = 0

        elif phase == "FADING_IN":
            alpha_increment = (255 / self.FADE_DURATION) * dt
            state["alpha"] = min(255, state["alpha"] + alpha_increment)
            if state["alpha"] >= 255:
                state["phase"] = "SCROLLING"
                state["offset"] = 0
                state["time_in_phase"] = 0

    # ===Rendering Helpers===
    def render_scrolling_lines(self, screen, lines, line_states, x_offset, y_offset, box_width):
        line_height = 20
        for i, (text, state) in enumerate(zip(lines, line_states)):
            text_surf = self.font.render(text, True, (255, 255, 255))
            text_width = text_surf.get_width()
            text_height = text_surf.get_height()

            #the line_surf is the rendered text
            line_surf = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
            line_surf.blit(text_surf, (0,0))

            #apply fade alpha
            alpha_surf = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, state["alpha"]))
            line_surf.blit(alpha_surf, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

            #clip to box_width
            clipped_surf = pygame.Surface((box_width, text_height), pygame.SRCALPHA)
            clipped_surf.blit(line_surf, (state["offset"], 0))

            screen.blit(clipped_surf, (x_offset, y_offset + i*line_height))

    def render_scrolling_colored_lines(self, screen, lines_with_color, line_states, x_offset, y_offset, box_width):
        line_height = self.CONSOLE_LINE_HEIGHT
        for i, ((text, color), state) in enumerate(zip(lines_with_color, line_states)):
            #render the text in its color
            text_surf = self.font.render(text, True, color)
            text_width = text_surf.get_width()
            text_height = text_surf.get_height()

            #fade alpha
            line_surf = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
            line_surf.blit(text_surf, (0,0))

            alpha_surf = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, state["alpha"]))
            line_surf.blit(alpha_surf, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

            #clip
            clipped_surf = pygame.Surface((box_width, text_height), pygame.SRCALPHA)
            clipped_surf.blit(line_surf, (state["offset"], 0))

            screen.blit(clipped_surf, (x_offset, y_offset + i*line_height))

    # ===Creating a New Scroll State===
    def _new_line_state(self, line_text):
        return {
            "offset": 0,
            "alpha": 255,
            "phase": "SCROLLING",
            "time_in_phase": 0
        }
    








