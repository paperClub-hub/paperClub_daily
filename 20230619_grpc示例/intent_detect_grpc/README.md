# 搜索词意图分类（gRPC）

- 目的：通过搜索词，判断搜索词分类

- 步骤：
    - proto定义:
    ```
    // 定义服务：
    syntax = "proto3";
    
    // 声明库
    package intent;
    
    // 搜索词的请求信息: 请求参数
    message IntentRequest {
        // text字段名，类型为 string
        string text = 1;
    }
    
    // 搜索词的响应信息： 方法为‘IntentResponse’
    message IntentResponse {
        // result为字段，类型为 string
        string result = 1; // 数字1,2是参数的位置顺序，并不是对参数赋值
    }
    
    // 定义意图识别服务, 方法为 ‘IntentService’
    service IntentService {
        // 搜索请求，返回结果: 方法名为‘Result’,
        // 一个服务中可以定义多个接口，也就是多个函数功能
        // Result 为对应方法名
        rpc Result (IntentRequest) returns (IntentResponse) {}
    }
    ````
  
  - 生成 proto protobuf
    ````
    命令：cd proto & python cmd.py
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./intent.proto"
    ````
    
  - gRPC 服务端
  

  - gRPC 客户端

  
  
