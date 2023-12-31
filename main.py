import time, pyautogui, pygetwindow, keyboard

class Rect: # 描述矩形
	def __init__(self, x = 0, y = 0, w = 0, h = 0):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	
	def fix(self, x = 0, y = 0, w = 0, h = 0): # 微調
		self.x += x
		self.y += y
		self.w += w
		self.h += h
	
	def toScalePoint(self, windowRect): # 絕對座標 to 視窗相對比例
		return ScalePoint((self.x-windowRect.x)/windowRect.w, (self.y-windowRect.y)/windowRect.h)
	
	def print(self):
		print("Rect: x%d y%d w%d h%d"%(self.x, self.y, self.w, self.h))

class ScalePoint: # 視窗相對座標
	def __init__(self, sX, sY):
		self.x = sX
		self.y = sY
	
	def toPoint(self, windowRect): # 視窗相對比例 to 絕對座標
		return Rect(windowRect.x + self.x*windowRect.w, windowRect.y + self.y*windowRect.h)

class ColorArea: # 定義顏色區
	def	__init__(self):
		self.area = dict()
	
	def addArea(self, areaName, color): # 添加區域
		self.area[areaName] = color
	
	def getArea(self, color): # 偵測某個顏色屬於哪個區域
		min_areaName = None # 最相近色塊
		min_colorDistance = 1e8 # 顏色距離
		for areaName, areaColor in self.area.items():
			colorDistance = self.getColorDistance(color, areaColor)
			if colorDistance < min_colorDistance:
				min_colorDistance = colorDistance # 求最小顏色距離 -> 求最相近的顏色
				min_areaName = areaName
		return min_areaName
	def getColorDistance(self, color1, color2): # 求顏色距離
		return (color1[0]-color2[0])**2 + (color1[1]-color2[1])**2 + (color1[2]-color2[2])**2

class KeyboardListener: # 鍵盤監聽
	def __init__(self): # 初始化
		self.b_run = True # 工具是否啟動
		self.b_fishing = False # 是否開始釣魚
		
		keyboard.hook(self.keyEvent)
	
	def keyEvent(self, e): # 按鍵事件
		if e.event_type == keyboard.KEY_UP and keyboard.is_pressed('alt'):
			if e.name == "]": self.stopTool() # "]" -> 退出工具
			if e.name == "[": self.switchFishingMode() # "[" -> 開始/停止釣魚
	
	def stopTool(self): # "]" -> 退出工具
		self.b_run = False
	
	def switchFishingMode(self): # "[" -> 開始/停止釣魚
		self.b_fishing = not self.b_fishing
		if self.b_fishing:
			print("start fishing")
		else:
			print("\nstop fishing")

class Window: # 視窗相關
	def __init__(self): # 初始化
		self.topFix = 38 # 視窗頂部條修正
		self.marginFix = 9 # 視窗margin修正
		
		#else: self.targetWindowTitle = "CatFantasy"
		self.targetWindowTitle = "CatFantasy"
		if "貓之城" in [w.title for w in pygetwindow.getAllWindows()]: self.targetWindowTitle = "貓之城"
		
		self.w = pygetwindow.getWindowsWithTitle(self.targetWindowTitle)[0] # 找目標視窗
	
	def getRect(self): # 獲得視窗的大小及座標
		rect = Rect(self.w.left, self.w.top, self.w.width, self.w.height)
		rect.fix(self.marginFix, self.topFix, -2*self.marginFix, -self.topFix-self.marginFix) # 去除未知原因造成的margin (win11?)
		return rect
	
	def switchWindow(self): # 切換視窗
		if pygetwindow.getActiveWindow().title == self.targetWindowTitle: return # 如果已經是當前視窗, 則不用切換
		self.w.activate()
		time.sleep(0.1) # 切換視窗後緩衝
	
	def screenshotPoint(self, sp): # 截圖一個像素
		self.switchWindow() # 切換視窗
		point = sp.toPoint(self.getRect())
		img = pyautogui.screenshot(region = (point.x, point.y, 1, 1)) # 截圖
		return img.getpixel((0, 0))	

class Mouse: # 滑鼠相關
	def __init__(self, window): # 初始化
		self.window = window
	
	def clickScalePoint(self, sp): # 點擊視窗的比例座標
		self.window.switchWindow() # 切換到目標視窗
		point = sp.toPoint(self.window.getRect())
		pyautogui.moveTo(point.x, point.y) # 移動到指定位置
		pyautogui.click() # 點擊
	
	def getScalePoint(self):
		mouse = pyautogui.position()
		sp = Rect(mouse.x, mouse.y).toScalePoint(self.window.getRect())
		return sp

class Main: # 主程式
	def __init__(self): # 初始化
		self.version = "v1" # 版本
		
		self.sp_fishing = ScalePoint(0.9013, 0.8086) # 釣魚鈕座標
		self.sp_throwBottle = ScalePoint(0.5321, 0.8167) # 小貓咪課堂的紙條 - "丟回去"按鈕的座標
		
		self.ca_cast = ColorArea() # 拋竿區域色塊
		self.ca_cast.addArea("5%", (68, 129, 154)) # 拋竿區域 = 5%
		self.ca_cast.addArea("2%", (48, 86, 103)) # 拋竿區域 = 2%
		self.ca_cast.addArea("0%", (40, 40, 40)) # 拋竿區域 = 0%
		self.ca_cast.addArea("white_ring", (239, 239, 239)) # 白圈
		
		self.kbListener = KeyboardListener() # 鍵盤監聽
		self.window = Window() # 視窗相關
		self.mouse = Mouse(self.window) # 滑鼠控制
		print("Cat Fantasy Auto Fishing Tool %s"%self.version)
		print("start/stop auto fishing >>> alt + [")
		print("quit tool >>> alt + ]")
		print("-------------------------------------")
	
	def run(self):
		while 1:
			# msp = self.mouse.getScalePoint(); print("%.4f %.4f"%(msp.x, msp.y)) # debug
			
			if self.quitCheck(): break # 退出檢測
			if self.kbListener.b_fishing: self.fishing() # 主迴圈
	
	def quitCheck(self): # 退出檢測
		if not self.kbListener.b_run:
			print("成功停止,按任意鍵結束...")
			input()
			return True
		return False
	
	def fishing(self): # 主迴圈
		self.mouse.clickScalePoint(self.sp_fishing) # 點擊釣魚
		
		self.cast() # 拋竿判定
		
		while self.window.screenshotPoint(self.sp_fishing) != (243, 243, 243): pass # 等待拉竿鈕出現
		
		self.window.switchWindow()
		pyautogui.mouseDown(button='left')
		time.sleep(1)
		pyautogui.mouseUp(button='left')
		# 先拉竿至紅色區域
		
		while self.window.screenshotPoint(self.sp_fishing) == (243, 243, 243): # 拉竿中
			self.window.switchWindow()
			pyautogui.mouseDown(button='left')
			time.sleep(0.21)
			pyautogui.mouseUp(button='left')
		# 反覆拉竿
		
		time.sleep(3) # 等待戰利品的確認畫面
		self.mouse.clickScalePoint(self.sp_fishing)
		
		time.sleep(0.5) # 等待拋竿鈕或是瓶中信出現
		if self.window.screenshotPoint(self.sp_fishing) != (255, 255, 255): # 如果拋竿鈕沒出現, 那就是瓶中信
			time.sleep(2)
			self.mouse.clickScalePoint(self.sp_fishing)
			time.sleep(4)
			self.mouse.clickScalePoint(self.sp_throwBottle)
			while self.window.screenshotPoint(self.sp_fishing) != (255, 255, 255): pass # 等待拋竿鈕
		
		print(".", end = "")
	
	def cast(self): # 拋竿判定
		castFix = self.window.getRect().h * 0.03 # 修正誤差, 提早拋竿
		
		time.sleep(0.35) # 等待拋竿圈載入
		
		castStartRange = None
		while 1:
			areaData = self.getAreaData()
			for i in range(len(areaData)):
				if areaData[i] == "5%":
					castStartRange = i
					break
			if castStartRange != None: break
		# 判定拋竿位置
		
		while 1: # 拋竿
			areaData = self.getAreaData()
			for i in range(len(areaData)):
				if areaData[i] == "white_ring" and i >= castStartRange-castFix:
					self.mouse.clickScalePoint(self.sp_fishing)
					return
	def getAreaData(self): # 分析拋竿區域
		self.window.switchWindow() # 切換視窗
		
		rect = self.window.getRect()
		middlePoint = ScalePoint(0.5, 0.5).toPoint(rect) # 中心點
		height = int(rect.h*0.3) # 偵測範圍
		
		img = pyautogui.screenshot(region = (middlePoint.x, middlePoint.y-height, 1, height)) # 截圖
		return [self.ca_cast.getArea(img.getpixel((0, i))) for i in range(height-1, -1, -1)] # 像素 -> 顏色 -> 區域

Main().run()
