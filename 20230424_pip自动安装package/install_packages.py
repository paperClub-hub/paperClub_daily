
def check_install_package(package_name="paddlenlp"):
	"""检测并进行安装"""
	def install_package(package_name="paddlenlp"):
		try:
			exit_status = os.system(f"pip install {package_name} -i https://mirrors.aliyun.com/pypi/simple")
			time.sleep(10)
			if exit_status != 0: # 检查命令是否成功执行
				print(f"{package_name}: 安装失败")
				return False
			else:
				print(f"{package_name}: 安装成功")
				return True
		except Exception as e:
			print(f"{package_name}: 在安装时发生错误 {e}")
			return False

	try:
		import paddlenlp # 特例测试
		print(f"paddlenlp: 已安装, version={paddlenlp.__version__}")
	except Exception as error:
		print(f"error: {error}")
		print("paddlenlp: 准备安装...")
		install_package(package_name=package_name)


check_install_package("paddlenlp")