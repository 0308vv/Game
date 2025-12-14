from tkinter import *
from PIL import Image, ImageTk
import random
import math
import winsound

# --- 게임 상수 설정 ---
WIDTH = 1280
HEIGHT = 720
img_path = './image/'

class Frame:
    def __init__(self):
        # 윈도우 생성 및 설정
        self.win = Tk()
        self.win.title("Hamstar")
        self.win.geometry("1280x720+130+50") # 창 크기 및 위치 설정
        self.win.resizable(False, False)     # 창 크기 변경 불가

        # 키 입력 바인딩
        self.keys = set()
        self.win.bind("<KeyPress>", self.key_down)
        self.win.bind("<KeyRelease>", self.key_up)
        self.win.focus_set()

        # 캔버스 생성 (더블 버퍼링용 cvs2 사용)
        self.cvs = Canvas(self.win, width=WIDTH, height=HEIGHT, bg="black") 
        self.cvs2 = Canvas(self.win, width=WIDTH, height=HEIGHT, bg="black")
        self.cvs.pack()
        
        # 이미지 리소스 로드
        # (1) 타이틀 화면 이미지
        self.title_img_raw = Image.open(f"{img_path}main.png")
        self.title_img_resized = self.title_img_raw.resize((WIDTH, HEIGHT), Image.LANCZOS)
        self.main_img = ImageTk.PhotoImage(file=f"{img_path}main.png")
        self.cvs.create_image(642,362,image=self.main_img, tags="title")

        # (2) 스테이지 배경 이미지
        self.img_stage1_raw = Image.open(f"{img_path}stage1.png")
        self.img_stage1_resized = self.img_stage1_raw.resize((WIDTH, HEIGHT), Image.LANCZOS)
        self.stage1_img = ImageTk.PhotoImage(self.img_stage1_resized)
        # 배경 무한 스크롤을 위한 반전 이미지
        self.img_stage1_resized_F = self.img_stage1_resized.transpose(Image.FLIP_LEFT_RIGHT)
        self.stage1_img_F = ImageTk.PhotoImage(self.img_stage1_resized_F)

        # (3) UI 버튼 이미지
        self.start_button_raw = Image.open(f"{img_path}start_button.png")
        self.start_button_resized = self.start_button_raw.resize((112, 48), Image.LANCZOS)
        self.start_button = ImageTk.PhotoImage(self.start_button_resized)
        self.cvs.create_image(595, 400, image=self.start_button, tags="start_btn")
        self.cvs.tag_bind("start_btn", "<Button-1>", self.start)

        # (4) 플레이어 캐릭터 이미지 (상태별)
        # 정지 상태
        self.player_img = Image.open(f"{img_path}stop_ham.png")
        self.player_img = self.player_img.resize((200, 100),Image.LANCZOS)
        self.player_img_F = self.player_img.transpose(Image.FLIP_LEFT_RIGHT)
        self.stopR_player_img = ImageTk.PhotoImage(self.player_img)
        self.stopL_player_img = ImageTk.PhotoImage(self.player_img_F)

        # 이동 상태 (좌/우)
        self.player_img = Image.open(f"{img_path}move_ham.png")
        self.player_img = self.player_img.resize((200, 100),Image.LANCZOS)
        self.player_img_F = self.player_img.transpose(Image.FLIP_LEFT_RIGHT)
        self.moveR_player_img = ImageTk.PhotoImage(self.player_img)
        self.moveL_player_img = ImageTk.PhotoImage(self.player_img_F)

        # 사격 상태 (정지/이동)
        self.player_img = Image.open(f"{img_path}stop_shoot_ham.png")
        self.player_img = self.player_img.resize((200, 100),Image.LANCZOS)
        self.player_img_F = self.player_img.transpose(Image.FLIP_LEFT_RIGHT)
        self.stopR_shoot_player_img = ImageTk.PhotoImage(self.player_img)
        self.stopL_shoot_player_img = ImageTk.PhotoImage(self.player_img_F)

        self.player_img = Image.open(f"{img_path}move_shoot_ham.png")
        self.player_img = self.player_img.resize((200, 100),Image.LANCZOS)
        self.player_img_F = self.player_img.transpose(Image.FLIP_LEFT_RIGHT)
        self.moveR_shoot_player_img = ImageTk.PhotoImage(self.player_img)
        self.moveL_shoot_player_img = ImageTk.PhotoImage(self.player_img_F)

        # 무적 상태
        self.player_img = Image.open(f"{img_path}invincible_ham.png")
        self.player_img = self.player_img.resize((200, 100),Image.LANCZOS)
        self.invincible_player_img = ImageTk.PhotoImage(self.player_img)

        # (5) 적 캐릭터 이미지
        self.enemy_img = Image.open(f"{img_path}fly_enemy.png")
        self.enemy_img = self.enemy_img.resize((110,90),Image.LANCZOS)
        self.fly_enemy = ImageTk.PhotoImage(self.enemy_img)
        
        self.enemy_img = Image.open(f"{img_path}spider_enemy.png")
        self.enemy_img = self.enemy_img.resize((110,90),Image.LANCZOS)
        self.spider_enemy = ImageTk.PhotoImage(self.enemy_img)
        
        # (6) 보스 이미지
        self.boss_img = Image.open(f"{img_path}boss.png") 
        self.boss_img_resized = self.boss_img.resize((660, 500), Image.LANCZOS)
        self.boss_img = ImageTk.PhotoImage(self.boss_img_resized)

        self.boss2_img = Image.open(f"{img_path}boss2.png")
        self.boss2_img_resized = self.boss2_img.resize((420, 420), Image.LANCZOS)
        self.boss2_img = ImageTk.PhotoImage(self.boss2_img_resized)
        
        clear_img = Image.open(f"{img_path}clear.png").convert("RGBA")
        clear_img = clear_img.resize((WIDTH, HEIGHT))
        clear_img.putalpha(100) 
        self.clear_bg = ImageTk.PhotoImage(clear_img)

        # (7) 맵 오브젝트 (발판) 이미지
        self.step_img_raw = Image.open(f"{img_path}step.png")
        self.platform_images = [] # 리사이징된 발판 이미지 캐싱용 리스트

        # (8) 게임 방법 버튼
        self.how_button = Image.open(f"{img_path}how_button.png")
        self.how_button_resized = self.how_button.resize((115, 50), Image.LANCZOS)
        self.how_btn_img = ImageTk.PhotoImage(self.how_button_resized)
        self.cvs.create_image(595, 470, image=self.how_btn_img, tags="how_btn")
        self.cvs.tag_bind("how_btn", "<Button-1>", self.how)
        
        # 5. 게임 변수 초기화 함수 호출
        self.init_game_vars()

        self.play_music("main.wav", loop=True)

        self.win.mainloop()
        

    def play_music(self, file_name, loop=False):
        path = f"./sound/{file_name}" # 경로 설정
        
        flags = winsound.SND_FILENAME | winsound.SND_ASYNC
        
        if loop:
            flags = flags | winsound.SND_LOOP # 반복 재생 옵션 추가
            

        winsound.PlaySound(path, flags)

    def stop_music(self):
        winsound.PlaySound(None, winsound.SND_PURGE)



    # ==========================
    # 보스전 진입 연출 함수들
    # ==========================
    def start_boss_transition(self):
        self.is_boss_transition = True
        print("보물 창고 경보 발동! 보스 등장")
        
        self.play_music("warning.wav", loop=False)

        # 1. 붉은색 비상 경고등 효과 (화면 전체 덮기)
        self.red_alert = self.cvs2.create_rectangle(0, 0, WIDTH, HEIGHT, fill="red", stipple="gray25", tags="alert")

        self.warning_text = self.cvs2.create_text(WIDTH // 2, HEIGHT // 2, 
                                                  text="WARNING!!\nBOSS IS COMING!!", 
                                                  font=("Arial", 80, "bold"), 
                                                  fill="red", tags="warning", justify="center")

        self.blink_count = 0
        self.flash_warning() # 깜빡임 시작

    def flash_warning(self):
        # 4번 깜빡이면 보스전 실제 시작
        if self.blink_count >= 4:
            self.cvs2.delete("warning") 
            self.cvs2.delete("alert")
            self.is_boss_transition = False 
            self.start_chase_mode()     
            return
        
        # 텍스트와 붉은 화면 상태 토글 (깜빡임 효과)
        current_state = self.cvs2.itemcget(self.red_alert, "state")
        if current_state == "hidden":
            self.cvs2.itemconfig(self.red_alert, state="normal") 
            self.cvs2.itemconfig(self.warning_text, fill="white")
        else:
            self.cvs2.itemconfig(self.red_alert, state="hidden") 
            self.cvs2.itemconfig(self.warning_text, fill="red")
        
        self.blink_count += 1
        self.win.after(400, self.flash_warning)

    def start_boss_fight_arena(self):
        self.play_music("boss.wav", loop=True)
        self.is_boss_fight = True
        self.cvs2.delete("all")
        print("보스전 아레나 입장! 점프 패드 가동!")
        
        # 맵 초기화
        self.platforms = [] 
        self.platform_images = []
        self.springs = []  # [신규] 점프 패드 리스트 초기화

        # 배경
        self.cvs2.create_image(640, 360, image=self.stage1_img, tags="bg")
        
        # 발판 생성 (아까 만든 높은 발판들)
        self.create_boss_platforms()

        # 점프 패드(트램펄린) 설치
        # (x1, y1, x2, y2) 좌표
        pad_coords = [
            (20, 640, 130, 655),  # 왼쪽 패드
            (1130, 640, 1250, 655)   # 오른쪽 패드
        ]
        
        for (x1, y1, x2, y2) in pad_coords:
            # 파란색(Cyan)으로 빛나는 패드 생성
            sp = self.cvs2.create_rectangle(x1, y1, x2, y2, fill="cyan", outline="white", width=2, tags="spring")
            self.springs.append(sp)
            self.cvs2.create_text((x1+x2)//2, y1-15, text="▲ JUMP", fill="cyan", font=("Arial", 10, "bold"))

        # 플레이어 및 보스 배치
        self.player = self.cvs2.create_image(300, 500, image=self.stopR_player_img)
        self.dy = 0
        self.jump_count = 0
        self.scroll_x = 0 
        self.boss_x = 900
        self.boss = self.cvs2.create_image(self.boss_x, 500, image=self.boss2_img, tags="boss")
        
        x, y, w, h = self.health_bar_x, self.health_bar_y, self.health_bar_width, self.health_bar_height
        self.health_bar_bg = self.cvs2.create_rectangle(x, y, x + w, y + h, fill="#2F2F2F", outline="")
        self.health_bar_fg = self.cvs2.create_rectangle(x + 2, y + 2, x + w - 2, y + h - 2, fill="#2ECC71", outline="")
        self.health_bar_border = self.cvs2.create_rectangle(x, y, x + w, y + h, outline="white", width=2)
        # 현재 체력 반영
        self.update_health_bar()
        self.create_boss_health_bar()

        self.game_loop()

        # 보스전 아레나 전용 발판 생성
    def create_boss_platforms(self):
        
        arena_layout = [
            (110, 300, 140, 30),   
            (350, 250, 80, 20),
            (540, 180, 200, 30),   
            (850, 250, 80, 20),
            (1010, 300, 140, 30),   
        ]

        img_raw = self.step_img_raw 

        for (x, y, w, h) in arena_layout:
            resized_img = img_raw.resize((w, h), Image.LANCZOS)
            photo_img = ImageTk.PhotoImage(resized_img)
            self.platform_images.append(photo_img)
            plat = self.cvs2.create_image(x, y, image=photo_img, anchor='nw', tags="ground")
            self.platforms.append(plat)

    def create_boss_health_bar(self):
        """보스 체력바 UI를 생성하는 함수"""
        x_c = WIDTH -450
        y_c = 30
        w_c = 400
        h_c = 30
        self.boss_hp_bg = self.cvs2.create_rectangle(x_c, y_c, x_c + w_c, y_c + h_c, fill="darkred", tags="boss_ui")
        self.boss_hp_fg = self.cvs2.create_rectangle(x_c, y_c, x_c + w_c, y_c + h_c, fill="red", tags="boss_ui")
        self.boss_hp_text = self.cvs2.create_text(x_c + 200, y_c + h_c // 2, text=f"BOSS HP: {self.boss_health}", font=("Arial", 15, "bold"), fill="white", tags="boss_ui")

    def how(self, event=None):
        """게임 방법 및 스토리 화면 출력"""
        self.cvs.delete("all")
        self.cvs.create_image(642, 362, image=self.main_img, tags="bg")
        self.cvs.create_rectangle(140, 60, 1140, 660, fill="black", stipple="gray50")
        story = (
            "\n🚫지하 창고 잠입 작전🚫\n\n"
            "이곳은 욕심쟁이 보스의 비밀 지하실입니다\n"
            "빼앗긴 보물(⭐)을 찾아 탈출하세요!\n"
            "경비 파리🪰와 거미🕷들을 조심해야 합니다\n\n"
            "■ 조작키 안내\n"
            "   이동 : ← →   /  점프 : ↑ (2단 점프)\n"
            "   공격 : Space\n\n"
            "※ 미션 : 보물(⭐) 5개를 획득하세요! ※\n"
        )
        self.cvs.create_text(640, 320, text=story, font=("맑은 고딕", 20, "bold"), fill="white", justify="center")
        
        # 진짜 시작 버튼 생성
        self.cvs.create_image(640, 610, image=self.start_button, tags="real_start_btn")
        self.cvs.tag_bind("real_start_btn", "<Button-1>", self.start)

    def init_game_vars(self):
        """게임 내에서 쓰이는 각종 변수 초기화"""
        self.player = None
        self.dy = 0 
        self.gravity = 1
        self.jump_power = -14 
        self.move_speed = 8   
        self.jump_count = 0
        self.scroll_x = 0 
        self.platforms = [] 
        self.enemies = []
        self.fly_data = {}
        self.stars = []       
        
        # [목표] 보물 수집 관련 변수
        self.star_count = 0  
        self.target_stars = 5 # 보스 등장 조건
        self.max_stars = 5   
        self.game_over_state = False
        self.star_text = None

        # [슈팅] 총알 관련 변수
        self.bullets = []
        self.bullet_range = 500      
        self.bullet_cooldown = 300   # 연사 쿨타임 (ms)
        self.is_cooling_down = False 
        
        self.bullet_speed = 15
        self.bullet_length = 20
        self.bullet_start_x = {}
        self.bullet_dir = {}
        self.player_dir = 'right'

        # 점수 및 UI
        self.score = 0
        self.score_text = None

        # 체력 관련 변수
        self.max_health = 100
        self.player_health = self.max_health
        self.enemy_damage = 10
        self.invincible_timer = 0
        self.invincible_duration = 60 
        
        # 체력바 UI 위치 설정
        self.health_bar_x = 60
        self.health_bar_y = 40
        self.health_bar_width = 300
        self.health_bar_height = 24
        self.health_bar_bg = None
        self.health_bar_fg = None
        self.health_bar_border = None
        self.fly_frame = 0

        # 보스전 상태 변수
        self.is_boss_fight = False
        self.is_boss_transition = False 
        self.boss_health = 500
        self.boss_max_health = 500
        self.boss_damage = 15
        self.boss = None
        self.is_chasing = False
        self.boss_run_frame = 0
        self.boss_bullets = []      # 보스 총알 리스트
        self.boss_shot_timer = 0    # 공격 쿨타임
        self.boss_move_dir = 1      # 이동 방향 (1: 오른쪽, -1: 왼쪽)
        self.boss_state = 'move'   # 현재 상태 ('move': 이동, 'attack': 고정 사격)
        self.boss_state_timer = 0  # 상태 유지 시간 체크용

    def key_down(self, event):
        """키를 눌렀을 때 실행되는 함수"""
        self.keys.add(event.keysym)
        if event.keysym == "Left": self.player_dir = 'left'
        elif event.keysym == "Right": self.player_dir = 'right'
        
        # 점프 (2단 점프 가능)
        if (event.keysym == "Up") and self.jump_count < 2:
             self.dy = self.jump_power
             self.jump_count += 1
        
        # 공격
        if event.keysym == "space": self.fire_bullet()

    def key_up(self, event):
        """키를 뗐을 때 실행되는 함수"""
        if event.keysym in self.keys: self.keys.remove(event.keysym)

    def fire_bullet(self):
        """총알 발사 로직"""
        if self.game_over_state: return
        if self.is_cooling_down: return # 쿨타임 중이면 발사 불가

        p_bbox = self.cvs2.bbox(self.player)
        if not p_bbox: return
        by = (p_bbox[1] + p_bbox[3]) / 2 
        
        # 플레이어 방향에 따라 총알 생성
        if self.player_dir == 'left':
            bx = p_bbox[0]
            bullet = self.cvs2.create_oval(bx - self.bullet_length, by-5, bx, by+5, fill="yellow", outline="orange", width=2, tags="bullet")
            self.bullet_start_x[bullet] = bx
            self.bullet_dir[bullet] = -1
        else:
            bx = p_bbox[2]
            bullet = self.cvs2.create_oval(bx, by-5, bx + self.bullet_length, by+5, fill="yellow", outline="orange", width=2, tags="bullet")
            self.bullet_start_x[bullet] = bx
            self.bullet_dir[bullet] = 1
        self.bullets.append(bullet)
        
        # 쿨타임 및 발사 애니메이션 적용
        self.is_player_shoot1 = True
        self.is_cooling_down = True
        self.cvs2.after(100, self.reset_animation)
        self.cvs2.after(self.bullet_cooldown, self.reset_cooldown)

    def reset_animation(self):
        self.is_player_shoot1 = False
    
    def reset_cooldown(self):
        self.is_cooling_down = False

    def start(self, event):
        """게임 시작 진입점"""
        print("게임 시작!")
        self.play_music("stage.wav", loop=True)
        self.cvs.pack_forget() # 타이틀 화면 숨김
        self.cvs2.pack()       # 게임 화면 표시
        self.init_game_vars()
        self.create_game_objects()
        self.game_loop()



    def create_game_objects(self):
        """맵, 배경, 적, 아이템 등 게임 오브젝트 생성"""
        self.cvs2.delete("all")
        self.platform_images = [] # 이미지 리스트 초기화

        # 배경 생성 (무한 스크롤용 2장)
        self.background_1 = self.cvs2.create_image(0, 0, image=self.stage1_img, anchor='nw', tags="bg1")
        self.background_2 = self.cvs2.create_image(1280, 0, image=self.stage1_img_F, anchor='nw', tags="bg2")

        # 바닥 생성
        ground_segment_width = 1280
        ground_start = -2000
        ground_end = 15000

        self.ground_img_raw = Image.open(f"{img_path}bottom.png")
        self.ground_img_resized = self.ground_img_raw.resize((1280, 70), Image.LANCZOS)
        self.ground_img = ImageTk.PhotoImage(self.ground_img_resized)

        for x in range(ground_start, ground_end, ground_segment_width):
            seg = self.cvs2.create_image(x, 685, image=self.ground_img, anchor='nw', tags="bottom")
            self.platforms.append(seg)
        
        # 별 이미지
        img_star_raw = Image.open(f"{img_path}star.png")
        img_star_resized = img_star_raw.resize((60, 60), Image.LANCZOS)
        self.star_img_file = ImageTk.PhotoImage(img_star_resized)

        # 맵 패턴 및 적 배치
        cur_x = 600
        platform_ranges = [] 
        map_steps = 70
        spider_count = 0
        fly_count = 0
        min_gap = 360
        max_gap = 520
        min_width = 120
        max_width = 260
        min_y = 360
        max_y = 550
        min_horizontal_sep = 60 

        for i in range(1, map_steps):
            placed = False
            attempts = 0
            max_attempts = 70

            # 발판 겹침 방지 및 생성
            while not placed and attempts < max_attempts:
                attempts += 1
                gap = random.randint(min_gap, max_gap)
                x_pos = cur_x + gap
                plat_w = random.randint(min_width, max_width)
                if not platform_ranges:
                    plat_y = random.randint(500, 520) 
                else:
                    plat_y = random.randint(min_y, max_y)

                new_x1 = x_pos
                new_x2 = x_pos + plat_w
                overlap = False
                for (ex1, ex2) in platform_ranges:
                    if not (new_x2 + min_horizontal_sep < ex1 or new_x1 - min_horizontal_sep > ex2):
                        overlap = True
                        break

                if not overlap:
                    # 발판 이미지 리사이징 및 배치
                    resized_step = self.step_img_raw.resize((plat_w, 30), Image.LANCZOS)
                    step_photo = ImageTk.PhotoImage(resized_step)
                    self.platform_images.append(step_photo) 
                    
                    p = self.cvs2.create_image(new_x1, plat_y, image=step_photo, anchor='nw', tags="ground")
                    self.platforms.append(p)
                    
                    platform_ranges.append((new_x1, new_x2))
                    cur_x = x_pos 
                    placed = True
                    break

            if not placed:
                cur_x += max_gap

            # 발판 위에 별(보물) 배치
            if platform_ranges and random.random() < 0.2:
                px1, px2 = platform_ranges[-1]
                star_x = px1 + random.randint(20, max(20, px2 - px1 - 20))
                star_y = plat_y - random.randint(60, 120)
                if self.star_img_file:
                    s = self.cvs2.create_image(star_x, star_y, image=self.star_img_file, tags="star")
                else:
                    s = self.cvs2.create_polygon(star_x, star_y-25, star_x+10, star_y-5, star_x+30, star_y-5, fill="gold", tags="star")
                self.stars.append(s)

            # 발판 위에 적 배치 (안전 거리 2000px 이후)
            if platform_ranges:
                px1, px2 = platform_ranges[-1]
                if px1 > 2000:
                    if random.random() < 0.50:
                        ex = px1 + random.randint(20, max(20, px2 - px1 - 20))
                        e = self.cvs2.create_image(ex, 640, image=self.spider_enemy, tags="enemy")
                        self.enemies.append(e)
                        spider_count += 1
                
                    if random.random() < 0.40:
                        ex = px1 + random.randint(20, max(20, px2 - px1 - 20))
                        ey = random.randint(max(360 - 80, plat_y - 150), max(360, plat_y - 40))
                        e = self.cvs2.create_image(ex, ey, image=self.fly_enemy, tags=("enemy","fly"))
                        self.enemies.append(e)
                        # 파리 개별 움직임 데이터 생성
                        self.fly_data[e] = {
                            'offset': random.uniform(0, 6.28),
                            'speed': random.uniform(0.05, 0.2), 
                            'amp': random.uniform(1.5, 4.5)     
                        }
                        fly_count += 1

        self.player = self.cvs2.create_image(100, 500, image=self.stopR_player_img)
        self.score_text = self.cvs2.create_text(970, 50, text=f"Score : {self.score}", font=("Arial", 25, "bold"), fill="white")
        self.star_text = self.cvs2.create_text(1180, 50, text=f"Star : {self.star_count}/{self.target_stars}", font=("Arial", 25, "bold"), fill="yellow")
        
        # 체력바 UI 그리기
        x, y, w, h = self.health_bar_x, self.health_bar_y, self.health_bar_width, self.health_bar_height
        self.health_bar_bg = self.cvs2.create_rectangle(x, y, x + w, y + h, fill="#2F2F2F", outline="")
        self.health_bar_fg = self.cvs2.create_rectangle(x + 2, y + 2, x + w - 2, y + h - 2, fill="#2ECC71", outline="")
        self.health_bar_border = self.cvs2.create_rectangle(x, y, x + w, y + h, outline="white", width=2)

        self.wall_msg = self.cvs2.create_text(640, 200, 
                                              text="⛔ 별 5개를 다 모아야 지나갈 수 있어! ⛔", 
                                              font=("맑은 고딕", 30, "bold"), 
                                              fill="red", 
                                              state="hidden") # 처음엔 안 보이게 설정

    def update_boss_health_bar(self):
        """보스 체력바 업데이트"""
        if self.boss_hp_fg:
            new_width = (self.boss_health / self.boss_max_health) * 400
            x_c = WIDTH - 450
            y_c = 30
            self.cvs2.coords(self.boss_hp_fg, x_c, y_c, x_c + new_width, y_c + 30)
            self.cvs2.itemconfig(self.boss_hp_text, text=f"BOSS HP: {max(0, self.boss_health)}")

    def update_health_bar(self):
        """플레이어 체력바 업데이트"""
        if self.health_bar_fg:
            new_width = (self.player_health / self.max_health) * self.health_bar_width
            self.cvs2.coords(self.health_bar_fg, self.health_bar_x, self.health_bar_y, 
                             self.health_bar_x + new_width, self.health_bar_y + self.health_bar_height)

    def game_over(self):
        """게임 오버 처리: 슬픈 음악 + 재시작 대기"""
        self.game_over_state = True # 플래그 설정
        
        winsound.PlaySound(None, winsound.SND_PURGE)

        # 배경 깔고 텍스트 띄우기
        self.cvs2.create_rectangle(0, 0, 1280, 720, fill="black", stipple="gray50")
        self.cvs2.create_text(640, 360, text="GAME OVER", font=("Impact", 80, "bold"), fill="red")

        
        # 키 입력 잠그고 'R'키만 열어두기
        self.win.unbind("<KeyPress>")
        self.win.unbind("<KeyRelease>")


    def game_clear(self):
        """게임 클리어 처리: 축하 음악 + 종료 안내"""
        self.game_over_state = True
        
        # 배경 지우고 축하 화면
        self.cvs2.delete("all")
        self.cvs2.create_image(WIDTH//2, HEIGHT//2, image=self.clear_bg)
        self.cvs2.create_text(640, 250, text="GAME CLEAR!", font=("Arial", 80, "bold"), fill="blue", justify="center")
        self.cvs2.create_text(640, 350, text="햄스터 마을의 평화를 지켰습니다!", font=("Arial", 55, "bold"), fill="aqua", justify="center")
        self.cvs2.create_text(640, 450, text=f"Final Score: {self.score}", font=("Arial", 40, "bold"), fill="white")
        self.cvs2.create_text(640, 600, text="Press 'Enter' to Exit", font=("Arial", 20), fill="white")

        # 축하 음악 재생
        self.play_music("main.wav", loop=True)
        
        # 엔터키 누르면 게임 꺼지게 하기
        self.win.unbind("<KeyPress>")
        self.win.bind("<Return>", lambda e: self.win.destroy())

    def restart_game(self, event):
        """R키를 눌렀을 때 게임을 재시작하는 함수"""
        # 음악 끄기
        self.stop_music()
        
        # 게임 변수 초기화
        self.init_game_vars()
        self.game_over_state = False # 게임 오버 상태 해제
        
        # 키 바인딩 복구 (다시 게임 조작 가능하게)
        self.win.bind("<KeyPress>", self.key_down)
        self.win.bind("<KeyRelease>", self.key_up)
        self.win.unbind("<r>") # 재시작 키는 해제
        
        # 게임 다시 시작 (스테이지 음악 재생 등)
        self.start(None)

    # 추격전 시작 (보스 소환)
    def start_chase_mode(self):
        self.is_chasing = True
        print("보스가 뒤에서 나타났다!")

        #  보스 생성
        self.boss_x = 0
        self.boss = self.cvs2.create_image(self.boss_x, 410, image=self.boss_img, tags="boss")
        
         # 보스를 화면 맨 앞으로 가져옴 (배경에 가려지지 않게)
        self.cvs2.tag_raise(self.boss)
    
    # 보스 공격 함수
    def fire_boss_bullet(self):
        if not self.boss or not self.player: return
        
        # 보스와 플레이어의 위치(중심점) 계산
        b_bbox = self.cvs2.bbox(self.boss)
        p_bbox = self.cvs2.bbox(self.player)
        if not b_bbox or not p_bbox: return
        
        bx, by = (b_bbox[0] + b_bbox[2]) / 2, (b_bbox[1] + b_bbox[3]) / 2
        px, py = (p_bbox[0] + p_bbox[2]) / 2, (p_bbox[1] + p_bbox[3]) / 2
        
        # 각도 계산 (플레이어 방향)
        angle = math.atan2(py - by, px - bx)
        
        # 총알 생성 (빨간색 구체)
        # 보스 몸체 중앙에서 발사
        bullet = self.cvs2.create_oval(bx-10, by-10, bx+10, by+10, fill="red", outline="yellow", width=2, tags="boss_bullet")
        
        # 총알 정보 저장 (ID, x속도, y속도)
        speed = 7 # 총알 속도
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        self.boss_bullets.append({'id': bullet, 'vx': vx, 'vy': vy})


    # 메인 게임 루프 (핵심 로직)

    def game_loop(self):
        if self.game_over_state: return

        # 추격전 로직 (보스가 뒤에서 달려옴)
        if self.is_chasing and not self.is_boss_fight:
            # 보스 데이터가 있을 때만 실행하도록 안전장치 걸기
            if self.boss:
                # 보스 이동 및 애니메이션
                self.boss_x += 8 
                self.boss_run_frame += 0.5 
                bobbing_y = math.sin(self.boss_run_frame) * 20 
                
                # 보스 이미지 실제로 이동
                self.cvs2.coords(self.boss, self.boss_x, 410 + bobbing_y)

                # 충돌 체크
                p_bbox = self.cvs2.bbox(self.player)
                b_bbox = self.cvs2.bbox(self.boss)

                if p_bbox and b_bbox:
                    # 보스에게 잡혔을 때
                    if b_bbox[2] > p_bbox[0] + 100: 
                        print("잡혔다! 전투 시작!") 
                        
                        self.win.after(500, self.start_boss_fight_arena) 
                        return

                        
       # 적 이동 처리 (파리 개별 움직임 포함)
        if not self.is_boss_fight:
            self.fly_frame += 1
            for enemy in self.enemies:
                tags = self.cvs2.gettags(enemy)
                if "fly" in tags:
                    data = self.fly_data.get(enemy, {'offset':0, 'speed':0.1, 'amp':3})
                    # 파리 움직임: sin 함수로 위아래 진동
                    individual_dy = math.sin(self.fly_frame * data['speed'] + data['offset']) * data['amp']
                    self.cvs2.move(enemy, -4, individual_dy)
                else:
                    self.cvs2.move(enemy, -4, 0)

        # 총알 이동 및 충돌 처리
        for b in self.bullets[:]:
            dir_sign = self.bullet_dir.get(b, 1)
            self.cvs2.move(b, self.bullet_speed * dir_sign, 0)
            b_bbox = self.cvs2.bbox(b)

            # 사정거리 체크
            start_x = self.bullet_start_x.get(b, 0)
            current_x = (b_bbox[0] + b_bbox[2]) / 2 if b_bbox else 0
            dist_moved = abs(current_x - start_x)

            # 화면 밖 or 사정거리 초과 시 삭제
            if not b_bbox or b_bbox[0] > WIDTH or b_bbox[2] < 0 or dist_moved > self.bullet_range:
                self.cvs2.delete(b)
                self.bullets.remove(b)
                if b in self.bullet_start_x: del self.bullet_start_x[b]
                if b in self.bullet_dir: del self.bullet_dir[b]
                continue

            # 충돌 감지 (적 & 보스)
            left, top, right, bottom = b_bbox[0]-6, b_bbox[1]-30, b_bbox[2]+6, b_bbox[3]+30
            overlapping = self.cvs2.find_overlapping(left, top, right, bottom)
            
            hit_something = False
            for item in overlapping:
                tags = self.cvs2.gettags(item)
                
                # (A) 일반 적 충돌
                if "enemy" in tags:
                    self.cvs2.delete(item)
                    if item in self.enemies: self.enemies.remove(item)
                    if item in self.fly_data: del self.fly_data[item]
                    
                    self.cvs2.delete(b)
                    self.bullets.remove(b)
                    if b in self.bullet_start_x: del self.bullet_start_x[b]
                    if b in self.bullet_dir: del self.bullet_dir[b]
                    
                    self.score += 100
                    hit_something = True
                    break
                
                # (B) 보스 충돌
                elif self.is_boss_fight and "boss" in tags:
                    self.boss_health -= 10
                    self.score += 50
                    self.update_boss_health_bar()
                    
                    self.cvs2.delete(b)
                    self.bullets.remove(b)
                    if b in self.bullet_start_x: del self.bullet_start_x[b]
                    if b in self.bullet_dir: del self.bullet_dir[b]
                    
                    hit_something = True
                    if self.boss_health <= 0:
                        self.game_clear()
                        return
                    break
            
            if hit_something: 
                if self.score_text: self.cvs2.itemconfig(self.score_text, text=f"Score : {self.score}")
                if self.star_text: self.cvs2.itemconfig(self.star_text, text=f"Star : {self.star_count}/{self.target_stars}")
                continue

        # 물리 엔진 & 플레이어 이동 (중력 적용)
        self.dy += self.gravity
        self.cvs2.move(self.player, 0, self.dy) 
        p_bbox = self.cvs2.bbox(self.player)
        
        # 점프 패드(트램펄린) 충돌 처리 로직
        if self.is_boss_fight and p_bbox:
            # 플레이어 발 밑의 좌표
            px = (p_bbox[0] + p_bbox[2]) / 2
            py = p_bbox[3]
            
            for sp in self.springs:
                s_bbox = self.cvs2.bbox(sp)
                # 플레이어가 패드 영역 안에 들어왔는지 확인
                if s_bbox and (s_bbox[0] < px < s_bbox[2]) and (s_bbox[1] <= py <= s_bbox[3] + 10):
                        print("슈퍼 점프!")
                        self.dy = -28  
                        self.cvs2.move(self.player,0,-10)
                        self.jump_count = 0 


        # 바닥 충돌 처리
        if self.dy >= 0 and p_bbox: 
            for pid in self.platforms:
                pl_bbox = self.cvs2.bbox(pid)
                # 발판 위에 착지했는지 확인
                if pl_bbox and (p_bbox[2]-60 > pl_bbox[0] and p_bbox[0]+60 < pl_bbox[2] and 
                    p_bbox[3] >= pl_bbox[1] and p_bbox[3] <= pl_bbox[1] + self.dy + 5):
                    self.dy = 0
                    self.cvs2.move(self.player, 0, pl_bbox[1] - p_bbox[3])
                    self.jump_count = 0
                    break
            # 보스전 바닥 처리
            if self.is_boss_fight and p_bbox[3] >= 650:
                self.dy = 0
                self.cvs2.move(self.player, 0, 650 - p_bbox[3])
                self.jump_count = 0

        # 플레이어 피격 처리 (적 & 보스)
        p_bbox = self.cvs2.bbox(self.player)
        if p_bbox:
            targets = self.enemies[:]
            if self.is_boss_fight and self.boss: targets.append(self.boss)
            
            for enemy in targets:
                e_bbox = self.cvs2.bbox(enemy)
                if enemy == self.boss:
                    if e_bbox and (p_bbox[2]-50 > e_bbox[0]+100 and p_bbox[0]+50 < e_bbox[2]-100 and 
                    p_bbox[3] > e_bbox[1]+100 and p_bbox[1] < e_bbox[3]):
                        if self.invincible_timer <= 0:
                            self.player_health = max(0, self.player_health - 5)
                            self.invincible_timer = self.invincible_duration
                            self.update_health_bar()
                        
                            # 넉백 효과
                            px = (p_bbox[0] + p_bbox[2]) / 2
                            ex = (e_bbox[0] + e_bbox[2]) / 2
                            if self.dy > -15:
                                self.dy = -10

                            if px < ex: self.cvs2.move(self.player, -30, 0)
                            else: self.cvs2.move(self.player, 30, 0)

                        if self.player_health <= 0:
                            self.game_over()
                            return
                else:
                    if e_bbox and (p_bbox[2]-50 > e_bbox[0] and p_bbox[0]+50 < e_bbox[2] and 
                        p_bbox[3] > e_bbox[1] and p_bbox[1] < e_bbox[3]):
                    
                        if self.invincible_timer <= 0:
                            self.player_health = max(0, self.player_health - 5)
                            self.invincible_timer = self.invincible_duration
                            self.update_health_bar()
                        
                            # 넉백 효과
                            px = (p_bbox[0] + p_bbox[2]) / 2
                            ex = (e_bbox[0] + e_bbox[2]) / 2
                            if self.dy > -15:
                                self.dy = -10

                            if px < ex: self.cvs2.move(self.player, -30, 0)
                            else: self.cvs2.move(self.player, 30, 0)

                        if self.player_health <= 0:
                            self.game_over()
                            return

      
   
        # 보스전 패턴: 상태(이동 vs 공격) 전환 시스템

        if self.is_boss_fight and self.boss and not self.game_over_state:
            
            # 상태 타이머 증가
            self.boss_state_timer += 1
            
            # 좌우로 이동만
            if self.boss_state == 'move':
                
                if not hasattr(self, 'boss_wander_timer'):
                    self.boss_wander_dir = -1
                    self.boss_wander_timer = 0

                # 방향 전환 타이머 체크
                if self.boss_wander_timer <= 0:
                    self.boss_wander_dir = random.choice([-1, 1]) # 랜덤 방향
                    self.boss_wander_timer = random.randint(60, 120) # 1~2초 유지
                
                self.boss_wander_timer -= 1 

                # 이동 계산 (벽 밖으로 나가지 않게)
                move_speed = 5
                limit_margin = 250 
                
                next_x = self.boss_x + (self.boss_wander_dir * move_speed)
                
                # 벽 안쪽이면 이동, 벽에 닿으면 튕겨 나오기
                if next_x > limit_margin and next_x < WIDTH - limit_margin:
                    self.boss_x = next_x 
                else:
                    self.boss_wander_dir *= -1 # 방향 반전
                
                #  위치 업데이트
                self.cvs2.coords(self.boss, self.boss_x, 500)
                
                # 공격 모드로 전환
                if self.boss_state_timer > 180:
                    self.boss_state = 'attack'
                    self.boss_state_timer = 0
                    print("보스: 공격 모드!")

  
            # 총알 난사

            elif self.boss_state == 'attack':
                # 움직이지 않음 (위치 고정)
                
                # 총알 발사 로직 
                self.boss_shot_timer += 1
                # 10프레임(약 0.16초)마다 발사
                if self.boss_shot_timer > 10: 
                    self.fire_boss_bullet()
                    self.boss_shot_timer = 0
                
                # 약 2초(120프레임) 지나면 -> 다시 이동 모드로 전환
                if self.boss_state_timer > 120:
                    self.boss_state = 'move'
                    self.boss_state_timer = 0
                    print("보스: 위치 변경... (이동 모드)")

            # (공통) 발사된 총알들의 이동 및 충돌 처리

            for b_data in self.boss_bullets[:]:
                b_id = b_data['id']
                self.cvs2.move(b_id, b_data['vx'], b_data['vy'])
                
                # 화면 밖 삭제
                bb_bbox = self.cvs2.bbox(b_id)
                if not bb_bbox or bb_bbox[0] < 0 or bb_bbox[2] > WIDTH or bb_bbox[3] > HEIGHT:
                    self.cvs2.delete(b_id)
                    self.boss_bullets.remove(b_data)
                    continue
                
                # 플레이어 피격 체크
                if p_bbox:
                    bx_c, by_c = (bb_bbox[0]+bb_bbox[2])/2, (bb_bbox[1]+bb_bbox[3])/2
                    if p_bbox[0] < bx_c < p_bbox[2] and p_bbox[1] < by_c < p_bbox[3]:
                        if self.invincible_timer <= 0:
                            self.player_health = max(0, self.player_health - 15)
                            self.invincible_timer = self.invincible_duration
                            self.update_health_bar()
                            
                            self.cvs2.delete(b_id)
                            self.boss_bullets.remove(b_data)
                            
                            if self.player_health <= 0:
                                self.game_over()
                                return
                        break
                    
        #  별(보물) 수집 처리
        for star in self.stars[:]: 
            s_bbox = self.cvs2.bbox(star)
            if p_bbox and s_bbox and (p_bbox[2]-10 > s_bbox[0] and p_bbox[0]+10 < s_bbox[2] and 
                           p_bbox[3] > s_bbox[1] and p_bbox[1] < s_bbox[3]):
                self.cvs2.delete(star) 
                self.stars.remove(star) 
                self.star_count += 1
                self.score += 500

                # 목표 달성 시 처리
                if self.star_count == self.target_stars:
                    # 화면에 남은 별들 모두 삭제 (더 이상 안 나오게)
                    for rest_star in self.stars:
                        self.cvs2.delete(rest_star)
                    self.stars = [] # 리스트 비우기

                    # 추격전 시작 (왼쪽에서 보스 등장)
                    self.start_boss_transition()

                if self.star_text: 
                    self.cvs2.itemconfig(self.score_text, text=f"Score : {self.score}")
                    self.cvs2.itemconfig(self.star_text, text=f"Star : {self.star_count}/{self.target_stars}")

        # 플레이어 좌우 이동 및 이미지 업데이트
        dx = 0
        if self.invincible_timer > 0: self.invincible_timer -= 1
        current_img = self.stopR_player_img
        
        if "Left" in self.keys:
            dx = -self.move_speed
            self.player_dir = 'left'
            current_img = self.moveL_shoot_player_img if (getattr(self, 'is_player_shoot1', False)) else self.moveL_player_img
        elif "Right" in self.keys:
            dx = self.move_speed
            self.player_dir = 'right'
            current_img = self.moveR_shoot_player_img if (getattr(self, 'is_player_shoot1', False)) else self.moveR_player_img
        else:
            if self.player_dir == 'left':
                current_img = self.stopL_shoot_player_img if (getattr(self, 'is_player_shoot1', False)) else self.stopL_player_img
            elif self.player_dir == 'right':
                current_img = self.stopR_shoot_player_img if (getattr(self, 'is_player_shoot1', False)) else self.stopR_player_img
            
        # 무적 상태 깜빡임 효과
        if self.invincible_timer > 0 and (self.invincible_timer // 6) % 2 == 0:
            current_img = self.invincible_player_img
        self.cvs2.itemconfig(self.player, image=current_img)

        # 배경 스크롤 처리 (보스전이 아닐 때만)
        if not self.is_boss_fight:
            center_right = WIDTH * 0.35
            center_left = WIDTH * 0.1   
            should_scroll = False
            scroll_speed = 0
            
            
            # 맵의 끝 설정
            map_limit_x = -14500 

            # 투명 벽 로직
            is_blocked = (self.scroll_x < map_limit_x) and \
                         (self.star_count < self.target_stars) and \
                         (dx > 0)

            if is_blocked:
                dx = 0 
                self.cvs2.itemconfig(self.wall_msg, state="normal") 
            else:
                self.cvs2.itemconfig(self.wall_msg, state="hidden")


            if p_bbox:
                # 오른쪽 스크롤
                if dx > 0 and p_bbox[0] > center_right and not is_blocked:
                    scroll_speed = -dx
                    should_scroll = True
                    self.scroll_x -= dx
                
                # 왼쪽 스크롤 (시작점 제한)
                elif dx < 0 and p_bbox[0] < center_left and self.scroll_x < 0:
                    scroll_speed = -dx 
                    should_scroll = True
                    self.scroll_x -= dx
            
            if should_scroll:
                self.cvs2.move("ground", scroll_speed, 0)
                self.cvs2.move("enemy", scroll_speed, 0)
                self.cvs2.move("star", scroll_speed, 0) 
                self.cvs2.move("bg1", scroll_speed * 0.5, 0)
                self.cvs2.move("bg2", scroll_speed * 0.5, 0)
                # 경고 문구는 화면에 고정되어야 하므로 move 시키지 않음
            else:
                # 스크롤이 멈췄을 때: 플레이어가 화면 밖으로 나가는지 검사
                p_bbox = self.cvs2.bbox(self.player)
                
                if p_bbox:
                    # [왼쪽 벽 막기] 시작점(0)보다 왼쪽으로 가려 하면 멈춤
                    if dx < 0 and p_bbox[0] <= 0:
                        dx = 0
                    
                    # [오른쪽 벽 막기] 화면 끝(1280)보다 오른쪽으로 가려 하면 멈춤
                    elif dx > 0 and p_bbox[2] >= WIDTH:
                        dx = 0

                # 검사 통과한 만큼만 이동
                self.cvs2.move(self.player, dx, 0)

                
            # 무한 배경 로직
            bg1 = self.cvs2.find_withtag("bg1")
            bg2 = self.cvs2.find_withtag("bg2")
            if self.cvs2.coords(bg1)[0] < -WIDTH: self.cvs2.move(bg1, WIDTH*2, 0)
            if self.cvs2.coords(bg2)[0] < -WIDTH: self.cvs2.move(bg2, WIDTH*2, 0)
            if self.cvs2.coords(bg1)[0] > WIDTH: self.cvs2.move(bg1, -WIDTH*2, 0)
            if self.cvs2.coords(bg2)[0] > WIDTH: self.cvs2.move(bg2, -WIDTH*2, 0)
        else:

            # 보스전 벽 막기 

            
            # 플레이어 위치 확인
            p_bbox = self.cvs2.bbox(self.player)
            
            if p_bbox:
                # 이동했을 때 위치 미리 계산
                next_left = p_bbox[0] + dx
                next_right = p_bbox[2] + dx
                
                margin = 40 
                
                if next_left >= -margin and next_right <= WIDTH + margin:
                    self.cvs2.move(self.player, dx, 0) 
                else:
                    pass

        # 다음 프레임 요청 (약 60FPS)
        self.win.after(16, self.game_loop)

# 메인 실행
if __name__=='__main__':
    Frame()