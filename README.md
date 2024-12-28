# 介绍

一个基于LLM的文字冒险游戏Demo.

# 运行方法

## 本地运行

python main.py

## 镜像运行

```shell
docker pull lifu963/llm-adventure:v3.1
docker run -p 7860:7860 lifu963/llm-adventure:v3.1
```

## 运行效果

<img width="1489" alt="all" src="https://github.com/user-attachments/assets/0dc08d05-8c46-455d-adba-5720c06af4fa" />

## 并发能力

至少支持 5 qps.

# 当前问题

- 文字太多，选择太少；干巴
- 考虑增加地图/同伴/道具机制；尽可能减少文字，增加可互动空间
