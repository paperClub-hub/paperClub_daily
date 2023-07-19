####

[frpc](https://github.com/stilleshan/frpc) 

[chisel](https://github.com/jpillora/chisel)

#### chisel 代理服务端: 将本地8001指向 [paperclub](http://infersite.com)网址http://infersite.com
```swagger codegen
cd ./chisel_1.8.1_windows_amd64
chisel.exe server --port 1234 --proxy http://infersite.com
这样在本地访问http://localhost:8001就会转跳到http://infersite.com
```


