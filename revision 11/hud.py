import pygame


class HUD:
    def __init__(self, submarine, config, screen_height):
        self.submarine = submarine
        self.config = config
        self.font = pygame.font.SysFont(None, config["font_size"])

        icon_height = int(screen_height * config["icon_scale_factor"])
        icon_size = (icon_height, icon_height)

        self.oxygen_icon = pygame.image.load(config["oxygen_icon_path"]).convert_alpha()
        self.oxygen_icon = pygame.transform.scale(self.oxygen_icon, icon_size)

        self.power_icon = pygame.image.load(config["power_icon_path"]).convert_alpha()
        self.power_icon = pygame.transform.scale(self.power_icon, icon_size)

        self.hull_icon = pygame.image.load(config["hull_icon_path"]).convert_alpha()
        self.hull_icon = pygame.transform.scale(self.hull_icon, icon_size)

    def draw(self, screen):
        depth_text = self.font.render(
            f"Depth: {int(self.submarine.y)}m", True, self.config["text_color"]
        )
        screen.blit(depth_text, (10, 10))


        icon_x = 10
        bar_x = icon_x + self.oxygen_icon.get_width() + 10


        if self.oxygen_icon:
            screen.blit(self.oxygen_icon, (icon_x, 40))
        self.draw_bar(screen, bar_x, 40, self.config["bar_width"], self.config["bar_height"],
                      self.submarine.oxygen, self.config["oxygen_color"])


        if self.power_icon:
            screen.blit(self.power_icon, (icon_x, 70))
        self.draw_bar(screen, bar_x, 70, self.config["bar_width"], self.config["bar_height"],
                      self.submarine.power, self.config["power_color"])

        if self.hull_icon:
            screen.blit(self.hull_icon, (icon_x, 100))
        self.draw_bar(screen, bar_x, 100, self.config["bar_width"], self.config["bar_height"],
                      self.submarine.hull, self.config["hull_color"])

    def draw_bar(self, screen, x, y, width, height, percentage, color):
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(screen, color, (x, y, width * (percentage / 100), height))
