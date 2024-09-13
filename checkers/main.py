import pygame
from game import Game
from constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, FPS, WHITE, BLACK, FONT_SIZE

def draw_menu(win):
    menu_font = pygame.font.SysFont(None, FONT_SIZE)
    title = menu_font.render("Checkers", True, WHITE)
    pvp = menu_font.render("1. Player vs Player", True, WHITE)
    pva = menu_font.render("2. Player vs AI", True, WHITE)
    rules = menu_font.render("3. Game Rules", True, WHITE)
    quit_text = menu_font.render("4. Quit", True, WHITE)

    win.fill(BLACK)
    win.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    win.blit(pvp, (WIDTH//2 - pvp.get_width()//2, 200))
    win.blit(pva, (WIDTH//2 - pva.get_width()//2, 250))
    win.blit(rules, (WIDTH//2 - rules.get_width()//2, 300))
    win.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, 350))
    pygame.display.update()

def show_rules(win):
    rules_font = pygame.font.SysFont(None, FONT_SIZE)
    rules = [
        "1. Red moves first, then players alternate turns",
        "2. Pieces move diagonally forward one square at a time",
        "3. Kings can move backwards",
        "4. Capturing is mandatory",
        "5. Multiple jumps are allowed in a single turn",
        "6. The game ends when a player captures all opponent's pieces",
        "   or when a player cannot make a legal move",
        "",
        "Press any key to return to menu"
    ]
    win.fill(BLACK)
    for i, rule in enumerate(rules):
        rule_text = rules_font.render(rule, True, WHITE)
        win.blit(rule_text, (50, 50 + i * 40))
    pygame.display.update()

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Checkers')
    clock = pygame.time.Clock()

    in_menu = True
    game = None

    while True:
        if in_menu:
            draw_menu(win)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        game = Game(win)
                        in_menu = False
                    elif event.key == pygame.K_2:
                        game = Game(win, ai_opponent=True)
                        in_menu = False
                    elif event.key == pygame.K_3:
                        show_rules(win)
                        pygame.event.wait()
                    elif event.key == pygame.K_4:
                        pygame.quit()
                        return
        else:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                    game.select(row, col)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.restart()
                    elif event.key == pygame.K_s:
                        game.save_game()
                    elif event.key == pygame.K_l:
                        game.load_game()
                    elif event.key == pygame.K_q:
                        in_menu = True

            game.update()

if __name__ == "__main__":
    main()