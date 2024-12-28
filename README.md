# 介绍

一个基于LLM的文字冒险游戏Demo.

# 运行方法

## 本地运行

python main.py

## 镜像运行

```shell
docker pull lifu963/llm-adventure:
docker run -p 7860:7860 gradio-app
```

## 运行效果

![image](https://github.com/user-attachments/assets/52946f8d-c563-4982-b71e-bd2f31fce07b)

![image](https://github.com/user-attachments/assets/57a3ca06-d725-499f-ac47-87b1ca313beb)

![image](https://github.com/user-attachments/assets/4e16f7ff-3baa-4db5-bcd4-9a76d89a7fa9)

## 并发能力

至少支持 5 qps.
